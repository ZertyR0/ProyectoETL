#!/usr/bin/env python3
"""
Generador de datos de prueba MEJORADO con trazabilidad y validación de duplicados
Sistema de Gestión de Proyectos - Base de Datos Origen
"""

import mysql.connector
import random
from faker import Faker
from datetime import datetime, date, timedelta
import sys
import hashlib
import json

# Configuración
fake = Faker('es_MX')
Faker.seed(42)  # Semilla para reproducibilidad

# Cantidades configurables
CANTIDAD_CLIENTES = 8
CANTIDAD_EMPLEADOS = 15
CANTIDAD_EQUIPOS = 5
CANTIDAD_PROYECTOS = 12
CANTIDAD_TAREAS_POR_PROYECTO = 8

# Sets para control de duplicados
clientes_generados = set()
empleados_generados = set()
equipos_generados = set()
proyectos_generados = set()
tareas_generadas = set()
asignaciones_equipo = set()

def generar_hash_registro(tipo, *valores):
    """Generar hash único para un registro basado en sus valores clave"""
    data = f"{tipo}|{'|'.join(map(str, valores))}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

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
    
    # Limpiar sets de control
    clientes_generados.clear()
    empleados_generados.clear()
    equipos_generados.clear()
    proyectos_generados.clear()
    tareas_generadas.clear()
    asignaciones_equipo.clear()

def generar_nombre_unico_cliente():
    """Generar un nombre único de cliente"""
    max_intentos = 50
    for _ in range(max_intentos):
        nombre = fake.company()
        if nombre not in clientes_generados:
            clientes_generados.add(nombre)
            return nombre
    # Si no se encuentra único, agregar sufijo
    nombre = f"{fake.company()} {random.randint(100, 999)}"
    clientes_generados.add(nombre)
    return nombre

def generar_nombre_unico_empleado():
    """Generar un nombre único de empleado"""
    max_intentos = 50
    for _ in range(max_intentos):
        nombre = fake.name()
        if nombre not in empleados_generados:
            empleados_generados.add(nombre)
            return nombre
    # Si no se encuentra único, agregar ID
    nombre = f"{fake.name()} ({random.randint(1000, 9999)})"
    empleados_generados.add(nombre)
    return nombre

def generar_nombre_unico_equipo(base_nombres, idx):
    """Generar un nombre único de equipo"""
    if idx < len(base_nombres):
        nombre = base_nombres[idx]
    else:
        nombre = f"Equipo {idx + 1}"
    
    if nombre not in equipos_generados:
        equipos_generados.add(nombre)
        return nombre
    
    # Agregar sufijo si está duplicado
    contador = 1
    while f"{nombre} ({contador})" in equipos_generados:
        contador += 1
    
    nombre_final = f"{nombre} ({contador})"
    equipos_generados.add(nombre_final)
    return nombre_final

