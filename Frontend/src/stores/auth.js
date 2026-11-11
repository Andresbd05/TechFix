import { defineStore } from 'pinia'
import authService from '@/services/authService'

const NOMBRE_ROL = {
  propietario: 'Propietario',
  admin: 'Administrador',
  tecnico: 'Técnico',
  invitado: 'Invitado',
}

const NOMBRE_PLAN = {
  gratis: 'Gratis',
  basico: 'Básico',
  pro: 'Pro',
  empresa: 'Empresa',
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
    nombre: localStorage.getItem('nombre') || null,
    rol: localStorage.getItem('rol') || null,
    cedulaTecnico: localStorage.getItem('cedulaTecnico') || null,
    plan: localStorage.getItem('plan') || null,
  }),
  getters: {
    estaAutenticado: (state) => !!state.token,
    esPropietario: (state) => state.rol === 'propietario',
    esAdmin: (state) => state.rol === 'admin',
    esTecnico: (state) => state.rol === 'tecnico',
    esInvitado: (state) => state.rol === 'invitado',
    nombreRol: (state) => NOMBRE_ROL[state.rol] || state.rol || '',
    nombrePlan: (state) => NOMBRE_PLAN[state.plan] || '',
    // Nombre para mostrar: el nombre real si lo hay, si no el usuario/correo
    nombreMostrar: (state) => state.nombre || state.username || '',

    // --- Permisos (mismo criterio que el backend; el backend igual los revalida) ---
    // Clientes: crear, editar, eliminar
    puedeGestionarClientes: (state) => ['propietario', 'admin'].includes(state.rol),
    // Inventario: crear, editar, eliminar, ajustar stock
    puedeGestionarInventario: (state) => ['propietario', 'admin'].includes(state.rol),
    // Reportes del inventario (cuánto vale): solo el propietario
    puedeVerReportes: (state) => state.rol === 'propietario',
    // Reparaciones: crear y eliminar
    puedeGestionarReparaciones: (state) => ['propietario', 'admin'].includes(state.rol),
    // Asignar técnico a una reparación: solo admin
    puedeAsignar: (state) => state.rol === 'admin',
    // Crear cuentas de usuario: solo admin
    puedeGestionarUsuarios: (state) => state.rol === 'admin',
    // El invitado solo mira
    soloLectura: (state) => state.rol === 'invitado',
  },
  actions: {
    // Avanzar/usar repuestos: propietario y admin con cualquiera; el técnico solo las suyas
    puedeTrabajarReparacion(cedulaTecnicoReparacion) {
      if (['propietario', 'admin'].includes(this.rol)) return true
      if (this.rol === 'tecnico') return this.cedulaTecnico === cedulaTecnicoReparacion
      return false
    },
    // Crea la cuenta (nombre + correo + contraseña) y entra de una vez
    async registrarYEntrar(nombre, email, password) {
      await authService.registroPublico({ nombre, email, password })
      await this.login(email, password)
    },
    // Cambia el plan de la cuenta y lo refleja al instante
    async cambiarPlan(plan) {
      await authService.cambiarPlan(plan)
      this.plan = plan
      localStorage.setItem('plan', plan)
    },
    async login(username, password) {
      const { data } = await authService.login(username, password)
      this.token = data.token
      localStorage.setItem('token', data.token)

      // /perfil devuelve rol, cédula de técnico y plan guardados en el token
      const { data: perfil } = await authService.perfil()
      this.username = perfil.usuario
      this.nombre = perfil.nombre
      this.rol = perfil.rol
      this.cedulaTecnico = perfil.cedula_tecnico
      this.plan = perfil.plan
      localStorage.setItem('username', perfil.usuario)
      if (perfil.nombre) localStorage.setItem('nombre', perfil.nombre)
      else localStorage.removeItem('nombre')
      localStorage.setItem('rol', perfil.rol)
      if (perfil.cedula_tecnico) localStorage.setItem('cedulaTecnico', perfil.cedula_tecnico)
      else localStorage.removeItem('cedulaTecnico')
      if (perfil.plan) localStorage.setItem('plan', perfil.plan)
      else localStorage.removeItem('plan')
    },
    logout() {
      this.token = null
      this.username = null
      this.nombre = null
      this.rol = null
      this.cedulaTecnico = null
      this.plan = null
      for (const clave of ['token', 'username', 'nombre', 'rol', 'cedulaTecnico', 'plan']) localStorage.removeItem(clave)
    },
  },
})
