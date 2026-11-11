<script setup>
import { claseEstado } from '@/utils/estados'

defineProps({
  estado: { type: String, required: true },
})
</script>

<template>
  <span class="etiqueta-estado" :class="claseEstado(estado)">
    <span class="punto" aria-hidden="true"></span>
    {{ estado }}
  </span>
</template>

<style scoped>
.etiqueta-estado {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px 3px 8px;
  border-radius: 980px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  background: var(--estado-fondo);
  color: var(--estado-texto);
}

.punto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--estado-punto);
}
</style>
