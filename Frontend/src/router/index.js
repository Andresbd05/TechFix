import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LandingView from '@/views/LandingView.vue'
import DemoView from '@/views/DemoView.vue'
import RegistroView from '@/views/RegistroView.vue'
import LoginView from '@/views/LoginView.vue'
import InicioView from '@/views/InicioView.vue'
import MiPlanView from '@/views/MiPlanView.vue'
import ReparacionesView from '@/views/ReparacionesView.vue'
import ReparacionDetalleView from '@/views/ReparacionDetalleView.vue'
import ClientesView from '@/views/ClientesView.vue'
import ClienteDetalleView from '@/views/ClienteDetalleView.vue'
import InventarioView from '@/views/InventarioView.vue'
import UsuariosView from '@/views/UsuariosView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Página pública de bienvenida con los planes (CTA). Si ya iniciaste sesión, te lleva al panel.
    { path: '/', name: 'landing', component: LandingView, meta: { soloInvitados: true, titulo: 'TechFix' } },
    // Demo pública de solo lectura (sin cuenta), para mostrar qué hace la app
    { path: '/demo', name: 'demo', component: DemoView, meta: { titulo: 'Demo' } },
    { path: '/registro', name: 'registro', component: RegistroView, meta: { soloInvitados: true, titulo: 'Crear cuenta' } },
    { path: '/login', name: 'login', component: LoginView, meta: { soloInvitados: true, titulo: 'Iniciar sesión' } },
    { path: '/inicio', name: 'inicio', component: InicioView, meta: { requiereAuth: true, titulo: 'Inicio' } },
    { path: '/reparaciones', name: 'reparaciones', component: ReparacionesView, meta: { requiereAuth: true, titulo: 'Reparaciones' } },
    {
      path: '/reparaciones/:id',
      name: 'reparacion',
      component: ReparacionDetalleView,
      props: true,
      meta: { requiereAuth: true, titulo: 'Reparación' },
    },
    { path: '/clientes', name: 'clientes', component: ClientesView, meta: { requiereAuth: true, titulo: 'Clientes' } },
    {
      path: '/clientes/:cedula',
      name: 'cliente',
      component: ClienteDetalleView,
      props: true,
      meta: { requiereAuth: true, titulo: 'Cliente' },
    },
    { path: '/inventario', name: 'inventario', component: InventarioView, meta: { requiereAuth: true, titulo: 'Inventario' } },
    { path: '/plan', name: 'plan', component: MiPlanView, meta: { requiereAuth: true, titulo: 'Mi plan' } },
    {
      path: '/usuarios',
      name: 'usuarios',
      component: UsuariosView,
      meta: { requiereAuth: true, soloAdmin: true, titulo: 'Usuarios' },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// Guardia de navegación: protege rutas privadas, evita volver al login ya
// autenticado y oculta las pantallas de admin a los técnicos.
// (El backend igual rechaza con 403 lo que un técnico no puede hacer.)
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiereAuth && !auth.estaAutenticado) {
    return { name: 'login' }
  }
  if (to.meta.soloInvitados && auth.estaAutenticado) {
    return { name: 'inicio' }
  }
  if (to.meta.soloAdmin && !auth.esAdmin) {
    return { name: 'inicio' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.titulo ? `${to.meta.titulo} | TechFix` : 'TechFix'
})

export default router
