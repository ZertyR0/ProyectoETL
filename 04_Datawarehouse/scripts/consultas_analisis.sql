-- =========================================================
-- CONSULTAS DE ANÁLISIS PARA EL DATAWAREHOUSE
-- Sistema de Business Intelligence - Proyectos
-- =========================================================

USE dw_proyectos_hist;

-- =========================================================
-- CONSULTAS DE VERIFICACIÓN
-- =========================================================

-- Verificar datos cargados
SELECT 'VERIFICACIÓN DE DATOS CARGADOS' as seccion;

SELECT 
    'DimCliente' as tabla, COUNT(*) as registros FROM DimCliente
UNION ALL
SELECT 
    'DimEmpleado' as tabla, COUNT(*) as registros FROM DimEmpleado
UNION ALL
SELECT 
    'DimEquipo' as tabla, COUNT(*) as registros FROM DimEquipo
UNION ALL
SELECT 
    'DimProyecto' as tabla, COUNT(*) as registros FROM DimProyecto
UNION ALL
SELECT 
    'DimTiempo' as tabla, COUNT(*) as registros FROM DimTiempo
UNION ALL
SELECT 
    'HechoProyecto' as tabla, COUNT(*) as registros FROM HechoProyecto
UNION ALL
SELECT 
    'HechoTarea' as tabla, COUNT(*) as registros FROM HechoTarea;

-- =========================================================
-- ANÁLISIS DE PROYECTOS
-- =========================================================

-- Top 10 proyectos por rentabilidad
SELECT 'TOP 10 PROYECTOS POR RENTABILIDAD' as seccion;

SELECT 
    dp.nombre_proyecto,
    dc.nombre as cliente,
    de.nombre as gerente,
    hp.presupuesto,
    hp.costo_real,
    hp.variacion_costos,
    ROUND((hp.variacion_costos / hp.presupuesto) * 100, 2) as porcentaje_variacion,
    CASE 
        WHEN hp.cumplimiento_presupuesto = 1 THEN 'En Presupuesto'
        ELSE 'Sobre Presupuesto'
    END as estado_presupuesto
FROM HechoProyecto hp
JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
WHERE hp.presupuesto > 0
ORDER BY hp.variacion_costos ASC
LIMIT 10;

-- Análisis de cumplimiento de tiempo
SELECT 'ANÁLISIS DE CUMPLIMIENTO DE TIEMPO' as seccion;

SELECT 
    YEAR(dt.fecha) as anio,
    MONTH(dt.fecha) as mes,
    dt.nombre_mes,
    COUNT(*) as proyectos_finalizados,
    SUM(hp.cumplimiento_tiempo) as proyectos_a_tiempo,
    ROUND((SUM(hp.cumplimiento_tiempo) / COUNT(*)) * 100, 2) as porcentaje_cumplimiento,
    AVG(hp.duracion_real) as duracion_promedio_dias,
    AVG(hp.variacion_cronograma) as retraso_promedio_dias
FROM HechoProyecto hp
JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
WHERE dt.fecha IS NOT NULL
GROUP BY YEAR(dt.fecha), MONTH(dt.fecha), dt.nombre_mes
ORDER BY anio DESC, mes DESC
LIMIT 12;

-- Top empleados por productividad
SELECT 'TOP EMPLEADOS POR PRODUCTIVIDAD' as seccion;

SELECT 
    de.nombre as empleado,
    de.puesto,
    de.departamento,
    COUNT(hp.id_proyecto) as proyectos_gestionados,
    AVG(hp.porcentaje_completado) as completado_promedio,
    SUM(hp.cumplimiento_tiempo) as proyectos_a_tiempo,
    SUM(hp.cumplimiento_presupuesto) as proyectos_en_presupuesto,
    AVG(hp.eficiencia_horas) as eficiencia_promedio
FROM HechoProyecto hp
JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
GROUP BY de.id_empleado, de.nombre, de.puesto, de.departamento
HAVING COUNT(hp.id_proyecto) >= 2
ORDER BY 
    proyectos_a_tiempo DESC,
    proyectos_en_presupuesto DESC,
    eficiencia_promedio DESC
LIMIT 10;

-- =========================================================
-- ANÁLISIS DE TAREAS
-- =========================================================

-- Eficiencia por empleado en tareas
SELECT 'EFICIENCIA POR EMPLEADO EN TAREAS' as seccion;

SELECT 
    de.nombre as empleado,
    de.puesto,
    COUNT(ht.id_tarea) as tareas_realizadas,
    AVG(ht.horas_plan) as horas_plan_promedio,
    AVG(ht.horas_reales) as horas_reales_promedio,
    AVG(ht.eficiencia_horas) as eficiencia_promedio,
    SUM(ht.cumplimiento_tiempo) as tareas_a_tiempo,
    ROUND((SUM(ht.cumplimiento_tiempo) / COUNT(ht.id_tarea)) * 100, 2) as porcentaje_puntualidad
FROM HechoTarea ht
JOIN DimEmpleado de ON ht.id_empleado = de.id_empleado
GROUP BY de.id_empleado, de.nombre, de.puesto
HAVING COUNT(ht.id_tarea) >= 3
ORDER BY eficiencia_promedio DESC, porcentaje_puntualidad DESC
LIMIT 15;

