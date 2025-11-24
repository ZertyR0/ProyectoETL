#!/usr/bin/env python3
"""Generador parametrizable de datos para BD origen
Refactor de generar_datos_completos.py usando get_config.

Uso programático:
from src.origen.generar_datos import generar_datos
resultado = generar_datos(proyectos=10, empleados_por_proyecto=5, tareas_por_proyecto=8)

CLI:
python -m src.origen.generar_datos --proyectos 10 --empleados-por-proyecto 5 --tareas-por-proyecto 8 --limpiar
"""
from __future__ import annotations
import os, sys, random
from datetime import timedelta
from decimal import Decimal
import argparse
import mysql.connector
from faker import Faker
from src.config.config_conexion import get_config

fake = Faker('es_MX')
Faker.seed(42)
random.seed(42)

ESTADOS = {
    'proyecto': {'pendiente': 1,'en_progreso': 2,'completado': 3,'cancelado': 4},
    'tarea': {'pendiente': 1,'en_progreso': 2,'completado': 3,'cancelado': 4}
}

class GeneracionResumen(dict):
    def __str__(self):
        return ("Clientes={clientes} Empleados={empleados} Equipos={equipos} "
                "Proyectos={proyectos} Tareas={tareas}").format(**self)

def _conectar_origen(ambiente: str):
    cfg = get_config(ambiente)
    params = dict(host=cfg['host_origen'], port=cfg['port_origen'], user=cfg['user_origen'],
                  password=cfg['password_origen'], database=cfg['database_origen'], autocommit=False)
    # Unix socket si existe (solo local)
    if 'unix_socket' in cfg and cfg['host_origen'] == 'localhost':
        params['unix_socket'] = cfg['unix_socket']
    return mysql.connector.connect(**params)

def limpiar_datos(conn):
    cur = conn.cursor()
    print("🧹 Limpiando tablas origen (modo limpieza explícita)...")
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for tabla in ['TareaEquipoHist','MiembroEquipo','Tarea','Proyecto','Equipo','Empleado','Cliente']:
        cur.execute(f"DELETE FROM {tabla}")
        print(f"  - {tabla} vaciada")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()

def generar_clientes(conn, cantidad: int):
    cur = conn.cursor()
    cur.execute("SELECT id_cliente FROM Cliente ORDER BY id_cliente")
    existentes = [r[0] for r in cur.fetchall()]
    if len(existentes) >= cantidad:
        print(f"👥 Reutilizando {cantidad} clientes existentes")
        return existentes[:cantidad]
    sectores = ['Tecnología','Manufactura','Retail','Salud','Educación','Finanzas']
    nuevos = cantidad - len(existentes)
    print(f"👥 Insertando {nuevos} clientes nuevos...")
    ids = existentes.copy()
    for _ in range(nuevos):
        cur.execute("""
            INSERT INTO Cliente (nombre, sector, contacto, telefono, email)
            VALUES (%s,%s,%s,%s,%s)
        """, (fake.company(), random.choice(sectores), fake.name(), fake.phone_number()[:20],
               fake.company_email()))
        ids.append(cur.lastrowid)
    conn.commit()
    return ids

def generar_empleados(conn, cantidad: int):
    cur = conn.cursor()
    puestos = ['Desarrollador','Analista','Gerente','Diseñador','QA','DevOps']
    ids = []
    print(f"👨‍💼 Generando {cantidad} empleados...")
    for _ in range(cantidad):
        cur.execute("""
            INSERT INTO Empleado (nombre, puesto)
            VALUES (%s,%s)
        """, (fake.name(), random.choice(puestos)))
        ids.append(cur.lastrowid)
    conn.commit(); return ids

