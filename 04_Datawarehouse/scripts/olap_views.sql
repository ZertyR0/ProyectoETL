-- ========================================
-- CUBO OLAP - VISTAS MATERIALIZADAS CON ROLLUP
-- Sistema de Soporte de Decisiones (DSS)
-- ========================================
-- 
-- Implementación de cubo OLAP lógico usando vistas con ROLLUP
-- para análisis multidimensional con capacidades de drill-down
--

USE dw_proyectos_hist;

-- ========================================
-- 1. VISTA OLAP: ANÁLISIS DE PROYECTOS POR DIMENSIONES
-- ========================================

-- Proyectos con agregaciones por Cliente, Equipo y Tiempo
CREATE OR REPLACE VIEW vw_olap_proyectos_rollup_cliente_equipo_tiempo AS
SELECT 
    -- Dimensiones principales
    COALESCE(dc.nombre_cliente, 'TODOS') as cliente,
    COALESCE(dc.sector, 'TODOS') as sector_cliente,
    COALESCE(de.nombre_equipo, 'TODOS') as equipo,
    COALESCE(de.tipo, 'TODOS') as tipo_equipo,
    COALESCE(dt.anio, 9999) as anio,
    COALESCE(dt.trimestre, 0) as trimestre,
    COALESCE(dt.mes, 0) as mes,
    
    -- Métricas de negocio
    COUNT(hp.id_proyecto) as total_proyectos,
    COUNT(CASE WHEN hp.estado = 'Completado' THEN 1 END) as proyectos_completados,
    COUNT(CASE WHEN hp.estado = 'Cancelado' THEN 1 END) as proyectos_cancelados,
    COUNT(CASE WHEN hp.estado = 'En Progreso' THEN 1 END) as proyectos_en_progreso,
    
    -- KPIs financieros
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real_total,
    AVG(hp.presupuesto) as presupuesto_promedio,
    AVG(hp.costo_real) as costo_real_promedio,
    
    -- KPIs de rendimiento
    AVG(hp.progreso_porcentaje) as progreso_promedio,
    SUM(CASE WHEN hp.fecha_fin_real <= hp.fecha_fin_plan THEN 1 ELSE 0 END) as proyectos_a_tiempo,
    
    -- Nivel de agregación (para drill-down)
    CASE 
        WHEN dc.id_cliente IS NULL AND de.id_equipo IS NULL AND dt.id_tiempo IS NULL THEN 'TOTAL'
        WHEN dc.id_cliente IS NULL AND de.id_equipo IS NULL THEN 'POR_TIEMPO'
        WHEN dc.id_cliente IS NULL AND dt.id_tiempo IS NULL THEN 'POR_EQUIPO'
        WHEN de.id_equipo IS NULL AND dt.id_tiempo IS NULL THEN 'POR_CLIENTE'
        WHEN dc.id_cliente IS NULL THEN 'EQUIPO_TIEMPO'
        WHEN de.id_equipo IS NULL THEN 'CLIENTE_TIEMPO'
        WHEN dt.id_tiempo IS NULL THEN 'CLIENTE_EQUIPO'
        ELSE 'DETALLADO'
    END as nivel_agregacion

FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
LEFT JOIN DimTiempo dt ON hp.id_tiempo = dt.id_tiempo

GROUP BY 
    dc.id_cliente, dc.nombre_cliente, dc.sector,
    de.id_equipo, de.nombre_equipo, de.tipo,
    dt.id_tiempo, dt.anio, dt.trimestre, dt.mes
WITH ROLLUP

HAVING COUNT(hp.id_proyecto) > 0;

-- ========================================
-- 2. VISTA OLAP: ANÁLISIS DE TAREAS POR DIMENSIONES
-- ========================================

