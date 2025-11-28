#!/usr/bin/env python3
"""
Script para corregir vistas BSC en Railway
Reemplaza costo_real_proy por costo_real (nombre correcto de columna)
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv('/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/backend/.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST_DESTINO'),
    port=int(os.getenv('DB_PORT_DESTINO', '3306')),
    user=os.getenv('DB_USER_DESTINO'),
    password=os.getenv('DB_PASSWORD_DESTINO'),
    database=os.getenv('DB_NAME_DESTINO')
)

cursor = conn.cursor()

print("🔧 Corrigiendo vistas BSC...")

# Vista 1: BSC Financiera
print("1. Creando vw_bsc_financiera...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_financiera AS
SELECT 
    codigo_objetivo, objetivo_nombre, objetivo_descripcion, perspectiva, vision_componente,
    owner_responsable, peso_ponderacion, total_krs,
    kr1_codigo, kr1_nombre, kr1_unidad_medida, kr1_meta, kr1_valor_observado, kr1_progreso,
    kr2_codigo, kr2_nombre, kr2_unidad_medida, kr2_meta, kr2_valor_observado, kr2_progreso,
    kr3_codigo, kr3_nombre, kr3_unidad_medida, kr3_meta, kr3_valor_observado, kr3_progreso,
    krs_en_meta,
    ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) as avance_objetivo_porcentaje,
    CASE 
        WHEN ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) >= 70 THEN 'Verde'
        WHEN ROUND((kr1_progreso * 1.0 + kr2_progreso * 0.8 + kr3_progreso * 1.2) / 3.0, 1) >= 50 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    ultima_actualizacion
FROM (
    SELECT 
        'F1' as codigo_objetivo,
        'Maximizar Rentabilidad' as objetivo_nombre,
        'Aumentar margen de ganancia y control de costos en proyectos' as objetivo_descripcion,
    'Financiera' as perspectiva,
        'Crecimiento Rentable' as vision_componente,
        'CFO' as owner_responsable,
        30.0 as peso_ponderacion,
        3 as total_krs,
        
        -- KR1: % Proyectos en Presupuesto
        'F1.1' as kr1_codigo,
        '% Proyectos en Presupuesto' as kr1_nombre,
        '%' as kr1_unidad_medida,
        80.0 as kr1_meta,
        ROUND(SUM(h.cumplimiento_presupuesto) * 100.0 / NULLIF(COUNT(*), 0), 1) as kr1_valor_observado,
        ROUND(LEAST(100, (SUM(h.cumplimiento_presupuesto) * 100.0 / NULLIF(COUNT(*), 0)) / 80.0 * 100), 1) as kr1_progreso,
        
        -- KR2: Variación Presupuesto (en miles)
        'F1.2' as kr2_codigo,
        'Variación Presupuesto' as kr2_nombre,
        'K$' as kr2_unidad_medida,
        10.0 as kr2_meta,
        ROUND(AVG(ABS(h.variacion_costos)) / 1000, 1) as kr2_valor_observado,
        ROUND(LEAST(100, GREATEST(0,
            CASE 
                WHEN AVG(ABS(h.variacion_costos)) / 1000 <= 10 THEN 100
                WHEN AVG(ABS(h.variacion_costos)) / 1000 >= 50 THEN 0
                ELSE ((50 - AVG(ABS(h.variacion_costos)) / 1000) / 40.0) * 100
            END
        )), 1) as kr2_progreso,
        
        -- KR3: Margen de Rentabilidad
        'F1.3' as kr3_codigo,
        'Margen de Rentabilidad' as kr3_nombre,
        '%' as kr3_unidad_medida,
        15.0 as kr3_meta,
        ROUND(AVG((h.presupuesto - h.costo_real) / NULLIF(h.presupuesto, 0) * 100), 1) as kr3_valor_observado,
        ROUND(LEAST(100, AVG((h.presupuesto - h.costo_real) / NULLIF(h.presupuesto, 0) * 100) / 15.0 * 100), 1) as kr3_progreso,
        
        0 as krs_en_meta,
        NOW() as ultima_actualizacion
    FROM HechoProyecto h
    WHERE h.presupuesto > 0
) AS base
""")
print("✓ vw_bsc_financiera creada")

