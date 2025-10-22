#!/usr/bin/env python3
"""
Script de configuración automática para el Sistema ETL Distribuido
Configura todo el proyecto de manera automática o por pasos
"""

import os
import sys
import subprocess
import mysql.connector
import argparse
from pathlib import Path
from datetime import datetime

class SetupProyectoETL:
    """Clase para configurar automáticamente el proyecto ETL"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.errores = []
        self.warnings = []
        
    def log(self, mensaje, tipo='info'):
        """Log con formato"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        emojis = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌', 'proceso': '🔄'}
        emoji = emojis.get(tipo, 'ℹ️')
        print(f"[{timestamp}] {emoji} {mensaje}")
        
        if tipo == 'error':
            self.errores.append(mensaje)
        elif tipo == 'warning':
            self.warnings.append(mensaje)
    
    def verificar_mysql(self):
        """Verificar que MySQL esté disponible"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password=''
            )
            conn.close()
            self.log("MySQL está disponible y funcionando", 'success')
            return True
        except Exception as e:
            self.log(f"Error conectando a MySQL: {e}", 'error')
            self.log("Asegúrate de que MySQL esté instalado y ejecutándose", 'warning')
            return False
    
    def instalar_dependencias(self):
        """Instalar dependencias Python"""
        self.log("Instalando dependencias Python...", 'proceso')
        
        try:
            # Verificar si existe venv
            venv_path = self.base_dir / 'venv'
            if not venv_path.exists():
                self.log("Creando entorno virtual...", 'proceso')
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
            
            # Activar venv y instalar dependencias
            if os.name == 'nt':  # Windows
                pip_path = venv_path / 'Scripts' / 'pip'
                python_path = venv_path / 'Scripts' / 'python'
            else:  # Unix/Linux/macOS
                pip_path = venv_path / 'bin' / 'pip'
                python_path = venv_path / 'bin' / 'python'
            
            # Instalar dependencias principales
            subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], check=True)
            
            # Instalar dependencias del dashboard
            dashboard_req = self.base_dir / '03_Dashboard' / 'backend' / 'requirements.txt'
            if dashboard_req.exists():
                subprocess.run([str(pip_path), 'install', '-r', str(dashboard_req)], check=True)
            
            self.log("Dependencias instaladas correctamente", 'success')
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error instalando dependencias: {e}", 'error')
            return False
        except Exception as e:
            self.log(f"Error inesperado instalando dependencias: {e}", 'error')
            return False
    
    def crear_bases_datos(self):
        """Crear las bases de datos"""
        self.log("Creando bases de datos...", 'proceso')
        
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                autocommit=True
            )
            cursor = conn.cursor()
            
            # Crear BD origen
            script_origen = self.base_dir / '01_GestionProyectos' / 'scripts' / 'crear_bd_origen.sql'
            if script_origen.exists():
                self.log("Creando base de datos origen...", 'proceso')
                self.ejecutar_script_sql(cursor, script_origen)
                self.log("Base de datos origen creada", 'success')
            
            # Crear datawarehouse
            script_dw = self.base_dir / '04_Datawarehouse' / 'scripts' / 'crear_datawarehouse.sql'
            if script_dw.exists():
                self.log("Creando datawarehouse...", 'proceso')
                self.ejecutar_script_sql(cursor, script_dw)
                self.log("Datawarehouse creado", 'success')
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log(f"Error creando bases de datos: {e}", 'error')
            return False
    
    def ejecutar_script_sql(self, cursor, script_path):
        """Ejecutar un script SQL"""
        with open(script_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
        
        # Dividir en comandos individuales
        comandos = [cmd.strip() for cmd in script_content.split(';') if cmd.strip()]
        
        for comando in comandos:
            if comando.upper().startswith(('SELECT', 'SHOW')):
                # Solo ejecutar, no mostrar resultados para setup
                try:
                    cursor.execute(comando)
                    cursor.fetchall()  # Consumir resultados
                except:
                    pass
            else:
                try:
                    cursor.execute(comando)
                except mysql.connector.Error as e:
                    # Ignorar algunos errores comunes
                    if e.errno not in [1007, 1050, 1051]:  # DB exists, table exists, unknown table
                        self.log(f"Warning SQL: {e}", 'warning')
    
    def generar_datos_prueba(self):
        """Generar datos de prueba"""
        self.log("Generando datos de prueba...", 'proceso')
        
        try:
            script_datos = self.base_dir / '01_GestionProyectos' / 'scripts' / 'generar_datos.py'
            
            if script_datos.exists():
                # Usar Python del venv si existe
                venv_path = self.base_dir / 'venv'
                if venv_path.exists():
                    if os.name == 'nt':
                        python_path = venv_path / 'Scripts' / 'python'
                    else:
                        python_path = venv_path / 'bin' / 'python'
                else:
                    python_path = sys.executable
                
                result = subprocess.run([str(python_path), str(script_datos)], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log("Datos de prueba generados", 'success')
                    return True
                else:
                    self.log(f"Error generando datos: {result.stderr}", 'error')
                    return False
            else:
                self.log("Script de generación de datos no encontrado", 'warning')
                return False
                
        except Exception as e:
            self.log(f"Error ejecutando generación de datos: {e}", 'error')
            return False
    
    def ejecutar_etl(self):
        """Ejecutar proceso ETL"""
        self.log("Ejecutando proceso ETL...", 'proceso')
        
        try:
            script_etl = self.base_dir / '02_ETL' / 'scripts' / 'etl_principal.py'
            
            if script_etl.exists():
                # Usar Python del venv si existe
                venv_path = self.base_dir / 'venv'
                if venv_path.exists():
                    if os.name == 'nt':
                        python_path = venv_path / 'Scripts' / 'python'
                    else:
                        python_path = venv_path / 'bin' / 'python'
                else:
                    python_path = sys.executable
                
                # Cambiar al directorio del ETL
                original_cwd = os.getcwd()
                os.chdir(self.base_dir / '02_ETL' / 'scripts')
                
                result = subprocess.run([str(python_path), 'etl_principal.py', 'local'], 
                                      capture_output=True, text=True)
                
                # Volver al directorio original
                os.chdir(original_cwd)
                
                if result.returncode == 0:
                    self.log("Proceso ETL ejecutado exitosamente", 'success')
                    return True
                else:
                    self.log(f"Error en ETL: {result.stderr}", 'error')
                    return False
            else:
                self.log("Script ETL no encontrado", 'warning')
                return False
                
        except Exception as e:
            self.log(f"Error ejecutando ETL: {e}", 'error')
            return False
    
    def verificar_configuracion(self):
        """Verificar que la configuración esté completa"""
        self.log("Verificando configuración...", 'proceso')
        
        verificaciones = []
        
        # Verificar bases de datos
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='gestionproyectos_hist'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Cliente")
            clientes = cursor.fetchone()[0]
            verificaciones.append(f"BD Origen: {clientes} clientes")
            cursor.close()
            conn.close()
        except:
            verificaciones.append("BD Origen: ERROR")
        
        try:
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='dw_proyectos_hist'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM HechoProyecto")
            hechos = cursor.fetchone()[0]
            verificaciones.append(f"Datawarehouse: {hechos} hechos")
            cursor.close()
            conn.close()
        except:
            verificaciones.append("Datawarehouse: ERROR")
        
        # Verificar archivos
        archivos_clave = [
            '01_GestionProyectos/scripts/crear_bd_origen.sql',
            '02_ETL/scripts/etl_principal.py',
            '03_Dashboard/backend/app.py',
            '04_Datawarehouse/scripts/crear_datawarehouse.sql'
        ]
        
        for archivo in archivos_clave:
            path = self.base_dir / archivo
            if path.exists():
                verificaciones.append(f"✅ {archivo}")
            else:
                verificaciones.append(f"❌ {archivo}")
        
        self.log("Estado de verificación:", 'info')
        for check in verificaciones:
            print(f"  {check}")
    
    def mostrar_resumen(self):
        """Mostrar resumen final"""
        print("\n" + "="*60)
        self.log("RESUMEN DE CONFIGURACIÓN", 'info')
        print("="*60)
        
        if self.errores:
            self.log(f"❌ Errores encontrados ({len(self.errores)}):", 'error')
            for error in self.errores[-5:]:
                print(f"  - {error}")
        
        if self.warnings:
            self.log(f"⚠️ Warnings ({len(self.warnings)}):", 'warning')
            for warning in self.warnings[-3:]:
                print(f"  - {warning}")
        
        if not self.errores:
            self.log("🎉 ¡Configuración completada exitosamente!", 'success')
            print("\n📋 Próximos pasos:")
            print("  1. Abrir dashboard: python 03_Dashboard/backend/app.py")
            print("  2. Abrir navegador: http://localhost:5001")
            print("  3. Verificar datos y ejecutar ETL desde la interfaz")
        else:
            self.log("⚠️ Configuración completada con errores", 'warning')
            print("\n🔧 Revisar errores y ejecutar manualmente los pasos fallidos")
    
    def setup_completo(self):
        """Ejecutar setup completo"""
        self.log("🚀 Iniciando configuración completa del Sistema ETL", 'info')
        
        # Verificar prerequisitos
        if not self.verificar_mysql():
            return False
        
        # Pasos del setup
        pasos = [
            ("Instalar dependencias", self.instalar_dependencias),
            ("Crear bases de datos", self.crear_bases_datos),
            ("Generar datos de prueba", self.generar_datos_prueba),
            ("Ejecutar ETL inicial", self.ejecutar_etl)
        ]
        
        for descripcion, funcion in pasos:
            self.log(f"Ejecutando: {descripcion}", 'proceso')
            if not funcion():
                self.log(f"Falló: {descripcion}", 'error')
            print()  # Línea en blanco
        
        # Verificación final
        self.verificar_configuracion()
        self.mostrar_resumen()
        
        return len(self.errores) == 0

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Configurar Sistema ETL Distribuido')
    parser.add_argument('--solo-dependencias', action='store_true', 
                       help='Solo instalar dependencias')
    parser.add_argument('--solo-bases-datos', action='store_true', 
                       help='Solo crear bases de datos')
    parser.add_argument('--solo-datos', action='store_true', 
                       help='Solo generar datos de prueba')
    parser.add_argument('--solo-etl', action='store_true', 
                       help='Solo ejecutar ETL')
    parser.add_argument('--verificar', action='store_true', 
                       help='Solo verificar configuración')
    
    args = parser.parse_args()
    
    setup = SetupProyectoETL()
    
    # Si no se especifica ninguna opción, hacer setup completo
    if not any(vars(args).values()):
        setup.setup_completo()
    else:
        # Ejecutar solo los pasos solicitados
        if args.solo_dependencias:
            setup.instalar_dependencias()
        
        if args.solo_bases_datos:
            if setup.verificar_mysql():
                setup.crear_bases_datos()
        
        if args.solo_datos:
            setup.generar_datos_prueba()
        
        if args.solo_etl:
            setup.ejecutar_etl()
        
        if args.verificar:
            setup.verificar_configuracion()
        
        setup.mostrar_resumen()

if __name__ == "__main__":
    main()
