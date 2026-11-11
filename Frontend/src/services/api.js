import axios from 'axios'

// URL del backend Flask (Backend/app.py corre en el puerto 5000).
// Se puede cambiar con un archivo .env: VITE_API_URL=http://localhost:5000
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
})

// Cada petición lleva el JWT que entregó /login en el header Authorization
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
