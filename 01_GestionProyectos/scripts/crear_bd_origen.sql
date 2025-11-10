-- =========================================================
-- SISTEMA DE GESTIÓN DE PROYECTOS - BASE DE DATOS ORIGEN
-- Script de creación optimizado y corregido
-- =========================================================

-- Configuración inicial
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- Eliminar y crear base de datos
DROP DATABASE IF EXISTS gestionproyectos_hist;
CREATE DATABASE gestionproyectos_hist
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE gestionproyectos_hist;

-- =========================================================
-- TABLAS MAESTRAS
-- =========================================================

CREATE TABLE Estado (
  id_estado       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_estado   VARCHAR(50) NOT NULL,
  descripcion     VARCHAR(100),
  activo          TINYINT(1) DEFAULT 1,
  UNIQUE KEY uq_estado_nombre (nombre_estado)
) ENGINE=InnoDB COMMENT='Estados para proyectos y tareas';

CREATE TABLE Cliente (
  id_cliente      INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(100) NOT NULL,
  sector          VARCHAR(50),
  contacto        VARCHAR(100),
  telefono        VARCHAR(20),
  email           VARCHAR(100),
  direccion       VARCHAR(200),
  fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  activo          TINYINT(1) DEFAULT 1,
  UNIQUE KEY uq_cliente_nombre (nombre),
  INDEX idx_cliente_sector (sector),
  INDEX idx_cliente_activo (activo)
) ENGINE=InnoDB COMMENT='Información de clientes';

CREATE TABLE Empleado (
  id_empleado     INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(100) NOT NULL,
  puesto          VARCHAR(50),
  departamento    VARCHAR(50),
  salario_base    DECIMAL(10,2),
  fecha_ingreso   DATE,
  activo          TINYINT(1) DEFAULT 1,
  INDEX idx_empleado_puesto (puesto),
  INDEX idx_empleado_depto (departamento),
  INDEX idx_empleado_activo (activo)
) ENGINE=InnoDB COMMENT='Información de empleados';

CREATE TABLE Equipo (
  id_equipo       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_equipo   VARCHAR(100) NOT NULL,
  descripcion     VARCHAR(200),
  fecha_creacion  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  activo          TINYINT(1) DEFAULT 1,
  UNIQUE KEY uq_equipo_nombre (nombre_equipo),
  INDEX idx_equipo_activo (activo)
) ENGINE=InnoDB COMMENT='Equipos de trabajo';

-- =========================================================
-- TABLAS PRINCIPALES
-- =========================================================

CREATE TABLE Proyecto (
  id_proyecto         INT AUTO_INCREMENT PRIMARY KEY,
  nombre              VARCHAR(150) NOT NULL,
  descripcion         TEXT,
  fecha_inicio        DATE,
  fecha_fin_plan      DATE,
  fecha_fin_real      DATE,
  presupuesto         DECIMAL(12,2) DEFAULT 0,
  costo_real          DECIMAL(12,2) DEFAULT 0,
  id_cliente          INT,
  id_estado           INT,
  id_empleado_gerente INT,
  prioridad           ENUM('Baja', 'Media', 'Alta', 'Crítica') DEFAULT 'Media',
  progreso_porcentaje INT DEFAULT 0,
  fecha_creacion      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_proyecto_cliente (id_cliente),
  INDEX idx_proyecto_estado (id_estado),
  INDEX idx_proyecto_gerente (id_empleado_gerente),
  INDEX idx_proyecto_fechas (fecha_inicio, fecha_fin_plan),
  INDEX idx_proyecto_prioridad (prioridad)
) ENGINE=InnoDB COMMENT='Proyectos principales';

CREATE TABLE Tarea (
  id_tarea          INT AUTO_INCREMENT PRIMARY KEY,
  nombre_tarea      VARCHAR(150) NOT NULL,
  descripcion       TEXT,
  fecha_inicio_plan DATE,
  fecha_fin_plan    DATE,
  fecha_inicio_real DATE,
  fecha_fin_real    DATE,
  horas_plan        INT DEFAULT 0,
  horas_reales      INT DEFAULT 0,
  id_proyecto       INT,
  id_empleado       INT,
  id_estado         INT,
  prioridad         ENUM('Baja', 'Media', 'Alta', 'Crítica') DEFAULT 'Media',
  progreso_porcentaje INT DEFAULT 0,
  costo_estimado    DECIMAL(10,2) DEFAULT 0,
  costo_real        DECIMAL(10,2) DEFAULT 0,
  fecha_creacion    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_tarea_proyecto (id_proyecto),
  INDEX idx_tarea_empleado (id_empleado),
  INDEX idx_tarea_estado (id_estado),
  INDEX idx_tarea_fechas (fecha_inicio_plan, fecha_fin_plan)
) ENGINE=InnoDB COMMENT='Tareas de proyectos';

