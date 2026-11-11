<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useClientesStore } from '@/stores/clientes'
import { useAvisosStore } from '@/stores/avisos'
import { useAuthStore } from '@/stores/auth'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import Icono from '@/components/ui/Icono.vue'
import DialogoConfirmar from '@/components/ui/DialogoConfirmar.vue'
import DialogoCliente from '@/components/clientes/DialogoCliente.vue'
import { plural } from '@/utils/formato'
import { mensajeError } from '@/utils/errores'

const clientes = useClientesStore()
const avisos = useAvisosStore()
const auth = useAuthStore()
const router = useRouter()

const cargando = ref(true)
const error = ref('')
const busqueda = ref('')

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const texto = busqueda.value.trim()
    // /clientes/buscar exige al menos 2 caracteres
    if (texto.length >= 2) await clientes.buscar(texto)
    else await clientes.cargar()
  } catch (e) {
    error.value = mensajeError(e, 'No se pudieron cargar los clientes.')
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

// Espera a que la persona deje de escribir antes de buscar
let temporizador
watch(busqueda, () => {
  clearTimeout(temporizador)
  temporizador = setTimeout(cargar, 300)
})

/* ---------- Crear / editar ---------- */
const dialogo = ref(false)
const clienteEditando = ref(null)

function nuevo() {
  clienteEditando.value = null
  dialogo.value = true
}

function editar(cliente) {
  clienteEditando.value = cliente
  dialogo.value = true
}

function alGuardar(mensaje) {
  dialogo.value = false
  avisos.mostrar(mensaje)
}

/* ---------- Eliminar ---------- */
const porEliminar = ref(null)
const eliminando = ref(false)
const errorEliminar = ref('')

// Se pide desde el diálogo de edición: lo cerramos y abrimos la confirmación
function pedirEliminar(cliente) {
  dialogo.value = false
  errorEliminar.value = ''
  porEliminar.value = cliente
}

async function eliminar() {
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await clientes.eliminar(porEliminar.value.cedula)
    avisos.mostrar(`${porEliminar.value.nombre} eliminado`)
    porEliminar.value = null
  } catch (e) {
    errorEliminar.value = mensajeError(e, 'No se pudo eliminar el cliente.')
  } finally {
    eliminando.value = false
  }
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Clientes">
      <button v-if="auth.puedeGestionarClientes" type="button" class="btn btn-primario btn-chico" @click="nuevo">
        <Icono nombre="mas" :tamano="14" />
        Nuevo cliente
      </button>
    </BarraPagina>

    <div class="contenedor">
      <header class="cabecera">
        <h1 class="titulo-pagina">Clientes</h1>
        <p class="texto-intro">Las personas que traen sus equipos al taller y su historial de reparaciones.</p>
      </header>

      <div class="barra-filtros">
        <div class="buscador">
          <Icono nombre="buscar" :tamano="16" />
          <label for="buscar-cliente" class="sr-only">Buscar cliente</label>
          <input
            id="buscar-cliente"
            v-model="busqueda"
            class="entrada"
            type="search"
            placeholder="Buscar por nombre, cédula o teléfono"
          />
        </div>
        <p class="texto-secundario texto-pequeno" aria-live="polite">
          {{ cargando ? '' : plural(clientes.lista.length, 'cliente', 'clientes') }}
        </p>
      </div>

      <p v-if="error" class="alerta alerta-error mb" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <div class="panel-plano">
        <p v-if="cargando && !clientes.lista.length" class="cargando">Cargando clientes…</p>

        <div v-else-if="!clientes.lista.length" class="vacio">
          <p class="titulo-bloque">{{ busqueda.trim() ? 'Sin resultados' : 'Aún no hay clientes' }}</p>
          <p>
            {{
              busqueda.trim().length === 1
                ? 'Escribe al menos 2 caracteres para buscar.'
                : busqueda.trim()
                  ? `Nadie coincide con «${busqueda.trim()}».`
                  : 'Agrega al primer cliente para registrar sus equipos.'
            }}
          </p>
          <button v-if="!busqueda.trim() && auth.puedeGestionarClientes" type="button" class="btn btn-primario" @click="nuevo">Nuevo cliente</button>
        </div>

        <table v-else class="tabla tabla-adaptable">
          <caption class="sr-only">Clientes</caption>
          <thead>
            <tr>
              <th scope="col">Nombre</th>
              <th scope="col">Cédula</th>
              <th scope="col">Teléfono</th>
              <th scope="col">Correo</th>
              <th scope="col"><span class="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in clientes.lista"
              :key="c.cedula"
              class="fila-enlace"
              @click="router.push(`/clientes/${c.cedula}`)"
            >
              <td class="celda-principal">
                <RouterLink :to="`/clientes/${c.cedula}`" class="nombre" @click.stop>{{ c.nombre }}</RouterLink>
              </td>
              <td data-etiqueta="Cédula" class="numero">{{ c.cedula }}</td>
              <td data-etiqueta="Teléfono" class="numero">{{ c.telefono }}</td>
              <td data-etiqueta="Correo" :class="{ 'texto-secundario': !c.correo }">{{ c.correo || 'Sin correo' }}</td>
              <td class="acciones-celda">
                <div v-if="auth.puedeGestionarClientes" class="acciones-fila">
                  <button type="button" class="btn btn-secundario btn-chico" @click.stop="editar(c)">
                    Editar<span class="sr-only"> a {{ c.nombre }}</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <DialogoCliente
      :abierto="dialogo"
      :cliente="clienteEditando"
      @cerrar="dialogo = false"
      @guardado="alGuardar"
      @eliminar="pedirEliminar"
    />

    <DialogoConfirmar
      :abierto="!!porEliminar"
      :titulo="`Eliminar a ${porEliminar?.nombre || ''}`"
      texto-confirmar="Eliminar cliente"
      peligro
      :procesando="eliminando"
      :error="errorEliminar"
      @confirmar="eliminar"
      @cerrar="porEliminar = null"
    >
      Se borrarán sus datos de contacto. Si tiene equipos registrados no se podrá eliminar.
    </DialogoConfirmar>
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 10px;
}

.nombre {
  font-weight: 600;
  color: var(--color-texto);
}

.mb {
  margin-bottom: 16px;
}
</style>
