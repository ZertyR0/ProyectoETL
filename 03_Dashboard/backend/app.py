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

# Configuración de base de datos desde variables de entorno
# Prioridad: Variables de entorno > Fallback local

def safe_int_env(key, default):
    """Convertir variable de entorno a int de forma segura"""
    try:
        value = os.getenv(key, str(default))
        return int(value)
    except (ValueError, TypeError):
        print(f"⚠️ Warning: {key}='{os.getenv(key)}' no es un número válido, usando {default}")
        return default

DB_CONFIG = {
    'host_origen': os.getenv('DB_HOST_ORIGEN', 'localhost'),
    'port_origen': safe_int_env('DB_PORT_ORIGEN', 3306),
    'user_origen': os.getenv('DB_USER_ORIGEN', 'root'),
    'password_origen': os.getenv('DB_PASSWORD_ORIGEN', ''),
    'host_destino': os.getenv('DB_HOST_DESTINO', 'localhost'),
    'port_destino': safe_int_env('DB_PORT_DESTINO', 3306),
    'user_destino': os.getenv('DB_USER_DESTINO', 'root'),
    'password_destino': os.getenv('DB_PASSWORD_DESTINO', ''),
    'db_origen': os.getenv('DB_NAME_ORIGEN', 'gestionproyectos_hist'),
    'db_destino': os.getenv('DB_NAME_DESTINO', 'dw_proyectos_hist')
}

print(f"🔧 Dashboard configurando...")
print(f"📊 BD Origen: {DB_CONFIG['host_origen']}:{DB_CONFIG['port_origen']}")
print(f"📊 BD Destino: {DB_CONFIG['host_destino']}:{DB_CONFIG['port_destino']}")
print(f"🌐 Ambiente: {os.getenv('FLASK_ENV', 'development')}")

