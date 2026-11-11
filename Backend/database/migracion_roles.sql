-- Migración: agrega los roles 'propietario' e 'invitado', la columna 'plan'
-- y la columna 'nombre', SIN borrar datos. Úsala solo si YA tienes la base
-- techfix_db cargada con información que quieres conservar. Si vas a empezar
-- de cero, no necesitas esto: carga techfix_db.sql, que ya trae todo.

USE techfix_db;

-- 1. Amplía el enum de roles
ALTER TABLE usuarios
    MODIFY rol ENUM('propietario', 'admin', 'tecnico', 'invitado') NOT NULL DEFAULT 'tecnico';

-- 2. Agrega la columna de plan (los usuarios existentes quedan en 'gratis')
ALTER TABLE usuarios
    ADD COLUMN plan ENUM('gratis', 'basico', 'pro', 'empresa') NOT NULL DEFAULT 'gratis' AFTER rol;

-- 3. Agrega la columna de nombre (para mostrar en la app)
ALTER TABLE usuarios
    ADD COLUMN nombre VARCHAR(100) DEFAULT NULL AFTER password_hash;

-- 4. Usuarios de ejemplo para los roles nuevos
--    Claves: propietario -> Dueno123*   ·   invitado -> Invitado123*
INSERT INTO usuarios (username, password_hash, nombre, rol, cedula_tecnico, plan) VALUES
('propietario', 'scrypt:32768:8:1$VOdlVAUI6Iss39cZ$e0b1dd4d04a72d30a9feb138674864cc231a92d7ee385c1b4cf422a398b48ea865e4ee910654b345d18d01bf84b6322a274925434075ded59b74ec3d902468db', 'Dueño del taller', 'propietario', NULL, 'gratis'),
('invitado', 'scrypt:32768:8:1$vbx5SnkYNj6jRV7V$1d489929ea81d46630518609fd1fb7698a4dbd9f7a66cb1673707a6271e2cafd663199a5dae94ce08ff85aedb3a4b3a098a46a100e1bc478edfd4dedd260d9b2', 'Invitado', 'invitado', NULL, 'gratis');
