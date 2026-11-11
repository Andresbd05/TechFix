SET NAMES utf8mb4;

DROP DATABASE IF EXISTS techfix_db;
CREATE DATABASE techfix_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE techfix_db;

CREATE TABLE clientes (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100)
);

CREATE TABLE marcas (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre_marca VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE equipos (
    id_equipo VARCHAR(20) PRIMARY KEY,
    cliente_cedula VARCHAR(20) NOT NULL,
    id_marca INT,
    tipo_dispositivo VARCHAR(20) NOT NULL,
    serial_imei VARCHAR(50) UNIQUE,
    FOREIGN KEY (cliente_cedula) REFERENCES clientes(cedula),
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
);

CREATE TABLE tecnicos (
    cedula_tecnico VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    reparacion_activa_id VARCHAR(20) DEFAULT NULL
);

CREATE TABLE reparaciones (
    id_reparacion VARCHAR(20) PRIMARY KEY,
    id_equipo VARCHAR(20) NOT NULL,
    cedula_tecnico VARCHAR(20),
    estado ENUM('Recibido', 'En revisión', 'En reparación', 'Listo', 'Entregado') NOT NULL DEFAULT 'Recibido',
    diagnostico TEXT NOT NULL,
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
    foto_evidencia_base64 LONGTEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo),
    FOREIGN KEY (cedula_tecnico) REFERENCES tecnicos(cedula_tecnico)
);

ALTER TABLE tecnicos
    ADD FOREIGN KEY (reparacion_activa_id) REFERENCES reparaciones(id_reparacion)
    ON DELETE SET NULL;

CREATE TABLE repuestos (
    sku_repuesto VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_marca INT,
    precio DECIMAL(10, 2) NOT NULL CHECK (precio >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
);

CREATE TABLE reparacion_repuestos (
    id_reparacion VARCHAR(20),
    sku_repuesto VARCHAR(30),
    cantidad INT NOT NULL CHECK (cantidad > 0),
    PRIMARY KEY (id_reparacion, sku_repuesto),
    FOREIGN KEY (id_reparacion) REFERENCES reparaciones(id_reparacion),
    FOREIGN KEY (sku_repuesto) REFERENCES repuestos(sku_repuesto)
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) DEFAULT NULL,
    rol ENUM('propietario', 'admin', 'tecnico', 'invitado') NOT NULL DEFAULT 'tecnico',
    plan ENUM('gratis', 'basico', 'pro', 'empresa') NOT NULL DEFAULT 'gratis',
    cedula_tecnico VARCHAR(20) DEFAULT NULL,
    FOREIGN KEY (cedula_tecnico) REFERENCES tecnicos(cedula_tecnico)
);

INSERT INTO clientes (cedula, nombre, telefono, correo) VALUES
('1061234567', 'Laura Gomez', '3109876543', 'laura.gomez@email.com'),
('1061987654', 'Carlos Restrepo', '3201234987', 'carlos.r@email.com'),
('1061555444', 'Diana Valencia', '3157778899', 'diana.val@email.com'),
('1061777888', 'Miguel Torres', '3004561234', 'miguel.torres@email.com'),
('1061222333', 'Valentina Ríos', '3112223344', 'vale.rios@email.com'),
('1061444555', 'Santiago Muñoz', '3185556677', 'santiago.m@email.com'),
('1061666777', 'Paula Cárdenas', '3226667788', 'paula.cardenas@email.com'),
('1061888999', 'Jorge Hernández', '3017778899', 'jorge.h@email.com'),
('1062111222', 'Camila Ortiz', '3148889900', 'camila.ortiz@email.com'),
('1062333444', 'Felipe Zúñiga', '3059990011', 'felipe.z@email.com');

INSERT INTO marcas (id_marca, nombre_marca) VALUES
(1, 'Samsung'),
(2, 'Apple'),
(3, 'Xiaomi'),
(4, 'Lenovo'),
(5, 'Asus'),
(6, 'Motorola'),
(7, 'HP'),
(8, 'Huawei');

INSERT INTO tecnicos (cedula_tecnico, nombre) VALUES
('1088111222', 'Javier Ruiz'),
('1088333444', 'Sofia Martinez'),
('1088555666', 'Andres Diaz'),
('1088777888', 'Camilo Rojas'),
('1088999000', 'Natalia Pérez');

