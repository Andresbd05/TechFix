"""
Prueba la conexión a MySQL usando los datos de config.py.

Uso:
    cd Backend
    python check_db.py

Si algo falla, el mensaje te dice qué revisar (contraseña, puerto o si falta
cargar la base). No modifica nada: solo se conecta y cuenta las filas.
"""
import sys

try:
    import MySQLdb  # lo instala Flask-MySQLdb (mysqlclient)
except ImportError:
    print("Falta el conector de MySQL. Instálalo con:")
    print("    pip install -r requirements.txt")
    sys.exit(1)

from config import Config

host = Config.MYSQL_HOST
port = getattr(Config, "MYSQL_PORT", 3306)
usuario = Config.MYSQL_USER
base = Config.MYSQL_DB

print(f"Intentando conectar a {usuario}@{host}:{port} ...")

try:
    conexion = MySQLdb.connect(
        host=host,
        user=usuario,
        passwd=Config.MYSQL_PASSWORD,
        port=port,
    )
except Exception as e:
    print("\nNo se pudo conectar al servidor MySQL.")
    print(f"  Detalle: {e}")
    print("\nRevisa en Backend/config.py:")
    print("  - MYSQL_PASSWORD: la contraseña de tu usuario root de MySQL.")
    print(f"  - MYSQL_PORT: ahora dice {port}. El valor típico es 3306.")
    print("  - Que el servidor MySQL esté encendido.")
    sys.exit(1)

cur = conexion.cursor()

# ¿Existe la base techfix_db?
cur.execute("SHOW DATABASES LIKE %s", (base,))
if cur.fetchone() is None:
    print(f"\nConexión al servidor OK, pero la base '{base}' no existe todavía.")
    print("Cárgala con el archivo database/techfix_db.sql (ver README).")
    cur.close()
    conexion.close()
    sys.exit(1)

cur.execute(f"USE `{base}`")
cur.execute("SELECT COUNT(*) FROM usuarios")
total_usuarios = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM reparaciones")
total_reparaciones = cur.fetchone()[0]

print("\nConexión correcta.")
print(f"  Base de datos: {base}")
print(f"  Usuarios registrados: {total_usuarios}")
print(f"  Reparaciones registradas: {total_reparaciones}")

cur.close()
conexion.close()
