-- ============================================================================
--  TechFix - Migracion de roles/plan/nombre (version PostgreSQL)
--
--  Agrega los roles 'propietario' e 'invitado', la columna 'plan' y la columna
--  'nombre', SIN borrar datos. Usala SOLO si ya tienes una base techfix_db en
--  PostgreSQL (hecha con una version anterior) con informacion que quieres
--  conservar. Si empiezas de cero, NO necesitas esto: carga
--  techfix_db_postgres.sql, que ya trae todo.
--
--  NOTA de PostgreSQL:
--   * Agregar valores a un tipo ENUM se hace con  ALTER TYPE ... ADD VALUE.
--     Ese comando no puede ejecutarse dentro de una transaccion junto con
--     sentencias que ya usen el valor nuevo; por eso aqui va primero y solo.
--   * PostgreSQL no tiene "AFTER columna": las columnas nuevas quedan al final.
--     La posicion no afecta el funcionamiento.
--
--  Con psql:  psql -U postgres -d techfix_db -f migracion_roles_postgres.sql
-- ============================================================================

\c techfix_db

-- 1. Asegura que exista el tipo de rol y que incluya los roles nuevos.
--    Si la base vieja aun no tenia un tipo ENUM para 'rol' (por ejemplo, era
--    un VARCHAR), crea el tipo y convierte la columna.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rol_usuario') THEN
        CREATE TYPE rol_usuario AS ENUM
            ('propietario', 'admin', 'tecnico', 'invitado');
        ALTER TABLE usuarios
            ALTER COLUMN rol DROP DEFAULT,
            ALTER COLUMN rol TYPE rol_usuario USING rol::rol_usuario,
            ALTER COLUMN rol SET DEFAULT 'tecnico';
    END IF;
END$$;

-- Si el tipo ya existia pero sin estos valores, los agrega.
ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'propietario';
ALTER TYPE rol_usuario ADD VALUE IF NOT EXISTS 'invitado';

-- 2. Tipo ENUM para el plan + columna 'plan' (los usuarios existentes quedan
--    en 'gratis').
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plan_usuario') THEN
        CREATE TYPE plan_usuario AS ENUM ('gratis', 'basico', 'pro', 'empresa');
    END IF;
END$$;

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS plan plan_usuario NOT NULL DEFAULT 'gratis';

-- 3. Columna 'nombre' (para mostrar en la app).
ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS nombre VARCHAR(100) DEFAULT NULL;

-- 4. Usuarios de ejemplo para los roles nuevos.
--    Claves: propietario -> Dueno123*   ·   invitado -> Invitado123*
INSERT INTO usuarios (username, password_hash, nombre, rol, cedula_tecnico, plan) VALUES
('propietario', 'scrypt:32768:8:1$VOdlVAUI6Iss39cZ$e0b1dd4d04a72d30a9feb138674864cc231a92d7ee385c1b4cf422a398b48ea865e4ee910654b345d18d01bf84b6322a274925434075ded59b74ec3d902468db', 'Dueño del taller', 'propietario', NULL, 'gratis'),
('invitado', 'scrypt:32768:8:1$vbx5SnkYNj6jRV7V$1d489929ea81d46630518609fd1fb7698a4dbd9f7a66cb1673707a6271e2cafd663199a5dae94ce08ff85aedb3a4b3a098a46a100e1bc478edfd4dedd260d9b2', 'Invitado', 'invitado', NULL, 'gratis')
ON CONFLICT (username) DO NOTHING;
