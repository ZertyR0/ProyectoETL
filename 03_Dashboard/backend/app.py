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
    
    # Agregar unix_socket si existe en la configuración
    if 'unix_socket' in config:
        DB_CONFIG['unix_socket'] = config['unix_socket']
    
    print(f"🚀 Dashboard configurado para ambiente: {AMBIENTE}")
    print(f"📊 BD Origen: {config['host_origen']}:{config['port_origen']}")
    if 'unix_socket' in config:
        print(f"   Socket: {config['unix_socket']}")
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
        
        # Obtener detalle de proyectos en el DW
        # Como DimProyecto puede no tener datos, obtenemos nombres directamente del origen
        conn_origen = get_connection('origen')
        cursor_origen = conn_origen.cursor()
        
        cursor.execute("""
            SELECT 
                hp.id_proyecto,
                hp.presupuesto,
                hp.costo_real,
                hp.duracion_planificada,
                hp.duracion_real,
                hp.cumplimiento_tiempo,
                hp.cumplimiento_presupuesto,
                hp.tareas_total,
                hp.tareas_completadas,
                hp.tareas_canceladas
            FROM HechoProyecto hp
            ORDER BY hp.id_proyecto
            LIMIT 50
        """)
        
        proyectos_dw = []
        for row in cursor.fetchall():
            id_proyecto = row[0]
            
            # Obtener nombre del proyecto desde la base de datos origen
            cursor_origen.execute("SELECT nombre FROM Proyecto WHERE id_proyecto = %s", (id_proyecto,))
            nombre_row = cursor_origen.fetchone()
            nombre_proyecto = nombre_row[0] if nombre_row else f"Proyecto {id_proyecto}"
            
            proyectos_dw.append({
                'id': id_proyecto,
                'nombre': nombre_proyecto,
                'presupuesto': float(row[1]) if row[1] else 0,
                'costo_real': float(row[2]) if row[2] else 0,
                'duracion_plan': row[3],
                'duracion_real': row[4],
                'cumplimiento_tiempo': row[5],
                'cumplimiento_presupuesto': row[6],
                'tareas_total': row[7],
                'tareas_completadas': row[8],
                'tareas_canceladas': row[9]
            })
        
        cursor_origen.close()
        conn_origen.close()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'estadisticas': stats,
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

