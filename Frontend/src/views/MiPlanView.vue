<script setup>
import { computed, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAvisosStore } from '@/stores/avisos'
import BarraPagina from '@/components/layout/BarraPagina.vue'
import DialogoBase from '@/components/ui/DialogoBase.vue'
import Icono from '@/components/ui/Icono.vue'
import { PLANES, nombrePlan } from '@/utils/planes'
import { mensajeError } from '@/utils/errores'

const auth = useAuthStore()
const avisos = useAvisosStore()

const planActual = computed(() => auth.plan || 'basico')
const cambiando = ref(false)

/* ---------- Elegir plan ---------- */
const dialogoTarjeta = ref(false)
const planElegido = ref(null)
const error = ref('')

function elegir(plan) {
  if (plan.clave === planActual.value || auth.soloLectura) return
  error.value = ''
  if (plan.clave === 'gratis') {
    // El plan gratis no necesita tarjeta
    cambiarPlan('gratis')
  } else {
    planElegido.value = plan
    reiniciarTarjeta()
    dialogoTarjeta.value = true
  }
}

async function cambiarPlan(clave) {
  cambiando.value = true
  error.value = ''
  try {
    await auth.cambiarPlan(clave)
    dialogoTarjeta.value = false
    avisos.mostrar(`Plan cambiado a ${nombrePlan(clave)}`)
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo cambiar el plan.')
  } finally {
    cambiando.value = false
  }
}

/* ---------- Simulación de tarjeta ---------- */
const tarjeta = reactive({ numero: '', nombre: '', vence: '', cvv: '' })
const erroresTarjeta = reactive({ numero: '', nombre: '', vence: '', cvv: '' })

function reiniciarTarjeta() {
  Object.assign(tarjeta, { numero: '', nombre: '', vence: '', cvv: '' })
  Object.assign(erroresTarjeta, { numero: '', nombre: '', vence: '', cvv: '' })
}

// Formatea el número en grupos de 4 mientras se escribe
function formatearNumero() {
  const soloDigitos = tarjeta.numero.replace(/\D/g, '').slice(0, 16)
  tarjeta.numero = soloDigitos.replace(/(.{4})/g, '$1 ').trim()
}

// Detecta la marca de la tarjeta según los primeros dígitos del número
const marcaTarjeta = computed(() => {
  const d = tarjeta.numero.replace(/\D/g, '')
  if (!d) return ''
  if (/^4/.test(d)) return 'Visa'
  if (/^(5[1-5]|222[1-9]|22[3-9]|2[3-6]|27[01]|2720)/.test(d)) return 'Mastercard'
  if (/^3[47]/.test(d)) return 'American Express'
  if (/^(6011|65|64[4-9]|622)/.test(d)) return 'Discover'
  if (/^(30[0-5]|3[689])/.test(d)) return 'Diners Club'
  return ''
})

function formatearVence() {
  let v = tarjeta.vence.replace(/\D/g, '').slice(0, 4)
  if (v.length >= 3) v = v.slice(0, 2) + '/' + v.slice(2)
  tarjeta.vence = v
}

function validarTarjeta() {
  const digitos = tarjeta.numero.replace(/\s/g, '')
  erroresTarjeta.numero = /^\d{13,16}$/.test(digitos) ? '' : 'Escribe un número de tarjeta válido.'
  erroresTarjeta.nombre = tarjeta.nombre.trim() ? '' : 'Escribe el nombre de la tarjeta.'
  const m = tarjeta.vence.match(/^(\d{2})\/(\d{2})$/)
  erroresTarjeta.vence = m && +m[1] >= 1 && +m[1] <= 12 ? '' : 'Usa el formato MM/AA.'
  erroresTarjeta.cvv = /^\d{3,4}$/.test(tarjeta.cvv) ? '' : 'El CVV tiene 3 o 4 dígitos.'
  return !Object.values(erroresTarjeta).some(Boolean)
}

