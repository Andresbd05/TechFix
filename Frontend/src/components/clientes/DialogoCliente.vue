<script setup>
import { computed, reactive, ref, watch } from 'vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import { useClientesStore } from '@/stores/clientes'
import { mensajeError } from '@/utils/errores'

// Crear o editar un cliente. Si recibe `cliente`, edita; si no, crea.
const props = defineProps({
  abierto: { type: Boolean, default: false },
  cliente: { type: Object, default: null },
})
const emit = defineEmits(['cerrar', 'guardado', 'eliminar'])

const clientes = useClientesStore()
const editando = computed(() => !!props.cliente)

const form = reactive({ cedula: '', nombre: '', telefono: '', correo: '' })
const errores = reactive({ cedula: '', nombre: '', telefono: '', correo: '' })
const guardando = ref(false)
const error = ref('')

watch(
  () => props.abierto,
  (abierto) => {
    if (!abierto) return
    const c = props.cliente || {}
    Object.assign(form, {
      cedula: c.cedula || '',
      nombre: c.nombre || '',
      telefono: c.telefono || '',
      correo: c.correo || '',
    })
    Object.assign(errores, { cedula: '', nombre: '', telefono: '', correo: '' })
    error.value = ''
  },
  { immediate: true },
)

function validar() {
  const cedula = form.cedula.trim()
  const telefono = form.telefono.trim()
  const correo = form.correo.trim()
  errores.cedula = !cedula
    ? 'Escribe la cédula.'
    : !/^\d{5,20}$/.test(cedula)
      ? 'Usa solo números, entre 5 y 20 dígitos.'
      : ''
  errores.nombre = form.nombre.trim() ? '' : 'Escribe el nombre completo.'
  errores.telefono = !telefono
    ? 'Escribe un teléfono de contacto.'
    : !/^[\d\s+-]{7,20}$/.test(telefono)
      ? 'Revisa el número: solo dígitos, espacios, + o -.'
      : ''
  errores.correo = correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo) ? 'Revisa el correo, por ejemplo nombre@correo.com.' : ''
  return !Object.values(errores).some(Boolean)
}

async function guardar() {
  error.value = ''
  if (!validar()) return
  guardando.value = true
  const datos = {
    nombre: form.nombre.trim(),
    telefono: form.telefono.trim(),
    correo: form.correo.trim() || null,
  }
  try {
    if (editando.value) {
      await clientes.actualizar(props.cliente.cedula, datos)
    } else {
      await clientes.crear({ cedula: form.cedula.trim(), ...datos })
    }
    emit('guardado', editando.value ? 'Cambios guardados' : `${datos.nombre} agregado a clientes`)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo guardar el cliente.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <DialogoBase :abierto="abierto" :titulo="editando ? 'Editar cliente' : 'Nuevo cliente'" @cerrar="emit('cerrar')">
    <form class="formulario" novalidate @submit.prevent="guardar">
      <div class="campo">
        <label for="cl-cedula">Cédula</label>
        <input
          id="cl-cedula"
          v-model="form.cedula"
          class="entrada numero"
          inputmode="numeric"
          :disabled="editando"
          :autofocus="!editando"
          :aria-invalid="!!errores.cedula"
          :aria-describedby="editando ? 'cl-cedula-ayuda' : errores.cedula ? 'cl-cedula-error' : undefined"
        />
        <p v-if="editando" id="cl-cedula-ayuda" class="ayuda">La cédula identifica al cliente y no se puede cambiar.</p>
        <p v-if="errores.cedula" id="cl-cedula-error" class="error-campo">{{ errores.cedula }}</p>
      </div>
      <div class="campo">
        <label for="cl-nombre">Nombre completo</label>
        <input
          id="cl-nombre"
          v-model="form.nombre"
          class="entrada"
          autocomplete="off"
          :autofocus="editando"
          :aria-invalid="!!errores.nombre"
          :aria-describedby="errores.nombre ? 'cl-nombre-error' : undefined"
        />
        <p v-if="errores.nombre" id="cl-nombre-error" class="error-campo">{{ errores.nombre }}</p>
      </div>
      <div class="campos-dos">
        <div class="campo">
          <label for="cl-telefono">Teléfono</label>
          <input
            id="cl-telefono"
            v-model="form.telefono"
            class="entrada numero"
            type="tel"
            inputmode="tel"
            autocomplete="off"
            :aria-invalid="!!errores.telefono"
            :aria-describedby="errores.telefono ? 'cl-telefono-error' : undefined"
          />
          <p v-if="errores.telefono" id="cl-telefono-error" class="error-campo">{{ errores.telefono }}</p>
        </div>
        <div class="campo">
          <label for="cl-correo">Correo <span class="texto-secundario">(opcional)</span></label>
          <input
            id="cl-correo"
            v-model="form.correo"
            class="entrada"
            type="email"
            autocomplete="off"
            :aria-invalid="!!errores.correo"
            :aria-describedby="errores.correo ? 'cl-correo-error' : undefined"
          />
          <p v-if="errores.correo" id="cl-correo-error" class="error-campo">{{ errores.correo }}</p>
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
          @click="emit('eliminar', cliente)"
        >
          Eliminar cliente
        </button>
        <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Agregar cliente' }}
        </button>
      </div>
    </form>
  </DialogoBase>
</template>
