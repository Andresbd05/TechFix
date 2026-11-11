<script setup>
import { RouterLink } from 'vue-router'
import Icono from '@/components/ui/Icono.vue'
import BotonTema from '@/components/ui/BotonTema.vue'
import FlujoTaller from '@/components/reparaciones/FlujoTaller.vue'
import EtiquetaEstado from '@/components/ui/EtiquetaEstado.vue'
import { formatoPesos } from '@/utils/formato'

// Datos de ejemplo fijos: la demo no usa el backend ni la base de datos,
// es una muestra de solo lectura de lo que hace TechFix.
const conteo = { Recibido: 4, 'En revisión': 2, 'En reparación': 2, Listo: 2, Entregado: 5 }

const reparaciones = [
  { id: 'REP-99X1', equipo: 'Teléfono Samsung', estado: 'En revisión', diagnostico: 'Pantalla estrellada tras caída' },
  { id: 'REP-99X4', equipo: 'Teléfono Xiaomi', estado: 'En reparación', diagnostico: 'No carga, puerto USB-C dañado' },
  { id: 'REP-10A4', equipo: 'Computador Asus', estado: 'Listo', diagnostico: 'Se recalienta y se apaga' },
  { id: 'REP-99X3', equipo: 'Teléfono Apple', estado: 'Recibido', diagnostico: 'Batería se descarga en 2 horas' },
]

const repuestos = [
  { nombre: 'Pantalla OLED S23', estado: null, stock: 10 },
  { nombre: 'Batería HP 240 G8', estado: 'Bajo', stock: 2 },
  { nombre: 'Cámara Redmi Note 12', estado: 'Agotado', stock: 0 },
]

const valorInventario = 17560000
</script>

<template>
  <div class="demo">
    <header class="demo-nav">
      <div class="contenedor demo-nav-interior">
        <RouterLink to="/" class="demo-marca">
          <Icono nombre="herramienta" :tamano="18" />
          TechFix
        </RouterLink>
        <div class="demo-nav-acciones">
          <RouterLink to="/login" class="btn btn-secundario btn-chico">Iniciar sesión</RouterLink>
          <BotonTema />
        </div>
      </div>
    </header>

    <div class="contenedor">
      <!-- Aviso de demo -->
      <p class="demo-banner" role="status">
        <Icono nombre="ver" :tamano="18" />
        <span>Estás viendo una <strong>demo de solo lectura</strong>. Los datos son de ejemplo y no se pueden modificar.</span>
      </p>

      <section class="demo-intro">
        <h1 class="titulo-pagina">Así se ve TechFix por dentro</h1>
        <p class="texto-intro">
          Un vistazo rápido al panel del taller: el estado de las reparaciones, el inventario y los clientes.
        </p>
      </section>

      <!-- Flujo del taller (componente real) -->
      <section class="seccion" aria-labelledby="demo-flujo">
        <h2 id="demo-flujo" class="titulo-seccion">Flujo del taller</h2>
        <div class="demo-no-interactivo mt-2">
          <FlujoTaller :conteo="conteo" />
        </div>
      </section>

      <div class="demo-grid">
        <!-- Reparaciones de ejemplo -->
        <section aria-labelledby="demo-rep">
          <h2 id="demo-rep" class="titulo-seccion">Reparaciones</h2>
          <div class="panel-plano mt-2">
            <ul class="lista">
              <li v-for="r in reparaciones" :key="r.id" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1 mono-id">{{ r.id }}</span>
                  <span class="linea-2">{{ r.equipo }} · {{ r.diagnostico }}</span>
                </span>
                <EtiquetaEstado :estado="r.estado" />
              </li>
            </ul>
          </div>
        </section>

        <!-- Inventario de ejemplo -->
        <section aria-labelledby="demo-inv">
          <h2 id="demo-inv" class="titulo-seccion">Inventario</h2>
          <div class="panel mt-2">
            <p class="texto-secundario texto-pequeno">Valor del inventario</p>
            <p class="demo-valor numero">{{ formatoPesos(valorInventario) }}</p>
            <ul class="lista demo-lista-inv">
              <li v-for="rp in repuestos" :key="rp.nombre" class="lista-item">
                <span class="cuerpo">
                  <span class="linea-1">{{ rp.nombre }}</span>
                </span>
                <span
                  v-if="rp.estado"
                  class="aviso-stock"
                  :class="rp.estado === 'Agotado' ? 'agotado' : 'bajo'"
                >
                  {{ rp.estado }}
                </span>
                <span v-else class="texto-secundario numero">{{ rp.stock }} en stock</span>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <!-- Cierre -->
      <section class="demo-cierre">
        <h2 class="demo-cierre-titulo">¿Te sirve para tu taller?</h2>
        <p class="texto-secundario">Crea tu cuenta y empieza con el plan gratis, o inicia sesión si ya tienes una.</p>
        <div class="demo-cierre-ctas">
          <RouterLink to="/login" class="btn btn-primario btn-grande">Iniciar sesión</RouterLink>
          <RouterLink to="/" class="btn btn-contorno btn-grande">Volver al inicio</RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.demo {
  min-height: 100vh;
  background: var(--color-superficie);
  padding-bottom: 80px;
}

.demo-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  height: var(--alto-nav);
  background: var(--color-nav-fondo);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--color-borde-sutil);
}

.demo-nav-interior {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.demo-marca {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
  font-size: 17px;
  letter-spacing: -0.02em;
  color: var(--color-texto);
}

.demo-marca:hover {
  text-decoration: none;
}

.demo-nav-acciones {
  display: flex;
  align-items: center;
  gap: 10px;
}

.demo-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 24px;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--color-info-suave);
  color: var(--color-info-texto);
  font-size: 15px;
}

.demo-intro {
  padding-top: 32px;
  display: grid;
  gap: 10px;
}

/* En la demo nada es interactivo: desactivamos clics en los componentes reales */
.demo-no-interactivo {
  pointer-events: none;
}

.demo-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 24px;
  margin-top: 56px;
  align-items: start;
}

.demo-valor {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 4px 0 8px;
}

.demo-lista-inv {
  margin: 0 -28px -28px;
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

.demo-cierre {
  text-align: center;
  margin-top: 72px;
  padding: 48px 24px;
  background: var(--color-fondo);
  border-radius: var(--radio-lg);
}

.demo-cierre-titulo {
  font-size: clamp(24px, 3.5vw, 34px);
  font-weight: 700;
  letter-spacing: -0.025em;
}

.demo-cierre .texto-secundario {
  margin-top: 8px;
}

.demo-cierre-ctas {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

@media (max-width: 760px) {
  .demo-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
