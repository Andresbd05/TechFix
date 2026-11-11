import { defineStore } from 'pinia'
import reparacionesService from '@/services/reparacionesService'
import { ESTADOS } from '@/utils/estados'

export const useReparacionesStore = defineStore('reparaciones', {
  state: () => ({
    lista: [],
  }),
  getters: {
    // { Recibido: 3, 'En revisión': 2, ... }
    conteoPorEstado: (state) => {
      const conteo = Object.fromEntries(ESTADOS.map((e) => [e, 0]))
      for (const r of state.lista) conteo[r.estado] = (conteo[r.estado] || 0) + 1
      return conteo
    },
    enCurso: (state) => state.lista.filter((r) => !['Listo', 'Entregado'].includes(r.estado)),
    listas: (state) => state.lista.filter((r) => r.estado === 'Listo'),
    sinTecnico: (state) =>
      state.lista.filter((r) => !r.cedula_tecnico && !['Listo', 'Entregado'].includes(r.estado)),
  },
  actions: {
    async cargar() {
      const { data } = await reparacionesService.obtenerTodas()
      this.lista = data.reparaciones
    },
    async crear(reparacion) {
      await reparacionesService.crear(reparacion)
      await this.cargar()
    },
    async eliminar(id) {
      await reparacionesService.eliminar(id)
      await this.cargar()
    },
  },
})
