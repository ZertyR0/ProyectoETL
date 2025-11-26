-- =============================================================================
-- MEJORAS BSC Y OLAP - Proyecto Final Inteligencia de Negocios
-- =============================================================================
-- Autor: Sistema ETL
-- Fecha: Noviembre 2025
-- Propósito: 
--   1. Integrar BSC con datos reales desde HechoProyecto
--   2. Implementar OLAP ROLLUP para agregaciones jerárquicas
-- =============================================================================

USE dw_proyectos_hist;

-- =============================================================================
-- 1. OLAP CON ROLLUP
-- =============================================================================

DROP VIEW IF EXISTS vw_olap_proyectos_rollup;

CREATE VIEW vw_olap_proyectos_rollup AS
SELECT 
    c.nombre as cliente,
    CASE 
        WHEN eq.nombre_equipo IS NULL THEN 'TOTAL POR CLIENTE'
        ELSE eq.nombre_equipo
    END as equipo,
    COUNT(h.id_proyecto) as total_proyectos,
    SUM(h.presupuesto) as presupuesto_total,
    SUM(h.costo_real_proy) as costo_real_total,
    AVG(h.variacion_costos) as variacion_presupuesto_promedio,
    SUM(h.tareas_completadas) as tareas_completadas_total,
    AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) as cumplimiento_tareas_promedio,
    AVG(h.variacion_cronograma) as dias_diferencia_promedio
FROM HechoProyecto h
JOIN DimCliente c ON h.id_cliente = c.id_cliente
JOIN DimEquipo eq ON h.id_equipo = eq.id_equipo
WHERE h.tareas_total > 0 AND h.presupuesto > 0
GROUP BY c.nombre, eq.nombre_equipo WITH ROLLUP
HAVING cliente IS NOT NULL;

-- =============================================================================
-- 2. BSC PERSPECTIVA FINANCIERA
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_financiera;

CREATE VIEW vw_bsc_financiera AS
SELECT 
    codigo_objetivo, objetivo_nombre, objetivo_descripcion, perspectiva, vision_componente,
    owner_responsable, peso_ponderacion, total_krs,
    kr1_valor_observado, kr1_progreso, kr2_valor_observado, kr2_progreso, kr3_valor_observado, kr3_progreso,
    krs_en_meta,
    ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) as avance_objetivo_porcentaje,
    CASE 
        WHEN ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) >= 85 THEN 'Verde'
        WHEN ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) >= 70 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    ultima_actualizacion
FROM (
    SELECT 
        'FIN-001' as codigo_objetivo,
        'Maximizar Rentabilidad de Proyectos' as objetivo_nombre,
        'Aumentar margen de ganancia y control de costos' as objetivo_descripcion,
        'Financiera' as perspectiva,
        'Crecimiento y Rentabilidad' as vision_componente,
        'CFO' as owner_responsable,
        3.0 as peso_ponderacion,
        3 as total_krs,
        
        -- KR1: % Proyectos en Presupuesto
        ROUND(SUM(h.cumplimiento_presupuesto) * 100.0 / COUNT(*), 1) as kr1_valor_observado,
        ROUND(LEAST(100, GREATEST(0, (SUM(h.cumplimiento_presupuesto) * 100.0 / COUNT(*)) / 80.0 * 100)), 1) as kr1_progreso,
        
        -- KR2: Variación Presupuesto Promedio (en miles de dólares)
        ROUND(AVG(ABS(h.variacion_costos)) / 1000, 1) as kr2_valor_observado,
        ROUND(LEAST(100, GREATEST(0,
            CASE 
                WHEN AVG(ABS(h.variacion_costos)) / 1000 <= 10 THEN 100
                WHEN AVG(ABS(h.variacion_costos)) / 1000 >= 100 THEN 0
                ELSE ((100 - AVG(ABS(h.variacion_costos)) / 1000) / 90.0) * 100
            END
        )), 1) as kr2_progreso,
        
        -- KR3: Rentabilidad Promedio
        ROUND(AVG((h.presupuesto - h.costo_real_proy) / NULLIF(h.presupuesto, 0) * 100), 1) as kr3_valor_observado,
        ROUND(LEAST(100, GREATEST(0, AVG((h.presupuesto - h.costo_real_proy) / NULLIF(h.presupuesto, 0) * 100) / 15.0 * 100)), 1) as kr3_progreso,
        
        0 as krs_en_meta,
        CURDATE() as ultima_actualizacion
    FROM HechoProyecto h
    WHERE h.presupuesto > 0 AND h.tareas_total > 0
) AS base;

-- =============================================================================
-- 3. BSC PERSPECTIVA CLIENTES
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_clientes;

