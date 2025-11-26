from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import subprocess
import traceback
from datetime import datetime, date
from decimal import Decimal
import json

app = Flask(__name__)
CORS(app)  # Permitir requests desde Angular

# Paths unificados a nueva estructura src/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_ROOT = os.path.join(PROJECT_ROOT, 'src')
CONFIG_ROOT = os.path.join(SRC_ROOT, 'config')
ETL_ROOT = os.path.join(SRC_ROOT, 'etl')

# Asegurar que el paquete raíz "src" esté disponible para imports tipo src.origen.*
# PROJECT_ROOT debe estar PRIMERO para resolver imports absolutos como "from src.origen.xxx"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
for p in (SRC_ROOT, CONFIG_ROOT, ETL_ROOT):
    if p not in sys.path:
        sys.path.append(p)

try:
    # Import desde ubicación centralizada (src/config/config_conexion.py)
    from src.config.config_conexion import get_config
    # Obtener configuración según ambiente
    AMBIENTE = os.getenv('ETL_AMBIENTE', 'local')
    config = get_config(AMBIENTE)
    
    # Configuración unificada usando el sistema de configuración ETL
    DB_CONFIG = {
        'host_origen': config['host_origen'],
        'port_origen': config['port_origen'],
        'user_origen': config['user_origen'],
        'password_origen': config['password_origen'],
        'host_destino': config['host_destino'],
        'port_destino': config['port_destino'],
        'user_destino': config['user_destino'],
        'password_destino': config['password_destino'],
        'db_origen': config['database_origen'],
        'db_destino': config['database_destino']
    }
    
    # Agregar unix_socket si existe en la configuración
    if 'unix_socket' in config:
        DB_CONFIG['unix_socket'] = config['unix_socket']
    
    print(f" Dashboard configurado para ambiente: {AMBIENTE}")
    print(f" BD Origen: {config['host_origen']}:{config['port_origen']}")
    if 'unix_socket' in config:
        print(f"   Socket: {config['unix_socket']}")
    print(f" BD Destino: {config['host_destino']}:{config['port_destino']}")
    
except ImportError:
    # Fallback a configuración local si no se puede importar
    print(" No se pudo importar configuración ETL, usando configuración local")
    AMBIENTE = 'local'  # Set default environment
    DB_CONFIG = {
        'host_origen': 'localhost',
        'port_origen': 3306,
        'user_origen': 'root',
        'password_origen': '',
        'host_destino': 'localhost',
        'port_destino': 3306,
        'user_destino': 'root',
        'password_destino': '',
        'db_origen': 'gestionproyectos_hist',
        'db_destino': 'dw_proyectos_hist'
    }

def get_connection(db_type='origen'):
    """Obtener conexión a la base de datos"""
    if db_type == 'origen':
        connection_params = {
            'user': DB_CONFIG['user_origen'],
            'password': DB_CONFIG['password_origen'],
            'database': DB_CONFIG['db_origen']
        }
        # Si hay unix_socket, usarlo en lugar de host/port
        if 'unix_socket' in DB_CONFIG and DB_CONFIG['unix_socket']:
            connection_params['unix_socket'] = DB_CONFIG['unix_socket']
        else:
            connection_params['host'] = DB_CONFIG['host_origen']
            connection_params['port'] = DB_CONFIG['port_origen']
        
        return mysql.connector.connect(**connection_params)
    else:
        # Conexión a destino (datawarehouse)
        connection_params = {
            'user': DB_CONFIG['user_destino'],
            'password': DB_CONFIG['password_destino'],
            'database': DB_CONFIG['db_destino']
        }
        # Si hay unix_socket, usarlo en lugar de host/port
        if 'unix_socket' in DB_CONFIG and DB_CONFIG['unix_socket']:
            connection_params['unix_socket'] = DB_CONFIG['unix_socket']
        else:
            connection_params['host'] = DB_CONFIG['host_destino']
            connection_params['port'] = DB_CONFIG['port_destino']
        
        return mysql.connector.connect(**connection_params)

def get_engine(db_type='origen'):
    """Obtener engine SQLAlchemy"""
    if db_type == 'origen':
        # Si hay unix_socket, usar ese en lugar de host/port
        if 'unix_socket' in DB_CONFIG and DB_CONFIG['unix_socket']:
            url = f"mysql+mysqlconnector://{DB_CONFIG['user_origen']}:{DB_CONFIG['password_origen']}@/?unix_socket={DB_CONFIG['unix_socket']}&database={DB_CONFIG['db_origen']}"
        else:
            url = f"mysql+mysqlconnector://{DB_CONFIG['user_origen']}:{DB_CONFIG['password_origen']}@{DB_CONFIG['host_origen']}:{DB_CONFIG['port_origen']}/{DB_CONFIG['db_origen']}"
    else:
        url = f"mysql+mysqlconnector://{DB_CONFIG['user_destino']}:{DB_CONFIG['password_destino']}@{DB_CONFIG['host_destino']}:{DB_CONFIG['port_destino']}/{DB_CONFIG['db_destino']}"
    
    return create_engine(url, pool_pre_ping=True)

@app.route('/')
def home():
    """Endpoint principal"""
    return jsonify({
        'message': 'API ETL Sistema Distribuido',
        'version': '1.0',
        'endpoints': {
            'GET /': 'Información de la API',
            'GET /status': 'Estado de conexiones',
            'GET /datos-origen': 'Datos de la BD origen',
            'GET /datos-datawarehouse': 'Datos del datawarehouse',
            'POST /insertar-datos': 'Insertar datos de prueba',
            'POST /ejecutar-etl': 'Ejecutar proceso ETL',
            'DELETE /limpiar-datos': 'Limpiar todas las tablas'
        }
    })