@app.route('/ejecutar-etl', methods=['POST'])
def ejecutar_etl():
    """Ejecutar proceso ETL"""
    try:
        # Importar el ETL principal
        import sys
        import os
        from pathlib import Path
        
        # Configurar paths
        base_dir = Path(__file__).parent.parent.parent
        etl_dir = base_dir / '02_ETL'
        etl_scripts_dir = etl_dir / 'scripts'
        etl_config_dir = etl_dir / 'config'
        
        # Agregar al path
        sys.path.insert(0, str(etl_scripts_dir))
        sys.path.insert(0, str(etl_config_dir))
        
        # Importar el ETL
        from etl_principal import ETLProyectos
        
        # Ejecutar ETL
        etl = ETLProyectos('local')
        success = etl.ejecutar_etl_completo()
        
        if success:
            # Obtener estadísticas del datawarehouse
            try:
                conn = get_connection('destino')
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
                
                cursor.execute("SELECT COUNT(*) FROM DimTiempo")
                result = cursor.fetchone()
                dim_tiempo = result[0] if result else 0
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'ETL ejecutado exitosamente',
                    'registros_procesados': {
                        'HechoProyecto': fact_proyectos,
                        'HechoTarea': fact_tareas,
                        'DimCliente': dim_clientes,
                        'DimTiempo': dim_tiempo
                    },
                    'total': fact_proyectos + fact_tareas + dim_clientes + dim_tiempo
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
def generar_datos():
    """Generar datos de prueba usando el generador final"""
    try:
        import sys
        from pathlib import Path
        
        # Agregar el directorio de datos al path
        datos_dir = Path(__file__).parent.parent.parent / '01_GestionProyectos' / 'datos'
        sys.path.insert(0, str(datos_dir))
        
        # Importar el generador final
        from generar_datos_final import GeneradorDatosFinal
        
        # Obtener parámetros del request
        data = request.get_json()
        num_proyectos = data.get('proyectos', 50)
        
        # Nota: El nuevo generador usa cantidades fijas internas
        # Se puede extender para aceptar parámetros personalizados
        
        # Crear instancia del generador
        generador = GeneradorDatosFinal()
        
        # Ejecutar la generación completa
        exito = generador.ejecutar()
        
        if exito:
            return jsonify({
                'success': True,
                'message': 'Datos generados exitosamente con el nuevo generador',
                'stats': generador.stats
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error durante la generación de datos'
            }), 500
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': str(e),
            'error': str(e),
            'traceback': traceback.format_exc()
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
            else:  # nombre
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
                # Convertir tipos especiales
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
                    resultado['mensaje'] = '✅ Proyecto encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = '⚠️ Proyecto encontrado en BD Origen pero NO en DataWarehouse (puede que no esté completado/cancelado)'
            else:
                resultado['mensaje'] = '❌ Proyecto no encontrado en BD Origen'
        
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
                cursor_destino.execute("SELECT * FROM DimCliente WHERE id_cliente = %s", 
                                      (cliente_origen['id_cliente'],))
                cliente_dw = cursor_destino.fetchone()
                
                if cliente_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in cliente_dw.items():
                        if isinstance(val, (date, datetime)):
                            cliente_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            cliente_dw[key] = float(val)
                    resultado['datos_dw'] = cliente_dw
                    resultado['mensaje'] = '✅ Cliente encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = '⚠️ Cliente encontrado en BD Origen pero NO en DataWarehouse'
            else:
                resultado['mensaje'] = '❌ Cliente no encontrado en BD Origen'
        
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
                cursor_destino.execute("SELECT * FROM DimEmpleado WHERE id_empleado = %s",
                                      (empleado_origen['id_empleado'],))
                empleado_dw = cursor_destino.fetchone()
                
                if empleado_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in empleado_dw.items():
                        if isinstance(val, (date, datetime)):
                            empleado_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            empleado_dw[key] = float(val)
                    resultado['datos_dw'] = empleado_dw
                    resultado['mensaje'] = '✅ Empleado encontrado en ambas bases de datos'
                else:
                    resultado['mensaje'] = '⚠️ Empleado encontrado en BD Origen pero NO en DataWarehouse'
            else:
                resultado['mensaje'] = '❌ Empleado no encontrado en BD Origen'
        
        # TAREAS
        elif tipo == 'tarea':
            if criterio == 'id':
                cursor_origen.execute("""
                    SELECT t.*, p.nombre as nombre_proyecto, e.nombre as nombre_empleado,
                           est.nombre_estado
                    FROM Tarea t
                    LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
                    LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
                    LEFT JOIN Estado est ON t.id_estado = est.id_estado
                    WHERE t.id_tarea = %s
                """, (valor,))
            else:
                cursor_origen.execute("""
                    SELECT t.*, p.nombre as nombre_proyecto, e.nombre as nombre_empleado,
                           est.nombre_estado
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
                cursor_destino.execute("SELECT * FROM HechoTarea WHERE id_tarea = %s",
                                      (tarea_origen['id_tarea'],))
                tarea_dw = cursor_destino.fetchone()
                
                if tarea_dw:
                    resultado['encontrado_dw'] = True
                    for key, val in tarea_dw.items():
                        if isinstance(val, (date, datetime)):
                            tarea_dw[key] = val.isoformat()
                        elif isinstance(val, Decimal):
                            tarea_dw[key] = float(val)
                    resultado['datos_dw'] = tarea_dw
                    resultado['mensaje'] = '✅ Tarea encontrada en ambas bases de datos'
                else:
                    resultado['mensaje'] = '⚠️ Tarea encontrada en BD Origen pero NO en DataWarehouse'
            else:
                resultado['mensaje'] = '❌ Tarea no encontrada en BD Origen'
        
        else:
            resultado['success'] = False
            resultado['mensaje'] = f'❌ Tipo "{tipo}" no soportado'
        
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
