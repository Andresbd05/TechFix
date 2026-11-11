<script setup>
import { computed, reactive, ref, watch } from 'vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import { useRepuestosStore } from '@/stores/repuestos'
import { MARCAS } from '@/utils/marcas'
import { mensajeError } from '@/utils/errores'

const props = defineProps({
  abierto: { type: Boolean, default: false },
  repuesto: { type: Object, default: null },
})
const emit = defineEmits(['cerrar', 'guardado', 'eliminar'])

const repuestos = useRepuestosStore()
const editando = computed(() => !!props.repuesto)

const form = reactive({ sku: '', nombre: '', marca: '', precio: '', stock: '' })
const errores = reactive({ sku: '', nombre: '', precio: '', stock: '' })
const guardando = ref(false)
const error = ref('')

watch(
  () => props.abierto,
  (abierto) => {
    if (!abierto) return
    const r = props.repuesto
    Object.assign(form, {
      sku: r?.sku_repuesto || '',
      nombre: r?.nombre || '',
      marca: r?.id_marca ?? '',
      precio: r ? r.precio : '',
      stock: r ? r.stock : 0,
    })
    Object.assign(errores, { sku: '', nombre: '', precio: '', stock: '' })
    error.value = ''
  },
  { immediate: true },
)

function validar() {
  const precio = Number(form.precio)
  const stock = Number(form.stock)
  errores.sku = !form.sku.trim()
    ? 'Escribe el código (SKU).'
    : form.sku.trim().length > 30
      ? 'Máximo 30 caracteres.'
      : ''
  errores.nombre = form.nombre.trim() ? '' : 'Escribe el nombre del repuesto.'
  errores.precio = form.precio === '' || Number.isNaN(precio) || precio < 0 ? 'Escribe un precio de 0 o más.' : ''
  errores.stock = form.stock === '' || !Number.isInteger(stock) || stock < 0 ? 'Escribe un número entero de 0 o más.' : ''
  return !Object.values(errores).some(Boolean)
}

async function guardar() {
  error.value = ''
  if (!validar()) return
  guardando.value = true
  const datos = {
    nombre: form.nombre.trim(),
    id_marca: form.marca === '' ? null : Number(form.marca),
    precio: Number(form.precio),
    stock: Number(form.stock),
  }
  try {
    if (editando.value) {
      await repuestos.actualizar(props.repuesto.sku_repuesto, datos)
    } else {
      await repuestos.crear({ sku_repuesto: form.sku.trim().toUpperCase(), ...datos })
    }
    emit('guardado', editando.value ? 'Cambios guardados' : `${datos.nombre} agregado al inventario`)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo guardar el repuesto.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <DialogoBase :abierto="abierto" :titulo="editando ? 'Editar repuesto' : 'Nuevo repuesto'" @cerrar="emit('cerrar')">
    <form class="formulario" novalidate @submit.prevent="guardar">
      <div class="campo">
        <label for="rp-sku">Código (SKU)</label>
        <input
          id="rp-sku"
          v-model="form.sku"
          class="entrada mono-id"
          maxlength="30"
          placeholder="Ej.: PAN-SAM-S23"
          :disabled="editando"
          :autofocus="!editando"
          :aria-invalid="!!errores.sku"
          :aria-describedby="editando ? 'rp-sku-ayuda' : undefined"
        />
        <p v-if="editando" id="rp-sku-ayuda" class="ayuda">El código no se puede cambiar.</p>
        <p v-if="errores.sku" class="error-campo">{{ errores.sku }}</p>
      </div>
      <div class="campo">
        <label for="rp-nombre">Nombre</label>
        <input
          id="rp-nombre"
          v-model="form.nombre"
          class="entrada"
          autocomplete="off"
          :autofocus="editando"
          :aria-invalid="!!errores.nombre"
        />
        <p v-if="errores.nombre" class="error-campo">{{ errores.nombre }}</p>
      </div>
      <div class="campo">
        <label for="rp-marca">Marca</label>
        <select id="rp-marca" v-model="form.marca" class="entrada">
          <option value="">Genérico (sin marca)</option>
          <option v-for="m in MARCAS" :key="m.id" :value="m.id">{{ m.nombre }}</option>
        </select>
      </div>
      <div class="campos-dos">
        <div class="campo">
          <label for="rp-precio">Precio (COP)</label>
          <input
            id="rp-precio"
            v-model="form.precio"
            class="entrada numero"
            type="number"
            min="0"
            step="100"
            inputmode="decimal"
            :aria-invalid="!!errores.precio"
          />
          <p v-if="errores.precio" class="error-campo">{{ errores.precio }}</p>
        </div>
        <div class="campo">
          <label for="rp-stock">Unidades en stock</label>
          <input
            id="rp-stock"
            v-model="form.stock"
            class="entrada numero"
            type="number"
            min="0"
            step="1"
            inputmode="numeric"
            :aria-invalid="!!errores.stock"
          />
          <p v-if="errores.stock" class="error-campo">{{ errores.stock }}</p>
        </div>
      </div>

      <p v-if="error" class="alerta alerta-error" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <div class="acciones-dialogo">
        <button
          v-if="editando"
          type="button"
          class="btn-texto peligro texto-pequeno eliminar"
          @click="emit('eliminar', repuesto)"
        >
          Eliminar repuesto
        </button>
        <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Agregar al inventario' }}
        </button>
      </div>
    </form>
  </DialogoBase>
</template>
