-- =========================================================
-- SCRIPT CORREGIDO PARA DATAWAREHOUSE
-- Sistema de Business Intelligence - Proyectos Históricos
-- =========================================================

-- Configuración inicial
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';

-- Eliminar y crear base de datos
DROP DATABASE IF EXISTS dw_proyectos_hist;
CREATE DATABASE dw_proyectos_hist
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE dw_proyectos_hist;

-- =========================================================
-- DIMENSIONES (SCD Tipo 1 - Actualización In-Place)
-- =========================================================

CREATE TABLE DimCliente (
  id_cliente        INT PRIMARY KEY,
  nombre            VARCHAR(100) NOT NULL,
  sector            VARCHAR(50),
  contacto          VARCHAR(100),
  telefono          VARCHAR(20),
  email             VARCHAR(100),
  direccion         VARCHAR(200),
  fecha_registro    DATE,
  activo            TINYINT(1) DEFAULT 1,
  fecha_carga       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_dim_cliente_sector (sector),
  INDEX idx_dim_cliente_activo (activo)
) ENGINE=InnoDB;

CREATE TABLE DimEmpleado (
  id_empleado       INT PRIMARY KEY,
  nombre            VARCHAR(100) NOT NULL,
  puesto            VARCHAR(50),
  departamento      VARCHAR(50),
  salario_base      DECIMAL(10,2),
  fecha_ingreso     DATE,
  activo            TINYINT(1) DEFAULT 1,
  fecha_carga       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_dim_empleado_puesto (puesto),
  INDEX idx_dim_empleado_depto (departamento),
  INDEX idx_dim_empleado_activo (activo)
) ENGINE=InnoDB;

CREATE TABLE DimEquipo (
  id_equipo         INT PRIMARY KEY,
  nombre_equipo     VARCHAR(100) NOT NULL,
  descripcion       VARCHAR(200),
  fecha_creacion    DATE,
  activo            TINYINT(1) DEFAULT 1,
  fecha_carga       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_dim_equipo_activo (activo)
) ENGINE=InnoDB;

CREATE TABLE DimProyecto (
  id_proyecto       INT PRIMARY KEY,
  nombre_proyecto   VARCHAR(150) NOT NULL,
  descripcion       TEXT,
  fecha_inicio_plan DATE,
  fecha_fin_plan    DATE,
  presupuesto_plan  DECIMAL(12,2) DEFAULT 0,
  prioridad         VARCHAR(20),
  fecha_carga       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_dim_proyecto_fechas (fecha_inicio_plan, fecha_fin_plan),
  INDEX idx_dim_proyecto_prioridad (prioridad)
) ENGINE=InnoDB;

CREATE TABLE DimTiempo (
  id_tiempo         INT AUTO_INCREMENT PRIMARY KEY,
  fecha             DATE NOT NULL UNIQUE,
  anio              INT,
  mes               INT,
  dia               INT,
  nombre_mes        VARCHAR(20),
  trimestre         INT,
  semestre          INT,
  dia_semana        INT,
  nombre_dia_semana VARCHAR(20),
  es_fin_semana     TINYINT(1) DEFAULT 0,
  es_feriado        TINYINT(1) DEFAULT 0,
  numero_semana     INT,
  
  INDEX idx_dim_tiempo_anio_mes (anio, mes),
  INDEX idx_dim_tiempo_trimestre (anio, trimestre),
  INDEX idx_dim_tiempo_semana (anio, numero_semana)
) ENGINE=InnoDB;

-- =========================================================
-- TABLA DE HECHOS - PROYECTOS
-- =========================================================