INSERT INTO equipos (id_equipo, cliente_cedula, id_marca, tipo_dispositivo, serial_imei) VALUES
('TEL-4F2A', '1061234567', 1, 'Telefono', '358932145678901'),
('COM-9B3C', '1061987654', 4, 'Computador', 'PF2KX9B3'),
('TEL-1A2B', '1061555444', 2, 'Telefono', '356712345678902'),
('TEL-8C7D', '1061234567', 3, 'Telefono', '351234567890123'),
('TEL-5E6F', '1061777888', 6, 'Telefono', '359876543210987'),
('COM-2D4E', '1061222333', 7, 'Computador', '5CD1234XYZ'),
('TAB-7G8H', '1061444555', 1, 'Tablet', 'R52T90ABCDE'),
('TEL-3J4K', '1061666777', 2, 'Telefono', '353456789012345'),
('COM-6L7M', '1061888999', 5, 'Computador', 'M3N0CV12345678A'),
('TEL-9N0P', '1062111222', 8, 'Telefono', '867530912345678'),
('TEL-1Q2R', '1062333444', 1, 'Telefono', '352109876543210'),
('COM-4S5T', '1061555444', 2, 'Computador', 'C02ZK1ABMD6M'),
('TEL-6U7V', '1061777888', 3, 'Telefono', '864201357924680');

INSERT INTO repuestos (sku_repuesto, nombre, id_marca, precio, stock) VALUES
('PAN-SAM-S23', 'Pantalla OLED S23', 1, 450000.00, 10),
('BAT-APP-13', 'Batería iPhone 13', 2, 180000.00, 15),
('TEC-LEN-T14', 'Teclado ThinkPad T14', 4, 120000.00, 5),
('PIN-XIA-X3', 'Pin de carga Poco X3', 3, 35000.00, 30),
('PAN-APP-13', 'Pantalla iPhone 13', 2, 620000.00, 4),
('BAT-SAM-A54', 'Batería Galaxy A54', 1, 95000.00, 12),
('TAP-SAM-T8', 'Tapa trasera Galaxy Tab S8', 1, 85000.00, 3),
('PAN-MOT-G84', 'Pantalla Moto G84', 6, 210000.00, 6),
('BAT-HP-240', 'Batería HP 240 G8', 7, 160000.00, 2),
('VEN-ASU-TUF', 'Ventilador Asus TUF F15', 5, 75000.00, 8),
('PIN-HUA-P30', 'Pin de carga Huawei P30 Lite', 8, 30000.00, 20),
('BAT-APP-MBA', 'Batería MacBook Air M1', 2, 350000.00, 1),
('CAM-XIA-N12', 'Cámara trasera Redmi Note 12', 3, 110000.00, 0),
('SSD-GEN-512', 'Disco SSD 512 GB', NULL, 190000.00, 7),
('PAS-GEN-001', 'Pasta térmica', NULL, 15000.00, 25);

INSERT INTO reparaciones (id_reparacion, id_equipo, cedula_tecnico, estado, diagnostico, fecha_ingreso) VALUES
('REP-10B2', 'COM-9B3C', '1088111222', 'Entregado', 'Lento al encender, cambio de disco a SSD', '2026-06-30 14:00:00'),
('REP-10B1', 'TEL-4F2A', '1088555666', 'Entregado', 'Se reinicia solo, se reinstaló el sistema', '2026-07-15 10:20:00'),
('REP-10A1', 'TEL-5E6F', '1088777888', 'Entregado', 'Pantalla con líneas verdes', '2026-08-20 09:45:00'),
('REP-10A2', 'COM-2D4E', '1088999000', 'Entregado', 'Batería no retiene carga', '2026-08-25 16:10:00'),
('REP-10A3', 'TAB-7G8H', '1088111222', 'Entregado', 'Tapa trasera quebrada', '2026-09-01 11:30:00'),
('REP-10A4', 'COM-6L7M', '1088333444', 'Listo', 'Se recalienta y se apaga', '2026-09-05 15:00:00'),
('REP-10A5', 'TEL-9N0P', '1088555666', 'Listo', 'No carga, pin de carga sulfatado', '2026-09-12 08:40:00'),
('REP-99X1', 'TEL-4F2A', '1088111222', 'En revisión', 'Pantalla estrellada tras caída', '2026-09-08 09:00:00'),
('REP-99X2', 'COM-9B3C', '1088333444', 'Recibido', 'Teclado no responde', '2026-09-09 10:30:00'),
('REP-99X4', 'TEL-8C7D', '1088555666', 'En reparación', 'No carga, puerto USB-C dañado', '2026-09-10 11:00:00'),
('REP-10A6', 'TEL-3J4K', '1088777888', 'En reparación', 'Pantalla rota, el táctil no responde', '2026-10-06 13:15:00'),
('REP-10A7', 'COM-4S5T', '1088999000', 'En revisión', 'No enciende', '2026-10-09 17:30:00'),
('REP-99X3', 'TEL-1A2B', NULL, 'Recibido', 'Batería se descarga en 2 horas', '2026-09-10 08:15:00'),
('REP-10A8', 'TEL-1Q2R', NULL, 'Recibido', 'Batería inflada', '2026-10-13 12:00:00'),
('REP-10A9', 'TEL-6U7V', NULL, 'Recibido', 'Cámara trasera borrosa', '2026-10-14 09:30:00');

