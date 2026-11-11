// Copia de la tabla `marcas` de database/techfix_db.sql.
// La API no tiene un endpoint de marcas; si agregas una marca nueva
// en MySQL, agrégala también aquí.
export const MARCAS = [
  { id: 1, nombre: 'Samsung' },
  { id: 2, nombre: 'Apple' },
  { id: 3, nombre: 'Xiaomi' },
  { id: 4, nombre: 'Lenovo' },
  { id: 5, nombre: 'Asus' },
  { id: 6, nombre: 'Motorola' },
  { id: 7, nombre: 'HP' },
  { id: 8, nombre: 'Huawei' },
]

export function nombreMarca(id) {
  if (id === null || id === undefined) return 'Sin marca'
  return MARCAS.find((m) => m.id === Number(id))?.nombre || `Marca ${id}`
}