CREATE VIEW vw_bsc_clientes AS
SELECT 
    'CLI-001' as codigo_objetivo,
    'Aumentar Satisfacción de Clientes' as objetivo_nombre,
    'Mejorar entregas a tiempo y calidad' as objetivo_descripcion,
    'Clientes' as perspectiva,
    'Propuesta de Valor' as vision_componente,
    'Gerente General' as owner_responsable,
    2.5 as peso_ponderacion,
    2 as total_krs,
    
    -- KR1: % Tareas Completadas
    ROUND(AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)), 1) as kr1_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100
        )),
        1
    ) as kr1_progreso,
    
    -- KR2: Retraso Promedio
    ROUND(
        AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END),
        1
    ) as kr2_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            CASE 
                WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END) <= 5 THEN 100
                WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END) >= 7.5 THEN 0
                ELSE ((7.5 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END)) / 2.5) * 100
            END
        )),
        1
    ) as kr2_progreso,
    
    0 as krs_en_meta,
    
    ROUND(
        (LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
         LEAST(100, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END) <= 5 THEN 100 ELSE ((7.5 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END)) / 2.5) * 100 END) * 0.9) / 1.9,
        1
    ) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
                    LEAST(100, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END) <= 5 THEN 100 ELSE ((7.5 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END)) / 2.5) * 100 END) * 0.9) / 1.9, 1) >= 85 THEN 'Verde'
        WHEN ROUND((LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
                    LEAST(100, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END) <= 5 THEN 100 ELSE ((7.5 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma END)) / 2.5) * 100 END) * 0.9) / 1.9, 1) >= 70 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    CURDATE() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.presupuesto > 0 AND h.tareas_total > 0;

-- =============================================================================
-- 4. BSC PERSPECTIVA PROCESOS INTERNOS
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_procesos;

CREATE VIEW vw_bsc_procesos AS
SELECT 
    'PROC-001' as codigo_objetivo,
    'Mejorar Eficiencia Operativa' as objetivo_nombre,
    'Optimizar procesos internos de ejecución' as objetivo_descripcion,
    'Procesos Internos' as perspectiva,
    'Excelencia Operacional' as vision_componente,
    'Director Operaciones' as owner_responsable,
    2.8 as peso_ponderacion,
    3 as total_krs,
    
    -- KR1: % Proyectos a Tiempo
    ROUND(
        SUM(h.cumplimiento_tiempo) * 100.0 / COUNT(*),
        1
    ) as kr1_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            (SUM(h.cumplimiento_tiempo) * 100.0 / COUNT(*)) / 85.0 * 100
        )),
        1
    ) as kr1_progreso,
    
    -- KR2: % Cumplimiento Tareas
    ROUND(AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)), 1) as kr2_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100
        )),
        1
    ) as kr2_progreso,
    
    -- KR3: Duración Promedio
    ROUND(AVG(h.duracion_real), 1) as kr3_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            CASE 
                WHEN AVG(h.duracion_real) <= 60 THEN 100
                WHEN AVG(h.duracion_real) >= 72 THEN 0
                ELSE ((72 - AVG(h.duracion_real)) / 12.0) * 100
            END
        )),
        1
    ) as kr3_progreso,
    
    0 as krs_en_meta,
    
    ROUND(
        (LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / COUNT(*)) / 85.0 * 100) * 1.0 +
         LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
         LEAST(100, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((72 - AVG(h.duracion_real)) / 12.0) * 100 END) * 0.8) / 2.8,
        1
    ) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / COUNT(*)) / 85.0 * 100) * 1.0 +
                    LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
                    LEAST(100, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((72 - AVG(h.duracion_real)) / 12.0) * 100 END) * 0.8) / 2.8, 1) >= 85 THEN 'Verde'
        WHEN ROUND((LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / COUNT(*)) / 85.0 * 100) * 1.0 +
                    LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 1.0 +
                    LEAST(100, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((72 - AVG(h.duracion_real)) / 12.0) * 100 END) * 0.8) / 2.8, 1) >= 70 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    CURDATE() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.presupuesto > 0 AND h.tareas_total > 0;

-- =============================================================================
-- 5. BSC PERSPECTIVA APRENDIZAJE E INNOVACIÓN
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_aprendizaje;

