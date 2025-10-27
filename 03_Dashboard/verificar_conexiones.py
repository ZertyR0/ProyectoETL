#!/usr/bin/env python3
"""
Script para verificar conexiones MySQL a los servidores remotos
"""

import mysql.connector
from mysql.connector import Error
import sys

def test_connection(host, port, user, password, database, name):
    """Prueba conexión a MySQL"""
    print(f"\n{'='*60}")
    print(f"🔍 Probando {name}")
    print(f"{'='*60}")
    print(f"Host: {host}:{port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    
    try:
        # Intentar conexión
        print("\n⏳ Conectando...")
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ CONEXIÓN EXITOSA")
            print(f"   Versión MySQL: {db_info}")
            
            # Obtener información adicional
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"   Base de datos activa: {db_name[0]}")
            
            # Listar tablas
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"   Tablas encontradas: {len(tables)}")
            
            if tables:
                print(f"   Lista de tablas:")
                for table in tables[:5]:  # Mostrar primeras 5
                    print(f"      - {table[0]}")
                if len(tables) > 5:
                    print(f"      ... y {len(tables) - 5} más")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ ERROR DE CONEXIÓN")
        print(f"   Código: {e.errno if hasattr(e, 'errno') else 'N/A'}")
        print(f"   Mensaje: {str(e)}")
        
        # Diagnóstico específico
        error_str = str(e).lower()
        if 'access denied' in error_str:
            print("\n💡 Posible causa: Usuario/password incorrecto")
            print("   Solución en el servidor:")
            print(f"   mysql -u root -p")
            print(f"   CREATE USER '{user}'@'%' IDENTIFIED BY '{password}';")
            print(f"   GRANT ALL PRIVILEGES ON {database}.* TO '{user}'@'%';")
            print(f"   FLUSH PRIVILEGES;")
            
        elif 'unknown database' in error_str:
            print("\n💡 Posible causa: Base de datos no existe")
            print("   Solución: Crear la base de datos en el servidor")
            
        elif "can't connect" in error_str or 'timed out' in error_str:
            print("\n💡 Posible causa: Servidor no acepta conexiones remotas")
            print("   Solución en el servidor:")
            print("   1. Editar /etc/mysql/mysql.conf.d/mysqld.cnf")
            print("      bind-address = 0.0.0.0")
            print("   2. sudo systemctl restart mysql")
            print("   3. sudo ufw allow 3306/tcp")
            
        elif 'connection refused' in error_str:
            print("\n💡 Posible causa: MySQL no está corriendo o firewall bloqueando")
            print("   Verificar en el servidor:")
            print("   sudo systemctl status mysql")
            print("   sudo ufw status")
        
        return False
    
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 VERIFICADOR DE CONEXIONES MYSQL")
    print("="*60)
    
    # Configuración de servidores
    servers = [
        {
            'name': 'Módulo 1 - Base de Datos Gestión',
            'host': '172.20.10.3',
            'port': 3306,
            'user': 'etl_user',
            'password': 'etl_password_123',
            'database': 'gestionproyectos_hist'
        },
        {
            'name': 'Módulo 3 - Data Warehouse',
            'host': '172.20.10.2',
            'port': 3306,
            'user': 'etl_user',
            'password': 'etl_password_123',
            'database': 'dw_proyectos_hist'
        }
    ]
    
    results = []
    
    # Probar cada servidor
    for server in servers:
        success = test_connection(
            server['host'],
            server['port'],
            server['user'],
            server['password'],
            server['database'],
            server['name']
        )
        results.append((server['name'], success))
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE CONEXIONES")
    print(f"{'='*60}")
    
    all_ok = True
    for name, success in results:
        status = "✅ OK" if success else "❌ FALLO"
        print(f"{status} - {name}")
        if not success:
            all_ok = False
    
    print(f"{'='*60}\n")
    
    if all_ok:
        print("🎉 ¡Todas las conexiones funcionan correctamente!")
        print("✅ Tu Dashboard puede conectarse a ambos servidores")
        return 0
    else:
        print("⚠️  Algunas conexiones fallaron")
        print("💡 Revisa los mensajes de error arriba para solucionar")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Verificación interrumpida por el usuario")
        sys.exit(130)
