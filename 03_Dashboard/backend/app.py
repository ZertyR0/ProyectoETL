from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import sys
import os
import subprocess
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuración ETL
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '02_ETL', 'config'))

try:
    from config_conexion import get_config
    AMBIENTE = os.getenv('ETL_AMBIENTE', 'local')
    config = get_config(AMBIENTE)
    
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
    
    if 'unix_socket' in config:
        DB_CONFIG['unix_socket'] = config['unix_socket']
    
    print(f"🚀 Dashboard: {AMBIENTE}")
    print(f"📊 Origen: {config['host_origen']}:{config['port_origen']}")
    print(f"🏢 Destino: {config['host_destino']}:{config['port_destino']}")
    
except ImportError:
    print("⚠️ Configuración local")
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
        return mysql.connector.connect(
            host=DB_CONFIG['host_destino'],
            port=DB_CONFIG['port_destino'],
            user=DB_CONFIG['user_destino'],
            password=DB_CONFIG['password_destino'],
            database=DB_CONFIG['db_destino']
        )

# Función eliminada - no necesaria

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
            'POST /generar-datos': 'Generar datos de prueba',
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
        cursor_destino.execute("SELECT COUNT(*) FROM hechoproyecto")
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
                   c.nombre as cliente, IFNULL(e.nombre, 'Sin estado') as nombre_estado
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
        cursor = conn.cursor()
        
        # Obtener estadísticas del DW
        stats = {}
        tablas = ['dimcliente', 'dimempleado', 'dimequipo', 'dimproyecto', 'dimtiempo', 'hechoproyecto', 'hechotarea']
        
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
            FROM hechoproyecto
        """)
        
        metricas_row = cursor.fetchone()
        metricas = {
            'total_proyectos': metricas_row[0] if metricas_row[0] else 0,
            'presupuesto_promedio': float(metricas_row[1]) if metricas_row[1] else 0,
            'duracion_promedio': float(metricas_row[2]) if metricas_row[2] else 0,
            'proyectos_a_tiempo': metricas_row[3] if metricas_row[3] else 0
        }
        
        # Obtener detalle de proyectos en el DW con nombres desde DimProyecto
        cursor.execute("""
            SELECT 
                hp.id_proyecto,
                dp.nombre_proyecto,
                hp.presupuesto,
                hp.costo_real,
                hp.duracion_planificada,
                hp.duracion_real,
                hp.cumplimiento_tiempo,
                hp.cumplimiento_presupuesto,
                hp.tareas_total,
                hp.tareas_completadas,
                hp.tareas_canceladas
            FROM hechoproyecto hp
            LEFT JOIN dimproyecto dp ON hp.id_proyecto = dp.id_proyecto
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
            cursor_origen = conn_origen.cursor()
            
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
                    print(f"❌ Error obteniendo estado para proyecto {nombre_proy}: {str(e)}")
                    estado = 'Desconocido'
                    id_estado = None
                
                proyectos_dw.append({
                    'id_proyecto': row[0],
                    'nombre_proyecto': row[1] if row[1] else f"Proyecto {row[0]}",
                    'estado': estado,
                    'id_estado': id_estado,
                    'presupuesto': float(row[2]) if row[2] else 0,
                    'costo_real': float(row[3]) if row[3] else 0,
                    'duracion_plan': row[4],
                    'duracion_real': row[5],
                    'cumplimiento_tiempo': row[6],
                    'cumplimiento_presupuesto': row[7],
                    'tareas_total': row[8],
                    'tareas_completadas': row[9],
                    'tareas_canceladas': row[10]
                })
            
            cursor_origen.close()
            conn_origen.close()
        else:
            # Modo local: usar estado de la misma base
            for row in proyectos_dw_rows:
                proyectos_dw.append({
                    'id_proyecto': row[0],
                    'nombre_proyecto': row[1] if row[1] else f"Proyecto {row[0]}",
                    'estado': 'N/A',
                    'id_estado': None,
                    'presupuesto': float(row[2]) if row[2] else 0,
                    'costo_real': float(row[3]) if row[3] else 0,
                    'duracion_plan': row[4],
                    'duracion_real': row[5],
                    'cumplimiento_tiempo': row[6],
                    'cumplimiento_presupuesto': row[7],
                    'tareas_total': row[8],
                    'tareas_completadas': row[9],
                    'tareas_canceladas': row[10]
                })
        
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

# Función eliminada - usar /generar-datos en su lugar

