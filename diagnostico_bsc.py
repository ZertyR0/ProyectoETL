#!/usr/bin/env python3
"""
Script de diagnóstico para verificar datos en vistas BSC
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

cursor = conn.cursor(dictionary=True)

print("🔍 DIAGNÓSTICO DE DATOS BSC\n")

# 1. Verificar datos en HechoProyecto
print("=" * 60)
print("1. DATOS EN HechoProyecto:")
print("=" * 60)
cursor.execute("""
    SELECT 
        COUNT(*) as total_registros,
        COUNT(DISTINCT id_cliente) as clientes,
        COUNT(DISTINCT id_empleado_gerente) as gerentes,
        SUM(CASE WHEN presupuesto > 0 THEN 1 ELSE 0 END) as con_presupuesto,
        SUM(CASE WHEN tareas_total > 0 THEN 1 ELSE 0 END) as con_tareas,
        SUM(cumplimiento_presupuesto) as cumple_presupuesto,
        SUM(cumplimiento_tiempo) as cumple_tiempo,
        AVG(presupuesto) as presupuesto_promedio,
        AVG(costo_real) as costo_real_promedio
    FROM HechoProyecto
""")
datos = cursor.fetchone()
for key, value in datos.items():
    print(f"  {key}: {value}")

# 2. Ver algunos registros de HechoProyecto
print("\n" + "=" * 60)
print("2. MUESTRA DE DATOS EN HechoProyecto:")
print("=" * 60)
cursor.execute("""
    SELECT 
        id_proyecto,
        presupuesto,
        costo_real,
        tareas_total,
        tareas_completadas,
        cumplimiento_presupuesto,
        cumplimiento_tiempo,
        duracion_real,
        horas_reales_total
    FROM HechoProyecto
    LIMIT 5
""")
proyectos = cursor.fetchall()
for p in proyectos:
    print(f"\nProyecto {p['id_proyecto']}:")
    for key, value in p.items():
        print(f"  {key}: {value}")

# 3. Probar consulta de vista BSC Financiera directamente
print("\n" + "=" * 60)
print("3. CONSULTA DIRECTA PARA BSC FINANCIERA:")
print("=" * 60)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(cumplimiento_presupuesto) as cumple_pres,
        AVG(ABS(variacion_costos)) as var_costos,
        AVG((presupuesto - costo_real) / NULLIF(presupuesto, 0) * 100) as margen
    FROM HechoProyecto
    WHERE presupuesto > 0
""")
result = cursor.fetchone()
print(f"  Total proyectos con presupuesto: {result['total']}")
print(f"  Cumplen presupuesto: {result['cumple_pres']}")
print(f"  Variación costos promedio: {result['var_costos']}")
print(f"  Margen promedio: {result['margen']}%")

# 4. Verificar vista BSC Financiera
print("\n" + "=" * 60)
print("4. VISTA vw_bsc_financiera:")
print("=" * 60)
try:
    cursor.execute("SELECT * FROM vw_bsc_financiera")
    bsc_fin = cursor.fetchone()
    if bsc_fin:
        print(f"  Objetivo: {bsc_fin['objetivo_nombre']}")
        print(f"  KR1 ({bsc_fin['kr1_nombre']}): {bsc_fin['kr1_valor_observado']} (Progreso: {bsc_fin['kr1_progreso']}%)")
        print(f"  KR2 ({bsc_fin['kr2_nombre']}): {bsc_fin['kr2_valor_observado']} (Progreso: {bsc_fin['kr2_progreso']}%)")
        print(f"  KR3 ({bsc_fin['kr3_nombre']}): {bsc_fin['kr3_valor_observado']} (Progreso: {bsc_fin['kr3_progreso']}%)")
        print(f"  Avance Global: {bsc_fin['avance_objetivo_porcentaje']}%")
        print(f"  Estado: {bsc_fin['estado_objetivo']}")
    else:
        print("  ⚠️  Vista sin datos")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 5. Verificar vista BSC Clientes
print("\n" + "=" * 60)
print("5. VISTA vw_bsc_clientes:")
print("=" * 60)
try:
    cursor.execute("SELECT * FROM vw_bsc_clientes")
    bsc_cli = cursor.fetchone()
    if bsc_cli:
        print(f"  Objetivo: {bsc_cli['objetivo_nombre']}")
        print(f"  KR1: {bsc_cli['kr1_valor_observado']} (Progreso: {bsc_cli['kr1_progreso']}%)")
        print(f"  KR2: {bsc_cli['kr2_valor_observado']} (Progreso: {bsc_cli['kr2_progreso']}%)")
        print(f"  Avance Global: {bsc_cli['avance_objetivo_porcentaje']}%")
    else:
        print("  ⚠️  Vista sin datos")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 6. Verificar DimEmpleado (necesario para Aprendizaje)
print("\n" + "=" * 60)
print("6. DimEmpleado:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) as total FROM DimEmpleado")
empleados = cursor.fetchone()
print(f"  Total empleados: {empleados['total']}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
