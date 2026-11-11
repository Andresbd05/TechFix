<script setup>
import { useTemaStore } from '@/stores/tema'
import Icono from '@/components/ui/Icono.vue'

const tema = useTemaStore()
</script>

<template>
  <button
    type="button"
    class="boton-tema"
    :aria-pressed="tema.esOscuro"
    :title="tema.esOscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
    @click="tema.alternar()"
  >
    <Icono :nombre="tema.esOscuro ? 'sol' : 'luna'" :tamano="18" />
    <span class="sr-only">{{ tema.esOscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro' }}</span>
  </button>
</template>

<style scoped>
.boton-tema {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--color-texto-2);
  flex-shrink: 0;
}

.boton-tema:hover {
  background: var(--color-linea-suave);
  color: var(--color-texto);
}
</style>
