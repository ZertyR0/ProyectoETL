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
    """Generar datos de prueba con cantidades personalizables"""
    try:
        from faker import Faker
        import random
        from datetime import timedelta, date
        
        # Obtener parámetros del request
        data = request.get_json()
        num_clientes = data.get('clientes', 10)
        num_empleados = data.get('empleados', 20)
        num_equipos = data.get('equipos', 5)
        num_proyectos = data.get('proyectos', 50)
        
        fake = Faker("es_MX")
        
        conn = get_connection('origen')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Contadores
        clientes_creados = empleados_creados = equipos_creados = 0
        proyectos_creados = tareas_creadas = asignaciones_creadas = 0
        
        # 1. Insertar Clientes
        sectores = ["tecnología", "finanzas", "salud", "educación", "retail", "manufactura", "servicios", "telecomunicaciones"]
        for _ in range(num_clientes):
            nombre_cli = fake.company()[:100]
            sector_cli = random.choice(sectores)[:50]
            contacto_cli = fake.name()[:100]
            tel_cli = fake.phone_number()[:20]
            email_cli = fake.company_email()[:100]
            direccion_cli = fake.address().replace('\n', ', ')[:200]
            cur.execute(
                "INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre_cli, sector_cli, contacto_cli, tel_cli, email_cli, direccion_cli)
            )
            clientes_creados += 1
        
        # 2. Insertar Empleados
        puestos = ["Desarrollador", "Analista", "QA", "Gerente de Proyecto", "Diseñador", "DevOps", "Arquitecto", "Líder Técnico"]
        departamentos = ["Desarrollo", "Calidad", "Infraestructura", "Gestión de Proyectos", "UX/UI", "Análisis"]
        for _ in range(num_empleados):
            nombre_emp = fake.name()[:100]
            puesto_emp = random.choice(puestos)
            depto_emp = random.choice(departamentos)[:50]
            # Salarios realistas según puesto
            salarios_base = {
                "Desarrollador": (35000, 65000),
                "Analista": (30000, 55000),
                "QA": (28000, 50000),
                "Gerente de Proyecto": (55000, 95000),
                "Diseñador": (32000, 58000),
                "DevOps": (40000, 75000),
                "Arquitecto": (60000, 110000),
                "Líder Técnico": (50000, 85000)
            }
            rango = salarios_base.get(puesto_emp, (30000, 60000))
            salario = round(random.uniform(rango[0], rango[1]), 2)
            fecha_ing = fake.date_between(start_date="-3650d", end_date="-180d")  # Entre 10 años y 6 meses atrás
            
            cur.execute(
                "INSERT INTO Empleado (nombre, puesto, departamento, salario_base, fecha_ingreso) VALUES (%s, %s, %s, %s, %s)",
                (nombre_emp, puesto_emp, depto_emp, salario, fecha_ing)
            )
            empleados_creados += 1
        
        # 3. Insertar Equipos
        # Obtener el último número de equipo existente
        cur.execute("SELECT COUNT(*) FROM Equipo")
        equipos_existentes = cur.fetchone()[0]
        inicio_equipo = equipos_existentes + 1
        
        for i in range(inicio_equipo, inicio_equipo + num_equipos):
            nombre_eq = f"Equipo {i}"
            desc_eq = fake.catch_phrase()[:200]
            cur.execute(
                "INSERT INTO Equipo (nombre_equipo, descripcion) VALUES (%s, %s)",
                (nombre_eq, desc_eq)
            )
            equipos_creados += 1
        
        # 4. Verificar/Insertar Estados
        cur.execute("SELECT COUNT(*) FROM Estado")
        if cur.fetchone()[0] == 0:
            estados = ["Pendiente", "En Progreso", "Completado", "Cancelado"]
            for estado in estados:
                cur.execute("INSERT INTO Estado (nombre_estado) VALUES (%s)", (estado,))
        
        # 5. Insertar MiembroEquipo
        cur.execute("SELECT id_empleado FROM Empleado")
        id_empleados = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT id_equipo FROM Equipo")
        id_equipos = [row[0] for row in cur.fetchall()]
        
        roles = ["Developer", "Analista", "QA", "Líder de Equipo", "Scrum Master"]
        for id_eq in id_equipos:
            miembros = random.sample(id_empleados, k=min(random.randint(3, 6), len(id_empleados)))
            for id_emp in miembros:
                inicio = fake.date_between(start_date="-720d", end_date="-180d")
                fin = None if random.random() < 0.5 else fake.date_between(start_date=inicio, end_date="+180d")
                rol = random.choice(roles)
                cur.execute(
                    "INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro) VALUES (%s, %s, %s, %s, %s)",
                    (id_eq, id_emp, inicio, fin, rol)
                )
        
        # 6. Generar Proyectos con estados aleatorios (el ETL filtrará los necesarios)
        cur.execute("SELECT id_cliente FROM Cliente")
        CLIENTES = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT id_empleado FROM Empleado")
        EMPLEADOS = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT id_equipo FROM Equipo")
        EQUIPOS = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT id_estado FROM Estado")
        TODOS_ESTADOS = [r[0] for r in cur.fetchall()]
        
        for _ in range(num_proyectos):
            id_cliente = random.choice(CLIENTES)
            id_gerente = random.choice(EMPLEADOS)
            # 60% Completado/Cancelado, 40% otros estados (para tener variedad)
            if random.random() < 0.6:
                cur.execute("SELECT id_estado FROM Estado WHERE nombre_estado IN ('Completado','Cancelado')")
                estados_finalizados = [r[0] for r in cur.fetchall()]
                id_estado_proj = random.choice(estados_finalizados) if estados_finalizados else random.choice(TODOS_ESTADOS)
            else:
                id_estado_proj = random.choice(TODOS_ESTADOS)
            
            # Nombres de proyectos más realistas
            prefijos_proyecto = [
                "Sistema de", "Plataforma de", "Aplicación para", "Portal de", "Migración a",
                "Implementación de", "Desarrollo de", "Integración de", "Optimización de", "Renovación de"
            ]
            sufijos_proyecto = [
                "gestión de inventarios", "recursos humanos", "ventas en línea", "servicios al cliente",
                "análisis de datos", "facturación electrónica", "seguimiento de proyectos", "control de calidad",
                "administración de contenidos", "comercio electrónico", "reportería ejecutiva", "procesos automatizados"
            ]
            nombre_proj = f"{random.choice(prefijos_proyecto)} {random.choice(sufijos_proyecto)}"[:150]
            desc_proj = fake.paragraph(nb_sentences=2)[:500]  # Descripción más completa
            fecha_inicio = fake.date_between(start_date="-540d", end_date="-180d")
            duracion_plan_dias = random.randint(45, 150)
            fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan_dias)
            delta_fin = random.randint(-5, 20)
            fecha_fin_real = fecha_fin_plan + timedelta(days=delta_fin)
            presupuesto = round(random.uniform(25000, 90000), 2)
            costo_real = round(presupuesto * random.uniform(0.9, 1.2), 2)
            
            cur.execute(
                "INSERT INTO Proyecto (id_cliente, nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real, presupuesto, costo_real, id_estado, id_empleado_gerente) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (id_cliente, nombre_proj, desc_proj, fecha_inicio, fecha_fin_plan, fecha_fin_real, presupuesto, costo_real, id_estado_proj, id_gerente)
            )
            id_proyecto = cur.lastrowid
            proyectos_creados += 1
            
            # Generar de 8 a 12 tareas para este proyecto con nombres realistas
            tareas_nombres = [
                "Análisis de requerimientos", "Diseño de arquitectura", "Configuración de base de datos",
                "Desarrollo de módulo principal", "Implementación de API REST", "Diseño de interfaz de usuario",
                "Desarrollo del frontend", "Integración de servicios externos", "Pruebas unitarias",
                "Pruebas de integración", "Documentación técnica", "Capacitación de usuarios",
                "Migración de datos", "Optimización de rendimiento", "Implementación de seguridad",
                "Deploy a producción", "Monitoreo y ajustes", "Revisión de código"
            ]
            tareas_seleccionadas = random.sample(tareas_nombres, k=random.randint(8, 12))
            
            for nombre_tarea in tareas_seleccionadas:
                t_inicio_plan = fake.date_between(start_date=fecha_inicio, end_date=(fecha_fin_plan - timedelta(days=15)))
                duracion_plan_t = random.randint(5, 20)
                t_fin_plan = t_inicio_plan + timedelta(days=duracion_plan_t)
                # Fecha de inicio real puede ser null si la tarea no ha comenzado
                t_inicio_real = t_inicio_plan if random.random() > 0.1 else None
                t_fin_real = t_fin_plan + timedelta(days=random.randint(-3, 10))
                horas_plan = random.randint(16, 120)
                horas_reales = max(1, int(horas_plan * random.uniform(0.8, 1.3)))
                # Estado de la tarea: mismo estado que el proyecto
                id_estado_tarea = id_estado_proj
                descripcion_tarea = fake.sentence(nb_words=8)[:200]
                
                cur.execute(
                    "INSERT INTO Tarea (id_proyecto, nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan, fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales, id_estado) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (id_proyecto, nombre_tarea, descripcion_tarea, t_inicio_plan, t_fin_plan, t_inicio_real, t_fin_real, horas_plan, horas_reales, id_estado_tarea)
                )
                id_tarea = cur.lastrowid
                tareas_creadas += 1
                
                id_equipo = random.choice(EQUIPOS)
                cur.execute(
                    "INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion) VALUES (%s,%s,%s,%s)",
                    (id_tarea, id_equipo, t_inicio_plan, t_fin_real)
                )
                asignaciones_creadas += 1
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Datos generados exitosamente',
            'stats': {
                'clientes': clientes_creados,
                'empleados': empleados_creados,
                'equipos': equipos_creados,
                'proyectos': proyectos_creados,
                'tareas': tareas_creadas,
                'asignaciones': asignaciones_creadas
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': str(e),
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
