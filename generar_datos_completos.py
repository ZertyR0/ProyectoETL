#!/usr/bin/env python3
"""
Generador de datos completos para BD remota
Adaptado a la estructura real de la base de datos
"""

import mysql.connector
import random
from faker import Faker
from datetime import datetime, date, timedelta
from decimal import Decimal

fake = Faker('es_MX')
Faker.seed(42)
random.seed(42)

# Configuración
HOST = '172.20.10.3'
USER = 'etl_user'
PASSWORD = 'etl_password_123'
DATABASE = 'gestionproyectos_hist'

CANTIDAD_PROYECTOS = 300
EMPLEADOS_POR_PROYECTO = 5
TAREAS_POR_PROYECTO = 10
LIMPIAR_DATOS = False  # NO limpiar, solo agregar nuevos

# IDs de estados (según tabla Estado)
ESTADOS = {
    'proyecto': {
        'pendiente': 10,
        'en_progreso': 11,
        'completado': 12,
        'cancelado': 13
    },
    'tarea': {
        'pendiente': 20,
        'en_progreso': 21,
        'completado': 22,
        'cancelado': 23
    }
}

def conectar():
    """Conectar a BD remota"""
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        autocommit=False
    )

def limpiar_datos(conn):
    """Limpiar todas las tablas"""
    print("🧹 Limpiando base de datos...")
    cursor = conn.cursor()
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tablas = ['TareaEquipoHist', 'MiembroEquipo', 'Tarea', 'Proyecto', 'Equipo', 'Empleado', 'Cliente']
    for tabla in tablas:
        cursor.execute(f"DELETE FROM {tabla}")
        print(f"  ✓ {tabla} limpiada")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("✅ Limpieza completada\n")

def generar_clientes(conn, cantidad):
    """Generar clientes únicos"""
    print(f"👥 Generando {cantidad} clientes...")
    cursor = conn.cursor()
    
    clientes_ids = []
    sectores = ['Tecnología', 'Manufactura', 'Retail', 'Salud', 'Educación', 'Finanzas']
    
    for i in range(cantidad):
        nombre = fake.company()
        cursor.execute("""
            INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion, ciudad, pais, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            random.choice(sectores),
            fake.name(),
            fake.phone_number()[:20],
            fake.company_email(),
            fake.address()[:200],
            fake.city(),
            'México',
            fake.date_between(start_date='-2y', end_date='today')
        ))
        clientes_ids.append(cursor.lastrowid)
    
    conn.commit()
    print(f"✅ {cantidad} clientes creados\n")
    return clientes_ids

def generar_empleados(conn, cantidad):
    """Generar empleados"""
    print(f"👨‍💼 Generando {cantidad} empleados...")
    cursor = conn.cursor()
    
    empleados_ids = []
    puestos = ['Desarrollador', 'Analista', 'Gerente', 'Diseñador', 'QA', 'DevOps']
    departamentos = ['Desarrollo', 'Análisis', 'Diseño', 'QA', 'Infraestructura']
    niveles = ['Junior', 'Mid', 'Senior', 'Lead']
    
    for i in range(cantidad):
        nombre = fake.name()
        puesto = random.choice(puestos)
        salario = Decimal(random.randint(25000, 80000))
        
        cursor.execute("""
            INSERT INTO Empleado (nombre, puesto, departamento, salario_base, salario, 
                                fecha_ingreso, fecha_contratacion, email, telefono, nivel, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            puesto,
            random.choice(departamentos),
            salario,
            salario,
            fake.date_between(start_date='-3y', end_date='-1m'),
            fake.date_between(start_date='-3y', end_date='-1m'),
            fake.email(),
            fake.phone_number()[:20],
            random.choice(niveles),
            1
        ))
        empleados_ids.append(cursor.lastrowid)
    
    conn.commit()
    print(f"✅ {cantidad} empleados creados\n")
    return empleados_ids

def generar_equipo(conn, num_equipo, empleados_asignados):
    """Generar un equipo"""
    cursor = conn.cursor()
    
    nombre_equipo = f"Equipo {fake.word().capitalize()} {num_equipo}"
    lider_id = empleados_asignados[0]  # Primer empleado es líder
    
    cursor.execute("""
        INSERT INTO Equipo (nombre_equipo, descripcion, fecha_creacion, lider_id, tipo, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        nombre_equipo,
        f"Equipo dedicado al proyecto {num_equipo}",
        date.today() - timedelta(days=random.randint(30, 365)),
        lider_id,
        'Proyecto',
        1
    ))
    
    id_equipo = cursor.lastrowid
    
    # Asignar miembros al equipo
    for empleado_id in empleados_asignados:
        rol = 'Líder' if empleado_id == lider_id else random.choice(['Desarrollador', 'Analista', 'Soporte'])
        cursor.execute("""
            INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_asignacion, rol, rol_miembro, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_equipo,
            empleado_id,
            date.today() - timedelta(days=random.randint(10, 300)),
            date.today() - timedelta(days=random.randint(10, 300)),
            rol,
            rol,
            1
        ))
    
    return id_equipo

