#!/usr/bin/env python3
"""
ETL FINAL - SEGURIDAD ABSOLUTA
Python NO conoce estructura de BD
Solo ejecuta 1 procedimiento almacenado
"""

import sys
import mysql.connector
from datetime import datetime

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def ejecutar_etl():
    """Ejecutar ETL completo - 1 sola llamada a MySQL"""
    
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "ETL - SEGURIDAD ABSOLUTA (OPCIÓN 3)" + " " * 23 + "║")
    print("║" + " " * 5 + "Python ejecuta 1 SP - CERO conocimiento de estructura" + " " * 8 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        print(f"[{timestamp()}] 🔄 Conectando a MySQL...")
        
        # Conexión local XAMPP
        conn = mysql.connector.connect(
            unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
            user='root',
            password='',
            database='dw_proyectos_hist'
        )
        
        print(f"[{timestamp()}] ✅ Conectado")
        print(f"[{timestamp()}] 🔄 Ejecutando procedimiento almacenado...")
        print()
        
        cursor = conn.cursor(dictionary=True)
        
        # LA ÚNICA LÍNEA IMPORTANTE - Todo el ETL está aquí
        inicio = datetime.now()
        cursor.execute("CALL sp_ejecutar_etl_completo()")
        resultado = cursor.fetchone()
        fin = datetime.now()
        
        cursor.nextset()
        cursor.close()
        conn.close()
        
        duracion = (fin - inicio).total_seconds()
        
        # Mostrar resultado
        if resultado and resultado.get('estado') == 'EXITOSO':
            print("=" * 70)
            print(f"[{timestamp()}] ✅ {resultado.get('mensaje')}")
            print("=" * 70)
            print(f"  📊 Clientes cargados:       {resultado.get('clientes', 0):,}")
            print(f"  📊 Empleados cargados:      {resultado.get('empleados', 0):,}")
            print(f"  📊 Equipos cargados:        {resultado.get('equipos', 0):,}")
            print(f"  📊 Proyectos procesados:    {resultado.get('proyectos', 0):,}")
            print(f"  📊 Tareas procesadas:       {resultado.get('tareas', 0):,}")
            print(f"  📊 Dimensión tiempo:        {resultado.get('registros_tiempo', 0):,} registros")
            print()
            print(f"  ⏱️  Duración total:          {duracion:.2f} segundos")
            print(f"  📅 Fecha/Hora:              {resultado.get('fecha_hora')}")
            print("=" * 70)
            print()
         
            print("=" * 70)
            return True
        else:
            print(f"[{timestamp()}] ❌ Error: Procedimiento no retornó éxito")
            if resultado:
                print(f"    Mensaje: {resultado.get('mensaje', 'Sin mensaje')}")
            return False
            
    except mysql.connector.Error as e:
        print(f"[{timestamp()}] ❌ Error MySQL: {e}")
        return False
    except Exception as e:
        print(f"[{timestamp()}] ❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    try:
        exito = ejecutar_etl()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] ⚠️  Interrumpido por usuario")
        sys.exit(2)

if __name__ == "__main__":
    main()
