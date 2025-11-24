-- ============================================================
-- DATAWAREHOUSE SIMPLE PARA SISTEMA DSS LOCAL
-- ============================================================

USE datawarehouse;

-- Dimensión Tiempo
CREATE TABLE IF NOT EXISTS DimTiempo (
    id_tiempo INT PRIMARY KEY,
    ano INT NOT NULL,
    mes INT NOT NULL,
    trimestre INT NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    INDEX idx_ano_mes (ano, mes)
);

-- Dimensión Cliente
CREATE TABLE IF NOT EXISTS DimCliente (
    id_cliente INT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion VARCHAR(200)
);

-- Dimensión Empleado
CREATE TABLE IF NOT EXISTS DimEmpleado (
    id_empleado INT PRIMARY KEY,
    nombre_empleado VARCHAR(100) NOT NULL,
    puesto VARCHAR(50),
    departamento VARCHAR(50),
    salario_base DECIMAL(10,2)
);

-- Dimensión Equipo
CREATE TABLE IF NOT EXISTS DimEquipo (
    id_equipo INT PRIMARY KEY,
    nombre_equipo VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200)
);

-- Dimensión Proyecto
CREATE TABLE IF NOT EXISTS DimProyecto (
    id_proyecto INT PRIMARY KEY,
    nombre_proyecto VARCHAR(150) NOT NULL,
    descripcion TEXT,
    id_cliente INT,
    id_gerente INT,
    prioridad VARCHAR(20),
    estado VARCHAR(50),
    FOREIGN KEY (id_cliente) REFERENCES DimCliente(id_cliente),
    FOREIGN KEY (id_gerente) REFERENCES DimEmpleado(id_empleado)
);

-- Tabla de Hechos - Proyecto
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
    FOREIGN KEY (id_proyecto) REFERENCES DimProyecto(id_proyecto),
    FOREIGN KEY (id_cliente) REFERENCES DimCliente(id_cliente),
    FOREIGN KEY (id_empleado) REFERENCES DimEmpleado(id_empleado),
    FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo),
    UNIQUE KEY uk_proyecto_tiempo (id_proyecto, id_tiempo)
);

-- Tabla de Hechos - Tarea
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
    FOREIGN KEY (id_proyecto) REFERENCES DimProyecto(id_proyecto),
    FOREIGN KEY (id_empleado) REFERENCES DimEmpleado(id_empleado),
    FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo),
    UNIQUE KEY uk_tarea_tiempo (id_tarea, id_tiempo)
);

-- ============================================================
-- MÓDULO BSC/OKR
-- ============================================================

-- Dimensión Objetivo BSC
CREATE TABLE IF NOT EXISTS DimObjetivo (
    id_objetivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_objetivo VARCHAR(200) NOT NULL,
    perspectiva_bsc ENUM('Financiera', 'Cliente', 'Procesos', 'Aprendizaje') NOT NULL,
    vision_estrategica TEXT,
    valor_actual DECIMAL(10,2) DEFAULT 0,
    valor_meta DECIMAL(10,2) DEFAULT 100,
    unidad_medida VARCHAR(50) DEFAULT '%',
    estado ENUM('Activo', 'Pausado', 'Completado') DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_perspectiva (perspectiva_bsc),
    INDEX idx_estado (estado)
);

-- Dimensión Key Results (KR)
CREATE TABLE IF NOT EXISTS DimKR (
    id_kr INT AUTO_INCREMENT PRIMARY KEY,
    id_objetivo INT NOT NULL,
    nombre_kr VARCHAR(200) NOT NULL,
    descripcion TEXT,
    valor_actual DECIMAL(10,2) DEFAULT 0,
    valor_meta DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(50) DEFAULT '%',
    estado ENUM('Pendiente', 'En Progreso', 'Completado', 'Atrasado') DEFAULT 'Pendiente',
    fecha_inicio DATE,
    fecha_meta DATE,
    fecha_completado DATE,
    FOREIGN KEY (id_objetivo) REFERENCES DimObjetivo(id_objetivo) ON DELETE CASCADE,
    INDEX idx_objetivo (id_objetivo),
    INDEX idx_estado (estado)
);

-- Tabla de Hechos OKR
CREATE TABLE IF NOT EXISTS HechoOKR (
    id_hecho_okr INT AUTO_INCREMENT PRIMARY KEY,
    id_objetivo INT NOT NULL,
    id_kr INT NOT NULL,
    id_tiempo INT NOT NULL,
    valor_medido DECIMAL(10,2) NOT NULL,
    porcentaje_logro DECIMAL(5,2) NOT NULL,
    estado_periodo ENUM('Planificado', 'En Ejecución', 'Completado') DEFAULT 'En Ejecución',
    comentarios TEXT,
    fecha_medicion DATE NOT NULL,
    FOREIGN KEY (id_objetivo) REFERENCES DimObjetivo(id_objetivo),
    FOREIGN KEY (id_kr) REFERENCES DimKR(id_kr),
    FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo),
    UNIQUE KEY uk_okr_tiempo (id_kr, id_tiempo)
);

-- ============================================================
-- VISTAS DE ANALÍTICA
-- ============================================================

-- Vista resumen de proyectos
CREATE OR REPLACE VIEW v_resumen_proyectos AS
SELECT 
    dp.nombre_proyecto,
    dc.nombre_cliente,
    de.nombre_empleado as gerente,
    dp.prioridad,
    dp.estado,
    hp.presupuesto,
    hp.costo_real,
    hp.progreso_porcentaje,
    dt.ano,
    dt.mes,
    dt.nombre_mes
FROM HechoProyecto hp
JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
JOIN DimEmpleado de ON hp.id_empleado = de.id_empleado
JOIN DimTiempo dt ON hp.id_tiempo = dt.id_tiempo;

-- Vista métricas por mes
CREATE OR REPLACE VIEW v_metricas_por_mes AS
SELECT 
    dt.ano,
    dt.mes,
    dt.nombre_mes,
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_total,
    AVG(hp.progreso_porcentaje) as progreso_promedio,
    COUNT(DISTINCT ht.id_tarea) as total_tareas,
    SUM(ht.horas_planificadas) as horas_planificadas,
    SUM(ht.horas_reales) as horas_reales
FROM DimTiempo dt
LEFT JOIN HechoProyecto hp ON dt.id_tiempo = hp.id_tiempo
LEFT JOIN HechoTarea ht ON dt.id_tiempo = ht.id_tiempo
GROUP BY dt.ano, dt.mes, dt.nombre_mes
ORDER BY dt.ano, dt.mes;

SELECT ' Datawarehouse creado exitosamente' as resultado;
SELECT 'Tablas principales creadas:' as info;
SHOW TABLES;