-- =========================================================
-- TABLA DE AUDITORÍA ETL
-- =========================================================

CREATE TABLE AuditoriaETL (
  id_auditoria        INT AUTO_INCREMENT PRIMARY KEY,
  fecha_hora          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  operacion           VARCHAR(50),
  tabla               VARCHAR(50),
  registros_procesados INT DEFAULT 0,
  estado              VARCHAR(20),
  mensaje             TEXT,
  usuario_etl         VARCHAR(100),
  
  INDEX idx_fecha (fecha_hora),
  INDEX idx_operacion (operacion),
  INDEX idx_estado (estado)
) ENGINE=InnoDB COMMENT='Auditoría de procesos ETL';

-- =========================================================
-- TABLAS DE RELACIÓN
-- =========================================================

CREATE TABLE MiembroEquipo (
  id_miembro     INT AUTO_INCREMENT PRIMARY KEY,
  id_equipo      INT,
  id_empleado    INT,
  fecha_inicio   DATE,
  fecha_fin      DATE,
  rol_miembro    VARCHAR(50),
  activo         TINYINT(1) DEFAULT 1,
  
  INDEX idx_miembro_equipo (id_equipo),
  INDEX idx_miembro_empleado (id_empleado),
  INDEX idx_miembro_activo (activo)
) ENGINE=InnoDB COMMENT='Miembros de equipos';

CREATE TABLE TareaEquipoHist (
  id_tarea_equipo  INT AUTO_INCREMENT PRIMARY KEY,
  id_tarea         INT,
  id_equipo        INT,
  fecha_asignacion DATE,
  fecha_liberacion DATE,
  horas_asignadas  INT DEFAULT 0,
  notas           TEXT,
  
  INDEX idx_teh_tarea (id_tarea),
  INDEX idx_teh_equipo (id_equipo),
  INDEX idx_teh_fechas (fecha_asignacion, fecha_liberacion)
) ENGINE=InnoDB COMMENT='Historial de asignaciones tarea-equipo';

-- =========================================================
-- DATOS INICIALES
-- =========================================================

INSERT INTO Estado (nombre_estado, descripcion) VALUES 
('Pendiente', 'Proyecto o tarea pendiente de iniciar'),
('En Progreso', 'Proyecto o tarea en desarrollo'),
('Completado', 'Proyecto o tarea finalizada exitosamente'),
('Cancelado', 'Proyecto o tarea cancelada');

-- =========================================================
-- FOREIGN KEYS (OPCIONAL - Comentado para flexibilidad ETL)
-- =========================================================

/*
-- Descomentar si se requiere integridad referencial estricta
ALTER TABLE Proyecto 
  ADD CONSTRAINT fk_proy_cliente  FOREIGN KEY (id_cliente)          REFERENCES Cliente(id_cliente) ON DELETE SET NULL,
  ADD CONSTRAINT fk_proy_estado   FOREIGN KEY (id_estado)           REFERENCES Estado(id_estado) ON DELETE SET NULL,
  ADD CONSTRAINT fk_proy_gerente  FOREIGN KEY (id_empleado_gerente) REFERENCES Empleado(id_empleado) ON DELETE SET NULL;

ALTER TABLE Tarea 
  ADD CONSTRAINT fk_tarea_proyecto FOREIGN KEY (id_proyecto) REFERENCES Proyecto(id_proyecto) ON DELETE CASCADE,
  ADD CONSTRAINT fk_tarea_empleado FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) ON DELETE SET NULL,
  ADD CONSTRAINT fk_tarea_estado   FOREIGN KEY (id_estado)   REFERENCES Estado(id_estado) ON DELETE SET NULL;

ALTER TABLE MiembroEquipo 
  ADD CONSTRAINT fk_me_equipo   FOREIGN KEY (id_equipo)   REFERENCES Equipo(id_equipo) ON DELETE CASCADE,
  ADD CONSTRAINT fk_me_empleado FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) ON DELETE CASCADE;

ALTER TABLE TareaEquipoHist 
  ADD CONSTRAINT fk_teh_tarea  FOREIGN KEY (id_tarea)  REFERENCES Tarea(id_tarea) ON DELETE CASCADE,
  ADD CONSTRAINT fk_teh_equipo FOREIGN KEY (id_equipo) REFERENCES Equipo(id_equipo) ON DELETE CASCADE;
*/

-- Restaurar configuración
SET FOREIGN_KEY_CHECKS = 1;

-- Verificación final
SELECT 'Base de datos gestionproyectos_hist creada exitosamente' as resultado;
SHOW TABLES;