# Vista 2: BSC Clientes
print("2. Creando vw_bsc_clientes...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_clientes AS
SELECT 
    'C1' as codigo_objetivo,
    'Satisfacción del Cliente' as objetivo_nombre,
    'Mejorar entregas a tiempo y calidad del servicio' as objetivo_descripcion,
    'Clientes' as perspectiva,
    'Propuesta de Valor' as vision_componente,
    'Director Comercial' as owner_responsable,
    25.0 as peso_ponderacion,
    2 as total_krs,
    
    -- KR1: % Cumplimiento de Tareas
    'C1.1' as kr1_codigo,
    '% Cumplimiento Tareas' as kr1_nombre,
    '%' as kr1_unidad_medida,
    90.0 as kr1_meta,
    ROUND(AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)), 1) as kr1_valor_observado,
    ROUND(LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100), 1) as kr1_progreso,
    
    -- KR2: Días de Retraso
    'C1.2' as kr2_codigo,
    'Días Retraso Promedio' as kr2_nombre,
    'días' as kr2_unidad_medida,
    5.0 as kr2_meta,
    ROUND(AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END), 1) as kr2_valor_observado,
    ROUND(LEAST(100, GREATEST(0,
        CASE 
            WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END) <= 5 THEN 100
            WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END) >= 15 THEN 0
            ELSE ((15 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END)) / 10.0) * 100
        END
    )), 1) as kr2_progreso,
    
    -- KR3: NULL (para igualar columnas)
    NULL as kr3_codigo,
    NULL as kr3_nombre,
    NULL as kr3_unidad_medida,
    NULL as kr3_meta,
    NULL as kr3_valor_observado,
    NULL as kr3_progreso,
    
    0 as krs_en_meta,
    
    ROUND((
        LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 0.6 +
        LEAST(100, GREATEST(0, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END) <= 5 THEN 100 ELSE ((15 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END)) / 10.0) * 100 END)) * 0.4
    ), 1) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((
            LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 0.6 +
            LEAST(100, GREATEST(0, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END) <= 5 THEN 100 ELSE ((15 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END)) / 10.0) * 100 END)) * 0.4
        ), 1) >= 70 THEN 'Verde'
        WHEN ROUND((
            LEAST(100, AVG(h.tareas_completadas * 100.0 / NULLIF(h.tareas_total, 0)) / 90.0 * 100) * 0.6 +
            LEAST(100, GREATEST(0, CASE WHEN AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END) <= 5 THEN 100 ELSE ((15 - AVG(CASE WHEN h.variacion_cronograma > 0 THEN h.variacion_cronograma ELSE 0 END)) / 10.0) * 100 END)) * 0.4
        ), 1) >= 50 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    NOW() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.tareas_total > 0
