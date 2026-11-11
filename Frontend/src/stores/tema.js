import { defineStore } from 'pinia'

const CLAVE = 'techfix-tema'

// Aplica el tema poniendo (o quitando) data-theme="oscuro" en <html>.
// El tema inicial lo fija un script en index.html para que no parpadee.
function aplicar(tema) {
  const html = document.documentElement
  if (tema === 'oscuro') html.setAttribute('data-theme', 'oscuro')
  else html.removeAttribute('data-theme')
}

export const useTemaStore = defineStore('tema', {
  state: () => ({
    tema: document.documentElement.getAttribute('data-theme') === 'oscuro' ? 'oscuro' : 'claro',
  }),
  getters: {
    esOscuro: (state) => state.tema === 'oscuro',
  },
  actions: {
    alternar() {
      this.tema = this.tema === 'oscuro' ? 'claro' : 'oscuro'
      aplicar(this.tema)
      try {
        localStorage.setItem(CLAVE, this.tema)
      } catch (e) {
        // Si el navegador bloquea localStorage, el tema dura solo esta sesión
      }
    },
  },
})
