import os
from flask import Flask, g
from flask_cors import CORS
import psycopg2
from config import Config

# 1. Inicializamos la aplicación Flask
app = Flask(__name__)

# 1.1 Permitimos que el frontend (otro dominio/puerto) consuma esta API.
#     Si defines CORS_ORIGINS (la URL de tu frontend; varias separadas por coma)
#     se restringe a esos orígenes; si no, se permite cualquiera.
_origenes = os.environ.get('CORS_ORIGINS')
if _origenes:
    CORS(app, origins=[o.strip() for o in _origenes.split(',') if o.strip()])
else:
    CORS(app)

# 2. Cargamos la configuración (que a su vez lee Backend/.env)
app.config.from_object(Config)


# 3. Conexión a PostgreSQL (Supabase).
#    Abrimos una conexión por cada petición y la guardamos en 'g'; se cierra
#    sola cuando la petición termina (teardown_appcontext, más abajo).
#    Antes de esto, de la conexión se encargaba Flask-MySQLdb.
def obtener_conexion():
    if 'conexion_db' not in g:
        url = app.config.get('DATABASE_URL')
        if not url:
            raise RuntimeError(
                "Falta DATABASE_URL. Copia Backend/.env.example a Backend/.env "
                "y pega la cadena de conexión de Supabase."
            )
        g.conexion_db = psycopg2.connect(url)
    return g.conexion_db


class _BaseDeDatos:
    """Compatibilidad con el resto del código: las rutas siguen usando
    db.connection.cursor() / .commit() / .rollback(), igual que antes."""

    @property
    def connection(self):
        return obtener_conexion()


db = _BaseDeDatos()


@app.teardown_appcontext
def cerrar_conexion(error=None):
    conexion = g.pop('conexion_db', None)
    if conexion is not None:
        conexion.close()


# Ruta de salud: visitar la raíz "/" confirma que la API está viva.
@app.route('/')
def inicio():
    return {"servicio": "TechFix API", "estado": "ok"}, 200


# 4. Importamos y registramos los Blueprints (antes eran 3 microservicios:
#    ms_taller, ms_inventario y ms_clientes; ahora viven en una sola API)
from routes.login import login_bp
from routes.clientes import clientes_bp
from routes.repuestos import repuestos_bp
from routes.reparaciones import reparaciones_bp

app.register_blueprint(login_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(repuestos_bp)
app.register_blueprint(reparaciones_bp)

# 5. Encendemos el servidor en el puerto 5000
if __name__ == '__main__':
    print("Iniciando el Servicio de TechFix en el puerto 5000...")
    app.run(debug=True, port=5000)