function pagar() {
  if (!validarTarjeta()) return
  cambiarPlan(planElegido.value.clave)
}
</script>

<template>
  <div class="pagina">
    <BarraPagina titulo="Mi plan" />

    <div class="contenedor">
      <header class="cabecera">
        <h1 class="titulo-pagina">Mi plan</h1>
        <p class="texto-intro">
          Tu cuenta está en el plan <strong>{{ nombrePlan(planActual) }}</strong>. Cámbialo cuando quieras.
        </p>
        <p v-if="auth.soloLectura" class="alerta alerta-info" role="status">
          <Icono nombre="ver" />
          <span>Estás en modo solo lectura: no puedes cambiar el plan.</span>
        </p>
      </header>

      <p v-if="error" class="alerta alerta-error mt-2" role="alert">
        <Icono nombre="alerta" />
        <span>{{ error }}</span>
      </p>

      <section class="planes" aria-label="Planes disponibles">
        <article
          v-for="plan in PLANES"
          :key="plan.clave"
          class="plan"
          :class="{ actual: plan.clave === planActual, destacado: plan.destacado }"
        >
          <p v-if="plan.clave === planActual" class="plan-badge actual-badge">Tu plan actual</p>
          <p v-else-if="plan.destacado" class="plan-badge">Más popular</p>

          <h2 class="plan-nombre">{{ plan.nombre }}</h2>
          <p class="plan-precio">
            <span class="plan-monto numero">{{ plan.precio }}</span>
            <span class="plan-periodo">{{ plan.periodo }}</span>
          </p>
          <p class="plan-resumen">{{ plan.resumen }}</p>
          <ul class="plan-incluye">
            <li v-for="item in plan.incluye" :key="item">
              <Icono nombre="check" :tamano="16" />
              <span>{{ item }}</span>
            </li>
          </ul>

          <button
            v-if="plan.clave === planActual"
            type="button"
            class="btn btn-secundario plan-cta"
            disabled
          >
            Plan actual
          </button>
          <button
            v-else
            type="button"
            class="btn plan-cta"
            :class="plan.destacado ? 'btn-primario' : 'btn-contorno'"
            :disabled="auth.soloLectura || cambiando"
            @click="elegir(plan)"
          >
            {{ plan.clave === 'gratis' ? 'Cambiar a Gratis' : 'Suscribirme' }}
          </button>
        </article>
      </section>
    </div>

    <!-- Simulación de tarjeta -->
    <DialogoBase
      :abierto="dialogoTarjeta"
      :titulo="`Suscribirme al plan ${planElegido?.nombre || ''}`"
      :descripcion="`${planElegido?.precio || ''} ${planElegido?.periodo || ''} · Es una simulación, no se cobra nada.`"
      ancho="460px"
      @cerrar="dialogoTarjeta = false"
    >
      <form class="formulario" novalidate @submit.prevent="pagar">
        <div class="campo">
          <label for="t-numero">Número de tarjeta</label>
          <div class="numero-tarjeta">
            <input
              id="t-numero"
              v-model="tarjeta.numero"
              class="entrada numero"
              :class="{ 'con-marca': marcaTarjeta }"
              inputmode="numeric"
              autocomplete="cc-number"
              placeholder="4242 4242 4242 4242"
              autofocus
              :aria-invalid="!!erroresTarjeta.numero"
              @input="formatearNumero"
            />
            <span v-if="marcaTarjeta" class="marca-tarjeta" aria-live="polite">{{ marcaTarjeta }}</span>
          </div>
          <p v-if="erroresTarjeta.numero" class="error-campo">{{ erroresTarjeta.numero }}</p>
          <p v-else-if="marcaTarjeta" class="ayuda">Tarjeta detectada: {{ marcaTarjeta }}.</p>
        </div>
        <div class="campo">
          <label for="t-nombre">Nombre en la tarjeta</label>
          <input
            id="t-nombre"
            v-model="tarjeta.nombre"
            class="entrada"
            autocomplete="cc-name"
            placeholder="Como aparece en la tarjeta"
            :aria-invalid="!!erroresTarjeta.nombre"
          />
          <p v-if="erroresTarjeta.nombre" class="error-campo">{{ erroresTarjeta.nombre }}</p>
        </div>
        <div class="campos-dos">
          <div class="campo">
            <label for="t-vence">Vencimiento</label>
            <input
              id="t-vence"
              v-model="tarjeta.vence"
              class="entrada numero"
              inputmode="numeric"
              autocomplete="cc-exp"
              placeholder="MM/AA"
              :aria-invalid="!!erroresTarjeta.vence"
              @input="formatearVence"
            />
            <p v-if="erroresTarjeta.vence" class="error-campo">{{ erroresTarjeta.vence }}</p>
          </div>
          <div class="campo">
            <label for="t-cvv">CVV</label>
            <input
              id="t-cvv"
              v-model="tarjeta.cvv"
              class="entrada numero"
              inputmode="numeric"
              autocomplete="cc-csc"
              maxlength="4"
              placeholder="123"
              :aria-invalid="!!erroresTarjeta.cvv"
            />
            <p v-if="erroresTarjeta.cvv" class="error-campo">{{ erroresTarjeta.cvv }}</p>
          </div>
        </div>

        <p v-if="error" class="alerta alerta-error" role="alert">
          <Icono nombre="alerta" />
          <span>{{ error }}</span>
        </p>

        <div class="acciones-dialogo">
          <button type="button" class="btn btn-secundario" @click="dialogoTarjeta = false">Cancelar</button>
          <button type="submit" class="btn btn-primario" :disabled="cambiando">
            {{ cambiando ? 'Procesando…' : 'Agregar tarjeta y suscribirme' }}
          </button>
        </div>
      </form>
    </DialogoBase>
  </div>
