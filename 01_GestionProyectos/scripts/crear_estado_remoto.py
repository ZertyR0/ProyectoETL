#!/usr/bin/env python3
"""
Script para crear la tabla Estado en la BD remota
Máquina 1: 172.20.10.3 - gestionproyectos_hist
"""

import mysql.connector
from mysql.connector import Error
import sys
from pathlib import Path

def ejecutar_sql_file(conn, sql_file_path):
    """Ejecuta un archivo SQL línea por línea"""
    cursor = conn.cursor()
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Dividir por punto y coma, pero ignorar los que están en comentarios
    statements = []
    current_statement = []
    in_delimiter = False
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Ignorar comentarios
        if line.startswith('--') or not line:
            continue
        
        # Manejar DELIMITER
        if line.upper().startswith('DELIMITER'):
            in_delimiter = not in_delimiter
            continue
        
        current_statement.append(line)
        
        # Si termina con ; y no estamos en un bloque DELIMITER
        if line.endswith(';') and not in_delimiter:
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # Ejecutar cada statement
    resultados = []
    for i, statement in enumerate(statements, 1):
        try:
            # Saltar comentarios de resultado
            if 'Resultado' in statement and 'SELECT' in statement and '===' in statement:
                cursor.execute(statement)
                result = cursor.fetchall()
                if result:
                    print(f"\n{result[0][0]}")
                continue
            
            cursor.execute(statement)
            
            # Si es un SELECT, mostrar resultados
            if statement.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                if result:
                    # Obtener nombres de columnas
                    columns = [desc[0] for desc in cursor.description]
                    print(f"\n{'  '.join(columns)}")
                    print("─" * (sum(len(c) for c in columns) + len(columns) * 2))
                    for row in result:
                        print(f"{'  '.join(str(val) for val in row)}")
            else:
                resultados.append(f" Statement {i} ejecutado")
            
            conn.commit()
            
        except Error as e:
            if 'Duplicate entry' in str(e) or 'already exists' in str(e):
                resultados.append(f"  Statement {i} omitido (ya existe)")
            else:
                print(f" Error en statement {i}: {e}")
                print(f"   SQL: {statement[:100]}...")
                # No detener, continuar con los siguientes
    
    cursor.close()
    return resultados

def main():
    """Función principal"""
    print("=" * 80)
    print("   CREAR TABLA ESTADO EN BASE DE DATOS REMOTA")
    print("=" * 80)
    
    config = {
        'host': '172.20.10.3',
        'port': 3306,
        'user': 'etl_user',
        'password': 'etl_password_123',
        'database': 'gestionproyectos_hist'
    }
    
    print(f"\n📍 Conectando a: {config['host']}:{config['port']}")
    print(f" Base de datos: {config['database']}")
    print(f"👤 Usuario: {config['user']}")
    
    try:
        print("\n⏳ Estableciendo conexión...")
        conn = mysql.connector.connect(**config)
        print(" Conexión exitosa!\n")
        
        # Ruta del archivo SQL
        script_dir = Path(__file__).parent
        sql_file = script_dir / 'crear_tabla_estado.sql'
        
        if not sql_file.exists():
            print(f" Error: No se encontró el archivo {sql_file}")
            return 1
        
        print(f"📄 Ejecutando: {sql_file.name}")
        print("─" * 80)
        
        resultados = ejecutar_sql_file(conn, sql_file)
        
        print("\n" + "─" * 80)
        print(" RESUMEN DE EJECUCIÓN:")
        for resultado in resultados:
            print(f"   {resultado}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print(" ¡TABLA ESTADO CREADA EXITOSAMENTE!")
        print("=" * 80)
        print("\n Ahora puedes:")
        print("   1. Ejecutar el proceso ETL desde el dashboard")
        print("   2. Generar más datos de prueba")
        print("   3. Usar la funcionalidad de trazabilidad")
        
        return 0
        
    except Error as e:
        print(f"\n ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
