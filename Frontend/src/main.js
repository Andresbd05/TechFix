import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import api from './services/api'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Si el token expiró (el backend responde 401), cerramos la sesión
// y volvemos al login con un aviso.
api.interceptors.response.use(
  (respuesta) => respuesta,
  (error) => {
    const esLogin = error.config?.url?.includes('/login')
    const auth = useAuthStore()
    if (error.response?.status === 401 && !esLogin && auth.estaAutenticado) {
      auth.logout()
      router.push({ name: 'login', query: { sesion: 'expirada' } })
    }
    return Promise.reject(error)
  },
)

app.mount('#app')