CREATE OR REPLACE VIEW vw_olap_tareas_rollup_equipo_proyecto_tiempo AS
SELECT 
    -- Dimensiones principales
    COALESCE(de.nombre_equipo, 'TODOS') as equipo,
    COALESCE(de.tipo, 'TODOS') as tipo_equipo,
    COALESCE(dp.nombre_proyecto, 'TODOS') as proyecto,
    COALESCE(dp.estado, 'TODOS') as estado_proyecto,
    COALESCE(dt.anio, 9999) as anio,
    COALESCE(dt.trimestre, 0) as trimestre,
    COALESCE(dt.mes, 0) as mes,
    
    -- Métricas de tareas
    COUNT(ht.id_tarea) as total_tareas,
    COUNT(CASE WHEN ht.estado = 'Completado' THEN 1 END) as tareas_completadas,
    COUNT(CASE WHEN ht.estado = 'Cancelado' THEN 1 END) as tareas_canceladas,
    COUNT(CASE WHEN ht.estado = 'En Progreso' THEN 1 END) as tareas_en_progreso,
    COUNT(CASE WHEN ht.estado = 'Pendiente' THEN 1 END) as tareas_pendientes,
    
    -- KPIs de productividad
    SUM(ht.horas_trabajadas) as horas_trabajadas_total,
    SUM(ht.horas_estimadas) as horas_estimadas_total,
    AVG(ht.horas_trabajadas) as horas_trabajadas_promedio,
    AVG(ht.progreso_porcentaje) as progreso_promedio_tareas,
    
    -- KPIs financieros de tareas
    SUM(ht.costo_real) as costo_tareas_total,
    SUM(ht.costo_estimado) as costo_tareas_estimado,
    AVG(ht.costo_real) as costo_tareas_promedio,
    
    -- Eficiencia
    CASE 
        WHEN SUM(ht.horas_estimadas) > 0 THEN 
            (SUM(ht.horas_trabajadas) / SUM(ht.horas_estimadas)) * 100
        ELSE NULL
    END as eficiencia_horas_porcentaje,
    
    -- Nivel de agregación
    CASE 
        WHEN de.id_equipo IS NULL AND dp.id_proyecto IS NULL AND dt.id_tiempo IS NULL THEN 'TOTAL'
        WHEN de.id_equipo IS NULL AND dp.id_proyecto IS NULL THEN 'POR_TIEMPO'
        WHEN de.id_equipo IS NULL AND dt.id_tiempo IS NULL THEN 'POR_PROYECTO'
        WHEN dp.id_proyecto IS NULL AND dt.id_tiempo IS NULL THEN 'POR_EQUIPO'
        WHEN de.id_equipo IS NULL THEN 'PROYECTO_TIEMPO'
        WHEN dp.id_proyecto IS NULL THEN 'EQUIPO_TIEMPO'
        WHEN dt.id_tiempo IS NULL THEN 'EQUIPO_PROYECTO'
        ELSE 'DETALLADO'
    END as nivel_agregacion

FROM HechoTarea ht
LEFT JOIN DimEquipo de ON ht.id_equipo = de.id_equipo
LEFT JOIN DimProyecto dp ON ht.id_proyecto = dp.id_proyecto
LEFT JOIN DimTiempo dt ON ht.id_tiempo = dt.id_tiempo

GROUP BY 
    de.id_equipo, de.nombre_equipo, de.tipo,
    dp.id_proyecto, dp.nombre_proyecto, dp.estado,
    dt.id_tiempo, dt.anio, dt.trimestre, dt.mes
WITH ROLLUP

HAVING COUNT(ht.id_tarea) > 0;

-- ========================================
-- 3. VISTA OLAP: KPIs EJECUTIVOS (DASHBOARD)
-- ========================================

