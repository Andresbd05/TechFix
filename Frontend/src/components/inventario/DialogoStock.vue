<script setup>
import { computed, ref, watch } from 'vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import { useRepuestosStore } from '@/stores/repuestos'
import { mensajeError } from '@/utils/errores'

// Registrar una entrada (llegó mercancía) o una salida (se dañó, se vendió...)
const props = defineProps({
  abierto: { type: Boolean, default: false },
  repuesto: { type: Object, default: null },
})
const emit = defineEmits(['cerrar', 'guardado'])

const repuestos = useRepuestosStore()

const tipo = ref('entrada')
const cantidad = ref(1)
const errorCantidad = ref('')
const error = ref('')
const guardando = ref(false)

watch(
  () => props.abierto,
  (abierto) => {
    if (!abierto) return
    tipo.value = 'entrada'
    cantidad.value = 1
    errorCantidad.value = ''
    error.value = ''
  },
)

const stockActual = computed(() => props.repuesto?.stock ?? 0)
const stockNuevo = computed(() => {
  const n = Number(cantidad.value) || 0
  return tipo.value === 'entrada' ? stockActual.value + n : stockActual.value - n
})

async function registrar() {
  const n = Number(cantidad.value)
  errorCantidad.value = !Number.isInteger(n) || n <= 0
    ? 'Escribe un número entero mayor que 0.'
    : tipo.value === 'salida' && n > stockActual.value
      ? `Solo hay ${stockActual.value} en inventario.`
      : ''
  if (errorCantidad.value) return
  guardando.value = true
  error.value = ''
  try {
    const data = await repuestos.ajustarStock(props.repuesto.sku_repuesto, tipo.value === 'entrada' ? n : -n)
    emit('guardado', `${data.mensaje}: ${props.repuesto.nombre} queda con ${data.stock_nuevo}`)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo registrar el movimiento.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <DialogoBase
    :abierto="abierto"
    titulo="Entrada o salida de stock"
    :descripcion="repuesto ? `${repuesto.nombre} (${repuesto.sku_repuesto})` : ''"
    ancho="440px"
    @cerrar="emit('cerrar')"
  >
    <form class="formulario" novalidate @submit.prevent="registrar">
      <fieldset class="campo tipo">
        <legend class="etiqueta">Movimiento</legend>
        <div class="segmentado-radio">
          <label>
            <input v-model="tipo" type="radio" name="tipo-movimiento" value="entrada" />
            <span>Entrada</span>
          </label>
          <label>
            <input v-model="tipo" type="radio" name="tipo-movimiento" value="salida" />
            <span>Salida</span>
          </label>
        </div>
      </fieldset>

      <div class="campo">
        <label for="stock-cantidad">Cantidad</label>
        <input
          id="stock-cantidad"
          v-model.number="cantidad"
          class="entrada numero"
          type="number"
          min="1"
          step="1"
          autofocus
          :aria-invalid="!!errorCantidad"
          aria-describedby="stock-resumen"
        />
        <p v-if="errorCantidad" class="error-campo">{{ errorCantidad }}</p>
      </div>

      <p id="stock-resumen" class="resumen numero" aria-live="polite">
        Hay <strong>{{ stockActual }}</strong>. Quedarán
        <strong :class="{ negativo: stockNuevo < 0 }">{{ stockNuevo }}</strong>.
      </p>

      <p v-if="error" class="alerta alerta-error" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <div class="acciones-dialogo">
        <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando…' : tipo === 'entrada' ? 'Registrar entrada' : 'Registrar salida' }}
        </button>
      </div>
    </form>
  </DialogoBase>
</template>

<style scoped>
.tipo {
  border: none;
  padding: 0;
}

.segmentado-radio {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  padding: 3px;
  border-radius: 12px;
  background: var(--color-linea-suave);
}

.segmentado-radio label {
  position: relative;
  cursor: pointer;
}

.segmentado-radio input {
  position: absolute;
  opacity: 0;
  inset: 0;
  cursor: pointer;
}

.segmentado-radio span {
  display: block;
  text-align: center;
  padding: 8px;
  border-radius: 9px;
  font-size: 15px;
  font-weight: 500;
}

.segmentado-radio input:checked + span {
  background: var(--color-superficie);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.segmentado-radio input:focus-visible + span {
  outline: 3px solid var(--color-foco);
}

.resumen {
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--color-fondo);
  color: var(--color-texto-2);
}

.resumen strong {
  color: var(--color-texto);
}

.resumen .negativo {
  color: var(--color-peligro);
}
</style>
