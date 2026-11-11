<script setup>
import { onBeforeUnmount, onMounted, ref, watch, useId } from 'vue'
import Icono from '@/components/ui/Icono.vue'

// Usa el <dialog> nativo: atrapa el foco, se cierra con Esc
// y devuelve el foco al botón que lo abrió.
const props = defineProps({
  abierto: { type: Boolean, default: false },
  titulo: { type: String, required: true },
  descripcion: { type: String, default: '' },
  ancho: { type: String, default: '480px' },
})
const emit = defineEmits(['cerrar'])

const dialogo = ref(null)
const idTitulo = useId()
const idDescripcion = useId()

watch(
  () => props.abierto,
  (abierto) => {
    const el = dialogo.value
    if (!el) return
    if (abierto && !el.open) el.showModal()
    if (!abierto && el.open) el.close()
  },
  { flush: 'post' },
)

// Si el componente aparece ya "abierto" (por ejemplo al entrar con ?nueva=1
// en la URL, desde Inicio o al recargar), el watch no se dispara porque el
// valor no cambió. Por eso también lo abrimos al montar.
onMounted(() => {
  if (props.abierto && dialogo.value && !dialogo.value.open) dialogo.value.showModal()
})

onBeforeUnmount(() => {
  if (dialogo.value?.open) dialogo.value.close()
})

// Se dispara con Esc o con el botón cerrar
function alCerrar() {
  if (props.abierto) emit('cerrar')
}
</script>

<template>
  <dialog
    ref="dialogo"
    class="dialogo"
    :style="{ '--ancho-dialogo': ancho }"
    :aria-labelledby="idTitulo"
    :aria-describedby="descripcion ? idDescripcion : undefined"
    @close="alCerrar"
  >
    <div class="dialogo-cuerpo">
      <h2 :id="idTitulo" class="dialogo-titulo">{{ titulo }}</h2>
      <p v-if="descripcion" :id="idDescripcion" class="dialogo-descripcion">{{ descripcion }}</p>
      <slot />
    </div>
    <button type="button" class="dialogo-cerrar" @click="emit('cerrar')">
      <Icono nombre="cerrar" :tamano="16" />
      <span class="sr-only">Cerrar</span>
    </button>
  </dialog>
</template>

<style scoped>
.dialogo {
  width: min(var(--ancho-dialogo), calc(100vw - 32px));
  max-height: calc(100vh - 48px);
  margin: auto;
  padding: 0;
  border: none;
  border-radius: var(--radio);
  background: var(--color-superficie);
  color: var(--color-texto);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.18);
}

.dialogo[open] {
  animation: aparecer 0.22s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.dialogo::backdrop {
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
}

.dialogo-cuerpo {
  padding: 32px;
  display: grid;
  gap: 18px;
}

.dialogo-titulo {
  font-size: 24px;
  line-height: 1.17;
  font-weight: 600;
  letter-spacing: -0.02em;
  padding-right: 32px;
}

.dialogo-descripcion {
  color: var(--color-texto-2);
  margin-top: -10px;
}

.dialogo-cerrar {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: var(--color-linea-suave);
  color: var(--color-texto-2);
}

.dialogo-cerrar:hover {
  background: #dedee3;
  color: var(--color-texto);
}

@keyframes aparecer {
  from {
    opacity: 0;
    transform: scale(0.97) translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@media (max-width: 520px) {
  .dialogo-cuerpo {
    padding: 24px 20px;
  }
}
</style>
