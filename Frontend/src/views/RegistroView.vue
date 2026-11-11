<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mensajeError } from '@/utils/errores'
import Icono from '@/components/ui/Icono.vue'
import BotonTema from '@/components/ui/BotonTema.vue'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ nombre: '', email: '', password: '' })
const errores = reactive({ nombre: '', email: '', password: '' })
const error = ref('')
const cargando = ref(false)
const verClave = ref(false)

function validar() {
  errores.nombre = form.nombre.trim() ? '' : 'Escribe tu nombre.'
  const email = form.email.trim()
  errores.email = !email
    ? 'Escribe tu correo.'
    : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
      ? 'Escribe un correo válido, por ejemplo nombre@correo.com.'
      : ''
  errores.password = form.password.length >= 6 ? '' : 'Usa al menos 6 caracteres.'
  return !errores.nombre && !errores.email && !errores.password
}

async function crearCuenta() {
  error.value = ''
  if (!validar()) return
  cargando.value = true
  try {
    await auth.registrarYEntrar(form.nombre.trim(), form.email.trim().toLowerCase(), form.password)
    router.push({ name: 'inicio' })
  } catch (e) {
    auth.logout()
    error.value = mensajeError(e, 'No se pudo crear la cuenta.')
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <div class="registro">
    <header class="reg-nav">
      <div class="contenedor reg-nav-interior">
        <RouterLink to="/" class="reg-marca">
          <Icono nombre="herramienta" :tamano="18" />
          TechFix
        </RouterLink>
        <BotonTema />
      </div>
    </header>

    <section class="reg-centro">
      <div class="reg-caja">
        <span class="reg-icono">
          <Icono nombre="herramienta" :tamano="34" />
        </span>
        <h1 class="reg-titulo">Crea tu cuenta</h1>
        <p class="reg-intro">Empiezas en el plan Gratis. Sin tarjeta de crédito.</p>

        <p v-if="error" class="alerta alerta-error" role="alert">
          <Icono nombre="alerta" />
          <span>{{ error }}</span>
        </p>

        <form class="formulario" novalidate @submit.prevent="crearCuenta">
          <div class="campo">
            <label for="reg-nombre">Nombre</label>
            <input
              id="reg-nombre"
              v-model="form.nombre"
              class="entrada"
              autocomplete="name"
              autofocus
              :aria-invalid="!!errores.nombre"
              :aria-describedby="errores.nombre ? 'reg-nombre-error' : undefined"
            />
            <p v-if="errores.nombre" id="reg-nombre-error" class="error-campo">{{ errores.nombre }}</p>
          </div>

          <div class="campo">
            <label for="reg-email">Correo</label>
            <input
              id="reg-email"
              v-model="form.email"
              class="entrada"
              type="email"
              autocomplete="email"
              autocapitalize="none"
              spellcheck="false"
              :aria-invalid="!!errores.email"
              :aria-describedby="errores.email ? 'reg-email-error' : undefined"
            />
            <p v-if="errores.email" id="reg-email-error" class="error-campo">{{ errores.email }}</p>
          </div>

          <div class="campo">
            <label for="reg-clave">Contraseña</label>
            <div class="clave">
              <input
                id="reg-clave"
                v-model="form.password"
                class="entrada"
                :type="verClave ? 'text' : 'password'"
                autocomplete="new-password"
                :aria-invalid="!!errores.password"
                :aria-describedby="errores.password ? 'reg-clave-error' : 'reg-clave-ayuda'"
              />
              <button type="button" class="btn-texto ver-clave" :aria-pressed="verClave" @click="verClave = !verClave">
                {{ verClave ? 'Ocultar' : 'Mostrar' }}
              </button>
            </div>
            <p v-if="errores.password" id="reg-clave-error" class="error-campo">{{ errores.password }}</p>
            <p v-else id="reg-clave-ayuda" class="ayuda">Mínimo 6 caracteres.</p>
          </div>

          <button class="btn btn-primario btn-grande" type="submit" :disabled="cargando">
            {{ cargando ? 'Creando cuenta…' : 'Crear cuenta' }}
          </button>
        </form>

        <p class="reg-pie">
          ¿Ya tienes cuenta?
          <RouterLink to="/login">Inicia sesión</RouterLink>
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.registro {
  min-height: 100vh;
  background: var(--color-superficie);
}

.reg-nav {
  height: var(--alto-nav);
  border-bottom: 1px solid var(--color-borde-sutil);
}

.reg-nav-interior {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.reg-marca {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
  font-size: 17px;
  letter-spacing: -0.02em;
  color: var(--color-texto);
}

.reg-marca:hover {
  text-decoration: none;
}

.reg-centro {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px var(--margen-lateral);
  min-height: calc(100vh - var(--alto-nav));
}

.reg-caja {
  width: 100%;
  max-width: 400px;
  display: grid;
  gap: 20px;
  text-align: center;
}

.reg-icono {
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

.reg-titulo {
  font-size: 32px;
  line-height: 1.12;
  font-weight: 600;
  letter-spacing: -0.025em;
}

.reg-intro {
  color: var(--color-texto-2);
  margin-top: -8px;
}

.registro .formulario {
  text-align: left;
  margin-top: 8px;
}

.registro .btn-grande {
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

.reg-pie {
  font-size: 14px;
  color: var(--color-texto-2);
}

.alerta {
  text-align: left;
}
</style>
