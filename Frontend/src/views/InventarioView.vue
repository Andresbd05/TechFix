<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRepuestosStore } from '@/stores/repuestos'
import { useAvisosStore } from '@/stores/avisos'
import { useAuthStore } from '@/stores/auth'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import Icono from '@/components/ui/Icono.vue'
import DialogoConfirmar from '@/components/ui/DialogoConfirmar.vue'
import DialogoRepuesto from '@/components/inventario/DialogoRepuesto.vue'
import DialogoStock from '@/components/inventario/DialogoStock.vue'
import { MARCAS, nombreMarca } from '@/utils/marcas'
import { formatoPesos, formatoNumero, plural } from '@/utils/formato'
import { mensajeError } from '@/utils/errores'

const MINIMO_STOCK = 5

const repuestos = useRepuestosStore()
const avisos = useAvisosStore()
const auth = useAuthStore()

const cargando = ref(true)
const error = ref('')
const busqueda = ref('')
const filtroStock = ref('todos')
const filtroMarca = ref('')

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    // El valor del inventario (reportes) solo lo puede ver el propietario
    if (auth.puedeVerReportes) await repuestos.recargarTodo()
    else await repuestos.cargar()
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo cargar el inventario.')
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const unidades = computed(() => repuestos.lista.reduce((suma, r) => suma + r.stock, 0))
const porPedir = computed(() => repuestos.lista.filter((r) => r.stock <= MINIMO_STOCK).length)
const agotados = computed(() => repuestos.lista.filter((r) => r.stock === 0).length)

const visibles = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  return repuestos.lista
    .filter((r) => filtroStock.value !== 'bajo' || r.stock <= MINIMO_STOCK)
    .filter((r) => filtroStock.value !== 'agotados' || r.stock === 0)
    .filter((r) => filtroMarca.value === '' || String(r.id_marca ?? 'generico') === String(filtroMarca.value))
    .filter((r) => !texto || r.nombre.toLowerCase().includes(texto) || r.sku_repuesto.toLowerCase().includes(texto))
    .sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
})

function estadoStock(stock) {
  if (stock === 0) return { clase: 'agotado', texto: 'Agotado' }
  if (stock <= MINIMO_STOCK) return { clase: 'bajo', texto: 'Bajo' }
  return null
}

/* ---------- Diálogos ---------- */
const dialogoRepuesto = ref(false)
const repuestoEditando = ref(null)
const dialogoStock = ref(false)
const repuestoStock = ref(null)

function nuevo() {
  repuestoEditando.value = null
  dialogoRepuesto.value = true
}

function editar(r) {
  repuestoEditando.value = r
  dialogoRepuesto.value = true
}

function ajustar(r) {
  repuestoStock.value = r
  dialogoStock.value = true
}

function alGuardar(mensaje) {
  dialogoRepuesto.value = false
  dialogoStock.value = false
  avisos.mostrar(mensaje)
}

const porEliminar = ref(null)
const eliminando = ref(false)
const errorEliminar = ref('')

// Se pide desde el diálogo de edición: lo cerramos y abrimos la confirmación
function pedirEliminar(r) {
  dialogoRepuesto.value = false
  errorEliminar.value = ''
  porEliminar.value = r
}

