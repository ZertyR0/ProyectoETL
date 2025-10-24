#!/usr/bin/env python3
"""
Generador de Datos SEGURO usando Stored Procedures
Sistema de Gestión de Proyectos
- NO hace SELECT directos
- Solo llama a procedimientos almacenados
- Previene filtración de datos
"""

import mysql.connector
import random
from faker import Faker
from datetime import datetime, date, timedelta
import sys

# Configuración
fake = Faker('es_MX')
Faker.seed(42)

CANTIDAD_CLIENTES = 8
CANTIDAD_EMPLEADOS = 15
CANTIDAD_EQUIPOS = 5
CANTIDAD_PROYECTOS = 12
CANTIDAD_TAREAS_POR_PROYECTO = 8

class GeneradorSeguro:
    """Clase para generar datos usando solo stored procedures"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.ids_clientes = []
        self.ids_empleados = []
        self.ids_equipos = []
        self.ids_proyectos = []
        
    def conectar_bd(self):
        """Conectar a la base de datos"""
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',  # En producción usar 'etl_user'
                password='',
                database='gestionproyectos_hist',
                autocommit=False
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Conectado a BD: gestionproyectos_hist")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error conectando: {err}")
            return False
    
    def cerrar_conexion(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def ejecutar_procedimiento(self, nombre_proc, parametros=None):
        """Ejecutar un procedimiento almacenado de forma segura"""
        try:
            if parametros:
                self.cursor.callproc(nombre_proc, parametros)
            else:
                self.cursor.callproc(nombre_proc)
            
            # Obtener resultados
            resultados = []
            for result in self.cursor.stored_results():
                resultados.extend(result.fetchall())
            
            self.conn.commit()
            return True, resultados
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"❌ Error en {nombre_proc}: {err}")
            return False, []
    
    def limpiar_tablas(self):
        """Limpiar tablas usando procedimiento"""
        print("🧹 Limpiando tablas existentes...")
        
        exito, resultado = self.ejecutar_procedimiento('sp_limpiar_datos')
        
        if exito:
            print("  ✅ Tablas limpiadas")
            # Limpiar caches locales
            self.ids_clientes.clear()
            self.ids_empleados.clear()
            self.ids_equipos.clear()
            self.ids_proyectos.clear()
        
        return exito
    
    def generar_clientes(self):
        """Generar clientes usando procedimiento"""
        print(f"👥 Generando {CANTIDAD_CLIENTES} clientes...")
        
        sectores = ['Tecnología', 'Construcción', 'Salud', 'Educación', 
                   'Financiero', 'Retail', 'Manufactura', 'Gobierno']
        
        clientes_creados = 0
        
        for i in range(CANTIDAD_CLIENTES):
            nombre = fake.company()
            sector = random.choice(sectores)
            contacto = fake.name()
            telefono = fake.phone_number()[:20]
            email = f"{nombre.lower().replace(' ', '')[:20]}@{fake.free_email_domain()}"
            direccion = fake.address()[:200]
            
            # Llamar procedimiento almacenado
            exito, resultado = self.ejecutar_procedimiento('sp_generar_cliente', [
                nombre, sector, contacto, telefono, email, direccion
            ])
            
            if exito and resultado:
                id_generado = resultado[0]['id_generado']
                self.ids_clientes.append(id_generado)
                clientes_creados += 1
        
        print(f"  ✅ {clientes_creados} clientes creados")
        return clientes_creados == CANTIDAD_CLIENTES
    
    def generar_empleados(self):
        """Generar empleados usando procedimiento"""
        print(f"👨‍💼 Generando {CANTIDAD_EMPLEADOS} empleados...")
        
        puestos = [
            'Gerente de Proyecto', 'Desarrollador Senior', 'Desarrollador Junior',
            'Analista', 'QA Tester', 'Diseñador UX/UI', 'Arquitecto de Software',
            'DevOps Engineer', 'Scrum Master', 'Product Owner', 'Business Analyst',
            'Data Engineer', 'Frontend Developer', 'Backend Developer'
        ]
        
        departamentos = ['Desarrollo', 'QA', 'Diseño', 'Gestión', 'DevOps', 'Análisis']
        
        empleados_creados = 0
        
        for i in range(CANTIDAD_EMPLEADOS):
            nombre = fake.name()
            puesto = random.choice(puestos)
            departamento = random.choice(departamentos)
            
            if 'Gerente' in puesto or 'Arquitecto' in puesto or 'Senior' in puesto:
                salario_base = random.randint(60000, 100000)
            elif 'Junior' in puesto:
                salario_base = random.randint(25000, 40000)
            else:
                salario_base = random.randint(40000, 70000)
            
            fecha_ingreso = fake.date_between(start_date='-3y', end_date='-6m')
            
            # Llamar procedimiento
            exito, resultado = self.ejecutar_procedimiento('sp_generar_empleado', [
                nombre, puesto, departamento, salario_base, fecha_ingreso
            ])
            
            if exito and resultado:
                id_generado = resultado[0]['id_generado']
                self.ids_empleados.append(id_generado)
                empleados_creados += 1
        
        print(f"  ✅ {empleados_creados} empleados creados")
        return empleados_creados == CANTIDAD_EMPLEADOS
    
    def generar_equipos(self):
        """Generar equipos usando procedimiento"""
        print(f"👥 Generando {CANTIDAD_EQUIPOS} equipos...")
        
        nombres_equipos = [
            'Equipo Alpha', 'Equipo Beta', 'Equipo Gamma', 'Equipo Delta', 
            'Equipo Epsilon', 'Team Innovación', 'Team Desarrollo'
        ]
        
        equipos_creados = 0
        
        for i in range(CANTIDAD_EQUIPOS):
            nombre_equipo = nombres_equipos[i] if i < len(nombres_equipos) else f"Equipo {i+1}"
            descripcion = fake.catch_phrase()
            
            # Llamar procedimiento
            exito, resultado = self.ejecutar_procedimiento('sp_generar_equipo', [
                nombre_equipo, descripcion
            ])
            
            if exito and resultado:
                id_generado = resultado[0]['id_generado']
                self.ids_equipos.append(id_generado)
                equipos_creados += 1
        
        print(f"  ✅ {equipos_creados} equipos creados")
        return equipos_creados == CANTIDAD_EQUIPOS
    
    def generar_proyectos(self):
        """Generar proyectos usando procedimiento"""
        print(f"📊 Generando {CANTIDAD_PROYECTOS} proyectos...")
        
        estados = [1, 2, 3, 4]
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        tipos_proyecto = [
            'Sistema Web', 'Aplicación Móvil', 'Plataforma E-commerce',
            'Sistema CRM', 'Portal Corporativo', 'API REST'
        ]
        
        proyectos_creados = 0
        
        for i in range(CANTIDAD_PROYECTOS):
            tipo = random.choice(tipos_proyecto)
            nombre = f"{tipo} {i+1}"
            descripcion = fake.text(max_nb_chars=300)
            
            fecha_inicio = fake.date_between(start_date='-1y', end_date='+30d')
            duracion_plan = random.randint(30, 180)
            fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan)
            
            estado = random.choice(estados)
            fecha_fin_real = None
            if estado in [3, 4]:
                variacion = random.randint(-15, 30)
                fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
            
            presupuesto = random.randint(50000, 500000)
            costo_real = presupuesto + random.randint(-20000, 50000) if fecha_fin_real else 0
            
            id_cliente = random.choice(self.ids_clientes) if self.ids_clientes else None
            id_empleado_gerente = random.choice(self.ids_empleados) if self.ids_empleados else None
            prioridad = random.choice(prioridades)
            progreso = random.randint(10, 100) if estado == 2 else (100 if estado == 3 else random.randint(0, 30))
            
            # Llamar procedimiento
            exito, resultado = self.ejecutar_procedimiento('sp_generar_proyecto', [
                nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
                presupuesto, costo_real, id_cliente, estado, id_empleado_gerente,
                prioridad, progreso
            ])
            
            if exito and resultado:
                id_generado = resultado[0]['id_generado']
                self.ids_proyectos.append(id_generado)
                proyectos_creados += 1
        
        print(f"  ✅ {proyectos_creados} proyectos creados")
        return proyectos_creados > 0
    
    def generar_tareas(self):
        """Generar tareas usando procedimiento"""
        print("📋 Generando tareas...")
        
        estados = [1, 2, 3, 4]
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        nombres_tareas = [
            'Análisis de Requerimientos', 'Diseño de Base de Datos', 'Desarrollo Frontend',
            'Desarrollo Backend', 'Pruebas Unitarias', 'Pruebas de Integración',
            'Documentación', 'Deployment'
        ]
        
        total_tareas = 0
        
        for id_proyecto in self.ids_proyectos:
            cantidad_tareas = random.randint(5, CANTIDAD_TAREAS_POR_PROYECTO)
            
            for i in range(cantidad_tareas):
                nombre_tarea = f"{random.choice(nombres_tareas)} - P{id_proyecto}"
                descripcion = fake.text(max_nb_chars=200)
                
                fecha_inicio_plan = fake.date_between(start_date='-6m', end_date='+1m')
                duracion = random.randint(3, 21)
                fecha_fin_plan = fecha_inicio_plan + timedelta(days=duracion)
                
                estado = random.choice(estados)
                fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 5)) if estado in [2, 3, 4] else None
                fecha_fin_real = None
                if estado in [3, 4]:
                    variacion = random.randint(-3, 7)
                    fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
                
                horas_plan = random.randint(8, 80)
                horas_reales = horas_plan + random.randint(-10, 20) if estado in [3, 4] else 0
                
                id_empleado = random.choice(self.ids_empleados) if self.ids_empleados else None
                prioridad = random.choice(prioridades)
                progreso = random.randint(80, 100) if estado == 3 else (random.randint(10, 90) if estado == 2 else 0)
                
                costo_estimado = horas_plan * random.randint(500, 1500)
                costo_real = horas_reales * random.randint(500, 1500) if horas_reales > 0 else 0
                
                # Llamar procedimiento
                exito, resultado = self.ejecutar_procedimiento('sp_generar_tarea', [
                    nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan,
                    fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                    id_proyecto, id_empleado, estado, prioridad, progreso,
                    costo_estimado, costo_real
                ])
                
                if exito:
                    total_tareas += 1
        
        print(f"  ✅ {total_tareas} tareas creadas")
        return total_tareas > 0
    
    def generar_miembros_equipo(self):
        """Generar miembros de equipo usando procedimiento"""
        print("👥 Generando miembros de equipo...")
        
        roles = ['Team Lead', 'Developer', 'Analyst', 'Tester', 'Designer', 'Support']
        total_miembros = 0
        
        for id_equipo in self.ids_equipos:
            cantidad_miembros = random.randint(3, min(6, len(self.ids_empleados)))
            miembros_equipo = random.sample(self.ids_empleados, cantidad_miembros)
            
            for id_empleado in miembros_equipo:
                fecha_inicio = fake.date_between(start_date='-2y', end_date='today')
                fecha_fin = None
                if random.random() < 0.2:
                    fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 365))
                
                rol_miembro = random.choice(roles)
                activo = 1 if fecha_fin is None else 0
                
                # Llamar procedimiento
                exito, resultado = self.ejecutar_procedimiento('sp_generar_miembro_equipo', [
                    id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro, activo
                ])
                
                if exito:
                    total_miembros += 1
        
        print(f"  ✅ {total_miembros} asignaciones creadas")
        return total_miembros > 0
    
    def obtener_ids_tareas(self):
        """Obtener IDs de tareas mediante procedimiento seguro"""
        exito, resultado = self.ejecutar_procedimiento('sp_obtener_ids_disponibles')
        
        if exito:
            return [item['id'] for item in resultado if item['tipo'] == 'PROYECTOS']
        return []
    
    def generar_historial_tareas_equipos(self):
        """Generar historial de tareas-equipos usando procedimiento"""
        print("📋 Generando historial de tareas-equipos...")
        
        # Obtener IDs disponibles
        ids_tareas = self.obtener_ids_tareas()
        total_asignaciones = 0
        
        for i in range(min(50, len(ids_tareas))):  # Limitar a 50 asignaciones
            if not self.ids_equipos:
                break
            
            id_tarea = i + 1  # Asumimos IDs secuenciales
            id_equipo = random.choice(self.ids_equipos)
            
            fecha_asignacion = fake.date_between(start_date='-1y', end_date='today')
            fecha_liberacion = None
            if random.random() < 0.6:
                fecha_liberacion = fecha_asignacion + timedelta(days=random.randint(7, 60))
            
            horas_asignadas = random.randint(10, 100)
            notas = fake.sentence() if random.random() < 0.3 else None
            
            # Llamar procedimiento
            exito, resultado = self.ejecutar_procedimiento('sp_generar_tarea_equipo', [
                id_tarea, id_equipo, fecha_asignacion, fecha_liberacion, horas_asignadas, notas
            ])
            
            if exito:
                total_asignaciones += 1
        
        print(f"  ✅ {total_asignaciones} asignaciones tarea-equipo creadas")
        return True
    
    def validar_integridad(self):
        """Validar integridad usando procedimiento"""
        print("\n🔍 Validando integridad de datos...")
        
        exito, resultado = self.ejecutar_procedimiento('sp_validar_integridad')
        
        if exito:
            for row in resultado:
                icono = "✅" if row['estado'] == 'OK' else "❌"
                print(f"  {icono} {row['validacion']}: {row['unicos']}/{row['total']}")
            return all(row['estado'] == 'OK' for row in resultado)
        
        return False
    
    def mostrar_resumen(self):
        """Mostrar resumen usando procedimiento"""
        print("\n📊 RESUMEN DE DATOS GENERADOS:")
        
        exito, resultado = self.ejecutar_procedimiento('sp_obtener_resumen')
        
        if exito:
            for row in resultado:
                print(f"  📦 {row['tabla']}: {row['total']} registros")
        
        # Estadísticas adicionales
        print("\n📈 ESTADÍSTICAS:")
        exito, stats = self.ejecutar_procedimiento('sp_estadisticas_proyectos')
        
        if exito:
            print("  Proyectos por estado:")
            for row in stats:
                print(f"    • {row['nombre_estado']}: {row['cantidad_proyectos']} ({row['progreso_promedio']}% promedio)")
    
    def ejecutar(self):
        """Ejecutar proceso completo de generación"""
        print("🚀 Generador de Datos SEGURO - Usando Stored Procedures")
        print("   ✓ Sin SELECT directos")
        print("   ✓ Prevención de filtración de datos")
        print("   ✓ Validación mediante triggers")
        print("=" * 70)
        
        if not self.conectar_bd():
            return False
        
        try:
            # Limpiar
            if not self.limpiar_tablas():
                return False
            
            # Generar datos
            if not self.generar_clientes():
                return False
            
            if not self.generar_empleados():
                return False
            
            if not self.generar_equipos():
                return False
            
            if not self.generar_proyectos():
                return False
            
            if not self.generar_tareas():
                return False
            
            if not self.generar_miembros_equipo():
                return False
            
            if not self.generar_historial_tareas_equipos():
                return False
            
            # Validar
            if self.validar_integridad():
                print("\n✅ Todos los datos pasaron las validaciones de integridad")
            else:
                print("\n⚠️  Algunas validaciones fallaron")
            
            # Mostrar resumen
            self.mostrar_resumen()
            
            print(f"\n🎉 ¡Datos de prueba generados exitosamente!")
            print(f"💡 Todos los datos fueron creados mediante stored procedures")
            print(f"🔒 Sin acceso directo a tablas sensibles")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.cerrar_conexion()

def main():
    """Función principal"""
    generador = GeneradorSeguro()
    exito = generador.ejecutar()
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
