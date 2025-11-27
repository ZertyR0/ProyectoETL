-- ========================================
-- BALANCED SCORECARD (BSC) CON OKR
-- Sistema de Soporte de Decisiones (DSS)
-- ========================================
--
-- Implementación de Balanced Scorecard con metodología OKR
-- (Objectives and Key Results) para seguimiento estratégico
--

USE dw_proyectos_hist;

-- ========================================
-- 1. DIMENSIÓN: OBJETIVOS ESTRATÉGICOS
-- ========================================

CREATE TABLE IF NOT EXISTS DimObjetivo (
    id_objetivo INT AUTO_INCREMENT PRIMARY KEY,
    codigo_objetivo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- BSC: 4 Perspectivas del Balanced Scorecard
    perspectiva ENUM(
        'Financiera', 
        'Clientes', 
        'Procesos Internos', 
        'Aprendizaje y Innovación'
    ) NOT NULL,
    
    -- Jerarquía y ownership
    objetivo_padre_id INT DEFAULT NULL,
    owner_responsable VARCHAR(100),
    equipo_responsable VARCHAR(100),
    
    -- Vinculación con visión estratégica
    vision_componente ENUM(
        'Transformación Digital',
        'Confiabilidad y Calidad',
        'Analítica Avanzada',
        'Automatización de Procesos',
        'Excelencia Operacional'
    ),
    
    -- Metadatos
    fecha_creacion DATE NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    peso_ponderacion DECIMAL(5,2) DEFAULT 1.0, -- Para cálculo de avance global
    activo BOOLEAN DEFAULT TRUE,
    
    -- Índices
    INDEX idx_perspectiva (perspectiva),
    INDEX idx_vision_componente (vision_componente),
    INDEX idx_activo (activo),
    
    -- Constraint de jerarquía
    FOREIGN KEY (objetivo_padre_id) REFERENCES DimObjetivo(id_objetivo)
);

-- ========================================
-- 2. DIMENSIÓN: KEY RESULTS (KR)
-- ========================================

CREATE TABLE IF NOT EXISTS DimKR (
    id_kr INT AUTO_INCREMENT PRIMARY KEY,
    id_objetivo INT NOT NULL,
    codigo_kr VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- Configuración de métrica
    formula_calculo TEXT, -- SQL o descripción del cálculo
    unidad_medida VARCHAR(50), -- '%', 'USD', 'días', 'horas', etc.
    tipo_metrica ENUM(
        'Incrementar', 'Decrementar', 'Mantener', 'Binario'
    ) DEFAULT 'Incrementar',
    
    -- Umbrales para semáforo (verde/amarillo/rojo)
    valor_inicial DECIMAL(15,2) DEFAULT 0,
    meta_objetivo DECIMAL(15,2) NOT NULL,
    umbral_verde DECIMAL(15,2), -- >= verde
    umbral_amarillo DECIMAL(15,2), -- >= amarillo, < verde
    -- < amarillo = rojo
    
    -- Configuración temporal
    frecuencia_medicion ENUM(
        'Semanal', 'Quincenal', 'Mensual', 'Trimestral'
    ) DEFAULT 'Mensual',
    
    -- Fuente de datos
    fuente_automatica BOOLEAN DEFAULT FALSE,
    query_automatica TEXT, -- Query para obtener valor automáticamente
    tabla_origen VARCHAR(100),
    
    -- Metadatos
    fecha_creacion DATE NOT NULL,
    peso_kr DECIMAL(5,2) DEFAULT 1.0, -- Peso dentro del objetivo
    activo BOOLEAN DEFAULT TRUE,
    
    -- Índices
    INDEX idx_objetivo (id_objetivo),
    INDEX idx_tipo_metrica (tipo_metrica),
    INDEX idx_activo (activo),
    
    -- Constraints
    FOREIGN KEY (id_objetivo) REFERENCES DimObjetivo(id_objetivo) ON DELETE CASCADE
);

