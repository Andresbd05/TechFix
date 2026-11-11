import api from './api'

export default {
  login(username, password) {
    return api.post('/login', { username, password })
  },
  perfil() {
    return api.get('/perfil')
  },
  // Solo un admin puede crear usuarios (POST /register exige rol admin)
  registrar(usuario) {
    return api.post('/register', usuario)
  },
  // Registro público: cualquiera crea su cuenta con correo y contraseña
  registroPublico(datos) {
    return api.post('/registro', datos)
  },
  // Cambiar el plan de la cuenta actual (simulación de suscripción)
  cambiarPlan(plan) {
    return api.put('/mi-plan', { plan })
  },
}