async function eliminar() {
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await repuestos.eliminar(porEliminar.value.sku_repuesto)
    avisos.mostrar(`${porEliminar.value.nombre} eliminado del inventario`)
    porEliminar.value = null
  } catch (e) {
    errorEliminar.value = mensajeError(e, 'No se pudo eliminar el repuesto.')
  } finally {
    eliminando.value = false
  }
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Inventario">
      <button v-if="auth.puedeGestionarInventario" type="button" class="btn btn-primario btn-chico" @click="nuevo">
        <Icono nombre="mas" :tamano="14" />
        Nuevo repuesto
      </button>
    </BarraPagina>

    <div class="contenedor">
      <header class="cabecera">
        <h1 class="titulo-pagina">Inventario</h1>
        <p class="texto-intro">Repuestos disponibles para las reparaciones y cuánto vale lo que hay en bodega.</p>
      </header>

      <p v-if="error" class="alerta alerta-error mt-3" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <dl class="ficha mt-3">
        <div v-if="auth.puedeVerReportes" class="ficha-dato">
          <dt>Valor del inventario</dt>
          <dd>{{ formatoPesos(repuestos.valorTotal) }}</dd>
        </div>
        <div class="ficha-dato">
          <dt>Referencias</dt>
          <dd>{{ repuestos.lista.length }}</dd>
        </div>
        <div class="ficha-dato">
          <dt>Unidades</dt>
          <dd>{{ formatoNumero(unidades) }}</dd>
        </div>
        <div class="ficha-dato">
          <dt>Por pedir (≤ {{ MINIMO_STOCK }})</dt>
          <dd :class="{ 'dato-aviso': porPedir }">{{ porPedir }}</dd>
        </div>
      </dl>

      <div class="barra-filtros">
        <div class="segmentado" role="group" aria-label="Filtrar por stock">
          <button type="button" :aria-pressed="filtroStock === 'todos'" @click="filtroStock = 'todos'">Todos</button>
          <button type="button" :aria-pressed="filtroStock === 'bajo'" @click="filtroStock = 'bajo'">
            Stock bajo<span class="cuenta">{{ porPedir }}</span>
          </button>
          <button type="button" :aria-pressed="filtroStock === 'agotados'" @click="filtroStock = 'agotados'">
            Agotados<span class="cuenta">{{ agotados }}</span>
          </button>
        </div>
        <div class="buscador">
          <Icono nombre="buscar" :tamano="16" />
          <label for="buscar-repuesto" class="sr-only">Buscar repuesto</label>
          <input id="buscar-repuesto" v-model="busqueda" class="entrada" type="search" placeholder="Buscar por nombre o código" />
        </div>
        <div class="filtro-marca">
          <label for="filtro-marca" class="sr-only">Marca</label>
          <select id="filtro-marca" v-model="filtroMarca" class="entrada">
            <option value="">Todas las marcas</option>
            <option v-for="m in MARCAS" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            <option value="generico">Genéricos</option>
          </select>
        </div>
      </div>

      <div class="panel-plano">
        <p v-if="cargando && !repuestos.lista.length" class="cargando">Cargando inventario…</p>

        <div v-else-if="!visibles.length" class="vacio">
          <p class="titulo-bloque">{{ repuestos.lista.length ? 'Ningún repuesto coincide' : 'El inventario está vacío' }}</p>
          <p>{{ repuestos.lista.length ? 'Cambia los filtros o la búsqueda.' : 'Agrega el primer repuesto del taller.' }}</p>
          <button v-if="!repuestos.lista.length && auth.puedeGestionarInventario" type="button" class="btn btn-primario" @click="nuevo">Nuevo repuesto</button>
        </div>

        <table v-else class="tabla tabla-adaptable">
          <caption class="sr-only">{{ plural(visibles.length, 'repuesto', 'repuestos') }}</caption>
          <thead>
            <tr>
              <th scope="col">Repuesto</th>
              <th scope="col">Marca</th>
              <th scope="col" class="derecha">Precio</th>
              <th scope="col" class="derecha">Stock</th>
              <th scope="col"><span class="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in visibles" :key="r.sku_repuesto">
              <td class="celda-principal">
                <span class="nombre">{{ r.nombre }}</span>
                <span class="sku">{{ r.sku_repuesto }}</span>
              </td>
              <td data-etiqueta="Marca">{{ nombreMarca(r.id_marca) }}</td>
              <td data-etiqueta="Precio" class="derecha numero">{{ formatoPesos(r.precio) }}</td>
              <td data-etiqueta="Stock" class="derecha">
                <span class="stock numero">
                  {{ r.stock }}
                  <span v-if="estadoStock(r.stock)" class="aviso-stock" :class="estadoStock(r.stock).clase">
                    {{ estadoStock(r.stock).texto }}
                  </span>
                </span>
              </td>
              <td class="acciones-celda">
                <div v-if="auth.puedeGestionarInventario" class="acciones-fila">
                  <button type="button" class="btn btn-secundario btn-chico" @click="ajustar(r)">
                    Entrada o salida<span class="sr-only"> de {{ r.nombre }}</span>
                  </button>
                  <button type="button" class="btn-texto texto-pequeno" @click="editar(r)">
                    Editar<span class="sr-only"> {{ r.nombre }}</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <section v-if="auth.puedeVerReportes && repuestos.porMarca.length" class="seccion" aria-labelledby="titulo-marcas">
        <h2 id="titulo-marcas" class="titulo-seccion">Valor por marca</h2>
        <div class="panel-plano mt-2">
          <ul class="lista">
            <li v-for="m in repuestos.porMarca" :key="m.marca" class="lista-item">
              <span class="cuerpo">
                <span class="linea-1">{{ m.marca }}</span>
                <span class="linea-2">
                  {{ plural(m.referencias, 'referencia', 'referencias') }}, {{ plural(m.unidades, 'unidad', 'unidades') }}
                </span>
              </span>
              <span class="numero valor-marca">{{ formatoPesos(m.valor) }}</span>
            </li>
          </ul>
        </div>
      </section>
    </div>

    <DialogoRepuesto
      :abierto="dialogoRepuesto"
      :repuesto="repuestoEditando"
      @cerrar="dialogoRepuesto = false"
      @guardado="alGuardar"
      @eliminar="pedirEliminar"
    />
    <DialogoStock :abierto="dialogoStock" :repuesto="repuestoStock" @cerrar="dialogoStock = false" @guardado="alGuardar" />
    <DialogoConfirmar
      :abierto="!!porEliminar"
      :titulo="`Eliminar ${porEliminar?.nombre || ''}`"
      texto-confirmar="Eliminar repuesto"
      peligro
      :procesando="eliminando"
      :error="errorEliminar"
      @confirmar="eliminar"
      @cerrar="porEliminar = null"
    >
      Se quitará del inventario. Si ya se usó en alguna reparación no se podrá eliminar.
    </DialogoConfirmar>
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 10px;
}

.ficha-dato dd.dato-aviso {
  color: var(--color-aviso);
}

.filtro-marca .entrada {
  min-height: 40px;
  font-size: 15px;
  background-color: var(--color-linea-suave);
  border-color: transparent;
  width: auto;
}

.nombre {
  display: block;
  font-weight: 500;
}

.sku {
  font-size: 13px;
  color: var(--color-texto-2);
}

.stock {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.aviso-stock {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 980px;
}

.aviso-stock.bajo {
  background: var(--color-aviso-suave);
  color: var(--color-aviso);
}

.aviso-stock.agotado {
  background: var(--color-peligro-suave);
  color: var(--color-peligro);
}

.valor-marca {
  font-weight: 600;
}
</style>
