#!/usr/bin/env python3
"""
Test rápido de conexión al Data Warehouse
"""
import mysql.connector
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 Probando Data Warehouse (172.20.10.2)...")
print("=" * 50)

try:
    conexion = mysql.connector.connect(
        host=os.getenv('DB_DW_HOST', '172.20.10.2'),
        port=3306,
        user=os.getenv('DB_DW_USER', 'etl_user'),
        password=os.getenv('DB_DW_PASSWORD', 'etl_password_123'),
        database=os.getenv('DB_DW_DATABASE', 'dw_proyectos_hist'),
        connect_timeout=5
    )
    
    print("✅ CONEXIÓN EXITOSA!")
    print(f"   Host: {os.getenv('DB_DW_HOST')}")
    print(f"   Database: {os.getenv('DB_DW_DATABASE')}")
    
    # Probar una consulta simple
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM dim_proyecto")
    resultado = cursor.fetchone()
    print(f"   Proyectos en DW: {resultado[0]}")
    
    cursor.close()
    conexion.close()
    print("\n✅ Todo funciona correctamente!")
    
except mysql.connector.Error as e:
    print(f"❌ ERROR: {e}")
    print(f"   Código: {e.errno}")
    print("\n💡 Verifica en el servidor 172.20.10.2:")
    print("   1. MySQL está corriendo")
    print("   2. bind-address = 0.0.0.0 en my.cnf")
    print("   3. Usuario 'etl_user' existe con permisos remotos")
    print("   4. Puerto 3306 abierto en firewall")
    exit(1)
