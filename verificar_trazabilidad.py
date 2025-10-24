#!/usr/bin/env python3
"""
Verificador de Trazabilidad y Búsqueda entre Bases de Datos
Sistema ETL - Gestión de Proyectos
"""

import mysql.connector
import sys
import pandas as pd
from datetime import datetime
from tabulate import tabulate

class VerificadorTrazabilidad:
    """Clase para verificar trazabilidad entre BD origen y destino"""
    
    def __init__(self):
        self.conn_origen = None
        self.conn_destino = None
        
    def conectar_bases(self):
        """Conectar a ambas bases de datos"""
        try:
            # Conexión a BD Origen
            self.conn_origen = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='gestionproyectos_hist'
            )
            print("✅ Conectado a BD Origen (gestionproyectos_hist)")
            
            # Conexión a BD Destino (DataWarehouse)
            self.conn_destino = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='dw_proyectos_hist'
            )
            print("✅ Conectado a BD Destino (dw_proyectos_hist)")
            
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error conectando: {err}")
            return False
    
    def cerrar_conexiones(self):
        """Cerrar conexiones a las bases de datos"""
        if self.conn_origen:
            self.conn_origen.close()
        if self.conn_destino:
            self.conn_destino.close()
    
    def verificar_conteos(self):
        """Verificar conteo de registros entre BD origen y destino"""
        print("\n" + "="*70)
        print("📊 VERIFICACIÓN DE CONTEOS")
        print("="*70)
        
        cursor_origen = self.conn_origen.cursor()
        cursor_destino = self.conn_destino.cursor()
        
        resultados = []
        
        # Verificar Clientes
        cursor_origen.execute("SELECT COUNT(*) FROM Cliente WHERE activo = 1")
        origen_clientes = cursor_origen.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM DimCliente")
        destino_clientes = cursor_destino.fetchone()[0]
        
        resultados.append([
            "Clientes", 
            origen_clientes, 
            destino_clientes, 
            "✅" if origen_clientes == destino_clientes else "❌"
        ])
        
        # Verificar Empleados
        cursor_origen.execute("SELECT COUNT(*) FROM Empleado WHERE activo = 1")
        origen_empleados = cursor_origen.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM DimEmpleado")
        destino_empleados = cursor_destino.fetchone()[0]
        
        resultados.append([
            "Empleados", 
            origen_empleados, 
            destino_empleados, 
            "✅" if origen_empleados == destino_empleados else "❌"
        ])
        
        # Verificar Equipos
        cursor_origen.execute("SELECT COUNT(*) FROM Equipo WHERE activo = 1")
        origen_equipos = cursor_origen.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM DimEquipo")
        destino_equipos = cursor_destino.fetchone()[0]
        
        resultados.append([
            "Equipos", 
            origen_equipos, 
            destino_equipos, 
            "✅" if origen_equipos == destino_equipos else "❌"
        ])
        
        # Verificar Proyectos (solo completados/cancelados)
        cursor_origen.execute("SELECT COUNT(*) FROM Proyecto WHERE id_estado IN (3, 4)")
        origen_proyectos = cursor_origen.fetchone()[0]
        
        cursor_destino.execute("SELECT COUNT(*) FROM DimProyecto")
        destino_proyectos = cursor_destino.fetchone()[0]
        
        resultados.append([
            "Proyectos (Completados/Cancelados)", 
            origen_proyectos, 
            destino_proyectos, 
            "✅" if origen_proyectos == destino_proyectos else "❌"
        ])
        
        # Verificar HechoProyecto
        cursor_destino.execute("SELECT COUNT(*) FROM HechoProyecto")
        destino_hechos_proy = cursor_destino.fetchone()[0]
        
        resultados.append([
            "HechoProyecto", 
            origen_proyectos, 
            destino_hechos_proy, 
            "✅" if origen_proyectos == destino_hechos_proy else "❌"
        ])
        
        # Mostrar resultados
        print(tabulate(resultados, headers=["Entidad", "BD Origen", "BD Destino", "Estado"], tablefmt="grid"))
        
        cursor_origen.close()
        cursor_destino.close()
    
    def buscar_proyecto_por_id(self, id_proyecto):
        """Buscar un proyecto por ID en ambas bases de datos"""
        print(f"\n🔍 Buscando Proyecto ID: {id_proyecto}")
        print("="*70)
        
        cursor_origen = self.conn_origen.cursor(dictionary=True)
        cursor_destino = self.conn_destino.cursor(dictionary=True)
        
        # Buscar en origen
        cursor_origen.execute("""
            SELECT p.*, c.nombre as cliente, e.nombre as gerente, est.nombre_estado
            FROM Proyecto p
            LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
            LEFT JOIN Empleado e ON p.id_empleado_gerente = e.id_empleado
            LEFT JOIN Estado est ON p.id_estado = est.id_estado
            WHERE p.id_proyecto = %s
        """, (id_proyecto,))
        
        proyecto_origen = cursor_origen.fetchone()
        
        if proyecto_origen:
            print("\n📦 BD ORIGEN (gestionproyectos_hist):")
            print("-" * 70)
            for key, value in proyecto_origen.items():
                print(f"  {key:30s}: {value}")
        else:
            print("❌ No encontrado en BD Origen")
            return
        
        # Buscar en destino
        cursor_destino.execute("""
            SELECT dp.*, hp.*
            FROM DimProyecto dp
            LEFT JOIN HechoProyecto hp ON dp.id_proyecto = hp.id_proyecto
            WHERE dp.id_proyecto = %s
        """, (id_proyecto,))
        
        proyecto_destino = cursor_destino.fetchone()
        
        if proyecto_destino:
            print("\n📦 BD DESTINO (dw_proyectos_hist):")
            print("-" * 70)
            for key, value in proyecto_destino.items():
                print(f"  {key:30s}: {value}")
            print("\n✅ Proyecto encontrado en ambas bases de datos")
        else:
            print("\n❌ No encontrado en BD Destino")
            print("⚠️  El proyecto podría no estar completado o cancelado")
        
        cursor_origen.close()
        cursor_destino.close()
    
    def buscar_cliente_por_nombre(self, nombre_cliente):
        """Buscar un cliente por nombre en ambas bases de datos"""
        print(f"\n🔍 Buscando Cliente: '{nombre_cliente}'")
        print("="*70)
        
        cursor_origen = self.conn_origen.cursor(dictionary=True)
        cursor_destino = self.conn_destino.cursor(dictionary=True)
        
        # Buscar en origen
        cursor_origen.execute("""
            SELECT * FROM Cliente 
            WHERE nombre LIKE %s
        """, (f"%{nombre_cliente}%",))
        
        clientes_origen = cursor_origen.fetchall()
        
        if clientes_origen:
            print(f"\n📦 BD ORIGEN: {len(clientes_origen)} resultado(s)")
            print("-" * 70)
            for cliente in clientes_origen:
                print(f"  ID: {cliente['id_cliente']}")
                print(f"  Nombre: {cliente['nombre']}")
                print(f"  Sector: {cliente['sector']}")
                print(f"  Email: {cliente['email']}")
                print(f"  Activo: {'Sí' if cliente['activo'] else 'No'}")
                print("-" * 70)
                
                # Buscar en destino
                cursor_destino.execute("""
                    SELECT * FROM DimCliente WHERE id_cliente = %s
                """, (cliente['id_cliente'],))
                
                cliente_destino = cursor_destino.fetchone()
                
                if cliente_destino:
                    print(f"  ✅ Encontrado en DW (id_cliente: {cliente_destino['id_cliente']})")
                else:
                    print(f"  ❌ NO encontrado en DW")
                print()
        else:
            print("❌ No se encontraron clientes con ese nombre en BD Origen")
        
        cursor_origen.close()
        cursor_destino.close()
    
    def buscar_empleado_por_nombre(self, nombre_empleado):
        """Buscar un empleado por nombre en ambas bases de datos"""
        print(f"\n🔍 Buscando Empleado: '{nombre_empleado}'")
        print("="*70)
        
        cursor_origen = self.conn_origen.cursor(dictionary=True)
        cursor_destino = self.conn_destino.cursor(dictionary=True)
        
        # Buscar en origen
        cursor_origen.execute("""
            SELECT * FROM Empleado 
            WHERE nombre LIKE %s
        """, (f"%{nombre_empleado}%",))
        
        empleados_origen = cursor_origen.fetchall()
        
        if empleados_origen:
            print(f"\n📦 BD ORIGEN: {len(empleados_origen)} resultado(s)")
            print("-" * 70)
            for empleado in empleados_origen:
                print(f"  ID: {empleado['id_empleado']}")
                print(f"  Nombre: {empleado['nombre']}")
                print(f"  Puesto: {empleado['puesto']}")
                print(f"  Departamento: {empleado['departamento']}")
                print(f"  Salario: ${empleado['salario_base']:,.2f}")
                print("-" * 70)
                
                # Buscar en destino
                cursor_destino.execute("""
                    SELECT * FROM DimEmpleado WHERE id_empleado = %s
                """, (empleado['id_empleado'],))
                
                empleado_destino = cursor_destino.fetchone()
                
                if empleado_destino:
                    print(f"  ✅ Encontrado en DW (id_empleado: {empleado_destino['id_empleado']})")
                else:
                    print(f"  ❌ NO encontrado en DW")
                print()
        else:
            print("❌ No se encontraron empleados con ese nombre en BD Origen")
        
        cursor_origen.close()
        cursor_destino.close()
    
    def verificar_duplicados_origen(self):
        """Verificar duplicados en la base de datos origen"""
        print("\n" + "="*70)
        print("🔍 VERIFICACIÓN DE DUPLICADOS EN BD ORIGEN")
        print("="*70)
        
        cursor = self.conn_origen.cursor()
        
        # Verificar clientes duplicados
        cursor.execute("""
            SELECT nombre, COUNT(*) as cantidad
            FROM Cliente
            GROUP BY nombre
            HAVING COUNT(*) > 1
        """)
        clientes_duplicados = cursor.fetchall()
        
        if clientes_duplicados:
            print("\n❌ Clientes duplicados encontrados:")
            for nombre, cantidad in clientes_duplicados:
                print(f"  • {nombre}: {cantidad} veces")
        else:
            print("\n✅ No hay clientes duplicados")
        
        # Verificar empleados duplicados
        cursor.execute("""
            SELECT nombre, COUNT(*) as cantidad
            FROM Empleado
            GROUP BY nombre
            HAVING COUNT(*) > 1
        """)
        empleados_duplicados = cursor.fetchall()
        
        if empleados_duplicados:
            print("\n❌ Empleados duplicados encontrados:")
            for nombre, cantidad in empleados_duplicados:
                print(f"  • {nombre}: {cantidad} veces")
        else:
            print("\n✅ No hay empleados duplicados")
        
        # Verificar emails duplicados
        cursor.execute("""
            SELECT email, COUNT(*) as cantidad
            FROM Cliente
            WHERE email IS NOT NULL AND email != ''
            GROUP BY email
            HAVING COUNT(*) > 1
        """)
        emails_duplicados = cursor.fetchall()
        
        if emails_duplicados:
            print("\n❌ Emails duplicados encontrados:")
            for email, cantidad in emails_duplicados:
                print(f"  • {email}: {cantidad} veces")
        else:
            print("\n✅ No hay emails duplicados")
        
        # Verificar proyectos duplicados
        cursor.execute("""
            SELECT nombre, COUNT(*) as cantidad
            FROM Proyecto
            GROUP BY nombre
            HAVING COUNT(*) > 1
        """)
        proyectos_duplicados = cursor.fetchall()
        
        if proyectos_duplicados:
            print("\n❌ Proyectos duplicados encontrados:")
            for nombre, cantidad in proyectos_duplicados:
                print(f"  • {nombre}: {cantidad} veces")
        else:
            print("\n✅ No hay proyectos duplicados")
        
        # Verificar asignaciones duplicadas en MiembroEquipo
        cursor.execute("""
            SELECT id_equipo, id_empleado, COUNT(*) as cantidad
            FROM MiembroEquipo
            GROUP BY id_equipo, id_empleado
            HAVING COUNT(*) > 1
        """)
        miembros_duplicados = cursor.fetchall()
        
        if miembros_duplicados:
            print("\n❌ Asignaciones equipo-empleado duplicadas:")
            for id_equipo, id_empleado, cantidad in miembros_duplicados:
                print(f"  • Equipo {id_equipo} - Empleado {id_empleado}: {cantidad} veces")
        else:
            print("\n✅ No hay asignaciones equipo-empleado duplicadas")
        
        cursor.close()
    
    def listar_proyectos_no_migrados(self):
        """Listar proyectos que están en origen pero no en destino"""
        print("\n" + "="*70)
        print("📋 PROYECTOS NO MIGRADOS AL DATAWAREHOUSE")
        print("="*70)
        
        cursor_origen = self.conn_origen.cursor(dictionary=True)
        cursor_destino = self.conn_destino.cursor()
        
        # Obtener todos los proyectos de origen
        cursor_origen.execute("""
            SELECT p.id_proyecto, p.nombre, est.nombre_estado, p.progreso_porcentaje
            FROM Proyecto p
            LEFT JOIN Estado est ON p.id_estado = est.id_estado
        """)
        proyectos_origen = cursor_origen.fetchall()
        
        # Obtener IDs de proyectos en destino
        cursor_destino.execute("SELECT id_proyecto FROM DimProyecto")
        ids_destino = {row[0] for row in cursor_destino.fetchall()}
        
        no_migrados = []
        for proyecto in proyectos_origen:
            if proyecto['id_proyecto'] not in ids_destino:
                no_migrados.append([
                    proyecto['id_proyecto'],
                    proyecto['nombre'][:50],
                    proyecto['nombre_estado'],
                    f"{proyecto['progreso_porcentaje']}%"
                ])
        
        if no_migrados:
            print(f"\n⚠️  {len(no_migrados)} proyecto(s) NO migrado(s):")
            print(tabulate(no_migrados, headers=["ID", "Nombre", "Estado", "Progreso"], tablefmt="grid"))
            print("\n💡 Nota: Solo se migran proyectos Completados o Cancelados")
        else:
            print("\n✅ Todos los proyectos elegibles han sido migrados")
        
        cursor_origen.close()
        cursor_destino.close()
    
    def generar_reporte_completo(self):
        """Generar un reporte completo de trazabilidad"""
        print("\n" + "="*70)
        print("📊 REPORTE COMPLETO DE TRAZABILIDAD")
        print("="*70)
        
        self.verificar_conteos()
        self.verificar_duplicados_origen()
        self.listar_proyectos_no_migrados()
        
        print("\n" + "="*70)
        print("✅ Reporte completo generado")
        print("="*70)

