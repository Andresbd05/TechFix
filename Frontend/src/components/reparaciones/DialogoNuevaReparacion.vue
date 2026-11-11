<script setup>
import { reactive, ref, watch } from 'vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import clientesService from '@/services/clientesService'
import { useReparacionesStore } from '@/stores/reparaciones'
import { nombreMarca } from '@/utils/marcas'
import { mensajeError } from '@/utils/errores'

// Crear una reparación: 1) buscar al cliente por cédula, 2) elegir uno de
// sus equipos, 3) escribir el diagnóstico.
const props = defineProps({
  abierto: { type: Boolean, default: false },
  cedulaInicial: { type: String, default: '' },
  equipoInicial: { type: String, default: '' },
})
const emit = defineEmits(['cerrar', 'creada'])

const reparaciones = useReparacionesStore()

const form = reactive({ cedula: '', id_equipo: '', id_reparacion: '', diagnostico: '' })
const errores = reactive({ cedula: '', id_equipo: '', id_reparacion: '', diagnostico: '' })
const cliente = ref(null)
const equipos = ref([])
const buscando = ref(false)
const guardando = ref(false)
const error = ref('')

function nuevoId() {
  const letras = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let id = 'REP-'
  for (let i = 0; i < 4; i++) id += letras[Math.floor(Math.random() * letras.length)]
  return id
}

function reiniciar() {
  Object.assign(form, { cedula: props.cedulaInicial, id_equipo: '', id_reparacion: nuevoId(), diagnostico: '' })
  Object.assign(errores, { cedula: '', id_equipo: '', id_reparacion: '', diagnostico: '' })
  cliente.value = null
  equipos.value = []
  error.value = ''
  if (props.cedulaInicial) buscarEquipos()
}

watch(
  () => props.abierto,
  (abierto) => abierto && reiniciar(),
  { immediate: true },
)

async function buscarEquipos() {
  errores.cedula = form.cedula.trim() ? '' : 'Escribe la cédula del cliente.'
  if (errores.cedula) return
  buscando.value = true
  cliente.value = null
  equipos.value = []
  form.id_equipo = ''
  try {
    const cedula = form.cedula.trim()
    const [{ data: c }, { data: e }] = await Promise.all([
      clientesService.obtener(cedula),
      clientesService.equipos(cedula),
    ])
    cliente.value = c.cliente
    equipos.value = e.equipos
    if (props.equipoInicial && e.equipos.some((x) => x.id_equipo === props.equipoInicial)) {
      form.id_equipo = props.equipoInicial
    } else if (e.equipos.length === 1) {
      form.id_equipo = e.equipos[0].id_equipo
    }
  } catch (e) {
    errores.cedula =
      e.response?.status === 404 ? 'No hay ningún cliente con esa cédula.' : mensajeError(e)
  } finally {
    buscando.value = false
  }
}

function validar() {
  errores.cedula = cliente.value ? '' : 'Busca primero al cliente.'
  errores.id_equipo = form.id_equipo ? '' : 'Elige el equipo que deja el cliente.'
  errores.id_reparacion = form.id_reparacion.trim()
    ? form.id_reparacion.trim().length > 20
      ? 'Máximo 20 caracteres.'
      : ''
    : 'Escribe un código para la reparación.'
  errores.diagnostico = form.diagnostico.trim() ? '' : 'Describe qué le pasa al equipo.'
  return !Object.values(errores).some(Boolean)
}

