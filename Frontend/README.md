# TechFix · Frontend

Interfaz en Vue 3 + Pinia + Vue Router para la API de TechFix (`../Backend`).

## Cómo correrlo

1. Levanta el backend (puerto 5000):

   ```sh
   cd ../Backend
   pip install -r requirements.txt
   python app.py
   ```

2. En otra terminal, levanta el front:

   ```sh
   npm install
   npm run dev
   ```

3. Abre la URL que muestra Vite (normalmente http://localhost:5173).

La URL de la API se configura en `.env`:

```
VITE_API_URL=http://localhost:5000
```

## Estructura

```
src/
├── assets/          base.css (colores y tipografía) y main.css (componentes)
├── components/
│   ├── layout/      NavBar (barra superior) y BarraPagina (barra de cada pantalla)
│   ├── ui/          Diálogos, ícono, etiqueta de estado y aviso flotante
│   ├── reparaciones/ Flujo del taller, progreso y diálogo de nueva reparación
│   ├── clientes/    Diálogo para crear/editar clientes
│   └── inventario/  Diálogos de repuesto y de entrada/salida de stock
├── router/          Rutas y guardias (sesión y rol admin)
├── services/        Llamadas a la API con axios (una por recurso)
├── stores/          Estado con Pinia (auth, clientes, repuestos, reparaciones, avisos)
├── utils/           Formato de pesos y fechas, estados, marcas y errores
└── views/           Una vista por pantalla
```

## Roles

- **Administrador:** todo, más asignar técnicos y crear usuarios.
- **Técnico:** ve todo el taller, pero solo avanza y agrega repuestos a sus reparaciones.

El front oculta lo que cada rol no puede hacer, pero quien decide es el backend:
si algo no está permitido, la API responde 403 y el mensaje se muestra en pantalla.
