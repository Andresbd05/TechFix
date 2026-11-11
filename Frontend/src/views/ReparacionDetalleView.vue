<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAvisosStore } from '@/stores/avisos'
import { useReparacionesStore } from '@/stores/reparaciones'
import { useRepuestosStore } from '@/stores/repuestos'
import reparacionesService from '@/services/reparacionesService'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import EtiquetaEstado from '@/components/ui/EtiquetaEstado.vue'
import Icono from '@/components/ui/Icono.vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import DialogoConfirmar from '@/components/ui/DialogoConfirmar.vue'
import ProgresoReparacion from '@/components/reparaciones/ProgresoReparacion.vue'
import { SIGUIENTE_ESTADO, estaTerminada } from '@/utils/estados'
import { formatoPesos, formatoFechaHora } from '@/utils/formato'
import { mensajeError } from '@/utils/errores'

const props = defineProps({
  id: { type: String, required: true },
})

const router = useRouter()
const auth = useAuthStore()
const avisos = useAvisosStore()
const reparaciones = useReparacionesStore()
const repuestos = useRepuestosStore()

const reparacion = ref(null)
const cotizacion = ref(null)
const cargando = ref(true)
const noEncontrada = ref(false)
const error = ref('')

async function cargar() {
  cargando.value = true
  error.value = ''
  noEncontrada.value = false
  try {
    const [{ data: r }, { data: c }] = await Promise.all([
      reparacionesService.obtener(props.id),
      reparacionesService.cotizacion(props.id),
    ])
    reparacion.value = r.reparacion
    cotizacion.value = c
  } catch (e) {
    if (e.response?.status === 404) noEncontrada.value = true
    else error.value = mensajeError(e, 'No se pudo cargar la reparación.')
  } finally {
    cargando.value = false
  }
}

watch(() => props.id, cargar, { immediate: true })

const siguiente = computed(() => SIGUIENTE_ESTADO[reparacion.value?.estado])
const terminada = computed(() => estaTerminada(reparacion.value?.estado))
// El backend vuelve a verificar esto; aquí solo decide qué botones mostrar
// Propietario y admin pueden con cualquiera; el técnico solo con las suyas; el invitado no
const puedeModificar = computed(() => auth.puedeTrabajarReparacion(reparacion.value?.cedula_tecnico))

function textoTecnico(cedula) {
  if (!cedula) return 'Sin asignar'
  return cedula === auth.cedulaTecnico ? `Tú (${cedula})` : `Cédula ${cedula}`
}

/* ---------- Avanzar de etapa ---------- */
const avanzando = ref(false)
const errorAvance = ref('')
const confirmarEntrega = ref(false)

function pedirAvance() {
  errorAvance.value = ''
  if (siguiente.value === 'Entregado') confirmarEntrega.value = true
  else avanzar()
}

async function avanzar() {
  avanzando.value = true
  errorAvance.value = ''
  try {
    const { data } = await reparacionesService.avanzar(props.id)
    confirmarEntrega.value = false
    avisos.mostrar(`${props.id} pasó a ${data.estado_nuevo}`)
    await cargar()
  } catch (e) {
    errorAvance.value = mensajeError(e, 'No se pudo cambiar la etapa.')
  } finally {
    avanzando.value = false
  }
}

/* ---------- Asignar técnico (solo admin) ---------- */
const cedulaAsignar = ref('')
const asignando = ref(false)
const errorAsignar = ref('')
const cedulasConocidas = computed(() => [
  ...new Set(reparaciones.lista.map((r) => r.cedula_tecnico).filter(Boolean)),
])

watch(
  () => auth.esAdmin,
  (esAdmin) => esAdmin && !reparaciones.lista.length && reparaciones.cargar().catch(() => {}),
  { immediate: true },
)

async function asignar() {
  errorAsignar.value = cedulaAsignar.value.trim() ? '' : 'Escribe la cédula del técnico.'
  if (errorAsignar.value) return
  asignando.value = true
  try {
    const { data } = await reparacionesService.asignarTecnico(props.id, cedulaAsignar.value.trim())
    avisos.mostrar(data.mensaje)
    cedulaAsignar.value = ''
    await Promise.all([cargar(), reparaciones.cargar()])
  } catch (e) {
    errorAsignar.value = mensajeError(e, 'No se pudo asignar el técnico.')
  } finally {
    asignando.value = false
  }
}

/* ---------- Agregar repuesto ---------- */
const dialogoRepuesto = ref(false)
const formRepuesto = reactive({ sku: '', cantidad: 1 })
const erroresRepuesto = reactive({ sku: '', cantidad: '' })
const guardandoRepuesto = ref(false)
const errorRepuesto = ref('')

