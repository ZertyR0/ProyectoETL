#!/usr/bin/env python3
"""
Script de verificación para despliegue distribuido
Verifica conectividad y configuración en las 3 máquinas
"""

import os
import sys
import mysql.connector
import requests
import subprocess
import time
from datetime import datetime

# Agregar path para importar configuración
sys.path.append(os.path.join(os.path.dirname(__file__), '02_ETL', 'config'))

try:
    from config_conexion import get_config, test_conexiones
except ImportError:
    print("❌ Error: No se pudo importar la configuración ETL")
    sys.exit(1)

def print_header(title):
    """Imprimir encabezado con formato"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_status(message, status):
    """Imprimir estado con íconos"""
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def verificar_ambiente():
    """Verificar variables de ambiente"""
    print_header("VERIFICACIÓN DE AMBIENTE")
    
    ambiente = os.getenv('ETL_AMBIENTE', 'local')
    print(f"📊 Ambiente configurado: {ambiente}")
    
    if ambiente == 'distribuido':
        print("🌐 Configuración distribuida detectada")
        
        variables_requeridas = [
            'ETL_HOST_ORIGEN',
            'ETL_HOST_DESTINO',
            'ETL_USER_ORIGEN',
            'ETL_USER_DESTINO',
            'ETL_PASSWORD_ORIGEN',
            'ETL_PASSWORD_DESTINO'
        ]
        
        for var in variables_requeridas:
            valor = os.getenv(var)
            if valor:
                if 'PASSWORD' in var:
                    print_status(f"{var}: {'*' * len(valor)}", True)
                else:
                    print_status(f"{var}: {valor}", True)
            else:
                print_status(f"{var}: NO CONFIGURADA", False)
                return False
        
        return True
    else:
        print("🖥️ Configuración local detectada")
        return True

def verificar_conectividad_red():
    """Verificar conectividad de red a máquinas remotas"""
    print_header("VERIFICACIÓN DE CONECTIVIDAD DE RED")
    
    config = get_config()
    
    hosts_a_probar = []
    
    if config['host_origen'] != 'localhost':
        hosts_a_probar.append(('BD Origen', config['host_origen'], config['port_origen']))
    
    if config['host_destino'] != 'localhost':
        hosts_a_probar.append(('Datawarehouse', config['host_destino'], config['port_destino']))
    
    if not hosts_a_probar:
        print("🖥️ Configuración local - No se requiere verificación de red")
        return True
    
    todas_conexiones_ok = True
    
    for nombre, host, puerto in hosts_a_probar:
        try:
            # Verificar conectividad con ping
            resultado = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                     capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print_status(f"Ping a {nombre} ({host})", True)
                
                # Verificar puerto específico
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                resultado_puerto = sock.connect_ex((host, puerto))
                sock.close()
                
                if resultado_puerto == 0:
                    print_status(f"Puerto {puerto} abierto en {nombre}", True)
                else:
                    print_status(f"Puerto {puerto} cerrado en {nombre}", False)
                    todas_conexiones_ok = False
            else:
                print_status(f"Ping a {nombre} ({host})", False)
                todas_conexiones_ok = False
                
        except Exception as e:
            print_status(f"Error verificando {nombre}: {str(e)}", False)
            todas_conexiones_ok = False
    
    return todas_conexiones_ok

def verificar_bases_datos():
    """Verificar conexiones a bases de datos"""
    print_header("VERIFICACIÓN DE BASES DE DATOS")
    
    return test_conexiones()

def verificar_estructura_bd():
    """Verificar que las tablas existan"""
    print_header("VERIFICACIÓN DE ESTRUCTURA DE BD")
    
    config = get_config()
    
    # Verificar BD origen
    try:
        conn_origen = mysql.connector.connect(
            host=config['host_origen'],
            port=config['port_origen'],
            user=config['user_origen'],
            password=config['password_origen'],
            database=config['database_origen']
        )
        
        cursor = conn_origen.cursor()
        cursor.execute("SHOW TABLES")
        tablas_origen = [tabla[0] for tabla in cursor.fetchall()]
        
        tablas_esperadas_origen = ['Cliente', 'Empleado', 'Equipo', 'Estado', 'Proyecto', 'Tarea']
        
        for tabla in tablas_esperadas_origen:
            if tabla in tablas_origen:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print_status(f"Tabla {tabla}: {count} registros", True)
            else:
                print_status(f"Tabla {tabla}: NO EXISTE", False)
        
        cursor.close()
        conn_origen.close()
        
    except Exception as e:
        print_status(f"Error verificando BD origen: {str(e)}", False)
        return False
    
    # Verificar Datawarehouse
    try:
        conn_destino = mysql.connector.connect(
            host=config['host_destino'],
            port=config['port_destino'],
            user=config['user_destino'],
            password=config['password_destino'],
            database=config['database_destino']
        )
        
        cursor = conn_destino.cursor()
        cursor.execute("SHOW TABLES")
        tablas_destino = [tabla[0] for tabla in cursor.fetchall()]
        
        tablas_esperadas_destino = ['DimCliente', 'DimEmpleado', 'DimProyecto', 'HechoProyecto']
        
        for tabla in tablas_esperadas_destino:
            if tabla in tablas_destino:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print_status(f"Tabla {tabla}: {count} registros", True)
            else:
                print_status(f"Tabla {tabla}: NO EXISTE", False)
        
        cursor.close()
        conn_destino.close()
        
        return True
        
    except Exception as e:
        print_status(f"Error verificando Datawarehouse: {str(e)}", False)
        return False

def verificar_servicios_web():
    """Verificar que los servicios web estén funcionando"""
    print_header("VERIFICACIÓN DE SERVICIOS WEB")
    
    # Verificar si el dashboard está corriendo
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        if response.status_code == 200:
            print_status("Dashboard API (puerto 5001)", True)
        else:
            print_status(f"Dashboard API responde con código {response.status_code}", False)
    except requests.exceptions.ConnectionError:
        print_status("Dashboard API (puerto 5001): NO DISPONIBLE", False)
    except Exception as e:
        print_status(f"Error verificando Dashboard API: {str(e)}", False)
    
    # Verificar frontend si está disponible
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print_status("Frontend Web (puerto 8000)", True)
        else:
            print_status("Frontend Web (puerto 8000): DISPONIBLE CON ADVERTENCIAS", False)
    except requests.exceptions.ConnectionError:
        print_status("Frontend Web (puerto 8000): NO DISPONIBLE (opcional)", True)
    except Exception as e:
        print_status(f"Frontend Web: {str(e)}", False)

def ejecutar_prueba_etl():
    """Ejecutar una prueba básica del ETL"""
    print_header("PRUEBA BÁSICA DE ETL")
    
    try:
        # Importar y ejecutar ETL
        sys.path.append(os.path.join(os.path.dirname(__file__), '02_ETL', 'scripts'))
        
        print("🔄 Iniciando prueba de ETL...")
        
        # Aquí ejecutaríamos el ETL real, pero por ahora solo verificamos que se puede importar
        try:
            from etl_principal import main as etl_main
            print_status("ETL principal importado correctamente", True)
            
            # Por seguridad, no ejecutamos ETL completo en verificación
            print("⚠️ ETL no ejecutado (solo verificación de importación)")
            print("💡 Para ejecutar ETL completo: python 02_ETL/scripts/etl_principal.py")
            
        except ImportError as e:
            print_status(f"Error importando ETL: {str(e)}", False)
            return False
            
        return True
        
    except Exception as e:
        print_status(f"Error en prueba ETL: {str(e)}", False)
        return False

def generar_reporte_final(resultados):
    """Generar reporte final de verificación"""
    print_header("REPORTE FINAL DE VERIFICACIÓN")
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(resultados.values())
    
    print(f"📊 Resumen de verificación:")
    print(f"   • Total de pruebas: {total_pruebas}")
    print(f"   • Pruebas exitosas: {pruebas_exitosas}")
    print(f"   • Pruebas fallidas: {total_pruebas - pruebas_exitosas}")
    print(f"   • Porcentaje de éxito: {(pruebas_exitosas/total_pruebas)*100:.1f}%")
    
    print(f"\n📋 Detalle por categoría:")
    for categoria, resultado in resultados.items():
        icon = "✅" if resultado else "❌"
        print(f"   {icon} {categoria}")
    
    if all(resultados.values()):
        print(f"\n🎉 ¡VERIFICACIÓN COMPLETADA EXITOSAMENTE!")
        print(f"   Su sistema ETL distribuido está listo para usar.")
        return True
    else:
        print(f"\n⚠️ VERIFICACIÓN COMPLETADA CON ERRORES")
        print(f"   Revise los errores arriba antes de usar el sistema.")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICADOR DE SISTEMA ETL DISTRIBUIDO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {}
    
    # Ejecutar todas las verificaciones
    resultados['Ambiente'] = verificar_ambiente()
    resultados['Conectividad de Red'] = verificar_conectividad_red()
    resultados['Bases de Datos'] = verificar_bases_datos()
    resultados['Estructura de BD'] = verificar_estructura_bd()
    resultados['Servicios Web'] = verificar_servicios_web()
    resultados['ETL'] = ejecutar_prueba_etl()
    
    # Generar reporte final
    exito_total = generar_reporte_final(resultados)
    
    # Código de salida
    sys.exit(0 if exito_total else 1)

if __name__ == "__main__":
    main()
