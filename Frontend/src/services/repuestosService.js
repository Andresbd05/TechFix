import api from './api'

export default {
  obtenerTodos() {
    return api.get('/repuestos')
  },
  obtener(sku) {
    return api.get(`/repuestos/${encodeURIComponent(sku)}`)
  },
  crear(repuesto) {
    return api.post('/repuestos', repuesto)
  },
  actualizar(sku, repuesto) {
    return api.put(`/repuestos/${encodeURIComponent(sku)}`, repuesto)
  },
  eliminar(sku) {
    return api.delete(`/repuestos/${encodeURIComponent(sku)}`)
  },
  stockBajo(minimo = 5) {
    return api.get('/repuestos/stock-bajo', { params: { minimo } })
  },
  // cantidad positiva = entrada, negativa = salida
  ajustarStock(sku, cantidad) {
    return api.patch(`/repuestos/${encodeURIComponent(sku)}/stock`, { cantidad })
  },
  valorInventario() {
    return api.get('/repuestos/valor-inventario')
  },
}
