<script setup>
import { RouterLink } from 'vue-router'
import { ESTADOS, claseEstado } from '@/utils/estados'
import Icono from '@/components/ui/Icono.vue'

// Las 5 etapas por las que pasa cada equipo, con cuántas reparaciones hay en cada una
defineProps({
  conteo: { type: Object, required: true },
})

function etiqueta(n, estado) {
  return `${n} ${n === 1 ? 'reparación' : 'reparaciones'} en ${estado}. Ver lista`
}
</script>

<template>
  <ol class="flujo" aria-label="Reparaciones por etapa">
    <li v-for="estado in ESTADOS" :key="estado" class="flujo-paso" :class="claseEstado(estado)">
      <span class="flujo-flecha" aria-hidden="true">
        <Icono nombre="chevron-derecha" :tamano="14" />
      </span>
      <RouterLink
        :to="{ name: 'reparaciones', query: { estado } }"
        class="flujo-enlace"
        :aria-label="etiqueta(conteo[estado] || 0, estado)"
      >
        <span class="flujo-cifra numero" :class="{ cero: !conteo[estado] }">{{ conteo[estado] || 0 }}</span>
        <span class="flujo-nombre">
          <span class="punto" aria-hidden="true"></span>
          {{ estado }}
        </span>
      </RouterLink>
    </li>
  </ol>
</template>

<style scoped>
.flujo {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  background: var(--color-superficie);
  border-radius: var(--radio-lg);
  overflow: hidden;
}

.flujo-paso {
  position: relative;
}

.flujo-paso + .flujo-paso {
  border-left: 1px solid var(--color-linea-suave);
}

.flujo-flecha {
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-superficie);
  border: 1px solid var(--color-linea-suave);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-texto-2);
  z-index: 1;
}

.flujo-paso:first-child .flujo-flecha {
  display: none;
}

.flujo-enlace {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 36px 28px 32px;
  color: var(--color-texto);
  height: 100%;
}

/* El contenedor recorta los bordes, así que el foco se dibuja hacia adentro */
.flujo-enlace:focus-visible {
  outline-offset: -4px;
  border-radius: 0;
}

.flujo-enlace:hover {
  text-decoration: none;
  background: var(--color-superficie-2);
}

.flujo-cifra {
  font-size: 56px;
  line-height: 1;
  font-weight: 600;
  letter-spacing: -0.04em;
}

.flujo-cifra.cero {
  color: #c7c7cc;
}

.flujo-nombre {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 15px;
  font-weight: 500;
  color: var(--estado-texto);
}

.punto {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--estado-punto);
}

@media (max-width: 860px) {
  .flujo {
    grid-template-columns: 1fr;
  }

  .flujo-paso + .flujo-paso {
    border-left: none;
    border-top: 1px solid var(--color-linea-suave);
  }

  .flujo-flecha {
    display: none;
  }

  .flujo-enlace {
    flex-direction: row-reverse;
    justify-content: space-between;
    align-items: center;
    padding: 18px 24px;
  }

  .flujo-cifra {
    font-size: 32px;
  }
}
</style>