-- ========================================
-- 3. TABLA DE HECHOS: MEDICIONES OKR
-- ========================================

CREATE TABLE IF NOT EXISTS HechoOKR (
    id_medicion INT AUTO_INCREMENT PRIMARY KEY,
    id_kr INT NOT NULL,
    id_tiempo INT NOT NULL,
    
    -- Valor medido
    valor_observado DECIMAL(15,2) NOT NULL,
    valor_anterior DECIMAL(15,2), -- Para calcular tendencia
    variacion_absoluta DECIMAL(15,2), -- valor_observado - valor_anterior
    variacion_porcentual DECIMAL(8,2), -- % de cambio
    
    -- Análisis de performance
    progreso_hacia_meta DECIMAL(8,2), -- % de avance hacia la meta
    estado_semaforo ENUM('Verde', 'Amarillo', 'Rojo') NOT NULL,
    cumple_meta BOOLEAN DEFAULT FALSE,
    
    -- Contexto de la medición
    comentario TEXT,
    fuente_medicion VARCHAR(100),
    medicion_automatica BOOLEAN DEFAULT FALSE,
    usuario_registro VARCHAR(50),
    
    -- Metadatos temporales
    fecha_medicion DATE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para consultas frecuentes
    INDEX idx_kr_tiempo (id_kr, id_tiempo),
    INDEX idx_fecha_medicion (fecha_medicion),
    INDEX idx_estado_semaforo (estado_semaforo),
    
    -- Constraints
    FOREIGN KEY (id_kr) REFERENCES DimKR(id_kr) ON DELETE CASCADE,
    FOREIGN KEY (id_tiempo) REFERENCES DimTiempo(id_tiempo),
    
    -- Constraint: una medición por KR por periodo
    UNIQUE KEY uk_kr_tiempo (id_kr, id_tiempo)
);

-- ========================================
-- 4. VISTA: TABLERO BSC CONSOLIDADO
-- ========================================

CREATE OR REPLACE VIEW vw_bsc_tablero_consolidado AS
SELECT 
    -- Información del objetivo
    obj.id_objetivo,
    obj.codigo_objetivo,
    obj.nombre as objetivo_nombre,
    obj.descripcion as objetivo_descripcion,
    obj.perspectiva,
    obj.vision_componente,
    obj.owner_responsable,
    obj.peso_ponderacion,
    
    -- Métricas del objetivo (agregación de KRs)
    COUNT(kr.id_kr) as total_krs,
    COUNT(CASE WHEN ultima_medicion.cumple_meta = TRUE THEN 1 END) as krs_en_meta,
    
    -- Avance ponderado del objetivo (promedio ponderado de KRs)
    COALESCE(
        SUM(ultima_medicion.progreso_hacia_meta * kr.peso_kr) / SUM(kr.peso_kr), 
        0
    ) as avance_objetivo_porcentaje,
    
    -- Estado general del objetivo
    CASE 
        WHEN AVG(CASE 
            WHEN ultima_medicion.estado_semaforo = 'Verde' THEN 3
            WHEN ultima_medicion.estado_semaforo = 'Amarillo' THEN 2
            WHEN ultima_medicion.estado_semaforo = 'Rojo' THEN 1
            ELSE 0
        END) >= 2.5 THEN 'Verde'
        WHEN AVG(CASE 
            WHEN ultima_medicion.estado_semaforo = 'Verde' THEN 3
            WHEN ultima_medicion.estado_semaforo = 'Amarillo' THEN 2
            WHEN ultima_medicion.estado_semaforo = 'Rojo' THEN 1
            ELSE 0
        END) >= 1.5 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    -- Información temporal
    MAX(ultima_medicion.fecha_medicion) as ultima_actualizacion

