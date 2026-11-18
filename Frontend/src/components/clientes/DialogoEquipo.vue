<script setup>
import { computed, reactive, ref, watch } from 'vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import clientesService from '@/services/clientesService'
import { MARCAS } from '@/utils/marcas'
import { mensajeError } from '@/utils/errores'

// Registra un equipo nuevo para un cliente. El código del equipo se genera
// solo (con un prefijo según el tipo) pero se puede cambiar a mano.
const props = defineProps({
  abierto: { type: Boolean, default: false },
  cedula: { type: String, required: true },
  nombreCliente: { type: String, default: '' },
})
const emit = defineEmits(['cerrar', 'guardado'])

const TIPOS = ['Telefono', 'Computador', 'Tablet', 'Otro']

const form = reactive({ tipo: 'Telefono', tipoOtro: '', id_equipo: '', id_marca: '', serial_imei: '' })
const errores = reactive({ tipo: '', id_equipo: '', serial_imei: '' })
const sufijo = ref('')
const idEditado = ref(false)
const guardando = ref(false)
const error = ref('')

// El tipo real: si eligió "Otro", vale lo que escriba
const tipoEfectivo = computed(() => (form.tipo === 'Otro' ? form.tipoOtro.trim() : form.tipo))

function prefijoTipo(tipo) {
  const t = (tipo || '').toLowerCase()
  if (t.startsWith('tel') || t.startsWith('cel') || t.startsWith('móv') || t.startsWith('mov')) return 'TEL'
  if (t.startsWith('com') || t.startsWith('por') || t.startsWith('lap') || t.startsWith('pc')) return 'COM'
  if (t.startsWith('tab')) return 'TAB'
  return 'EQP'
}

function sufijoAleatorio() {
  const letras = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let s = ''
  for (let i = 0; i < 4; i++) s += letras[Math.floor(Math.random() * letras.length)]
  return s
}

function codigoSugerido() {
  return `${prefijoTipo(tipoEfectivo.value)}-${sufijo.value}`
}

function reiniciar() {
  Object.assign(form, { tipo: 'Telefono', tipoOtro: '', id_marca: '', serial_imei: '' })
  Object.assign(errores, { tipo: '', id_equipo: '', serial_imei: '' })
  sufijo.value = sufijoAleatorio()
  idEditado.value = false
  form.id_equipo = codigoSugerido()
  error.value = ''
}

watch(
  () => props.abierto,
  (abierto) => abierto && reiniciar(),
  { immediate: true },
)

// Mientras el usuario no toque el código a mano, lo mantenemos al día con el tipo
watch([() => form.tipo, () => form.tipoOtro], () => {
  if (!idEditado.value) form.id_equipo = codigoSugerido()
})

function validar() {
  errores.tipo = tipoEfectivo.value ? '' : 'Indica qué tipo de equipo es.'
  const id = form.id_equipo.trim()
  errores.id_equipo = !id
    ? 'El equipo necesita un código.'
    : id.length > 20
      ? 'Máximo 20 caracteres.'
      : ''
  errores.serial_imei = form.serial_imei.trim().length > 50 ? 'Máximo 50 caracteres.' : ''
  return !Object.values(errores).some(Boolean)
}

async function guardar() {
  error.value = ''
  if (!validar()) return
  guardando.value = true
  const datos = {
    id_equipo: form.id_equipo.trim().toUpperCase(),
    tipo_dispositivo: tipoEfectivo.value,
    id_marca: form.id_marca === '' ? null : Number(form.id_marca),
    serial_imei: form.serial_imei.trim() || null,
  }
  try {
    await clientesService.crearEquipo(props.cedula, datos)
    emit('guardado', `Equipo ${datos.id_equipo} agregado`)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo registrar el equipo.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <DialogoBase
    :abierto="abierto"
    titulo="Agregar equipo"
    :descripcion="nombreCliente ? `Registra un dispositivo de ${nombreCliente}.` : 'Registra un dispositivo del cliente.'"
    ancho="520px"
    @cerrar="emit('cerrar')"
  >
    <form class="formulario" novalidate @submit.prevent="guardar">
      <div class="campos-dos">
        <div class="campo">
          <label for="eq-tipo">Tipo de equipo</label>
          <select
            id="eq-tipo"
            v-model="form.tipo"
            class="entrada"
            :aria-invalid="!!errores.tipo"
          >
            <option value="Telefono">Teléfono</option>
            <option value="Computador">Computador</option>
            <option value="Tablet">Tablet</option>
            <option value="Otro">Otro…</option>
          </select>
        </div>
        <div v-if="form.tipo === 'Otro'" class="campo">
          <label for="eq-tipo-otro">¿Qué equipo es?</label>
          <input
            id="eq-tipo-otro"
            v-model="form.tipoOtro"
            class="entrada"
            placeholder="Ej.: Consola, Impresora"
            autocomplete="off"
            :aria-invalid="!!errores.tipo"
          />
        </div>
      </div>
      <p v-if="errores.tipo" class="error-campo">{{ errores.tipo }}</p>

      <div class="campo">
        <label for="eq-codigo">Código del equipo</label>
        <input
          id="eq-codigo"
          v-model="form.id_equipo"
          class="entrada mono-id"
          maxlength="20"
          autocomplete="off"
          :aria-invalid="!!errores.id_equipo"
          aria-describedby="eq-codigo-ayuda"
          @input="idEditado = true"
        />
        <p id="eq-codigo-ayuda" class="ayuda">Lo generamos por ti. Puedes cambiarlo si usas otro código.</p>
        <p v-if="errores.id_equipo" class="error-campo">{{ errores.id_equipo }}</p>
      </div>

      <div class="campos-dos">
        <div class="campo">
          <label for="eq-marca">Marca <span class="texto-secundario">(opcional)</span></label>
          <select id="eq-marca" v-model="form.id_marca" class="entrada">
            <option value="">Sin marca</option>
            <option v-for="m in MARCAS" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
        <div class="campo">
          <label for="eq-serial">Serial / IMEI <span class="texto-secundario">(opcional)</span></label>
          <input
            id="eq-serial"
            v-model="form.serial_imei"
            class="entrada mono-id"
            maxlength="50"
            autocomplete="off"
            :aria-invalid="!!errores.serial_imei"
            :aria-describedby="errores.serial_imei ? 'eq-serial-error' : undefined"
          />
          <p v-if="errores.serial_imei" id="eq-serial-error" class="error-campo">{{ errores.serial_imei }}</p>
        </div>
      </div>

      <p v-if="error" class="alerta alerta-error" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <div class="acciones-dialogo">
        <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Guardando…' : 'Agregar equipo' }}
        </button>
      </div>
    </form>
  </DialogoBase>
</template>

<style scoped>
select.entrada {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='none' stroke='%238a8a8e' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' d='M1 1.5 6 6.5 11 1.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 38px;
  cursor: pointer;
}
</style>
