<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useReparacionesStore } from '@/stores/reparaciones'
import { useAvisosStore } from '@/stores/avisos'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import EtiquetaEstado from '@/components/ui/EtiquetaEstado.vue'
import Icono from '@/components/ui/Icono.vue'
import DialogoNuevaReparacion from '@/components/reparaciones/DialogoNuevaReparacion.vue'
import { ESTADOS } from '@/utils/estados'
import { formatoFecha, fechaOrdenable, plural } from '@/utils/formato'
import { mensajeError } from '@/utils/errores'

const auth = useAuthStore()
const reparaciones = useReparacionesStore()
const avisos = useAvisosStore()
const route = useRoute()
const router = useRouter()

const cargando = ref(true)
const error = ref('')
const busqueda = ref('')
const soloMias = ref(false)

// El filtro de estado vive en la URL (?estado=Listo) para poder compartirlo
const estadoFiltro = computed(() => (ESTADOS.includes(route.query.estado) ? route.query.estado : ''))

function filtrarPor(estado) {
  const query = { ...route.query }
  if (estado) query.estado = estado
  else delete query.estado
  router.replace({ query })
}

// ?nueva=1 abre el formulario (lo usan Inicio y la ficha del cliente)
const dialogoNueva = computed(() => route.query.nueva === '1')

function abrirNueva() {
  router.replace({ query: { ...route.query, nueva: '1' } })
}

function cerrarNueva() {
  const query = { ...route.query }
  delete query.nueva
  delete query.cedula
  delete query.equipo
  router.replace({ query })
}

function alCrear(id) {
  avisos.mostrar(`Reparación ${id} creada`)
  router.push(`/reparaciones/${id}`)
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    await reparaciones.cargar()
  } catch (e) {
    error.value = mensajeError(e, 'No se pudieron cargar las reparaciones.')
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const visibles = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  return reparaciones.lista
    .filter((r) => !estadoFiltro.value || r.estado === estadoFiltro.value)
    .filter((r) => !soloMias.value || r.cedula_tecnico === auth.cedulaTecnico)
    .filter(
      (r) =>
        !texto ||
        r.id_reparacion.toLowerCase().includes(texto) ||
        r.id_equipo.toLowerCase().includes(texto) ||
        r.diagnostico.toLowerCase().includes(texto),
    )
    .sort((a, b) => fechaOrdenable(b.fecha_ingreso) - fechaOrdenable(a.fecha_ingreso))
})

watch(busqueda, () => {
  if (busqueda.value && estadoFiltro.value) filtrarPor('')
})

function tecnicoTexto(cedula) {
  if (!cedula) return 'Sin asignar'
  return cedula === auth.cedulaTecnico ? 'Tú' : cedula
}

function abrir(r) {
  router.push(`/reparaciones/${r.id_reparacion}`)
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Reparaciones">
      <button v-if="auth.puedeGestionarReparaciones" type="button" class="btn btn-primario btn-chico" @click="abrirNueva">
        <Icono nombre="mas" :tamano="14" />
        Nueva reparación
      </button>
    </BarraPagina>

    <div class="contenedor">
      <header class="cabecera">
        <h1 class="titulo-pagina">Reparaciones</h1>
        <p class="texto-intro">Cada equipo que entra al taller, desde que se recibe hasta que se entrega.</p>
      </header>

      <div class="barra-filtros">
        <div class="segmentado" role="group" aria-label="Filtrar por etapa">
          <button type="button" :aria-pressed="!estadoFiltro" @click="filtrarPor('')">
            Todas<span class="cuenta">{{ reparaciones.lista.length }}</span>
          </button>
          <button
            v-for="estado in ESTADOS"
            :key="estado"
            type="button"
            :aria-pressed="estadoFiltro === estado"
            @click="filtrarPor(estado)"
          >
            {{ estado }}<span class="cuenta">{{ reparaciones.conteoPorEstado[estado] }}</span>
          </button>
        </div>
      </div>

      <div class="fila separado barra-secundaria">
        <div class="buscador">
          <Icono nombre="buscar" :tamano="16" />
          <label for="buscar-reparacion" class="sr-only">Buscar reparación</label>
          <input
            id="buscar-reparacion"
            v-model="busqueda"
            class="entrada"
            type="search"
            placeholder="Buscar por código, equipo o diagnóstico"
          />
        </div>
        <label v-if="auth.cedulaTecnico" class="interruptor">
          <input v-model="soloMias" type="checkbox" />
          Solo las mías
        </label>
      </div>

      <p v-if="error" class="alerta alerta-error mt-2" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <div class="panel-plano mt-2">
        <p v-if="cargando" class="cargando">Cargando reparaciones…</p>

        <div v-else-if="!visibles.length" class="vacio">
          <p class="titulo-bloque">
            {{ reparaciones.lista.length ? 'Ninguna reparación coincide' : 'Aún no hay reparaciones' }}
          </p>
          <p>
            {{
              reparaciones.lista.length
                ? 'Prueba con otra etapa o cambia la búsqueda.'
                : 'Registra el primer equipo que llegue al taller.'
            }}
          </p>
          <button
            v-if="!reparaciones.lista.length && auth.puedeGestionarReparaciones"
            type="button"
            class="btn btn-primario"
            @click="abrirNueva"
          >
            Nueva reparación
          </button>
        </div>

        <table v-else class="tabla tabla-adaptable">
          <caption class="sr-only">
            {{ plural(visibles.length, 'reparación', 'reparaciones') }}
            {{ estadoFiltro ? `en ${estadoFiltro}` : '' }}
          </caption>
          <thead>
            <tr>
              <th scope="col">Reparación</th>
              <th scope="col">Equipo</th>
              <th scope="col">Técnico</th>
              <th scope="col">Etapa</th>
              <th scope="col">Ingreso</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in visibles" :key="r.id_reparacion" class="fila-enlace" @click="abrir(r)">
              <td class="celda-principal">
                <RouterLink :to="`/reparaciones/${r.id_reparacion}`" class="mono-id" @click.stop>
                  {{ r.id_reparacion }}
                </RouterLink>
                <span class="diagnostico">{{ r.diagnostico }}</span>
              </td>
              <td data-etiqueta="Equipo">{{ r.id_equipo }}</td>
              <td data-etiqueta="Técnico" :class="{ 'texto-secundario': !r.cedula_tecnico }">
                {{ tecnicoTexto(r.cedula_tecnico) }}
              </td>
              <td data-etiqueta="Etapa"><EtiquetaEstado :estado="r.estado" /></td>
              <td data-etiqueta="Ingreso" class="numero texto-secundario">{{ formatoFecha(r.fecha_ingreso) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <DialogoNuevaReparacion
      :abierto="dialogoNueva"
      :cedula-inicial="route.query.cedula || ''"
      :equipo-inicial="route.query.equipo || ''"
      @cerrar="cerrarNueva"
      @creada="alCrear"
    />
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 10px;
}

.barra-secundaria {
  margin-top: 4px;
}

.diagnostico {
  display: block;
  font-size: 14px;
  color: var(--color-texto-2);
  max-width: 32ch;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 760px) {
  .diagnostico {
    max-width: none;
    white-space: normal;
  }
}
</style>
