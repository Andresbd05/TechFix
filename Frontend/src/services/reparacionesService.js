import api from './api'

export default {
  obtenerTodas() {
    return api.get('/reparaciones')
  },
  obtener(id) {
    return api.get(`/reparaciones/${encodeURIComponent(id)}`)
  },
  crear(reparacion) {
    return api.post('/reparaciones', reparacion)
  },
  eliminar(id) {
    return api.delete(`/reparaciones/${encodeURIComponent(id)}`)
  },
  asignarTecnico(id, cedulaTecnico) {
    return api.put(`/reparaciones/${encodeURIComponent(id)}/asignar`, { cedula_tecnico: cedulaTecnico })
  },
  avanzar(id) {
    return api.put(`/reparaciones/${encodeURIComponent(id)}/avanzar`)
  },
  usarRepuesto(id, sku, cantidad) {
    return api.post(`/reparaciones/${encodeURIComponent(id)}/repuestos`, { sku_repuesto: sku, cantidad })
  },
  cotizacion(id) {
    return api.get(`/reparaciones/${encodeURIComponent(id)}/cotizacion`)
  },
  mias() {
    return api.get('/mis-reparaciones')
  },
}
