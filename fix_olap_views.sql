-- ========================================
-- FIX: Corregir Vistas OLAP para Railway
-- Fecha: 2025-11-28
-- ========================================

USE dw_proyectos_hist;

-- ========================================
-- 1. DROP vistas antiguas si existen
-- ========================================
DROP VIEW IF EXISTS vw_olap_kpis_ejecutivos;
DROP VIEW IF EXISTS vw_olap_sector_performance;

-- ========================================
-- 2. VISTA CORREGIDA: KPIs Ejecutivos
-- ========================================
CREATE VIEW vw_olap_kpis_ejecutivos AS
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
-- 3. VISTA CORREGIDA: Performance por Sector
-- ========================================
CREATE VIEW vw_olap_sector_performance AS
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
-- 4. VERIFICACIÓN: Consultar datos de prueba
-- ========================================

-- Ver KPIs más recientes
SELECT 
    anio,
    trimestre,
    total_proyectos_periodo,
    proyectos_completados,
    proyectos_activos,
    ROUND(presupuesto_total_periodo, 2) as presupuesto_total,
    ROUND(eficiencia_estimacion_porcentaje, 2) as eficiencia_pct
FROM vw_olap_kpis_ejecutivos
ORDER BY anio DESC, trimestre DESC
LIMIT 5;

-- Ver performance por sector
SELECT 
    sector,
    anio,
    proyectos_sector,
    ROUND(facturacion_sector, 2) as facturacion,
    ROUND(margen_rentabilidad_porcentaje, 2) as rentabilidad_pct
FROM vw_olap_sector_performance
ORDER BY anio DESC, facturacion_sector DESC
LIMIT 10;

-- Verificar que hay datos en HechoProyecto
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT id_cliente) as clientes,
    COUNT(DISTINCT id_empleado_gerente) as gerentes,
    COUNT(DISTINCT id_tiempo_fin_real) as periodos_tiempo
FROM HechoProyecto;

-- Verificar JOIN con DimCliente
SELECT 
    hp.id_proyecto,
    dc.nombre as nombre_cliente,
    dc.sector,
    hp.presupuesto
FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LIMIT 5;