CREATE VIEW vw_bsc_aprendizaje AS
SELECT 
    'APRE-001' as codigo_objetivo,
    'Desarrollar Capacidades del Equipo' as objetivo_nombre,
    'Mejorar eficiencia y participación' as objetivo_descripcion,
    'Aprendizaje y Innovación' as perspectiva,
    'Desarrollo de Talento' as vision_componente,
    'Director RR.HH.' as owner_responsable,
    1.9 as peso_ponderacion,
    2 as total_krs,
    
    -- KR1: Eficiencia en Horas
    ROUND(AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)), 1) as kr1_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            CASE 
                WHEN AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)) <= 15 THEN 100
                WHEN AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)) >= 18 THEN 0
                ELSE ((18 - AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0))) / 3.0) * 100
            END
        )),
        1
    ) as kr1_progreso,
    
    -- KR2: % Empleados Activos
    ROUND(
        (COUNT(DISTINCT h.id_empleado_gerente) * 100.0 / 
         (SELECT COUNT(*) FROM DimEmpleado)),
        1
    ) as kr2_valor_observado,
    ROUND(
        LEAST(100, GREATEST(0,
            (COUNT(DISTINCT h.id_empleado_gerente) * 100.0 / 
             (SELECT COUNT(*) FROM DimEmpleado)) / 80.0 * 100
        )),
        1
    ) as kr2_progreso,
    
    0 as krs_en_meta,
    
    ROUND(
        (LEAST(100, CASE WHEN AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((18 - AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0))) / 3.0) * 100 END) * 1.0 +
         LEAST(100, (COUNT(DISTINCT h.id_empleado_gerente) * 100.0 / (SELECT COUNT(*) FROM DimEmpleado)) / 80.0 * 100) * 0.9) / 1.9,
        1
    ) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((LEAST(100, CASE WHEN AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((18 - AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0))) / 3.0) * 100 END) * 1.0 +
                    LEAST(100, (COUNT(DISTINCT h.id_empleado_gerente) * 100.0 / (SELECT COUNT(*) FROM DimEmpleado)) / 80.0 * 100) * 0.9) / 1.9, 1) >= 85 THEN 'Verde'
        WHEN ROUND((LEAST(100, CASE WHEN AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((18 - AVG(h.horas_reales_total / NULLIF(h.tareas_total, 0))) / 3.0) * 100 END) * 1.0 +
                    LEAST(100, (COUNT(DISTINCT h.id_empleado_gerente) * 100.0 / (SELECT COUNT(*) FROM DimEmpleado)) / 80.0 * 100) * 0.9) / 1.9, 1) >= 70 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    CURDATE() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.presupuesto > 0 AND h.tareas_total > 0;

-- =============================================================================
-- 6. BSC TABLERO CONSOLIDADO
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_tablero_consolidado;

CREATE VIEW vw_bsc_tablero_consolidado AS
SELECT * FROM vw_bsc_financiera
UNION ALL
SELECT * FROM vw_bsc_clientes
UNION ALL
SELECT * FROM vw_bsc_procesos
UNION ALL
SELECT * FROM vw_bsc_aprendizaje;

-- =============================================================================
-- 7. BSC KRs DETALLE
-- =============================================================================

DROP VIEW IF EXISTS vw_bsc_krs_detalle;

CREATE VIEW vw_bsc_krs_detalle AS
-- Financiera KRs
SELECT 
    'FIN-001-KR1' as id_kr, 'FIN-001-KR1' as codigo_kr,
    '% Proyectos en Presupuesto' as kr_nombre,
    'Porcentaje de proyectos que se mantienen dentro del presupuesto (variación <= 5%)' as kr_descripcion,
    '%' as unidad_medida, 'Incrementar' as tipo_metrica,
    0 as valor_inicial, 80.0 as meta_objetivo, 80.0 as umbral_verde, 68.0 as umbral_amarillo, 1.0 as peso_kr,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr1_valor_observado as valor_observado, NULL as valor_anterior, NULL as variacion_absoluta,
    NULL as variacion_porcentual, kr1_progreso as progreso_hacia_meta,
    CASE WHEN kr1_progreso >= 100 THEN 'Verde' WHEN kr1_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END as estado_semaforo,
    CASE WHEN kr1_progreso >= 100 THEN TRUE ELSE FALSE END as cumple_meta,
    'Cálculo automático desde HechoProyecto' as comentario, ultima_actualizacion as fecha_medicion
FROM vw_bsc_financiera
UNION ALL
SELECT 
    'FIN-001-KR2', 'FIN-001-KR2', 'Variación Presupuesto Promedio',
    'Variación promedio del presupuesto en todos los proyectos',
    '%', 'Decrementar', 50, 10.0, 10.0, 13.0, 0.8,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr2_valor_observado, NULL, NULL, NULL, kr2_progreso,
    CASE WHEN kr2_progreso >= 100 THEN 'Verde' WHEN kr2_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr2_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_financiera
