#!/usr/bin/env python3
"""
Generador de datos de prueba para la base de datos gestionproyectos_hist
Crea datos realistas para todas las tablas del sistema
"""

import mysql.connector
import random
from faker import Faker
from datetime import datetime, date, timedelta
import sys

# Configuración
fake = Faker('es_MX')
CANTIDAD_CLIENTES = 8
CANTIDAD_EMPLEADOS = 15
CANTIDAD_EQUIPOS = 5
CANTIDAD_PROYECTOS = 12
CANTIDAD_TAREAS_POR_PROYECTO = 8

def conectar_bd():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='gestionproyectos_hist',
            autocommit=True
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error conectando: {err}")
        return None

def limpiar_tablas(cursor):
    """Limpiar todas las tablas manteniendo los estados"""
    print("🧹 Limpiando tablas existentes...")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tablas = ['TareaEquipoHist', 'MiembroEquipo', 'Tarea', 'Proyecto', 'Equipo', 'Empleado', 'Cliente']
    for tabla in tablas:
        cursor.execute(f"DELETE FROM {tabla}")
        cursor.execute(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1")
        print(f"  ✅ {tabla} limpiada")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def generar_clientes(cursor):
    """Generar clientes de prueba"""
    print(f"👥 Generando {CANTIDAD_CLIENTES} clientes...")
    
    sectores = ['Tecnología', 'Construcción', 'Salud', 'Educación', 'Financiero', 'Retail', 'Manufactura', 'Gobierno']
    
    for i in range(CANTIDAD_CLIENTES):
        nombre = fake.company()
        sector = random.choice(sectores)
        contacto = fake.name()
        telefono = fake.phone_number()[:20]
        email = fake.company_email()
        direccion = fake.address()[:200]
        
        cursor.execute("""
            INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, sector, contacto, telefono, email, direccion))
    
    print(f"  ✅ {CANTIDAD_CLIENTES} clientes creados")

def generar_empleados(cursor):
    """Generar empleados de prueba"""
    print(f"👨‍💼 Generando {CANTIDAD_EMPLEADOS} empleados...")
    
    puestos = ['Gerente de Proyecto', 'Desarrollador Senior', 'Desarrollador Junior', 'Analista', 'QA Tester', 
              'Diseñador UX/UI', 'Arquitecto de Software', 'DevOps Engineer', 'Scrum Master', 'Product Owner']
    
    departamentos = ['Desarrollo', 'QA', 'Diseño', 'Gestión', 'DevOps', 'Análisis']
    
    for i in range(CANTIDAD_EMPLEADOS):
        nombre = fake.name()
        puesto = random.choice(puestos)
        departamento = random.choice(departamentos)
        salario_base = random.randint(25000, 80000)
        fecha_ingreso = fake.date_between(start_date='-3y', end_date='today')
        
        cursor.execute("""
            INSERT INTO Empleado (nombre, puesto, departamento, salario_base, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, puesto, departamento, salario_base, fecha_ingreso))
    
    print(f"  ✅ {CANTIDAD_EMPLEADOS} empleados creados")

def generar_equipos(cursor):
    """Generar equipos de trabajo"""
    print(f"👥 Generando {CANTIDAD_EQUIPOS} equipos...")
    
    nombres_equipos = ['Equipo Alpha', 'Equipo Beta', 'Equipo Gamma', 'Equipo Delta', 'Equipo Epsilon', 
                      'Team Innovación', 'Team Desarrollo', 'Team QA', 'Team DevOps', 'Team Frontend']
    
    for i in range(CANTIDAD_EQUIPOS):
        nombre_equipo = nombres_equipos[i] if i < len(nombres_equipos) else f"Equipo {i+1}"
        descripcion = fake.catch_phrase()
        
        cursor.execute("""
            INSERT INTO Equipo (nombre_equipo, descripcion)
            VALUES (%s, %s)
        """, (nombre_equipo, descripcion))
    
    print(f"  ✅ {CANTIDAD_EQUIPOS} equipos creados")

def generar_proyectos(cursor):
    """Generar proyectos de prueba"""
    print(f"📊 Generando {CANTIDAD_PROYECTOS} proyectos...")
    
    # Obtener IDs existentes
    cursor.execute("SELECT id_cliente FROM Cliente")
    clientes = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_empleado FROM Empleado WHERE puesto LIKE '%Gerente%' OR puesto LIKE '%Manager%'")
    gerentes = [row[0] for row in cursor.fetchall()]
    if not gerentes:
        cursor.execute("SELECT id_empleado FROM Empleado LIMIT 5")
        gerentes = [row[0] for row in cursor.fetchall()]
    
    estados = [1, 2, 3, 4]  # Pendiente, En Progreso, Completado, Cancelado
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    for i in range(CANTIDAD_PROYECTOS):
        nombre = f"Proyecto {fake.catch_phrase()}"[:150]
        descripcion = fake.text(max_nb_chars=300)
        
        # Fechas realistas
        fecha_inicio = fake.date_between(start_date='-1y', end_date='+30d')
        duracion_plan = random.randint(30, 180)
        fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan)
        
        # Algunas tienen fecha real de finalización
        estado = random.choice(estados)
        fecha_fin_real = None
        if estado in [3, 4]:  # Completado o Cancelado
            variacion = random.randint(-15, 30)
            fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
        
        presupuesto = random.randint(50000, 500000)
        costo_real = presupuesto + random.randint(-20000, 50000) if fecha_fin_real else 0
        
        id_cliente = random.choice(clientes)
        id_empleado_gerente = random.choice(gerentes)
        prioridad = random.choice(prioridades)
        progreso = random.randint(10, 100) if estado == 2 else (100 if estado == 3 else random.randint(0, 30))
        
        cursor.execute("""
            INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
                                presupuesto, costo_real, id_cliente, id_estado, id_empleado_gerente,
                                prioridad, progreso_porcentaje)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
              presupuesto, costo_real, id_cliente, estado, id_empleado_gerente,
              prioridad, progreso))
    
    print(f"  ✅ {CANTIDAD_PROYECTOS} proyectos creados")

def generar_tareas(cursor):
    """Generar tareas para cada proyecto"""
    print("📋 Generando tareas...")
    
    # Obtener proyectos
    cursor.execute("SELECT id_proyecto FROM Proyecto")
    proyectos = [row[0] for row in cursor.fetchall()]
    
    # Obtener empleados
    cursor.execute("SELECT id_empleado FROM Empleado")
    empleados = [row[0] for row in cursor.fetchall()]
    
    estados = [1, 2, 3, 4]
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    nombres_tareas = [
        'Análisis de Requerimientos', 'Diseño de Base de Datos', 'Desarrollo Frontend',
        'Desarrollo Backend', 'Pruebas Unitarias', 'Pruebas de Integración',
        'Documentación', 'Deployment', 'Configuración de Servidor', 'Training de Usuario',
        'Code Review', 'Optimización de Performance', 'Implementación de Seguridad',
        'Testing de Carga', 'Migración de Datos', 'Setup de Monitoreo'
    ]
    
    total_tareas = 0
    for id_proyecto in proyectos:
        cantidad_tareas = random.randint(5, CANTIDAD_TAREAS_POR_PROYECTO)
        
        for i in range(cantidad_tareas):
            nombre_tarea = f"{random.choice(nombres_tareas)} - P{id_proyecto}"[:150]
            descripcion = fake.text(max_nb_chars=200)
            
            # Fechas de la tarea
            fecha_inicio_plan = fake.date_between(start_date='-6m', end_date='+1m')
            duracion = random.randint(3, 21)
            fecha_fin_plan = fecha_inicio_plan + timedelta(days=duracion)
            
            # Algunas tienen fechas reales
            estado = random.choice(estados)
            fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 5)) if estado in [2, 3, 4] else None
            fecha_fin_real = None
            if estado in [3, 4]:
                variacion = random.randint(-3, 7)
                fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
            
            horas_plan = random.randint(8, 80)
            horas_reales = horas_plan + random.randint(-10, 20) if estado in [3, 4] else 0
            
            id_empleado = random.choice(empleados)
            prioridad = random.choice(prioridades)
            progreso = random.randint(80, 100) if estado == 3 else (random.randint(10, 90) if estado == 2 else 0)
            
            costo_estimado = horas_plan * random.randint(500, 1500)
            costo_real = horas_reales * random.randint(500, 1500) if horas_reales > 0 else 0
            
            cursor.execute("""
                INSERT INTO Tarea (nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan,
                                 fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                                 id_proyecto, id_empleado, id_estado, prioridad, progreso_porcentaje,
                                 costo_estimado, costo_real)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan,
                  fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                  id_proyecto, id_empleado, estado, prioridad, progreso,
                  costo_estimado, costo_real))
            
            total_tareas += 1
    
    print(f"  ✅ {total_tareas} tareas creadas")

