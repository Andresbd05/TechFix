<script setup>
import { RouterLink } from 'vue-router'
import Icono from '@/components/ui/Icono.vue'
import BotonTema from '@/components/ui/BotonTema.vue'

// Beneficios que se muestran bajo el hero. El glifo es un SVG simple local.
const beneficios = [
  {
    titulo: 'Reparaciones ordenadas',
    texto: 'Cada equipo avanza por etapas claras: recibido, en revisión, en reparación, listo y entregado.',
    glifo: 'herramienta',
  },
  {
    titulo: 'Clientes y su historial',
    texto: 'Encuentra a cualquier cliente, sus equipos y todo lo que ha traído al taller.',
    glifo: 'clientes',
  },
  {
    titulo: 'Inventario al día',
    texto: 'Controla el stock de repuestos, con avisos cuando algo está por agotarse.',
    glifo: 'inventario',
  },
]

// Planes. Todos los botones llevan al login (el alta de cuentas la hace un admin).
const planes = [
  {
    nombre: 'Gratis',
    precio: '$0',
    periodo: 'para siempre',
    resumen: 'Para probar TechFix en un taller pequeño.',
    incluye: ['Hasta 10 clientes', '1 técnico', 'Reparaciones e inventario'],
    cta: 'Empezar gratis',
    destino: { name: 'registro' },
    destacado: false,
    estilo: 'plan-gratis',
  },
  {
    nombre: 'Básico',
    precio: '$49.900',
    periodo: 'al mes',
    resumen: 'Lo esencial para el día a día del taller.',
    incluye: ['Hasta 50 clientes', '2 técnicos', 'Reparaciones e inventario'],
    cta: 'Empezar',
    destino: { name: 'registro' },
    destacado: false,
    estilo: 'plan-basico',
  },
  {
    nombre: 'Pro',
    precio: '$99.900',
    periodo: 'al mes',
    resumen: 'Para talleres con más movimiento.',
    incluye: ['Clientes ilimitados', 'Hasta 10 técnicos', 'Reportes del taller'],
    cta: 'Suscribirme',
    destino: { name: 'registro' },
    destacado: true,
    estilo: 'plan-pro',
  },
  {
    nombre: 'Empresa',
    precio: '$179.900',
    periodo: 'al mes',
    resumen: 'Para cadenas con varias sedes.',
    incluye: ['Todo ilimitado', 'Multisucursal', 'Soporte prioritario'],
    cta: 'Hablar con ventas',
    destino: 'mailto:ventas@techfix.com',
    destacado: false,
    estilo: 'plan-empresa',
  },
]
</script>