const repuestoElegido = computed(() => repuestos.lista.find((r) => r.sku_repuesto === formRepuesto.sku))

async function abrirRepuesto() {
  Object.assign(formRepuesto, { sku: '', cantidad: 1 })
  Object.assign(erroresRepuesto, { sku: '', cantidad: '' })
  errorRepuesto.value = ''
  dialogoRepuesto.value = true
  try {
    await repuestos.cargar()
  } catch (e) {
    errorRepuesto.value = mensajeError(e, 'No se pudo cargar el inventario.')
  }
}

async function agregarRepuesto() {
  const cantidad = Number(formRepuesto.cantidad)
  erroresRepuesto.sku = formRepuesto.sku ? '' : 'Elige un repuesto.'
  erroresRepuesto.cantidad =
    Number.isInteger(cantidad) && cantidad > 0
      ? repuestoElegido.value && cantidad > repuestoElegido.value.stock
        ? `Solo hay ${repuestoElegido.value.stock} en inventario.`
        : ''
      : 'La cantidad debe ser un número entero mayor que 0.'
  if (erroresRepuesto.sku || erroresRepuesto.cantidad) return
  guardandoRepuesto.value = true
  errorRepuesto.value = ''
  try {
    const { data } = await reparacionesService.usarRepuesto(props.id, formRepuesto.sku, cantidad)
    avisos.mostrar(data.mensaje)
    dialogoRepuesto.value = false
    await cargar()
  } catch (e) {
    errorRepuesto.value = mensajeError(e, 'No se pudo agregar el repuesto.')
  } finally {
    guardandoRepuesto.value = false
  }
}

/* ---------- Eliminar ---------- */
const confirmarEliminar = ref(false)
const eliminando = ref(false)
const errorEliminar = ref('')

function pedirEliminar() {
  errorEliminar.value = ''
  confirmarEliminar.value = true
}