def generar_proyecto(conn, num_proyecto, id_cliente, id_gerente):
    """Generar un proyecto completo"""
    cursor = conn.cursor()
    
    # Determinar estado del proyecto
    rand = random.random()
    if rand < 0.26:  # 26% completados
        id_estado_num = ESTADOS['proyecto']['completado']
        estado_text = 'Completado'
    elif rand < 0.66:  # 40% cancelados  
        id_estado_num = ESTADOS['proyecto']['cancelado']
        estado_text = 'Cancelado'
    else:  # 34% en progreso
        id_estado_num = ESTADOS['proyecto']['en_progreso']
        estado_text = 'En Progreso'
    
    tipos = ['Sistema CRM', 'Portal Web', 'App Móvil', 'API REST', 'Dashboard', 'E-commerce']
    nombre = f"{random.choice(tipos)} - {fake.company()}"
    
    fecha_inicio = fake.date_between(start_date='-1y', end_date='today')
    duracion_dias = random.randint(60, 180)
    fecha_fin_plan = fecha_inicio + timedelta(days=duracion_dias)
    
    presupuesto = Decimal(random.randint(100000, 1000000))
    progreso = random.randint(70, 100) if estado_text in ['Completado', 'Cancelado'] else random.randint(20, 70)
    
    # Calcular fecha_fin_real y costo_real si está completado o cancelado
    fecha_fin_real = None
    costo_real = None
    if estado_text == 'Completado':
        variacion = random.randint(-10, 20)
        fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
        costo_real = presupuesto * Decimal(random.uniform(0.85, 1.15))
        progreso = 100
    elif estado_text == 'Cancelado':
        dias_trabajados = random.randint(20, duracion_dias - 10)
        fecha_fin_real = fecha_inicio + timedelta(days=dias_trabajados)
        costo_real = presupuesto * Decimal(random.uniform(0.3, 0.7))
        progreso = random.randint(30, 70)
    
    cursor.execute("""
        INSERT INTO Proyecto (
            nombre, descripcion, fecha_inicio, fecha_fin_estimada, fecha_fin_plan, fecha_fin_real,
            estado, id_estado, id_cliente, id_empleado_gerente,
            presupuesto, costo_real, progreso, progreso_porcentaje, prioridad
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        nombre,
        fake.text(max_nb_chars=200),
        fecha_inicio,
        fecha_fin_plan,
        fecha_fin_plan,
        fecha_fin_real,
        estado_text,
        id_estado_num,
        id_cliente,
        id_gerente,
        presupuesto,
        costo_real,
        progreso,
        progreso,
        random.choice(['Alta', 'Media', 'Baja'])
    ))
    
    return cursor.lastrowid, estado_text, fecha_inicio, fecha_fin_plan, fecha_fin_real

def generar_tareas(conn, id_proyecto, estado_proyecto, empleados, fecha_inicio_proy, fecha_fin_plan_proy, fecha_fin_real_proy):
    """Generar tareas para un proyecto"""
    cursor = conn.cursor()
    
    tareas_creadas = 0
    for i in range(TAREAS_POR_PROYECTO):
        # Determinar estado de la tarea basado en el proyecto
        if estado_proyecto == 'Completado':
            if random.random() < 0.8:
                id_estado = ESTADOS['tarea']['completado']
                estado_text = 'Completado'
            else:
                id_estado = ESTADOS['tarea']['cancelado']
                estado_text = 'Cancelado'
        elif estado_proyecto == 'Cancelado':
            id_estado = ESTADOS['tarea']['cancelado']
            estado_text = 'Cancelado'
        else:  # En Progreso
            opciones = ['Pendiente', 'En Progreso', 'Completado']
            estado_text = random.choice(opciones)
            id_estado = ESTADOS['tarea'][estado_text.lower().replace(' ', '_')]
        
        # Fechas de la tarea
        dias_desde_inicio = random.randint(0, (fecha_fin_plan_proy - fecha_inicio_proy).days)
        fecha_inicio_tarea = fecha_inicio_proy + timedelta(days=dias_desde_inicio)
        duracion_tarea = random.randint(3, 20)
        fecha_fin_plan_tarea = fecha_inicio_tarea + timedelta(days=duracion_tarea)
        
        fecha_inicio_real = None
        fecha_fin_real = None
        if estado_text in ['Completado', 'Cancelado', 'En Progreso']:
            fecha_inicio_real = fecha_inicio_tarea + timedelta(days=random.randint(-2, 3))
        if estado_text == 'Completado':
            variacion = random.randint(-5, 7)
            fecha_fin_real = fecha_fin_plan_tarea + timedelta(days=variacion)
        elif estado_text == 'Cancelado':
            fecha_fin_real = fecha_inicio_real + timedelta(days=random.randint(1, duracion_tarea - 1))
        
        # Horas y costos
        horas_plan = random.randint(10, 100)
        horas_reales = 0
        if estado_text in ['Completado', 'En Progreso']:
            horas_reales = int(horas_plan * random.uniform(0.7, 1.3))
        elif estado_text == 'Cancelado':
            horas_reales = int(horas_plan * random.uniform(0.2, 0.6))
        
        costo_estimado = Decimal(horas_plan * random.randint(500, 2000))
        costo_real = Decimal(horas_reales * random.randint(500, 2000)) if horas_reales > 0 else Decimal(0)
        
        progreso_tarea = 100 if estado_text == 'Completado' else (random.randint(40, 70) if estado_text == 'Cancelado' else random.randint(0, 80))
        
        id_empleado = random.choice(empleados)
        
        cursor.execute("""
            INSERT INTO Tarea (
                titulo, nombre_tarea, descripcion, estado, id_estado, prioridad,
                fecha_creacion, fecha_vencimiento, fecha_completado,
                id_proyecto, id_responsable, id_empleado_responsable, id_empleado,
                fecha_inicio, fecha_inicio_plan, fecha_inicio_real,
                fecha_fin_plan, fecha_fin_real,
                estimacion_horas, horas_estimadas, horas_plan,
                horas_trabajadas, horas_reales,
                costo_estimado, costo_real,
                progreso, progreso_porcentaje
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            f"Tarea {i+1}",
            f"Tarea {i+1} - {fake.catch_phrase()[:80]}",
            fake.text(max_nb_chars=150),
            estado_text,
            id_estado,
            random.choice(['Alta', 'Media', 'Baja']),
            fecha_inicio_proy,
            fecha_fin_plan_tarea,
            fecha_fin_real if estado_text == 'Completado' else None,
            id_proyecto,
            id_empleado,
            id_empleado,
            id_empleado,
            fecha_inicio_tarea,
            fecha_inicio_tarea,
            fecha_inicio_real,
            fecha_fin_plan_tarea,
            fecha_fin_real,
            horas_plan,
            horas_plan,
            horas_plan,
            horas_reales,
            horas_reales,
            costo_estimado,
            costo_real,
            progreso_tarea,
            progreso_tarea
        ))
        
        tareas_creadas += 1
    
    return tareas_creadas

