<script setup>
import { useAvisosStore } from '@/stores/avisos'
import Icono from '@/components/ui/Icono.vue'

const avisos = useAvisosStore()
</script>

<template>
  <!-- La región siempre existe para que el lector de pantalla anuncie cada mensaje -->
  <div class="aviso-region" role="status" aria-live="polite">
    <Transition name="aviso">
      <p v-if="avisos.texto" :key="avisos.id" class="aviso">
        <Icono nombre="check" :tamano="16" />
        {{ avisos.texto }}
      </p>
    </Transition>
  </div>
</template>

<style scoped>
.aviso-region {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 28px;
  display: flex;
  justify-content: center;
  pointer-events: none;
  z-index: 60;
  padding: 0 16px;
}

.aviso {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 980px;
  background: rgba(29, 29, 31, 0.92);
  backdrop-filter: blur(20px);
  color: #fff;
  font-size: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.aviso-enter-active,
.aviso-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}

.aviso-enter-from,
.aviso-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
