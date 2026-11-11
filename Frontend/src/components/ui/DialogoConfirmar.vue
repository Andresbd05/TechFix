<script setup>
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'

// Confirmación para acciones que no se pueden deshacer.
// El botón dice exactamente lo que va a pasar ("Eliminar cliente").
defineProps({
  abierto: { type: Boolean, default: false },
  titulo: { type: String, required: true },
  textoConfirmar: { type: String, required: true },
  peligro: { type: Boolean, default: false },
  procesando: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['confirmar', 'cerrar'])
</script>

<template>
  <DialogoBase :abierto="abierto" :titulo="titulo" ancho="440px" @cerrar="emit('cerrar')">
    <div class="texto-secundario">
      <slot />
    </div>
    <p v-if="error" class="alerta alerta-error" role="alert">
      <Icono nombre="alerta" />
      <span>{{ error }}</span>
    </p>
    <div class="acciones-dialogo">
      <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
      <button
        type="button"
        class="btn"
        :class="peligro ? 'btn-peligro' : 'btn-primario'"
        :disabled="procesando"
        @click="emit('confirmar')"
      >
        {{ procesando ? 'Un momento…' : textoConfirmar }}
      </button>
    </div>
  </DialogoBase>
</template>