def main():
    print("\n" + "="*70)
    print("🌐 GENERADOR DE DATOS COMPLETOS - BD REMOTA")
    print("="*70 + "\n")
    
    try:
        conn = conectar()
        print("✅ Conectado a BD remota\n")
        
        # Limpiar solo si está habilitado
        if LIMPIAR_DATOS:
            limpiar_datos(conn)
        else:
            print("ℹ️  Modo: AGREGAR nuevos datos (sin limpiar)\n")
        
        # Generar clientes (1 por proyecto)
        clientes_ids = generar_clientes(conn, CANTIDAD_PROYECTOS)
        
        # Generar empleados (pool general)
        total_empleados = CANTIDAD_PROYECTOS * EMPLEADOS_POR_PROYECTO
        empleados_ids = generar_empleados(conn, total_empleados)
        
        # Generar proyectos con equipos y tareas
        print(f"🏗️  Generando {CANTIDAD_PROYECTOS} proyectos completos...")
        proyectos_creados = 0
        tareas_totales = 0
        
        for i in range(CANTIDAD_PROYECTOS):
            # Empleados para este proyecto
            inicio_emp = i * EMPLEADOS_POR_PROYECTO
            empleados_proyecto = empleados_ids[inicio_emp:inicio_emp + EMPLEADOS_POR_PROYECTO]
            
            # Crear equipo
            id_equipo = generar_equipo(conn, i + 1, empleados_proyecto)
            
            # Crear proyecto
            id_gerente = empleados_proyecto[0]  # Líder es gerente
            id_proyecto, estado_proy, f_inicio, f_fin_plan, f_fin_real = generar_proyecto(
                conn, i + 1, clientes_ids[i], id_gerente
            )
            
            # Crear tareas
            tareas = generar_tareas(conn, id_proyecto, estado_proy, empleados_proyecto, 
                                   f_inicio, f_fin_plan, f_fin_real)
            tareas_totales += tareas
            
            proyectos_creados += 1
            
            if (i + 1) % 10 == 0:
                conn.commit()
                print(f"  ✓ {i + 1}/{CANTIDAD_PROYECTOS} proyectos...")
        
        conn.commit()
        print(f"  ✅ {proyectos_creados} proyectos completados\n")
        
        # Resumen final
        cursor = conn.cursor()
        print("="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        
        cursor.execute("SELECT COUNT(*) FROM Cliente")
        print(f"  Clientes:  {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Empleado")
        print(f"  Empleados: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Equipo")
        print(f"  Equipos:   {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Proyecto")
        print(f"  Proyectos: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM Tarea")
        print(f"  Tareas:    {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT id_estado, COUNT(*) FROM Proyecto GROUP BY id_estado")
        print("\n  Estados de proyectos:")
        for row in cursor.fetchall():
            estado_nombre = {10: 'Pendiente', 11: 'En Progreso', 12: 'Completado', 13: 'Cancelado'}.get(row[0], row[0])
            print(f"    {estado_nombre}: {row[1]}")
        
        print("="*70)
        print("✅ ¡GENERACIÓN EXITOSA!")
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
