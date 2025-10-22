-- =========================================================
-- REINICIO LIMPIO
-- =========================================================
SET FOREIGN_KEY_CHECKS = 0;
DROP DATABASE IF EXISTS dw_proyectos_hist;
SET FOREIGN_KEY_CHECKS = 1;

CREATE DATABASE dw_proyectos_hist
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
USE dw_proyectos_hist;

-- =========================================================
-- DIMENSIONES
-- (Se asume integración directa 1:1 con claves naturales del OLTP
--  para Cliente/Empleado/Equipo/Proyecto, y surrogate key en DimTiempo)
-- =========================================================
CREATE TABLE DimCliente (
  id_cliente   INT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  sector       VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE DimEmpleado (
  id_empleado  INT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  puesto       VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE DimEquipo (
  id_equipo      INT PRIMARY KEY,
  nombre_equipo  VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE DimProyecto (
  id_proyecto       INT PRIMARY KEY,
  nombre_proyecto   VARCHAR(150) NOT NULL,
  fecha_inicio_plan DATE,
  fecha_fin_plan    DATE,
  costo_plan        DECIMAL(12,2) DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE DimTiempo (
  id_tiempo     INT AUTO_INCREMENT PRIMARY KEY,
  fecha         DATE NOT NULL UNIQUE,
  anio          INT,
  mes           INT,
  nombre_mes    VARCHAR(20),
  trimestre     INT,
  dia_semana    VARCHAR(20),
  es_fin_semana TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;

-- =========================================================
-- HECHOS
-- =========================================================
CREATE TABLE HechoProyecto (
  id_hecho_proyecto      BIGINT AUTO_INCREMENT PRIMARY KEY,
  -- FKs a dimensiones
  id_proyecto            INT NOT NULL,
  id_cliente             INT NOT NULL,
  id_empleado_gerente    INT,
  id_tiempo_fin_real     INT,
  -- Métricas
  presupuesto            DECIMAL(12,2) DEFAULT 0,
  duracion_planificada   INT DEFAULT 0,     -- días
  duracion_real          INT DEFAULT 0,     -- días
  variacion_cronograma   INT DEFAULT 0,     -- días (real - plan)
  cumplimiento_tiempo    TINYINT(1) DEFAULT 0,
  tareas_total           INT DEFAULT 0,
  tareas_completadas     INT DEFAULT 0,
  horas_estimadas_total  INT DEFAULT 0,
  horas_reales_total     INT DEFAULT 0,
  variacion_horas        INT DEFAULT 0,     -- reales - plan
  cambios_equipo_proyecto VARCHAR(100),
  costo_real             DECIMAL(12,2) DEFAULT 0,
  variacion_costos       DECIMAL(12,2) DEFAULT 0,  -- costo_real - presupuesto
  cumplimiento_presupuesto TINYINT(1) DEFAULT 0,
  -- Índices y FKs
  KEY ix_hp_proyecto (id_proyecto),
  KEY ix_hp_cliente  (id_cliente),
  KEY ix_hp_gerente  (id_empleado_gerente),
  KEY ix_hp_tiempo   (id_tiempo_fin_real),
  CONSTRAINT fk_hp_proyecto  FOREIGN KEY (id_proyecto)         REFERENCES DimProyecto(id_proyecto),
  CONSTRAINT fk_hp_cliente   FOREIGN KEY (id_cliente)          REFERENCES DimCliente(id_cliente),
  CONSTRAINT fk_hp_gerente   FOREIGN KEY (id_empleado_gerente) REFERENCES DimEmpleado(id_empleado),
  CONSTRAINT fk_hp_tiempo    FOREIGN KEY (id_tiempo_fin_real)  REFERENCES DimTiempo(id_tiempo)
) ENGINE=InnoDB;

CREATE TABLE HechoTarea (
  id_hecho_tarea     BIGINT AUTO_INCREMENT PRIMARY KEY,
  -- FKs a dimensiones
  id_tarea           INT NOT NULL,
  id_proyecto        INT NOT NULL,
  id_empleado        INT,
  id_tiempo_fin_real INT,
  -- Métricas
  horas_plan         INT DEFAULT 0,
  horas_reales       INT DEFAULT 0,
  variacion_horas    INT DEFAULT 0,
  costo_real_tarea   DECIMAL(12,2) DEFAULT 0,
  cumplimiento_tiempo TINYINT(1) DEFAULT 0,
  -- Índices y FKs
  KEY ix_ht_proy   (id_proyecto),
  KEY ix_ht_emp    (id_empleado),
  KEY ix_ht_tiempo (id_tiempo_fin_real),
  CONSTRAINT fk_ht_proyecto  FOREIGN KEY (id_proyecto)        REFERENCES DimProyecto(id_proyecto),
  CONSTRAINT fk_ht_empleado  FOREIGN KEY (id_empleado)        REFERENCES DimEmpleado(id_empleado),
  CONSTRAINT fk_ht_tiempo    FOREIGN KEY (id_tiempo_fin_real) REFERENCES DimTiempo(id_tiempo)
) ENGINE=InnoDB;
