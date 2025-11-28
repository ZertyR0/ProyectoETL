-- Script SQL para recrear vistas OLAP en Railway con nombres de columnas correctos
-- Ejecutar este script en Railway MySQL Dashboard

-- 1. Eliminar vistas antiguas
DROP VIEW IF EXISTS vw_olap_detallado;
DROP VIEW IF EXISTS vw_olap_por_cliente;
DROP VIEW IF EXISTS vw_olap_por_equipo;
DROP VIEW IF EXISTS vw_olap_por_anio;
DROP VIEW IF EXISTS vw_olap_total;

-- 2. VISTA DETALLADA (nivel más granular)
CREATE VIEW vw_olap_detallado AS
SELECT 
    hp.id_proyecto,
    dp.nombre_proyecto as proyecto,
    COALESCE(dc.nombre, 'Sin Cliente') as cliente,
    dc.sector,
    COALESCE(de.nombre_equipo, 'N/A') as equipo,
    YEAR(hp.id_tiempo_fin_real) as anio,
    QUARTER(hp.id_tiempo_fin_real) as trimestre,
    MONTH(hp.id_tiempo_fin_real) as mes,
    dp.estado,
    hp.presupuesto,
    hp.costo_real_proy as costo_real,
    (hp.presupuesto - hp.costo_real_proy) as margen,
    CASE 
        WHEN hp.presupuesto > 0 
        THEN ROUND(((hp.presupuesto - hp.costo_real_proy) / hp.presupuesto * 100), 2)
        ELSE 0 
    END as rentabilidad_porcentaje,
    hp.horas_reales_total as horas_reales,
    hp.horas_plan_total as horas_estimadas,
    CASE 
        WHEN hp.costo_real_proy <= hp.presupuesto THEN 'Sí'
        ELSE 'No'
    END as en_presupuesto,
    dp.fecha_inicio_plan as fecha_inicio,
    hp.id_tiempo_fin_real as fecha_fin
FROM HechoProyecto hp
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
ORDER BY hp.id_tiempo_fin_real DESC, dp.nombre_proyecto;

-- 3. VISTA POR CLIENTE (agregado por cliente)
CREATE VIEW vw_olap_por_cliente AS
SELECT 
    hp.id_cliente,
    COALESCE(dc.nombre, 'Sin Cliente') as cliente,
    dc.sector,
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Completado' THEN hp.id_proyecto END) as proyectos_completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real_proy) as costo_total,
    SUM(hp.presupuesto - hp.costo_real_proy) as margen_total,
    CASE 
        WHEN SUM(hp.presupuesto) > 0 
        THEN ROUND(((SUM(hp.presupuesto) - SUM(hp.costo_real_proy)) / SUM(hp.presupuesto) * 100), 2)
        ELSE 0 
    END as rentabilidad_promedio_porcentaje,
    ROUND(AVG(CASE 
        WHEN hp.costo_real_proy <= hp.presupuesto THEN 100
        ELSE 0
    END), 2) as porcentaje_en_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
GROUP BY hp.id_cliente, dc.nombre, dc.sector
ORDER BY total_proyectos DESC;

-- 4. VISTA POR EQUIPO (agregado por equipo)
CREATE VIEW vw_olap_por_equipo AS
SELECT 
    hp.id_equipo,
    COALESCE(de.nombre_equipo, 'N/A') as equipo,
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Completado' THEN hp.id_proyecto END) as proyectos_completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real_proy) as costo_total,
    SUM(hp.presupuesto - hp.costo_real_proy) as margen_total,
    CASE 
        WHEN SUM(hp.presupuesto) > 0 
        THEN ROUND(((SUM(hp.presupuesto) - SUM(hp.costo_real_proy)) / SUM(hp.presupuesto) * 100), 2)
        ELSE 0 
        END as rentabilidad_promedio_porcentaje,
    SUM(hp.horas_reales_total) as horas_reales_total,
    SUM(hp.horas_plan_total) as horas_estimadas_total
FROM HechoProyecto hp
LEFT JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
GROUP BY hp.id_equipo, de.nombre_equipo
ORDER BY total_proyectos DESC;

-- 5. VISTA POR AÑO (agregado por tiempo)
CREATE VIEW vw_olap_por_anio AS
SELECT 
    YEAR(hp.id_tiempo_fin_real) as anio,
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Completado' THEN hp.id_proyecto END) as proyectos_completados,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Cancelado' THEN hp.id_proyecto END) as proyectos_cancelados,
    COUNT(DISTINCT CASE WHEN dp.estado = 'En Progreso' THEN hp.id_proyecto END) as proyectos_en_progreso,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real_proy) as costo_total,
    SUM(hp.presupuesto - hp.costo_real_proy) as margen_total,
    CASE 
        WHEN SUM(hp.presupuesto) > 0 
        THEN ROUND(((SUM(hp.presupuesto) - SUM(hp.costo_real_proy)) / SUM(hp.presupuesto) * 100), 2)
        ELSE 0 
    END as rentabilidad_promedio_porcentaje,
    SUM(hp.horas_reales_total) as horas_reales_total,
    SUM(hp.horas_plan_total) as horas_estimadas_total
FROM HechoProyecto hp
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
GROUP BY YEAR(hp.id_tiempo_fin_real)
ORDER BY YEAR(hp.id_tiempo_fin_real) DESC;

-- 6. VISTA TOTAL (resumen global)
CREATE VIEW vw_olap_total AS
SELECT 
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Completado' THEN hp.id_proyecto END) as proyectos_completados,
    COUNT(DISTINCT CASE WHEN dp.estado = 'Cancelado' THEN hp.id_proyecto END) as proyectos_cancelados,
    COUNT(DISTINCT CASE WHEN dp.estado = 'En Progreso' THEN hp.id_proyecto END) as proyectos_activos,
    COUNT(DISTINCT hp.id_cliente) as total_clientes,
    COUNT(DISTINCT hp.id_equipo) as total_equipos,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real_proy) as costo_total,
    SUM(hp.presupuesto - hp.costo_real_proy) as margen_total,
    CASE 
        WHEN SUM(hp.presupuesto) > 0 
        THEN ROUND(((SUM(hp.presupuesto) - SUM(hp.costo_real_proy)) / SUM(hp.presupuesto) * 100), 2)
        ELSE 0 
    END as rentabilidad_promedio_porcentaje,
    ROUND(AVG(CASE 
        WHEN hp.costo_real_proy <= hp.presupuesto THEN 100
        ELSE 0
    END), 2) as porcentaje_cumplimiento_presupuesto,
    SUM(hp.horas_reales_total) as horas_reales_total,
    SUM(hp.horas_plan_total) as horas_estimadas_total,
    CASE 
        WHEN SUM(hp.horas_plan_total) > 0 
        THEN ROUND((SUM(hp.horas_reales_total) / SUM(hp.horas_plan_total) * 100), 2)
        ELSE 0 
    END as eficiencia_estimacion_porcentaje
FROM HechoProyecto hp
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto;

-- Verificar que las vistas se crearon correctamente
SELECT 'vw_olap_detallado' as vista, COUNT(*) as registros FROM vw_olap_detallado
UNION ALL
SELECT 'vw_olap_por_cliente', COUNT(*) FROM vw_olap_por_cliente
UNION ALL
SELECT 'vw_olap_por_equipo', COUNT(*) FROM vw_olap_por_equipo
UNION ALL
SELECT 'vw_olap_por_anio', COUNT(*) FROM vw_olap_por_anio
UNION ALL
SELECT 'vw_olap_total', 1 FROM vw_olap_total;
