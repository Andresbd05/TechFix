// Convierte un error de axios en un mensaje claro para la persona
export function mensajeError(error, porDefecto = 'No se pudo completar la acción.') {
  if (error?.response?.data?.error) return error.response.data.error
  if (error?.request && !error?.response) {
    return 'No hay conexión con el servidor. Revisa que el backend esté corriendo en el puerto 5000.'
  }
  return porDefecto
}