FROM DimObjetivo obj
LEFT JOIN DimKR kr ON obj.id_objetivo = kr.id_objetivo AND kr.activo = TRUE
LEFT JOIN (
    -- Subquery para obtener la última medición de cada KR
    SELECT h1.*
    FROM HechoOKR h1
    INNER JOIN (
        SELECT id_kr, MAX(fecha_medicion) as max_fecha
        FROM HechoOKR
        GROUP BY id_kr
    ) h2 ON h1.id_kr = h2.id_kr AND h1.fecha_medicion = h2.max_fecha
) ultima_medicion ON kr.id_kr = ultima_medicion.id_kr

WHERE obj.activo = TRUE
GROUP BY obj.id_objetivo, obj.codigo_objetivo, obj.nombre, obj.descripcion, 
         obj.perspectiva, obj.vision_componente, obj.owner_responsable, obj.peso_ponderacion
ORDER BY obj.perspectiva, obj.codigo_objetivo;

-- ========================================
-- 5. VISTA: DETALLE KRs CON ÚLTIMA MEDICIÓN
-- ========================================

CREATE OR REPLACE VIEW vw_bsc_krs_detalle AS
SELECT 
    -- Información del KR
    kr.id_kr,
    kr.codigo_kr,
    kr.nombre as kr_nombre,
    kr.descripcion as kr_descripcion,
    kr.unidad_medida,
    kr.tipo_metrica,
    kr.valor_inicial,
    kr.meta_objetivo,
    kr.umbral_verde,
    kr.umbral_amarillo,
    kr.peso_kr,
    
    -- Información del objetivo padre
    obj.codigo_objetivo,
    obj.nombre as objetivo_nombre,
    obj.perspectiva,
    
    -- Última medición
    ultima_medicion.valor_observado,
    ultima_medicion.valor_anterior,
    ultima_medicion.variacion_absoluta,
    ultima_medicion.variacion_porcentual,
    ultima_medicion.progreso_hacia_meta,
    ultima_medicion.estado_semaforo,
    ultima_medicion.cumple_meta,
    ultima_medicion.comentario,
    ultima_medicion.fecha_medicion,
    
    -- Análisis de tendencia
    CASE 
        WHEN ultima_medicion.variacion_porcentual > 5 THEN 'Mejorando'
        WHEN ultima_medicion.variacion_porcentual < -5 THEN 'Empeorando'
        ELSE 'Estable'
    END as tendencia

FROM DimKR kr
INNER JOIN DimObjetivo obj ON kr.id_objetivo = obj.id_objetivo
LEFT JOIN (
    SELECT h1.*
    FROM HechoOKR h1
    INNER JOIN (
        SELECT id_kr, MAX(fecha_medicion) as max_fecha
        FROM HechoOKR
        GROUP BY id_kr
    ) h2 ON h1.id_kr = h2.id_kr AND h1.fecha_medicion = h2.max_fecha
) ultima_medicion ON kr.id_kr = ultima_medicion.id_kr

WHERE kr.activo = TRUE AND obj.activo = TRUE
ORDER BY obj.perspectiva, obj.codigo_objetivo, kr.codigo_kr;

-- ========================================
-- 6. PROCEDIMIENTOS ALMACENADOS BSC/OKR
-- ========================================

DELIMITER $$