<template>
  <div class="landing">
    <!-- Barra pública (la barra de la app solo aparece tras iniciar sesión) -->
    <header class="lp-nav">
      <div class="contenedor lp-nav-interior">
        <span class="lp-marca">
          <Icono nombre="herramienta" :tamano="18" />
          TechFix
        </span>
        <nav class="lp-nav-acciones" aria-label="Accesos">
          <a href="#planes" class="lp-nav-enlace">Planes</a>
          <RouterLink to="/login" class="lp-nav-enlace">Iniciar sesión</RouterLink>
          <RouterLink to="/registro" class="btn btn-primario btn-chico">Crear cuenta</RouterLink>
          <BotonTema />
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="lp-hero">
      <div class="contenedor">
        <p class="lp-kicker">Software para talleres de reparación</p>
        <h1 class="lp-nombre">TechFix</h1>
        <p class="lp-lema">El taller, bajo control.</p>
        <p class="lp-sub">
          TechFix reúne tus reparaciones, clientes e inventario en un solo lugar. Menos papeles, más
          equipos entregados a tiempo.
        </p>
        <div class="lp-hero-ctas">
          <RouterLink to="/registro" class="btn btn-primario btn-grande">Crear cuenta</RouterLink>
          <RouterLink to="/demo" class="btn btn-contorno btn-grande">Ver demo</RouterLink>
        </div>
        <p class="lp-hero-nota">Sin tarjeta de crédito · Cancela cuando quieras</p>
      </div>
    </section>

    <!-- Beneficios -->
    <section class="lp-beneficios" aria-labelledby="lp-beneficios-tit">
      <div class="contenedor">
        <h2 id="lp-beneficios-tit" class="sr-only">Lo que puedes hacer con TechFix</h2>
        <ul class="lp-grid-beneficios">
          <li v-for="b in beneficios" :key="b.titulo" class="lp-beneficio">
            <span class="lp-beneficio-glifo" aria-hidden="true">
              <Icono :nombre="b.glifo" :tamano="22" />
            </span>
            <h3 class="lp-beneficio-tit">{{ b.titulo }}</h3>
            <p class="lp-beneficio-txt">{{ b.texto }}</p>
          </li>
        </ul>
      </div>
    </section>

    <!-- Planes (los CTA) -->
    <section id="planes" class="lp-planes" aria-labelledby="lp-planes-tit">
      <div class="contenedor">
        <div class="lp-planes-cabecera">
          <h2 id="lp-planes-tit" class="lp-planes-titulo">Un plan para cada taller</h2>
          <p class="lp-planes-sub">Empieza gratis y cambia de plan cuando lo necesites.</p>
        </div>

        <div class="lp-grid-planes">
          <article
            v-for="plan in planes"
            :key="plan.nombre"
            class="lp-plan"
            :class="[plan.estilo, { destacado: plan.destacado }]"
          >
            <p v-if="plan.destacado" class="lp-plan-badge">Más popular</p>
            <h3 class="lp-plan-nombre">{{ plan.nombre }}</h3>
            <p class="lp-plan-precio">
              <span class="lp-plan-monto numero">{{ plan.precio }}</span>
              <span class="lp-plan-periodo">{{ plan.periodo }}</span>
            </p>
            <p class="lp-plan-resumen">{{ plan.resumen }}</p>
            <ul class="lp-plan-incluye">
              <li v-for="item in plan.incluye" :key="item">
                <Icono nombre="check" :tamano="16" />
                <span>{{ item }}</span>
              </li>
            </ul>
            <a
              v-if="typeof plan.destino === 'string'"
              :href="plan.destino"
              class="btn lp-plan-cta"
              :class="plan.destacado ? 'btn-primario' : 'btn-secundario'"
            >
              {{ plan.cta }}
            </a>
            <RouterLink
              v-else
              :to="plan.destino"
              class="btn lp-plan-cta"
              :class="plan.destacado ? 'btn-primario' : 'btn-secundario'"
            >
              {{ plan.cta }}
            </RouterLink>
          </article>
        </div>
      </div>
    </section>

    <!-- Cierre -->
    <section class="lp-cierre">
      <div class="contenedor">
        <h2 class="lp-cierre-titulo">Pon orden en tu taller hoy.</h2>
        <RouterLink to="/demo" class="btn btn-primario btn-grande">Crear cuenta</RouterLink>
      </div>
    </section>

    <footer class="lp-footer">
      <div class="contenedor lp-footer-interior">
        <span class="lp-marca">
          <Icono nombre="herramienta" :tamano="16" />
          TechFix
        </span>
        <span class="texto-pequeno">Proyecto académico · {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing {
  background: var(--color-superficie);
}

/* ---------- Barra pública ---------- */
.lp-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  height: var(--alto-nav);
  background: var(--color-nav-fondo);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--color-borde-sutil);
}

.lp-nav-interior {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.lp-marca {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
  font-size: 17px;
  letter-spacing: -0.02em;
  color: var(--color-texto);
}

.lp-nav-acciones {
  display: flex;
  align-items: center;
  gap: 18px;
}

.lp-nav-enlace {
  font-size: 14px;
  color: var(--color-texto-2);
}

.lp-nav-enlace:hover {
  color: var(--color-texto);
  text-decoration: none;
}

/* ---------- Hero ---------- */
.lp-hero {
  text-align: center;
  padding: clamp(64px, 12vw, 128px) 0 clamp(48px, 8vw, 88px);
}

.lp-kicker {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-accion);
  letter-spacing: -0.01em;
}