</template>

<style scoped>
.cabecera {
  padding-top: 56px;
  display: grid;
  gap: 10px;
  max-width: 44em;
}

.cabecera .alerta {
  margin-top: 6px;
}

.planes {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.plan {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--color-superficie);
  border: 1px solid var(--color-linea);
  border-radius: var(--radio);
  padding: 28px 24px;
}

.plan.destacado {
  border-color: var(--color-accion);
}

.plan.actual {
  border-color: var(--color-exito);
  box-shadow: 0 0 0 1px var(--color-exito);
}

.plan-badge {
  position: absolute;
  top: -12px;
  left: 24px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 980px;
  background: var(--color-accion);
  color: #fff;
}

.plan-badge.actual-badge {
  background: var(--color-exito);
}

.plan-nombre {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.015em;
}

.plan-precio {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 12px;
}

.plan-monto {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.plan-periodo {
  font-size: 14px;
  color: var(--color-texto-2);
}

.plan-resumen {
  color: var(--color-texto-2);
  font-size: 14px;
  line-height: 1.4;
  margin-top: 10px;
  min-height: 2.8em;
}

.plan-incluye {
  list-style: none;
  padding: 0;
  margin: 18px 0 24px;
  display: grid;
  gap: 10px;
}

.plan-incluye li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
}

.plan-incluye svg {
  color: var(--color-exito);
  flex-shrink: 0;
  margin-top: 2px;
}

.plan-cta {
  margin-top: auto;
  width: 100%;
}

/* Marca de la tarjeta (Visa, Mastercard…) detectada dentro del campo */
.numero-tarjeta {
  position: relative;
}

.numero-tarjeta .entrada.con-marca {
  padding-right: 128px;
}

.marca-tarjeta {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  padding: 4px 10px;
  border-radius: 8px;
  background: var(--color-linea-suave);
  color: var(--color-texto);
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  pointer-events: none;
}

@media (max-width: 920px) {
  .planes {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .planes {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
