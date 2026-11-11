<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Icono from '@/components/ui/Icono.vue'
import BotonTema from '@/components/ui/BotonTema.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const menuAbierto = ref(false)

const enlaces = computed(() => {
  const lista = [
    { to: '/inicio', texto: 'Inicio' },
    { to: '/reparaciones', texto: 'Reparaciones' },
    { to: '/clientes', texto: 'Clientes' },
    { to: '/inventario', texto: 'Inventario' },
    { to: '/plan', texto: 'Mi plan' },
  ]
  if (auth.esAdmin) lista.push({ to: '/usuarios', texto: 'Usuarios' })
  return lista
})

// "Reparaciones" queda marcado también dentro de /reparaciones/REP-...
function esActivo(to) {
  return to === '/inicio' ? route.path === '/inicio' : route.path.startsWith(to)
}

watch(() => route.fullPath, () => (menuAbierto.value = false))

function cerrarSesion() {
  auth.logout()
  router.push('/') // vuelve a la página pública
}
</script>

<template>
  <header class="nav-global">
    <nav class="contenedor nav-interior" aria-label="Principal">
      <RouterLink to="/inicio" class="marca">
        <Icono nombre="herramienta" :tamano="17" />
        <span>TechFix</span>
      </RouterLink>

      <button
        class="nav-boton-menu"
        type="button"
        :aria-expanded="menuAbierto"
        aria-controls="nav-panel"
        @click="menuAbierto = !menuAbierto"
      >
        <Icono :nombre="menuAbierto ? 'cerrar' : 'menu'" />
        <span class="sr-only">{{ menuAbierto ? 'Cerrar menú' : 'Abrir menú' }}</span>
      </button>

      <div id="nav-panel" class="nav-panel" :class="{ abierto: menuAbierto }">
        <ul class="nav-enlaces">
          <li v-for="enlace in enlaces" :key="enlace.to">
            <RouterLink :to="enlace.to" :class="{ activo: esActivo(enlace.to) }">
              {{ enlace.texto }}
            </RouterLink>
          </li>
        </ul>

        <div class="nav-usuario">
          <BotonTema />
          <span class="nav-nombre">
            {{ auth.nombreMostrar }}
            <span class="nav-rol">
              {{ auth.nombreRol }}<template v-if="auth.nombrePlan"> · Plan {{ auth.nombrePlan }}</template>
            </span>
          </span>
          <button type="button" class="nav-salir" @click="cerrarSesion">Cerrar sesión</button>
        </div>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.nav-global {
  position: relative;
  z-index: 30;
  height: var(--alto-nav);
  background: var(--color-nav-fondo);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--color-borde-sutil);
}

.nav-interior {
  height: 100%;
  display: flex;
  align-items: center;
  gap: 28px;
}

.marca {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--color-texto);
  font-weight: 600;
  font-size: 17px;
  letter-spacing: -0.02em;
}

.marca:hover {
  text-decoration: none;
}

.nav-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.nav-enlaces {
  display: flex;
  gap: 26px;
  list-style: none;
  padding: 0;
}

.nav-enlaces a {
  font-size: 13px;
  color: var(--color-texto-2);
  letter-spacing: -0.01em;
  padding: 4px 0;
  transition: color 0.2s;
}

.nav-enlaces a:hover {
  color: var(--color-texto);
  text-decoration: none;
}

.nav-enlaces a.activo {
  color: var(--color-texto);
  font-weight: 600;
}

.nav-usuario {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
}

.nav-nombre {
  color: var(--color-texto);
  font-weight: 500;
}

.nav-rol {
  color: var(--color-texto-2);
  font-weight: 400;
  margin-left: 4px;
}

.nav-salir {
  border: none;
  background: none;
  color: var(--color-enlace);
  font-size: 13px;
  padding: 4px 0;
}

.nav-salir:hover {
  text-decoration: underline;
}

.nav-boton-menu {
  display: none;
  margin-left: auto;
  border: none;
  background: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

@media (max-width: 820px) {
  .nav-boton-menu {
    display: inline-flex;
  }

  .nav-panel {
    display: none;
    position: absolute;
    top: var(--alto-nav);
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    gap: 0;
    height: calc(100dvh - var(--alto-nav));
    overflow-y: auto;
    padding: 8px var(--margen-lateral) 24px;
    background: var(--color-superficie-2);
    border-bottom: 1px solid var(--color-borde-sutil);
  }

  .nav-panel.abierto {
    display: flex;
  }

  .nav-enlaces {
    flex-direction: column;
    gap: 0;
  }

  .nav-enlaces a {
    display: block;
    font-size: 21px;
    font-weight: 600;
    color: var(--color-texto);
    padding: 12px 0;
  }

  .nav-usuario {
    justify-content: space-between;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid var(--color-linea-suave);
    font-size: 15px;
  }

  .nav-salir {
    font-size: 15px;
  }
}
</style>
