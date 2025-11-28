#!/usr/bin/env python3
"""
Script para desplegar vistas OLAP corregidas en Railway
"""

import mysql.connector
import os

# Configuración Railway (desde variables de entorno del backend)
config_railway = {
    'host': 'interchange.proxy.rlwy.net',
    'port': 22434,
    'user': 'root',
    'password': os.getenv('MYSQL_ROOT_PASSWORD', 'wpTpNMEWfuGLciBWxVzMgzIKAjnpqCjl'),
    'database': 'dw_proyectos_hist'
}

def deploy_views_to_railway():
    """Recrear vistas OLAP en Railway con nombres correctos"""
    
    print("🚀 Conectando a Railway MySQL...")
    try:
        conn = mysql.connector.connect(**config_railway)
        cursor = conn.cursor()
        print(f"✅ Conectado a {config_railway['host']}:{config_railway['port']}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    print("\n🔧 Recreando vistas OLAP...\n")
    
    # DROP vistas existentes
    print("1. Eliminando vistas antiguas...")
    vistas_a_eliminar = [
        'vw_olap_detallado',
        'vw_olap_por_cliente',
        'vw_olap_por_equipo',
        'vw_olap_por_anio',
        'vw_olap_total'
    ]
    
    for vista in vistas_a_eliminar:
        try:
            cursor.execute(f"DROP VIEW IF EXISTS {vista}")
            print(f"   ✓ {vista} eliminada")
        except Exception as e:
            print(f"   ⚠ Error eliminando {vista}: {e}")
    
    # VISTA 1: vw_olap_detallado
    print("\n2. Creando vw_olap_detallado...")
    try:
        cursor.execute("""
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
        ORDER BY hp.id_tiempo_fin_real DESC, dp.nombre_proyecto
        """)
        print("   ✓ vw_olap_detallado creada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # VISTA 2: vw_olap_por_cliente
    print("\n3. Creando vw_olap_por_cliente...")
    try:
        cursor.execute("""
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
        ORDER BY total_proyectos DESC
        """)
        print("   ✓ vw_olap_por_cliente creada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # VISTA 3: vw_olap_por_equipo
    print("\n4. Creando vw_olap_por_equipo...")
    try:
        cursor.execute("""
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
        ORDER BY total_proyectos DESC
        """)
        print("   ✓ vw_olap_por_equipo creada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # VISTA 4: vw_olap_por_anio
    print("\n5. Creando vw_olap_por_anio...")
    try:
        cursor.execute("""
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
        ORDER BY YEAR(hp.id_tiempo_fin_real) DESC
        """)
        print("   ✓ vw_olap_por_anio creada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # VISTA 5: vw_olap_total
    print("\n6. Creando vw_olap_total...")
    try:
        cursor.execute("""
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
        LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
        """)
        print("   ✓ vw_olap_total creada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Todas las vistas OLAP desplegadas exitosamente en Railway!")
    return True

if __name__ == '__main__':
    try:
        deploy_views_to_railway()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
