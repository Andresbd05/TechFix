<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mensajeError } from '@/utils/errores'
import Icono from '@/components/ui/Icono.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const errores = reactive({ username: '', password: '' })
const error = ref('')
const cargando = ref(false)
const verClave = ref(false)

const sesionExpirada = computed(() => route.query.sesion === 'expirada')

function validar() {
  errores.username = form.username.trim() ? '' : 'Escribe tu usuario.'
  errores.password = form.password ? '' : 'Escribe tu contraseña.'
  return !errores.username && !errores.password
}

async function iniciarSesion() {
  error.value = ''
  if (!validar()) return
  cargando.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    router.push({ name: 'inicio' })
  } catch (e) {
    auth.logout()
    error.value = mensajeError(e, 'No se pudo iniciar sesión.')
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <section class="login">
    <div class="login-caja">
      <span class="login-icono">
        <Icono nombre="herramienta" :tamano="34" />
      </span>
      <h1 class="login-titulo">Inicia sesión en TechFix</h1>
      <p class="login-intro">Reparaciones, clientes e inventario del taller en un solo lugar.</p>

      <p v-if="sesionExpirada && !error" class="alerta alerta-info" role="status">
        Tu sesión expiró. Vuelve a iniciar sesión para continuar.
      </p>
      <p v-if="error" class="alerta alerta-error" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <form class="formulario" novalidate @submit.prevent="iniciarSesion">
        <div class="campo">
          <label for="usuario">Usuario</label>
          <input
            id="usuario"
            v-model="form.username"
            class="entrada"
            autocomplete="username"
            autocapitalize="none"
            spellcheck="false"
            autofocus
            :aria-invalid="!!errores.username"
            :aria-describedby="errores.username ? 'usuario-error' : undefined"
          />
          <p v-if="errores.username" id="usuario-error" class="error-campo">{{ errores.username }}</p>
        </div>

        <div class="campo">
          <label for="clave">Contraseña</label>
          <div class="clave">
            <input
              id="clave"
              v-model="form.password"
              class="entrada"
              :type="verClave ? 'text' : 'password'"
              autocomplete="current-password"
              :aria-invalid="!!errores.password"
              :aria-describedby="errores.password ? 'clave-error' : undefined"
            />
            <button
              type="button"
              class="btn-texto ver-clave"
              :aria-pressed="verClave"
              @click="verClave = !verClave"
            >
              {{ verClave ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
          <p v-if="errores.password" id="clave-error" class="error-campo">{{ errores.password }}</p>
        </div>

        <button class="btn btn-primario btn-grande" type="submit" :disabled="cargando">
          {{ cargando ? 'Iniciando sesión…' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="login-pie">
        ¿No tienes cuenta?
        <RouterLink to="/registro">Crea una gratis</RouterLink>
      </p>
    </div>
  </section>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px var(--margen-lateral);
  background: var(--color-superficie);
}

.login-caja {
  width: 100%;
  max-width: 400px;
  display: grid;
  gap: 20px;
  text-align: center;
}

.login-icono {
  justify-self: center;
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-fondo);
  color: var(--color-texto);
}

.login-titulo {
  font-size: 32px;
  line-height: 1.12;
  font-weight: 600;
  letter-spacing: -0.025em;
}

.login-intro {
  color: var(--color-texto-2);
  margin-top: -8px;
}

.login .formulario {
  text-align: left;
  margin-top: 8px;
}

.login .btn-grande {
  width: 100%;
  margin-top: 6px;
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

.login-pie {
  font-size: 14px;
  color: var(--color-texto-2);
  margin-top: 8px;
}

.alerta {
  text-align: left;
}
</style>
