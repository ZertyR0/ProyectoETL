#!/usr/bin/env python3
"""
Script para actualizar horas en HechoProyecto desde Railway
Calcula y actualiza horas_reales_total y horas_estimadas_total
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv('/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/backend/.env')

# Conectar a base origen
conn_origen = mysql.connector.connect(
    host=os.getenv('DB_HOST_ORIGEN'),
    port=int(os.getenv('DB_PORT_ORIGEN', '3306')),
    user=os.getenv('DB_USER_ORIGEN'),
    password=os.getenv('DB_PASSWORD_ORIGEN'),
    database=os.getenv('DB_NAME_ORIGEN')
)

# Conectar a DataWarehouse
conn_dw = mysql.connector.connect(
    host=os.getenv('DB_HOST_DESTINO'),
    port=int(os.getenv('DB_PORT_DESTINO', '3306')),
    user=os.getenv('DB_USER_DESTINO'),
    password=os.getenv('DB_PASSWORD_DESTINO'),
    database=os.getenv('DB_NAME_DESTINO')
)

cursor_origen = conn_origen.cursor(dictionary=True)
cursor_dw = conn_dw.cursor()

print("🔄 Actualizando horas en HechoProyecto...")

# Obtener horas por proyecto desde base origen
cursor_origen.execute("""
    SELECT 
        id_proyecto,
        COALESCE(SUM(horas_plan), 0) as horas_estimadas,
        COALESCE(SUM(horas_reales), 0) as horas_reales
    FROM Tarea
    GROUP BY id_proyecto
""")

proyectos_horas = cursor_origen.fetchall()
print(f"Encontrados {len(proyectos_horas)} proyectos con horas")

# Actualizar cada proyecto en HechoProyecto
actualizados = 0
for proy in proyectos_horas:
    id_proy = proy['id_proyecto']
    horas_est = int(proy['horas_estimadas'] or 0)
    horas_real = int(proy['horas_reales'] or 0)
    var_horas = horas_real - horas_est
    
    # Calcular eficiencia
    eficiencia = (horas_est / horas_real * 100) if horas_real > 0 else 0
    
    cursor_dw.execute("""
        UPDATE HechoProyecto 
        SET horas_estimadas_total = %s,
            horas_reales_total = %s,
            variacion_horas = %s,
            eficiencia_horas = %s
        WHERE id_proyecto = %s
    """, (horas_est, horas_real, var_horas, eficiencia, id_proy))
    
    if cursor_dw.rowcount > 0:
        actualizados += 1
        if actualizados <= 5:  # Mostrar primeros 5
            print(f"  ✓ Proyecto {id_proy}: {horas_est}h plan, {horas_real}h reales")

conn_dw.commit()

print(f"\n✅ Actualizados {actualizados} proyectos")

# Verificar resultado
cursor_dw.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(horas_estimadas_total) as horas_est_total,
        SUM(horas_reales_total) as horas_reales_total,
        AVG(horas_reales_total) as promedio_horas
    FROM HechoProyecto
    WHERE horas_reales_total > 0
""")

stats = cursor_dw.fetchone()
print(f"\n📊 Estadísticas:")
print(f"  Proyectos con horas: {stats[0]}")
print(f"  Horas estimadas totales: {stats[1]}")
print(f"  Horas reales totales: {stats[2]}")
print(f"  Promedio horas por proyecto: {stats[3]:.1f}")

cursor_origen.close()
cursor_dw.close()
conn_origen.close()
conn_dw.close()

print("\n🎉 ¡Actualización completada! Recarga el dashboard.")