def generar_miembros_equipo(cursor):
    """Generar asignaciones de miembros a equipos"""
    print("👥 Generando miembros de equipo...")
    
    cursor.execute("SELECT id_equipo FROM Equipo")
    equipos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_empleado FROM Empleado")
    empleados = [row[0] for row in cursor.fetchall()]
    
    roles = ['Team Lead', 'Developer', 'Analyst', 'Tester', 'Designer', 'Support']
    
    total_miembros = 0
    for id_equipo in equipos:
        # Cada equipo tiene entre 3-6 miembros
        miembros_equipo = random.sample(empleados, random.randint(3, min(6, len(empleados))))
        
        for id_empleado in miembros_equipo:
            fecha_inicio = fake.date_between(start_date='-2y', end_date='today')
            fecha_fin = None
            if random.random() < 0.2:  # 20% han salido del equipo
                fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 365))
            
            rol_miembro = random.choice(roles)
            activo = 1 if fecha_fin is None else 0
            
            cursor.execute("""
                INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro, activo))
            
            total_miembros += 1
    
    print(f"  ✅ {total_miembros} asignaciones de miembros creadas")

def generar_historial_tareas_equipos(cursor):
    """Generar historial de asignaciones tarea-equipo"""
    print("📋 Generando historial de tareas-equipos...")
    
    cursor.execute("SELECT id_tarea FROM Tarea")
    tareas = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_equipo FROM Equipo")
    equipos = [row[0] for row in cursor.fetchall()]
    
    total_asignaciones = 0
    for id_tarea in tareas:
        # No todas las tareas tienen equipos asignados
        if random.random() < 0.7:  # 70% de las tareas tienen equipo
            id_equipo = random.choice(equipos)
            fecha_asignacion = fake.date_between(start_date='-1y', end_date='today')
            fecha_liberacion = None
            
            if random.random() < 0.6:  # 60% ya terminaron
                fecha_liberacion = fecha_asignacion + timedelta(days=random.randint(7, 60))
            
            horas_asignadas = random.randint(10, 100)
            notas = fake.sentence() if random.random() < 0.3 else None
            
            cursor.execute("""
                INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion, 
                                           horas_asignadas, notas)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion, horas_asignadas, notas))
            
            total_asignaciones += 1
    
    print(f"  ✅ {total_asignaciones} asignaciones tarea-equipo creadas")

