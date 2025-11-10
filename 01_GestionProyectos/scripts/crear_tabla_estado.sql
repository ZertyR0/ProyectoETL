-- ============================================================
-- CREAR TABLA ESTADO FALTANTE
-- Base de datos: gestionproyectos_hist
-- Máquina 1: 172.20.10.3
-- ============================================================

USE gestionproyectos_hist;

-- Crear tabla Estado si no existe
CREATE TABLE IF NOT EXISTS Estado (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    tipo_entidad ENUM('proyecto', 'tarea', 'general') DEFAULT 'general',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar estados predefinidos si no existen
INSERT IGNORE INTO Estado (nombre_estado, descripcion, tipo_entidad) VALUES
    -- Estados de Proyecto
    ('Planificación', 'Proyecto en fase de planificación', 'proyecto'),
    ('En Proceso', 'Proyecto en ejecución', 'proyecto'),
    ('En Pausa', 'Proyecto pausado temporalmente', 'proyecto'),
    ('Completado', 'Proyecto finalizado exitosamente', 'proyecto'),
    ('Cancelado', 'Proyecto cancelado', 'proyecto'),
    
    -- Estados de Tarea
    ('Pendiente', 'Tarea pendiente de iniciar', 'tarea'),
    ('En Progreso', 'Tarea en desarrollo', 'tarea'),
    ('En Revisión', 'Tarea en proceso de revisión', 'tarea'),
    ('Bloqueada', 'Tarea bloqueada por dependencias', 'tarea'),
    ('Terminada', 'Tarea completada', 'tarea'),
    
    -- Estados Generales
    ('Activo', 'Registro activo', 'general'),
    ('Inactivo', 'Registro inactivo', 'general');

-- Verificar que las tablas Proyecto y Tarea tengan la columna id_estado
-- Si no existe, agregarla

-- Para tabla Proyecto
SET @dbname = DATABASE();
SET @tablename = 'Proyecto';
SET @columnname = 'id_estado';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      TABLE_SCHEMA = @dbname
      AND TABLE_NAME = @tablename
      AND COLUMN_NAME = @columnname
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT, ADD CONSTRAINT fk_proyecto_estado FOREIGN KEY (', @columnname, ') REFERENCES Estado(id_estado)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Para tabla Tarea
SET @tablename = 'Tarea';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      TABLE_SCHEMA = @dbname
      AND TABLE_NAME = @tablename
      AND COLUMN_NAME = @columnname
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' INT, ADD CONSTRAINT fk_tarea_estado FOREIGN KEY (', @columnname, ') REFERENCES Estado(id_estado)')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Actualizar proyectos existentes sin estado (asignar "En Proceso" por defecto)
UPDATE Proyecto 
SET id_estado = (SELECT id_estado FROM Estado WHERE nombre_estado = 'En Proceso' LIMIT 1)
WHERE id_estado IS NULL;

-- Actualizar tareas existentes sin estado (asignar "Pendiente" por defecto)
UPDATE Tarea 
SET id_estado = (SELECT id_estado FROM Estado WHERE nombre_estado = 'Pendiente' LIMIT 1)
WHERE id_estado IS NULL;

-- Mostrar resumen
SELECT '=== TABLA ESTADO CREADA ===' as Resultado;
SELECT * FROM Estado ORDER BY id_estado;

SELECT '=== PROYECTOS CON ESTADO ===' as Resultado;
SELECT 
    COUNT(*) as total_proyectos,
    COUNT(id_estado) as con_estado,
    COUNT(*) - COUNT(id_estado) as sin_estado
FROM Proyecto;

SELECT '=== TAREAS CON ESTADO ===' as Resultado;
SELECT 
    COUNT(*) as total_tareas,
    COUNT(id_estado) as con_estado,
    COUNT(*) - COUNT(id_estado) as sin_estado
FROM Tarea;
