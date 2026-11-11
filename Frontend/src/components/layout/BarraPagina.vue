<script setup>
import { RouterLink } from 'vue-router'
import Icono from '@/components/ui/Icono.vue'

// Barra fija de cada pantalla (como la barra de producto de apple.com):
// nombre de la sección a la izquierda y acciones a la derecha.
defineProps({
  titulo: { type: String, required: true },
  volverA: { type: String, default: '' },
  volverTexto: { type: String, default: '' },
})
</script>

<template>
  <div class="barra-pagina">
    <div class="contenedor barra-interior">
      <div class="barra-izquierda">
        <RouterLink v-if="volverA" :to="volverA" class="volver">
          <Icono nombre="chevron-izquierda" :tamano="16" />
          {{ volverTexto }}
        </RouterLink>
        <span v-else class="barra-titulo">{{ titulo }}</span>
      </div>
      <div class="barra-acciones">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.barra-pagina {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 52px;
  background: var(--color-nav-fondo);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--color-borde-sutil);
}

.barra-interior {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.barra-titulo {
  font-size: 21px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.volver {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 15px;
}

.barra-acciones {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