def mostrar_resumen(cursor):
    """Mostrar resumen de datos generados"""
    print("\n📊 RESUMEN DE DATOS GENERADOS:")
    
    tablas = ['Cliente', 'Empleado', 'Equipo', 'Proyecto', 'Tarea', 'MiembroEquipo', 'TareaEquipoHist']
    
    for tabla in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        print(f"  📦 {tabla}: {count} registros")

def main():
    """Función principal"""
    print("🚀 Generador de Datos de Prueba - Sistema de Gestión de Proyectos")
    print("=" * 60)
    
    conn = conectar_bd()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        sys.exit(1)
    
    cursor = conn.cursor()
    
    try:
        # Generar todos los datos
        limpiar_tablas(cursor)
        generar_clientes(cursor)
        generar_empleados(cursor)
        generar_equipos(cursor)
        generar_proyectos(cursor)
        generar_tareas(cursor)
        generar_miembros_equipo(cursor)
        generar_historial_tareas_equipos(cursor)
        
        # Mostrar resumen
        mostrar_resumen(cursor)
        
        print(f"\n🎉 ¡Datos de prueba generados exitosamente!")
        print(f"💡 La base de datos 'gestionproyectos_hist' está lista para el ETL")
        
    except Exception as e:
        print(f"❌ Error generando datos: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
