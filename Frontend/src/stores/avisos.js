import { defineStore } from 'pinia'

// Mensajes cortos de confirmación ("Cliente guardado") que se anuncian
// también a lectores de pantalla desde AvisoToast.vue
export const useAvisosStore = defineStore('avisos', {
  state: () => ({
    texto: '',
    id: 0,
  }),
  actions: {
    mostrar(texto) {
      this.texto = texto
      const id = ++this.id
      setTimeout(() => {
        if (this.id === id) this.texto = ''
      }, 4000)
    },
  },
})
