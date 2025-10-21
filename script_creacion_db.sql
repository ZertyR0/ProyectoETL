-- =========================================================
-- REINICIO LIMPIO
-- =========================================================
SET FOREIGN_KEY_CHECKS = 0;
DROP DATABASE IF EXISTS gestionproyectos_hist;
SET FOREIGN_KEY_CHECKS = 1;

CREATE DATABASE gestionproyectos_hist
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;
USE gestionproyectos_hist;

-- =========================================================
-- TABLAS MAESTRAS
-- =========================================================
CREATE TABLE Cliente (
  id_cliente      INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(100) NOT NULL,
  sector          VARCHAR(50),
  contacto        VARCHAR(100),
  telefono        VARCHAR(20),
  email           VARCHAR(100),
  UNIQUE KEY uq_cliente_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE Empleado (
  id_empleado     INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(100) NOT NULL,
  puesto          VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE Equipo (
  id_equipo       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_equipo   VARCHAR(100) NOT NULL,
  descripcion     VARCHAR(200),
  UNIQUE KEY uq_equipo_nombre (nombre_equipo)
) ENGINE=InnoDB;

CREATE TABLE Estado (
  id_estado       INT AUTO_INCREMENT PRIMARY KEY,
  nombre_estado   VARCHAR(50) NOT NULL,
  UNIQUE KEY uq_estado_nombre (nombre_estado)
) ENGINE=InnoDB;

-- =========================================================
-- PROYECTOS / TAREAS
-- =========================================================
CREATE TABLE Proyecto (
  id_proyecto         INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente          INT NOT NULL,
  nombre              VARCHAR(150) NOT NULL,
  descripcion         VARCHAR(100),
  fecha_inicio        DATE,
  fecha_fin_plan      DATE,
  fecha_fin_real      DATE,
  presupuesto         DECIMAL(12,2) DEFAULT 0,
  costo_real          DECIMAL(12,2) DEFAULT 0,
  id_estado           INT NOT NULL,
  id_empleado_gerente INT,
  KEY ix_proy_cliente (id_cliente),
  KEY ix_proy_estado  (id_estado),
  KEY ix_proy_gerente (id_empleado_gerente),
  CONSTRAINT fk_proy_cliente  FOREIGN KEY (id_cliente)          REFERENCES Cliente(id_cliente),
  CONSTRAINT fk_proy_estado   FOREIGN KEY (id_estado)           REFERENCES Estado(id_estado),
  CONSTRAINT fk_proy_gerente  FOREIGN KEY (id_empleado_gerente) REFERENCES Empleado(id_empleado)
) ENGINE=InnoDB;

CREATE TABLE Tarea (
  id_tarea          INT AUTO_INCREMENT PRIMARY KEY,
  id_proyecto       INT NOT NULL,
  nombre_tarea      VARCHAR(150) NOT NULL,
  fecha_inicio_plan DATE,
  fecha_fin_plan    DATE,
  fecha_fin_real    DATE,
  horas_plan        INT DEFAULT 0,
  horas_reales      INT DEFAULT 0,
  id_estado         INT NOT NULL,
  KEY ix_tarea_proy   (id_proyecto),
  KEY ix_tarea_estado (id_estado),
  CONSTRAINT fk_tarea_proyecto FOREIGN KEY (id_proyecto) REFERENCES Proyecto(id_proyecto),
  CONSTRAINT fk_tarea_estado   FOREIGN KEY (id_estado)   REFERENCES Estado(id_estado)
) ENGINE=InnoDB;

-- =========================================================
-- HISTÓRICOS DE EQUIPOS / ASIGNACIONES
-- =========================================================
CREATE TABLE MiembroEquipo (
  id_miembro     INT AUTO_INCREMENT PRIMARY KEY,
  id_equipo      INT NOT NULL,
  id_empleado    INT NOT NULL,
  fecha_inicio   DATE,
  fecha_hasta    DATE,
  rol_miembro    VARCHAR(50),
  KEY ix_me_equipo   (id_equipo),
  KEY ix_me_empleado (id_empleado),
  CONSTRAINT fk_me_equipo   FOREIGN KEY (id_equipo)   REFERENCES Equipo(id_equipo),
  CONSTRAINT fk_me_empleado FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado)
) ENGINE=InnoDB;

CREATE TABLE TareaEquipoHist (
  id_tarea_equipo  INT AUTO_INCREMENT PRIMARY KEY,
  id_tarea         INT NOT NULL,
  id_equipo        INT NOT NULL,
  fecha_asignacion DATE,
  fecha_liberacion DATE,
  KEY ix_teh_tarea  (id_tarea),
  KEY ix_teh_equipo (id_equipo),
  CONSTRAINT fk_teh_tarea  FOREIGN KEY (id_tarea)  REFERENCES Tarea(id_tarea),
  CONSTRAINT fk_teh_equipo FOREIGN KEY (id_equipo) REFERENCES Equipo(id_equipo)
) ENGINE=InnoDB;