-- Procedimiento para calcular y actualizar estado de semáforo
CREATE PROCEDURE sp_calcular_estado_semaforo(
    IN p_id_kr INT,
    IN p_valor_observado DECIMAL(15,2),
    OUT p_estado_semaforo VARCHAR(10),
    OUT p_progreso_hacia_meta DECIMAL(8,2),
    OUT p_cumple_meta BOOLEAN
)
BEGIN
    DECLARE v_tipo_metrica VARCHAR(20);
    DECLARE v_meta_objetivo DECIMAL(15,2);
    DECLARE v_umbral_verde DECIMAL(15,2);
    DECLARE v_umbral_amarillo DECIMAL(15,2);
    DECLARE v_valor_inicial DECIMAL(15,2);
    
    -- Obtener configuración del KR
    SELECT tipo_metrica, meta_objetivo, umbral_verde, umbral_amarillo, valor_inicial
    INTO v_tipo_metrica, v_meta_objetivo, v_umbral_verde, v_umbral_amarillo, v_valor_inicial
    FROM DimKR
    WHERE id_kr = p_id_kr;
    
    -- Calcular progreso hacia la meta
    IF v_meta_objetivo != v_valor_inicial THEN
        SET p_progreso_hacia_meta = ((p_valor_observado - v_valor_inicial) / (v_meta_objetivo - v_valor_inicial)) * 100;
        
        -- Limitar progreso entre 0 y 100% de forma estricta
        -- Si se cumple o supera la meta, progreso = 100%
        IF v_tipo_metrica IN ('Incrementar', 'Aumentar') THEN
            IF p_valor_observado >= v_meta_objetivo THEN
                SET p_progreso_hacia_meta = 100;
            END IF;
        ELSEIF v_tipo_metrica IN ('Decrementar', 'Disminuir') THEN
            IF p_valor_observado <= v_meta_objetivo THEN
                SET p_progreso_hacia_meta = 100;
            END IF;
        END IF;
        
        -- Asegurar que nunca sea menor a 0% ni mayor a 100%
        SET p_progreso_hacia_meta = GREATEST(0, LEAST(100, p_progreso_hacia_meta));
    ELSE
        SET p_progreso_hacia_meta = 100;
    END IF;
    
    -- Determinar cumplimiento de meta
    IF v_tipo_metrica IN ('Incrementar', 'Aumentar') THEN
        SET p_cumple_meta = (p_valor_observado >= v_meta_objetivo);
    ELSEIF v_tipo_metrica IN ('Decrementar', 'Disminuir') THEN
        SET p_cumple_meta = (p_valor_observado <= v_meta_objetivo);
    ELSEIF v_tipo_metrica = 'Binario' THEN
        SET p_cumple_meta = (p_valor_observado = v_meta_objetivo);
    ELSE
        SET p_cumple_meta = (ABS(p_valor_observado - v_meta_objetivo) <= ABS(v_meta_objetivo * 0.05));
    END IF;
    
    -- Determinar estado de semáforo
    IF v_tipo_metrica IN ('Incrementar', 'Aumentar') THEN
        IF p_valor_observado >= v_umbral_verde THEN
            SET p_estado_semaforo = 'Verde';
        ELSEIF p_valor_observado >= v_umbral_amarillo THEN
            SET p_estado_semaforo = 'Amarillo';
        ELSE
            SET p_estado_semaforo = 'Rojo';
        END IF;
    ELSEIF v_tipo_metrica IN ('Decrementar', 'Disminuir') THEN
        IF p_valor_observado <= v_umbral_verde THEN
            SET p_estado_semaforo = 'Verde';
        ELSEIF p_valor_observado <= v_umbral_amarillo THEN
            SET p_estado_semaforo = 'Amarillo';
        ELSE
            SET p_estado_semaforo = 'Rojo';
        END IF;
    ELSE
        -- Para métricas binarias o de mantener
        IF p_cumple_meta THEN
            SET p_estado_semaforo = 'Verde';
        ELSE
            SET p_estado_semaforo = 'Rojo';
        END IF;
    END IF;
END$$