.lp-nombre {
  font-size: clamp(64px, 14vw, 148px);
  line-height: 0.98;
  font-weight: 700;
  letter-spacing: -0.045em;
  margin-top: 8px;
  background: linear-gradient(180deg, var(--color-texto) 0%, var(--color-texto-2) 160%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.lp-lema {
  font-size: clamp(24px, 4vw, 44px);
  line-height: 1.08;
  font-weight: 600;
  letter-spacing: -0.025em;
  margin-top: 12px;
}

.lp-sub {
  font-size: clamp(18px, 2.4vw, 23px);
  line-height: 1.38;
  color: var(--color-texto-2);
  letter-spacing: -0.014em;
  max-width: 30em;
  margin: 20px auto 0;
}

.lp-hero-ctas {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 34px;
}

.lp-hero-nota {
  font-size: 13px;
  color: var(--color-texto-2);
  margin-top: 18px;
}

/* ---------- Beneficios ---------- */
.lp-beneficios {
  padding: clamp(40px, 7vw, 80px) 0;
  background: var(--color-fondo);
}

.lp-grid-beneficios {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.lp-beneficio {
  background: var(--color-superficie);
  border-radius: var(--radio);
  padding: 28px;
}

.lp-beneficio-glifo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--color-info-suave);
  color: var(--color-accion);
}

.lp-beneficio-tit {
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.015em;
  margin-top: 16px;
}

.lp-beneficio-txt {
  color: var(--color-texto-2);
  margin-top: 6px;
  font-size: 15px;
  line-height: 1.45;
}

/* ---------- Planes ---------- */
.lp-planes {
  padding: clamp(56px, 9vw, 104px) 0;
}

.lp-planes-cabecera {
  text-align: center;
  margin-bottom: 44px;
}

.lp-planes-titulo {
  font-size: clamp(30px, 4.5vw, 44px);
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.026em;
}

.lp-planes-sub {
  color: var(--color-texto-2);
  font-size: 18px;
  margin-top: 10px;
}

.lp-grid-planes {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  align-items: start;
}

.lp-plan {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-superficie);
  border: 1px solid var(--color-linea);
  border-radius: var(--radio);
  padding: 28px 24px;
  height: 100%;
}

.lp-plan.destacado {
  border-color: var(--color-accion);
  box-shadow: 0 0 0 1px var(--color-accion), 0 18px 40px rgba(0, 113, 227, 0.14);
}

.lp-plan-badge {
  position: absolute;
  top: -12px;
  left: 24px;
  background: var(--color-accion);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 980px;
}

.lp-plan-nombre {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.015em;
}

.lp-plan-precio {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 12px;
}

.lp-plan-monto {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.lp-plan-periodo {
  font-size: 14px;
  color: var(--color-texto-2);
}

.lp-plan-resumen {
  color: var(--color-texto-2);
  font-size: 14px;
  line-height: 1.4;
  margin-top: 10px;
  min-height: 2.8em;
}

.lp-plan-incluye {
  list-style: none;
  padding: 0;
  margin: 18px 0 24px;
  display: grid;
  gap: 10px;
}

.lp-plan-incluye li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
}

.lp-plan-incluye svg {
  color: var(--color-exito);
  flex-shrink: 0;
  margin-top: 2px;
}

.lp-plan-cta {
  margin-top: auto;
  width: 100%;
}

/* ---------- Cierre ---------- */
.lp-cierre {
  text-align: center;
  padding: clamp(56px, 9vw, 104px) 0;
  background: var(--color-fondo);
}

.lp-cierre-titulo {
  font-size: clamp(28px, 4.5vw, 44px);
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.026em;
  margin-bottom: 26px;
}

/* ---------- Footer ---------- */
.lp-footer {
  padding: 28px 0;
  border-top: 1px solid var(--color-linea-suave);
}

.lp-footer-interior {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: var(--color-texto-2);
}

/* ---------- Responsive ---------- */
@media (max-width: 920px) {
  .lp-grid-planes {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .lp-grid-beneficios {
    grid-template-columns: minmax(0, 1fr);
  }

  .lp-nav-enlace {
    display: none;
  }
}

@media (max-width: 560px) {
  .lp-grid-planes {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
