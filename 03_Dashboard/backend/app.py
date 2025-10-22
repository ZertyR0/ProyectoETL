from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import subprocess
import traceback
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Permitir requests desde Angular

# Agregar path para importar configuración ETL
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '02_ETL', 'config'))

try:
    from config_conexion import get_config
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
    
    print(f"🚀 Dashboard configurado para ambiente: {AMBIENTE}")
    print(f"📊 BD Origen: {config['host_origen']}:{config['port_origen']}")
    print(f"🏢 BD Destino: {config['host_destino']}:{config['port_destino']}")
    
except ImportError:
    # Fallback a configuración local si no se puede importar
    print("⚠️ No se pudo importar configuración ETL, usando configuración local")
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
        return mysql.connector.connect(
            host=DB_CONFIG['host_origen'],
            port=DB_CONFIG['port_origen'],
            user=DB_CONFIG['user_origen'],
            password=DB_CONFIG['password_origen'],
            database=DB_CONFIG['db_origen']
        )
    else:
        return mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )

def get_engine(db_type='origen'):
    """Obtener engine SQLAlchemy"""
    if db_type == 'origen':
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
                   c.nombre as cliente, e.nombre_estado
            FROM Proyecto p
            JOIN Cliente c ON p.id_cliente = c.id_cliente
            JOIN Estado e ON p.id_estado = e.id_estado
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
        cursor = conn.cursor()
        
        # Obtener estadísticas
        stats = {}
        tablas = ['DimCliente', 'DimEmpleado', 'DimEquipo', 'DimProyecto', 'DimTiempo', 'HechoProyecto', 'HechoTarea']
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                stats[tabla] = cursor.fetchone()[0]
            except:
                stats[tabla] = 0
        
        # Obtener métricas del datawarehouse
        cursor.execute("""
            SELECT 
                COUNT(*) as total_proyectos,
                AVG(presupuesto) as presupuesto_promedio,
                AVG(duracion_real) as duracion_promedio,
                SUM(CASE WHEN cumplimiento_tiempo = 1 THEN 1 ELSE 0 END) as proyectos_a_tiempo
            FROM HechoProyecto
        """)
        
        metricas_row = cursor.fetchone()
        metricas = {
            'total_proyectos': metricas_row[0] if metricas_row[0] else 0,
            'presupuesto_promedio': float(metricas_row[1]) if metricas_row[1] else 0,
            'duracion_promedio': float(metricas_row[2]) if metricas_row[2] else 0,
            'proyectos_a_tiempo': metricas_row[3] if metricas_row[3] else 0
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'estadisticas': stats,
            'metricas': metricas
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/insertar-datos', methods=['POST'])
def insertar_datos():
    """Generar datos de prueba en la base origen"""
    try:
        # Ejecutar script de generación de datos
        # Aquí puedes llamar al script de generación o ejecutar la lógica directamente
        
        conn = get_connection('origen')
        cursor = conn.cursor()
        
        # Insertar algunos datos de ejemplo
        from faker import Faker
        import random
        fake = Faker('es_MX')
        
        # Insertar clientes
        for _ in range(5):
            nombre = fake.company()[:100]
            sector = fake.bs().split()[0][:50]
            contacto = fake.name()[:100]
            cursor.execute(
                "INSERT INTO Cliente (nombre, sector, contacto) VALUES (%s, %s, %s)",
                (nombre, sector, contacto)
            )
        
        # Insertar empleados
        puestos = ["Desarrollador", "Analista", "QA", "Gerente"]
        for _ in range(10):
            nombre = fake.name()[:100]
            puesto = random.choice(puestos)
            cursor.execute(
                "INSERT INTO Empleado (nombre, puesto) VALUES (%s, %s)",
                (nombre, puesto)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Datos de prueba insertados correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/ejecutar-etl', methods=['POST'])
def ejecutar_etl():
    """Ejecutar proceso ETL"""
    try:
        # Importar y ejecutar el ETL mejorado
        import sys
        import os
        
        # Agregar el directorio actual al path para importar el ETL
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Importar el ETL simplificado
        from etl_simple import ejecutar_etl as run_etl
        
        # Ejecutar ETL
        success = run_etl()
        
        if success:
            # Obtener estadísticas del datawarehouse
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Contar registros en tablas principales
                cursor.execute("SELECT COUNT(*) FROM HechoProyecto")
                result = cursor.fetchone()
                fact_proyectos = result[0] if result else 0
                
                cursor.execute("SELECT COUNT(*) FROM HechoTarea")
                result = cursor.fetchone()
                fact_tareas = result[0] if result else 0
                
                cursor.execute("SELECT COUNT(*) FROM DimCliente")
                result = cursor.fetchone()
                dim_clientes = result[0] if result else 0
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'ETL ejecutado exitosamente',
                    'data': {
                        'registros_procesados': fact_proyectos + fact_tareas,
                        'fact_proyectos': fact_proyectos,
                        'fact_tareas': fact_tareas,
                        'dim_clientes': dim_clientes,
                        'tablas_actualizadas': ['DimCliente', 'DimEmpleado', 'DimProyecto', 'DimTiempo', 'HechoProyecto', 'HechoTarea']
                    }
                })
                
            except Exception as db_error:
                return jsonify({
                    'success': True,
                    'message': 'ETL ejecutado, pero no se pudieron obtener estadísticas',
                    'data': {
                        'registros_procesados': 'N/A',
                        'error_estadisticas': str(db_error)
                    }
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Error en la ejecución del ETL'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error ejecutando ETL: {str(e)}'
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
