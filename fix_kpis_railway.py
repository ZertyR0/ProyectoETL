#!/usr/bin/env python3
"""
Script para corregir vistas OLAP en Railway
Ejecuta las correcciones directamente sin problemas de terminal
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/backend/.env')

# SQL para corregir las vistas
SQL_FIXES = """
-- CREAR O REEMPLAZAR VISTA: KPIs Ejecutivos CORREGIDA
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
GROUP BY dt.anio, dt.trimestre, dt.mes;

-- CREAR O REEMPLAZAR VISTA: Análisis por Cliente CORREGIDA
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
GROUP BY dc.id_cliente, dc.nombre, dc.sector, dt.anio;

-- CREAR O REEMPLAZAR VISTA: Performance por Sector
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
GROUP BY dc.sector, dt.anio;

-- CREAR O REEMPLAZAR VISTA: ROLLUP Proyectos
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
GROUP BY dc.sector, dt.anio, dt.trimestre WITH ROLLUP;
"""

def main():
    print("🔧 Conectando a Railway DataWarehouse...")
    
    try:
        # Conectar al DW
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST_DESTINO'),
            port=int(os.getenv('DB_PORT_DESTINO')),
            user=os.getenv('DB_USER_DESTINO'),
            password=os.getenv('DB_PASSWORD_DESTINO'),
            database=os.getenv('DB_NAME_DESTINO')
        )
        
        cursor = conn.cursor()
        
        print("✅ Conexión establecida")
        print("🔄 Ejecutando correcciones SQL...")
        
        # Ejecutar cada statement por separado
        for statement in SQL_FIXES.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
                print(f"  ✓ Ejecutado: {statement[:50]}...")
        
        conn.commit()
        print("\n✅ Vistas OLAP corregidas exitosamente")
        
        # Verificar
        print("\n🔍 Verificando datos...")
        
        cursor.execute("SELECT COUNT(*) FROM HechoProyecto")
        hechos = cursor.fetchone()[0]
        print(f"  - HechoProyecto: {hechos} registros")
        
        cursor.execute("SELECT COUNT(*) FROM DimCliente")
        clientes = cursor.fetchone()[0]
        print(f"  - DimCliente: {clientes} registros")
        
        # Probar vista KPIs
        cursor.execute("SELECT * FROM vw_olap_kpis_ejecutivos LIMIT 1")
        kpi = cursor.fetchone()
        if kpi:
            print(f"\n✅ Vista KPIs funcional:")
            print(f"  - Total proyectos: {kpi[3]}")
            print(f"  - Completados: {kpi[4]}")
            print(f"  - Activos: {kpi[5]}")
        
        # Probar vista clientes
        cursor.execute("SELECT * FROM vw_olap_analisis_cliente LIMIT 1")
        cliente = cursor.fetchone()
        if cliente:
            print(f"\n✅ Vista Clientes funcional:")
            print(f"  - Cliente: {cliente[1]}")
            print(f"  - Sector: {cliente[2]}")
            print(f"  - Proyectos: {cliente[4]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ¡Corrección completada! Reinicia el backend en Railway.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
