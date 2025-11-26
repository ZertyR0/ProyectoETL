-- ========================================
-- CUBO OLAP - VISTAS CORREGIDAS
-- Análisis multidimensional con datos reales
-- ========================================

USE dw_proyectos_hist;

-- ========================================
-- 1. VISTA BASE: Datos del cubo con todas las dimensiones
-- ========================================
CREATE OR REPLACE VIEW vw_olap_base AS
SELECT 
    -- IDs para joins
    hp.id_proyecto,
    hp.id_cliente,
    hp.id_equipo,
    hp.id_tiempo_fin_real as id_tiempo,
    
    -- Dimensiones
    dc.nombre as cliente_nombre,
    dc.sector as cliente_sector,
    de.nombre_equipo as equipo_nombre,
    dt.anio,
    dt.trimestre,
    dt.mes,
    dt.fecha,
    
    -- Métricas del proyecto
    hp.presupuesto,
    hp.costo_real_proy as costo_real,
    hp.duracion_real,
    hp.duracion_planificada,
    hp.cumplimiento_presupuesto,
    hp.cumplimiento_tiempo,
    
    -- Métricas calculadas
    (hp.presupuesto - hp.costo_real_proy) as margen,
    CASE 
        WHEN hp.presupuesto > 0 
        THEN ((hp.presupuesto - hp.costo_real_proy) / hp.presupuesto * 100)
        ELSE 0 
    END as rentabilidad_pct,
    
    -- Indicadores
    CASE WHEN hp.cumplimiento_presupuesto = 1 THEN 1 ELSE 0 END as en_presupuesto,
    CASE WHEN hp.cumplimiento_tiempo = 1 THEN 1 ELSE 0 END as a_tiempo,
    1 as completado,  -- HechoProyecto solo tiene proyectos completados/cancelados
    0 as cancelado
    
FROM HechoProyecto hp
INNER JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
INNER JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
INNER JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo;

-- ========================================
-- 2. VISTA OLAP: KPIs por Cliente
-- ========================================
CREATE OR REPLACE VIEW vw_olap_por_cliente AS
SELECT 
    id_cliente,
    cliente_nombre as nombre,
    cliente_sector as sector,
    
    -- Conteos
    COUNT(*) as total_proyectos,
    SUM(completado) as proyectos_completados,
    SUM(cancelado) as proyectos_cancelados,
    
    -- Financiero
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(presupuesto) as presupuesto_promedio,
    AVG(costo_real) as costo_promedio,
    SUM(margen) as margen_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    
    -- Cumplimiento
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo,
    ROUND(SUM(en_presupuesto) * 100.0 / COUNT(*), 2) as pct_en_presupuesto,
    ROUND(SUM(a_tiempo) * 100.0 / COUNT(*), 2) as pct_a_tiempo,
    
    -- Duración
    AVG(duracion_real) as duracion_promedio,
    AVG(duracion_planificada) as duracion_planificada_promedio
    
FROM vw_olap_base
GROUP BY id_cliente, cliente_nombre, cliente_sector
ORDER BY total_proyectos DESC;

-- ========================================
-- 3. VISTA OLAP: KPIs por Equipo
-- ========================================
CREATE OR REPLACE VIEW vw_olap_por_equipo AS
SELECT 
    id_equipo,
    equipo_nombre as nombre,
    
    -- Conteos
    COUNT(*) as total_proyectos,
    SUM(completado) as proyectos_completados,
    SUM(cancelado) as proyectos_cancelados,
    
    -- Financiero
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(presupuesto) as presupuesto_promedio,
    AVG(costo_real) as costo_promedio,
    SUM(margen) as margen_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    
    -- Cumplimiento
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo,
    ROUND(SUM(en_presupuesto) * 100.0 / COUNT(*), 2) as pct_en_presupuesto,
    ROUND(SUM(a_tiempo) * 100.0 / COUNT(*), 2) as pct_a_tiempo,
    
    -- Duración
    AVG(duracion_real) as duracion_promedio,
    AVG(duracion_planificada) as duracion_planificada_promedio
    
FROM vw_olap_base
GROUP BY id_equipo, equipo_nombre
ORDER BY total_proyectos DESC;

-- ========================================
-- 4. VISTA OLAP: KPIs por Tiempo (Año)
-- ========================================
CREATE OR REPLACE VIEW vw_olap_por_anio AS
SELECT 
    anio,
    
    -- Conteos
    COUNT(*) as total_proyectos,
    SUM(completado) as proyectos_completados,
    SUM(cancelado) as proyectos_cancelados,
    
    -- Financiero
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(presupuesto) as presupuesto_promedio,
    AVG(costo_real) as costo_promedio,
    SUM(margen) as margen_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    
    -- Cumplimiento
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo,
    ROUND(SUM(en_presupuesto) * 100.0 / COUNT(*), 2) as pct_en_presupuesto,
    ROUND(SUM(a_tiempo) * 100.0 / COUNT(*), 2) as pct_a_tiempo,
    
    -- Duración
    AVG(duracion_real) as duracion_promedio,
    AVG(duracion_planificada) as duracion_planificada_promedio
    