-- =========================================================
-- ANÁLISIS TEMPORAL
-- =========================================================

-- Tendencias por trimestre
SELECT 'TENDENCIAS POR TRIMESTRE' as seccion;

SELECT 
    dt.anio,
    dt.trimestre,
    COUNT(DISTINCT hp.id_proyecto) as proyectos_finalizados,
    AVG(hp.presupuesto) as presupuesto_promedio,
    AVG(hp.costo_real) as costo_real_promedio,
    AVG(hp.duracion_real) as duracion_promedio,
    ROUND(AVG(hp.porcentaje_completado), 2) as completado_promedio,
    ROUND((SUM(hp.cumplimiento_tiempo) / COUNT(*)) * 100, 2) as cumplimiento_tiempo_pct,
    ROUND((SUM(hp.cumplimiento_presupuesto) / COUNT(*)) * 100, 2) as cumplimiento_presupuesto_pct
FROM HechoProyecto hp
JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
WHERE dt.fecha IS NOT NULL
GROUP BY dt.anio, dt.trimestre
ORDER BY dt.anio DESC, dt.trimestre DESC;

-- =========================================================
-- ANÁLISIS POR CLIENTE
-- =========================================================

-- Métricas por cliente
SELECT 'MÉTRICAS POR CLIENTE' as seccion;

SELECT 
    dc.nombre as cliente,
    dc.sector,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_total,
    AVG(hp.porcentaje_completado) as completado_promedio,
    SUM(hp.cumplimiento_tiempo) as proyectos_a_tiempo,
    SUM(hp.cumplimiento_presupuesto) as proyectos_en_presupuesto,
    ROUND((SUM(hp.cumplimiento_tiempo) / COUNT(*)) * 100, 2) as pct_tiempo,
    ROUND((SUM(hp.cumplimiento_presupuesto) / COUNT(*)) * 100, 2) as pct_presupuesto
FROM HechoProyecto hp
JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
GROUP BY dc.id_cliente, dc.nombre, dc.sector
ORDER BY total_proyectos DESC, presupuesto_total DESC;

-- =========================================================
-- MÉTRICAS EJECUTIVAS
-- =========================================================

-- Dashboard ejecutivo
SELECT 'DASHBOARD EJECUTIVO' as seccion;

SELECT 
    'Resumen General' as metrica,
    CONCAT(COUNT(DISTINCT hp.id_proyecto), ' proyectos') as valor
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Presupuesto Total',
    CONCAT('$', FORMAT(SUM(hp.presupuesto), 0))
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Costo Real Total',
    CONCAT('$', FORMAT(SUM(hp.costo_real), 0))
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Proyectos a Tiempo',
    CONCAT(ROUND((SUM(hp.cumplimiento_tiempo) / COUNT(*)) * 100, 1), '%')
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Proyectos en Presupuesto',
    CONCAT(ROUND((SUM(hp.cumplimiento_presupuesto) / COUNT(*)) * 100, 1), '%')
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Eficiencia Promedio',
    CONCAT(ROUND(AVG(hp.eficiencia_horas), 1), '%')
FROM HechoProyecto hp
UNION ALL
SELECT 
    'Duración Promedio',
    CONCAT(ROUND(AVG(hp.duracion_real), 0), ' días')
FROM HechoProyecto hp;

-- =========================================================
-- ALERTAS Y PROBLEMAS
-- =========================================================

-- Proyectos con problemas
SELECT 'PROYECTOS CON PROBLEMAS' as seccion;

SELECT 
    dp.nombre_proyecto,
    dc.nombre as cliente,
    de.nombre as gerente,
    CASE 
        WHEN hp.cumplimiento_tiempo = 0 AND hp.cumplimiento_presupuesto = 0 THEN 'Tiempo y Presupuesto'
        WHEN hp.cumplimiento_tiempo = 0 THEN 'Tiempo'
        WHEN hp.cumplimiento_presupuesto = 0 THEN 'Presupuesto'
        ELSE 'Sin Problemas'
    END as problemas,
    hp.variacion_cronograma as dias_retraso,
    hp.variacion_costos as sobrecosto,
    hp.porcentaje_completado
FROM HechoProyecto hp
JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
WHERE hp.cumplimiento_tiempo = 0 OR hp.cumplimiento_presupuesto = 0
ORDER BY hp.variacion_costos DESC;

-- =========================================================
-- ANÁLISIS DE PRODUCTIVIDAD
-- =========================================================

-- Productividad por departamento
SELECT 'PRODUCTIVIDAD POR DEPARTAMENTO' as seccion;

SELECT 
    de.departamento,
    COUNT(DISTINCT de.id_empleado) as empleados,
    COUNT(ht.id_tarea) as tareas_totales,
    ROUND(COUNT(ht.id_tarea) / COUNT(DISTINCT de.id_empleado), 2) as tareas_por_empleado,
    AVG(ht.eficiencia_horas) as eficiencia_promedio,
    ROUND((SUM(ht.cumplimiento_tiempo) / COUNT(ht.id_tarea)) * 100, 2) as pct_puntualidad
FROM HechoTarea ht
JOIN DimEmpleado de ON ht.id_empleado = de.id_empleado
WHERE de.departamento IS NOT NULL
GROUP BY de.departamento
ORDER BY eficiencia_promedio DESC;

SELECT '========================================' as fin_consultas;
