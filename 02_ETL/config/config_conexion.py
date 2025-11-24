#!/usr/bin/env python3
"""
Configuración de conexiones para el sistema ETL
Soporta tanto configuración local como distribuida
"""

import os
from typing import Dict, Any

# =========================================================
# CONFIGURACIÓN PARA DESARROLLO LOCAL
# =========================================================
CONFIG_LOCAL = {
    'host_origen': 'localhost',
    'port_origen': 3306,
    'user_origen': 'root',
    'password_origen': '',
    'database_origen': 'gestionproyectos_hist',
    'unix_socket': '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
    
    # Para desarrollo local, usar mismo servidor para ambas BD
    'host_destino': 'localhost',
    'port_destino': 3306,
    'user_destino': 'root',
    'password_destino': '',
    'database_destino': 'dw_proyectos_hist'
}

# =========================================================
# CONFIGURACIÓN PARA AMBIENTE DISTRIBUIDO (3 MÁQUINAS)
# =========================================================
CONFIG_DISTRIBUIDO = {
    # Máquina 1: Base de datos origen
    'host_origen': '172.20.10.3',
    'port_origen': 3306,
    'user_origen': 'etl_user',
    'password_origen': 'etl_password_123',
    'database_origen': 'gestionproyectos_hist',
    
    # Máquina 3: Datawarehouse
    'host_destino': '172.20.10.2',
    'port_destino': 3306,
    'user_destino': 'etl_user',
    'password_destino': 'etl_password_123',
    'database_destino': 'dw_proyectos_hist'
}

# =========================================================
# CONFIGURACIÓN PARA TESTING
# =========================================================
CONFIG_TEST = {
    'host_origen': 'localhost',
    'port_origen': 3306,
    'user_origen': 'root',
    'password_origen': '',
    'database_origen': 'test_gestionproyectos_hist',
    
    'host_destino': 'localhost',
    'port_destino': 3306,
    'user_destino': 'root',
    'password_destino': '',
    'database_destino': 'test_dw_proyectos_hist'
}

def get_config(ambiente: str = 'local') -> Dict[str, Any]:
    """
    Obtiene la configuración según el ambiente especificado
    
    Args:
        ambiente: 'local', 'distribuido', o 'test'
    
    Returns:
        Dict con la configuración de conexiones
    """
    configs = {
        'local': CONFIG_LOCAL,
        'distribuido': CONFIG_DISTRIBUIDO,
        'test': CONFIG_TEST
    }
    
    # Verificar si hay variables de ambiente que sobrescriban la configuración
    ambiente_env = os.getenv('ETL_AMBIENTE', ambiente)
    
    if ambiente_env not in configs:
        print(f"⚠️ Ambiente '{ambiente_env}' no reconocido, usando 'local'")
        ambiente_env = 'local'
    
    config = configs[ambiente_env].copy()
    
    # Permitir sobrescribir con variables de ambiente
    config.update({
        'host_origen': os.getenv('ETL_HOST_ORIGEN', config['host_origen']),
        'port_origen': int(os.getenv('ETL_PORT_ORIGEN', config['port_origen'])),
        'user_origen': os.getenv('ETL_USER_ORIGEN', config['user_origen']),
        'password_origen': os.getenv('ETL_PASSWORD_ORIGEN', config['password_origen']),
        'database_origen': os.getenv('ETL_DB_ORIGEN', config['database_origen']),
        
        'host_destino': os.getenv('ETL_HOST_DESTINO', config['host_destino']),
        'port_destino': int(os.getenv('ETL_PORT_DESTINO', config['port_destino'])),
        'user_destino': os.getenv('ETL_USER_DESTINO', config['user_destino']),
        'password_destino': os.getenv('ETL_PASSWORD_DESTINO', config['password_destino']),
        'database_destino': os.getenv('ETL_DB_DESTINO', config['database_destino'])
    })
    
    return config

def get_connection_string(tipo: str = 'origen', ambiente: str = 'local') -> str:
    """
    Genera string de conexión para SQLAlchemy
    
    Args:
        tipo: 'origen' o 'destino'
        ambiente: 'local', 'distribuido', o 'test'
    
    Returns:
        String de conexión para SQLAlchemy
    """
    config = get_config(ambiente)
    
    if tipo == 'origen':
        return f"mysql+mysqlconnector://{config['user_origen']}:{config['password_origen']}@{config['host_origen']}:{config['port_origen']}/{config['database_origen']}"
    elif tipo == 'destino':
        return f"mysql+mysqlconnector://{config['user_destino']}:{config['password_destino']}@{config['host_destino']}:{config['port_destino']}/{config['database_destino']}"
    else:
        raise ValueError("tipo debe ser 'origen' o 'destino'")

def test_conexiones(ambiente: str = 'local') -> bool:
    """
    Prueba las conexiones a las bases de datos
    
    Args:
        ambiente: Ambiente a probar
    
    Returns:
        True si ambas conexiones funcionan
    """
    import mysql.connector
    
    config = get_config(ambiente)
    
    try:
        # Probar conexión origen
        print(f"🔍 Probando conexión origen ({config['host_origen']}:{config['port_origen']})...")
        conn_origen = mysql.connector.connect(
            host=config['host_origen'],
            port=config['port_origen'],
            user=config['user_origen'],
            password=config['password_origen'],
            database=config['database_origen']
        )
        conn_origen.close()
        print("   Conexión origen exitosa")
        
        # Probar conexión destino
        print(f"🔍 Probando conexión destino ({config['host_destino']}:{config['port_destino']})...")
        conn_destino = mysql.connector.connect(
            host=config['host_destino'],
            port=config['port_destino'],
            user=config['user_destino'],
            password=config['password_destino'],
            database=config['database_destino']
        )
        conn_destino.close()
        print("   Conexión destino exitosa")
        
        print("🎉 Todas las conexiones funcionan correctamente")
        return True
        
    except Exception as e:
        print(f" Error en las conexiones: {e}")
        return False

if __name__ == "__main__":
    """Script de prueba para verificar conexiones"""
    import sys
    
    ambiente = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    print(f"🚀 Probando configuración ETL - Ambiente: {ambiente}")
    print("=" * 50)
    
    config = get_config(ambiente)
    print("📋 Configuración actual:")
    for key, value in config.items():
        if 'password' in key:
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    test_conexiones(ambiente)
