<script setup>
import { nextTick, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import NavBar from '@/components/layout/NavBar.vue'
import AvisoToast from '@/components/ui/AvisoToast.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

// Al cambiar de pantalla, llevamos el foco al título para que
// teclado y lectores de pantalla empiecen desde arriba
let primeraCarga = true
watch(
  () => route.path,
  async () => {
    if (primeraCarga) {
      primeraCarga = false
      return
    }
    await nextTick()
    const titulo = document.querySelector('main h1')
    if (titulo) {
      titulo.setAttribute('tabindex', '-1')
      titulo.focus({ preventScroll: true })
    }
  },
)
</script>

<template>
  <a class="salto-contenido" href="#contenido">Saltar al contenido</a>
  <NavBar v-if="auth.estaAutenticado" />
  <main id="contenido">
    <RouterView />
  </main>
  <AvisoToast />
</template>

<style>
main h1:focus {
  outline: none;
}
</style>