@app.route('/status')
def status():
    """Verificar estado de las conexiones"""
    try:
        # Probar conexión origen
        conn_origen = get_connection('origen')
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute("SELECT COUNT(*) FROM Proyecto")
        proyectos = cursor_origen.fetchone()[0]
        cursor_origen.close()
        conn_origen.close()
        
        # Probar conexión destino
        conn_destino = get_connection('destino')
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute("SELECT COUNT(*) FROM HechoProyecto")
        hechos = cursor_destino.fetchone()[0]
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'status': 'success',
            'origen': {
                'conectado': True,
                'proyectos': proyectos,
                'host': DB_CONFIG['host_origen']
            },
            'destino': {
                'conectado': True,
                'hechos_proyecto': hechos,
                'host': DB_CONFIG['host_destino']
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/datos-origen')
def datos_origen():
    """Obtener datos de la base origen"""
    try:
        conn = get_connection('origen')
        cursor = conn.cursor()
        
        # Obtener estadísticas
        stats = {}
        tablas = ['Cliente', 'Empleado', 'Equipo', 'Estado', 'Proyecto', 'Tarea', 'TareaEquipoHist']
        
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            stats[tabla] = cursor.fetchone()[0]
        
        # Obtener proyectos recientes
        cursor.execute("""
            SELECT p.id_proyecto, p.nombre, p.fecha_inicio, p.presupuesto, 
                   c.nombre as cliente, IFNULL(e.nombre_estado, 'Sin estado') as nombre_estado
            FROM Proyecto p
            LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
            LEFT JOIN Estado e ON p.id_estado = e.id_estado
            ORDER BY p.id_proyecto DESC
            LIMIT 10
        """)
        
        proyectos = []
        for row in cursor.fetchall():
            proyectos.append({
                'id': row[0],
                'nombre': row[1],
                'fecha_inicio': row[2].isoformat() if row[2] else None,
                'presupuesto': float(row[3]) if row[3] else 0,
                'cliente': row[4],
                'estado': row[5]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'estadisticas': stats,
            'proyectos_recientes': proyectos
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/datos-datawarehouse')
def datos_datawarehouse():
    """Obtener datos del datawarehouse"""
    try:
        conn = get_connection('destino')
        cursor = conn.cursor(buffered=True)  # buffered=True para evitar "Unread result found"
        
        # Obtener estadísticas del DW
        stats = {}
        tablas = ['DimCliente', 'DimEmpleado', 'DimEquipo', 'DimProyecto', 'DimTiempo', 'HechoProyecto', 'HechoTarea']
        tabla_keys = ['dimcliente', 'dimempleado', 'dimequipo', 'dimproyecto', 'dimtiempo', 'hechoproyecto', 'hechotarea']
        
        for i, tabla in enumerate(tablas):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                result = cursor.fetchone()
                stats[tabla_keys[i]] = result[0] if result else 0
            except Exception as e:
                print(f" Error contando {tabla}: {str(e)}")
                stats[tabla_keys[i]] = 0
        
        # Obtener métricas básicas del datawarehouse (sin proyectos_completados, se calculará después)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_proyectos,
                AVG(presupuesto) as presupuesto_promedio,
                AVG(CASE 
                    WHEN tareas_total > 0 THEN (tareas_completadas * 100.0 / tareas_total)
                    ELSE 0 
                END) as progreso_promedio
            FROM HechoProyecto
        """)
        
        metricas_row = cursor.fetchone()
        if metricas_row:
            metricas = {
                'total_proyectos': metricas_row[0] if metricas_row[0] else 0,
                'presupuesto_promedio': float(metricas_row[1]) if metricas_row[1] else 0,
                'progreso_promedio': float(metricas_row[2]) if metricas_row[2] else 0,
                'proyectos_completados': 0  # Se calculará después con estados reales
            }
        else:
            metricas = {
                'total_proyectos': 0,
                'presupuesto_promedio': 0,
                'progreso_promedio': 0,
                'proyectos_completados': 0
            }
        
        # Obtener detalle de proyectos en el DW con nombres desde DimProyecto
        cursor.execute("""
            SELECT 
                hp.id_proyecto,
                dp.nombre_proyecto,
                hp.duracion_planificada,
                hp.duracion_real,
                hp.cumplimiento_tiempo,
                hp.presupuesto,
                hp.costo_real_proy,
                CASE 
                    WHEN hp.tareas_total > 0 THEN (hp.tareas_completadas * 100.0 / hp.tareas_total)
                    ELSE 0 
                END as porcentaje_completado,
                dc.nombre as cliente,
                de.nombre as gerente,
                hp.cumplimiento_presupuesto,
                hp.tareas_completadas,
                hp.tareas_canceladas
            FROM HechoProyecto hp
            LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
            LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
            LEFT JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
            ORDER BY hp.id_proyecto
            LIMIT 50
        """)
        
        proyectos_dw_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Obtener estados desde base origen (solo en modo distribuido)
        proyectos_dw = []
        if AMBIENTE == 'distribuido':
            conn_origen = get_connection('origen')
            cursor_origen = conn_origen.cursor(buffered=True)  # buffered para evitar errores
            
            for row in proyectos_dw_rows:
                id_proy = row[0]
                nombre_proy = row[1]
                # Consultar estado desde origen por NOMBRE (más confiable que por ID)
                try:
                    cursor_origen.execute("""
                        SELECT estado, id_estado FROM Proyecto WHERE nombre = %s
                    """, (nombre_proy,))
                    estado_row = cursor_origen.fetchone()
                    if estado_row:
                        estado = estado_row[0]
                        id_estado = estado_row[1]
                    else:
                        # Si no encuentra por nombre, intentar por ID
                        cursor_origen.execute("""
                            SELECT estado, id_estado FROM Proyecto WHERE id_proyecto = %s
                        """, (id_proy,))
                        estado_row = cursor_origen.fetchone()
                        estado = estado_row[0] if estado_row else 'Desconocido'
                        id_estado = estado_row[1] if estado_row else None
                except Exception as e:
                    print(f" Error obteniendo estado para proyecto {nombre_proy}: {str(e)}")
                    estado = 'Desconocido'
                    id_estado = None
                
                proyectos_dw.append({
                    'id_proyecto': row[0],
                    'nombre_proyecto': row[1] if row[1] else f"Proyecto {row[0]}",
                    'presupuesto': float(row[2]) if row[2] else 0,
                    'costo_real': float(row[3]) if row[3] else 0,
                    'progreso_porcentaje': row[4] if row[4] else 0,
                    'cliente': row[5] if row[5] else 'Sin cliente',
                    'gerente': row[6] if row[6] else 'Sin gerente',
                    'estado': row[7] if row[7] else 'Sin estado',
                    'prioridad': row[8] if row[8] else 'Media',
                    'tareas_completadas': row[9],
                    'tareas_canceladas': row[10]
                })
            
            cursor_origen.close()
            conn_origen.close()
        else:
            # Modo local: consultar id_estado desde base origen y mapear a nombre
            conn_origen = get_connection('origen')
            cursor_origen = conn_origen.cursor(buffered=True)  # buffered para evitar errores
            
            # Mapeo de id_estado a nombre_estado (actualizado)
            mapeo_estados = {
                1: 'Planificación',
                2: 'En Progreso',
                3: 'En Pausa',
                4: 'Completado',
                5: 'Cancelado'
            }
            
            for row in proyectos_dw_rows:
                nombre_proyecto = row[1]
                porcentaje_completado = float(row[7]) if row[7] else 0
                
                # Consultar id_estado desde origen usando el NOMBRE del proyecto
                try:
                    cursor_origen.execute("""
                        SELECT p.id_estado
                        FROM Proyecto p
                        WHERE TRIM(p.nombre) = TRIM(%s)
                    """, (nombre_proyecto,))
                    estado_row = cursor_origen.fetchone()
                    if estado_row:
                        id_estado = estado_row[0]
                        estado = mapeo_estados.get(id_estado, 'Desconocido')
                    else:
                        # Fallback: determinar por porcentaje
                        estado = "Completado" if porcentaje_completado >= 100 else "Cancelado"
                except Exception as e:
                    print(f" Error obteniendo estado para proyecto '{nombre_proyecto}': {str(e)}")
                    # Fallback: determinar por porcentaje
                    estado = "Completado" if porcentaje_completado >= 100 else "Cancelado"
                
                proyectos_dw.append({
                    'id_proyecto': row[0],
                    'nombre_proyecto': nombre_proyecto if nombre_proyecto else f"Proyecto {row[0]}",
                    'estado': estado,
                    'duracion_planificada': row[2] if row[2] else 0,
                    'duracion_real': row[3] if row[3] else 0,
                    'cumplimiento_tiempo': 'Sí' if row[4] == 1 else 'No',
                    'presupuesto': float(row[5]) if row[5] else 0,
                    'costo_real': float(row[6]) if row[6] else 0,
                    'porcentaje_completado': porcentaje_completado,
                    'cliente': row[8] if row[8] else 'Sin cliente',
                    'gerente': row[9] if row[9] else 'Sin gerente',
                    'cumplimiento_presupuesto': 'Sí' if row[10] == 1 else 'No',
                    'tareas_completadas': row[11] if row[11] else 0,
                    'tareas_canceladas': row[12] if row[12] else 0
                })
            
            cursor_origen.close()
            conn_origen.close()
        
        # Calcular proyectos completados basándose en estados reales
        proyectos_completados = sum(1 for p in proyectos_dw if p.get('estado') == 'Completado')
        metricas['proyectos_completados'] = proyectos_completados
        
        # Calcular días promedio y proyectos a tiempo
        total_proyectos = len(proyectos_dw)
        if total_proyectos > 0:
            # Calcular días promedio considerando solo proyectos con datos válidos
            duraciones_validas = [p['duracion_planificada'] for p in proyectos_dw if p.get('duracion_planificada', 0) > 0]
            if duraciones_validas:
                metricas['dias_promedio'] = sum(duraciones_validas) / len(duraciones_validas)
            else:
                metricas['dias_promedio'] = 0
            
            # Calcular proyectos a tiempo (cumplimiento_tiempo == 'Sí')
            proyectos_a_tiempo = sum(1 for p in proyectos_dw if p.get('cumplimiento_tiempo') == 'Sí')
            metricas['proyectos_a_tiempo'] = proyectos_a_tiempo
            
            # Total de tareas desde HechoTarea (valor real)
            metricas['total_tareas'] = stats['hechotarea']
        else:
            metricas['dias_promedio'] = 0
            metricas['proyectos_a_tiempo'] = 0
            metricas['total_tareas'] = stats.get('hechotarea', 0)
        
        return jsonify({
            'status': 'success',
            'stats': {
                'clientes': stats['dimcliente'],
                'empleados': stats['dimempleado'],
                'equipos': stats['dimequipo'],
                'proyectos': stats['dimproyecto'],
                'hechos_proyecto': stats['hechoproyecto'],
                'hechos_tarea': stats['hechotarea']
            },
            'metricas': metricas,
            'proyectos': proyectos_dw
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/insertar-datos', methods=['POST'])
def insertar_datos():
    """Generar datos de prueba (rápido) reutilizando nuevo generador parametrizable.
    Sólo requiere número de proyectos; empleados/tareas por proyecto usan defaults.
    """
    try:
        data = request.get_json() if request.is_json else {}
        num_proyectos = int(data.get('proyectos', 50))
        ambiente = os.getenv('ETL_AMBIENTE', 'local')
        print(f" Generando {num_proyectos} proyectos (insertar-datos) ambiente={ambiente}...")
        from src.origen.generar_datos import generar_datos
        resumen = generar_datos(proyectos=num_proyectos, empleados_por_proyecto=5, tareas_por_proyecto=8, limpiar=False, ambiente=ambiente)
        return jsonify({
            'status': 'success',
            'message': f'{num_proyectos} proyectos generados',
            'resumen': resumen
        })
    except Exception as e:
        import traceback
        return jsonify({'status': 'error','message': str(e),'traceback': traceback.format_exc()}), 500

@app.route('/ejecutar-etl', methods=['POST'])
def ejecutar_etl():
    """Ejecutar proceso ETL usando script SQL manual (fixed schema).
    Flujo:
      1. Limpiar HechoProyecto y dimensiones
      2. Cargar dimensiones desde origen
      3. Cargar HechoProyecto con id_equipo desde TareaEquipoHist
    """
    try:
        print(" Iniciando proceso ETL manual...")
        
        # Get project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Execute ETL SQL script
        import subprocess
        etl_script = """
-- Clear DW
TRUNCATE TABLE HechoTarea;
TRUNCATE TABLE HechoProyecto;
DELETE FROM DimCliente;
DELETE FROM DimEmpleado;
DELETE FROM DimEquipo;
DELETE FROM DimProyecto;

-- Populate DimTiempo with all dates needed
INSERT IGNORE INTO DimTiempo (id_tiempo, fecha, anio, mes, trimestre)
SELECT DISTINCT
    fecha_fin_real,
    fecha_fin_real,
    YEAR(fecha_fin_real),
    MONTH(fecha_fin_real),
    QUARTER(fecha_fin_real)
FROM gestionproyectos_hist.Proyecto
WHERE fecha_fin_real IS NOT NULL
UNION
SELECT DISTINCT
    fecha_fin_real,
    fecha_fin_real,
    YEAR(fecha_fin_real),
    MONTH(fecha_fin_real),
    QUARTER(fecha_fin_real)
FROM gestionproyectos_hist.Tarea
WHERE fecha_fin_real IS NOT NULL;

-- Load dimensions
INSERT INTO DimCliente (id_cliente, nombre, sector)
SELECT id_cliente, nombre, sector
FROM gestionproyectos_hist.Cliente;

INSERT INTO DimEmpleado (id_empleado, nombre, puesto)
SELECT id_empleado, nombre, puesto
FROM gestionproyectos_hist.Empleado;

INSERT INTO DimEquipo (id_equipo, nombre_equipo, descripcion)
SELECT id_equipo, nombre_equipo, descripcion
FROM gestionproyectos_hist.Equipo;

-- Load DimProyecto (SOLO proyectos Completados o Cancelados)
INSERT INTO DimProyecto (id_proyecto, nombre_proyecto, fecha_inicio_plan, fecha_fin_plan, presupuesto, estado, progreso_porcentaje)
SELECT 
    p.id_proyecto, 
    p.nombre, 
    p.fecha_inicio, 
    p.fecha_fin_plan, 
    p.presupuesto,
    e.nombre_estado,
    CASE
        WHEN e.id_estado = 4 THEN 100.0  -- Completado
        WHEN e.id_estado = 5 THEN 0.0    -- Cancelado
        ELSE (
            SELECT (COUNT(CASE WHEN t.id_estado = 4 THEN 1 END) * 100.0 / COUNT(*))
            FROM gestionproyectos_hist.Tarea t
            WHERE t.id_proyecto = p.id_proyecto
        )
    END as progreso_porcentaje
FROM gestionproyectos_hist.Proyecto p
LEFT JOIN gestionproyectos_hist.Estado e ON p.id_estado = e.id_estado
WHERE p.id_estado IN (4, 5);  -- Solo Completados y Cancelados

-- Load HechoProyecto WITH id_equipo (SOLO proyectos Completados o Cancelados)
INSERT INTO HechoProyecto (
    id_proyecto, id_cliente, id_empleado_gerente, id_equipo,
    id_tiempo_fin_real, presupuesto, costo_real_proy,
    duracion_planificada, duracion_real, tareas_total,
    tareas_completadas, tareas_canceladas,
    horas_plan_total, horas_reales_total,
    cumplimiento_tiempo, cumplimiento_presupuesto, variacion_costos, variacion_cronograma
)
SELECT 
    p.id_proyecto,
    p.id_cliente,
    p.id_empleado_gerente,
    (
        SELECT teh.id_equipo
        FROM gestionproyectos_hist.Tarea t
        JOIN gestionproyectos_hist.TareaEquipoHist teh ON t.id_tarea = teh.id_tarea
        WHERE t.id_proyecto = p.id_proyecto
        GROUP BY teh.id_equipo
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) as id_equipo,
    COALESCE(p.fecha_fin_real, p.fecha_fin_plan, CURRENT_DATE),
    p.presupuesto,
    p.costo_real,
    DATEDIFF(p.fecha_fin_plan, p.fecha_inicio) as duracion_planificada,
    DATEDIFF(COALESCE(p.fecha_fin_real, CURRENT_DATE), p.fecha_inicio) as duracion_real,
    (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto),
    (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto AND t.id_estado = 4),
    (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto AND t.id_estado = 5),
    (SELECT COALESCE(SUM(horas_plan), 0) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto),
    (SELECT COALESCE(SUM(horas_reales), 0) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto),
    -- Cumplimiento de tiempo: 1 si terminó a tiempo o antes, 0 si se retrasó
    CASE 
        WHEN DATEDIFF(COALESCE(p.fecha_fin_real, CURRENT_DATE), p.fecha_inicio) <= DATEDIFF(p.fecha_fin_plan, p.fecha_inicio) 
        THEN 1 
        ELSE 0 
    END as cumplimiento_tiempo,
    -- Cumplimiento de presupuesto: 1 si gastó igual o menos, 0 si se excedió
    CASE 
        WHEN p.costo_real <= p.presupuesto 
        THEN 1 
        ELSE 0 
    END as cumplimiento_presupuesto,
    -- Variación de costos: diferencia entre costo real y presupuesto
    (p.costo_real - p.presupuesto) as variacion_costos,
    -- Variación de cronograma: diferencia en días entre duración real y planificada
    (DATEDIFF(COALESCE(p.fecha_fin_real, CURRENT_DATE), p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio)) as variacion_cronograma
FROM gestionproyectos_hist.Proyecto p
WHERE p.id_estado IN (4, 5)  -- Solo Completados y Cancelados
  AND p.fecha_fin_real IS NOT NULL;  -- Solo con fecha de finalización

-- Load HechoTarea (tareas de proyectos finalizados)
INSERT INTO HechoTarea (
    id_tarea, id_proyecto, id_equipo, id_tiempo_fin_real,
    horas_plan, horas_reales, variacion_horas, cumplimiento_tiempo
)
SELECT 
    t.id_tarea,
    t.id_proyecto,
    (
        SELECT teh.id_equipo
        FROM gestionproyectos_hist.TareaEquipoHist teh
        WHERE teh.id_tarea = t.id_tarea
        LIMIT 1
    ) as id_equipo,
    COALESCE(t.fecha_fin_real, t.fecha_fin_plan, CURRENT_DATE),
    t.horas_plan,
    t.horas_reales,
    (t.horas_reales - t.horas_plan) as variacion_horas,
    -- Cumplimiento: 1 si terminó a tiempo, 0 si se retrasó
    CASE 
        WHEN t.fecha_fin_real IS NOT NULL 
             AND t.fecha_fin_real <= t.fecha_fin_plan 
        THEN 1 
        ELSE 0 
    END as cumplimiento_tiempo
FROM gestionproyectos_hist.Tarea t
WHERE t.id_proyecto IN (
    SELECT id_proyecto 
    FROM gestionproyectos_hist.Proyecto 
    WHERE id_estado IN (4, 5)
);

SELECT 
    COUNT(*) as total_proyectos,
    COUNT(id_equipo) as con_equipo
FROM HechoProyecto;
"""
        
        # Write script to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(etl_script)
            temp_sql = f.name
        
        try:
            # Execute via mysql command
            env = os.environ.copy()
            env['MYSQL_PWD'] = DB_CONFIG.get('password_destino', '')
            
            result = subprocess.run(
                [
                    'mysql',
                    '-u', DB_CONFIG.get('user_destino', 'root'),
                    '-h', DB_CONFIG.get('host_destino', 'localhost'),
                    '-P', str(DB_CONFIG.get('port_destino', 3306)),
                    DB_CONFIG.get('db_destino', 'dw_proyectos_hist')
                ],
                stdin=open(temp_sql, 'r'),
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            
            if result.returncode != 0:
                print(f" ETL SQL failed: {result.stderr}")
                return jsonify({
                    'success': False,
                    'message': f'ETL failed: {result.stderr[-200:]}',
                    'returncode': result.returncode
                }), 500
            
            print(" ETL completado exitosamente")
            
        finally:
            os.unlink(temp_sql)
        
        # Estadísticas post-carga
        try:
            conn = get_connection('destino'); cursor = conn.cursor()
            def _count(sql):
                try:
                    cursor.execute(sql); return int(cursor.fetchone()[0])
                except Exception:
                    return 0
            stats = {
                'HechoProyecto': _count('SELECT COUNT(*) FROM HechoProyecto'),
                'HechoTarea': _count('SELECT COUNT(*) FROM HechoTarea'),
                'DimCliente': _count('SELECT COUNT(*) FROM DimCliente'),
                'DimEquipo': _count('SELECT COUNT(*) FROM DimEquipo'),
                'proyectos_con_equipo': _count('SELECT COUNT(*) FROM HechoProyecto WHERE id_equipo IS NOT NULL')
            }
            cursor.close(); conn.close()
        except Exception as db_error:
            stats = {}
            print(f" No se pudieron obtener estadísticas post-ETL: {db_error}")

        return jsonify({
            'success': True,
            'message': 'ETL completado exitosamente',
            'registros_procesados': stats,
            'total': sum(stats.values()) if stats else 0
        })

    except Exception as e:
        import traceback
        return jsonify({'success': False,'message': f'Error ejecutando ETL: {e}','traceback': traceback.format_exc()}), 500

@app.route('/datos-origen/todas-tablas', methods=['GET'])
def obtener_todas_tablas_origen():
    """Obtiene datos de todas las tablas de la base de datos origen"""
    try:
        conn = get_connection('origen')
        cursor = conn.cursor()
        
        # Definir el orden y configuración de las tablas
        tablas_config = [
            {'nombre': 'Estado', 'limite': 10},
            {'nombre': 'Cliente', 'limite': 10},
            {'nombre': 'Empleado', 'limite': 10},
            {'nombre': 'Equipo', 'limite': 10},
            {'nombre': 'Proyecto', 'limite': 15},
            {'nombre': 'MiembroEquipo', 'limite': 15},
            {'nombre': 'Tarea', 'limite': 15}
        ]
        
        resultado = []
        
        for tabla_config in tablas_config:
            tabla = tabla_config['nombre']
            limite = tabla_config['limite']
            
            try:
                # Obtener el total de registros
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                total = cursor.fetchone()[0]
                
                # Obtener nombres de columnas
                cursor.execute(f"DESCRIBE {tabla}")
                columnas_info = cursor.fetchall()
                columnas = [col[0] for col in columnas_info]
                
                # Obtener datos (limitados)
                cursor.execute(f"SELECT * FROM {tabla} ORDER BY {columnas[0]} DESC LIMIT {limite}")
                filas = cursor.fetchall()
                
                # Convertir a diccionarios
                datos = []
                for fila in filas:
                    fila_dict = {}
                    for i, valor in enumerate(fila):
                        # Convertir tipos especiales a string para JSON
                        if isinstance(valor, (date, datetime)):
                            fila_dict[columnas[i]] = valor.strftime('%Y-%m-%d')
                        elif isinstance(valor, Decimal):
                            fila_dict[columnas[i]] = float(valor)
                        else:
                            fila_dict[columnas[i]] = valor
                    datos.append(fila_dict)
                
                resultado.append({
                    'tabla': tabla,
                    'total_registros': total,
                    'registros_mostrados': len(datos),
                    'columnas': columnas,
                    'datos': datos
                })
                
            except Exception as e:
                resultado.append({
                    'tabla': tabla,
                    'error': str(e),
                    'total_registros': 0,
                    'registros_mostrados': 0,
                    'columnas': [],
                    'datos': []
                })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'tablas': resultado
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo datos: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/limpiar-datos', methods=['DELETE'])
def limpiar_datos():
    """Limpiar todas las tablas"""
    try:
        # Limpiar origen
        conn_origen = get_connection('origen')
        cursor_origen = conn_origen.cursor()
        
        cursor_origen.execute("SET FOREIGN_KEY_CHECKS=0")
        tablas_origen = ['TareaEquipoHist', 'Tarea', 'Proyecto', 'MiembroEquipo', 'Estado', 'Equipo', 'Empleado', 'Cliente']
        for tabla in tablas_origen:
            cursor_origen.execute(f"TRUNCATE TABLE {tabla}")
        cursor_origen.execute("SET FOREIGN_KEY_CHECKS=1")
        
        cursor_origen.close()
        conn_origen.close()
        
        # Limpiar destino
        conn_destino = get_connection('destino')
        cursor_destino = conn_destino.cursor()
        
        cursor_destino.execute("SET FOREIGN_KEY_CHECKS=0")
        tablas_destino = ['HechoTarea', 'HechoProyecto', 'DimTiempo', 'DimProyecto', 'DimEquipo', 'DimEmpleado', 'DimCliente']
        for tabla in tablas_destino:
            cursor_destino.execute(f"TRUNCATE TABLE {tabla}")
        cursor_destino.execute("SET FOREIGN_KEY_CHECKS=1")
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Todas las tablas han sido limpiadas'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/generar-datos', methods=['POST'])
def generar_datos_personalizados():
    """Generar datos de prueba personalizados usando generar_datos_final.py (fixed schema).
    Parámetros JSON: 
      - proyectos: número de proyectos (requerido)
      - empleados: total empleados O empleados_por_proyecto (opcional)
      - tareas_por_proyecto: tareas por proyecto (opcional, default 10)
      - limpiar: bool (opcional, default False)
    """
    try:
        data = request.get_json() or {}
        
        # Obtener proyectos (siempre requerido)
        proyectos = int(data.get('proyectos', 25))
        
        # Si viene 'empleados' (total), calcular empleados_por_proyecto
        if 'empleados' in data:
            empleados_total = int(data['empleados'])
            empleados_pp = max(1, empleados_total // proyectos) if proyectos > 0 else 5
        else:
            empleados_pp = int(data.get('empleados_por_proyecto', 5))
        
        tareas_pp = int(data.get('tareas_por_proyecto', 10))
        limpiar = bool(data.get('limpiar', False))
        
        print(f" Generación: {proyectos} proyectos × {empleados_pp} empleados × {tareas_pp} tareas (limpiar={limpiar})")
        
        # Call fixed generator via subprocess (from project root)
        import subprocess
        import json
        
        # Get project root (2 levels up from backend/)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        generator_path = os.path.join(project_root, '01_GestionProyectos', 'datos', 'generar_datos_final.py')
        
        # Set environment variables for generator
        env = os.environ.copy()
        env['CANTIDAD_PROYECTOS'] = str(proyectos)
        env['EMPLEADOS_POR_PROYECTO'] = str(empleados_pp)
        env['TAREAS_POR_PROYECTO'] = str(tareas_pp)
        env['LIMPIAR_TABLAS'] = 'true' if limpiar else 'false'
        
        result = subprocess.run(
            ['python3', generator_path],
            capture_output=True,
            text=True,
            env=env,
            timeout=600,  # Aumentado timeout para 650 proyectos
            cwd=project_root
        )
        
        if result.returncode == 0:
            # Parse output for stats
            output = result.stdout
            stats = {
                'proyectos': proyectos,
                'empleados': proyectos * empleados_pp,
                'tareas': proyectos * tareas_pp,
                'equipos': proyectos
            }
            return jsonify({
                'success': True,
                'message': 'Generación completada',
                'stats': stats,
                'output': output[-500:] if len(output) > 500 else output
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Generator failed: {result.stderr[-500:]}',
                'returncode': result.returncode
            }), 500
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f" ERROR generando datos: {str(e)}")
        print(error_trace)
        return jsonify({'success': False,'message': str(e),'traceback': error_trace}), 500

@app.route('/buscar-trazabilidad', methods=['POST'])
def buscar_trazabilidad():
    """Buscar un registro en BD Origen y verificar si está en DataWarehouse"""
    try:
        data = request.get_json()
        tipo = data.get('tipo')  # 'proyecto', 'cliente', 'empleado', 'tarea'
        criterio = data.get('criterio')  # 'id' o 'nombre'
        valor = data.get('valor')
        
        if not tipo or not criterio or not valor:
            return jsonify({
                'success': False,
                'message': 'Faltan parámetros requeridos (tipo, criterio, valor)'
            }), 400
        
        conn_origen = get_connection('origen')
        cursor_origen = conn_origen.cursor(dictionary=True)
        
        conn_destino = get_connection('destino')
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        resultado = {
            'success': True,
            'tipo': tipo,
            'encontrado_origen': False,
            'encontrado_dw': False,
            'datos_origen': None,
            'datos_dw': None,
            'mensaje': ''
        }
        
        # PROYECTOS
        if tipo == 'proyecto':
            if criterio == 'id':
                cursor_origen.execute("""
                    SELECT p.*, c.nombre as nombre_cliente, e.nombre as nombre_gerente, 
                           est.nombre_estado
                    FROM Proyecto p
                    LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
                    LEFT JOIN Empleado e ON p.id_empleado_gerente = e.id_empleado
                    LEFT JOIN Estado est ON p.id_estado = est.id_estado
                    WHERE p.id_proyecto = %s
                """, (valor,))
            else:
                cursor_origen.execute("""
                    SELECT p.*, c.nombre as nombre_cliente, e.nombre as nombre_gerente,
                           est.nombre_estado
                    FROM Proyecto p
                    LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
                    LEFT JOIN Empleado e ON p.id_empleado_gerente = e.id_empleado
                    LEFT JOIN Estado est ON p.id_estado = est.id_estado
                    WHERE p.nombre LIKE %s
                """, (f'%{valor}%',))
            
            proyecto_origen = cursor_origen.fetchone()
            
            if proyecto_origen:
                resultado['encontrado_origen'] = True
                for key, val in proyecto_origen.items():
                    if isinstance(val, (date, datetime)):
                        proyecto_origen[key] = val.isoformat()
                    elif isinstance(val, Decimal):
                        proyecto_origen[key] = float(val)
                resultado['datos_origen'] = proyecto_origen
                
                # Buscar en DW
                cursor_destino.execute("""
                    SELECT hp.*, dp.nombre_proyecto
                    FROM HechoProyecto hp
                    LEFT JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
                    WHERE hp.id_proyecto = %s
                """, (proyecto_origen['id_proyecto'],))
                proyecto_dw = cursor_destino.fetchone()
                
                if proyecto_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in proyecto_dw.items():
                        if isinstance(val, (date, datetime)):
                            proyecto_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            proyecto_dw[key] = float(val)
                    resultado['datos_dw'] = proyecto_dw
                    resultado['mensaje'] = '✓ Proyecto encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = 'Proyecto en Origen pero no en DW (solo se cargan proyectos Completados o Cancelados)'
            else:
                resultado['mensaje'] = 'Proyecto no encontrado en Base Origen'
        
        # CLIENTES
        elif tipo == 'cliente':
            if criterio == 'id':
                cursor_origen.execute("SELECT * FROM Cliente WHERE id_cliente = %s", (valor,))
            else:
                cursor_origen.execute("SELECT * FROM Cliente WHERE nombre LIKE %s", (f'%{valor}%',))
            
            cliente_origen = cursor_origen.fetchone()
            
            if cliente_origen:
                resultado['encontrado_origen'] = True
                for key, val in cliente_origen.items():
                    if isinstance(val, (date, datetime)):
                        cliente_origen[key] = val.isoformat()
                    elif isinstance(val, Decimal):
                        cliente_origen[key] = float(val)
                resultado['datos_origen'] = cliente_origen
                
                # Buscar en DW
                cursor_destino.execute("""
                    SELECT * FROM DimCliente WHERE id_cliente = %s
                """, (cliente_origen['id_cliente'],))
                cliente_dw = cursor_destino.fetchone()
                
                if cliente_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in cliente_dw.items():
                        if isinstance(val, (date, datetime)):
                            cliente_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            cliente_dw[key] = float(val)
                    resultado['datos_dw'] = cliente_dw
                    resultado['mensaje'] = '✓ Cliente encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = 'Cliente en Origen pero no en DW'
            else:
                resultado['mensaje'] = 'Cliente no encontrado en Base Origen'
        
        # EMPLEADOS
        elif tipo == 'empleado':
            if criterio == 'id':
                cursor_origen.execute("SELECT * FROM Empleado WHERE id_empleado = %s", (valor,))
            else:
                cursor_origen.execute("SELECT * FROM Empleado WHERE nombre LIKE %s", (f'%{valor}%',))
            
            empleado_origen = cursor_origen.fetchone()
            
            if empleado_origen:
                resultado['encontrado_origen'] = True
                for key, val in empleado_origen.items():
                    if isinstance(val, (date, datetime)):
                        empleado_origen[key] = val.isoformat()
                    elif isinstance(val, Decimal):
                        empleado_origen[key] = float(val)
                resultado['datos_origen'] = empleado_origen
                
                # Buscar en DW
                cursor_destino.execute("""
                    SELECT * FROM DimEmpleado WHERE id_empleado = %s
                """, (empleado_origen['id_empleado'],))
                empleado_dw = cursor_destino.fetchone()
                
                if empleado_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in empleado_dw.items():
                        if isinstance(val, (date, datetime)):
                            empleado_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            empleado_dw[key] = float(val)
                    resultado['datos_dw'] = empleado_dw
                    resultado['mensaje'] = '✓ Empleado encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = 'Empleado en Origen pero no en DW'
            else:
                resultado['mensaje'] = 'Empleado no encontrado en Base Origen'
        
        # EQUIPOS
        elif tipo == 'equipo':
            if criterio == 'id':
                cursor_origen.execute("SELECT * FROM Equipo WHERE id_equipo = %s", (valor,))
            else:
                cursor_origen.execute("SELECT * FROM Equipo WHERE nombre_equipo LIKE %s", (f'%{valor}%',))
            
            equipo_origen = cursor_origen.fetchone()
            
            if equipo_origen:
                resultado['encontrado_origen'] = True
                for key, val in equipo_origen.items():
                    if isinstance(val, (date, datetime)):
                        equipo_origen[key] = val.isoformat()
                    elif isinstance(val, Decimal):
                        equipo_origen[key] = float(val)
                resultado['datos_origen'] = equipo_origen
                
                # Buscar en DW
                cursor_destino.execute("""
                    SELECT * FROM DimEquipo WHERE id_equipo = %s
                """, (equipo_origen['id_equipo'],))
                equipo_dw = cursor_destino.fetchone()
                
                if equipo_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in equipo_dw.items():
                        if isinstance(val, (date, datetime)):
                            equipo_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            equipo_dw[key] = float(val)
                    resultado['datos_dw'] = equipo_dw
                    resultado['mensaje'] = '✓ Equipo encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = 'Equipo en Origen pero no en DW'
            else:
                resultado['mensaje'] = 'Equipo no encontrado en Base Origen'
        
        # TAREAS
        elif tipo == 'tarea':
            if criterio == 'id':
                cursor_origen.execute("""
                    SELECT 
                           t.*, 
                           p.nombre as nombre_proyecto, 
                           p.id_estado as id_estado_proyecto,
                           e.nombre as nombre_empleado,
                           est.nombre_estado as nombre_estado
                    FROM Tarea t
                    LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
                    LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
                    LEFT JOIN Estado est ON t.id_estado = est.id_estado
                    WHERE t.id_tarea = %s
                """, (valor,))
            else:
                cursor_origen.execute("""
                    SELECT 
                           t.*, 
                           p.nombre as nombre_proyecto, 
                           p.id_estado as id_estado_proyecto,
                           e.nombre as nombre_empleado,
                           est.nombre_estado as nombre_estado
                    FROM Tarea t
                    LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
                    LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
                    LEFT JOIN Estado est ON t.id_estado = est.id_estado
                    WHERE t.nombre_tarea LIKE %s
                """, (f'%{valor}%',))
            
            tarea_origen = cursor_origen.fetchone()
            
            if tarea_origen:
                resultado['encontrado_origen'] = True
                for key, val in tarea_origen.items():
                    if isinstance(val, (date, datetime)):
                        tarea_origen[key] = val.isoformat()
                    elif isinstance(val, Decimal):
                        tarea_origen[key] = float(val)
                resultado['datos_origen'] = tarea_origen
                
                # Buscar en DW
                cursor_destino.execute("""
                    SELECT ht.*, dp.nombre_proyecto
                    FROM HechoTarea ht
                    LEFT JOIN DimProyecto dp ON ht.id_proyecto = dp.id_proyecto
                    WHERE ht.id_tarea = %s
                """, (tarea_origen['id_tarea'],))
                tarea_dw = cursor_destino.fetchone()
                
                if tarea_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in tarea_dw.items():
                        if isinstance(val, (date, datetime)):
                            tarea_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            tarea_dw[key] = float(val)
                    resultado['datos_dw'] = tarea_dw
                    resultado['mensaje'] = ' Tarea encontrada en ambas bases de datos'
                else:
                    # Explicar motivo probable: ETL solo carga tareas de proyectos completados/cancelados
                    id_estado_proyecto = tarea_origen.get('id_estado_proyecto')
                    # Mapeo habitual (local): 3=Completado, 4=Cancelado. En distribuido pueden variar.
                    if id_estado_proyecto not in (3, 4, 12, 13, 14):
                        resultado['mensaje'] = ' Tarea encontrada en BD Origen pero NO en DataWarehouse (proyecto no finalizado)'
                        resultado['motivo_no_dw'] = 'El ETL carga tareas solo de proyectos Completados/Cancelados.'
                    else:
                        # Intento adicional: buscar por id_proyecto e id_empleado como heurística
                        try:
                            cursor_destino.execute(
                                """
                                SELECT ht.*, dp.nombre_proyecto
                                FROM HechoTarea ht
                                LEFT JOIN DimProyecto dp ON ht.id_proyecto = dp.id_proyecto
                                WHERE ht.id_proyecto = %s AND (%s IS NULL OR ht.id_empleado = %s)
                                ORDER BY ht.id_hecho_tarea DESC LIMIT 1
                                """,
                                (
                                    tarea_origen.get('id_proyecto'),
                                    tarea_origen.get('id_empleado'),
                                    tarea_origen.get('id_empleado')
                                )
                            )
                            tarea_dw_alt = cursor_destino.fetchone()
                            if tarea_dw_alt:
                                for key, val in tarea_dw_alt.items():
                                    if isinstance(val, (date, datetime)):
                                        tarea_dw_alt[key] = val.isoformat()
                                    elif isinstance(val, Decimal):
                                        tarea_dw_alt[key] = float(val)
                                resultado['datos_dw_sugerido'] = tarea_dw_alt
                                resultado['mensaje'] = ' No se encontró por id_tarea, pero existe una tarea probable relacionada en DW'
                            else:
                                resultado['mensaje'] = ' Tarea encontrada en BD Origen pero NO en DataWarehouse'
                        except Exception:
                            resultado['mensaje'] = ' Tarea encontrada en BD Origen pero NO en DataWarehouse'
            else:
                resultado['mensaje'] = ' Tarea no encontrada en BD Origen'
        
        else:
            resultado['success'] = False
            resultado['mensaje'] = f' Tipo "{tipo}" no soportado'
        
        cursor_origen.close()
        conn_origen.close()
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify(resultado)
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error en búsqueda: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# ========================================
# ENDPOINTS OLAP PARA DSS
# ========================================

@app.route('/olap/kpis', methods=['GET'])
def get_olap_kpis():
    """
    Endpoint para obtener KPIs con capacidad de drill-down
    Parámetros: dim (dimensiones), cliente_id, equipo_id, anio, trimestre
    """
    try:
        # Parámetros de filtro
        dimensiones = request.args.get('dim', '').split(',') if request.args.get('dim') else []
        cliente_id = request.args.get('cliente_id', type=int)
        equipo_id = request.args.get('equipo_id', type=int)
        anio = request.args.get('anio', type=int)
        trimestre = request.args.get('trimestre', type=int)
        nivel = request.args.get('nivel', 'DETALLADO')
        
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Construir consulta dinámica usando el procedimiento OLAP
        import sys
        print(f"DEBUG: Llamando SP con: nivel={nivel}, cliente={cliente_id}, equipo={equipo_id}, anio={anio}, trimestre={trimestre}", flush=True, file=sys.stderr)
        cursor_destino.callproc('sp_olap_drill_down_proyectos', [
            nivel, cliente_id, equipo_id, anio, trimestre
        ])
        
        resultados = []
        for result in cursor_destino.stored_results():
            rows = result.fetchall()
            print(f"DEBUG: Recibidas {len(rows)} filas del SP", flush=True, file=sys.stderr)
            if rows:
                first_row = dict(rows[0])
                print(f"DEBUG: Primera fila - Completados: {first_row.get('proyectos_completados')}, Progreso: {first_row.get('progreso_promedio')}", flush=True, file=sys.stderr)
            resultados.extend(rows)
        
        # Convertir Decimal a float para JSON
        for row in resultados:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'data': resultados,
            'filtros_aplicados': {
                'dimensiones': dimensiones,
                'cliente_id': cliente_id,
                'equipo_id': equipo_id,
                'anio': anio,
                'trimestre': trimestre,
                'nivel': nivel
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error en consulta OLAP KPIs: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/olap/series', methods=['GET'])
def get_olap_series():
    """
    Endpoint para series temporales OLAP
    Parámetros: granularidad (mes|trimestre|anio), metrica, periodo_meses
    """
    try:
        granularidad = request.args.get('granularidad', 'mes')
        metrica = request.args.get('metrica', 'proyectos')
        periodo_meses = request.args.get('periodo_meses', 12, type=int)
        
        # Validar parámetros
        if granularidad not in ['mes', 'trimestre', 'anio']:
            return jsonify({
                'success': False,
                'message': 'Granularidad debe ser: mes, trimestre, o anio'
            }), 400
            
        if metrica not in ['proyectos', 'presupuesto', 'horas']:
            return jsonify({
                'success': False,
                'message': 'Métrica debe ser: proyectos, presupuesto, o horas'
            }), 400
        
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Llamar procedimiento para series temporales
        cursor_destino.callproc('sp_olap_series_temporales', [
            granularidad, metrica, periodo_meses
        ])
        
        resultados = []
        for result in cursor_destino.stored_results():
            resultados.extend(result.fetchall())
        
        # Convertir Decimal a float para JSON
        for row in resultados:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'data': resultados,
            'configuracion': {
                'granularidad': granularidad,
                'metrica': metrica,
                'periodo_meses': periodo_meses
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error en series temporales OLAP: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/olap/kpis-ejecutivos', methods=['GET'])
def get_kpis_ejecutivos():
    """
    Endpoint para KPIs ejecutivos del dashboard principal
    """
    try:
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener KPIs ejecutivos
        cursor_destino.execute("""
            SELECT * FROM vw_olap_kpis_ejecutivos 
            ORDER BY fecha DESC 
            LIMIT 12
        """)
        
        kpis_temporales = cursor_destino.fetchall()
        
        # Obtener resumen por sector
        cursor_destino.execute("""
            SELECT * FROM vw_olap_sector_performance 
            WHERE anio = YEAR(CURDATE())
            ORDER BY facturacion_sector DESC
        """)
        
        performance_sectores = cursor_destino.fetchall()
        
        # Convertir Decimal a float
        for row in kpis_temporales + performance_sectores:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                elif isinstance(value, date):
                    row[key] = value.isoformat()
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'kpis_temporales': kpis_temporales,
            'performance_sectores': performance_sectores
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error en KPIs ejecutivos: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/olap/rollup', methods=['GET'])
def get_olap_rollup():
    """
    Endpoint para obtener datos con ROLLUP (agregaciones jerárquicas)
    """
    try:
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener datos ROLLUP
        cursor_destino.execute("SELECT * FROM vw_olap_proyectos_rollup")
        datos_rollup = cursor_destino.fetchall()
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'datos': datos_rollup,
            'total_registros': len(datos_rollup)
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error en OLAP ROLLUP: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/olap/dimensiones', methods=['GET'])
def get_dimensiones():
    """
    Endpoint para obtener valores únicos de dimensiones para filtros
    """
    try:
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener clientes
        cursor_destino.execute("SELECT id_cliente, nombre AS nombre_cliente, sector FROM DimCliente ORDER BY nombre")
        clientes = cursor_destino.fetchall()
        
        # Obtener equipos
        cursor_destino.execute("SELECT id_equipo, nombre_equipo, descripcion AS tipo FROM DimEquipo ORDER BY nombre_equipo")
        equipos = cursor_destino.fetchall()
        
        # Obtener años disponibles
        cursor_destino.execute("SELECT DISTINCT anio FROM DimTiempo WHERE anio <= YEAR(CURDATE()) ORDER BY anio DESC")
        anios = cursor_destino.fetchall()
        
        # Obtener sectores únicos
        cursor_destino.execute("SELECT DISTINCT sector FROM DimCliente ORDER BY sector")
        sectores = cursor_destino.fetchall()
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'dimensiones': {
                'clientes': clientes,
                'equipos': equipos,
                'anios': anios,
                'sectores': sectores
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo dimensiones: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# ========================================
# ENDPOINTS BSC/OKR PARA DSS
# ========================================

@app.route('/bsc/okr', methods=['GET'])
def get_bsc_okr():
    """
    Endpoint para obtener tablero BSC consolidado con OKRs
    """
    try:
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener tablero BSC consolidado
        cursor_destino.execute("SELECT * FROM vw_bsc_tablero_consolidado ORDER BY perspectiva, codigo_objetivo")
        objetivos = cursor_destino.fetchall()
        
        # Obtener detalle de KRs
        cursor_destino.execute("SELECT * FROM vw_bsc_krs_detalle ORDER BY perspectiva, codigo_objetivo, codigo_kr")
        krs = cursor_destino.fetchall()
        
        # Organizar datos por perspectiva
        perspectivas = {}
        for objetivo in objetivos:
            perspectiva = objetivo['perspectiva']
            if perspectiva not in perspectivas:
                perspectivas[perspectiva] = {
                    'nombre': perspectiva,
                    'avance_global': 0,
                    'objetivos': [],
                    'resumen': {
                        'total_objetivos': 0,
                        'objetivos_verde': 0,
                        'objetivos_amarillo': 0,
                        'objetivos_rojo': 0,
                        'avance_promedio': 0
                    }
                }
            
            # Convertir Decimal a float
            for key, value in objetivo.items():
                if isinstance(value, Decimal):
                    objetivo[key] = float(value)
                elif isinstance(value, date):
                    objetivo[key] = value.isoformat()
            
            # Mapear campos a los nombres esperados por el frontend
            objetivo['nombre'] = objetivo.get('objetivo_nombre', '')
            objetivo['descripcion'] = objetivo.get('objetivo_descripcion', '')
            objetivo['avance'] = objetivo.get('avance_objetivo_porcentaje', 0)
            
            # Agregar KRs al objetivo
            objetivo['krs'] = []
            for kr in krs:
                if kr['codigo_objetivo'] == objetivo['codigo_objetivo']:
                    # Convertir Decimal a float en KRs
                    for key, value in kr.items():
                        if isinstance(value, Decimal):
                            kr[key] = float(value)
                        elif isinstance(value, date):
                            kr[key] = value.isoformat()
                    objetivo['krs'].append(kr)
            
            perspectivas[perspectiva]['objetivos'].append(objetivo)
            
            # Actualizar resumen de perspectiva
            resumen = perspectivas[perspectiva]['resumen']
            resumen['total_objetivos'] += 1
            if objetivo['estado_objetivo'] == 'Verde':
                resumen['objetivos_verde'] += 1
            elif objetivo['estado_objetivo'] == 'Amarillo':
                resumen['objetivos_amarillo'] += 1
            else:
                resumen['objetivos_rojo'] += 1
            
            if objetivo['avance_objetivo_porcentaje']:
                resumen['avance_promedio'] += objetivo['avance_objetivo_porcentaje']
        
        # Calcular promedios y avance global
        for perspectiva in perspectivas.values():
            if perspectiva['resumen']['total_objetivos'] > 0:
                perspectiva['resumen']['avance_promedio'] /= perspectiva['resumen']['total_objetivos']
                perspectiva['avance_global'] = perspectiva['resumen']['avance_promedio']
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'perspectivas': perspectivas
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo BSC/OKR: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


# ================================================================
# NOTA: Endpoint deshabilitado - El BSC debe mostrar solo datos del ETL
# según los requisitos del proyecto (visualización, no captura manual)
# ================================================================
# @app.route('/bsc/medicion', methods=['POST'])
# def registrar_medicion_okr():
#     """
#     Endpoint para registrar nueva medición de un KR
#     DESHABILITADO: Los datos deben venir del sistema de gestión vía ETL
#     """
#     try:
#         datos = request.get_json()
#         
#         # Validar campos requeridos
#         campos_requeridos = ['id_kr', 'valor_observado', 'fecha_medicion']
#         for campo in campos_requeridos:
#             if campo not in datos:
#                 return jsonify({
#                     'success': False,
#                     'message': f'Campo requerido faltante: {campo}'
#                 }), 400
#         
#         # Conectar a DataWarehouse
#         conn_destino = mysql.connector.connect(
#             host=DB_CONFIG['host_destino'],
#             port=DB_CONFIG['port_destino'],
#             user=DB_CONFIG['user_destino'],
#             password=DB_CONFIG['password_destino'],
#             database=DB_CONFIG['db_destino']
#         )
#         cursor_destino = conn_destino.cursor()
#         
#         # Llamar procedimiento para registrar medición
#         cursor_destino.callproc('sp_registrar_medicion_okr', [
#             datos['id_kr'],
#             datos['valor_observado'],
#             datos['fecha_medicion'],
#             datos.get('comentario', ''),
#             datos.get('fuente_medicion', 'Dashboard Manual'),
#             datos.get('usuario_registro', 'dashboard_user')
#         ])
#         
#         conn_destino.commit()
#         cursor_destino.close()
#         conn_destino.close()
#         
#         return jsonify({
#             'success': True,
#             'message': 'Medición registrada exitosamente'
#         })
#         
#     except Exception as e:
#         import traceback
#         return jsonify({
#             'success': False,
#             'message': f'Error registrando medición: {str(e)}',
#             'traceback': traceback.format_exc()
#         }), 500

@app.route('/bsc/historico-kr/<int:id_kr>', methods=['GET'])
def get_historico_kr(id_kr):
    """
    Endpoint para obtener histórico de mediciones de un KR específico
    """
    try:
        meses = request.args.get('meses', 12, type=int)
        
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener histórico del KR
        cursor_destino.execute("""
            SELECT 
                h.valor_observado,
                h.variacion_absoluta,
                h.variacion_porcentual,
                h.progreso_hacia_meta,
                h.estado_semaforo,
                h.comentario,
                h.fecha_medicion,
                dt.anio,
                dt.mes,
                kr.nombre as kr_nombre,
                kr.meta_objetivo,
                kr.unidad_medida
            FROM HechoOKR h
            JOIN DimTiempo dt ON h.id_tiempo = dt.id_tiempo
            JOIN DimKR kr ON h.id_kr = kr.id_kr
            WHERE h.id_kr = %s 
                AND h.fecha_medicion >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            ORDER BY h.fecha_medicion ASC
        """, (id_kr, meses))
        
        historico = cursor_destino.fetchall()
        
        # Convertir Decimal y date a tipos serializables
        for row in historico:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                elif isinstance(value, date):
                    row[key] = value.isoformat()
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'historico': historico
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo histórico KR: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/bsc/vision-estrategica', methods=['GET'])
def get_vision_estrategica():
    """
    Endpoint para obtener resumen de la visión estratégica
    """
    try:
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Obtener resumen por componente de visión
        cursor_destino.execute("""
            SELECT 
                obj.vision_componente,
                COUNT(obj.id_objetivo) as total_objetivos,
                AVG(bsc.avance_objetivo_porcentaje) as avance_promedio,
                COUNT(CASE WHEN bsc.estado_objetivo = 'Verde' THEN 1 END) as objetivos_verde,
                COUNT(CASE WHEN bsc.estado_objetivo = 'Amarillo' THEN 1 END) as objetivos_amarillo,
                COUNT(CASE WHEN bsc.estado_objetivo = 'Rojo' THEN 1 END) as objetivos_rojo
            FROM DimObjetivo obj
            LEFT JOIN vw_bsc_tablero_consolidado bsc ON obj.id_objetivo = bsc.id_objetivo
            WHERE obj.activo = TRUE
            GROUP BY obj.vision_componente
            ORDER BY avance_promedio DESC
        """)
        
        vision_componentes = cursor_destino.fetchall()
        
        # Convertir Decimal a float
        for row in vision_componentes:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'vision_componentes': vision_componentes,
            'vision_statement': {
                'titulo': 'Transformación Digital para la Excelencia Operacional',
                'descripcion': 'Liderar la transformación digital mediante sistemas de soporte de decisiones, procesos automatizados y analítica avanzada para entregar valor superior a nuestros clientes.',
                'pilares': [
                    'Transformación Digital',
                    'Confiabilidad y Calidad',
                    'Analítica Avanzada',
                    'Automatización de Procesos',
                    'Excelencia Operacional'
                ]
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo visión estratégica: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# ========================================
# ENDPOINTS PREDICCIÓN RAYLEIGH PARA DSS
# ========================================

# Importar módulo Rayleigh
try:
    from rayleigh import generar_prediccion_completa, validar_acceso_pm
except ImportError:
    print(" Advertencia: Módulo Rayleigh no disponible")
    def generar_prediccion_completa(*args, **kwargs):
        return {'success': False, 'message': 'Módulo Rayleigh no disponible'}
    def validar_acceso_pm(headers):
        return False

@app.route('/prediccion/defectos-rayleigh', methods=['POST'])
def predecir_defectos_rayleigh():
    """
    Endpoint para predicción de defectos usando distribución de Rayleigh
    Requiere permisos de Project Manager (control de acceso)
    """
    try:
        # Validar acceso PM
        if not validar_acceso_pm(request.headers):
            return jsonify({
                'success': False,
                'message': 'Acceso denegado. Se requieren permisos de Project Manager.',
                'codigo_error': 'ACCESS_DENIED'
            }), 403
        
        datos = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['tamanio_proyecto', 'duracion_semanas']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido faltante: {campo}'
                }), 400
        
        # Validar rangos
        if datos['tamanio_proyecto'] <= 0 or datos['duracion_semanas'] <= 0:
            return jsonify({
                'success': False,
                'message': 'Tamaño de proyecto y duración deben ser valores positivos'
            }), 400
        
        if datos['duracion_semanas'] > 104:  # Máximo 2 años
            return jsonify({
                'success': False,
                'message': 'Duración máxima permitida: 104 semanas (2 años)'
            }), 400
        
        # Parámetros opcionales con valores por defecto
        complejidad = datos.get('complejidad', 'media')
        tipo_proyecto = datos.get('tipo_proyecto', 'web')
        esfuerzo_testing = datos.get('esfuerzo_testing', 160.0)
        
        # Validar enums
        complejidades_validas = ['baja', 'media', 'alta']
        tipos_validos = ['web', 'movil', 'sistema', 'api']
        
        if complejidad not in complejidades_validas:
            return jsonify({
                'success': False,
                'message': f'Complejidad debe ser una de: {complejidades_validas}'
            }), 400
            
        if tipo_proyecto not in tipos_validos:
            return jsonify({
                'success': False,
                'message': f'Tipo de proyecto debe ser uno de: {tipos_validos}'
            }), 400
        
        # Generar predicción
        prediccion = generar_prediccion_completa(
            tamanio_proyecto=datos['tamanio_proyecto'],
            duracion_semanas=datos['duracion_semanas'],
            complejidad=complejidad,
            tipo_proyecto=tipo_proyecto,
            fecha_inicio=datetime.now(),
            esfuerzo_testing=esfuerzo_testing
        )
        
        # Opcional: guardar predicción en DataWarehouse para auditoría
        if datos.get('guardar_en_dw', False):
            try:
                conn_destino = mysql.connector.connect(
                    host=DB_CONFIG['host_destino'],
                    port=DB_CONFIG['port_destino'],
                    user=DB_CONFIG['user_destino'],
                    password=DB_CONFIG['password_destino'],
                    database=DB_CONFIG['db_destino']
                )
                cursor_destino = conn_destino.cursor()
                
                # Crear tabla de predicciones si no existe
                cursor_destino.execute("""
                    CREATE TABLE IF NOT EXISTS HechoPrediccionDefectos (
                        id_prediccion INT AUTO_INCREMENT PRIMARY KEY,
                        tamanio_proyecto DECIMAL(10,2),
                        duracion_semanas INT,
                        complejidad VARCHAR(20),
                        tipo_proyecto VARCHAR(20),
                        total_defectos_estimado INT,
                        sigma_parametro DECIMAL(8,4),
                        tiempo_pico_semanas DECIMAL(6,2),
                        usuario_solicitud VARCHAR(50),
                        fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        datos_completos_json TEXT
                    )
                """)
                
                # Insertar predicción
                cursor_destino.execute("""
                    INSERT INTO HechoPrediccionDefectos (
                        tamanio_proyecto, duracion_semanas, complejidad, tipo_proyecto,
                        total_defectos_estimado, sigma_parametro, tiempo_pico_semanas,
                        usuario_solicitud, datos_completos_json
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    datos['tamanio_proyecto'],
                    datos['duracion_semanas'],
                    complejidad,
                    tipo_proyecto,
                    prediccion['metricas_proyecto']['total_defectos_estimado'],
                    prediccion['parametros_calibracion']['sigma'],
                    prediccion['metricas_proyecto']['tiempo_pico_semanas'],
                    request.headers.get('X-USER', 'dashboard_pm'),
                    json.dumps(prediccion, default=str)
                ))
                
                conn_destino.commit()
                cursor_destino.close()
                conn_destino.close()
                
                prediccion['guardado_en_dw'] = True
                
            except Exception as e:
                print(f"Error guardando predicción en DW: {e}")
                prediccion['guardado_en_dw'] = False
        
        return jsonify(prediccion)
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error generando predicción: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/prediccion/historico', methods=['GET'])
def get_historico_predicciones():
    """
    Endpoint para obtener histórico de predicciones realizadas
    """
    try:
        # Validar acceso PM
        if not validar_acceso_pm(request.headers):
            return jsonify({
                'success': False,
                'message': 'Acceso denegado. Se requieren permisos de Project Manager.'
            }), 403
        
        limite = request.args.get('limite', 10, type=int)
        usuario = request.args.get('usuario')
        
        # Conectar a DataWarehouse
        conn_destino = mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )
        cursor_destino = conn_destino.cursor(dictionary=True)
        
        # Verificar si tabla existe
        cursor_destino.execute("""
            SELECT COUNT(*) as existe 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'HechoPrediccionDefectos'
        """)
        
        if cursor_destino.fetchone()['existe'] == 0:
            return jsonify({
                'success': True,
                'predicciones': [],
                'mensaje': 'No hay predicciones históricas disponibles'
            })
        
        # Construir query con filtros
        sql_base = """
            SELECT 
                id_prediccion,
                tamanio_proyecto,
                duracion_semanas,
                complejidad,
                tipo_proyecto,
                total_defectos_estimado,
                tiempo_pico_semanas,
                usuario_solicitud,
                fecha_prediccion
            FROM HechoPrediccionDefectos
        """
        
        parametros = []
        if usuario:
            sql_base += " WHERE usuario_solicitud = %s"
            parametros.append(usuario)
        
        sql_base += " ORDER BY fecha_prediccion DESC LIMIT %s"
        parametros.append(limite)
        
        cursor_destino.execute(sql_base, parametros)
        predicciones = cursor_destino.fetchall()
        
        # Convertir Decimal y datetime
        for pred in predicciones:
            for key, value in pred.items():
                if isinstance(value, Decimal):
                    pred[key] = float(value)
                elif isinstance(value, datetime):
                    pred[key] = value.isoformat()
        
        cursor_destino.close()
        conn_destino.close()
        
        return jsonify({
            'success': True,
            'predicciones': predicciones
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error obteniendo histórico: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/prediccion/validar-acceso', methods=['GET'])
def validar_acceso_prediccion():
    """
    Endpoint para validar si el usuario tiene acceso a predicciones
    """
    try:
        tiene_acceso = validar_acceso_pm(request.headers)
        
        return jsonify({
            'success': True,
            'tiene_acceso': tiene_acceso,
            'role_detectado': request.headers.get('X-ROLE', 'no_especificado'),
            'mensaje': 'Acceso autorizado para predicciones' if tiene_acceso else 'Acceso denegado - se requieren permisos PM'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error validando acceso: {str(e)}'
        }), 500


@app.route('/trazabilidad/tarea/<int:id_tarea>', methods=['GET'])
def trazabilidad_tarea(id_tarea: int):
    """Trazabilidad rápida de una tarea por ID.
    Devuelve:
      - Registro en origen (Tarea + Proyecto + Estado + Empleado)
      - Registro en DW (HechoTarea + métricas) si existe
      - Motivo cuando no está en DW (proyecto no finalizado / ETL pendiente)
      - Sugerencias de acción
    """
    try:
        # Conexión y consulta origen (cursor regular para evitar problemas tipados)
        conn_origen = get_connection('origen')
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(
            """
            SELECT 
                t.id_tarea, t.nombre_tarea, t.descripcion, t.fecha_inicio_plan, t.fecha_fin_plan,
                t.fecha_inicio_real, t.fecha_fin_real, t.horas_plan, t.horas_reales,
                t.id_proyecto, t.id_empleado, t.id_estado, t.prioridad, t.progreso_porcentaje,
                t.costo_estimado, t.costo_real, t.fecha_creacion, t.fecha_actualizacion,
                p.nombre AS nombre_proyecto, p.id_estado AS id_estado_proyecto, p.progreso_porcentaje AS progreso_proyecto,
                est.nombre_estado AS nombre_estado_tarea, estp.nombre_estado AS nombre_estado_proyecto,
                e.nombre AS nombre_empleado
            FROM Tarea t
            LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
            LEFT JOIN Estado est ON t.id_estado = est.id_estado
            LEFT JOIN Estado estp ON p.id_estado = estp.id_estado
            LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
            WHERE t.id_tarea = %s
            """,
            (id_tarea,)
        )
        row = cursor_origen.fetchone()
        cols = [d[0] for d in cursor_origen.description] if cursor_origen.description else []

        if not row:
            cursor_origen.close(); conn_origen.close()
            return jsonify({
                'success': True,
                'id_tarea': id_tarea,
                'en_origen': False,
                'en_dw': False,
                'mensaje': 'La tarea no existe en la BD origen',
                'sugerencias': [
                    'Verificar que el ID es correcto',
                    'Regenerar datos si se eliminó recientemente (/generar-datos)'
                ]
            }), 404

        # Transformar fila a dict serializable
        from datetime import date, datetime
        from decimal import Decimal
        tarea_origen = {}
        for i, v in enumerate(row):
            c = cols[i]
            if isinstance(v, (date, datetime)):
                tarea_origen[c] = v.isoformat()
            elif isinstance(v, Decimal):
                tarea_origen[c] = float(v)
            else:
                tarea_origen[c] = v

        # Conexión y consulta destino
        conn_destino = get_connection('destino')
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(
            """
            SELECT ht.id_hecho_tarea, ht.id_tarea, ht.id_proyecto, ht.id_empleado, ht.id_equipo,
                   ht.id_tiempo_inicio_plan, ht.id_tiempo_fin_plan, ht.id_tiempo_inicio_real, ht.id_tiempo_fin_real,
                   ht.duracion_planificada, ht.duracion_real, ht.variacion_cronograma, ht.cumplimiento_tiempo,
                   ht.horas_plan, ht.horas_reales, ht.variacion_horas, ht.eficiencia_horas,
                   ht.costo_estimado, ht.costo_real, ht.variacion_costo, ht.progreso_porcentaje,
                   ht.fecha_carga, ht.fecha_actualizacion, dp.nombre_proyecto
            FROM HechoTarea ht
            LEFT JOIN DimProyecto dp ON ht.id_proyecto = dp.id_proyecto
            WHERE ht.id_tarea = %s
            """,
            (id_tarea,)
        )
        row_dw = cursor_destino.fetchone()
        cols_dw = [d[0] for d in cursor_destino.description] if cursor_destino.description else []

        tarea_dw = None
        if row_dw:
            tarea_dw = {}
            for i, v in enumerate(row_dw):
                c = cols_dw[i]
                if isinstance(v, (date, datetime)):
                    tarea_dw[c] = v.isoformat()
                elif isinstance(v, Decimal):
                    tarea_dw[c] = float(v)
                else:
                    tarea_dw[c] = v

        # Última ETL (tuple)
        cursor_destino.execute("SELECT COALESCE(MAX(fecha_actualizacion), '2000-01-01') FROM HechoTarea")
        ultima_etl_row = cursor_destino.fetchone()
        ultima_etl_vals = list(ultima_etl_row) if ultima_etl_row else []
        ultima_etl = ultima_etl_vals[0] if ultima_etl_vals else '2000-01-01'
        if isinstance(ultima_etl, (date, datetime)):
            ultima_etl = ultima_etl.isoformat()

        # Motivo y sugerencias
        id_estado_proyecto = tarea_origen.get('id_estado_proyecto')
        es_proyecto_finalizado = id_estado_proyecto in (3, 4)
        motivo = None
        sugerencias = []
        if not tarea_dw:
            if not es_proyecto_finalizado:
                motivo = 'Proyecto aún no finalizado (estado distinto de Completado/Cancelado); ETL incremental no carga sus tareas.'
                sugerencias.append('Ejecutar /ejecutar-etl cuando el proyecto cambie a Completado o Cancelado.')
            else:
                motivo = 'La tarea no aparece pese a que el proyecto está finalizado. Puede requerir nueva ejecución ETL.'
                sugerencias.append('Forzar sincronización ejecutando /ejecutar-etl.')
                sugerencias.append('Verificar que la tarea tenga fechas plan/real y horas distintas de NULL.')

        resultado = {
            'success': True,
            'id_tarea': id_tarea,
            'en_origen': True,
            'en_dw': tarea_dw is not None,
            'datos_origen': tarea_origen,
            'datos_dw': tarea_dw,
            'ultima_etl': ultima_etl,
            'motivo_no_dw': motivo,
            'sugerencias': sugerencias
        }

        cursor_origen.close(); conn_origen.close()
        cursor_destino.close(); conn_destino.close()
        return jsonify(resultado)

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'id_tarea': id_tarea,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ========================================
# ENDPOINTS OLAP MEJORADOS CON VISTAS
# ========================================

@app.route('/olap/kpis-v2', methods=['GET'])
def get_olap_kpis_v2():
    """
    Endpoint mejorado para KPIs OLAP usando vistas optimizadas
    Soporta todos los niveles: detallado, por_cliente, por_equipo, por_tiempo, total
    """
    try:
        # Parámetros - normalizar nivel a minúsculas sin importar el formato
        nivel_raw = request.args.get('nivel', 'detallado')
        nivel = nivel_raw.lower().replace('_', '_')  # por_cliente, por_equipo, etc.
        cliente_id = request.args.get('cliente_id', type=int)
        equipo_id = request.args.get('equipo_id', type=int)
        anio = request.args.get('anio', type=int)
        
        conn = get_connection('destino')
        cursor = conn.cursor(dictionary=True)
        
        # Seleccionar vista según nivel
        if nivel == 'total':
            query = "SELECT * FROM vw_olap_total"
            
        elif nivel == 'por_cliente':
            query = "SELECT * FROM vw_olap_por_cliente"
            if cliente_id:
                query += f" WHERE id_cliente = {cliente_id}"
            query += " ORDER BY total_proyectos DESC"
            
        elif nivel == 'por_equipo':
            query = "SELECT * FROM vw_olap_por_equipo"
            if equipo_id:
                query += f" WHERE id_equipo = {equipo_id}"
            query += " ORDER BY total_proyectos DESC"
            
        elif nivel == 'por_tiempo':
            query = "SELECT * FROM vw_olap_por_anio"
            if anio:
                query += f" WHERE anio = {anio}"
            query += " ORDER BY anio DESC"
            
        else:  # detallado
            query = "SELECT * FROM vw_olap_detallado"
            conditions = []
            if cliente_id:
                # Necesitamos join para filtrar por cliente en detallado
                query = """
                SELECT d.*, dc.id_cliente 
                FROM vw_olap_detallado d
                JOIN HechoProyecto hp ON d.id_proyecto = hp.id_proyecto
                JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
                """
                conditions.append(f"dc.id_cliente = {cliente_id}")
            if equipo_id:
                if not cliente_id:
                    query = """
                    SELECT d.*, de.id_equipo
                    FROM vw_olap_detallado d
                    JOIN HechoProyecto hp ON d.id_proyecto = hp.id_proyecto
                    JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
                    """
                conditions.append(f"de.id_equipo = {equipo_id}")
            if anio:
                conditions.append(f"anio = {anio}")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY fecha DESC LIMIT 100"
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        # Convertir Decimal a float
        for row in resultados:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
                elif isinstance(value, date):
                    row[key] = value.isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'nivel': nivel,
            'total_resultados': len(resultados),
            'data': resultados,
            'filtros': {
                'cliente_id': cliente_id,
                'equipo_id': equipo_id,
                'anio': anio
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/olap/filtros-disponibles', methods=['GET'])
def get_filtros_disponibles():
    """
    Obtiene los valores disponibles para los filtros (clientes, equipos, años)
    de forma dinámica desde el DataWarehouse
    """
    try:
        conn = get_connection('destino')
        cursor = conn.cursor(dictionary=True)
        
        # Clientes con proyectos
        cursor.execute("""
            SELECT DISTINCT 
                dc.id_cliente,
                dc.nombre as nombre_cliente,
                dc.sector,
                COUNT(hp.id_proyecto) as total_proyectos
            FROM DimCliente dc
            INNER JOIN HechoProyecto hp ON dc.id_cliente = hp.id_cliente
            GROUP BY dc.id_cliente, dc.nombre, dc.sector
            HAVING total_proyectos > 0
            ORDER BY dc.nombre
        """)
        clientes = cursor.fetchall()
        
        # Equipos con proyectos
        cursor.execute("""
            SELECT DISTINCT 
                de.id_equipo,
                de.nombre_equipo,
                COUNT(hp.id_proyecto) as total_proyectos
            FROM DimEquipo de
            INNER JOIN HechoProyecto hp ON de.id_equipo = hp.id_equipo
            GROUP BY de.id_equipo, de.nombre_equipo
            HAVING total_proyectos > 0
            ORDER BY de.nombre_equipo
        """)
        equipos = cursor.fetchall()
        
        # Años disponibles
        cursor.execute("""
            SELECT DISTINCT 
                dt.anio,
                COUNT(DISTINCT hp.id_proyecto) as total_proyectos
            FROM DimTiempo dt
            INNER JOIN HechoProyecto hp ON dt.id_tiempo = hp.id_tiempo_fin_real
            GROUP BY dt.anio
            ORDER BY dt.anio DESC
        """)
        anios = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'filtros': {
                'clientes': clientes,
                'equipos': equipos,
                'anios': anios
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # Usar puerto de variable de entorno (Railway, Heroku, etc) o 5001 por defecto
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Iniciando Dashboard en puerto {port}")
    print(f"   Modo: {'Desarrollo' if debug else 'Producción'}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
