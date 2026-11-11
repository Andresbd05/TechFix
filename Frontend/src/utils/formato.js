const pesos = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

export function formatoPesos(valor) {
  return pesos.format(Number(valor) || 0)
}

// plural(1, 'reparación', 'reparaciones') -> "1 reparación"
export function plural(n, singular, varias) {
  return `${n} ${n === 1 ? singular : varias}`
}

export function formatoNumero(valor) {
  return new Intl.NumberFormat('es-CO').format(Number(valor) || 0)
}

// MySQL guarda la fecha sin zona horaria y Flask la envía como
// "Tue, 08 Sep 2026 09:00:00 GMT". Se lee en UTC para mostrar la
// hora tal cual se registró en el taller (sin restar 5 horas).
function aFecha(valor) {
  if (!valor) return null
  if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$/.test(valor)) {
    return new Date(valor.replace(' ', 'T') + 'Z')
  }
  const fecha = new Date(valor)
  return Number.isNaN(fecha.getTime()) ? null : fecha
}

export function formatoFecha(valor) {
  const fecha = aFecha(valor)
  if (!fecha) return '—'
  return fecha.toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

export function formatoFechaHora(valor) {
  const fecha = aFecha(valor)
  if (!fecha) return '—'
  return fecha.toLocaleString('es-CO', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZone: 'UTC',
  })
}

export function fechaOrdenable(valor) {
  const fecha = aFecha(valor)
  return fecha ? fecha.getTime() : 0
}