CREATE OR REPLACE VIEW vw_olap_kpis_ejecutivos AS
SELECT 
    dt.anio,
    dt.trimestre,
    dt.mes,
    dt.fecha,
    
    -- KPIs de Proyectos
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos_periodo,
    SUM(hp.tareas_completadas) as proyectos_completados,
    COUNT(DISTINCT CASE WHEN hp.porcentaje_completado < 100 THEN hp.id_proyecto END) as proyectos_activos,
    
    -- KPIs Financieros
    SUM(hp.presupuesto) as presupuesto_total_periodo,
    SUM(hp.costo_real) as costo_real_total_periodo,
    AVG(CASE WHEN hp.costo_real > 0 AND hp.presupuesto > 0 
        THEN (hp.costo_real / hp.presupuesto) * 100 
        ELSE NULL END) as variacion_presupuesto_promedio,
    
    -- KPIs de Calidad y Tiempo
    AVG(hp.porcentaje_completado) as progreso_promedio_proyectos,
    SUM(hp.cumplimiento_tiempo) as proyectos_entregados_a_tiempo,
    
    -- KPIs de Recursos Humanos
    COUNT(DISTINCT hp.id_empleado_gerente) as empleados_activos_periodo,
    SUM(hp.horas_reales_total) as horas_trabajadas_total_periodo,
    AVG(hp.horas_reales_total) as horas_promedio_por_proyecto,
    
    -- KPIs de Productividad
    CASE 
        WHEN SUM(hp.horas_estimadas_total) > 0 THEN 
            (SUM(hp.horas_reales_total) / SUM(hp.horas_estimadas_total)) * 100
        ELSE NULL
    END as eficiencia_estimacion_porcentaje,
    
    -- Velocidad de cierre de tareas
    SUM(hp.tareas_completadas) as tareas_cerradas_periodo,
    SUM(hp.tareas_total) as tareas_total_periodo

FROM DimTiempo dt
LEFT JOIN HechoProyecto hp ON dt.id_tiempo = hp.id_tiempo_fin_real

WHERE dt.fecha >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH) -- Últimos 2 años
GROUP BY dt.id_tiempo, dt.anio, dt.trimestre, dt.mes, dt.fecha
ORDER BY dt.fecha DESC;

-- ========================================
-- 4. VISTA OLAP: ANÁLISIS POR SECTOR DE CLIENTE
-- ========================================

CREATE OR REPLACE VIEW vw_olap_sector_performance AS
SELECT 
    dc.sector,
    dt.anio,
    
    -- Métricas de proyectos por sector
    COUNT(hp.id_proyecto) as proyectos_sector,
    SUM(hp.presupuesto) as facturacion_sector,
    SUM(hp.costo_real) as costo_sector,
    AVG(hp.porcentaje_completado) as progreso_promedio_sector,
    
    -- Rentabilidad por sector
    CASE 
        WHEN SUM(hp.presupuesto) > 0 THEN 
            ((SUM(hp.presupuesto) - SUM(hp.costo_real)) / SUM(hp.presupuesto)) * 100
        ELSE NULL
    END as margen_rentabilidad_porcentaje,
    
    -- Satisfacción del cliente (proxy: proyectos completados a tiempo)
    CASE 
        WHEN COUNT(hp.id_proyecto) > 0 THEN
            (SUM(hp.cumplimiento_tiempo) / COUNT(hp.id_proyecto)) * 100
        ELSE NULL
    END as indice_cumplimiento_porcentaje

FROM DimCliente dc
JOIN HechoProyecto hp ON dc.id_cliente = hp.id_cliente
JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
WHERE dt.anio >= YEAR(CURDATE()) - 2
GROUP BY dc.sector, dt.anio
ORDER BY dc.sector, dt.anio;

-- ========================================
-- 5. ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS OLAP
-- ========================================

-- Índices compuestos para mejorar performance de drill-down
CREATE INDEX IF NOT EXISTS idx_olap_proyecto_cliente_tiempo ON HechoProyecto(id_cliente, id_tiempo_fin_real);
CREATE INDEX IF NOT EXISTS idx_olap_proyecto_equipo ON HechoProyecto(id_equipo);
CREATE INDEX IF NOT EXISTS idx_olap_proyecto_gerente ON HechoProyecto(id_empleado_gerente);

-- Índices para dimensiones frecuentemente consultadas
CREATE INDEX IF NOT EXISTS idx_dim_cliente_sector ON DimCliente(sector);
CREATE INDEX IF NOT EXISTS idx_dim_equipo_nombre ON DimEquipo(nombre_equipo);
CREATE INDEX IF NOT EXISTS idx_dim_tiempo_anio_mes ON DimTiempo(anio, mes);
CREATE INDEX IF NOT EXISTS idx_dim_proyecto_nombre ON DimProyecto(nombre_proyecto);

-- ========================================
-- 6. PROCEDIMIENTOS PARA ANÁLISIS OLAP
-- ========================================

DELIMITER $$

