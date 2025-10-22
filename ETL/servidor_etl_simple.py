#!/usr/bin/env python3
"""
Servidor HTTP simple para ejecutar ETL de forma remota
Solo permite ejecutar el proceso ETL, no acceso completo al servidor
"""

import http.server
import socketserver
import subprocess
import json
import sys
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configuración
PORT = 8081
ETL_SCRIPT_PATH = "/Users/andrescruzortiz/etlfolder/ETL_simplificado.py"

class ETLHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Manejar solicitudes GET"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_info()
        elif path == '/status':
            self.send_status()
        elif path == '/ejecutar-etl':
            self.send_response(405)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "error": "Método no permitido",
                "mensaje": "Usa POST para ejecutar el ETL"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_404()
    
    def do_POST(self):
        """Manejar solicitudes POST"""
        path = urlparse(self.path).path
        
        if path == '/ejecutar-etl':
            self.ejecutar_etl()
        else:
            self.send_404()
    
    def send_info(self):
        """Enviar información de la API"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        info = {
            "nombre": "Servidor ETL Remoto",
            "version": "1.0",
            "descripcion": "Servidor HTTP para ejecutar ETL de forma remota",
            "endpoints": {
                "GET /": "Información del servidor",
                "GET /status": "Estado del servidor",
                "POST /ejecutar-etl": "Ejecutar proceso ETL"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(info, indent=2).encode())
    
    def send_status(self):
        """Enviar estado del servidor"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "etl_disponible": os.path.exists(ETL_SCRIPT_PATH),
            "etl_path": ETL_SCRIPT_PATH
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def ejecutar_etl(self):
        """Ejecutar el proceso ETL"""
        try:
            print(f"🚀 [{datetime.now()}] Iniciando ejecución de ETL")
            
            # Usar el Python del entorno virtual
            python_cmd = "/Users/andrescruzortiz/etlfolder/.venv/bin/python"
            
            # Ejecutar el script ETL
            result = subprocess.run([
                python_cmd, ETL_SCRIPT_PATH
            ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
            
            if result.returncode == 0:
                self.send_response(200)
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "mensaje": "ETL ejecutado exitosamente",
                    "output": result.stdout,
                    "exitcode": result.returncode
                }
                print(f"✅ [{datetime.now()}] ETL ejecutado exitosamente")
            else:
                self.send_response(500)
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "mensaje": "Error en la ejecución del ETL",
                    "error": result.stderr,
                    "output": result.stdout,
                    "exitcode": result.returncode
                }
                print(f"❌ [{datetime.now()}] Error en ETL: {result.stderr}")
            
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except subprocess.TimeoutExpired:
            self.send_response(408)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "mensaje": "Error: ETL demoró más de 5 minutos",
                "error": "Timeout"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            print(f"⏰ [{datetime.now()}] ETL timeout")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "mensaje": "Error inesperado en el servidor",
                "error": str(e)
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            print(f"💥 [{datetime.now()}] Error inesperado: {str(e)}")
    
    def send_404(self):
        """Enviar error 404"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "error": "Endpoint no encontrado",
            "mensaje": "Endpoints disponibles: GET /, GET /status, POST /ejecutar-etl"
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Personalizar logging"""
        print(f"🌐 [{datetime.now()}] {format % args}")

if __name__ == "__main__":
    print("🚀 Iniciando Servidor ETL Remoto...")
    print(f"📍 Script ETL: {ETL_SCRIPT_PATH}")
    print(f"🌐 URL: http://172.26.163.200:{PORT}")
    print("📋 Endpoints disponibles:")
    print(f"   GET  http://172.26.163.200:{PORT}/ - Información del servidor")
    print(f"   GET  http://172.26.163.200:{PORT}/status - Estado del servidor")
    print(f"   POST http://172.26.163.200:{PORT}/ejecutar-etl - Ejecutar ETL")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), ETLHandler) as httpd:
            print(f"✅ Servidor iniciado en puerto {PORT}")
            print("🔄 Esperando solicitudes... (Ctrl+C para detener)")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar servidor: {e}")
