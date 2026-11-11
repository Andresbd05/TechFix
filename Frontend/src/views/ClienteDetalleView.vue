<script setup>
import { ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import clientesService from '@/services/clientesService'
import { useAvisosStore } from '@/stores/avisos'
import { useClientesStore } from '@/stores/clientes'
import { useAuthStore } from '@/stores/auth'
import DialogoConfirmar from '@/components/ui/DialogoConfirmar.vue'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import EtiquetaEstado from '@/components/ui/EtiquetaEstado.vue'
import Icono from '@/components/ui/Icono.vue'
import DialogoCliente from '@/components/clientes/DialogoCliente.vue'
import { nombreMarca } from '@/utils/marcas'
import { formatoFecha } from '@/utils/formato'
import { mensajeError } from '@/utils/errores'

const props = defineProps({
  cedula: { type: String, required: true },
})

const avisos = useAvisosStore()
const clientes = useClientesStore()
const auth = useAuthStore()
const router = useRouter()

const historial = ref(null)
const equipos = ref([])
const cargando = ref(true)
const noEncontrado = ref(false)
const error = ref('')

async function cargar() {
  cargando.value = true
  error.value = ''
  noEncontrado.value = false
  try {
    const [{ data: h }, { data: e }] = await Promise.all([
      clientesService.historial(props.cedula),
      clientesService.equipos(props.cedula),
    ])
    historial.value = h
    equipos.value = e.equipos
  } catch (e) {
    if (e.response?.status === 404) noEncontrado.value = true
    else error.value = mensajeError(e, 'No se pudo cargar el cliente.')
  } finally {
    cargando.value = false
  }
}

watch(() => props.cedula, cargar, { immediate: true })

const dialogoEditar = ref(false)

function alGuardar(mensaje) {
  dialogoEditar.value = false
  avisos.mostrar(mensaje)
  cargar()
}

/* ---------- Eliminar (se pide desde el diálogo de edición) ---------- */
const confirmarEliminar = ref(false)
const eliminando = ref(false)
const errorEliminar = ref('')

function pedirEliminar() {
  dialogoEditar.value = false
  errorEliminar.value = ''
  confirmarEliminar.value = true
}

async function eliminar() {
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await clientes.eliminar(props.cedula)
    confirmarEliminar.value = false
    avisos.mostrar(`${historial.value.cliente.nombre} eliminado`)
    router.push('/clientes')
  } catch (e) {
    errorEliminar.value = mensajeError(e, 'No se pudo eliminar el cliente.')
  } finally {
    eliminando.value = false
  }
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Cliente" volver-a="/clientes" volver-texto="Clientes">
      <button
        v-if="historial && auth.puedeGestionarClientes"
        type="button"
        class="btn btn-secundario btn-chico"
        @click="dialogoEditar = true"
      >
        Editar cliente
      </button>
    </BarraPagina>

    <div class="contenedor">
      <p v-if="cargando && !historial" class="cargando">Cargando cliente…</p>

      <div v-else-if="noEncontrado" class="vacio mt-3">
        <h1 class="titulo-pagina">No encontramos ese cliente</h1>
        <p class="mt-1">No hay ningún cliente con la cédula {{ cedula }}.</p>
        <RouterLink to="/clientes" class="btn btn-primario">Ver clientes</RouterLink>
      </div>

      <p v-else-if="error && !historial" class="alerta alerta-error mt-3" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <template v-else-if="historial">
        <header class="cabecera">
          <h1 class="titulo-pagina">{{ historial.cliente.nombre }}</h1>
          <dl class="datos">
            <div>
              <dt>Cédula</dt>
              <dd class="numero">{{ historial.cliente.cedula }}</dd>
            </div>
            <div>
              <dt>Teléfono</dt>
              <dd>
                <a :href="`tel:${historial.cliente.telefono}`" class="numero">{{ historial.cliente.telefono }}</a>
              </dd>
            </div>
            <div>
              <dt>Correo</dt>
              <dd>
                <a v-if="historial.cliente.correo" :href="`mailto:${historial.cliente.correo}`">
                  {{ historial.cliente.correo }}
                </a>
                <span v-else class="texto-secundario">Sin correo</span>
              </dd>
            </div>
          </dl>
        </header>

        <dl class="ficha mt-3">
          <div class="ficha-dato">
            <dt>Reparaciones</dt>
            <dd>{{ historial.total_reparaciones }}</dd>
          </div>
          <div class="ficha-dato">
            <dt>Sin entregar</dt>
            <dd>{{ historial.reparaciones_pendientes }}</dd>
          </div>
          <div class="ficha-dato">
            <dt>Equipos registrados</dt>
            <dd>{{ equipos.length }}</dd>
          </div>
        </dl>

        <section class="seccion" aria-labelledby="titulo-equipos">
          <h2 id="titulo-equipos" class="titulo-seccion">Equipos</h2>
          <div class="panel-plano mt-2">
            <p v-if="!equipos.length" class="vacio">Este cliente no tiene equipos registrados.</p>
            <ul v-else class="lista">
              <li v-for="eq in equipos" :key="eq.id_equipo" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1">{{ eq.tipo_dispositivo }} {{ nombreMarca(eq.id_marca) }}</span>
                  <span class="linea-2">{{ eq.id_equipo }}, serial {{ eq.serial_imei }}</span>
                </span>
                <RouterLink
                  v-if="auth.puedeGestionarReparaciones"
                  :to="{ name: 'reparaciones', query: { nueva: 1, cedula: historial.cliente.cedula, equipo: eq.id_equipo } }"
                  class="btn btn-contorno btn-chico"
                >
                  Nueva reparación<span class="sr-only"> para {{ eq.id_equipo }}</span>
                </RouterLink>
              </li>
            </ul>
          </div>
        </section>

        <section class="seccion" aria-labelledby="titulo-historial">
          <h2 id="titulo-historial" class="titulo-seccion">Historial de reparaciones</h2>
          <div class="panel-plano mt-2">
            <p v-if="!historial.reparaciones.length" class="vacio">Todavía no ha traído equipos a reparar.</p>
            <ul v-else class="lista">
              <li v-for="r in historial.reparaciones" :key="r.id_reparacion">
                <RouterLink :to="`/reparaciones/${r.id_reparacion}`" class="lista-item">
                  <span class="cuerpo">
                    <span class="linea-1">
                      <span class="mono-id">{{ r.id_reparacion }}</span>
                      <span class="equipo">{{ r.equipo }}</span>
                    </span>
                    <span class="linea-2">{{ r.diagnostico }}</span>
                  </span>
                  <span class="fecha texto-pequeno texto-secundario numero">{{ formatoFecha(r.fecha_ingreso) }}</span>
                  <EtiquetaEstado :estado="r.estado" />
                  <Icono nombre="chevron-derecha" class="chevron" />
                </RouterLink>
              </li>
            </ul>
          </div>
        </section>
      </template>
    </div>

    <DialogoCliente
      :abierto="dialogoEditar"
      :cliente="historial?.cliente || null"
      @cerrar="dialogoEditar = false"
      @guardado="alGuardar"
      @eliminar="pedirEliminar"
    />

    <DialogoConfirmar
      :abierto="confirmarEliminar"
      :titulo="`Eliminar a ${historial?.cliente.nombre || ''}`"
      texto-confirmar="Eliminar cliente"
      peligro
      :procesando="eliminando"
      :error="errorEliminar"
      @confirmar="eliminar"
      @cerrar="confirmarEliminar = false"
    >
      Se borrarán sus datos de contacto. Si tiene equipos registrados no se podrá eliminar.
    </DialogoConfirmar>
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 16px;
}

.datos {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 40px;
}

.datos dt {
  font-size: 13px;
  color: var(--color-texto-2);
}

.datos dd {
  font-size: 17px;
  font-weight: 500;
}

.equipo {
  font-weight: 400;
  color: var(--color-texto-2);
  margin-left: 8px;
}

@media (max-width: 600px) {
  .fecha {
    display: none;
  }
}
</style>
