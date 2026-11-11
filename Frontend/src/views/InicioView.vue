<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useReparacionesStore } from '@/stores/reparaciones'
import { useRepuestosStore } from '@/stores/repuestos'
import repuestosService from '@/services/repuestosService'
import reparacionesService from '@/services/reparacionesService'
import FlujoTaller from '@/components/reparaciones/FlujoTaller.vue'
import EtiquetaEstado from '@/components/ui/EtiquetaEstado.vue'
import Icono from '@/components/ui/Icono.vue'
import { formatoPesos, formatoFecha, plural } from '@/utils/formato'
import { estaTerminada } from '@/utils/estados'
import { mensajeError } from '@/utils/errores'

const auth = useAuthStore()
const reparaciones = useReparacionesStore()
const repuestos = useRepuestosStore()

const cargando = ref(true)
const error = ref('')
const stockBajo = ref([])
const misReparaciones = ref([])

const MINIMO_STOCK = 5

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const pedidos = [
      reparaciones.cargar(),
      repuestosService.stockBajo(MINIMO_STOCK).then(({ data }) => (stockBajo.value = data.repuestos)),
    ]
    // El valor del inventario (reportes) solo lo puede ver el propietario
    if (auth.puedeVerReportes) {
      pedidos.push(repuestos.cargarValor())
    }
    if (auth.cedulaTecnico) {
      pedidos.push(reparacionesService.mias().then(({ data }) => (misReparaciones.value = data.reparaciones)))
    }
    await Promise.all(pedidos)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo cargar el resumen del taller.')
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const misEnCurso = computed(() => misReparaciones.value.filter((r) => !estaTerminada(r.estado)))

const resumen = computed(() => {
  if (auth.cedulaTecnico) {
    return `Tienes ${plural(misEnCurso.value.length, 'reparación asignada', 'reparaciones asignadas')} en curso.`
  }
  const enCurso = reparaciones.enCurso.length
  const listas = reparaciones.listas.length
  return `Hay ${plural(enCurso, 'reparación', 'reparaciones')} en curso y ${plural(listas, 'lista', 'listas')} para entregar.`
})

const marcasPrincipales = computed(() => repuestos.porMarca.slice(0, 4))
</script>