def menu_principal():
    """Menú principal de la aplicación"""
    verificador = VerificadorTrazabilidad()
    
    if not verificador.conectar_bases():
        print("❌ No se pudo conectar a las bases de datos")
        return
    
    while True:
        print("\n" + "="*70)
        print("🔍 VERIFICADOR DE TRAZABILIDAD - Sistema ETL")
        print("="*70)
        print("1. Verificar conteos generales")
        print("2. Buscar proyecto por ID")
        print("3. Buscar cliente por nombre")
        print("4. Buscar empleado por nombre")
        print("5. Verificar duplicados en BD Origen")
        print("6. Listar proyectos no migrados")
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
            nombre = input("Ingrese nombre del cliente (o parte): ").strip()
            if nombre:
                verificador.buscar_cliente_por_nombre(nombre)
            else:
                print("❌ Debe ingresar un nombre")
        
        elif opcion == "4":
            nombre = input("Ingrese nombre del empleado (o parte): ").strip()
            if nombre:
                verificador.buscar_empleado_por_nombre(nombre)
            else:
                print("❌ Debe ingresar un nombre")
        
        elif opcion == "5":
            verificador.verificar_duplicados_origen()
        
        elif opcion == "6":
            verificador.listar_proyectos_no_migrados()
        
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
        
        verificador = VerificadorTrazabilidad()
        if not verificador.conectar_bases():
            sys.exit(1)
        
        if comando == "reporte":
            verificador.generar_reporte_completo()
        elif comando == "conteos":
            verificador.verificar_conteos()
        elif comando == "duplicados":
            verificador.verificar_duplicados_origen()
        elif comando == "no-migrados":
            verificador.listar_proyectos_no_migrados()
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("Comandos disponibles: reporte, conteos, duplicados, no-migrados")
        
        verificador.cerrar_conexiones()
    else:
        menu_principal()

if __name__ == "__main__":
    main()