CREATE TABLE HechoProyecto (
  id_hecho_proyecto      BIGINT AUTO_INCREMENT PRIMARY KEY,
  
  -- Claves foráneas a dimensiones
  id_proyecto            INT NOT NULL,
  id_cliente             INT,
  id_empleado_gerente    INT,
  id_tiempo_inicio       INT,
  id_tiempo_fin_plan     INT,
  id_tiempo_fin_real     INT,
  
  -- Métricas de tiempo
  duracion_planificada   INT DEFAULT 0,     -- días
  duracion_real          INT DEFAULT 0,     -- días
  variacion_cronograma   INT DEFAULT 0,     -- días (real - plan)
  cumplimiento_tiempo    TINYINT(1) DEFAULT 0,
  dias_retraso           INT DEFAULT 0,
  
  -- Métricas financieras
  presupuesto            DECIMAL(12,2) DEFAULT 0,
  costo_real             DECIMAL(12,2) DEFAULT 0,
  variacion_costos       DECIMAL(12,2) DEFAULT 0,  -- costo_real - presupuesto
  cumplimiento_presupuesto TINYINT(1) DEFAULT 0,
  porcentaje_sobrecosto  DECIMAL(5,2) DEFAULT 0,
  
  -- Métricas de trabajo
  tareas_total           INT DEFAULT 0,
  tareas_completadas     INT DEFAULT 0,
  tareas_canceladas      INT DEFAULT 0,
  tareas_pendientes      INT DEFAULT 0,
  porcentaje_completado  DECIMAL(5,2) DEFAULT 0,
  
  -- Métricas de recursos
  horas_estimadas_total  INT DEFAULT 0,
  horas_reales_total     INT DEFAULT 0,
  variacion_horas        INT DEFAULT 0,     -- reales - plan
  eficiencia_horas       DECIMAL(5,2) DEFAULT 0,
  
  -- Métricas de equipos
  equipos_asignados      INT DEFAULT 0,
  cambios_equipo_proy    INT DEFAULT 0,
  
  -- Métricas de calidad
  retrabajos             INT DEFAULT 0,
  errores_detectados     INT DEFAULT 0,
  satisfaccion_cliente   DECIMAL(3,1) DEFAULT 0, -- 1-10
  
  -- Metadatos
  fecha_carga            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Índices para optimización de consultas
  INDEX idx_hp_proyecto (id_proyecto),
  INDEX idx_hp_cliente (id_cliente),
  INDEX idx_hp_gerente (id_empleado_gerente),
  INDEX idx_hp_tiempo_inicio (id_tiempo_inicio),
  INDEX idx_hp_tiempo_fin (id_tiempo_fin_real),
  INDEX idx_hp_cumplimiento (cumplimiento_tiempo, cumplimiento_presupuesto),
  INDEX idx_hp_fechas (id_tiempo_inicio, id_tiempo_fin_real)
) ENGINE=InnoDB;

-- =========================================================
-- TABLA DE HECHOS - TAREAS
-- =========================================================

CREATE TABLE HechoTarea (
  id_hecho_tarea     BIGINT AUTO_INCREMENT PRIMARY KEY,
  
  -- Claves foráneas a dimensiones
  id_tarea           INT NOT NULL,
  id_proyecto        INT NOT NULL,
  id_empleado        INT,
  id_equipo          INT,
  id_tiempo_inicio_plan   INT,
  id_tiempo_fin_plan      INT,
  id_tiempo_inicio_real   INT,
  id_tiempo_fin_real      INT,
  
  -- Métricas de tiempo
  duracion_planificada    INT DEFAULT 0,     -- días
  duracion_real           INT DEFAULT 0,     -- días
  variacion_cronograma    INT DEFAULT 0,     -- días
  cumplimiento_tiempo     TINYINT(1) DEFAULT 0,
  dias_retraso            INT DEFAULT 0,
  
  -- Métricas de trabajo
  horas_plan              INT DEFAULT 0,
  horas_reales            INT DEFAULT 0,
  variacion_horas         INT DEFAULT 0,
  eficiencia_horas        DECIMAL(5,2) DEFAULT 0,
  
  -- Métricas financieras
  costo_estimado          DECIMAL(10,2) DEFAULT 0,
  costo_real_tarea        DECIMAL(10,2) DEFAULT 0,
  variacion_costo         DECIMAL(10,2) DEFAULT 0,
  
  -- Métricas de calidad
  retrabajos_tarea        INT DEFAULT 0,
  errores_tarea           INT DEFAULT 0,
  cambios_alcance         INT DEFAULT 0,
  
  -- Estado y progreso
  porcentaje_completado   DECIMAL(5,2) DEFAULT 0,
  complejidad_estimada    INT DEFAULT 1, -- 1-5
  complejidad_real        INT DEFAULT 1, -- 1-5
  
  -- Metadatos
  fecha_carga             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Índices para optimización
  INDEX idx_ht_tarea (id_tarea),
  INDEX idx_ht_proyecto (id_proyecto),
  INDEX idx_ht_empleado (id_empleado),
  INDEX idx_ht_equipo (id_equipo),
  INDEX idx_ht_tiempo_plan (id_tiempo_fin_plan),
  INDEX idx_ht_tiempo_real (id_tiempo_fin_real),
  INDEX idx_ht_cumplimiento (cumplimiento_tiempo),
  INDEX idx_ht_eficiencia (eficiencia_horas)
) ENGINE=InnoDB;

