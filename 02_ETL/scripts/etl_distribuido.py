#!/usr/bin/env python3
"""
ETL Distribuido - Carga datos de BD Origen remota a DataWarehouse remoto
Máquina 1 (172.20.10.3) -> Máquina 2 (local) -> Máquina 3 (172.20.10.2)
"""

import sys
import os
from pathlib import Path

# Agregar path para importar configuración
sys.path.insert(0, str(Path(__file__).parent.parent / 'config'))

from config_conexion import get_config
import mysql.connector
from datetime import datetime, date
import pandas as pd
from sqlalchemy import create_engine

def ejecutar_etl_distribuido():
    """Ejecutar ETL completo en modo distribuido"""
    
    print("\n" + "="*70)
    print("🌐 ETL DISTRIBUIDO - 3 MÁQUINAS")
    print("="*70)
    
    # Obtener configuración distribuida
    config = get_config('distribuido')
    
    print(f"\n📊 BD Origen:  {config['host_origen']}:{config['port_origen']}")
    print(f"🏢 BD Destino: {config['host_destino']}:{config['port_destino']}")
    
    try:
        # ===== PASO 1: CONECTAR A AMBAS BDs =====
        print("\n🔗 Conectando a bases de datos...")
        
        conn_origen = mysql.connector.connect(
            host=config['host_origen'],
            port=config['port_origen'],
            user=config['user_origen'],
            password=config['password_origen'],
            database=config['database_origen']
        )
        
        conn_destino = mysql.connector.connect(
            host=config['host_destino'],
            port=config['port_destino'],
            user=config['user_destino'],
            password=config['password_destino'],
            database=config['database_destino']
        )
        
        print("✅ Conexiones establecidas")
        
        cursor_destino = conn_destino.cursor()
        
        # ===== PASO 2: LIMPIAR DATAWAREHOUSE =====
        print("\n🧹 Limpiando DataWarehouse...")
        
        cursor_destino.execute("SET FOREIGN_KEY_CHECKS = 0")
        tablas_limpiar = ['HechoTarea', 'HechoProyecto', 'DimTiempo', 'DimProyecto', 'DimEquipo', 'DimEmpleado', 'DimCliente']
        
        for tabla in tablas_limpiar:
            cursor_destino.execute(f"DELETE FROM {tabla}")
            print(f"  ✓ {tabla} limpiada")
        
        cursor_destino.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn_destino.commit()
        
        # ===== PASO 3: CARGAR DIMENSIONES =====
        print("\n📦 Cargando dimensiones...")
        
        # DimCliente
        df_clientes = pd.read_sql(
            "SELECT id_cliente, nombre, sector, contacto, telefono, email, direccion, fecha_registro FROM Cliente",
            conn_origen
        )
        df_clientes.to_sql('DimCliente', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ DimCliente: {len(df_clientes)} registros")
        
        # DimEmpleado
        df_empleados = pd.read_sql(
            "SELECT id_empleado, nombre, puesto, departamento, salario_base, fecha_ingreso, activo FROM Empleado WHERE activo = 1",
            conn_origen
        )
        df_empleados.to_sql('DimEmpleado', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ DimEmpleado: {len(df_empleados)} registros")
        
        # DimEquipo
        df_equipos = pd.read_sql(
            "SELECT id_equipo, nombre_equipo, descripcion, fecha_creacion, activo FROM Equipo WHERE activo = 1",
            conn_origen
        )
        df_equipos.to_sql('DimEquipo', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ DimEquipo: {len(df_equipos)} registros")
        
        # DimProyecto (solo completados y cancelados)
        df_proyectos = pd.read_sql(
            "SELECT id_proyecto, nombre as nombre_proyecto, descripcion, fecha_inicio, fecha_fin_plan, presupuesto as presupuesto_plan, prioridad FROM Proyecto WHERE id_estado IN (12, 13)",
            conn_origen
        )
        # Renombrar columna para match con DW
        df_proyectos.rename(columns={'fecha_inicio': 'fecha_inicio'}, inplace=True)
        df_proyectos.to_sql('DimProyecto', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ DimProyecto: {len(df_proyectos)} registros")
        
        # DimTiempo
        print(f"  ⏳ Generando DimTiempo...")
        from datetime import timedelta
        fecha_inicio = date.today() - timedelta(days=3*365)
        fecha_fin = date.today() + timedelta(days=365)
        
        fechas = []
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            fechas.append({
                'id_tiempo': fecha_actual.year * 10000 + fecha_actual.month * 100 + fecha_actual.day,
                'fecha': fecha_actual,
                'anio': fecha_actual.year,
                'trimestre': (fecha_actual.month - 1) // 3 + 1,
                'mes': fecha_actual.month,
                'numero_semana': fecha_actual.isocalendar()[1],
                'dia': fecha_actual.day,
                'dia_semana': fecha_actual.isoweekday(),
                'nombre_mes': fecha_actual.strftime('%B'),
                'nombre_dia_semana': fecha_actual.strftime('%A')
            })
            fecha_actual += timedelta(days=1)
        
        df_tiempo = pd.DataFrame(fechas)
        df_tiempo.to_sql('DimTiempo', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ DimTiempo: {len(df_tiempo)} registros")
        
        # ===== PASO 4: CARGAR HECHOS =====
        print("\n📊 Cargando hechos...")
        
        # HechoProyecto con métricas calculadas
        query_hechos = """
        SELECT 
            p.id_proyecto,
            p.id_cliente,
            p.id_empleado_gerente,
            YEAR(p.fecha_inicio)*10000 + MONTH(p.fecha_inicio)*100 + DAY(p.fecha_inicio) as id_tiempo_inicio,
            YEAR(p.fecha_fin_plan)*10000 + MONTH(p.fecha_fin_plan)*100 + DAY(p.fecha_fin_plan) as id_tiempo_fin_plan,
            IF(p.fecha_fin_real IS NULL, NULL, YEAR(p.fecha_fin_real)*10000 + MONTH(p.fecha_fin_real)*100 + DAY(p.fecha_fin_real)) as id_tiempo_fin_real,
            DATEDIFF(p.fecha_fin_plan, p.fecha_inicio) as duracion_planificada,
            IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio), 0) as duracion_real,
            IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio), 0) as variacion_cronograma,
            IF(p.fecha_fin_real IS NULL, 0, IF(p.fecha_fin_real <= p.fecha_fin_plan, 1, 0)) as cumplimiento_tiempo,
            p.presupuesto,
            IFNULL(p.costo_real, 0) as costo_real,
            IFNULL(p.costo_real, 0) - p.presupuesto as variacion_costos,
            IF(IFNULL(p.costo_real, 0) <= p.presupuesto, 1, 0) as cumplimiento_presupuesto,
            IF(p.presupuesto > 0, ((IFNULL(p.costo_real, 0) - p.presupuesto) / p.presupuesto * 100), 0) as porcentaje_sobrecosto,
            (SELECT COUNT(*) FROM Tarea WHERE id_proyecto = p.id_proyecto) as tareas_total,
            (SELECT COUNT(*) FROM Tarea WHERE id_proyecto = p.id_proyecto AND id_estado = 13) as tareas_completadas,
            (SELECT COUNT(*) FROM Tarea WHERE id_proyecto = p.id_proyecto AND id_estado = 14) as tareas_canceladas,
            (SELECT COUNT(*) FROM Tarea WHERE id_proyecto = p.id_proyecto AND id_estado IN (10,11)) as tareas_pendientes,
            p.progreso_porcentaje as porcentaje_completado,
            IFNULL((SELECT SUM(horas_plan) FROM Tarea WHERE id_proyecto = p.id_proyecto), 0) as horas_estimadas_total,
            IFNULL((SELECT SUM(horas_reales) FROM Tarea WHERE id_proyecto = p.id_proyecto), 0) as horas_reales_total,
            IFNULL((SELECT SUM(horas_reales - horas_plan) FROM Tarea WHERE id_proyecto = p.id_proyecto), 0) as variacion_horas,
            IF((SELECT SUM(horas_plan) FROM Tarea WHERE id_proyecto = p.id_proyecto) > 0,
               ((SELECT SUM(horas_reales) FROM Tarea WHERE id_proyecto = p.id_proyecto) / 
                (SELECT SUM(horas_plan) FROM Tarea WHERE id_proyecto = p.id_proyecto) * 100), 0) as eficiencia_horas
        FROM Proyecto p
        WHERE p.id_estado IN (12, 13)
        """
        
        df_hechos = pd.read_sql(query_hechos, conn_origen)
        df_hechos.to_sql('HechoProyecto', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ HechoProyecto: {len(df_hechos)} registros")
        
        # HechoTarea
        query_tareas = """
        SELECT 
            t.id_tarea,
            t.id_proyecto,
            COALESCE(t.id_empleado, t.id_empleado_responsable, t.id_responsable) as id_empleado,
            YEAR(t.fecha_inicio_plan)*10000 + MONTH(t.fecha_inicio_plan)*100 + DAY(t.fecha_inicio_plan) as id_tiempo_inicio_plan,
            YEAR(t.fecha_fin_plan)*10000 + MONTH(t.fecha_fin_plan)*100 + DAY(t.fecha_fin_plan) as id_tiempo_fin_plan,
            IF(t.fecha_inicio_real IS NULL, NULL, YEAR(t.fecha_inicio_real)*10000 + MONTH(t.fecha_inicio_real)*100 + DAY(t.fecha_inicio_real)) as id_tiempo_inicio_real,
            IF(t.fecha_fin_real IS NULL, NULL, YEAR(t.fecha_fin_real)*10000 + MONTH(t.fecha_fin_real)*100 + DAY(t.fecha_fin_real)) as id_tiempo_fin_real,
            DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan) as duracion_planificada,
            IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real), 0) as duracion_real,
            IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real) - DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan), 0) as variacion_cronograma,
            IF(t.fecha_fin_real IS NULL, 0, IF(t.fecha_fin_real <= t.fecha_fin_plan, 1, 0)) as cumplimiento_tiempo,
            t.horas_plan,
            t.horas_reales,
            t.horas_reales - t.horas_plan as variacion_horas,
            t.costo_estimado,
            t.costo_real,
            t.costo_real - t.costo_estimado as variacion_costo,
            t.progreso_porcentaje
        FROM Tarea t
        JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
        WHERE p.id_estado IN (12, 13)
        """
        
        df_tareas = pd.read_sql(query_tareas, conn_origen)
        df_tareas.to_sql('HechoTarea', con=create_engine(
            f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
        ), if_exists='append', index=False)
        print(f"  ✓ HechoTarea: {len(df_tareas)} registros")
        
        # Cerrar conexiones
        conn_origen.close()
        conn_destino.close()
        
        print("\n" + "="*70)
        print("✅ ETL DISTRIBUIDO COMPLETADO EXITOSAMENTE")
        print("="*70)
        
        total_registros = len(df_clientes) + len(df_empleados) + len(df_equipos) + len(df_proyectos) + len(df_tiempo) + len(df_hechos) + len(df_tareas)
        
        print(f"\n📊 Resumen:")
        print(f"   Clientes:        {len(df_clientes)}")
        print(f"   Empleados:       {len(df_empleados)}")
        print(f"   Equipos:         {len(df_equipos)}")
        print(f"   Proyectos:       {len(df_proyectos)}")
        print(f"   Fechas:          {len(df_tiempo)}")
        print(f"   HechoProyecto:   {len(df_hechos)}")
        print(f"   HechoTarea:      {len(df_tareas)}")
        print(f"   TOTAL:           {total_registros}")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    ejecutar_etl_distribuido()