async function eliminar() {
  eliminando.value = true
  errorEliminar.value = ''
  try {
    await reparaciones.eliminar(props.id)
    confirmarEliminar.value = false
    avisos.mostrar(`Reparación ${props.id} eliminada`)
    router.push('/reparaciones')
  } catch (e) {
    errorEliminar.value = mensajeError(e, 'No se pudo eliminar la reparación.')
  } finally {
    eliminando.value = false
  }
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Reparación" volver-a="/reparaciones" volver-texto="Reparaciones">
      <EtiquetaEstado v-if="reparacion" :estado="reparacion.estado" />
    </BarraPagina>

    <div class="contenedor">
      <p v-if="cargando && !reparacion" class="cargando">Cargando reparación…</p>

      <div v-else-if="noEncontrada" class="vacio mt-3">
        <h1 class="titulo-pagina">No encontramos {{ id }}</h1>
        <p class="mt-1">Puede que se haya eliminado o que el código esté mal escrito.</p>
        <RouterLink to="/reparaciones" class="btn btn-primario">Ver todas las reparaciones</RouterLink>
      </div>

      <p v-else-if="error && !reparacion" class="alerta alerta-error mt-3" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <template v-else-if="reparacion">
        <header class="cabecera">
          <h1 class="titulo-pagina mono-id">{{ reparacion.id_reparacion }}</h1>
          <p class="texto-intro">{{ reparacion.diagnostico }}</p>
          <dl class="datos">
            <div>
              <dt>Equipo</dt>
              <dd>{{ reparacion.id_equipo }}</dd>
            </div>
            <div>
              <dt>Ingresó</dt>
              <dd>{{ formatoFechaHora(reparacion.fecha_ingreso) }}</dd>
            </div>
            <div>
              <dt>Técnico</dt>
              <dd :class="{ 'texto-secundario': !reparacion.cedula_tecnico }">
                {{ textoTecnico(reparacion.cedula_tecnico) }}
              </dd>
            </div>
          </dl>
        </header>

        <!-- Avance -->
        <section class="panel bloque" aria-labelledby="titulo-avance">
          <h2 id="titulo-avance" class="titulo-bloque">Avance</h2>
          <ProgresoReparacion :estado="reparacion.estado" class="mt-3" />

          <div class="accion-avance">
            <p v-if="reparacion.estado === 'Entregado'" class="texto-secundario">
              El equipo ya se entregó al cliente.
            </p>
            <p v-else-if="!reparacion.cedula_tecnico" class="alerta alerta-info">
              <Icono nombre="alerta" />
              <span>
                Para avanzar esta reparación primero hay que asignarle un técnico.
                <template v-if="!auth.esAdmin">Pídeselo a un administrador.</template>
              </span>
            </p>
            <p v-else-if="!puedeModificar" class="texto-secundario">
              No tienes permiso para cambiar la etapa de esta reparación.
            </p>
            <template v-else>
              <p class="texto-secundario">Siguiente etapa: {{ siguiente }}.</p>
              <button type="button" class="btn btn-primario" :disabled="avanzando" @click="pedirAvance">
                {{ avanzando ? 'Guardando…' : siguiente === 'Entregado' ? 'Entregar al cliente' : `Pasar a ${siguiente}` }}
              </button>
            </template>
          </div>
          <p v-if="errorAvance && !confirmarEntrega" class="alerta alerta-error mt-2" role="alert">
            <Icono nombre="alerta" />
            <span>{{ errorAvance }}</span>
          </p>
        </section>

        <!-- Técnico (solo admin, mientras la reparación siga abierta) -->
        <section v-if="auth.esAdmin && !terminada" class="panel bloque" aria-labelledby="titulo-tecnico">
          <h2 id="titulo-tecnico" class="titulo-bloque">
            {{ reparacion.cedula_tecnico ? 'Cambiar técnico' : 'Asignar técnico' }}
          </h2>
          <p class="texto-secundario mt-1">
            Cada técnico trabaja en una sola reparación a la vez. Si está ocupado, te avisaremos.
          </p>
          <form class="fila asignar mt-2" novalidate @submit.prevent="asignar">
            <div class="campo">
              <label for="cedula-tecnico">Cédula del técnico</label>
              <input
                id="cedula-tecnico"
                v-model="cedulaAsignar"
                class="entrada"
                list="cedulas-tecnicos"
                inputmode="numeric"
                autocomplete="off"
                :aria-invalid="!!errorAsignar"
                :aria-describedby="errorAsignar ? 'asignar-error' : undefined"
              />
              <datalist id="cedulas-tecnicos">
                <option v-for="c in cedulasConocidas" :key="c" :value="c" />
              </datalist>
            </div>
            <button type="submit" class="btn btn-primario" :disabled="asignando">
              {{ asignando ? 'Asignando…' : 'Asignar técnico' }}
            </button>
          </form>
          <p v-if="errorAsignar" id="asignar-error" class="error-campo mt-1" role="alert">{{ errorAsignar }}</p>
        </section>

        <!-- Repuestos y cotización -->
        <section class="panel-plano bloque" aria-labelledby="titulo-cotizacion">
          <div class="fila separado cabecera-panel">
            <h2 id="titulo-cotizacion" class="titulo-bloque">Repuestos y cotización</h2>
            <button
              v-if="!terminada && puedeModificar"
              type="button"
              class="btn btn-secundario btn-chico"
              @click="abrirRepuesto"
            >
              <Icono nombre="mas" :tamano="14" />
              Agregar repuesto
            </button>
          </div>

          <p v-if="!cotizacion?.repuestos.length" class="vacio">Todavía no se han usado repuestos.</p>

          <table v-else class="tabla tabla-adaptable">
            <caption class="sr-only">Repuestos usados en {{ id }}</caption>
            <thead>
              <tr>
                <th scope="col">Repuesto</th>
                <th scope="col" class="derecha">Cantidad</th>
                <th scope="col" class="derecha">Precio unitario</th>
                <th scope="col" class="derecha">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in cotizacion.repuestos" :key="r.sku_repuesto">
                <td class="celda-principal">
                  <span class="nombre-repuesto">{{ r.nombre }}</span>
                  <span class="texto-pequeno texto-secundario">{{ r.sku_repuesto }}</span>
                </td>
                <td data-etiqueta="Cantidad" class="derecha numero">{{ r.cantidad }}</td>
                <td data-etiqueta="Precio unitario" class="derecha numero">{{ formatoPesos(r.precio_unitario) }}</td>
                <td data-etiqueta="Valor" class="derecha numero">{{ formatoPesos(r.valor) }}</td>
              </tr>
            </tbody>
          </table>

          <dl v-if="cotizacion?.repuestos.length" class="totales">
            <div>
              <dt>Subtotal</dt>
              <dd class="numero">{{ formatoPesos(cotizacion.subtotal) }}</dd>
            </div>
            <div>
              <dt>IVA (19 %)</dt>
              <dd class="numero">{{ formatoPesos(cotizacion.iva) }}</dd>
            </div>
            <div class="total">
              <dt>Total</dt>
              <dd class="numero">{{ formatoPesos(cotizacion.total) }}</dd>
            </div>
          </dl>
        </section>

        <section v-if="auth.puedeGestionarReparaciones" class="zona-eliminar" aria-label="Eliminar reparación">
          <button type="button" class="btn-texto peligro" @click="pedirEliminar">
            Eliminar reparación
          </button>
        </section>
      </template>
    </div>

    <!-- Diálogos -->
    <DialogoConfirmar
      :abierto="confirmarEntrega"
      :titulo="`Entregar ${id} al cliente`"
      texto-confirmar="Entregar al cliente"
      :procesando="avanzando"
      :error="errorAvance"
      @confirmar="avanzar"
      @cerrar="confirmarEntrega = false"
    >
      Confirma que el cliente ya recogió su equipo. Una reparación entregada no puede volver a una etapa anterior.
    </DialogoConfirmar>

    <DialogoConfirmar
      :abierto="confirmarEliminar"
      :titulo="`Eliminar ${id}`"
      texto-confirmar="Eliminar reparación"
      peligro
      :procesando="eliminando"
      :error="errorEliminar"
      @confirmar="eliminar"
      @cerrar="confirmarEliminar = false"
    >
      Se borrará la reparación y su historial. Esta acción no se puede deshacer.
    </DialogoConfirmar>

    <DialogoBase
      :abierto="dialogoRepuesto"
      titulo="Agregar repuesto"
      :descripcion="`Se descontará del inventario y se sumará a la cotización de ${id}.`"
      @cerrar="dialogoRepuesto = false"
    >
      <form class="formulario" novalidate @submit.prevent="agregarRepuesto">
        <div class="campo">
          <label for="repuesto-sku">Repuesto</label>
          <select
            id="repuesto-sku"
            v-model="formRepuesto.sku"
            class="entrada"
            autofocus
            :aria-invalid="!!erroresRepuesto.sku"
          >
            <option value="" disabled>Elige un repuesto</option>
            <option v-for="r in repuestos.lista" :key="r.sku_repuesto" :value="r.sku_repuesto" :disabled="r.stock === 0">
              {{ r.nombre }} ({{ r.stock === 0 ? 'agotado' : `${r.stock} disponibles` }})
            </option>
          </select>
          <p v-if="erroresRepuesto.sku" class="error-campo">{{ erroresRepuesto.sku }}</p>
        </div>
        <div class="campo">
          <label for="repuesto-cantidad">Cantidad</label>
          <input
            id="repuesto-cantidad"
            v-model.number="formRepuesto.cantidad"
            class="entrada numero"
            type="number"
            min="1"
            :max="repuestoElegido?.stock"
            step="1"
            :aria-invalid="!!erroresRepuesto.cantidad"
          />
          <p v-if="erroresRepuesto.cantidad" class="error-campo">{{ erroresRepuesto.cantidad }}</p>
          <p v-else-if="repuestoElegido" class="ayuda">
            {{ formatoPesos(repuestoElegido.precio) }} c/u. Suma
            {{ formatoPesos(repuestoElegido.precio * (Number(formRepuesto.cantidad) || 0)) }} antes de IVA.
          </p>
        </div>
        <p v-if="errorRepuesto" class="alerta alerta-error" role="alert">
          <Icono nombre="alerta" />
          <span>{{ errorRepuesto }}</span>
        </p>
        <div class="acciones-dialogo">
          <button type="button" class="btn btn-secundario" @click="dialogoRepuesto = false">Cancelar</button>
          <button type="submit" class="btn btn-primario" :disabled="guardandoRepuesto">
            {{ guardandoRepuesto ? 'Agregando…' : 'Agregar a la reparación' }}
          </button>
        </div>
      </form>
    </DialogoBase>
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 12px;
}

.datos {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 40px;
  margin-top: 12px;
}

.datos dt {
  font-size: 13px;
  color: var(--color-texto-2);
}

.datos dd {
  font-size: 17px;
  font-weight: 500;
}

.bloque {
  margin-top: 28px;
}

.accion-avance {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 36px;
  padding-top: 24px;
  border-top: 1px solid var(--color-linea-suave);
}

.asignar {
  align-items: flex-end;
}

.asignar .campo {
  flex: 1;
  min-width: 220px;
  max-width: 320px;
}

.cabecera-panel {
  padding: 24px 28px 12px;
}

.nombre-repuesto {
  display: block;
  font-weight: 500;
}

.totales {
  margin-left: auto;
  max-width: 360px;
  padding: 8px 28px 24px;
  display: grid;
  gap: 6px;
}

.totales div {
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.totales dt {
  color: var(--color-texto-2);
}

.totales .total {
  border-top: 1px solid var(--color-linea-suave);
  padding-top: 10px;
  margin-top: 6px;
  font-size: 21px;
  font-weight: 600;
}

.totales .total dt {
  color: var(--color-texto);
}

.zona-eliminar {
  margin-top: 40px;
  text-align: center;
}
</style>
