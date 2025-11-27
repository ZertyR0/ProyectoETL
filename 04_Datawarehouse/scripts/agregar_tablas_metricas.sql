-- ===================================================================
-- SCRIPT: Agregar Tablas de Métricas al DataWarehouse
-- Propósito: Crear tablas para almacenar métricas de calidad, RRHH
--            y satisfacción que se calcularán desde la BD origen
-- Fecha: 2025-11-25
-- ===================================================================

USE dw_proyectos_hist;

-- Tabla de hechos para defectos de calidad
CREATE TABLE IF NOT EXISTS HechoDefecto (
    id_hecho_defecto BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT NOT NULL,
    id_tiempo_reporte INT NOT NULL,
    id_tiempo_resolucion INT NULL,
    severidad ENUM('Baja', 'Media', 'Alta', 'Crítica'),
    estado ENUM('Abierto', 'En Progreso', 'Resuelto', 'Cerrado'),
    dias_resolucion INT NULL,
    INDEX idx_proyecto (id_proyecto),
    INDEX idx_tiempo (id_tiempo_reporte)
) ENGINE=InnoDB;

-- Tabla de hechos para capacitaciones
CREATE TABLE IF NOT EXISTS HechoCapacitacion (
    id_hecho_capacitacion BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_tiempo_inicio INT NOT NULL,
    id_tiempo_fin INT NULL,
    nombre_curso VARCHAR(200),
    horas_duracion INT,
    estado ENUM('Planificada', 'En Curso', 'Completada', 'Cancelada'),
    INDEX idx_empleado (id_empleado),
    INDEX idx_tiempo (id_tiempo_inicio)
) ENGINE=InnoDB;

-- Tabla de hechos para satisfacción del cliente
CREATE TABLE IF NOT EXISTS HechoSatisfaccion (
    id_hecho_satisfaccion BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_proyecto INT NOT NULL,
    id_cliente INT NOT NULL,
    id_tiempo_evaluacion INT NOT NULL,
    calificacion DECIMAL(3,2),
    INDEX idx_proyecto (id_proyecto),
    INDEX idx_cliente (id_cliente)
) ENGINE=InnoDB;

-- Tabla de hechos para movimientos de empleados
CREATE TABLE IF NOT EXISTS HechoMovimientoEmpleado (
    id_hecho_movimiento BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_tiempo_movimiento INT NOT NULL,
    tipo_movimiento ENUM('Ingreso', 'Egreso', 'Promoción', 'Transferencia'),
    INDEX idx_empleado (id_empleado),
    INDEX idx_tiempo (id_tiempo_movimiento),
    INDEX idx_tipo (tipo_movimiento)
) ENGINE=InnoDB;

SELECT 'Tablas de métricas creadas en DataWarehouse' AS status;

-- Mostrar estructura creada
SELECT 
    'HechoDefecto' as tabla,
    COUNT(*) as registros 
FROM HechoDefecto
UNION ALL
SELECT 'HechoCapacitacion', COUNT(*) FROM HechoCapacitacion
UNION ALL
SELECT 'HechoSatisfaccion', COUNT(*) FROM HechoSatisfaccion
UNION ALL
SELECT 'HechoMovimientoEmpleado', COUNT(*) FROM HechoMovimientoEmpleado;
