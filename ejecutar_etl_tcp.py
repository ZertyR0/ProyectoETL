#!/usr/bin/env python3
"""
Script para ejecutar ETL usando conexión TCP
"""

import mysql.connector
from datetime import datetime
import sys

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def ejecutar_etl():
    try:
        print(f"[{timestamp()}] Conectando a BD origen...")
        conn_origen = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gestionproyectos_hist'
        )
        print(f"[{timestamp()}]  Conectado a origen")
        
        print(f"[{timestamp()}] Conectando a DataWarehouse...")
        conn_dw = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dw_proyectos_hist'
        )
        print(f"[{timestamp()}]  Conectado a DW")
        
        cursor = conn_dw.cursor(dictionary=True)
        
        print(f"[{timestamp()}] Ejecutando sp_etl_proceso_completo...")
        print("="*70)
        
        inicio = datetime.now()
        
        # Intentar con el segundo procedimiento
        cursor.callproc('sp_etl_proceso_completo', 
                       [conn_origen.connection_id, 'localhost', 'root', '', 'gestionproyectos_hist'])
        
        # Obtener resultado
        for result in cursor.stored_results():
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(row)
        
        conn_dw.commit()
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print("="*70)
        print(f"[{timestamp()}]  ETL completado exitosamente")
        print(f"[{timestamp()}] Duración: {duracion:.2f} segundos")
        
        # Verificar resultados
        cursor.execute("SELECT COUNT(*) as total FROM HechoProyecto")
        result = cursor.fetchone()
        print(f"[{timestamp()}] HechoProyecto: {result['total']} registros")
        
        cursor.execute("SELECT COUNT(*) as total FROM HechoTarea")
        result = cursor.fetchone()
        print(f"[{timestamp()}] HechoTarea: {result['total']} registros")
        
        cursor.execute("SELECT COUNT(*) as total FROM HechoOKR")
        result = cursor.fetchone()
        print(f"[{timestamp()}] HechoOKR: {result['total']} registros")
        
        cursor.close()
        conn_dw.close()
        conn_origen.close()
        
        print("="*70)
        return True
        
    except mysql.connector.Error as e:
        print(f"\n[{timestamp()}]  Error MySQL: {e.errno} ({e.sqlstate}): {e.msg}")
        return False
    except Exception as e:
        print(f"\n[{timestamp()}]  Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ejecutar_etl()
    sys.exit(0 if success else 1)