FROM vw_olap_base
GROUP BY anio
ORDER BY anio;

-- ========================================
-- 5. VISTA OLAP: KPIs por Trimestre
-- ========================================
CREATE OR REPLACE VIEW vw_olap_por_trimestre AS
SELECT 
    anio,
    trimestre,
    CONCAT(anio, '-Q', trimestre) as periodo,
    
    -- Conteos
    COUNT(*) as total_proyectos,
    SUM(completado) as proyectos_completados,
    SUM(cancelado) as proyectos_cancelados,
    
    -- Financiero
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(presupuesto) as presupuesto_promedio,
    AVG(costo_real) as costo_promedio,
    SUM(margen) as margen_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    
    -- Cumplimiento
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo,
    ROUND(SUM(en_presupuesto) * 100.0 / COUNT(*), 2) as pct_en_presupuesto,
    ROUND(SUM(a_tiempo) * 100.0 / COUNT(*), 2) as pct_a_tiempo,
    
    -- Duración
    AVG(duracion_real) as duracion_promedio
    
FROM vw_olap_base
GROUP BY anio, trimestre
ORDER BY anio, trimestre;

-- ========================================
-- 6. VISTA OLAP: KPIs Totales (Resumen Ejecutivo)
-- ========================================
CREATE OR REPLACE VIEW vw_olap_total AS
SELECT 
    -- Conteos
    COUNT(*) as total_proyectos,
    SUM(completado) as proyectos_completados,
    SUM(cancelado) as proyectos_cancelados,
    COUNT(DISTINCT id_cliente) as total_clientes,
    COUNT(DISTINCT id_equipo) as total_equipos,
    COUNT(DISTINCT anio) as anios_operacion,
    
    -- Financiero
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(presupuesto) as presupuesto_promedio,
    AVG(costo_real) as costo_promedio,
    SUM(margen) as margen_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    
    -- Cumplimiento
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo,
    ROUND(SUM(en_presupuesto) * 100.0 / COUNT(*), 2) as pct_en_presupuesto,
    ROUND(SUM(a_tiempo) * 100.0 / COUNT(*), 2) as pct_a_tiempo,
    
    -- Duración
    AVG(duracion_real) as duracion_promedio,
    AVG(duracion_planificada) as duracion_planificada_promedio,
    MIN(fecha) as fecha_primer_proyecto,
    MAX(fecha) as fecha_ultimo_proyecto
    
FROM vw_olap_base;

-- ========================================
-- 7. VISTA OLAP: Detallado (Proyecto por Proyecto)
-- ========================================
CREATE OR REPLACE VIEW vw_olap_detallado AS
SELECT 
    id_proyecto,
    cliente_nombre,
    equipo_nombre,
    anio,
    trimestre,
    mes,
    fecha,
    
    -- Métricas
    presupuesto,
    costo_real,
    margen,
    rentabilidad_pct,
    duracion_real,
    duracion_planificada,
    
    -- Estado y cumplimiento
    en_presupuesto,
    a_tiempo,
    cumplimiento_presupuesto,
    cumplimiento_tiempo
    
FROM vw_olap_base
ORDER BY fecha DESC;

-- ========================================
-- 8. VISTA OLAP: Cliente + Año (Drill-down Cliente → Tiempo)
-- ========================================
CREATE OR REPLACE VIEW vw_olap_cliente_anio AS
SELECT 
    id_cliente,
    cliente_nombre,
    anio,
    
    COUNT(*) as total_proyectos,
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo
    
FROM vw_olap_base
GROUP BY id_cliente, cliente_nombre, anio
ORDER BY id_cliente, anio;

-- ========================================
-- 9. VISTA OLAP: Equipo + Año (Drill-down Equipo → Tiempo)
-- ========================================
CREATE OR REPLACE VIEW vw_olap_equipo_anio AS
SELECT 
    id_equipo,
    equipo_nombre,
    anio,
    
    COUNT(*) as total_proyectos,
    SUM(presupuesto) as presupuesto_total,
    SUM(costo_real) as costo_real_total,
    AVG(rentabilidad_pct) as rentabilidad_promedio,
    SUM(en_presupuesto) as proy_en_presupuesto,
    SUM(a_tiempo) as proy_a_tiempo
    
FROM vw_olap_base
GROUP BY id_equipo, equipo_nombre, anio
ORDER BY id_equipo, anio;

-- ========================================
-- VERIFICACIÓN
-- ========================================
SELECT 'Vistas OLAP creadas correctamente' as resultado;

SELECT 'Vista por Cliente' as vista, COUNT(*) as registros FROM vw_olap_por_cliente
UNION ALL
SELECT 'Vista por Equipo', COUNT(*) FROM vw_olap_por_equipo
UNION ALL
SELECT 'Vista por Año', COUNT(*) FROM vw_olap_por_anio
UNION ALL
SELECT 'Vista por Trimestre', COUNT(*) FROM vw_olap_por_trimestre
UNION ALL
SELECT 'Vista Total', COUNT(*) FROM vw_olap_total
UNION ALL
SELECT 'Vista Detallado', COUNT(*) FROM vw_olap_detallado;