-- Procedimiento para registrar nueva medición OKR
CREATE PROCEDURE sp_registrar_medicion_okr(
    IN p_id_kr INT,
    IN p_valor_observado DECIMAL(15,2),
    IN p_fecha_medicion DATE,
    IN p_comentario TEXT,
    IN p_fuente_medicion VARCHAR(100),
    IN p_usuario_registro VARCHAR(50)
)
BEGIN
    DECLARE v_valor_anterior DECIMAL(15,2) DEFAULT NULL;
    DECLARE v_variacion_absoluta DECIMAL(15,2) DEFAULT 0;
    DECLARE v_variacion_porcentual DECIMAL(8,2) DEFAULT 0;
    DECLARE v_estado_semaforo VARCHAR(10);
    DECLARE v_progreso_hacia_meta DECIMAL(8,2);
    DECLARE v_cumple_meta BOOLEAN;
    DECLARE v_id_tiempo INT;
    
    -- Obtener ID de tiempo para la fecha
    SELECT id_tiempo INTO v_id_tiempo
    FROM DimTiempo 
    WHERE fecha = p_fecha_medicion
    LIMIT 1;
    
    IF v_id_tiempo IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fecha no encontrada en DimTiempo';
    END IF;
    
    -- Obtener valor anterior (última medición)
    SELECT valor_observado INTO v_valor_anterior
    FROM HechoOKR
    WHERE id_kr = p_id_kr AND fecha_medicion < p_fecha_medicion
    ORDER BY fecha_medicion DESC
    LIMIT 1;
    
    -- Calcular variaciones
    IF v_valor_anterior IS NOT NULL THEN
        SET v_variacion_absoluta = p_valor_observado - v_valor_anterior;
        IF v_valor_anterior != 0 THEN
            SET v_variacion_porcentual = (v_variacion_absoluta / v_valor_anterior) * 100;
        END IF;
    END IF;
    
    -- Calcular estado de semáforo
    CALL sp_calcular_estado_semaforo(
        p_id_kr, p_valor_observado, 
        v_estado_semaforo, v_progreso_hacia_meta, v_cumple_meta
    );
    
    -- Insertar o actualizar medición
    INSERT INTO HechoOKR (
        id_kr, id_tiempo, valor_observado, valor_anterior,
        variacion_absoluta, variacion_porcentual, progreso_hacia_meta,
        estado_semaforo, cumple_meta, comentario, fuente_medicion,
        usuario_registro, fecha_medicion
    ) VALUES (
        p_id_kr, v_id_tiempo, p_valor_observado, v_valor_anterior,
        v_variacion_absoluta, v_variacion_porcentual, v_progreso_hacia_meta,
        v_estado_semaforo, v_cumple_meta, p_comentario, p_fuente_medicion,
        p_usuario_registro, p_fecha_medicion
    )
    ON DUPLICATE KEY UPDATE
        valor_observado = p_valor_observado,
        valor_anterior = v_valor_anterior,
        variacion_absoluta = v_variacion_absoluta,
        variacion_porcentual = v_variacion_porcentual,
        progreso_hacia_meta = v_progreso_hacia_meta,
        estado_semaforo = v_estado_semaforo,
        cumple_meta = v_cumple_meta,
        comentario = p_comentario,
        fuente_medicion = p_fuente_medicion,
        usuario_registro = p_usuario_registro,
        fecha_registro = CURRENT_TIMESTAMP;
        
END$$

DELIMITER ;

-- ========================================
-- 7. DATOS DE EJEMPLO PARA BSC/OKR
-- ========================================

-- Insertar objetivos estratégicos por perspectiva
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, vision_componente, owner_responsable, fecha_creacion, peso_ponderacion) VALUES

-- Perspectiva Financiera
('FIN-001', 'Incrementar Rentabilidad de Proyectos', 'Aumentar el margen de rentabilidad promedio de proyectos al 25%', 'Financiera', 'Excelencia Operacional', 'CFO', CURDATE(), 2.0),
('FIN-002', 'Optimizar Costos Operacionales', 'Reducir costos operacionales en 15% mediante automatización', 'Financiera', 'Automatización de Procesos', 'Director Operaciones', CURDATE(), 1.5),

-- Perspectiva Clientes
('CLI-001', 'Mejorar Satisfacción del Cliente', 'Alcanzar 95% de satisfacción en entregas a tiempo', 'Clientes', 'Confiabilidad y Calidad', 'Director Comercial', CURDATE(), 2.0),
('CLI-002', 'Expandir Cartera de Clientes', 'Aumentar cartera de clientes activos en 30%', 'Clientes', 'Transformación Digital', 'Director Comercial', CURDATE(), 1.5),

