#!/usr/bin/env python3
"""
Script rápido para poblar horas en DW
- Carga HechoTarea desde origen
- Actualiza HechoProyecto.horas_reales_total
"""

import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/backend/.env')

print("🚀 Poblando datos de horas en DW...\n")

# Conexiones
conn_origen = mysql.connector.connect(
    host=os.getenv('DB_HOST_ORIGEN'),
    port=int(os.getenv('DB_PORT_ORIGEN', '3306')),
    user=os.getenv('DB_USER_ORIGEN'),
    password=os.getenv('DB_PASSWORD_ORIGEN'),
    database=os.getenv('DB_NAME_ORIGEN')
)

conn_dw = mysql.connector.connect(
    host=os.getenv('DB_HOST_DESTINO'),
    port=int(os.getenv('DB_PORT_DESTINO', '3306')),
    user=os.getenv('DB_USER_DESTINO'),
    password=os.getenv('DB_PASSWORD_DESTINO'),
    database=os.getenv('DB_NAME_DESTINO')
)

cursor_origen = conn_origen.cursor(dictionary=True)
cursor_dw = conn_dw.cursor(dictionary=True)

# Paso 1: Verificar si HechoTarea tiene datos
cursor_dw.execute("SELECT COUNT(*) as total FROM HechoTarea")
total_tareas = cursor_dw.fetchone()['total']

if total_tareas == 0:
    print("📦 PASO 1: Cargando HechoTarea desde origen...")
    
    # Obtener tareas con horas desde origen
    cursor_origen.execute("""
        SELECT 
            t.id_tarea,
            t.id_proyecto,
            t.id_empleado,
            t.nombre_tarea,
            t.descripcion,
            t.horas_plan,
            t.horas_reales,
            DATE(t.fecha_inicio_plan) as fecha_inicio_plan,
            DATE(t.fecha_fin_plan) as fecha_fin_plan,
            DATE(t.fecha_inicio_real) as fecha_inicio_real,
            DATE(t.fecha_fin_real) as fecha_fin_real,
            t.id_estado,
            t.prioridad
        FROM Tarea t
        WHERE t.horas_reales > 0 OR t.horas_plan > 0
    """)
    
    tareas = cursor_origen.fetchall()
    print(f"   ✓ Obtenidas {len(tareas)} tareas con horas")
    
    # Insertar en HechoTarea
    insert_query = """
        INSERT INTO HechoTarea (
            id_tarea, id_proyecto, id_empleado, 
            nombre_tarea, descripcion_tarea,
            horas_plan, horas_reales,
            id_estado, prioridad, fecha_carga
        ) VALUES (
            %(id_tarea)s, %(id_proyecto)s, %(id_empleado)s,
            %(nombre_tarea)s, %(descripcion)s,
            %(horas_plan)s, %(horas_reales)s,
            %(id_estado)s, %(prioridad)s, NOW()
        )
        ON DUPLICATE KEY UPDATE
            horas_reales = VALUES(horas_reales),
            horas_plan = VALUES(horas_plan)
    """
    
    batch_size = 500
    for i in range(0, len(tareas), batch_size):
        batch = tareas[i:i+batch_size]
        cursor_dw.executemany(insert_query, batch)
        conn_dw.commit()
        print(f"   ✓ Insertadas {min(i+batch_size, len(tareas))}/{len(tareas)} tareas")
    
    print(f"   ✅ HechoTarea cargado: {len(tareas)} registros\n")
else:
    print(f"✓ HechoTarea ya tiene {total_tareas} registros\n")

# Paso 2: Actualizar horas_reales_total y horas_estimadas_total en HechoProyecto
print("📊 PASO 2: Actualizando HechoProyecto.horas_*_total...")

cursor_dw.execute("""
    UPDATE HechoProyecto hp
    INNER JOIN (
        SELECT 
            id_proyecto,
            SUM(COALESCE(horas_reales, 0)) as total_reales,
            SUM(COALESCE(horas_plan, 0)) as total_estimadas
        FROM HechoTarea
        GROUP BY id_proyecto
    ) t ON hp.id_proyecto = t.id_proyecto
    SET 
        hp.horas_reales_total = t.total_reales,
        hp.horas_estimadas_total = t.total_estimadas
""")

rows_updated = cursor_dw.rowcount
conn_dw.commit()
print(f"   ✅ Actualizados {rows_updated} proyectos con horas\n")

# Paso 3: Verificar resultados
print("📈 PASO 3: Verificando resultados...")

cursor_dw.execute("""
    SELECT 
        COUNT(*) as proyectos_con_horas,
        SUM(horas_reales_total) as total_horas_reales,
        SUM(horas_estimadas_total) as total_horas_estimadas,
        AVG(horas_reales_total) as promedio_horas
    FROM HechoProyecto
    WHERE horas_reales_total > 0
""")

resultado = cursor_dw.fetchone()
print(f"   Proyectos con horas: {resultado['proyectos_con_horas']}")
print(f"   Total horas reales: {resultado['total_horas_reales']:,.0f}")
print(f"   Total horas estimadas: {resultado['total_horas_estimadas']:,.0f}")
print(f"   Promedio horas/proyecto: {resultado['promedio_horas']:,.1f}")

# Cerrar conexiones
conn_origen.close()
conn_dw.close()

print("\n✅ ¡Poblado completo! Recarga el dashboard.")