# Variable global para ambiente ETL
AMBIENTE = os.getenv('ETL_AMBIENTE', 'local')

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
                hp.costo_real,
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
        
        # Mapeo de id_estado a nombre_estado
        mapeo_estados = {
            1: 'Planificación',
            2: 'En Progreso',
            3: 'En Pausa',
            4: 'Completado',
            5: 'Cancelado'
        }
        
        if AMBIENTE == 'distribuido':
            conn_origen = get_connection('origen')
            cursor_origen = conn_origen.cursor(buffered=True)
            
            for row in proyectos_dw_rows:
                id_proy = row[0]
                nombre_proy = row[1]
                # Consultar id_estado desde origen por NOMBRE
                try:
                    cursor_origen.execute("""
                        SELECT id_estado FROM Proyecto WHERE nombre = %s
                    """, (nombre_proy,))
                    estado_row = cursor_origen.fetchone()
                    if estado_row:
                        id_estado = estado_row[0]
                        estado = mapeo_estados.get(id_estado, 'Desconocido')
                    else:
                        # Si no encuentra por nombre, intentar por ID
                        cursor_origen.execute("""
                            SELECT id_estado FROM Proyecto WHERE id_proyecto = %s
                        """, (id_proy,))
                        estado_row = cursor_origen.fetchone()
                        id_estado = estado_row[0] if estado_row else None
                        estado = mapeo_estados.get(id_estado, 'Desconocido') if estado_row else 'Desconocido'
                except Exception as e:
                    print(f" Error obteniendo estado para proyecto {nombre_proy}: {str(e)}")
                    estado = 'Desconocido'
                    id_estado = None
                
                proyectos_dw.append({
                    'id_proyecto': row[0],
                    'nombre_proyecto': row[1] if row[1] else f"Proyecto {row[0]}",
                    'duracion_planificada': int(row[2]) if row[2] else 0,
                    'duracion_real': int(row[3]) if row[3] else 0,
                    'cumplimiento_tiempo': row[4] if row[4] else 0,
                    'presupuesto': float(row[5]) if row[5] else 0,
                    'costo_real': float(row[6]) if row[6] else 0,
                    'progreso_porcentaje': float(row[7]) if row[7] else 0,
                    'cliente': row[8] if row[8] else 'Sin cliente',
                    'gerente': row[9] if row[9] else 'Sin gerente',
                    'cumplimiento_presupuesto': row[10] if row[10] else 0,
                    'tareas_completadas': int(row[11]) if row[11] else 0,
                    'tareas_canceladas': int(row[12]) if row[12] else 0,
                    'estado': estado,
                    'prioridad': 'Media'
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
            duraciones_validas = [p['duracion_real'] for p in proyectos_dw if p.get('duracion_real', 0) > 0]
            if duraciones_validas:
                metricas['dias_promedio'] = int(sum(duraciones_validas) / len(duraciones_validas))
            else:
                metricas['dias_promedio'] = 0
            
            # Calcular proyectos a tiempo (cumplimiento_tiempo == 1 o 'Sí')
            proyectos_a_tiempo = sum(1 for p in proyectos_dw if p.get('cumplimiento_tiempo') in [1, 'Sí', True])
            metricas['proyectos_a_tiempo'] = proyectos_a_tiempo
            
            # Total de tareas (sumar de todos los proyectos)
            total_tareas_completadas = sum(p.get('tareas_completadas', 0) for p in proyectos_dw)
            total_tareas_canceladas = sum(p.get('tareas_canceladas', 0) for p in proyectos_dw)
            metricas['total_tareas'] = total_tareas_completadas + total_tareas_canceladas
        else:
            metricas['dias_promedio'] = 0
            metricas['proyectos_a_tiempo'] = 0
            metricas['total_tareas'] = 0
        
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
        
        # TODO: Implementar generador de datos para ambiente distribuido
        return jsonify({
            'status': 'error',
            'message': 'Generación de datos no disponible en Railway. Use el script local 01_GestionProyectos/datos/generar_datos_final.py'
        }), 501
        
    except Exception as e:
        import traceback
        return jsonify({'status': 'error','message': str(e),'traceback': traceback.format_exc()}), 500

@app.route('/ejecutar-etl', methods=['POST'])
def ejecutar_etl():
    """Ejecutar proceso ETL usando Python mysql-connector (sin subprocess)"""
    try:
        print(" Iniciando proceso ETL...")
        
        conn = get_connection('destino')
        cursor = conn.cursor()
        
        # 0. Verificar y agregar columna id_equipo ANTES del truncate
        print(" Verificando estructura HechoProyecto...")
        cursor.execute("SHOW COLUMNS FROM HechoProyecto LIKE 'id_equipo'")
        if not cursor.fetchone():
            print(" - Agregando columna id_equipo...")
            cursor.execute("ALTER TABLE HechoProyecto ADD COLUMN id_equipo INT AFTER id_empleado_gerente")
            cursor.execute("ALTER TABLE HechoProyecto ADD KEY idx_id_equipo (id_equipo)")
        
        # 1. Limpiar tablas
        print(" Limpiando tablas...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        conn.commit()
        
        cursor.execute("TRUNCATE TABLE HechoTarea")
        cursor.execute("TRUNCATE TABLE HechoProyecto")
        conn.commit()
        
        cursor.execute("DELETE FROM DimCliente")
        cursor.execute("DELETE FROM DimEmpleado")
        cursor.execute("DELETE FROM DimEquipo")
        cursor.execute("DELETE FROM DimProyecto")
        conn.commit()
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        
        # 2. Cargar dimensiones desde origen
        print(" Cargando dimensiones...")
        
        # DimCliente
        cursor.execute("""
            INSERT INTO DimCliente (id_cliente, nombre, sector)
            SELECT id_cliente, nombre, sector FROM gestionproyectos_hist.Cliente
        """)
        conn.commit()
        print(f" - DimCliente: {cursor.rowcount} registros")
        
        # DimEmpleado  
        cursor.execute("""
            INSERT INTO DimEmpleado (id_empleado, nombre, puesto)
            SELECT id_empleado, nombre, puesto FROM gestionproyectos_hist.Empleado
        """)
        conn.commit()
        print(f" - DimEmpleado: {cursor.rowcount} registros")
        
        # DimEquipo
        cursor.execute("""
            INSERT INTO DimEquipo (id_equipo, nombre_equipo, descripcion)
            SELECT id_equipo, nombre_equipo, descripcion FROM gestionproyectos_hist.Equipo
        """)
        conn.commit()
        print(f" - DimEquipo: {cursor.rowcount} registros")
        
        # DimProyecto (solo Completados/Cancelados)
        cursor.execute("""
            INSERT INTO DimProyecto (id_proyecto, nombre_proyecto, fecha_inicio, presupuesto_plan)
            SELECT id_proyecto, nombre, fecha_inicio, presupuesto
            FROM gestionproyectos_hist.Proyecto
            WHERE id_estado IN (4, 5)
        """)
        conn.commit()
        proyectos_dim = cursor.rowcount
        print(f" - DimProyecto: {proyectos_dim} registros")
        
        # DimTiempo
        cursor.execute("""
            INSERT IGNORE INTO DimTiempo (id_tiempo, fecha, anio, mes, trimestre)
            SELECT DISTINCT
                CAST(DATE_FORMAT(fecha_fin_real, '%Y%m%d') AS UNSIGNED),
                fecha_fin_real,
                YEAR(fecha_fin_real),
                MONTH(fecha_fin_real),
                QUARTER(fecha_fin_real)
            FROM gestionproyectos_hist.Proyecto
            WHERE fecha_fin_real IS NOT NULL AND id_estado IN (4, 5)
        """)
        conn.commit()
        print(f" - DimTiempo: {cursor.rowcount} registros")
        
        # 3. Cargar HechoProyecto
        print(" Cargando HechoProyecto...")
        cursor.execute("""
            INSERT INTO HechoProyecto (
                id_proyecto, id_cliente, id_empleado_gerente, id_equipo, id_tiempo_fin_real,
                presupuesto, costo_real, duracion_planificada, duracion_real,
                cumplimiento_tiempo, cumplimiento_presupuesto,
                tareas_total, tareas_completadas, tareas_canceladas
            )
            SELECT 
                p.id_proyecto,
                p.id_cliente,
                p.id_empleado_gerente,
                -- Obtener equipo principal del proyecto
                (SELECT te.id_equipo 
                 FROM gestionproyectos_hist.Tarea t 
                 JOIN gestionproyectos_hist.TareaEquipoHist te ON t.id_tarea = te.id_tarea 
                 WHERE t.id_proyecto = p.id_proyecto 
                 GROUP BY te.id_equipo 
                 ORDER BY COUNT(*) DESC 
                 LIMIT 1) as id_equipo,
                CAST(DATE_FORMAT(p.fecha_fin_real, '%Y%m%d') AS UNSIGNED),
                p.presupuesto,
                COALESCE(p.costo_real, p.presupuesto * 1.1),
                DATEDIFF(p.fecha_fin_plan, p.fecha_inicio),
                DATEDIFF(p.fecha_fin_real, p.fecha_inicio),
                CASE WHEN p.fecha_fin_real <= p.fecha_fin_plan THEN 1 ELSE 0 END,
                CASE WHEN COALESCE(p.costo_real, p.presupuesto * 1.1) <= p.presupuesto THEN 1 ELSE 0 END,
                (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto),
                (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto AND t.id_estado = 4),
                (SELECT COUNT(*) FROM gestionproyectos_hist.Tarea t WHERE t.id_proyecto = p.id_proyecto AND t.id_estado = 5)
            FROM gestionproyectos_hist.Proyecto p
            WHERE p.id_estado IN (4, 5) AND p.fecha_fin_real IS NOT NULL
        """)
        
        hechos = cursor.rowcount
        conn.commit()
        print(f" - HechoProyecto: {hechos} registros")
        
        cursor.close()
        conn.close()
        
        print(f" ETL completado exitosamente")
        
        # 4. Actualizar vistas OLAP
        print(" Actualizando vistas OLAP...")
        cursor.execute("""
            CREATE OR REPLACE VIEW vw_olap_detallado AS
            SELECT 
                hp.id_proyecto,
                dp.nombre as nombre_proyecto,
                de_estado.nombre_estado as estado,
                hp.id_cliente,
                dc.nombre as cliente,
                dc.sector,
                COALESCE(de.nombre_equipo, 'Sin Equipo') as equipo,
                hp.id_empleado_gerente as id_gerente,
                dem.nombre as gerente,
                dt.fecha,
                dt.anio,
                dt.mes,
                dt.trimestre,
                hp.presupuesto,
                hp.costo_real,
                hp.duracion_planificada,
                hp.duracion_real,
                hp.cumplimiento_tiempo,
                hp.cumplimiento_presupuesto,
                hp.tareas_total,
                hp.tareas_completadas,
                hp.tareas_canceladas,
                CASE 
                    WHEN hp.tareas_total > 0 
                    THEN ROUND((hp.tareas_completadas / hp.tareas_total) * 100, 2)
                    ELSE 0 
                END as porcentaje_completado,
                (hp.presupuesto - hp.costo_real) as margen,
                CASE 
                    WHEN hp.presupuesto > 0 
                    THEN ROUND(((hp.presupuesto - hp.costo_real) / hp.presupuesto) * 100, 2)
                    ELSE 0 
                END as rentabilidad_porcentaje
            FROM HechoProyecto hp
            INNER JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
            INNER JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
            INNER JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
            LEFT JOIN DimEquipo de ON hp.id_equipo = de.id_equipo
            LEFT JOIN DimEmpleado dem ON hp.id_empleado_gerente = dem.id_empleado
            LEFT JOIN gestionproyectos_hist.Estado de_estado ON dp.id_estado = de_estado.id_estado
            ORDER BY dt.fecha DESC
        """)
        
        return jsonify({
            'success': True,
            'message': f'ETL ejecutado exitosamente: {hechos} proyectos cargados',
            'stats': {
                'HechoProyecto': hechos,
                'DimProyecto': proyectos_dim
            }
        })
        
    except Exception as e:
        import traceback
        print(f" Error en ETL: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


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
    """Generar datos de prueba directamente en Railway usando lógica del generador.
    Parámetros JSON: 
      - proyectos: número de proyectos (requerido)
      - empleados_por_proyecto: empleados por proyecto (opcional, default 5)
      - tareas_por_proyecto: tareas por proyecto (opcional, default 10)
      - limpiar: bool (opcional, default False)
    """
    try:
        data = request.get_json() or {}
        
        # Obtener parámetros
        proyectos = int(data.get('proyectos', 25))
        empleados_pp = int(data.get('empleados_por_proyecto', 5))
        tareas_pp = int(data.get('tareas_por_proyecto', 10))
        limpiar = bool(data.get('limpiar', False))
        
        print(f" Generando: {proyectos} proyectos × {empleados_pp} empleados × {tareas_pp} tareas (limpiar={limpiar})")
        
        # Usar conexión origen (Railway)
        conn = get_connection('origen')
        cursor = conn.cursor()
        
        # Importar faker para generar datos
        from faker import Faker
        import random
        import hashlib
        from datetime import date, timedelta
        
        fake = Faker('es_MX')
        Faker.seed(42)
        random.seed(42)
        
        # Sets para control de duplicados
        nombres_unicos = {
            'clientes': set(),
            'empleados': set(), 
            'equipos': set(),
            'proyectos': set(),
            'emails': set()
        }
        
        def generar_email_unico(base):
            base_limpia = base.lower().replace(' ', '').replace(',', '')[:20]
            email = f"{base_limpia}@{fake.free_email_domain()}"
            contador = 1
            while email in nombres_unicos['emails']:
                email = f"{base_limpia}{contador}@{fake.free_email_domain()}"
                contador += 1
            nombres_unicos['emails'].add(email)
            return email
        
        def generar_nombre_unico(tipo, generador_func):
            max_intentos = 50
            for intento in range(max_intentos):
                nombre = generador_func()
                if nombre not in nombres_unicos[tipo]:
                    nombres_unicos[tipo].add(nombre)
                    return nombre
            # Si no se encuentra único, agregar sufijo
            nombre = f"{generador_func()} #{random.randint(1000, 9999)}"
            nombres_unicos[tipo].add(nombre)
            return nombre
        
        stats = {'clientes': 0, 'empleados': 0, 'equipos': 0, 'proyectos': 0, 'tareas': 0}
        
        # 1. Limpiar si se solicita
        if limpiar:
            print("   Limpiando datos...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tablas = ['TareaEquipoHist', 'MiembroEquipo', 'Tarea', 'Proyecto', 'Equipo', 'Empleado', 'Cliente']
            for tabla in tablas:
                cursor.execute(f"DELETE FROM {tabla}")
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()
            
            # Limpiar sets
            for key in nombres_unicos:
                nombres_unicos[key].clear()
        else:
            # Cargar nombres existentes para evitar duplicados
            cursor.execute("SELECT nombre FROM Cliente")
            for (nombre,) in cursor.fetchall():
                nombres_unicos['clientes'].add(nombre)
            
            cursor.execute("SELECT nombre FROM Empleado")
            for (nombre,) in cursor.fetchall():
                nombres_unicos['empleados'].add(nombre)
            
            cursor.execute("SELECT email FROM Empleado WHERE email IS NOT NULL")
            for (email,) in cursor.fetchall():
                nombres_unicos['emails'].add(email)
            
            cursor.execute("SELECT nombre_equipo FROM Equipo")
            for (nombre,) in cursor.fetchall():
                nombres_unicos['equipos'].add(nombre)
            
            cursor.execute("SELECT nombre FROM Proyecto")
            for (nombre,) in cursor.fetchall():
                nombres_unicos['proyectos'].add(nombre)
        
        # 2. Generar clientes (pocos para que tengan varios proyectos)
        num_clientes = max(3, proyectos // 4)  # 1 cliente cada 4 proyectos aprox
        print(f"   Generando {num_clientes} clientes...")
        
        sectores = ['Tecnología', 'Finanzas', 'Salud', 'Educación', 'Retail', 'Manufactura']
        clientes_ids = []
        
        for i in range(num_clientes):
            nombre = generar_nombre_unico('clientes', fake.company)
            sector = random.choice(sectores)
            contacto = fake.name()
            telefono = fake.phone_number()[:20]
            email = generar_email_unico(nombre)
            
            cursor.execute('''
                INSERT INTO Cliente (nombre, sector, contacto, telefono, email)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, sector, contacto, telefono, email))
            
            clientes_ids.append(cursor.lastrowid)
            stats['clientes'] += 1
        
        conn.commit()
        
        # 3. Obtener conteos actuales para generar nombres únicos
        cursor.execute("SELECT COUNT(*) FROM Proyecto")
        contador_proyectos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Equipo")
        contador_equipos = cursor.fetchone()[0]
        
        # 4. Generar proyectos con equipos y tareas
        print(f"   Generando {proyectos} proyectos completos...")
        
        for i in range(proyectos):
            # Cliente para este proyecto
            id_cliente = clientes_ids[i % len(clientes_ids)]
            
            # Generar empleados para este proyecto
            empleados_proyecto = []
            puestos = ['Gerente de Proyecto', 'Desarrollador Senior', 'Desarrollador', 'Analista', 'QA Tester']
            
            for j in range(empleados_pp):
                nombre_emp = generar_nombre_unico('empleados', fake.name)
                puesto = puestos[j % len(puestos)]
                email_emp = generar_email_unico(nombre_emp)
                
                cursor.execute('''
                    INSERT INTO Empleado (nombre, puesto, email)
                    VALUES (%s, %s, %s)
                ''', (nombre_emp, puesto, email_emp))
                
                empleados_proyecto.append({
                    'id': cursor.lastrowid,
                    'nombre': nombre_emp,
                    'puesto': puesto,
                    'es_gerente': 'Gerente' in puesto
                })
                stats['empleados'] += 1
            
            # Generar proyecto
            nombre_proy = generar_nombre_unico('proyectos', 
                lambda: f"Proyecto {fake.catch_phrase()} #{contador_proyectos + i + 1}")
            descripcion = fake.text(max_nb_chars=200)
            
            fecha_inicio = fake.date_between(start_date=date(2023, 1, 1), end_date=date(2024, 12, 31))
            duracion_plan = random.randint(60, 180)
            fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan)
            
            # Estados: 35% Completado, 15% Cancelado, 25% En Progreso, 15% Planificación, 10% En Pausa
            rand = random.random()
            if rand < 0.35:
                estado = 4  # Completado
                variacion = random.randint(-15, 30)
                fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
            elif rand < 0.50:
                estado = 5  # Cancelado  
                dias_transcurridos = random.randint(30, duracion_plan - 10)
                fecha_fin_real = fecha_inicio + timedelta(days=dias_transcurridos)
            elif rand < 0.75:
                estado = 2  # En Progreso
                fecha_fin_real = None
            elif rand < 0.90:
                estado = 1  # Planificación
                fecha_fin_real = None
            else:
                estado = 3  # En Pausa
                fecha_fin_real = None
            
            presupuesto = random.randint(100000, 500000)
            if estado == 4:  # Completado
                costo_real = int(presupuesto * random.uniform(0.80, 1.20))
            elif estado == 5:  # Cancelado
                costo_real = int(presupuesto * random.uniform(0.30, 0.70))
            else:  # Otros
                costo_real = int(presupuesto * random.uniform(0.20, 0.80))
            
            gerente = next((e for e in empleados_proyecto if e['es_gerente']), empleados_proyecto[0])
            
            cursor.execute('''
                INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, 
                                    fecha_fin_real, presupuesto, costo_real, id_cliente, 
                                    id_estado, id_empleado_gerente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (nombre_proy, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
                  presupuesto, costo_real, id_cliente, estado, gerente['id']))
            
            id_proyecto = cursor.lastrowid
            stats['proyectos'] += 1
            
            # Generar equipo
            nombre_equipo = generar_nombre_unico('equipos', 
                lambda: f"Equipo Proyecto {contador_equipos + i + 1}")
            
            cursor.execute('''
                INSERT INTO Equipo (nombre_equipo, descripcion)
                VALUES (%s, %s)
            ''', (nombre_equipo, fake.catch_phrase()))
            
            id_equipo = cursor.lastrowid
            stats['equipos'] += 1
            
            # Asignar empleados al equipo
            for emp in empleados_proyecto:
                rol = 'Team Lead' if emp['es_gerente'] else 'Developer'
                fecha_inicio_equipo = fecha_inicio
                fecha_fin_equipo = fecha_fin_real if estado in [4, 5] else None
                
                cursor.execute('''
                    INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (id_equipo, emp['id'], fecha_inicio_equipo, fecha_fin_equipo, rol))
            
            # Generar tareas
            nombres_tareas = ['Análisis de Requerimientos', 'Diseño de Arquitectura', 'Implementación Backend',
                             'Desarrollo Frontend', 'Testing', 'Documentación', 'Deploy']
            
            tareas_seleccionadas = random.sample(nombres_tareas, min(tareas_pp, len(nombres_tareas)))
            
            for nombre_tarea in tareas_seleccionadas:
                nombre_completo = f"{nombre_tarea} - P{id_proyecto}"
                
                inicio_offset = random.randint(0, max(1, duracion_plan - 20))
                fecha_inicio_tarea = fecha_inicio + timedelta(days=inicio_offset)
                duracion_tarea = random.randint(5, 21)
                fecha_fin_tarea = fecha_inicio_tarea + timedelta(days=duracion_tarea)
                
                # Estado coherente con proyecto
                if estado == 4:  # Proyecto completado
                    estado_tarea = random.choices([4, 5], weights=[85, 15])[0]
                    fecha_fin_real_tarea = fecha_fin_tarea + timedelta(days=random.randint(-3, 7)) if estado_tarea == 4 else None
                elif estado == 5:  # Proyecto cancelado
                    estado_tarea = random.choices([4, 5, 2], weights=[30, 40, 30])[0]
                    fecha_fin_real_tarea = fecha_fin_tarea if estado_tarea == 4 else None
                else:  # Otros estados
                    estado_tarea = random.choices([4, 2, 1], weights=[40, 40, 20])[0]
                    fecha_fin_real_tarea = fecha_fin_tarea if estado_tarea == 4 else None
                
                horas_plan = random.randint(16, 80)
                horas_reales = horas_plan + random.randint(-10, 20) if estado_tarea == 4 else int(horas_plan * random.uniform(0.2, 0.8))
                
                cursor.execute('''
                    INSERT INTO Tarea (nombre_tarea, fecha_inicio_plan, fecha_fin_plan,
                                     fecha_fin_real, horas_plan, horas_reales,
                                     id_proyecto, id_estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (nombre_completo, fecha_inicio_tarea, fecha_fin_tarea,
                      fecha_fin_real_tarea, horas_plan, horas_reales, id_proyecto, estado_tarea))
                
                id_tarea = cursor.lastrowid
                stats['tareas'] += 1
                
                # Asignar tarea al equipo
                cursor.execute('''
                    INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion)
                    VALUES (%s, %s, %s, %s)
                ''', (id_tarea, id_equipo, fecha_inicio_tarea, fecha_fin_real_tarea))
            
            # Commit cada 10 proyectos
            if (i + 1) % 10 == 0:
                conn.commit()
                print(f"     {i + 1}/{proyectos} proyectos generados...")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"   ✅ Generación completada")
        
        return jsonify({
            'success': True,
            'message': f'Datos generados exitosamente en Railway',
            'stats': {
                'clientes': stats['clientes'],
                'empleados': stats['empleados'], 
                'equipos': stats['equipos'],
                'proyectos': stats['proyectos'],
                'tareas': stats['tareas']
            },
            'info': f"{proyectos} proyectos con {empleados_pp} empleados cada uno"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f" ERROR generando datos: {str(e)}")
        print(error_trace)
        return jsonify({
            'success': False,
            'message': str(e),
            'traceback': error_trace
        }), 500

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
            ORDER BY anio DESC, trimestre DESC 
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
            # avance_objetivo_porcentaje ya viene de la vista, no necesita mapeo
            
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
            estado = objetivo.get('estado_objetivo', '')
            if estado == 'Verde':
                resumen['objetivos_verde'] += 1
            elif estado == 'Amarillo':
                resumen['objetivos_amarillo'] += 1
            else:
                resumen['objetivos_rojo'] += 1
            
            avance = objetivo.get('avance_objetivo_porcentaje', 0)
            if avance:
                resumen['avance_promedio'] += float(avance)
        
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
                bsc.perspectiva as vision_componente,
                COUNT(*) as total_objetivos,
                AVG(bsc.avance) as avance_promedio,
                COUNT(CASE WHEN bsc.estado = 'Verde' THEN 1 END) as objetivos_verde,
                COUNT(CASE WHEN bsc.estado = 'Amarillo' THEN 1 END) as objetivos_amarillo,
                COUNT(CASE WHEN bsc.estado = 'Rojo' THEN 1 END) as objetivos_rojo
            FROM vw_bsc_tablero_consolidado bsc
            GROUP BY bsc.perspectiva
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
            # Usar vista detallada para poder filtrar por año
            query = """
                SELECT 
                    COUNT(DISTINCT id_proyecto) as total_proyectos,
                    SUM(CASE WHEN estado = 'Completado' THEN 1 ELSE 0 END) as proyectos_completados,
                    SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as proyectos_cancelados,
                    0 as proyectos_activos,
                    COUNT(DISTINCT cliente) as total_clientes,
                    COUNT(DISTINCT equipo) as total_equipos,
                    SUM(presupuesto) as presupuesto_total,
                    SUM(costo_real) as costo_total,
                    SUM(margen) as margen_total,
                    ROUND(AVG(rentabilidad_porcentaje), 2) as rentabilidad_promedio_porcentaje,
                    ROUND(AVG(CASE 
                        WHEN en_presupuesto = 'Sí' THEN 100
                        WHEN en_presupuesto = 'No' THEN 0
                        ELSE NULL
                    END), 2) as porcentaje_cumplimiento_presupuesto,
                    SUM(horas_reales) as horas_reales_total,
                    SUM(horas_estimadas) as horas_estimadas_total,
                    CASE 
                        WHEN SUM(horas_estimadas) > 0 
                        THEN ROUND((SUM(horas_reales) / SUM(horas_estimadas) * 100), 2)
                        ELSE 0 
                    END as eficiencia_estimacion_porcentaje
                FROM vw_olap_detallado
            """
            conditions = []
            if cliente_id:
                conn_temp = get_connection('destino')
                cur_temp = conn_temp.cursor(dictionary=True)
                cur_temp.execute(f"SELECT nombre FROM DimCliente WHERE id_cliente = {cliente_id}")
                cliente_row = cur_temp.fetchone()
                cur_temp.close()
                conn_temp.close()
                if cliente_row:
                    conditions.append(f"cliente = '{cliente_row['nombre']}'")
            if equipo_id:
                conn_temp = get_connection('destino')
                cur_temp = conn_temp.cursor(dictionary=True)
                cur_temp.execute(f"SELECT nombre_equipo FROM DimEquipo WHERE id_equipo = {equipo_id}")
                equipo_row = cur_temp.fetchone()
                cur_temp.close()
                conn_temp.close()
                if equipo_row:
                    conditions.append(f"equipo = '{equipo_row['nombre_equipo']}'")
            if anio:
                conditions.append(f"anio = {anio}")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
        elif nivel == 'por_cliente':
            # Usar vista detallada y agregar por cliente
            query = """
                SELECT 
                    cliente,
                    MAX(sector) as sector,
                    COUNT(DISTINCT id_proyecto) as total_proyectos,
                    SUM(CASE WHEN estado = 'Completado' THEN 1 ELSE 0 END) as proyectos_completados,
                    SUM(presupuesto) as presupuesto_total,
                    SUM(costo_real) as costo_total,
                    SUM(margen) as margen_total,
                    ROUND(AVG(rentabilidad_porcentaje), 2) as rentabilidad_promedio_porcentaje,
                    ROUND(AVG(CASE 
                        WHEN en_presupuesto = 'Sí' THEN 100
                        WHEN en_presupuesto = 'No' THEN 0
                        ELSE NULL
                    END), 2) as porcentaje_en_presupuesto
                FROM vw_olap_detallado
            """
            conditions = []
            if cliente_id:
                # Necesitamos obtener el nombre del cliente
                conn_temp = get_connection('destino')
                cur_temp = conn_temp.cursor(dictionary=True)
                cur_temp.execute(f"SELECT nombre FROM DimCliente WHERE id_cliente = {cliente_id}")
                cliente_row = cur_temp.fetchone()
                cur_temp.close()
                conn_temp.close()
                if cliente_row:
                    conditions.append(f"cliente = '{cliente_row['nombre']}'")
            if anio:
                conditions.append(f"anio = {anio}")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY cliente ORDER BY total_proyectos DESC"
            
        elif nivel == 'por_equipo':
            # Usar vista detallada y agregar por equipo
            query = """
                SELECT 
                    equipo,
                    COUNT(DISTINCT id_proyecto) as total_proyectos,
                    SUM(CASE WHEN estado = 'Completado' THEN 1 ELSE 0 END) as proyectos_completados,
                    SUM(presupuesto) as presupuesto_total,
                    SUM(costo_real) as costo_total,
                    SUM(margen) as margen_total,
                    ROUND(AVG(rentabilidad_porcentaje), 2) as rentabilidad_promedio_porcentaje,
                    SUM(horas_reales) as horas_reales_total,
                    SUM(horas_estimadas) as horas_estimadas_total
                FROM vw_olap_detallado
            """
            conditions = []
            if equipo_id:
                # Necesitamos obtener el nombre del equipo
                conn_temp = get_connection('destino')
                cur_temp = conn_temp.cursor(dictionary=True)
                cur_temp.execute(f"SELECT nombre_equipo FROM DimEquipo WHERE id_equipo = {equipo_id}")
                equipo_row = cur_temp.fetchone()
                cur_temp.close()
                conn_temp.close()
                if equipo_row:
                    conditions.append(f"equipo = '{equipo_row['nombre_equipo']}'")
            if anio:
                conditions.append(f"anio = {anio}")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY equipo ORDER BY total_proyectos DESC"
            
        elif nivel == 'por_tiempo':
            query = "SELECT * FROM vw_olap_por_anio"
            if anio:
                query += f" WHERE anio = {anio}"
            query += " ORDER BY anio DESC"
            
        else:  # detallado
            query = "SELECT * FROM vw_olap_detallado"
            conditions = []
            if cliente_id:
                # La vista ya tiene el cliente, solo filtrar
                conditions.append(f"cliente = (SELECT nombre FROM DimCliente WHERE id_cliente = {cliente_id})")
            if anio:
                conditions.append(f"anio = {anio}")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY anio DESC, proyecto DESC LIMIT 100"
        
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
        
        # Equipos con proyectos (nota: HechoProyecto no tiene id_equipo, retornar lista vacía)
        equipos = []
        
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
