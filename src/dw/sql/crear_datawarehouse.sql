-- DATAWAREHOUSE consolidado (migrado de crear_datawarehouse_simple.sql)
USE dw_proyectos_hist;

CREATE TABLE IF NOT EXISTS DimTiempo (
	id_tiempo INT PRIMARY KEY,
	ano INT NOT NULL,
	mes INT NOT NULL,
	trimestre INT NOT NULL,
	nombre_mes VARCHAR(20) NOT NULL,
	INDEX idx_ano_mes (ano, mes)
);

CREATE TABLE IF NOT EXISTS DimCliente (
	id_cliente INT PRIMARY KEY,
	nombre_cliente VARCHAR(100) NOT NULL,
	sector VARCHAR(50),
	contacto VARCHAR(100),
	telefono VARCHAR(20),
	email VARCHAR(100),
	direccion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS DimEmpleado (
	id_empleado INT PRIMARY KEY,
	nombre_empleado VARCHAR(100) NOT NULL,
	puesto VARCHAR(50),
	departamento VARCHAR(50),
	salario_base DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS DimEquipo (
	id_equipo INT PRIMARY KEY,
	nombre_equipo VARCHAR(100) NOT NULL,
	descripcion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS DimProyecto (
	id_proyecto INT PRIMARY KEY,
	nombre_proyecto VARCHAR(150) NOT NULL,
	descripcion TEXT,
	id_cliente INT,
	id_gerente INT,
	prioridad VARCHAR(20),
	estado VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS HechoProyecto (
	id_hecho_proyecto INT AUTO_INCREMENT PRIMARY KEY,
	id_proyecto INT NOT NULL,
	id_cliente INT NOT NULL,
	id_empleado INT NOT NULL,
	id_tiempo INT NOT NULL,
	presupuesto DECIMAL(12,2) DEFAULT 0,
	costo_real DECIMAL(12,2) DEFAULT 0,
	progreso_porcentaje INT DEFAULT 0,
	fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	UNIQUE KEY uk_proyecto_tiempo (id_proyecto, id_tiempo)
);

CREATE TABLE IF NOT EXISTS HechoTarea (
	id_hecho_tarea INT AUTO_INCREMENT PRIMARY KEY,
	id_tarea INT NOT NULL,
	id_proyecto INT NOT NULL,
	id_empleado INT NOT NULL,
	id_tiempo INT NOT NULL,
	horas_planificadas INT DEFAULT 0,
	horas_reales INT DEFAULT 0,
	costo_planificado DECIMAL(10,2) DEFAULT 0,
	costo_real DECIMAL(10,2) DEFAULT 0,
	progreso_porcentaje INT DEFAULT 0,
	fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	UNIQUE KEY uk_tarea_tiempo (id_tarea, id_tiempo)
);

SELECT 'DataWarehouse básico listo' AS resultado;
