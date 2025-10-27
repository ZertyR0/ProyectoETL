#!/usr/bin/env python3
"""
ETL Principal - Sistema de Gestión de Proyectos (OPCIÓN 2 - Máxima Seguridad)
TODO el proceso ETL está en procedimientos almacenados de MySQL
Python solo orquesta y monitorea
"""

import sys
import os
from pathlib import Path

# Agregar el directorio config al path
sys.path.append(str(Path(__file__).parent.parent / 'config'))

import mysql.connector
from datetime import datetime

# Importar configuraciones
from config_conexion import get_config

class ETLProyectos:
    """Clase principal para el proceso ETL - Orquestador de SPs"""
    
    def __init__(self, ambiente='local'):
        self.ambiente = ambiente
        self.config = get_config(ambiente)
        self.conn_destino = None
        
        print(f"[{self._timestamp()}] ℹ️  ETL inicializado - Ambiente: {ambiente}")
    
    def _timestamp(self):
        """Obtener timestamp formateado"""
        return datetime.now().strftime('%H:%M:%S')
    
    def _log(self, mensaje, nivel='INFO'):
        """Logging simple"""
        simbolo = {
            'INFO': 'ℹ️ ',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️ ',
            'PROCESO': '🔄'
        }.get(nivel, 'ℹ️ ')
        
        print(f"[{self._timestamp()}] {simbolo} {mensaje}")
    
    def conectar_datawarehouse(self):
        """Conectar solo al datawarehouse (donde están los SPs)"""
        try:
            self._log("Conectando al DataWarehouse...", 'PROCESO')
            
            conn_params = {
                'host': self.config['host_destino'],
                'port': self.config['port_destino'],
                'user': self.config['user_destino'],
                'password': self.config['password_destino'],
                'database': self.config['database_destino']
            }
            
            self.conn_destino = mysql.connector.connect(**conn_params)
            self._log("Conexión establecida exitosamente", 'SUCCESS')
            return True
            
        except Exception as e:
            self._log(f"Error conectando: {e}", 'ERROR')
            return False
    
    def ejecutar_etl_completo(self):
        """
        Ejecutar el proceso ETL completo
        TODO el procesamiento está en el stored procedure sp_etl_proceso_completo()
        """
        try:
            self._log("Iniciando proceso ETL completo", 'INFO')
            print("=" * 70)
            
            # Conectar al DW
            if not self.conectar_datawarehouse():
                return False
            
            # Ejecutar el SP que hace TODO el ETL
            self._log("Ejecutando procedimiento almacenado: sp_etl_proceso_completo()", 'PROCESO')
            self._log("Este SP realiza:", 'INFO')
            self._log("  1. Limpieza del DataWarehouse", 'INFO')
            self._log("  2. Extracción desde BD origen", 'INFO')
            self._log("  3. Transformación de datos (métricas)", 'INFO')
            self._log("  4. Carga de dimensiones", 'INFO')
            self._log("  5. Carga de hechos", 'INFO')
            print()
            
            cursor = self.conn_destino.cursor(dictionary=True)
            
            # Llamar al SP maestro
            inicio = datetime.now()
            cursor.execute("CALL sp_etl_proceso_completo()")
            resultado = cursor.fetchone()
            fin = datetime.now()
            
            cursor.nextset()  # Limpiar resultsets
            cursor.close()
            self.conn_destino.close()
            
            # Mostrar resultado
            duracion = (fin - inicio).total_seconds()
            
            if resultado and resultado.get('resultado') == 'EXITOSO':
                print()
                print("=" * 70)
                self._log("PROCESO ETL COMPLETADO EXITOSAMENTE", 'SUCCESS')
                print("=" * 70)
                print(f"  Mensaje: {resultado.get('mensaje', 'N/A')}")
                print(f"  Duración: {duracion:.2f} segundos")
                print(f"  Fecha: {resultado.get('fecha_hora', 'N/A')}")
                print()
                self._log("✨ TODAS las operaciones se ejecutaron en MySQL", 'SUCCESS')
                self._log("✨ Python solo orquestó el proceso", 'SUCCESS')
                self._log("✨ CERO exposición de estructura de BD en código Python", 'SUCCESS')
                print("=" * 70)
                return True
            else:
                self._log("El procedimiento no retornó resultado exitoso", 'ERROR')
                return False
                
        except Exception as e:
            self._log(f"Error en proceso ETL: {e}", 'ERROR')
            import traceback
            print(traceback.format_exc())
            return False
    
    def obtener_estadisticas(self):
        """Obtener estadísticas del DataWarehouse"""
        try:
            if not self.conn_destino or not self.conn_destino.is_connected():
                if not self.conectar_datawarehouse():
                    return None
            
            cursor = self.conn_destino.cursor(dictionary=True)
            
            stats = {}
            tablas = ['DimCliente', 'DimEmpleado', 'DimEquipo', 'DimProyecto', 
                     'DimTiempo', 'HechoProyecto', 'HechoTarea']
            
            for tabla in tablas:
                cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
                resultado = cursor.fetchone()
                stats[tabla] = resultado['total'] if resultado else 0
            
            cursor.close()
            return stats
            
        except Exception as e:
            self._log(f"Error obteniendo estadísticas: {e}", 'ERROR')
            return None

def main():
    """Función principal"""
    # Determinar ambiente
    ambiente = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ETL - MÁXIMA SEGURIDAD (OPCIÓN 2)" + " " * 20 + "║")
    print("║" + " " * 10 + "TODO el procesamiento en MySQL via SPs" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Crear y ejecutar ETL
    etl = ETLProyectos(ambiente)
    
    try:
        exito = etl.ejecutar_etl_completo()
        
        if exito:
            # Mostrar estadísticas
            print()
            print("📊 Estadísticas del DataWarehouse:")
            print("-" * 70)
            stats = etl.obtener_estadisticas()
            if stats:
                for tabla, count in stats.items():
                    print(f"  {tabla:20} → {count:10,} registros")
            print("-" * 70)
        
        exit_code = 0 if exito else 1
        
    except KeyboardInterrupt:
        print()
        print("[{0}] ⚠️  Proceso ETL interrumpido por el usuario".format(
            datetime.now().strftime('%H:%M:%S')
        ))
        exit_code = 2
        
    except Exception as e:
        print()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error inesperado: {e}")
        exit_code = 3
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