""")
print("✓ vw_bsc_clientes creada")

# Vista 3: BSC Procesos
print("3. Creando vw_bsc_procesos...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_procesos AS
SELECT 
    'P1' as codigo_objetivo,
    'Eficiencia Operativa' as objetivo_nombre,
    'Optimizar procesos de ejecución de proyectos' as objetivo_descripcion,
    'Procesos Internos' as perspectiva,
    'Excelencia Operacional' as vision_componente,
    'Director de Operaciones' as owner_responsable,
    25.0 as peso_ponderacion,
    2 as total_krs,
    
    -- KR1: % Proyectos a Tiempo
    'P1.1' as kr1_codigo,
    '% Proyectos a Tiempo' as kr1_nombre,
    '%' as kr1_unidad_medida,
    85.0 as kr1_meta,
    ROUND(SUM(h.cumplimiento_tiempo) * 100.0 / NULLIF(COUNT(*), 0), 1) as kr1_valor_observado,
    ROUND(LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / NULLIF(COUNT(*), 0)) / 85.0 * 100), 1) as kr1_progreso,
    
    -- KR2: Duración Promedio
    'P1.2' as kr2_codigo,
    'Duración Promedio Proyectos' as kr2_nombre,
    'días' as kr2_unidad_medida,
    60.0 as kr2_meta,
    ROUND(AVG(h.duracion_real), 1) as kr2_valor_observado,
    ROUND(LEAST(100, GREATEST(0,
        CASE 
            WHEN AVG(h.duracion_real) <= 60 THEN 100
            WHEN AVG(h.duracion_real) >= 90 THEN 0
            ELSE ((90 - AVG(h.duracion_real)) / 30.0) * 100
        END
    )), 1) as kr2_progreso,
    
    -- KR3: NULL (para igualar columnas)
    NULL as kr3_codigo,
    NULL as kr3_nombre,
    NULL as kr3_unidad_medida,
    NULL as kr3_meta,
    NULL as kr3_valor_observado,
    NULL as kr3_progreso,
    
    0 as krs_en_meta,
    
    ROUND((
        LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / NULLIF(COUNT(*), 0)) / 85.0 * 100) * 0.6 +
        LEAST(100, GREATEST(0, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((90 - AVG(h.duracion_real)) / 30.0) * 100 END)) * 0.4
    ), 1) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((
            LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / NULLIF(COUNT(*), 0)) / 85.0 * 100) * 0.6 +
            LEAST(100, GREATEST(0, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((90 - AVG(h.duracion_real)) / 30.0) * 100 END)) * 0.4
        ), 1) >= 70 THEN 'Verde'
        WHEN ROUND((
            LEAST(100, (SUM(h.cumplimiento_tiempo) * 100.0 / NULLIF(COUNT(*), 0)) / 85.0 * 100) * 0.6 +
            LEAST(100, GREATEST(0, CASE WHEN AVG(h.duracion_real) <= 60 THEN 100 ELSE ((90 - AVG(h.duracion_real)) / 30.0) * 100 END)) * 0.4
        ), 1) >= 50 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    NOW() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.duracion_real > 0
""")
print("✓ vw_bsc_procesos creada")

# Vista 4: BSC Aprendizaje
print("4. Creando vw_bsc_aprendizaje...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_aprendizaje AS
SELECT 
    'A1' as codigo_objetivo,
    'Desarrollo del Talento' as objetivo_nombre,
    'Mejorar capacidades y eficiencia del equipo' as objetivo_descripcion,
    'Aprendizaje y Innovación' as perspectiva,
    'Capital Humano' as vision_componente,
    'Director de RRHH' as owner_responsable,
    20.0 as peso_ponderacion,
    2 as total_krs,
    
    -- KR1: Horas Promedio por Tarea (fallback a horas_plan si horas_reales=0)
    'A1.1' as kr1_codigo,
    'Horas Promedio por Tarea' as kr1_nombre,
    'hrs' as kr1_unidad_medida,
    15.0 as kr1_meta,
    ROUND(AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)), 1) as kr1_valor_observado,
    ROUND(LEAST(100, GREATEST(0,
        CASE 
            WHEN AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)) <= 15 THEN 100
            WHEN AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)) >= 25 THEN 0
            ELSE ((25 - AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0))) / 10.0) * 100
        END
    )), 1) as kr1_progreso,
    
    -- KR2: % Empleados Activos
    'A1.2' as kr2_codigo,
    '% Empleados Activos' as kr2_nombre,
    '%' as kr2_unidad_medida,
    80.0 as kr2_meta,
    ROUND((SELECT SUM(activo) * 100.0 / NULLIF(COUNT(*), 0) FROM DimEmpleado), 1) as kr2_valor_observado,
    ROUND(LEAST(100, (SELECT SUM(activo) * 100.0 / NULLIF(COUNT(*), 0) FROM DimEmpleado) / 80.0 * 100), 1) as kr2_progreso,
    
    -- KR3: NULL (para igualar columnas)
    NULL as kr3_codigo,
    NULL as kr3_nombre,
    NULL as kr3_unidad_medida,
    NULL as kr3_meta,
    NULL as kr3_valor_observado,
    NULL as kr3_progreso,
    
    0 as krs_en_meta,
    
    ROUND((
        LEAST(100, GREATEST(0, CASE WHEN AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((25 - AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0))) / 10.0) * 100 END)) * 0.5 +
        LEAST(100, (SELECT SUM(activo) * 100.0 / NULLIF(COUNT(*), 0) FROM DimEmpleado) / 80.0 * 100) * 0.5
    ), 1) as avance_objetivo_porcentaje,
    
    CASE 
        WHEN ROUND((
            LEAST(100, GREATEST(0, CASE WHEN AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((25 - AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0))) / 10.0) * 100 END)) * 0.5 +
            LEAST(100, (SELECT SUM(activo) * 100.0 / NULLIF(COUNT(*), 0) FROM DimEmpleado) / 80.0 * 100) * 0.5
        ), 1) >= 70 THEN 'Verde'
        WHEN ROUND((
            LEAST(100, GREATEST(0, CASE WHEN AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0)) <= 15 THEN 100 ELSE ((25 - AVG((CASE WHEN h.horas_reales_total > 0 THEN h.horas_reales_total ELSE h.horas_estimadas_total END) / NULLIF(h.tareas_total, 0))) / 10.0) * 100 END)) * 0.5 +
            LEAST(100, (SELECT SUM(activo) * 100.0 / NULLIF(COUNT(*), 0) FROM DimEmpleado) / 80.0 * 100) * 0.5
        ), 1) >= 50 THEN 'Amarillo'
        ELSE 'Rojo'
    END as estado_objetivo,
    
    NOW() as ultima_actualizacion