@app.route('/ejecutar-etl', methods=['POST'])
def ejecutar_etl():
    """Ejecutar proceso ETL"""
    try:
        print("🚀 Iniciando proceso ETL...")
        
        # MODO DISTRIBUIDO: Usar script Python ETL que conecta a 2 BDs remotas
        if os.environ.get('ETL_AMBIENTE') == 'distribuido':
            print("🌐 Modo distribuido detectado - usando ETL Python")
            
            # Importar y ejecutar ETL distribuido
            import sys
            from pathlib import Path
            etl_path = Path(__file__).parent.parent.parent / '02_ETL' / 'scripts'
            sys.path.insert(0, str(etl_path))
            
            from etl_distribuido import ejecutar_etl_distribuido
            
            success = ejecutar_etl_distribuido()
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Error ejecutando ETL distribuido',
                    'error': 'Revisar logs del servidor'
                }), 500
        
        # MODO LOCAL: Usar procedimiento almacenado
        else:
            print("🏠 Modo local detectado - usando procedimiento almacenado")
            
            # Conectar al datawarehouse
            connection_params = {
                'user': DB_CONFIG['user_destino'],
                'password': DB_CONFIG['password_destino'],
                'database': DB_CONFIG['db_destino']
            }
            
            # Solo usar unix_socket si el host es localhost
            if DB_CONFIG['host_destino'] == 'localhost' and 'unix_socket' in DB_CONFIG and DB_CONFIG['unix_socket']:
                connection_params['unix_socket'] = DB_CONFIG['unix_socket']
            else:
                connection_params['host'] = DB_CONFIG['host_destino']
                connection_params['port'] = DB_CONFIG['port_destino']
            
            conn_destino = mysql.connector.connect(**connection_params)
            cursor = conn_destino.cursor(dictionary=True)
            
            # Ejecutar el procedimiento almacenado completo
            print("⏳ Ejecutando sp_ejecutar_etl_completo()...")
            cursor.execute("CALL sp_ejecutar_etl_completo()")
            resultado = cursor.fetchone()
            
            print(f"✅ Resultado: {resultado}")
            
            cursor.nextset()
            cursor.close()
            conn_destino.close()
            
            # Verificar si hubo éxito
            if resultado and resultado.get('estado') == 'ERROR':
                return jsonify({
                    'success': False,
                    'message': resultado.get('mensaje', 'Error desconocido en ETL'),
                    'error': str(resultado)
                }), 500
            
            success = True
        
        if success:
            # Obtener estadísticas del datawarehouse
            try:
                conn = get_connection('destino')
                cursor = conn.cursor()
                
                # Contar registros en tablas principales
                cursor.execute("SELECT COUNT(*) FROM hechoproyecto")
                fact_proyectos = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM hechotarea")
                fact_tareas = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM dimcliente")
                dim_clientes = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM dimtiempo")
                dim_tiempo = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': f'ETL ejecutado exitosamente - {resultado.get("mensaje", "Completado")}' if resultado else 'ETL ejecutado exitosamente',
                    'registros_procesados': {
                        'HechoProyecto': int(fact_proyectos) if fact_proyectos else 0,
                        'HechoTarea': int(fact_tareas) if fact_tareas else 0,
                        'DimCliente': int(dim_clientes) if dim_clientes else 0,
                        'DimTiempo': int(dim_tiempo) if dim_tiempo else 0
                    },
                    'total': int(fact_proyectos or 0) + int(fact_tareas or 0) + int(dim_clientes or 0) + int(dim_tiempo or 0)
                })
                
            except Exception as db_error:
                return jsonify({
                    'success': True,
                    'message': 'ETL ejecutado, pero no se pudieron obtener estadísticas',
                    'error_estadisticas': str(db_error)
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Error en la ejecución del ETL'
            }), 500
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error ejecutando ETL: {str(e)}',
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
        tablas_origen = ['TareaEquipoHist', 'Tarea', 'Proyecto', 'MiembroEquipo', 'Equipo', 'Empleado', 'Cliente']
        for tabla in tablas_origen:
            try:
                cursor_origen.execute(f"TRUNCATE TABLE {tabla}")
            except:
                cursor_origen.execute(f"DELETE FROM {tabla}")
        cursor_origen.execute("SET FOREIGN_KEY_CHECKS=1")
        
        cursor_origen.close()
        conn_origen.close()
        
        # Limpiar destino
        conn_destino = get_connection('destino')
        cursor_destino = conn_destino.cursor()
        
        cursor_destino.execute("SET FOREIGN_KEY_CHECKS=0")
        tablas_destino = ['HechoTarea', 'HechoProyecto', 'DimTiempo', 'DimProyecto', 'DimEquipo', 'DimEmpleado', 'DimCliente']
        for tabla in tablas_destino:
            try:
                cursor_destino.execute(f"TRUNCATE TABLE {tabla}")
            except:
                cursor_destino.execute(f"DELETE FROM {tabla}")
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
def generar_datos():
    """Generar datos de prueba"""
    try:
        import sys
        from pathlib import Path
        import subprocess
        
        # Obtener parámetros del request
        data = request.get_json()
        num_proyectos = data.get('proyectos', 50)
        
        # En modo distribuido, usar el script de generación remota
        if os.environ.get('ETL_AMBIENTE') == 'distribuido':
            print("🌐 Generando datos en modo distribuido...")
            
            # Ejecutar el script de generación completa desde la raíz del proyecto
            project_root = Path(__file__).parent.parent.parent
            script_path = project_root / 'generar_datos_completos.py'
            
            # Cambiar al directorio del proyecto para asegurar rutas correctas
            result = subprocess.run(
                ['python3', str(script_path)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': 'Datos generados exitosamente en BD remota',
                    'output': result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error durante la generación de datos',
                    'error': result.stderr
                }), 500
        
        # Modo local - usar faker directamente
        else:
            print("🏠 Generando datos en modo local...")
            
            from faker import Faker
            import random
            
            fake = Faker('es_MX')
            conn = get_connection('origen')
            cursor = conn.cursor()
            
            # Generar algunos datos básicos
            # Clientes
            for _ in range(10):
                nombre = fake.company()[:100]
                sector = fake.bs().split()[0][:50]
                contacto = fake.name()[:100]
                cursor.execute(
                    "INSERT INTO Cliente (nombre, sector, contacto, telefono, email) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, sector, contacto, fake.phone_number()[:20], fake.email())
                )
            
            # Empleados
            puestos = ["Desarrollador", "Analista", "QA", "Gerente", "Diseñador"]
            for _ in range(15):
                nombre = fake.name()[:100]
                puesto = random.choice(puestos)
                cursor.execute(
                    "INSERT INTO Empleado (nombre, puesto, departamento, email) VALUES (%s, %s, %s, %s)",
                    (nombre, puesto, fake.job()[:50], fake.email())
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Datos generados exitosamente en modo local'
            })
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'Timeout: La generación tardó más de 120 segundos',
            'error': 'Timeout'
        }), 500
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': str(e),
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Función de trazabilidad eliminada - demasiado compleja


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