def generar_clientes(cursor):
    """Generar clientes de prueba únicos con trazabilidad"""
    print(f"👥 Generando {CANTIDAD_CLIENTES} clientes...")
    
    sectores = ['Tecnología', 'Construcción', 'Salud', 'Educación', 'Financiero', 'Retail', 'Manufactura', 'Gobierno']
    emails_usados = set()
    
    for i in range(CANTIDAD_CLIENTES):
        nombre = generar_nombre_unico_cliente()
        sector = random.choice(sectores)
        contacto = fake.name()
        telefono = fake.phone_number()[:20]
        
        # Generar email único
        email_base = nombre.lower().replace(' ', '').replace(',', '')[:20]
        email = f"{email_base}@{fake.free_email_domain()}"
        
        # Asegurar unicidad del email
        contador = 1
        while email in emails_usados:
            email = f"{email_base}{contador}@{fake.free_email_domain()}"
            contador += 1
        emails_usados.add(email)
        
        direccion = fake.address()[:200]
        
        cursor.execute("""
            INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, sector, contacto, telefono, email, direccion))
    
    print(f"  ✅ {CANTIDAD_CLIENTES} clientes únicos creados")

def generar_empleados(cursor):
    """Generar empleados de prueba únicos con trazabilidad"""
    print(f"👨‍💼 Generando {CANTIDAD_EMPLEADOS} empleados...")
    
    puestos = [
        'Gerente de Proyecto', 'Desarrollador Senior', 'Desarrollador Junior', 
        'Analista', 'QA Tester', 'Diseñador UX/UI', 'Arquitecto de Software', 
        'DevOps Engineer', 'Scrum Master', 'Product Owner', 'Business Analyst',
        'Data Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer'
    ]
    
    departamentos = ['Desarrollo', 'QA', 'Diseño', 'Gestión', 'DevOps', 'Análisis', 'Infraestructura']
    
    for i in range(CANTIDAD_EMPLEADOS):
        nombre = generar_nombre_unico_empleado()
        puesto = random.choice(puestos)
        departamento = random.choice(departamentos)
        
        # Salario basado en el puesto
        if 'Gerente' in puesto or 'Arquitecto' in puesto or 'Senior' in puesto:
            salario_base = random.randint(60000, 100000)
        elif 'Junior' in puesto:
            salario_base = random.randint(25000, 40000)
        else:
            salario_base = random.randint(40000, 70000)
        
        fecha_ingreso = fake.date_between(start_date='-3y', end_date='-6m')
        
        cursor.execute("""
            INSERT INTO Empleado (nombre, puesto, departamento, salario_base, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, puesto, departamento, salario_base, fecha_ingreso))
    
    print(f"  ✅ {CANTIDAD_EMPLEADOS} empleados únicos creados")

def generar_equipos(cursor):
    """Generar equipos de trabajo únicos"""
    print(f"👥 Generando {CANTIDAD_EQUIPOS} equipos...")
    
    nombres_equipos = [
        'Equipo Alpha', 'Equipo Beta', 'Equipo Gamma', 'Equipo Delta', 'Equipo Epsilon', 
        'Team Innovación', 'Team Desarrollo', 'Team QA', 'Team DevOps', 'Team Frontend',
        'Team Backend', 'Team Mobile', 'Team Cloud', 'Team Data', 'Team Security'
    ]
    
    for i in range(CANTIDAD_EQUIPOS):
        nombre_equipo = generar_nombre_unico_equipo(nombres_equipos, i)
        descripcion = fake.catch_phrase()
        
        cursor.execute("""
            INSERT INTO Equipo (nombre_equipo, descripcion)
            VALUES (%s, %s)
        """, (nombre_equipo, descripcion))
    
    print(f"  ✅ {CANTIDAD_EQUIPOS} equipos únicos creados")

def generar_proyectos(cursor):
    """Generar proyectos de prueba únicos con trazabilidad"""
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
    
    tipos_proyecto = [
        'Sistema Web', 'Aplicación Móvil', 'Plataforma E-commerce', 
        'Sistema CRM', 'Portal Corporativo', 'API REST', 'Dashboard Analytics',
        'Sistema ERP', 'Migración Cloud', 'Modernización Legacy'
    ]
    
    for i in range(CANTIDAD_PROYECTOS):
        # Generar nombre único
        tipo = random.choice(tipos_proyecto)
        empresa = random.choice(list(clientes_generados))
        nombre = f"{tipo} - {empresa}"[:150]
        
        # Asegurar unicidad del nombre del proyecto
        contador = 1
        while nombre in proyectos_generados:
            nombre = f"{tipo} - {empresa} v{contador}"[:150]
            contador += 1
        proyectos_generados.add(nombre)
        
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
    
    print(f"  ✅ {CANTIDAD_PROYECTOS} proyectos únicos creados")