FROM HechoProyecto h
WHERE h.tareas_total > 0
""")
print("✓ vw_bsc_aprendizaje creada")

# Vista 5: BSC Tablero Consolidado
print("5. Creando vw_bsc_tablero_consolidado...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_tablero_consolidado AS
SELECT * FROM vw_bsc_financiera
UNION ALL
SELECT * FROM vw_bsc_clientes
UNION ALL
SELECT * FROM vw_bsc_procesos
UNION ALL
SELECT * FROM vw_bsc_aprendizaje
""")
print("✓ vw_bsc_tablero_consolidado creada")

# Vista 6: BSC KRs Detalle (unpivot desde tablero consolidado)
print("6. Creando vw_bsc_krs_detalle...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_bsc_krs_detalle AS
SELECT 
    t.perspectiva,
    t.codigo_objetivo,
    t.objetivo_nombre,
    t.objetivo_descripcion,
    t.vision_componente,
    t.owner_responsable,
    kr.codigo_kr,
    kr.kr_nombre,
    kr.unidad_medida,
    kr.meta_objetivo,
    kr.valor_observado,
    kr.progreso_hacia_meta,
    CASE 
        WHEN kr.progreso_hacia_meta >= 70 THEN 'Verde'
        WHEN kr.progreso_hacia_meta >= 50 THEN 'Amarillo'
        ELSE 'Rojo'
    END AS estado_semaforo
FROM vw_bsc_tablero_consolidado t
JOIN (
    SELECT 
        codigo_objetivo,
        kr1_codigo AS codigo_kr,
        kr1_nombre AS kr_nombre,
        kr1_unidad_medida AS unidad_medida,
        kr1_meta AS meta_objetivo,
        kr1_valor_observado AS valor_observado,
        kr1_progreso AS progreso_hacia_meta
    FROM vw_bsc_tablero_consolidado WHERE kr1_codigo IS NOT NULL
    UNION ALL
    SELECT 
        codigo_objetivo,
        kr2_codigo AS codigo_kr,
        kr2_nombre AS kr_nombre,
        kr2_unidad_medida AS unidad_medida,
        kr2_meta AS meta_objetivo,
        kr2_valor_observado AS valor_observado,
        kr2_progreso AS progreso_hacia_meta
    FROM vw_bsc_tablero_consolidado WHERE kr2_codigo IS NOT NULL
    UNION ALL
    SELECT 
        codigo_objetivo,
        kr3_codigo AS codigo_kr,
        kr3_nombre AS kr_nombre,
        kr3_unidad_medida AS unidad_medida,
        kr3_meta AS meta_objetivo,
        kr3_valor_observado AS valor_observado,
        kr3_progreso AS progreso_hacia_meta
    FROM vw_bsc_tablero_consolidado WHERE kr3_codigo IS NOT NULL
) kr ON kr.codigo_objetivo = t.codigo_objetivo
""")
print("✓ vw_bsc_krs_detalle creada")

conn.commit()
cursor.close()
conn.close()

print("\n✅ ¡Todas las vistas BSC corregidas exitosamente!")
print("🔄 Recarga el dashboard para ver los cambios")
