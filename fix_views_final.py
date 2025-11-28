#!/usr/bin/env python3
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

# Vista 1: KPIs Ejecutivos
print("Creando vw_olap_kpis_ejecutivos...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_kpis_ejecutivos AS
SELECT 
    dt.anio,
    dt.trimestre,
    dt.mes,
    COUNT(DISTINCT hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as proyectos_completados,
    SUM(CASE WHEN hp.porcentaje_completado < 100 THEN 1 ELSE 0 END) as proyectos_activos,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real_total,
    AVG(hp.porcentaje_completado) as eficiencia_promedio,
    SUM(hp.horas_reales_total) as horas_trabajadas,
    SUM(hp.cumplimiento_tiempo) as proyectos_a_tiempo,
    SUM(hp.cumplimiento_presupuesto) as proyectos_en_presupuesto
FROM HechoProyecto hp
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
GROUP BY dt.anio, dt.trimestre, dt.mes
""")
print("✓ vw_olap_kpis_ejecutivos")

# Vista 2: Performance por Sector
print("Creando vw_olap_sector_performance...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_sector_performance AS
SELECT 
    dc.sector,
    dt.anio,
    COUNT(hp.id_proyecto) as proyectos_sector,
    SUM(hp.presupuesto) as facturacion_sector,
    SUM(hp.costo_real) as costo_sector,
    AVG(hp.porcentaje_completado) as progreso_promedio_sector,
    (SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100 as margen_rentabilidad_porcentaje,
    (SUM(hp.cumplimiento_tiempo) / NULLIF(COUNT(hp.id_proyecto), 0)) * 100 as indice_cumplimiento_porcentaje
FROM DimCliente dc
JOIN HechoProyecto hp ON dc.id_cliente = hp.id_cliente
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
WHERE dt.anio >= YEAR(CURDATE()) - 2
GROUP BY dc.sector, dt.anio
""")
print("✓ vw_olap_sector_performance")

# Vista 3: Análisis por Cliente
print("Creando vw_olap_analisis_cliente...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_analisis_cliente AS
SELECT 
    dc.id_cliente,
    dc.nombre as nombre_cliente,
    dc.sector,
    dt.anio,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(CASE WHEN hp.porcentaje_completado = 100 THEN 1 ELSE 0 END) as completados,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_real,
    (SUM(hp.costo_real) / NULLIF(SUM(hp.presupuesto), 0)) * 100 as rentabilidad_porcentaje,
    (SUM(CASE WHEN hp.porcentaje_completado >= 100 THEN hp.presupuesto ELSE 0 END) / 
     NULLIF(SUM(hp.presupuesto), 0)) * 100 as porcentaje_presupuesto
FROM DimCliente dc
JOIN HechoProyecto hp ON dc.id_cliente = hp.id_cliente
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
GROUP BY dc.id_cliente, dc.nombre, dc.sector, dt.anio
""")
print("✓ vw_olap_analisis_cliente")

# Vista 4: ROLLUP Proyectos
print("Creando vw_olap_proyectos_rollup...")
cursor.execute("""
CREATE OR REPLACE VIEW vw_olap_proyectos_rollup AS
SELECT 
    dc.sector,
    dt.anio,
    dt.trimestre,
    COUNT(hp.id_proyecto) as total_proyectos,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_total,
    AVG(hp.porcentaje_completado) as progreso_promedio
FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
LEFT JOIN DimTiempo dt ON hp.id_tiempo_inicio = dt.id_tiempo
GROUP BY dc.sector, dt.anio, dt.trimestre WITH ROLLUP
""")
print("✓ vw_olap_proyectos_rollup")

conn.commit()
cursor.close()
conn.close()

print("\n✅ ¡Todas las vistas OLAP creadas exitosamente!")
print("🔄 Reinicia el backend en Railway para aplicar cambios")