def generar_tareas(cursor):
    """Generar tareas para cada proyecto - sin duplicados"""
    print("📋 Generando tareas...")
    
    # Obtener proyectos
    cursor.execute("SELECT id_proyecto, nombre FROM Proyecto")
    proyectos = cursor.fetchall()
    
    # Obtener empleados
    cursor.execute("SELECT id_empleado FROM Empleado")
    empleados = [row[0] for row in cursor.fetchall()]
    
    estados = [1, 2, 3, 4]
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    
    nombres_tareas_base = [
        'Análisis de Requerimientos', 'Diseño de Base de Datos', 'Desarrollo Frontend',
        'Desarrollo Backend', 'Pruebas Unitarias', 'Pruebas de Integración',
        'Documentación Técnica', 'Deployment', 'Configuración de Servidor', 'Training de Usuario',
        'Code Review', 'Optimización de Performance', 'Implementación de Seguridad',
        'Testing de Carga', 'Migración de Datos', 'Setup de Monitoreo',
        'Diseño UI/UX', 'Integración de APIs', 'Testing E2E', 'Refactoring'
    ]
    
    total_tareas = 0
    for id_proyecto, nombre_proyecto in proyectos:
        cantidad_tareas = random.randint(5, CANTIDAD_TAREAS_POR_PROYECTO)
        
        # Seleccionar tareas únicas para este proyecto
        tareas_proyecto = random.sample(nombres_tareas_base, min(cantidad_tareas, len(nombres_tareas_base)))
        
        for i, nombre_tarea_base in enumerate(tareas_proyecto):
            # Crear identificador único para la tarea
            nombre_tarea = f"{nombre_tarea_base} - P{id_proyecto}"[:150]
            hash_tarea = generar_hash_registro('tarea', id_proyecto, nombre_tarea_base)
            
            # Verificar que no esté duplicada
            if hash_tarea in tareas_generadas:
                continue
            tareas_generadas.add(hash_tarea)
            
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
    
    print(f"  ✅ {total_tareas} tareas únicas creadas")

def generar_miembros_equipo(cursor):
    """Generar asignaciones de miembros a equipos - sin duplicados"""
    print("👥 Generando miembros de equipo...")
    
    cursor.execute("SELECT id_equipo FROM Equipo")
    equipos = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_empleado FROM Empleado")
    empleados = [row[0] for row in cursor.fetchall()]
    
    roles = ['Team Lead', 'Developer', 'Analyst', 'Tester', 'Designer', 'Support', 'DevOps']
    
    total_miembros = 0
    for id_equipo in equipos:
        # Cada equipo tiene entre 3-6 miembros únicos
        cantidad_miembros = min(random.randint(3, 6), len(empleados))
        miembros_equipo = random.sample(empleados, cantidad_miembros)
        
        for id_empleado in miembros_equipo:
            # Verificar duplicados en asignaciones
            hash_asignacion = generar_hash_registro('miembro', id_equipo, id_empleado)
            if hash_asignacion in asignaciones_equipo:
                continue
            asignaciones_equipo.add(hash_asignacion)
            
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
    
    print(f"  ✅ {total_miembros} asignaciones únicas de miembros creadas")

def generar_historial_tareas_equipos(cursor):
    """Generar historial de asignaciones tarea-equipo - sin duplicados"""
    print("📋 Generando historial de tareas-equipos...")
    
    cursor.execute("SELECT id_tarea FROM Tarea")
    tareas = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_equipo FROM Equipo")
    equipos = [row[0] for row in cursor.fetchall()]
    
    asignaciones_historial = set()
    total_asignaciones = 0
    
    for id_tarea in tareas:
        # No todas las tareas tienen equipos asignados
        if random.random() < 0.7:  # 70% de las tareas tienen equipo
            id_equipo = random.choice(equipos)
            
            # Verificar duplicado en historial
            hash_historial = generar_hash_registro('historial', id_tarea, id_equipo)
            if hash_historial in asignaciones_historial:
                continue
            asignaciones_historial.add(hash_historial)
            
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
    
    print(f"  ✅ {total_asignaciones} asignaciones únicas tarea-equipo creadas")

