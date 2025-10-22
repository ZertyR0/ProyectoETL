#!/usr/bin/env python3
"""
ETL REMOTO PORTABLE - Ejecutable desde cualquier computadora
===========================================================
Este script puede ser ejecutado desde cualquier computadora con Python.
Se conecta remotamente a la base de datos y ejecuta el proceso ETL completo.

Requisitos:
- Python 3.6+
- pandas, sqlalchemy, mysql-connector-python (se instalan automáticamente)

Uso:
    python3 etl_remoto_portable.py
"""

import sys
import subprocess
import os
from datetime import datetime

def load_config():
    """Cargar configuración desde archivo config_conexion.py"""
    try:
        # Intentar cargar configuración personalizada
        from config_conexion import get_config
        return get_config()
    except ImportError:
        # Usar configuración por defecto si no existe el archivo
        print("⚠️ Archivo config_conexion.py no encontrado, usando configuración por defecto")
        return {
            'host': '172.26.163.200',
            'port': 3306,
            'user': 'etl_user',
            'password': 'etl_password_123',
            'db_origen': 'gestionproyectos_hist',
            'db_destino': 'dw_proyectos_hist',
            'timeout': 30,
            'reintentos': 3
        }

# Cargar configuración
SERVER_CONFIG = load_config()

def print_header():
    """Mostrar header del ETL"""
    print("=" * 70)
    print("🚀 ETL REMOTO PORTABLE")
    print("=" * 70)
    print(f"📍 Servidor: {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    print(f"📊 Base origen: {SERVER_CONFIG['db_origen']}")
    print(f"🏗️ Data warehouse: {SERVER_CONFIG['db_destino']}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

def install_dependencies():
    """Instalar dependencias automáticamente"""
    print("🔍 Verificando dependencias...")
    
    required_packages = [
        'pandas',
        'sqlalchemy',
        'mysql-connector-python'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} ya está instalado")
        except ImportError:
            print(f"📦 Instalando {package}...")
            install_success = False
            
            # Intentar diferentes métodos de instalación
            install_methods = [
                # Método 1: instalación normal
                [sys.executable, '-m', 'pip', 'install', package, '--quiet'],
                # Método 2: instalación con --user
                [sys.executable, '-m', 'pip', 'install', package, '--user', '--quiet'],
                # Método 3: instalación con --break-system-packages (último recurso)
                [sys.executable, '-m', 'pip', 'install', package, '--break-system-packages', '--quiet']
            ]
            
            for method in install_methods:
                try:
                    subprocess.check_call(method)
                    print(f"✅ {package} instalado exitosamente")
                    install_success = True
                    break
                except subprocess.CalledProcessError:
                    continue
            
            if not install_success:
                print(f"❌ Error instalando {package}")
                print("💡 Instala manualmente con uno de estos comandos:")
                print(f"   pip install {package}")
                print(f"   pip install {package} --user")
                print(f"   pip install {package} --break-system-packages")
                return False
    
    print("✅ Todas las dependencias están listas")
    return True

def test_connection():
    """Probar conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        import mysql.connector
        
        # Probar conexión a base origen
        conn_origen = mysql.connector.connect(
            host=SERVER_CONFIG['host'],
            port=SERVER_CONFIG['port'],
            user=SERVER_CONFIG['user'],
            password=SERVER_CONFIG['password'],
            database=SERVER_CONFIG['db_origen']
        )
        
        cursor = conn_origen.cursor()
        cursor.execute("SELECT COUNT(*) FROM Proyecto")
        result = cursor.fetchone()
        proyectos = result[0] if result else 0
        cursor.close()
        conn_origen.close()
        
        print(f"✅ Conexión origen exitosa: {proyectos} proyectos encontrados")
        
        # Probar conexión a data warehouse
        conn_dw = mysql.connector.connect(
            host=SERVER_CONFIG['host'],
            port=SERVER_CONFIG['port'],
            user=SERVER_CONFIG['user'],
            password=SERVER_CONFIG['password'],
            database=SERVER_CONFIG['db_destino']
        )
        
        cursor = conn_dw.cursor()
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        cursor.close()
        conn_dw.close()
        
        print(f"✅ Conexión data warehouse exitosa: {len(tablas)} tablas encontradas")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verifica:")
        print("   - Conexión a internet")
        print(f"   - Servidor {SERVER_CONFIG['host']} accesible")
        print("   - Credenciales correctas")
        return False

def execute_etl():
    """Ejecutar el proceso ETL"""
    print("🚀 Iniciando proceso ETL...")
    
    try:
        import pandas as pd
        import numpy as np
        from sqlalchemy import create_engine, text
        
        # URLs de conexión
        src_url = f"mysql+mysqlconnector://{SERVER_CONFIG['user']}:{SERVER_CONFIG['password']}@{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/{SERVER_CONFIG['db_origen']}"
        dw_url = f"mysql+mysqlconnector://{SERVER_CONFIG['user']}:{SERVER_CONFIG['password']}@{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}/{SERVER_CONFIG['db_destino']}"
        
        # Crear engines
        engine_src = create_engine(src_url, pool_pre_ping=True)
        engine_dw = create_engine(dw_url, pool_pre_ping=True)
        
        print("📊 Conectado a las bases de datos")
        
        # Verificar datos origen
        with engine_src.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as proyectos FROM Proyecto"))
            row = result.fetchone()
            proyectos = row[0] if row else 0
            print(f"📋 Proyectos en origen: {proyectos}")
            
            if proyectos == 0:
                print("⚠️ No hay proyectos en la base origen")
                return False
        
        # Limpiar data warehouse
        print("🧹 Limpiando data warehouse...")
        with engine_dw.begin() as conn:
            try:
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
                conn.execute(text("TRUNCATE TABLE HechoTarea"))
                conn.execute(text("TRUNCATE TABLE HechoProyecto"))  
                conn.execute(text("TRUNCATE TABLE DimTiempo"))
                conn.execute(text("TRUNCATE TABLE DimProyecto"))
                conn.execute(text("TRUNCATE TABLE DimEquipo"))
                conn.execute(text("TRUNCATE TABLE DimEmpleado"))
                conn.execute(text("TRUNCATE TABLE DimCliente"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
                print("✅ Data warehouse limpiado")
            except Exception as e:
                print(f"⚠️ Advertencia al limpiar: {e}")
        
        # Cargar dimensiones
        print("📋 Cargando dimensiones...")
        
        # DimCliente
        df_cliente = pd.read_sql("SELECT id_cliente, nombre, sector FROM Cliente", engine_src)
        df_cliente.to_sql("DimCliente", con=engine_dw, if_exists="append", index=False)
        print(f"✅ DimCliente: {len(df_cliente)} registros")
        
        # DimEmpleado
        df_empleado = pd.read_sql("SELECT id_empleado, nombre, puesto FROM Empleado", engine_src)
        df_empleado.to_sql("DimEmpleado", con=engine_dw, if_exists="append", index=False)
        print(f"✅ DimEmpleado: {len(df_empleado)} registros")
        
        # DimEquipo
        df_equipo = pd.read_sql("SELECT id_equipo, nombre_equipo FROM Equipo", engine_src)
        df_equipo.to_sql("DimEquipo", con=engine_dw, if_exists="append", index=False)
        print(f"✅ DimEquipo: {len(df_equipo)} registros")
        
        # DimProyecto
        df_proyecto = pd.read_sql("""
            SELECT id_proyecto, nombre as nombre_proyecto, 
                   fecha_inicio as fecha_inicio_plan, 
                   fecha_fin_plan, 
                   presupuesto as costo_plan
            FROM Proyecto
        """, engine_src)
        df_proyecto.to_sql("DimProyecto", con=engine_dw, if_exists="append", index=False)
        print(f"✅ DimProyecto: {len(df_proyecto)} registros")
        
        # DimTiempo
        print("⏰ Generando dimensión tiempo...")
        fechas_unicas = set()
        
        # Obtener fechas únicas de proyectos
        df_fechas = pd.read_sql("SELECT fecha_inicio, fecha_fin_plan, fecha_fin_real FROM Proyecto", engine_src)
        for col in df_fechas.columns:
            fechas_unicas.update(pd.to_datetime(df_fechas[col].dropna()).dt.date.tolist())
        
        # Obtener fechas de tareas
        df_fechas_tarea = pd.read_sql("SELECT fecha_inicio_plan, fecha_fin_plan, fecha_fin_real FROM Tarea", engine_src)
        for col in df_fechas_tarea.columns:
            fechas_unicas.update(pd.to_datetime(df_fechas_tarea[col].dropna()).dt.date.tolist())
        
        # Crear DimTiempo
        dim_tiempo = pd.DataFrame(sorted(fechas_unicas), columns=["fecha"])
        dim_tiempo["fecha"] = pd.to_datetime(dim_tiempo["fecha"])
        dim_tiempo["anio"] = dim_tiempo["fecha"].dt.year
        dim_tiempo["mes"] = dim_tiempo["fecha"].dt.month
        dim_tiempo["trimestre"] = ((dim_tiempo["mes"] - 1) // 3) + 1
        
        dim_tiempo[["fecha", "anio", "mes", "trimestre"]].to_sql("DimTiempo", con=engine_dw, if_exists="append", index=False)
        print(f"✅ DimTiempo: {len(dim_tiempo)} registros")
        
        # Cerrar conexiones
        engine_src.dispose()
        engine_dw.dispose()
        
        print("🎉 ETL completado exitosamente!")
        print("📊 Data warehouse actualizado con datos remotos")
        return True
        
    except Exception as e:
        print(f"❌ Error durante ETL: {e}")
        print("💡 Revisa la conexión y permisos de base de datos")
        return False

def main():
    """Función principal"""
    try:
        print_header()
        
        # Verificar Python
        if sys.version_info < (3, 6):
            print("❌ Se requiere Python 3.6 o superior")
            print(f"📍 Versión actual: {sys.version}")
            return 1
        
        print(f"✅ Python {sys.version.split()[0]} detectado")
        
        # Instalar dependencias
        if not install_dependencies():
            return 1
        
        print()
        
        # Probar conexión
        if not test_connection():
            return 1
        
        print()
        
        # Preguntar si continuar
        respuesta = input("¿Ejecutar ETL? (s/n): ").strip().lower()
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ ETL cancelado por el usuario")
            return 0
        
        print()
        
        # Ejecutar ETL
        if execute_etl():
            print()
            print("=" * 70)
            print("🎉 PROCESO ETL COMPLETADO EXITOSAMENTE")
            print("📊 Data warehouse remoto actualizado")
            print("=" * 70)
            return 0
        else:
            print()
            print("=" * 70)
            print("❌ PROCESO ETL FALLÓ")
            print("💡 Revisa los errores anteriores")
            print("=" * 70)
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ ETL interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