<template>
  <div class="pagina">
    <section class="hero contenedor">
      <h1 class="titulo-hero">Hola, {{ auth.nombreMostrar }}.</h1>
      <p class="hero-resumen" aria-live="polite">
        {{ cargando ? 'Revisando el taller…' : resumen }}
      </p>
      <div class="hero-acciones">
        <RouterLink
          v-if="auth.puedeGestionarReparaciones"
          :to="{ name: 'reparaciones', query: { nueva: 1 } }"
          class="btn btn-primario btn-grande"
        >
          Nueva reparación
        </RouterLink>
        <RouterLink to="/reparaciones" class="btn btn-contorno btn-grande">Ver reparaciones</RouterLink>
      </div>
    </section>

    <div class="contenedor">
      <p v-if="error" class="alerta alerta-error mt-3" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
        <button class="btn-texto" type="button" @click="cargar">Reintentar</button>
      </p>

      <section class="seccion" aria-labelledby="titulo-flujo">
        <div class="seccion-cabecera">
          <h2 id="titulo-flujo" class="titulo-seccion">Flujo del taller</h2>
          <p class="texto-secundario texto-pequeno">Elige una etapa para ver sus reparaciones.</p>
        </div>
        <FlujoTaller :conteo="reparaciones.conteoPorEstado" />
      </section>

      <section class="seccion mosaico" aria-label="Pendientes del día">
        <!-- Para el técnico: lo suyo primero -->
        <article v-if="auth.cedulaTecnico" class="tesela">
          <h2 class="titulo-bloque">Tus reparaciones</h2>
          <p class="tesela-cifra numero">{{ misEnCurso.length }}</p>
          <ul v-if="misEnCurso.length" class="lista">
            <li v-for="r in misEnCurso.slice(0, 5)" :key="r.id_reparacion">
              <RouterLink :to="`/reparaciones/${r.id_reparacion}`" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1 mono-id">{{ r.id_reparacion }}</span>
                  <span class="linea-2">{{ r.diagnostico }}</span>
                </span>
                <EtiquetaEstado :estado="r.estado" />
                <Icono nombre="chevron-derecha" class="chevron" />
              </RouterLink>
            </li>
          </ul>
          <p v-else-if="!cargando" class="tesela-vacia">No tienes reparaciones en curso.</p>
        </article>

        <article class="tesela">
          <h2 class="titulo-bloque">Listas para entregar</h2>
          <p class="tesela-cifra numero">{{ reparaciones.listas.length }}</p>
          <ul v-if="reparaciones.listas.length" class="lista">
            <li v-for="r in reparaciones.listas.slice(0, 5)" :key="r.id_reparacion">
              <RouterLink :to="`/reparaciones/${r.id_reparacion}`" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1 mono-id">{{ r.id_reparacion }}</span>
                  <span class="linea-2">Equipo {{ r.id_equipo }}, ingresó el {{ formatoFecha(r.fecha_ingreso) }}</span>
                </span>
                <Icono nombre="chevron-derecha" class="chevron" />
              </RouterLink>
            </li>
          </ul>
          <p v-else-if="!cargando" class="tesela-vacia">Nada pendiente por entregar.</p>
        </article>

        <article v-if="auth.esAdmin" class="tesela">
          <h2 class="titulo-bloque">Sin técnico asignado</h2>
          <p class="tesela-cifra numero">{{ reparaciones.sinTecnico.length }}</p>
          <ul v-if="reparaciones.sinTecnico.length" class="lista">
            <li v-for="r in reparaciones.sinTecnico.slice(0, 5)" :key="r.id_reparacion">
              <RouterLink :to="`/reparaciones/${r.id_reparacion}`" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1 mono-id">{{ r.id_reparacion }}</span>
                  <span class="linea-2">{{ r.diagnostico }}</span>
                </span>
                <span class="texto-pequeno enlace-falso">Asignar</span>
                <Icono nombre="chevron-derecha" class="chevron" />
              </RouterLink>
            </li>
          </ul>
          <p v-else-if="!cargando" class="tesela-vacia">Todas las reparaciones tienen técnico.</p>
        </article>

        <article class="tesela">
          <h2 class="titulo-bloque">Stock bajo</h2>
          <p class="tesela-cifra numero">{{ stockBajo.length }}</p>
          <ul v-if="stockBajo.length" class="lista">
            <li v-for="r in stockBajo.slice(0, 5)" :key="r.sku_repuesto" class="lista-item">
              <span class="cuerpo">
                <span class="linea-1">{{ r.nombre }}</span>
                <span class="linea-2">{{ r.sku_repuesto }}</span>
              </span>
              <span class="stock" :class="{ agotado: r.stock === 0 }">
                {{ r.stock === 0 ? 'Agotado' : r.stock === 1 ? 'Queda 1' : `Quedan ${r.stock}` }}
              </span>
            </li>
          </ul>
          <p v-else-if="!cargando" class="tesela-vacia">Todo el inventario tiene más de {{ MINIMO_STOCK }} unidades.</p>
          <RouterLink to="/inventario" class="tesela-enlace">Ver inventario</RouterLink>
        </article>

        <article v-if="auth.puedeVerReportes" class="tesela">
          <h2 class="titulo-bloque">Valor del inventario</h2>
          <p class="tesela-cifra numero">{{ formatoPesos(repuestos.valorTotal) }}</p>
          <ul v-if="marcasPrincipales.length" class="lista">
            <li v-for="m in marcasPrincipales" :key="m.marca" class="lista-item">
              <span class="cuerpo">
                <span class="linea-1">{{ m.marca }}</span>
                <span class="linea-2">{{ plural(m.unidades, 'unidad', 'unidades') }}</span>
              </span>
              <span class="numero">{{ formatoPesos(m.valor) }}</span>
            </li>
          </ul>
        </article>
      </section>
    </div>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding-top: 88px;
  padding-bottom: 8px;
}

.hero-resumen {
  font-size: clamp(21px, 2.6vw, 28px);
  line-height: 1.25;
  font-weight: 500;
  color: var(--color-texto-2);
  letter-spacing: -0.02em;
  margin: 16px auto 0;
  max-width: 26em;
}

.hero-acciones {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 32px;
}

.mosaico {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.tesela {
  min-width: 0;
  background: var(--color-superficie);
  border-radius: var(--radio-lg);
  padding: 32px 0 16px;
  display: flex;
  flex-direction: column;
}

.tesela > .titulo-bloque,
.tesela-cifra,
.tesela-vacia,
.tesela-enlace {
  padding: 0 32px;
}

.tesela-cifra {
  font-size: 48px;
  line-height: 1.05;
  font-weight: 600;
  letter-spacing: -0.035em;
  margin: 8px 0 16px;
}

.tesela .lista-item {
  padding-left: 32px;
  padding-right: 28px;
}

.tesela-vacia {
  color: var(--color-texto-2);
  padding-bottom: 16px;
}

.tesela-enlace {
  margin-top: auto;
  padding-top: 12px;
  padding-bottom: 8px;
  font-size: 15px;
}

.stock {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-aviso);
  white-space: nowrap;
}

.stock.agotado {
  color: var(--color-peligro);
}

.enlace-falso {
  color: var(--color-enlace);
}

@media (max-width: 760px) {
  .hero {
    padding-top: 56px;
  }

  .mosaico {
    grid-template-columns: minmax(0, 1fr);
  }

  .tesela > .titulo-bloque,
  .tesela-cifra,
  .tesela-vacia,
  .tesela-enlace {
    padding: 0 24px;
  }

  .tesela .lista-item {
    padding-left: 24px;
    padding-right: 20px;
  }
}
</style>
