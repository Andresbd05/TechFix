import { defineStore } from 'pinia'
import repuestosService from '@/services/repuestosService'

export const useRepuestosStore = defineStore('repuestos', {
  state: () => ({
    lista: [],
    valorTotal: 0,
    porMarca: [],
  }),
  actions: {
    async cargar() {
      const { data } = await repuestosService.obtenerTodos()
      this.lista = data.repuestos
    },
    async cargarValor() {
      const { data } = await repuestosService.valorInventario()
      this.valorTotal = data.valor_total
      this.porMarca = data.por_marca
    },
    async recargarTodo() {
      await Promise.all([this.cargar(), this.cargarValor()])
    },
    async crear(repuesto) {
      await repuestosService.crear(repuesto)
      await this.recargarTodo()
    },
    async actualizar(sku, repuesto) {
      await repuestosService.actualizar(sku, repuesto)
      await this.recargarTodo()
    },
    async eliminar(sku) {
      await repuestosService.eliminar(sku)
      await this.recargarTodo()
    },
    async ajustarStock(sku, cantidad) {
      const { data } = await repuestosService.ajustarStock(sku, cantidad)
      await this.recargarTodo()
      return data
    },
  },
})
