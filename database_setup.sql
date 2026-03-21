-- Base de datos para el detector de fatiga
CREATE DATABASE IF NOT EXISTS detector_fatiga CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE detector_fatiga;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    hash_contrasena VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    INDEX idx_nombre_usuario (nombre_usuario)
) ENGINE=InnoDB;

-- Tabla de sesiones
CREATE TABLE IF NOT EXISTS sesiones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    inicio_sesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fin_sesion TIMESTAMP NULL,
    metodo_autenticacion ENUM('contrasena', 'gestos_faciales', 'ambos') NOT NULL,
    duracion_segundos INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_sesiones_usuario (usuario_id, inicio_sesion)
) ENGINE=InnoDB;

-- Tabla de eventos de fatiga
CREATE TABLE IF NOT EXISTS eventos_fatiga (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    tipo_evento ENUM('ojos_cerrados', 'bostezo', 'cabeza_abajo', 'alerta_activada', 'quiz_respondido') NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severidad ENUM('baja', 'media', 'alta') DEFAULT 'baja',
    detalles JSON,
    FOREIGN KEY (sesion_id) REFERENCES sesiones(id) ON DELETE CASCADE,
    INDEX idx_eventos_sesion (sesion_id, fecha_evento)
) ENGINE=InnoDB;

-- Tabla de respuestas de quiz
CREATE TABLE IF NOT EXISTS respuestas_quiz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    pregunta TEXT NOT NULL,
    respuesta_esperada VARCHAR(100),
    respuesta_usuario VARCHAR(100),
    es_correcta BOOLEAN,
    tiempo_respuesta_ms INT,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones(id) ON DELETE CASCADE,
    INDEX idx_quiz_sesion (sesion_id, fecha_respuesta)
) ENGINE=InnoDB;

-- Tabla de logs del sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nivel_log ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    mensaje TEXT NOT NULL,
    modulo VARCHAR(100),
    nombre_funcion VARCHAR(100),
    sesion_id INT NULL,
    fecha_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalles JSON,
    FOREIGN KEY (sesion_id) REFERENCES sesiones(id) ON DELETE SET NULL,
    INDEX idx_nivel_log (nivel_log, fecha_log),
    INDEX idx_logs_sesion (sesion_id, fecha_log)
) ENGINE=InnoDB;

-- Tabla de validaciones de sistema
CREATE TABLE IF NOT EXISTS validaciones_sistema (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_validacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    camara_disponible BOOLEAN,
    microfono_disponible BOOLEAN,
    altavoz_disponible BOOLEAN,
    configuracion_valida BOOLEAN,
    modelo_ia_cargado BOOLEAN,
    detalles_validacion JSON
) ENGINE=InnoDB;

-- Insertar usuario de prueba (contraseña: admin123)
INSERT INTO usuarios (nombre_usuario, hash_contrasena, nombre_completo) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxHZb7HVm', 'Administrador')
ON DUPLICATE KEY UPDATE nombre_usuario=nombre_usuario;
