<script setup>
import { computed } from 'vue'
import { ESTADOS } from '@/utils/estados'
import Icono from '@/components/ui/Icono.vue'

const props = defineProps({
  estado: { type: String, required: true },
})

const indiceActual = computed(() => ESTADOS.indexOf(props.estado))
const terminada = computed(() => props.estado === 'Entregado')

function claseDe(i) {
  if (i < indiceActual.value || terminada.value) return 'hecho'
  if (i === indiceActual.value) return 'actual'
  return 'pendiente'
}
</script>

<template>
  <ol class="progreso" aria-label="Avance de la reparación">
    <li
      v-for="(nombre, i) in ESTADOS"
      :key="nombre"
      class="paso"
      :class="claseDe(i)"
      :aria-current="i === indiceActual ? 'step' : undefined"
    >
      <span class="circulo" aria-hidden="true">
        <Icono v-if="claseDe(i) === 'hecho'" nombre="check" :tamano="14" />
      </span>
      <span class="nombre">{{ nombre }}</span>
      <span v-if="claseDe(i) === 'hecho'" class="sr-only">(completado)</span>
      <span v-else-if="claseDe(i) === 'actual'" class="sr-only">(etapa actual)</span>
    </li>
  </ol>
</template>

<style scoped>
.progreso {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}

.paso {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-align: center;
}

/* Línea que une cada paso con el anterior */
.paso + .paso::before {
  content: '';
  position: absolute;
  top: 13px;
  right: 50%;
  width: 100%;
  height: 2px;
  background: var(--color-linea);
  z-index: 0;
}

.paso.hecho::before,
.paso.actual::before {
  background: var(--color-accion);
}

.circulo {
  position: relative;
  z-index: 1;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-superficie);
  border: 2px solid var(--color-linea);
  color: #fff;
}

.hecho .circulo {
  background: var(--color-accion);
  border-color: var(--color-accion);
}

.actual .circulo {
  border-color: var(--color-accion);
  box-shadow: 0 0 0 5px rgba(0, 113, 227, 0.16);
}

.actual .circulo::after {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-accion);
}

.nombre {
  font-size: 14px;
  line-height: 1.25;
  color: var(--color-texto-2);
  max-width: 9em;
}

.hecho .nombre {
  color: var(--color-texto);
}

.actual .nombre {
  color: var(--color-texto);
  font-weight: 600;
}

@media (max-width: 520px) {
  .nombre {
    font-size: 12px;
  }
}
</style>
