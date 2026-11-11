import api from './api'

export default {
  obtenerTodos() {
    return api.get('/clientes')
  },
  buscar(texto) {
    return api.get('/clientes/buscar', { params: { q: texto } })
  },
  obtener(cedula) {
    return api.get(`/clientes/${encodeURIComponent(cedula)}`)
  },
  crear(cliente) {
    return api.post('/clientes', cliente)
  },
  actualizar(cedula, cliente) {
    return api.put(`/clientes/${encodeURIComponent(cedula)}`, cliente)
  },
  eliminar(cedula) {
    return api.delete(`/clientes/${encodeURIComponent(cedula)}`)
  },
  equipos(cedula) {
    return api.get(`/clientes/${encodeURIComponent(cedula)}/equipos`)
  },
  historial(cedula) {
    return api.get(`/clientes/${encodeURIComponent(cedula)}/historial`)
  },
}
