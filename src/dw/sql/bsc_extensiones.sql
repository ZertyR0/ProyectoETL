-- Balanced Scorecard extensiones
-- Migrado desde lógica en etl_local_simple.py
-- Tablas y datos de ejemplo para objetivos y key results

USE dw_proyectos_hist;

CREATE TABLE IF NOT EXISTS DimObjetivo (
    id_objetivo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_objetivo VARCHAR(150) NOT NULL,
    perspectiva_bsc ENUM('Financiera','Cliente','Procesos','Aprendizaje') NOT NULL,
    valor_actual DECIMAL(10,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS DimKR (
    id_kr INT AUTO_INCREMENT PRIMARY KEY,
    id_objetivo INT NOT NULL,
    nombre_kr VARCHAR(150) NOT NULL,
    valor_actual DECIMAL(10,2) DEFAULT 0,
    valor_meta DECIMAL(10,2) DEFAULT 100,
    estado VARCHAR(30) DEFAULT 'En Progreso',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dimkr_objetivo FOREIGN KEY (id_objetivo) REFERENCES DimObjetivo(id_objetivo)
) ENGINE=InnoDB;

-- Datos de ejemplo (idempotente)
INSERT INTO DimObjetivo (nombre_objetivo, perspectiva_bsc, valor_actual, estado)
VALUES
('Aumentar ingresos por ventas','Financiera',85.0,'Activo'),
('Mejorar satisfacción cliente','Cliente',78.0,'Activo'),
('Optimizar procesos internos','Procesos',92.0,'Activo'),
('Capacitar personal técnico','Aprendizaje',70.0,'Activo')
ON DUPLICATE KEY UPDATE valor_actual=VALUES(valor_actual);

INSERT INTO DimKR (id_objetivo, nombre_kr, valor_actual, valor_meta, estado)
SELECT o.id_objetivo,
       CASE o.nombre_objetivo
            WHEN 'Aumentar ingresos por ventas' THEN 'Incremento ventas 15%'
            WHEN 'Mejorar satisfacción cliente' THEN 'NPS > 80'
            WHEN 'Optimizar procesos internos' THEN 'Reducir tiempo proceso 20%'
            WHEN 'Capacitar personal técnico' THEN 'Certificar 50 empleados'
       END AS nombre_kr,
       CASE o.nombre_objetivo
            WHEN 'Aumentar ingresos por ventas' THEN 85.0
            WHEN 'Mejorar satisfacción cliente' THEN 78.0
            WHEN 'Optimizar procesos internos' THEN 92.0
            WHEN 'Capacitar personal técnico' THEN 35.0
       END AS valor_actual,
       CASE o.nombre_objetivo
            WHEN 'Capacitar personal técnico' THEN 50.0 ELSE 100.0 END AS valor_meta,
       CASE o.nombre_objetivo
            WHEN 'Optimizar procesos internos' THEN 'Completado'
            ELSE 'En Progreso'
       END AS estado
FROM DimObjetivo o
LEFT JOIN DimKR k ON k.id_objetivo = o.id_objetivo
WHERE k.id_objetivo IS NULL;

SELECT 'Extensiones BSC listas' AS resultado;