-- Procedimiento para drill-down dinámico en proyectos
CREATE PROCEDURE sp_olap_drill_down_proyectos(
    IN p_nivel VARCHAR(20),
    IN p_cliente_id INT DEFAULT NULL,
    IN p_equipo_id INT DEFAULT NULL,
    IN p_anio INT DEFAULT NULL,
    IN p_trimestre INT DEFAULT NULL
)
BEGIN
    DECLARE sql_query TEXT;
    
    SET sql_query = '
    SELECT 
        cliente, sector_cliente, equipo, tipo_equipo,
        anio, trimestre, mes,
        total_proyectos, proyectos_completados, 
        proyectos_cancelados, proyectos_en_progreso,
        presupuesto_total, costo_real_total,
        progreso_promedio, proyectos_a_tiempo,
        nivel_agregacion
    FROM vw_olap_proyectos_rollup_cliente_equipo_tiempo
    WHERE 1=1';
    
    -- Filtros dinámicos
    IF p_cliente_id IS NOT NULL THEN
        SET sql_query = CONCAT(sql_query, ' AND cliente != "TODOS"');
    END IF;
    
    IF p_equipo_id IS NOT NULL THEN
        SET sql_query = CONCAT(sql_query, ' AND equipo != "TODOS"');
    END IF;
    
    IF p_anio IS NOT NULL THEN
        SET sql_query = CONCAT(sql_query, ' AND anio = ', p_anio);
    END IF;
    
    IF p_trimestre IS NOT NULL THEN
        SET sql_query = CONCAT(sql_query, ' AND trimestre = ', p_trimestre);
    END IF;
    
    -- Nivel de agregación deseado
    IF p_nivel IS NOT NULL THEN
        SET sql_query = CONCAT(sql_query, ' AND nivel_agregacion = "', p_nivel, '"');
    END IF;
    
    SET sql_query = CONCAT(sql_query, ' ORDER BY anio DESC, trimestre DESC, total_proyectos DESC');
    
    SET @sql = sql_query;
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

-- Procedimiento para series temporales OLAP
CREATE PROCEDURE sp_olap_series_temporales(
    IN p_granularidad VARCHAR(10), -- 'mes', 'trimestre', 'anio'
    IN p_metrica VARCHAR(30),      -- 'proyectos', 'presupuesto', 'horas'
    IN p_periodo_meses INT DEFAULT 12
)
BEGIN
    DECLARE sql_base TEXT;
    
    IF p_granularidad = 'anio' THEN
        SET sql_base = '
        SELECT 
            anio as periodo,
            SUM(total_proyectos) as proyectos,
            SUM(presupuesto_total) as presupuesto,
            SUM(horas_trabajadas_total_periodo) as horas
        FROM vw_olap_kpis_ejecutivos
        WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL ';
        SET sql_base = CONCAT(sql_base, p_periodo_meses, ' MONTH)
        GROUP BY anio ORDER BY anio');
    
    ELSEIF p_granularidad = 'trimestre' THEN
        SET sql_base = '
        SELECT 
            CONCAT(anio, "-T", trimestre) as periodo,
            SUM(total_proyectos_periodo) as proyectos,
            SUM(presupuesto_total_periodo) as presupuesto,
            SUM(horas_trabajadas_total_periodo) as horas
        FROM vw_olap_kpis_ejecutivos
        WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL ';
        SET sql_base = CONCAT(sql_base, p_periodo_meses, ' MONTH)
        GROUP BY anio, trimestre ORDER BY anio, trimestre');
    
    ELSE -- mes
        SET sql_base = '
        SELECT 
            DATE_FORMAT(fecha, "%Y-%m") as periodo,
            SUM(total_proyectos_periodo) as proyectos,
            SUM(presupuesto_total_periodo) as presupuesto,
            SUM(horas_trabajadas_total_periodo) as horas
        FROM vw_olap_kpis_ejecutivos
        WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL ';
        SET sql_base = CONCAT(sql_base, p_periodo_meses, ' MONTH)
        GROUP BY DATE_FORMAT(fecha, "%Y-%m") ORDER BY fecha');
    END IF;
    
    SET @sql = sql_base;
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

-- ========================================
-- FIN DE CREACIÓN DE CUBO OLAP
-- ========================================