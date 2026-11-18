"""
Prueba la conexión a PostgreSQL (Supabase) usando DATABASE_URL de Backend/.env.

Uso:
    cd Backend
    python check_db.py

No modifica nada: solo se conecta y cuenta las filas. Si algo falla, el mensaje
te dice qué revisar (la cadena de conexión, el SSL o si falta cargar la base).
"""
import re
import sys

try:
    import psycopg2
except ImportError:
    print("Falta psycopg2. Instálalo con:")
    print("    pip install -r requirements.txt")
    sys.exit(1)

from config import Config

url = Config.DATABASE_URL
if not url:
    print("Falta DATABASE_URL.")
    print("Copia Backend/.env.example a Backend/.env y pega tu cadena de Supabase.")
    sys.exit(1)

# Ocultamos la contraseña al imprimir la cadena
url_segura = re.sub(r'://([^:/@]+):[^@]+@', r'://\1:***@', url)
print(f"Intentando conectar a {url_segura} ...")

try:
    conexion = psycopg2.connect(url)
except Exception as e:
    print("\nNo se pudo conectar a PostgreSQL.")
    print(f"  Detalle: {e}")
    print("\nRevisa en Backend/.env:")
    print("  - DATABASE_URL: la cadena de conexión de Supabase (con tu contraseña).")
    print("  - Que termine en ?sslmode=require")
    print("  - El puerto: 6543 (pooler, recomendado) o 5432 (conexión directa).")
    sys.exit(1)

cur = conexion.cursor()

try:
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM reparaciones")
    total_reparaciones = cur.fetchone()[0]
except Exception as e:
    print("\nConexión al servidor OK, pero no encuentro las tablas.")
    print("¿Cargaste database/techfix_db_postgres.sql en tu base de Supabase?")
    print(f"  Detalle: {e}")
    cur.close()
    conexion.close()
    sys.exit(1)

print("\nConexión correcta.")
print(f"  Usuarios registrados: {total_usuarios}")
print(f"  Reparaciones registradas: {total_reparaciones}")

cur.close()
conexion.close()
