-- ============================================================
-- EPS CITAS - Base de Datos Completa con Datos de Prueba
-- ============================================================

CREATE DATABASE IF NOT EXISTS eps_citas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eps_citas;

-- ============================================================
-- TABLA: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  documento VARCHAR(15) UNIQUE NOT NULL,
  nombre VARCHAR(80) NOT NULL,
  apellido VARCHAR(80) NOT NULL,
  telefono VARCHAR(20),
  correo VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('paciente','doctor','admin') NOT NULL,
  eps VARCHAR(100),
  activo TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA: doctores
-- ============================================================
CREATE TABLE IF NOT EXISTS doctores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  especialidad VARCHAR(100) NOT NULL,
  consultorio VARCHAR(50),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================================
-- TABLA: citas
-- ============================================================
CREATE TABLE IF NOT EXISTS citas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  paciente_doc VARCHAR(15) NOT NULL,
  doctor_id INT NOT NULL,
  tipo_cita VARCHAR(50) NOT NULL,
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  direccion_eps VARCHAR(150),
  estado ENUM('pendiente','atendida','no_asistio','cancelada') DEFAULT 'pendiente',
  notas TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (paciente_doc) REFERENCES usuarios(documento),
  FOREIGN KEY (doctor_id) REFERENCES doctores(id)
);

-- ============================================================
-- DATOS DE PRUEBA
-- Passwords: todos usan "password123" hasheado con werkzeug
-- Hash generado: pbkdf2:sha256:...
-- Para pruebas usar: werkzeug.security.generate_password_hash("password123")
-- ============================================================

-- Admin
INSERT INTO usuarios (documento, nombre, apellido, telefono, correo, password, rol, eps) VALUES
('1000000001', 'Carlos', 'Administrador', '3001234567', 'admin@eps.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'admin', 'EPS Sura');

-- Doctores
INSERT INTO usuarios (documento, nombre, apellido, telefono, correo, password, rol, eps) VALUES
('2000000001', 'María', 'González', '3109876543', 'maria.gonzalez@eps.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'doctor', 'EPS Sura'),
('2000000002', 'Andrés', 'Martínez', '3156789012', 'andres.martinez@eps.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'doctor', 'EPS Sura'),
('2000000003', 'Laura', 'Rodríguez', '3187654321', 'laura.rodriguez@eps.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'doctor', 'EPS Sura'),
('2000000004', 'Felipe', 'Castro', '3212345678', 'felipe.castro@eps.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'doctor', 'EPS Sura');

-- Pacientes
INSERT INTO usuarios (documento, nombre, apellido, telefono, correo, password, rol, eps) VALUES
('3000000001', 'Juan', 'Pérez', '3001111111', 'juan.perez@gmail.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'paciente', 'EPS Sura'),
('3000000002', 'Ana', 'López', '3002222222', 'ana.lopez@gmail.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'paciente', 'EPS Sanitas'),
('3000000003', 'Pedro', 'Ramírez', '3003333333', 'pedro.ramirez@gmail.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'paciente', 'EPS Sura'),
('3000000004', 'Sofía', 'Herrera', '3004444444', 'sofia.herrera@gmail.com',
 'pbkdf2:sha256:260000$rK8mQZ2X$a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 'paciente', 'EPS Compensar');

-- Registrar doctores en tabla doctores
INSERT INTO doctores (usuario_id, especialidad, consultorio) VALUES
((SELECT id FROM usuarios WHERE documento='2000000001'), 'Medicina General', 'Cons. 101'),
((SELECT id FROM usuarios WHERE documento='2000000002'), 'Odontología', 'Cons. 202'),
((SELECT id FROM usuarios WHERE documento='2000000003'), 'Cardiología', 'Cons. 305'),
((SELECT id FROM usuarios WHERE documento='2000000004'), 'Pediatría', 'Cons. 410');

-- Citas de prueba
INSERT INTO citas (paciente_doc, doctor_id, tipo_cita, fecha, hora, direccion_eps, estado, notas) VALUES
('3000000001', 1, 'Consulta General', DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00:00', 'Cra 43A #5A-113, Medellín', 'pendiente', NULL),
('3000000002', 1, 'Consulta General', DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:30:00', 'Cra 43A #5A-113, Medellín', 'pendiente', NULL),
('3000000003', 2, 'Limpieza Dental', DATE_ADD(CURDATE(), INTERVAL 3 DAY), '10:00:00', 'Cra 43A #5A-113, Medellín', 'pendiente', NULL),
('3000000001', 3, 'Electrocardiograma', DATE_ADD(CURDATE(), INTERVAL 5 DAY), '14:00:00', 'Cl 10 #32-16, Medellín', 'pendiente', NULL),
('3000000004', 4, 'Control Pediátrico', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00:00', 'Cra 43A #5A-113, Medellín', 'pendiente', NULL),
('3000000002', 3, 'Consulta Cardiología', DATE_SUB(CURDATE(), INTERVAL 5 DAY), '11:00:00', 'Cl 10 #32-16, Medellín', 'atendida', 'Paciente en buenas condiciones'),
('3000000003', 1, 'Consulta General', DATE_SUB(CURDATE(), INTERVAL 10 DAY), '09:30:00', 'Cra 43A #5A-113, Medellín', 'no_asistio', 'No se presentó a la cita'),
('3000000001', 2, 'Revisión Dental', DATE_SUB(CURDATE(), INTERVAL 15 DAY), '15:00:00', 'Cra 43A #5A-113, Medellín', 'atendida', 'Revisión rutinaria completada');
