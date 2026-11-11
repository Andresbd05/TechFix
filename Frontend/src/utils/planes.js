// Planes de suscripción de TechFix. Se usan en la landing y en "Mi plan".
export const PLANES = [
  {
    clave: 'gratis',
    nombre: 'Gratis',
    precio: '$0',
    periodo: 'para siempre',
    resumen: 'Para probar TechFix en un taller pequeño.',
    incluye: ['Hasta 10 clientes', '1 técnico', 'Reparaciones e inventario'],
    destacado: false,
  },
  {
    clave: 'basico',
    nombre: 'Básico',
    precio: '$49.900',
    periodo: 'al mes',
    resumen: 'Lo esencial para el día a día del taller.',
    incluye: ['Hasta 50 clientes', '2 técnicos', 'Reparaciones e inventario'],
    destacado: false,
  },
  {
    clave: 'pro',
    nombre: 'Pro',
    precio: '$99.900',
    periodo: 'al mes',
    resumen: 'Para talleres con más movimiento.',
    incluye: ['Clientes ilimitados', 'Hasta 10 técnicos', 'Reportes del taller'],
    destacado: true,
  },
  {
    clave: 'empresa',
    nombre: 'Empresa',
    precio: '$179.900',
    periodo: 'al mes',
    resumen: 'Para cadenas con varias sedes.',
    incluye: ['Todo ilimitado', 'Multisucursal', 'Soporte prioritario'],
    destacado: false,
  },
]

export function nombrePlan(clave) {
  return PLANES.find((p) => p.clave === clave)?.nombre || ''
}
