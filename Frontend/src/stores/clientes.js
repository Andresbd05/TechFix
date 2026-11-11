import { defineStore } from 'pinia'
import clientesService from '@/services/clientesService'

export const useClientesStore = defineStore('clientes', {
  state: () => ({
    lista: [],
  }),
  actions: {
    async cargar() {
      const { data } = await clientesService.obtenerTodos()
      this.lista = data.clientes
    },
    async buscar(texto) {
      const { data } = await clientesService.buscar(texto)
      this.lista = data.clientes
    },
    async crear(cliente) {
      await clientesService.crear(cliente)
      await this.cargar()
    },
    async actualizar(cedula, cliente) {
      await clientesService.actualizar(cedula, cliente)
      await this.cargar()
    },
    async eliminar(cedula) {
      await clientesService.eliminar(cedula)
      await this.cargar()
    },
  },
})
