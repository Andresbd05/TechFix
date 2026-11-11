<script setup>
// Íconos de trazo (24x24). "herramienta" es el ícono "tool" de Feather (licencia MIT).
const props = defineProps({
  nombre: { type: String, required: true },
  tamano: { type: Number, default: 18 },
})

const trazos = {
  herramienta: [
    'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
  ],
  buscar: ['M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14z', 'M20 20l-4-4'],
  mas: ['M12 5v14', 'M5 12h14'],
  'chevron-derecha': ['M9 6l6 6-6 6'],
  'chevron-izquierda': ['M15 6l-6 6 6 6'],
  menu: ['M4 8h16', 'M4 16h16'],
  cerrar: ['M6 6l12 12', 'M18 6L6 18'],
  alerta: ['M12 8v5', 'M12 16.5v.5', 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z'],
  check: ['M5 12.5l4.5 4.5L19 7.5'],
  clientes: ['M12 11.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z', 'M5 20a7 7 0 0 1 14 0'],
  inventario: ['M3.5 7.5l8.5-4 8.5 4v9l-8.5 4-8.5-4z', 'M3.5 7.5l8.5 4 8.5-4', 'M12 11.5V20'],
  luna: ['M21 12.8A8.5 8.5 0 1 1 11.2 3a6.5 6.5 0 0 0 9.8 9.8z'],
  sol: [
    'M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z',
    'M12 1.5v2.5', 'M12 20v2.5', 'M3.5 12H1', 'M23 12h-2.5',
    'M5.3 5.3l1.8 1.8', 'M16.9 16.9l1.8 1.8', 'M18.7 5.3l-1.8 1.8', 'M7.1 16.9l-1.8 1.8',
  ],
  ver: ['M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z', 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z'],
}
</script>

<template>
  <svg
    :width="props.tamano"
    :height="props.tamano"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path v-for="(d, i) in trazos[props.nombre]" :key="i" :d="d" />
  </svg>
</template>