def validar_integridad_datos(cursor):
    """Validar la integridad y unicidad de los datos generados"""
    print("\n🔍 Validando integridad de datos...")
    
    validaciones = []
    
    # Verificar nombres únicos de clientes
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT nombre) as unicos FROM Cliente")
    total, unicos = cursor.fetchone()
    validaciones.append(("Clientes únicos", total == unicos, f"{unicos}/{total}"))
    
    # Verificar emails únicos de clientes
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT email) as unicos FROM Cliente WHERE email IS NOT NULL")
    total, unicos = cursor.fetchone()
    validaciones.append(("Emails únicos", total == unicos, f"{unicos}/{total}"))
    
    # Verificar nombres únicos de empleados
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT nombre) as unicos FROM Empleado")
    total, unicos = cursor.fetchone()
    validaciones.append(("Empleados únicos", total == unicos, f"{unicos}/{total}"))
    
    # Verificar equipos únicos
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT nombre_equipo) as unicos FROM Equipo")
    total, unicos = cursor.fetchone()
    validaciones.append(("Equipos únicos", total == unicos, f"{unicos}/{total}"))
    
    # Verificar proyectos únicos
    cursor.execute("SELECT COUNT(*) as total, COUNT(DISTINCT nombre) as unicos FROM Proyecto")
    total, unicos = cursor.fetchone()
    validaciones.append(("Proyectos únicos", total == unicos, f"{unicos}/{total}"))
    
    # Verificar asignaciones únicas de miembros
    cursor.execute("""
        SELECT COUNT(*) as total, 
               COUNT(DISTINCT CONCAT(id_equipo, '-', id_empleado)) as unicos 
        FROM MiembroEquipo
    """)
    total, unicos = cursor.fetchone()
    validaciones.append(("Asignaciones equipo-empleado únicas", total == unicos, f"{unicos}/{total}"))
    
    # Verificar asignaciones únicas en historial
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(DISTINCT CONCAT(id_tarea, '-', id_equipo, '-', fecha_asignacion)) as unicos
        FROM TareaEquipoHist
    """)
    total, unicos = cursor.fetchone()
    validaciones.append(("Asignaciones historial únicas", total == unicos, f"{unicos}/{total}"))
    
    # Mostrar resultados
    todas_validas = True
    for nombre, valido, detalle in validaciones:
        icono = "✅" if valido else "❌"
        print(f"  {icono} {nombre}: {detalle}")
        if not valido:
            todas_validas = False
    
    return todas_validas

def mostrar_resumen(cursor):
    """Mostrar resumen de datos generados"""
    print("\n📊 RESUMEN DE DATOS GENERADOS:")
    
    tablas = [
        ('Cliente', 'id_cliente'),
        ('Empleado', 'id_empleado'),
        ('Equipo', 'id_equipo'),
        ('Proyecto', 'id_proyecto'),
        ('Tarea', 'id_tarea'),
        ('MiembroEquipo', 'id_miembro'),
        ('TareaEquipoHist', 'id_tarea_equipo')
    ]
    
    for tabla, id_col in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        print(f"  📦 {tabla}: {count} registros")
    
    # Mostrar estadísticas adicionales
    print("\n📈 ESTADÍSTICAS:")
    
    cursor.execute("""
        SELECT e.nombre_estado, COUNT(*) as cantidad
        FROM Proyecto p
        JOIN Estado e ON p.id_estado = e.id_estado
        GROUP BY e.nombre_estado
    """)
    print("  Proyectos por estado:")
    for estado, cantidad in cursor.fetchall():
        print(f"    • {estado}: {cantidad}")
    
    cursor.execute("""
        SELECT departamento, COUNT(*) as cantidad
        FROM Empleado
        GROUP BY departamento
        ORDER BY cantidad DESC
    """)
    print("\n  Empleados por departamento:")
    for dept, cantidad in cursor.fetchall():
        print(f"    • {dept}: {cantidad}")

def main():
    """Función principal"""
    print("🚀 Generador de Datos MEJORADO - Sistema de Gestión de Proyectos")
    print("   ✓ Con trazabilidad")
    print("   ✓ Sin duplicados")
    print("   ✓ Validación de integridad")
    print("=" * 70)
    
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
        
        # Validar integridad
        if validar_integridad_datos(cursor):
            print("\n✅ Todos los datos pasaron las validaciones de integridad")
        else:
            print("\n⚠️  Algunas validaciones fallaron, revisar datos")
        
        # Mostrar resumen
        mostrar_resumen(cursor)
        
        print(f"\n🎉 ¡Datos de prueba generados exitosamente!")
        print(f"💡 La base de datos 'gestionproyectos_hist' está lista para el ETL")
        print(f"📋 Todos los registros son únicos y trazables")
        
    except Exception as e:
        print(f"❌ Error generando datos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
