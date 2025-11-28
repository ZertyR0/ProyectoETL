#!/usr/bin/env python3
"""
Crear vistas OLAP para análisis multidimensional
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

print("🔧 Creando vistas OLAP para análisis multidimensional...")

# Vista 1: OLAP Detallado (nivel más granular)
print("1. Creando vw_olap_detallado...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_detallado AS
SELECT 
    hp.id_proyecto as proyecto,
    dp.nombre_proyecto,
    COALESCE(dc.nombre, 'Sin Cliente') as cliente,
    COALESCE(dc.sector, '-') as sector,
    'N/A' as equipo,
    COALESCE(dt.anio, YEAR(CURDATE())) as anio,
    CASE 
        WHEN hp.porcentaje_completado = 100 THEN 'Completado'
        WHEN hp.porcentaje_completado > 0 THEN 'En Progreso'
        ELSE 'Pendiente'
    END as estado,
    hp.presupuesto as presupuesto,
    hp.costo_real as costo_real,
    hp.tareas_total as total_proyectos,
    hp.tareas_completadas as completados,
    ROUND((hp.costo_real / NULLIF(hp.presupuesto, 0)) * 100, 1) as rentabilidad_porcentaje,
    CASE 
        WHEN hp.presupuesto > 0 AND hp.costo_real <= hp.presupuesto THEN 'Sí'
        ELSE 'No'
    END as en_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
WHERE hp.presupuesto > 0
""")
print("✓ vw_olap_detallado")

# Vista 2: OLAP por Cliente
print("2. Creando vw_olap_por_cliente...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_por_cliente AS
SELECT 
    COALESCE(dc.nombre, 'Sin Cliente') as cliente,
    COALESCE(dc.sector, '-') as sector,
    '-' as equipo_placeholder,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real,
    ROUND((SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100, 1) as rentabilidad_porcentaje,
    ROUND((SUM(CASE WHEN hp.costo_real <= hp.presupuesto THEN hp.presupuesto ELSE 0 END) / 
     NULLIF(SUM(hp.presupuesto), 0)) * 100, 1) as porcentaje_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
GROUP BY dc.nombre, dc.sector
ORDER BY total_proyectos DESC
""")
print("✓ vw_olap_por_cliente")

# Vista 3: OLAP por Equipo (usando cambios_equipo_proy como proxy)
print("3. Creando vw_olap_por_equipo...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_por_equipo AS
SELECT 
    'N/A' as equipo,
    '-' as sector,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real,
    (SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100 as rentabilidad_porcentaje,
    (SUM(CASE WHEN hp.porcentaje_completado >= 100 THEN hp.presupuesto ELSE 0 END) / 
     NULLIF(SUM(hp.presupuesto), 0)) * 100 as porcentaje_presupuesto
FROM HechoProyecto hp
WHERE hp.equipos_asignados > 0
GROUP BY hp.id_equipo
""")
print("✓ vw_olap_por_equipo")

# Vista 4: OLAP por Año
print("4. Creando vw_olap_por_anio...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_por_anio AS
SELECT 
    '-' as cliente_placeholder,
    '-' as sector_placeholder,
    COALESCE(dt.anio, YEAR(CURDATE())) as anio,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real,
    ROUND((SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100, 1) as rentabilidad_porcentaje,
    ROUND((SUM(CASE WHEN hp.costo_real <= hp.presupuesto THEN hp.presupuesto ELSE 0 END) / 
     NULLIF(SUM(hp.presupuesto), 0)) * 100, 1) as porcentaje_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
GROUP BY dt.anio
ORDER BY anio DESC
""")
print("✓ vw_olap_por_anio")

# Vista 5: OLAP Total (agregado global)
print("5. Creando vw_olap_total...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_total AS
SELECT 
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real,
    (SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100 as rentabilidad_porcentaje,
    (SUM(CASE WHEN hp.porcentaje_completado >= 100 THEN hp.presupuesto ELSE 0 END) / 
     NULLIF(SUM(hp.presupuesto), 0)) * 100 as porcentaje_presupuesto
FROM HechoProyecto hp
""")
print("✓ vw_olap_total")

conn.commit()
cursor.close()
conn.close()

print("\n✅ Todas las vistas OLAP creadas exitosamente!")
print("🔄 Recarga el dashboard para ver los cambios")
