from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from config import Config

# 1. Inicializamos la aplicación Flask
app = Flask(__name__)

# 1.1 Permitimos que el frontend de Vue (otro puerto) consuma esta API
CORS(app)

# 2. Cargamos la configuración de la base de datos
app.config.from_object(Config)

# 3. Inicializamos la conexión a MySQL
mysql = MySQL(app)

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