def generar_equipo(conn, empleados_ids, indice: int):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Equipo (nombre_equipo, descripcion)
        VALUES (%s,%s)
    """, (f"Equipo {fake.word().capitalize()} {indice}", f"Equipo dedicado al proyecto {indice}"))
    id_equipo = cur.lastrowid
    lider = empleados_ids[0]
    for eid in empleados_ids:
        rol = 'Líder' if eid == lider else random.choice(['Desarrollador','Analista','Soporte'])
        cur.execute("""
            INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, rol_miembro)
            VALUES (%s,%s,%s,%s)
        """, (id_equipo, eid, fake.date_between(start_date='-300d', end_date='today'), rol))
    return id_equipo

def generar_proyecto(conn, indice: int, id_cliente: int, id_gerente: int):
    cur = conn.cursor()
    r = random.random()
    if r < 0.26:
        estado = 'completado'
    elif r < 0.66:
        estado = 'cancelado'
    else:
        estado = 'en_progreso'
    id_estado = ESTADOS['proyecto'][estado]
    tipos = ['Sistema CRM','Portal Web','App Móvil','API REST','Dashboard','E-commerce']
    nombre = f"{random.choice(tipos)} - {fake.company()}"
    fecha_inicio = fake.date_between(start_date='-1y', end_date='today')
    duracion = random.randint(60,180)
    fecha_fin_plan = fecha_inicio + timedelta(days=duracion)
    presupuesto = Decimal(random.randint(100000,1000000))
    progreso = random.randint(20,70)
    fecha_fin_real = None; costo_real = None
    if estado == 'completado':
        progreso = 100
        fecha_fin_real = fecha_fin_plan + timedelta(days=random.randint(-10,20))
        costo_real = presupuesto * Decimal(random.uniform(0.85,1.15))
    elif estado == 'cancelado':
        progreso = random.randint(30,70)
        fecha_fin_real = fecha_inicio + timedelta(days=random.randint(20,duracion-10))
        costo_real = presupuesto * Decimal(random.uniform(0.3,0.7))
    cur.execute("""
        INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
                              id_estado, id_cliente, id_empleado_gerente, presupuesto, costo_real)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (nombre, fake.text(max_nb_chars=200), fecha_inicio, fecha_fin_plan, fecha_fin_real, id_estado,
           id_cliente, id_gerente, presupuesto, costo_real))
    return cur.lastrowid, estado, fecha_inicio, fecha_fin_plan, fecha_fin_real

