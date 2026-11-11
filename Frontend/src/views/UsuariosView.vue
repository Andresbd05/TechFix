<script setup>
import { reactive, ref } from 'vue'
import authService from '@/services/authService'
import { useAvisosStore } from '@/stores/avisos'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import Icono from '@/components/ui/Icono.vue'
import { mensajeError } from '@/utils/errores'

const avisos = useAvisosStore()

// Los usuarios nuevos quedan en el plan Gratis por defecto
const form = reactive({ username: '', password: '', rol: 'tecnico', plan: 'gratis', cedula_tecnico: '' })
const errores = reactive({ username: '', password: '', cedula_tecnico: '' })
const guardando = ref(false)
const error = ref('')
const verClave = ref(false)

function validar() {
  errores.username = !form.username.trim()
    ? 'Escribe un nombre de usuario.'
    : /\s/.test(form.username.trim())
      ? 'Sin espacios, por ejemplo «sofia» o «sofia.m».'
      : ''
  errores.password = form.password.length >= 6 ? '' : 'Usa al menos 6 caracteres.'
  errores.cedula_tecnico =
    form.rol === 'tecnico' && !form.cedula_tecnico.trim() ? 'Escribe la cédula del técnico.' : ''
  return !Object.values(errores).some(Boolean)
}

async function crear() {
  error.value = ''
  if (!validar()) return
  guardando.value = true
  try {
    await authService.registrar({
      username: form.username.trim(),
      password: form.password,
      rol: form.rol,
      plan: form.plan,
      cedula_tecnico: form.rol === 'tecnico' ? form.cedula_tecnico.trim() : null,
    })
    avisos.mostrar(`Usuario ${form.username.trim()} creado`)
    Object.assign(form, { username: '', password: '', rol: 'tecnico', plan: 'gratis', cedula_tecnico: '' })
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo crear el usuario.')
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Usuarios" />

    <div class="contenedor angosto">
      <header class="cabecera">
        <h1 class="titulo-pagina">Usuarios</h1>
        <p class="texto-intro">Crea cuentas para el equipo del taller. Cada técnico inicia sesión con la suya.</p>
      </header>

      <section class="panel mt-3" aria-labelledby="titulo-crear">
        <h2 id="titulo-crear" class="titulo-bloque">Nuevo usuario</h2>
        <form class="formulario mt-2" novalidate @submit.prevent="crear">
          <fieldset class="campo rol">
            <legend class="etiqueta">Rol</legend>
            <label class="opcion-rol">
              <input v-model="form.rol" type="radio" name="rol" value="propietario" />
              <span>
                <strong>Propietario</strong>
                <span class="texto-secundario">Maneja inventario, reportes y clientes.</span>
              </span>
            </label>
            <label class="opcion-rol">
              <input v-model="form.rol" type="radio" name="rol" value="admin" />
              <span>
                <strong>Administrador</strong>
                <span class="texto-secundario">Crea usuarios y asigna técnicos.</span>
              </span>
            </label>
            <label class="opcion-rol">
              <input v-model="form.rol" type="radio" name="rol" value="tecnico" />
              <span>
                <strong>Técnico</strong>
                <span class="texto-secundario">Trabaja las reparaciones que le asignan.</span>
              </span>
            </label>
            <label class="opcion-rol">
              <input v-model="form.rol" type="radio" name="rol" value="invitado" />
              <span>
                <strong>Invitado</strong>
                <span class="texto-secundario">Solo puede ver, no modifica nada.</span>
              </span>
            </label>
          </fieldset>

          <div class="campos-dos">
            <div class="campo">
              <label for="us-usuario">Usuario</label>
              <input
                id="us-usuario"
                v-model="form.username"
                class="entrada"
                autocomplete="off"
                autocapitalize="none"
                spellcheck="false"
                :aria-invalid="!!errores.username"
                :aria-describedby="errores.username ? 'us-usuario-error' : undefined"
              />
              <p v-if="errores.username" id="us-usuario-error" class="error-campo">{{ errores.username }}</p>
            </div>
            <div class="campo">
              <label for="us-clave">Contraseña</label>
              <div class="clave">
                <input
                  id="us-clave"
                  v-model="form.password"
                  class="entrada"
                  :type="verClave ? 'text' : 'password'"
                  autocomplete="new-password"
                  :aria-invalid="!!errores.password"
                  :aria-describedby="errores.password ? 'us-clave-error' : 'us-clave-ayuda'"
                />
                <button type="button" class="btn-texto ver-clave" :aria-pressed="verClave" @click="verClave = !verClave">
                  {{ verClave ? 'Ocultar' : 'Mostrar' }}
                </button>
              </div>
              <p v-if="errores.password" id="us-clave-error" class="error-campo">{{ errores.password }}</p>
              <p v-else id="us-clave-ayuda" class="ayuda">Mínimo 6 caracteres.</p>
            </div>
          </div>

          <div class="campo">
            <label for="us-plan">Plan</label>
            <select id="us-plan" v-model="form.plan" class="entrada">
              <option value="gratis">Gratis</option>
              <option value="basico">Básico</option>
              <option value="pro">Pro</option>
              <option value="empresa">Empresa</option>
            </select>
            <p class="ayuda">Los usuarios nuevos quedan en el plan Gratis.</p>
          </div>

          <div v-if="form.rol === 'tecnico'" class="campo">
            <label for="us-cedula">Cédula del técnico</label>
            <input
              id="us-cedula"
              v-model="form.cedula_tecnico"
              class="entrada numero"
              inputmode="numeric"
              autocomplete="off"
              :aria-invalid="!!errores.cedula_tecnico"
              aria-describedby="us-cedula-ayuda"
            />
            <p v-if="errores.cedula_tecnico" class="error-campo">{{ errores.cedula_tecnico }}</p>
            <p id="us-cedula-ayuda" class="ayuda">Debe ser la cédula de un técnico registrado en el taller.</p>
          </div>

          <p v-if="error" class="alerta alerta-error" role="alert">
            <Icono nombre="alerta" />
            <span>{{ error }}</span>
          </p>

          <div>
            <button type="submit" class="btn btn-primario" :disabled="guardando">
              {{ guardando ? 'Creando…' : 'Crear usuario' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.angosto {
  max-width: calc(720px + var(--margen-lateral) * 2);
}

.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 10px;
}

.rol {
  border: none;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.rol legend {
  margin-bottom: 8px;
}

.opcion-rol {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--color-linea);
  border-radius: 14px;
  cursor: pointer;
  font-weight: 400;
}

.opcion-rol:has(input:checked) {
  border-color: var(--color-accion);
  box-shadow: 0 0 0 1px var(--color-accion);
}

.opcion-rol input {
  margin-top: 3px;
  width: 18px;
  height: 18px;
  accent-color: var(--color-accion);
  flex-shrink: 0;
}

.opcion-rol > span {
  display: grid;
  gap: 2px;
  font-size: 15px;
}

.opcion-rol .texto-secundario {
  font-size: 13px;
}

.clave {
  position: relative;
}

.clave .entrada {
  padding-right: 88px;
}

.ver-clave {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
}

@media (max-width: 560px) {
  .rol {
    grid-template-columns: 1fr;
  }
}
</style>
