#!/usr/bin/env python3
"""
Script de Prueba de Conexión Remota
Base de Datos: gestionproyectos_hist @ 172.20.10.3
"""

import mysql.connector
from mysql.connector import Error
import sys

# Configuración de conexión
CONFIG = {
    'host': '172.20.10.3',
    'port': 3306,
    'user': 'etl_user',
    'password': 'etl_password_123',
    'database': 'gestionproyectos_hist'
}

def test_connection():
    """Probar conexión a la base de datos remota"""
    print("=" * 80)
    print("🔌 PRUEBA DE CONEXIÓN A BASE DE DATOS REMOTA")
    print("=" * 80)
    print(f"\n📍 Conectando a:")
    print(f"   Host: {CONFIG['host']}")
    print(f"   Puerto: {CONFIG['port']}")
    print(f"   Base de datos: {CONFIG['database']}")
    print(f"   Usuario: {CONFIG['user']}")
    print("\n⏳ Conectando...")
    
    try:
        # Intentar conexión
        connection = mysql.connector.connect(**CONFIG)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"\n✅ ¡CONEXIÓN EXITOSA!")
            print(f"   Servidor MySQL: {db_info}")
            
            cursor = connection.cursor()
            
            # Obtener información de la base de datos
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"   Base de datos activa: {db_name}")
            
            # Listar tablas
            print("\n📊 TABLAS DISPONIBLES:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                for i, (table,) in enumerate(tables, 1):
                    print(f"   {i}. {table}")
                
                # Contar registros
                print("\n📈 CONTEO DE REGISTROS POR TABLA:")
                print("-" * 80)
                
                total_records = 0
                for (table,) in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"   {table:30} → {count:>10,} registros")
                        total_records += count
                    except Error as e:
                        print(f"   {table:30} → Error: {e}")
                
                print("-" * 80)
                print(f"   {'TOTAL':30} → {total_records:>10,} registros")
                
                # Mostrar estructura de una tabla (ejemplo: Proyecto)
                if 'Proyecto' in [t[0] for t in tables]:
                    print("\n🔍 ESTRUCTURA DE LA TABLA 'Proyecto':")
                    cursor.execute("DESCRIBE Proyecto")
                    columns = cursor.fetchall()
                    
                    print(f"\n   {'Campo':<25} {'Tipo':<20} {'Null':<8} {'Key':<6}")
                    print("   " + "-" * 70)
                    for col in columns:
                        field, type_, null, key, default, extra = col
                        print(f"   {field:<25} {type_:<20} {null:<8} {key:<6}")
                
                # Mostrar algunos proyectos de ejemplo
                print("\n📋 PROYECTOS DE EJEMPLO (primeros 5):")
                cursor.execute("SELECT id_proyecto, nombre, estado, fecha_inicio FROM Proyecto LIMIT 5")
                proyectos = cursor.fetchall()
                
                if proyectos:
                    print(f"\n   {'ID':<6} {'Nombre':<40} {'Estado':<15} {'Fecha Inicio'}")
                    print("   " + "-" * 80)
                    for proyecto in proyectos:
                        id_p, nombre, estado, fecha = proyecto
                        fecha_str = fecha.strftime('%Y-%m-%d') if fecha else 'N/A'
                        nombre_short = (nombre[:37] + '...') if len(nombre) > 40 else nombre
                        print(f"   {id_p:<6} {nombre_short:<40} {estado:<15} {fecha_str}")
                else:
                    print("   No hay proyectos en la base de datos")
                
            else:
                print("   ⚠️  No se encontraron tablas en la base de datos")
            
            # Cerrar cursor y conexión
            cursor.close()
            connection.close()
            
            print("\n" + "=" * 80)
            print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print("\n💡 La conexión remota está funcionando correctamente.")
            print("   Ahora puedes usar esta base de datos en tu sistema ETL.\n")
            
            return True
            
    except Error as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   {e}\n")
        
        # Diagnóstico del error
        error_code = e.errno if hasattr(e, 'errno') else None
        
        if error_code == 1130:  # Host not allowed
            print("🔧 SOLUCIÓN:")
            print("   El usuario no tiene permisos para conectarse desde este host.")
            print("\n   Ejecuta en el SERVIDOR (172.20.10.3):")
            print("   " + "-" * 70)
            print("   mysql -u root -p")
            print("   GRANT ALL PRIVILEGES ON gestionproyectos_hist.*")
            print("   TO 'etl_user'@'172.20.10.12'")
            print("   IDENTIFIED BY 'etl_password_123';")
            print("   FLUSH PRIVILEGES;")
            print("   " + "-" * 70)
            print("\n   O consulta: 01_GestionProyectos/CONFIGURAR_ACCESO_REMOTO.md")
            
        elif error_code == 2003:  # Can't connect
            print("🔧 SOLUCIÓN:")
            print("   No se puede alcanzar el servidor.")
            print("\n   Verifica:")
            print("   1. ¿El servidor MySQL está corriendo?")
            print("      → sudo systemctl status mysql")
            print("   2. ¿El servidor escucha en 0.0.0.0?")
            print("      → Editar bind-address en my.cnf")
            print("   3. ¿El firewall permite el puerto 3306?")
            print("      → sudo ufw allow 3306")
            print("   4. ¿Puedes hacer ping al servidor?")
            print("      → ping 172.20.10.3")
            
        elif error_code == 1045:  # Access denied
            print("🔧 SOLUCIÓN:")
            print("   Usuario o contraseña incorrectos.")
            print("\n   Verifica las credenciales:")
            print(f"   Usuario: {CONFIG['user']}")
            print(f"   Contraseña: {CONFIG['password']}")
            
        else:
            print("🔧 DIAGNÓSTICO:")
            print("   Error no reconocido. Verifica:")
            print("   1. Configuración de red")
            print("   2. Estado del servidor MySQL")
            print("   3. Permisos del usuario")
            print("   4. Configuración del firewall")
        
        print("\n" + "=" * 80)
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