def generar_tareas(conn, id_proyecto: int, estado_proyecto: str, empleados: list[int], f_ini, f_fin_plan, f_fin_real, tareas_por_proyecto: int):
    cur = conn.cursor(); total = 0
    for i in range(tareas_por_proyecto):
        if estado_proyecto == 'completado':
            estado_tarea = 'completado' if random.random() < 0.8 else 'cancelado'
        elif estado_proyecto == 'cancelado':
            estado_tarea = 'cancelado'
        else:
            estado_tarea = random.choice(['pendiente','en_progreso','completado'])
        id_estado = ESTADOS['tarea'][estado_tarea]
        dias_offset = random.randint(0, (f_fin_plan - f_ini).days)
        inicio_plan = f_ini + timedelta(days=dias_offset)
        duracion = random.randint(3,20)
        fin_plan = inicio_plan + timedelta(days=duracion)
        inicio_real = None; fin_real = None
        if estado_tarea in ['en_progreso','completado','cancelado']:
            inicio_real = inicio_plan + timedelta(days=random.randint(-2,3))
        if estado_tarea == 'completado':
            fin_real = fin_plan + timedelta(days=random.randint(-5,7))
        elif estado_tarea == 'cancelado':
            fin_real = inicio_real + timedelta(days=random.randint(1,duracion-1)) if inicio_real else None
        horas_plan = random.randint(10,100)
        if estado_tarea == 'completado':
            horas_reales = int(horas_plan * random.uniform(0.7,1.3))
        elif estado_tarea == 'en_progreso':
            horas_reales = int(horas_plan * random.uniform(0.3,0.9))
        elif estado_tarea == 'cancelado':
            horas_reales = int(horas_plan * random.uniform(0.2,0.6))
        else:
            horas_reales = 0
        costo_estimado = Decimal(horas_plan * random.randint(500,2000))
        costo_real = Decimal(horas_reales * random.randint(500,2000)) if horas_reales > 0 else Decimal(0)
        progreso = 100 if estado_tarea == 'completado' else (random.randint(40,70) if estado_tarea == 'cancelado' else random.randint(0,80))
        empleado_id = random.choice(empleados)
        cur.execute("""
            INSERT INTO Tarea (nombre_tarea, id_estado, id_proyecto,
                               fecha_inicio_plan, fecha_fin_plan, fecha_fin_real,
                               horas_plan, horas_reales)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (f"Tarea {i+1} - {fake.catch_phrase()[:80]}", id_estado, id_proyecto,
               inicio_plan, fin_plan, fin_real, horas_plan, horas_reales))
        total += 1
    return total

def generar_datos(proyectos: int = 10, empleados_por_proyecto: int = 5, tareas_por_proyecto: int = 8,
                  limpiar: bool = False, ambiente: str | None = None) -> GeneracionResumen:
    ambiente_final = ambiente if ambiente is not None else os.getenv('ETL_AMBIENTE', 'local')
    conn = _conectar_origen(ambiente_final)
    if limpiar:
        limpiar_datos(conn)
    clientes_ids = generar_clientes(conn, proyectos)
    empleados_total = proyectos * empleados_por_proyecto
    empleados_ids = generar_empleados(conn, empleados_total)
    proyectos_creados = 0; tareas_total = 0; equipos_total = 0
    for i in range(proyectos):
        slice_ini = i * empleados_por_proyecto
        slice_fin = slice_ini + empleados_por_proyecto
        empleados_proy = empleados_ids[slice_ini:slice_fin]
        if not empleados_proy:
            break
        generar_equipo(conn, empleados_proy, i+1); equipos_total += 1
        # clientes_ids proviene de INSERTs -> siempre ints; defensivo por si se reutiliza
        id_cliente_raw = clientes_ids[i]
        id_cliente = int(id_cliente_raw) if isinstance(id_cliente_raw, (int, str)) else int(getattr(id_cliente_raw, 'id_cliente', 0))
        id_proy_tuple = generar_proyecto(conn, i+1, id_cliente, int(empleados_proy[0]))
        # id_proy_tuple esperado: (id_proy, estado, f_ini, f_fin_plan, f_fin_real)
        if not id_proy_tuple or id_proy_tuple[0] is None:
            continue
        id_proy, estado_proy, f_ini, f_fin_plan, f_fin_real = id_proy_tuple
        # id_proy garantizado int por autoincrement -> defensivo si fuese None
        if id_proy is None:
            continue
        tareas_total += generar_tareas(conn, int(id_proy), estado_proy, empleados_proy, f_ini, f_fin_plan, f_fin_real, tareas_por_proyecto)
        proyectos_creados += 1
        if (i+1) % 10 == 0:
            conn.commit(); print(f"  ✓ {i+1}/{proyectos} proyectos procesados")
    conn.commit()
    cur = conn.cursor()
    def _count(tabla: str) -> int:
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        row = cur.fetchone()
        if not row:
            return 0
        # row es tupla (count(*)) -> índice 0
        val = row[0] if isinstance(row, (list, tuple)) else row
        if isinstance(val, int):
            return val
        try:
            return int(str(val))
        except Exception:
            return 0
    resumen = GeneracionResumen(clientes=_count('Cliente'), empleados=_count('Empleado'), equipos=_count('Equipo'),
                                proyectos=_count('Proyecto'), tareas=_count('Tarea'))
    print("\n✅ Generación completada:", resumen)
    cur.close(); conn.close()
    return resumen

def _parse_args(argv):
    p = argparse.ArgumentParser(description="Generar datos de ejemplo para el origen")
    p.add_argument('--proyectos', type=int, default=10)
    p.add_argument('--empleados-por-proyecto', type=int, default=5)
    p.add_argument('--tareas-por-proyecto', type=int, default=8)
    p.add_argument('--limpiar', action='store_true')
    p.add_argument('--ambiente', type=str, default=None)
    return p.parse_args(argv)

def main(argv=None):
    args = _parse_args(argv or sys.argv[1:])
    generar_datos(proyectos=args.proyectos, empleados_por_proyecto=args.empleados_por_proyecto,
                  tareas_por_proyecto=args.tareas_por_proyecto, limpiar=args.limpiar, ambiente=args.ambiente)

if __name__ == '__main__':
    main()
