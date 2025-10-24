#!/usr/bin/env python3
"""
Verificador de Trazabilidad SEGURO usando Stored Procedures
- NO hace SELECT directos
- Solo llama a procedimientos almacenados
- Previene filtración de datos sensibles
"""

import mysql.connector
import sys
from tabulate import tabulate

class VerificadorSeguro:
    """Clase para verificar trazabilidad usando solo stored procedures"""
    
    def __init__(self):
        self.conn_origen = None
        self.conn_destino = None
    
    def conectar_bases(self):
        """Conectar a ambas bases de datos"""
        try:
            # Conexión a BD Origen (usar usuario limitado en producción)
            self.conn_origen = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',  # En producción: 'etl_user'
                password='',
                database='gestionproyectos_hist'
            )
            print("✅ Conectado a BD Origen (gestionproyectos_hist)")
            
            # Conexión a BD Destino (usar usuario readonly en producción)
            self.conn_destino = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',  # En producción: 'dw_readonly'
                password='',
                database='dw_proyectos_hist'
            )
            print("✅ Conectado a BD Destino (dw_proyectos_hist)")
            
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error conectando: {err}")
            return False
    
    def cerrar_conexiones(self):
        """Cerrar conexiones"""
        if self.conn_origen:
            self.conn_origen.close()
        if self.conn_destino:
            self.conn_destino.close()
    
    def llamar_procedimiento(self, conexion, nombre_proc, parametros=None):
        """Llamar procedimiento almacenado de forma segura"""
        try:
            cursor = conexion.cursor(dictionary=True)
            
            if parametros:
                cursor.callproc(nombre_proc, parametros)
            else:
                cursor.callproc(nombre_proc)
            
            # Obtener resultados
            resultados = []
            for result in cursor.stored_results():
                resultados.extend(result.fetchall())
            
            cursor.close()
            return resultados
            
        except mysql.connector.Error as err:
            print(f"❌ Error en {nombre_proc}: {err}")
            return []
    
    def verificar_conteos(self):
        """Verificar conteos usando procedimientos"""
        print("\n" + "="*70)
        print("📊 VERIFICACIÓN DE CONTEOS")
        print("="*70)
        
        # Obtener conteos de origen (solo números, sin datos)
        conteos_origen = self.llamar_procedimiento(
            self.conn_origen, 
            'sp_obtener_resumen'
        )
        
        # Obtener conteos de destino
        conteos_destino = self.llamar_procedimiento(
            self.conn_destino,
            'sp_dw_obtener_conteos'
        )
        
        # Preparar tabla comparativa
        resultados = []
        
        # Mapear tablas origen a destino
        mapeo = {
            'Cliente': 'DimCliente',
            'Empleado': 'DimEmpleado',
            'Equipo': 'DimEquipo',
            'Proyecto': 'DimProyecto'
        }
        
        for tabla_origen, tabla_destino in mapeo.items():
            origen_row = next((r for r in conteos_origen if r['tabla'] == tabla_origen), None)
            destino_row = next((r for r in conteos_destino if r['tabla'] == tabla_destino), None)
            
            if origen_row and destino_row:
                total_origen = origen_row['total']
                total_destino = destino_row['total']
                estado = "✅" if total_origen == total_destino else "❌"
                
                resultados.append([
                    tabla_origen,
                    total_origen,
                    total_destino,
                    estado
                ])
        
        # Hechos de proyecto
        hechos = next((r for r in conteos_destino if r['tabla'] == 'HechoProyecto'), None)
        if hechos:
            resultados.append([
                'HechoProyecto',
                '-',
                hechos['total'],
                '📊'
            ])
        
        print(tabulate(resultados, 
                      headers=["Entidad", "BD Origen", "BD Destino", "Estado"], 
                      tablefmt="grid"))
    
    def buscar_proyecto_por_id(self, id_proyecto):
        """Buscar proyecto usando procedimientos"""
        print(f"\n🔍 Buscando Proyecto ID: {id_proyecto}")
        print("="*70)
        
        # Buscar en DW usando procedimiento
        resultado_dw = self.llamar_procedimiento(
            self.conn_destino,
            'sp_dw_buscar_proyecto',
            [id_proyecto]
        )
        
        if resultado_dw:
            print("\n📦 BD DESTINO (dw_proyectos_hist) - Dimensión:")
            print("-" * 70)
            
            # Primera consulta: DimProyecto
            proyecto = resultado_dw[0] if len(resultado_dw) > 0 else None
            if proyecto:
                for key, value in proyecto.items():
                    print(f"  {key:30s}: {value}")
            
            # Segunda consulta: HechoProyecto (si hay más resultados)
            print("\n📦 BD DESTINO - Métricas (HechoProyecto):")
            print("-" * 70)
            
            # Hacer segunda llamada para obtener hechos
            cursor = self.conn_destino.cursor(dictionary=True)
            cursor.callproc('sp_dw_buscar_proyecto', [id_proyecto])
            
            # Saltar primer result set (DimProyecto)
            results = list(cursor.stored_results())
            if len(results) > 1:
                hechos = results[1].fetchall()
                if hechos:
                    for key, value in hechos[0].items():
                        print(f"  {key:30s}: {value}")
            
            cursor.close()
            
            print("\n✅ Proyecto encontrado en DataWarehouse")
        else:
            print("\n❌ No encontrado en BD Destino")
            print("⚠️  El proyecto podría no estar completado o cancelado")
    
    def buscar_cliente_por_id(self, id_cliente):
        """Buscar cliente usando procedimientos"""
        print(f"\n🔍 Buscando Cliente ID: {id_cliente}")
        print("="*70)
        
        # Buscar usando procedimiento
        cursor = self.conn_destino.cursor(dictionary=True)
        cursor.callproc('sp_dw_buscar_cliente', [id_cliente])
        
        # Primer result: Info del cliente
        results = list(cursor.stored_results())
        
        if len(results) > 0:
            cliente_info = results[0].fetchall()
            
            if cliente_info:
                print("\n📦 Cliente encontrado en DW:")
                print("-" * 70)
                for key, value in cliente_info[0].items():
                    print(f"  {key:30s}: {value}")
                
                # Segundo result: Métricas de proyectos
                if len(results) > 1:
                    metricas = results[1].fetchall()
                    if metricas:
                        print("\n📊 Métricas de Proyectos del Cliente:")
                        print("-" * 70)
                        for key, value in metricas[0].items():
                            print(f"  {key:30s}: {value}")
                
                print("\n✅ Cliente encontrado")
            else:
                print("\n❌ Cliente no encontrado en DW")
        
        cursor.close()
    
    def verificar_duplicados_origen(self):
        """Verificar duplicados usando procedimiento"""
        print("\n" + "="*70)
        print("🔍 VERIFICACIÓN DE DUPLICADOS EN BD ORIGEN")
        print("="*70)
        
        # Llamar procedimiento de verificación
        duplicados = self.llamar_procedimiento(
            self.conn_origen,
            'sp_verificar_duplicados'
        )
        
        if duplicados:
            print("\n❌ Duplicados encontrados:")
            for dup in duplicados:
                print(f"  • {dup['tipo']}: {dup['valor']} ({dup['cantidad']} veces)")
        else:
            print("\n✅ No se encontraron duplicados")
    
    def validar_integridad_origen(self):
        """Validar integridad en origen usando procedimiento"""
        print("\n" + "="*70)
        print("🔍 VALIDACIÓN DE INTEGRIDAD EN BD ORIGEN")
        print("="*70)
        
        # Llamar procedimiento
        validaciones = self.llamar_procedimiento(
            self.conn_origen,
            'sp_validar_integridad'
        )
        
        if validaciones:
            for val in validaciones:
                icono = "✅" if val['estado'] == 'OK' else "❌"
                print(f"  {icono} {val['validacion']}: {val['unicos']}/{val['total']}")
        else:
            print("⚠️  No se pudo obtener validaciones")
    
    def obtener_metricas_dw(self):
        """Obtener métricas del DW usando procedimiento"""
        print("\n" + "="*70)
        print("📊 MÉTRICAS DEL DATAWAREHOUSE")
        print("="*70)
        
        # Llamar procedimiento
        metricas = self.llamar_procedimiento(
            self.conn_destino,
            'sp_dw_obtener_metricas'
        )
        
        if metricas:
            for metrica in metricas:
                print(f"\n📈 {metrica['categoria']}:")
                print("-" * 70)
                for key, value in metrica.items():
                    if key != 'categoria':
                        print(f"  {key:30s}: {value}")
    
    def generar_reporte_completo(self):
        """Generar reporte completo usando procedimientos"""
        print("\n" + "="*70)
        print("📊 REPORTE COMPLETO DE TRAZABILIDAD SEGURA")
        print("="*70)
        
        self.verificar_conteos()
        self.validar_integridad_origen()
        self.verificar_duplicados_origen()
        self.obtener_metricas_dw()
        
        print("\n" + "="*70)
        print("✅ Reporte completo generado usando solo procedimientos almacenados")
        print("🔒 Sin acceso directo a datos sensibles")
        print("="*70)

