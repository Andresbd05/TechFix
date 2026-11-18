import os
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables de Backend/.env (sin importar desde qué carpeta se ejecute).
# Ese archivo .env NO se sube a git: está en .gitignore.
load_dotenv(Path(__file__).resolve().parent / '.env')


class Config:
    # Cadena de conexión de PostgreSQL / Supabase.
    # Ejemplo (pooler):
    #   postgresql://postgres.<REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:6543/postgres?sslmode=require
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Clave secreta para firmar los tokens JWT (debe venir del .env).
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # Minutos que dura la sesión antes de expirar.
    JWT_EXPIRATION_MINUTES = int(os.environ.get('JWT_EXPIRATION_MINUTES', '30'))