INSERT INTO reparacion_repuestos (id_reparacion, sku_repuesto, cantidad) VALUES
('REP-99X1', 'PAN-SAM-S23', 1),
('REP-99X4', 'PIN-XIA-X3', 1),
('REP-10B2', 'SSD-GEN-512', 1),
('REP-10A1', 'PAN-MOT-G84', 1),
('REP-10A2', 'BAT-HP-240', 1),
('REP-10A3', 'TAP-SAM-T8', 1),
('REP-10A4', 'VEN-ASU-TUF', 1),
('REP-10A4', 'PAS-GEN-001', 1),
('REP-10A5', 'PIN-HUA-P30', 1),
('REP-10A6', 'PAN-APP-13', 1);

UPDATE tecnicos SET reparacion_activa_id = 'REP-99X1' WHERE cedula_tecnico = '1088111222';
UPDATE tecnicos SET reparacion_activa_id = 'REP-99X2' WHERE cedula_tecnico = '1088333444';
UPDATE tecnicos SET reparacion_activa_id = 'REP-99X4' WHERE cedula_tecnico = '1088555666';
UPDATE tecnicos SET reparacion_activa_id = 'REP-10A6' WHERE cedula_tecnico = '1088777888';
UPDATE tecnicos SET reparacion_activa_id = 'REP-10A7' WHERE cedula_tecnico = '1088999000';

INSERT INTO usuarios (username, password_hash, nombre, rol, cedula_tecnico, plan) VALUES
('admin', 'scrypt:32768:8:1$eEs5hzv8FQVMaxRo$833756f93c40fef73c79d06689e48e9c0632c36fead49666012f8c0f0171e236210435794f6adab173a34cb3a0539e69794d6eb9f079e03931523b107d032899', 'Administrador', 'admin', NULL, 'gratis'),
('propietario', 'scrypt:32768:8:1$VOdlVAUI6Iss39cZ$e0b1dd4d04a72d30a9feb138674864cc231a92d7ee385c1b4cf422a398b48ea865e4ee910654b345d18d01bf84b6322a274925434075ded59b74ec3d902468db', 'Dueño del taller', 'propietario', NULL, 'gratis'),
('invitado', 'scrypt:32768:8:1$vbx5SnkYNj6jRV7V$1d489929ea81d46630518609fd1fb7698a4dbd9f7a66cb1673707a6271e2cafd663199a5dae94ce08ff85aedb3a4b3a098a46a100e1bc478edfd4dedd260d9b2', 'Invitado', 'invitado', NULL, 'gratis'),
('javier', 'scrypt:32768:8:1$Acn9V0YicYMVZ6Hr$8f1657768367fb18f092553ca85767e7ed619ca8af940be7f0a8ca8c35f2e481318de38873c8c2426772f768277b4a634f3b7af294eed5fe20e6777ae0fce908', 'Javier Ruiz', 'tecnico', '1088111222', 'gratis'),
('sofia', 'scrypt:32768:8:1$ArnHspVFBlX94tNn$f83c2a188442a07c1e4846d4c48f551e27015005d269604a6a73bbdc3b220501b6f56daadc9723ab472d64c7bc7e09183d1a384d5564113b0bb9121cfabcf559', 'Sofía Martínez', 'tecnico', '1088333444', 'gratis'),
('andres', 'scrypt:32768:8:1$KRN3fMS8JJdfDZrS$07acacde127a7df0f0f602e46244bff3d5e9cdd3d12f41151e7958c7df5f58e67dfd7c8cad840eab9e795495448457232c2b2242fec12bb6f9128d9f4f64065d', 'Andrés Díaz', 'tecnico', '1088555666', 'gratis'),
('camilo', 'scrypt:32768:8:1$MpK1cBm7RCxexsnf$1f4033a8aee5a148a1aaf45fcee3981a267ef9880a942b6c78ccdaa6f07069c8a7707de4f94c84d685c63dc874371a886ae381fd87fbf7058f4839ba8f8600df', 'Camilo Rojas', 'tecnico', '1088777888', 'gratis'),
('natalia', 'scrypt:32768:8:1$XzauxyklZIxluW8m$7544399a6c03bdbac3a3288fbadc47edc1c68e06746d7ec2b0b76d164f9edaa68f9079cf6ebf2940483757ae0fcb0621088986f57d16173d3afe587bbe58c669', 'Natalia Pérez', 'tecnico', '1088999000', 'gratis');