def menu_principal():
    """Menú principal"""
    verificador = VerificadorSeguro()
    
    if not verificador.conectar_bases():
        print("❌ No se pudo conectar a las bases de datos")
        return
    
    while True:
        print("\n" + "="*70)
        print("🔒 VERIFICADOR SEGURO DE TRAZABILIDAD")
        print("   ✓ Solo procedimientos almacenados")
        print("   ✓ Sin SELECT directos")
        print("="*70)
        print("1. Verificar conteos generales")
        print("2. Buscar proyecto por ID (en DW)")
        print("3. Buscar cliente por ID (en DW)")
        print("4. Verificar duplicados en origen")
        print("5. Validar integridad en origen")
        print("6. Obtener métricas del DW")
        print("7. Generar reporte completo")
        print("0. Salir")
        print("="*70)
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            verificador.verificar_conteos()
        
        elif opcion == "2":
            id_proyecto = input("Ingrese ID del proyecto: ").strip()
            if id_proyecto.isdigit():
                verificador.buscar_proyecto_por_id(int(id_proyecto))
            else:
                print("❌ ID inválido")
        
        elif opcion == "3":
            id_cliente = input("Ingrese ID del cliente: ").strip()
            if id_cliente.isdigit():
                verificador.buscar_cliente_por_id(int(id_cliente))
            else:
                print("❌ ID inválido")
        
        elif opcion == "4":
            verificador.verificar_duplicados_origen()
        
        elif opcion == "5":
            verificador.validar_integridad_origen()
        
        elif opcion == "6":
            verificador.obtener_metricas_dw()
        
        elif opcion == "7":
            verificador.generar_reporte_completo()
        
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")
    
    verificador.cerrar_conexiones()

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        verificador = VerificadorSeguro()
        if not verificador.conectar_bases():
            sys.exit(1)
        
        if comando == "reporte":
            verificador.generar_reporte_completo()
        elif comando == "conteos":
            verificador.verificar_conteos()
        elif comando == "duplicados":
            verificador.verificar_duplicados_origen()
        elif comando == "integridad":
            verificador.validar_integridad_origen()
        elif comando == "metricas":
            verificador.obtener_metricas_dw()
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("Comandos disponibles: reporte, conteos, duplicados, integridad, metricas")
        
        verificador.cerrar_conexiones()
    else:
        menu_principal()

if __name__ == "__main__":
    main()