-- Perspectiva Procesos Internos
('PRO-001', 'Automatizar Procesos ETL', 'Implementar 90% de procesos ETL automatizados', 'Procesos Internos', 'Automatización de Procesos', 'CTO', CURDATE(), 2.0),
('PRO-002', 'Mejorar Calidad de Datos', 'Reducir errores de datos a menos del 2%', 'Procesos Internos', 'Confiabilidad y Calidad', 'Data Manager', CURDATE(), 1.8),

-- Perspectiva Aprendizaje e Innovación
('INN-001', 'Capacitar Equipo en BI/Analytics', 'Certificar 80% del equipo técnico en herramientas BI', 'Aprendizaje y Innovación', 'Analítica Avanzada', 'CHRO', CURDATE(), 1.5),
('INN-002', 'Implementar Cultura Data-Driven', 'Establecer dashboard ejecutivo con 95% de adopción', 'Aprendizaje y Innovación', 'Transformación Digital', 'CDO', CURDATE(), 1.8);

-- Insertar KRs para cada objetivo
INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, descripcion, formula_calculo, unidad_medida, tipo_metrica, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo, peso_kr, frecuencia_medicion, fecha_creacion) VALUES

-- KRs para FIN-001 (Rentabilidad)
(1, 'FIN-001-KR1', 'Margen de Rentabilidad Promedio', 'Porcentaje de margen sobre ventas de proyectos', 'AVG((presupuesto - costo_real) / presupuesto * 100)', '%', 'Incrementar', 18.0, 25.0, 25.0, 22.0, 1.0, 'Mensual', CURDATE()),
(1, 'FIN-001-KR2', 'Proyectos con Rentabilidad > 20%', 'Cantidad de proyectos con margen superior al 20%', 'COUNT(*) WHERE margen > 20', 'cantidad', 'Incrementar', 5, 15, 15, 12, 0.8, 'Mensual', CURDATE()),

-- KRs para CLI-001 (Satisfacción)
(3, 'CLI-001-KR1', 'Entregas a Tiempo', 'Porcentaje de proyectos entregados en fecha', 'COUNT(entregado_a_tiempo) / COUNT(*) * 100', '%', 'Incrementar', 75.0, 95.0, 95.0, 90.0, 1.0, 'Mensual', CURDATE()),
(3, 'CLI-001-KR2', 'NPS de Clientes', 'Net Promoter Score de satisfacción', 'Encuestas de satisfacción', 'puntos', 'Incrementar', 6.5, 8.5, 8.5, 7.5, 0.9, 'Trimestral', CURDATE()),

-- KRs para PRO-001 (Automatización ETL)
(5, 'PRO-001-KR1', 'Procesos ETL Automatizados', 'Porcentaje de procesos ETL sin intervención manual', 'COUNT(automaticos) / COUNT(*) * 100', '%', 'Incrementar', 60.0, 90.0, 90.0, 85.0, 1.0, 'Mensual', CURDATE()),
(5, 'PRO-001-KR2', 'Tiempo Promedio de ETL', 'Tiempo promedio de ejecución de procesos ETL', 'AVG(tiempo_ejecucion)', 'minutos', 'Decrementar', 120.0, 45.0, 45.0, 60.0, 0.7, 'Semanal', CURDATE()),

-- KRs para INN-001 (Capacitación)
(7, 'INN-001-KR1', 'Empleados Certificados BI', 'Porcentaje de equipo técnico con certificación BI', 'COUNT(certificados) / COUNT(tecnicos) * 100', '%', 'Incrementar', 25.0, 80.0, 80.0, 70.0, 1.0, 'Mensual', CURDATE()),
(7, 'INN-001-KR2', 'Horas de Capacitación', 'Horas totales de capacitación en BI por empleado', 'SUM(horas_capacitacion) / COUNT(empleados)', 'horas', 'Incrementar', 8.0, 40.0, 40.0, 30.0, 0.6, 'Mensual', CURDATE());

-- ========================================
-- FIN DE CREACIÓN DE MÓDULO BSC/OKR
-- ========================================