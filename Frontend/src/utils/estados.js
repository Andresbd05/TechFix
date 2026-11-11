// Mismo flujo que FLUJO_ESTADOS en Backend/routes/reparaciones.py
export const ESTADOS = ['Recibido', 'En revisión', 'En reparación', 'Listo', 'Entregado']

export const SIGUIENTE_ESTADO = {
  Recibido: 'En revisión',
  'En revisión': 'En reparación',
  'En reparación': 'Listo',
  Listo: 'Entregado',
}

// Estados en los que ya no se puede cambiar técnico ni agregar repuestos
export const ESTADOS_TERMINADOS = ['Listo', 'Entregado']

export function estaTerminada(estado) {
  return ESTADOS_TERMINADOS.includes(estado)
}

// Clase CSS por estado (el color siempre va acompañado del nombre del estado)
export function claseEstado(estado) {
  return {
    Recibido: 'estado-recibido',
    'En revisión': 'estado-revision',
    'En reparación': 'estado-reparacion',
    Listo: 'estado-listo',
    Entregado: 'estado-entregado',
  }[estado]
}