UNION ALL
SELECT 
    'FIN-001-KR3', 'FIN-001-KR3', 'Rentabilidad Promedio',
    'Rentabilidad promedio: (Presupuesto - Costo Real) / Presupuesto * 100',
    '%', 'Incrementar', 0, 15.0, 15.0, 12.0, 1.2,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr3_valor_observado, NULL, NULL, NULL, kr3_progreso,
    CASE WHEN kr3_progreso >= 100 THEN 'Verde' WHEN kr3_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr3_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_financiera

-- Clientes KRs
UNION ALL
SELECT 
    'CLI-001-KR1', 'CLI-001-KR1', '% Tareas Completadas',
    'Porcentaje de tareas completadas sobre total',
    '%', 'Incrementar', 0, 90.0, 90.0, 81.0, 1.0,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr1_valor_observado, NULL, NULL, NULL, kr1_progreso,
    CASE WHEN kr1_progreso >= 100 THEN 'Verde' WHEN kr1_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr1_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_clientes
UNION ALL
SELECT 
    'CLI-001-KR2', 'CLI-001-KR2', 'Retraso Promedio en Días',
    'Promedio de días de retraso en proyectos retrasados',
    'días', 'Decrementar', 30, 5.0, 5.0, 7.5, 0.9,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr2_valor_observado, NULL, NULL, NULL, kr2_progreso,
    CASE WHEN kr2_progreso >= 100 THEN 'Verde' WHEN kr2_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr2_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_clientes

-- Procesos KRs
UNION ALL
SELECT 
    'PROC-001-KR1', 'PROC-001-KR1', '% Proyectos a Tiempo',
    'Porcentaje de proyectos completados en plazo',
    '%', 'Incrementar', 0, 85.0, 85.0, 76.5, 1.0,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr1_valor_observado, NULL, NULL, NULL, kr1_progreso,
    CASE WHEN kr1_progreso >= 100 THEN 'Verde' WHEN kr1_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr1_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_procesos
UNION ALL
SELECT 
    'PROC-001-KR2', 'PROC-001-KR2', '% Cumplimiento Tareas',
    'Porcentaje de tareas completadas sobre total',
    '%', 'Incrementar', 0, 90.0, 90.0, 76.5, 1.0,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr2_valor_observado, NULL, NULL, NULL, kr2_progreso,
    CASE WHEN kr2_progreso >= 100 THEN 'Verde' WHEN kr2_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr2_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_procesos
UNION ALL
SELECT 
    'PROC-001-KR3', 'PROC-001-KR3', 'Duración Promedio Proyectos',
    'Duración promedio de proyectos en días',
    'días', 'Mantener', 90, 60.0, 60.0, 72.0, 0.8,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr3_valor_observado, NULL, NULL, NULL, kr3_progreso,
    CASE WHEN kr3_progreso >= 100 THEN 'Verde' WHEN kr3_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr3_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_procesos

-- Aprendizaje KRs
UNION ALL
SELECT 
    'APRE-001-KR1', 'APRE-001-KR1', 'Eficiencia en Horas',
    'Horas promedio por tarea (eficiencia)',
    'horas/tarea', 'Decrementar', 30, 15.0, 15.0, 18.0, 1.0,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr1_valor_observado, NULL, NULL, NULL, kr1_progreso,
    CASE WHEN kr1_progreso >= 100 THEN 'Verde' WHEN kr1_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr1_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_aprendizaje
UNION ALL
SELECT 
    'APRE-001-KR2', 'APRE-001-KR2', '% Empleados Activos',
    'Porcentaje de empleados participando activamente',
    '%', 'Incrementar', 0, 80.0, 80.0, 68.0, 0.9,
    codigo_objetivo, objetivo_nombre, perspectiva,
    kr2_valor_observado, NULL, NULL, NULL, kr2_progreso,
    CASE WHEN kr2_progreso >= 100 THEN 'Verde' WHEN kr2_progreso >= 70 THEN 'Amarillo' ELSE 'Rojo' END,
    CASE WHEN kr2_progreso >= 100 THEN TRUE ELSE FALSE END,
    'Cálculo automático desde HechoProyecto', ultima_actualizacion
FROM vw_bsc_aprendizaje;

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================

SELECT '=== VERIFICACIÓN DE VISTAS CREADAS ===' as mensaje;

SELECT 'vw_olap_proyectos_rollup' as vista, COUNT(*) as registros FROM vw_olap_proyectos_rollup
UNION ALL
SELECT 'vw_bsc_tablero_consolidado', COUNT(*) FROM vw_bsc_tablero_consolidado
UNION ALL
SELECT 'vw_bsc_krs_detalle', COUNT(*) FROM vw_bsc_krs_detalle;

SELECT '=== RESUMEN BSC POR PERSPECTIVA ===' as mensaje;
SELECT * FROM vw_bsc_tablero_consolidado ORDER BY perspectiva;