async function crear() {
  error.value = ''
  if (!validar()) return
  guardando.value = true
  const id = form.id_reparacion.trim().toUpperCase()
  try {
    await reparaciones.crear({
      id_reparacion: id,
      id_equipo: form.id_equipo,
      diagnostico: form.diagnostico.trim(),
    })
    emit('creada', id)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo crear la reparación.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <DialogoBase
    :abierto="abierto"
    titulo="Nueva reparación"
    descripcion="Registra el equipo que llega al taller."
    ancho="560px"
    @cerrar="emit('cerrar')"
  >
    <form class="formulario" novalidate @submit.prevent="crear">
      <div class="campo">
        <label for="nr-cedula">Cédula del cliente</label>
        <div class="fila buscar-cliente">
          <input
            id="nr-cedula"
            v-model="form.cedula"
            class="entrada"
            inputmode="numeric"
            autocomplete="off"
            autofocus
            :aria-invalid="!!errores.cedula"
            :aria-describedby="errores.cedula ? 'nr-cedula-error' : undefined"
            @keydown.enter.prevent="buscarEquipos"
          />
          <button type="button" class="btn btn-secundario" :disabled="buscando" @click="buscarEquipos">
            {{ buscando ? 'Buscando…' : 'Buscar' }}
          </button>
        </div>
        <p v-if="errores.cedula" id="nr-cedula-error" class="error-campo">{{ errores.cedula }}</p>
      </div>

      <fieldset v-if="cliente" class="campo equipos">
        <legend class="etiqueta">Equipo de {{ cliente.nombre }}</legend>
        <p v-if="!equipos.length" class="texto-secundario texto-pequeno">
          Este cliente no tiene equipos registrados.
        </p>
        <label v-for="eq in equipos" :key="eq.id_equipo" class="opcion-equipo">
          <input v-model="form.id_equipo" type="radio" name="equipo" :value="eq.id_equipo" />
          <span class="opcion-texto">
            <span class="linea-1">{{ eq.tipo_dispositivo }} {{ nombreMarca(eq.id_marca) }}</span>
            <span class="linea-2">{{ eq.id_equipo }}, serial {{ eq.serial_imei }}</span>
          </span>
        </label>
        <p v-if="errores.id_equipo" class="error-campo">{{ errores.id_equipo }}</p>
      </fieldset>

      <div class="campo">
        <label for="nr-id">Código de la reparación</label>
        <input
          id="nr-id"
          v-model="form.id_reparacion"
          class="entrada mono-id"
          maxlength="20"
          :aria-invalid="!!errores.id_reparacion"
          aria-describedby="nr-id-ayuda"
        />
        <p id="nr-id-ayuda" class="ayuda">Lo generamos por ti. Puedes cambiarlo si usas otro código.</p>
        <p v-if="errores.id_reparacion" class="error-campo">{{ errores.id_reparacion }}</p>
      </div>

      <div class="campo">
        <label for="nr-diagnostico">Diagnóstico</label>
        <textarea
          id="nr-diagnostico"
          v-model="form.diagnostico"
          class="entrada"
          placeholder="Ej.: pantalla rota, el táctil no responde"
          :aria-invalid="!!errores.diagnostico"
          :aria-describedby="errores.diagnostico ? 'nr-diagnostico-error' : undefined"
        ></textarea>
        <p v-if="errores.diagnostico" id="nr-diagnostico-error" class="error-campo">{{ errores.diagnostico }}</p>
      </div>

      <p v-if="error" class="alerta alerta-error" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <div class="acciones-dialogo">
        <button type="button" class="btn btn-secundario" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primario" :disabled="guardando">
          {{ guardando ? 'Creando…' : 'Crear reparación' }}
        </button>
      </div>
    </form>
  </DialogoBase>
</template>

<style scoped>
.buscar-cliente {
  flex-wrap: nowrap;
}

.buscar-cliente .entrada {
  flex: 1;
}

.equipos {
  border: none;
  padding: 0;
  gap: 8px;
}

.equipos legend {
  margin-bottom: 8px;
}

.opcion-equipo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid var(--color-linea);
  border-radius: 12px;
  cursor: pointer;
  font-weight: 400;
}

.opcion-equipo:has(input:checked) {
  border-color: var(--color-accion);
  box-shadow: 0 0 0 1px var(--color-accion);
}

.opcion-equipo input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-accion);
}

.opcion-texto {
  display: grid;
}

.linea-1 {
  font-weight: 600;
  font-size: 15px;
}

.linea-2 {
  font-size: 13px;
  color: var(--color-texto-2);
}
</style>