-- =========================================================
-- FOREIGN KEYS OPCIONALES (Para integridad referencial)
-- =========================================================

/*
-- Comentado por defecto para mayor flexibilidad en ETL
-- Descomentar si se requiere integridad referencial estricta

ALTER TABLE HechoProyecto
  ADD CONSTRAINT fk_hp_proyecto  FOREIGN KEY (id_proyecto)         REFERENCES DimProyecto(id_proyecto) ON DELETE CASCADE,
  ADD CONSTRAINT fk_hp_cliente   FOREIGN KEY (id_cliente)          REFERENCES DimCliente(id_cliente) ON DELETE SET NULL,
  ADD CONSTRAINT fk_hp_gerente   FOREIGN KEY (id_empleado_gerente) REFERENCES DimEmpleado(id_empleado) ON DELETE SET NULL,
  ADD CONSTRAINT fk_hp_tiempo_inicio FOREIGN KEY (id_tiempo_inicio) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_hp_tiempo_fin_plan FOREIGN KEY (id_tiempo_fin_plan) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_hp_tiempo_fin_real FOREIGN KEY (id_tiempo_fin_real) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL;

ALTER TABLE HechoTarea
  ADD CONSTRAINT fk_ht_proyecto  FOREIGN KEY (id_proyecto)         REFERENCES DimProyecto(id_proyecto) ON DELETE CASCADE,
  ADD CONSTRAINT fk_ht_empleado  FOREIGN KEY (id_empleado)         REFERENCES DimEmpleado(id_empleado) ON DELETE SET NULL,
  ADD CONSTRAINT fk_ht_equipo    FOREIGN KEY (id_equipo)           REFERENCES DimEquipo(id_equipo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_ht_tiempo_inicio_plan FOREIGN KEY (id_tiempo_inicio_plan) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_ht_tiempo_fin_plan FOREIGN KEY (id_tiempo_fin_plan) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_ht_tiempo_inicio_real FOREIGN KEY (id_tiempo_inicio_real) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL,
  ADD CONSTRAINT fk_ht_tiempo_fin_real FOREIGN KEY (id_tiempo_fin_real) REFERENCES DimTiempo(id_tiempo) ON DELETE SET NULL;
*/

-- =========================================================
-- VISTAS PARA ANÁLISIS COMÚN
-- =========================================================

-- Vista resumen de proyectos
CREATE VIEW v_resumen_proyectos AS
SELECT 
    p.id_proyecto,
    dp.nombre_proyecto,
    dc.nombre as cliente,
    de.nombre as gerente,
    hp.presupuesto,
    hp.costo_real,
    hp.variacion_costos,
    hp.duracion_planificada,
    hp.duracion_real,
    hp.variacion_cronograma,
    hp.cumplimiento_tiempo,
    hp.cumplimiento_presupuesto,
    hp.porcentaje_completado,
    CASE 
        WHEN hp.cumplimiento_tiempo = 1 AND hp.cumplimiento_presupuesto = 1 THEN 'Exitoso'
        WHEN hp.cumplimiento_tiempo = 0 OR hp.cumplimiento_presupuesto = 0 THEN 'Con Problemas'
        ELSE 'En Progreso'
    END as estado_proyecto
FROM HechoProyecto hp
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado;

-- Vista métricas por tiempo
CREATE VIEW v_metricas_por_mes AS
SELECT 
    dt.anio,
    dt.mes,
    dt.nombre_mes,
    COUNT(*) as proyectos_finalizados,
    AVG(hp.duracion_real) as duracion_promedio,
    AVG(hp.variacion_costos) as variacion_costos_promedio,
    SUM(hp.cumplimiento_tiempo) as proyectos_a_tiempo,
    SUM(hp.cumplimiento_presupuesto) as proyectos_en_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
WHERE dt.fecha IS NOT NULL
GROUP BY dt.anio, dt.mes, dt.nombre_mes
ORDER BY dt.anio, dt.mes;

-- Restaurar configuración
SET FOREIGN_KEY_CHECKS = 1;

-- Verificar creación
SELECT 'Datawarehouse dw_proyectos_hist creado exitosamente' as resultado;
SHOW TABLES;
