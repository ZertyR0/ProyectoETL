#!/usr/bin/env python3
"""
GENERADOR DE DATOS FINAL - Sistema de Gestión de Proyectos
Versión unificada y optimizada que combina:
- Seguridad (sin SQL injection)
- Sin duplicados
- Datos realistas y únicos por proyecto
- Validación de integridad

CARACTERÍSTICAS:
✓ Cada proyecto tiene su propio equipo de empleados
✓ Sin reutilización de recursos entre proyectos
✓ Validación de unicidad
✓ Trazabilidad completa
"""

import mysql.connector
import random
from faker import Faker
from datetime import datetime, date, timedelta
import sys
import hashlib

# Configuración
fake = Faker('es_MX')
Faker.seed(42)

# Cantidades configurables
CANTIDAD_PROYECTOS = 50  # Número de proyectos a generar
EMPLEADOS_POR_PROYECTO = 5  # Cada proyecto tendrá su equipo exclusivo
EQUIPOS_POR_PROYECTO = 1  # Cada proyecto tendrá su equipo propio
TAREAS_POR_PROYECTO = 10  # Tareas por proyecto

# Sets para control de duplicados
nombres_unicos = {
    'clientes': set(),
    'empleados': set(),
    'equipos': set(),
    'proyectos': set(),
    'emails': set()
}

class GeneradorDatosFinal:
    """Generador unificado de datos sin duplicados"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.stats = {
            'clientes': 0,
            'empleados': 0,
            'equipos': 0,
            'proyectos': 0,
            'tareas': 0,
            'asignaciones': 0
        }
    
    def conectar_bd(self):
        """Conectar a la base de datos con el socket correcto"""
        try:
            # Intentar conexión con socket XAMPP
            try:
                self.conn = mysql.connector.connect(
                    user='root',
                    password='',
                    database='gestionproyectos_hist',
                    unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                    autocommit=False
                )
                print(" Conectado vía socket XAMPP")
            except:
                # Fallback a conexión TCP
                self.conn = mysql.connector.connect(
                    host='localhost',
                    port=3306,
                    user='root',
                    password='',
                    database='gestionproyectos_hist',
                    autocommit=False
                )
                print(" Conectado vía TCP")
            
            self.cursor = self.conn.cursor(dictionary=True)
            return True
            
        except mysql.connector.Error as err:
            print(f" Error conectando: {err}")
            return False
    
    def cerrar_conexion(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def generar_hash(self, tipo, *valores):
        """Generar hash único para control de duplicados"""
        data = f"{tipo}|{'|'.join(map(str, valores))}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def limpiar_tablas(self):
        """Limpiar tablas manteniendo Estados"""
        print("\n🧹 Limpiando tablas existentes...")
        
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tablas = ['TareaEquipoHist', 'MiembroEquipo', 'Tarea', 'Proyecto', 'Equipo', 'Empleado', 'Cliente']
            for tabla in tablas:
                self.cursor.execute(f"TRUNCATE TABLE {tabla}")
                print(f"  ✓ {tabla} limpiada")
            
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.conn.commit()
            
            # Limpiar sets de control
            for key in nombres_unicos:
                nombres_unicos[key].clear()
            
            print("   Limpieza completada")
            return True
            
        except Exception as e:
            print(f"   Error limpiando: {e}")
            self.conn.rollback()
            return False
    
    def _cargar_nombres_existentes(self):
        """Cargar nombres existentes en la BD para evitar duplicados en modo incremental"""
        print("📚 Cargando nombres existentes para evitar duplicados...")
        
        try:
            # Cargar clientes existentes
            self.cursor.execute("SELECT nombre FROM Cliente")
            for (nombre,) in self.cursor.fetchall():
                nombres_unicos['clientes'].add(nombre)
            
            # Cargar empleados existentes
            self.cursor.execute("SELECT nombre FROM Empleado")
            for (nombre,) in self.cursor.fetchall():
                nombres_unicos['empleados'].add(nombre)
            
            # Cargar equipos existentes
            self.cursor.execute("SELECT nombre FROM Equipo")
            for (nombre,) in self.cursor.fetchall():
                nombres_unicos['equipos'].add(nombre)
            
            # Cargar proyectos existentes
            self.cursor.execute("SELECT nombre FROM Proyecto")
            for (nombre,) in self.cursor.fetchall():
                nombres_unicos['proyectos'].add(nombre)
            
            # Cargar emails existentes
            self.cursor.execute("SELECT email FROM Empleado WHERE email IS NOT NULL")
            for (email,) in self.cursor.fetchall():
                nombres_unicos['emails'].add(email)
            
            print(f"  ✓ {len(nombres_unicos['clientes'])} clientes existentes")
            print(f"  ✓ {len(nombres_unicos['empleados'])} empleados existentes")
            print(f"  ✓ {len(nombres_unicos['equipos'])} equipos existentes")
            print(f"  ✓ {len(nombres_unicos['proyectos'])} proyectos existentes")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error cargando nombres existentes: {e}")
            return False
    
    def generar_nombre_unico(self, tipo, generador_func):
        """Generar un nombre único del tipo especificado"""
        max_intentos = 50
        for intento in range(max_intentos):
            nombre = generador_func()
            if nombre not in nombres_unicos[tipo]:
                nombres_unicos[tipo].add(nombre)
                return nombre
        
        # Si no se encuentra único después de 50 intentos, agregar sufijo
        nombre = f"{generador_func()} #{random.randint(1000, 9999)}"
        nombres_unicos[tipo].add(nombre)
        return nombre
    
    def generar_email_unico(self, base):
        """Generar email único"""
        base_limpia = base.lower().replace(' ', '').replace(',', '')[:20]
        email = f"{base_limpia}@{fake.free_email_domain()}"
        
        contador = 1
        while email in nombres_unicos['emails']:
            email = f"{base_limpia}{contador}@{fake.free_email_domain()}"
            contador += 1
        
        nombres_unicos['emails'].add(email)
        return email
    
    def generar_clientes(self, cantidad=None):
        """Generar un cliente por proyecto (relación 1:1)"""
        if cantidad is None:
            cantidad = CANTIDAD_PROYECTOS
            
        print(f"\n👥 Generando {cantidad} clientes (1 por proyecto)...")
        
        sectores = ['Tecnología', 'Finanzas', 'Salud', 'Educación', 'Retail', 
                   'Manufactura', 'Servicios', 'Telecomunicaciones', 'Gobierno', 'Energía']
        
        clientes_ids = []
        
        for i in range(cantidad):
            nombre = self.generar_nombre_unico('clientes', fake.company)
            sector = random.choice(sectores)
            contacto = fake.name()
            telefono = fake.phone_number()[:20]
            email = self.generar_email_unico(nombre)
            direccion = fake.address().replace('\n', ', ')[:200]
            
            self.cursor.execute("""
                INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, sector, contacto, telefono, email, direccion))
            
            clientes_ids.append(self.cursor.lastrowid)
            self.stats['clientes'] += 1
        
        self.conn.commit()
        print(f"   {self.stats['clientes']} clientes únicos creados")
        return clientes_ids
    
    def generar_empleados_por_proyecto(self, num_proyecto, cantidad=None):
        """Generar empleados exclusivos para un proyecto específico"""
        if cantidad is None:
            cantidad = EMPLEADOS_POR_PROYECTO
            
        puestos = [
            ('Gerente de Proyecto', 'Gestión', (60000, 100000)),
            ('Desarrollador Senior', 'Desarrollo', (50000, 80000)),
            ('Desarrollador', 'Desarrollo', (40000, 60000)),
            ('Analista', 'Análisis', (45000, 65000)),
            ('QA Tester', 'QA', (35000, 55000)),
            ('Diseñador UX/UI', 'Diseño', (40000, 65000)),
            ('DevOps Engineer', 'DevOps', (50000, 75000)),
            ('Arquitecto de Software', 'Desarrollo', (65000, 95000)),
            ('Scrum Master', 'Gestión', (50000, 70000)),
            ('Product Owner', 'Gestión', (55000, 80000))
        ]
        
        empleados_proyecto = []
        puestos_proyecto = random.sample(puestos, min(cantidad, len(puestos)))
        
        for puesto, departamento, (sal_min, sal_max) in puestos_proyecto:
            nombre = self.generar_nombre_unico('empleados', fake.name)
            salario = random.randint(sal_min, sal_max)
            fecha_ingreso = fake.date_between(start_date='-3y', end_date='-6m')
            
            self.cursor.execute("""
                INSERT INTO Empleado (nombre, puesto, departamento, salario_base, fecha_ingreso)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, puesto, departamento, salario, fecha_ingreso))
            
            empleados_proyecto.append({
                'id': self.cursor.lastrowid,
                'nombre': nombre,
                'puesto': puesto,
                'es_gerente': 'Gerente' in puesto
            })
            self.stats['empleados'] += 1
        
        return empleados_proyecto
    
    def generar_equipo_por_proyecto(self, num_proyecto, empleados, fecha_fin_proyecto=None, estado_proyecto=None):
        """Generar equipo exclusivo para un proyecto
        
        Args:
            num_proyecto: Número del proyecto
            empleados: Lista de empleados del equipo
            fecha_fin_proyecto: Fecha de fin del proyecto (si está completado/cancelado)
            estado_proyecto: Estado del proyecto (3=Completado, 4=Cancelado)
        """
        nombre_equipo = self.generar_nombre_unico('equipos', 
            lambda: f"Equipo Proyecto {num_proyecto + 1}")
        descripcion = fake.catch_phrase()
        
        self.cursor.execute("""
            INSERT INTO Equipo (nombre_equipo, descripcion)
            VALUES (%s, %s)
        """, (nombre_equipo, descripcion))
        
        id_equipo = self.cursor.lastrowid
        self.stats['equipos'] += 1
        
        # Asignar todos los empleados del proyecto a este equipo
        roles = ['Team Lead', 'Developer', 'Senior Developer', 'Analyst', 'Tester', 'Designer']
        
        for idx, empleado in enumerate(empleados):
            rol = 'Team Lead' if empleado['es_gerente'] else random.choice(roles)
            fecha_inicio = fake.date_between(start_date='-2y', end_date='-1m')
            
            # Si el proyecto está completado/cancelado, el equipo también debe tener fecha_fin
            if estado_proyecto in [3, 4] and fecha_fin_proyecto:
                # Fecha fin del equipo cercana a la fecha fin del proyecto
                dias_variacion = random.randint(-5, 10)
                fecha_fin = fecha_fin_proyecto + timedelta(days=dias_variacion)
                activo = 0  # Equipo inactivo
            else:
                fecha_fin = None  # Equipo activo
                activo = 1
            
            self.cursor.execute("""
                INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_fin, 
                                          rol_miembro, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_equipo, empleado['id'], fecha_inicio, fecha_fin, rol, activo))
            
            self.stats['asignaciones'] += 1
        
        return id_equipo
    
    def generar_proyecto_base(self, num_proyecto, id_cliente, empleados):
        """Generar un proyecto base (sin equipo ni tareas) y retornar sus datos clave
        
        Returns:
            tuple: (id_proyecto, fecha_fin_real, estado)
        """
        tipos_proyecto = [
            'Sistema Web', 'Aplicación Móvil', 'Plataforma E-commerce',
            'Sistema CRM', 'Portal Corporativo', 'API REST', 
            'Dashboard Analytics', 'Sistema ERP', 'App IoT',
            'Plataforma Cloud', 'Sistema de Facturación', 'Portal de Servicios'
        ]
        
        tipo = random.choice(tipos_proyecto)
        
        # Obtener el nombre del cliente de la BD en lugar del set
        cursor_temp = self.conn.cursor()
        cursor_temp.execute("SELECT nombre FROM Cliente WHERE id_cliente = %s", (id_cliente,))
        result = cursor_temp.fetchone()
        cliente_nombre = result[0] if result else "Cliente"
        cursor_temp.close()
        
        nombre = self.generar_nombre_unico('proyectos', 
            lambda: f"{tipo} - {cliente_nombre.split()[0]}")
        
        descripcion = fake.text(max_nb_chars=300)
        
        # Fechas del proyecto
        fecha_inicio = fake.date_between(start_date='-1y', end_date='+30d')
        duracion_plan = random.randint(60, 180)
        fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan)
        
        # Estado: 60% Completado/Cancelado (para el ETL), 40% otros
        if random.random() < 0.6:
            estado = random.choice([3, 4])  # Completado o Cancelado
            variacion = random.randint(-15, 30)
            fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
        else:
            estado = random.choice([1, 2])  # Pendiente o En Progreso
            fecha_fin_real = None
        
        presupuesto = random.randint(100000, 800000)
        costo_real = presupuesto + random.randint(-30000, 50000) if fecha_fin_real else 0
        
        # Gerente del proyecto (el primer empleado con puesto de gerente)
        gerente = next((e for e in empleados if e['es_gerente']), empleados[0])
        
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        prioridad = random.choice(prioridades)
        progreso = 100 if estado == 3 else (random.randint(10, 90) if estado == 2 else 0)
        
        # Insertar proyecto SIN id_equipo (se actualizará después)
        self.cursor.execute("""
            INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, 
                                fecha_fin_real, presupuesto, costo_real, id_cliente, 
                                id_estado, id_empleado_gerente, prioridad, progreso_porcentaje)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
              presupuesto, costo_real, id_cliente, estado, gerente['id'],
              prioridad, progreso))
        
        id_proyecto = self.cursor.lastrowid
        self.stats['proyectos'] += 1
        
        # Guardar datos del proyecto para uso posterior
        self._proyecto_fecha_inicio = fecha_inicio
        self._proyecto_fecha_fin_plan = fecha_fin_plan
        
        return id_proyecto, fecha_fin_real, estado
    
    def completar_proyecto(self, id_proyecto, id_equipo, empleados, estado_proyecto):
        """Completar el proyecto actualizando el equipo y generando tareas"""
        # No hay columna id_equipo en Proyecto, así que solo generamos las tareas
        # Generar tareas del proyecto
        self.generar_tareas_proyecto(
            id_proyecto, empleados, id_equipo,
            self._proyecto_fecha_inicio, self._proyecto_fecha_fin_plan, estado_proyecto
        )
    
    def generar_tareas_proyecto(self, id_proyecto, empleados, id_equipo, 
                               fecha_inicio_proyecto, fecha_fin_proyecto, estado_proyecto):
        """Generar tareas únicas para un proyecto específico"""
        nombres_tareas = [
            'Análisis de Requerimientos', 'Diseño de Arquitectura', 'Setup de Infraestructura',
            'Diseño de Base de Datos', 'Implementación Backend', 'Desarrollo Frontend',
            'Integración de APIs', 'Implementación de Seguridad', 'Pruebas Unitarias',
            'Pruebas de Integración', 'Testing E2E', 'Optimización de Performance',
            'Documentación Técnica', 'Code Review', 'Deploy a Staging',
            'Testing de Usuario', 'Corrección de Bugs', 'Deploy a Producción',
            'Capacitación', 'Monitoreo Post-Deploy'
        ]
        
        tareas_seleccionadas = random.sample(nombres_tareas, 
                                            min(TAREAS_POR_PROYECTO, len(nombres_tareas)))
        
        estados_tarea = [1, 2, 3, 4]
        prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
        
        for nombre_tarea in tareas_seleccionadas:
            nombre_completo = f"{nombre_tarea} - P{id_proyecto}"
            descripcion = fake.text(max_nb_chars=200)
            
            # Fechas dentro del rango del proyecto
            dias_proyecto = (fecha_fin_proyecto - fecha_inicio_proyecto).days
            inicio_offset = random.randint(0, max(1, dias_proyecto - 20))
            fecha_inicio_plan = fecha_inicio_proyecto + timedelta(days=inicio_offset)
            
            duracion = random.randint(5, 21)
            fecha_fin_plan = fecha_inicio_plan + timedelta(days=duracion)
            
            # Estado de la tarea similar al proyecto
            if estado_proyecto in [3, 4]:
                estado = random.choice([3, 4])
                fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 3))
                variacion = random.randint(-3, 7)
                fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
            elif estado_proyecto == 2:
                estado = random.choice([2, 3])
                fecha_inicio_real = fecha_inicio_plan if estado == 2 else None
                fecha_fin_real = None
            else:
                estado = 1
                fecha_inicio_real = None
                fecha_fin_real = None
            
            horas_plan = random.randint(16, 120)
            horas_reales = horas_plan + random.randint(-10, 30) if estado in [3, 4] else 0
            
            # Asignar a un empleado del equipo del proyecto
            empleado = random.choice(empleados)
            prioridad = random.choice(prioridades)
            progreso = 100 if estado == 3 else (random.randint(20, 80) if estado == 2 else 0)
            
            costo_estimado = horas_plan * random.randint(600, 1800)
            costo_real = horas_reales * random.randint(600, 1800) if horas_reales > 0 else 0
            
            self.cursor.execute("""
                INSERT INTO Tarea (nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan,
                                 fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                                 id_proyecto, id_empleado, id_estado, prioridad, 
                                 progreso_porcentaje, costo_estimado, costo_real)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre_completo, descripcion, fecha_inicio_plan, fecha_fin_plan,
                  fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                  id_proyecto, empleado['id'], estado, prioridad, progreso,
                  costo_estimado, costo_real))
            
            id_tarea = self.cursor.lastrowid
            self.stats['tareas'] += 1
            
            # Asignar tarea al equipo del proyecto
            fecha_asignacion = fecha_inicio_plan
            fecha_liberacion = fecha_fin_real if estado in [3, 4] else None
            
            self.cursor.execute("""
                INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, 
                                            fecha_liberacion, horas_asignadas, notas)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion, 
                  horas_plan, f"Asignado a {nombre_tarea}"))
    
    def validar_integridad(self):
        """Validar integridad y unicidad de los datos"""
        print("\n🔍 Validando integridad...")
        
        validaciones = [
            ("Clientes únicos", "SELECT COUNT(*) as t, COUNT(DISTINCT nombre) as u FROM Cliente"),
            ("Emails únicos", "SELECT COUNT(*) as t, COUNT(DISTINCT email) as u FROM Cliente"),
            ("Empleados únicos", "SELECT COUNT(*) as t, COUNT(DISTINCT nombre) as u FROM Empleado"),
            ("Equipos únicos", "SELECT COUNT(*) as t, COUNT(DISTINCT nombre_equipo) as u FROM Equipo"),
            ("Proyectos únicos", "SELECT COUNT(*) as t, COUNT(DISTINCT nombre) as u FROM Proyecto"),
        ]
        
        todas_ok = True
        for nombre, query in validaciones:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            total = result['t']
            unicos = result['u']
            ok = total == unicos
            icono = "" if ok else ""
            print(f"  {icono} {nombre}: {unicos}/{total}")
            if not ok:
                todas_ok = False
        
        # Validar que no haya empleados compartidos entre proyectos
        self.cursor.execute("""
            SELECT e.nombre, COUNT(DISTINCT p.id_proyecto) as proyectos
            FROM Empleado e
            JOIN Tarea t ON t.id_empleado = e.id_empleado
            JOIN Proyecto p ON p.id_proyecto = t.id_proyecto
            GROUP BY e.id_empleado
            HAVING proyectos > 1
        """)
        empleados_compartidos = self.cursor.fetchall()
        
        if empleados_compartidos:
            print(f"  ⚠️  {len(empleados_compartidos)} empleados están en múltiples proyectos")
            todas_ok = False
        else:
            print(f"   Sin empleados compartidos entre proyectos")
        
        return todas_ok
    
    def mostrar_resumen(self):
        """Mostrar resumen detallado"""
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL DE GENERACIÓN")
        print("="*70)
        
        tablas_info = [
            ('Cliente', 'id_cliente'),
            ('Empleado', 'id_empleado'),
            ('Equipo', 'id_equipo'),
            ('Proyecto', 'id_proyecto'),
            ('Tarea', 'id_tarea'),
            ('MiembroEquipo', 'id_miembro'),
            ('TareaEquipoHist', 'id_tarea_equipo')
        ]
        
        print("\n📦 Registros por tabla:")
        for tabla, _ in tablas_info:
            self.cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
            count = self.cursor.fetchone()['total']
            print(f"  • {tabla:20} {count:>6} registros")
        
        print("\n📈 Estadísticas por proyecto:")
        print(f"  • Clientes:           {self.stats['clientes']}")
        print(f"  • Empleados totales:  {self.stats['empleados']}")
        print(f"  • Empleados/proyecto: {EMPLEADOS_POR_PROYECTO}")
        print(f"  • Equipos:            {self.stats['equipos']}")
        print(f"  • Proyectos:          {self.stats['proyectos']}")
        print(f"  • Tareas totales:     {self.stats['tareas']}")
        print(f"  • Tareas/proyecto:    ~{self.stats['tareas']//self.stats['proyectos']}")
        
        # Distribución por estado
        print("\n📊 Proyectos por estado:")
        self.cursor.execute("""
            SELECT e.nombre_estado, COUNT(*) as cantidad,
                   ROUND(AVG(p.progreso_porcentaje), 1) as progreso_avg
            FROM Proyecto p
            JOIN Estado e ON p.id_estado = e.id_estado
            GROUP BY e.id_estado, e.nombre_estado
            ORDER BY e.id_estado
        """)
        for row in self.cursor.fetchall():
            print(f"  • {row['nombre_estado']:15} {row['cantidad']:>3} proyectos "
                  f"(progreso: {row['progreso_avg']}%)")
    
    def ejecutar(self, limpiar=True, num_proyectos=None, num_clientes=None, num_empleados=None, num_equipos=None):
        """Ejecutar el proceso completo de generación
        
        Args:
            limpiar: Si True, limpia las tablas antes de generar. Si False, agrega datos incrementalmente.
            num_proyectos: Número de proyectos a generar. Si None, usa CANTIDAD_PROYECTOS.
            num_clientes: Número de clientes a generar. Si None, usa num_proyectos (1 cliente por proyecto).
            num_empleados: Empleados por proyecto. Si None, usa EMPLEADOS_POR_PROYECTO.
            num_equipos: Equipos por proyecto. Si None, usa EQUIPOS_POR_PROYECTO.
        """
        cantidad_proyectos = num_proyectos or CANTIDAD_PROYECTOS
        cantidad_clientes = num_clientes or cantidad_proyectos  # 1 cliente por proyecto por defecto
        empleados_por_proyecto = num_empleados or EMPLEADOS_POR_PROYECTO
        equipos_por_proyecto = num_equipos or EQUIPOS_POR_PROYECTO
        
        # En modo incremental, cambiar semilla para evitar duplicados
        if not limpiar:
            import time
            nueva_semilla = int(time.time())
            Faker.seed(nueva_semilla)
            random.seed(nueva_semilla)
            print(f"🎲 Modo incremental: nueva semilla aleatoria = {nueva_semilla}")
        
        print("="*70)
        print("🚀 GENERADOR DE DATOS FINAL")
        print("="*70)
        print(f"📊 Configuración:")
        print(f"   • {cantidad_proyectos} proyectos")
        print(f"   • {cantidad_clientes} clientes")
        print(f"   • {empleados_por_proyecto} empleados por proyecto")
        print(f"   • {equipos_por_proyecto} equipo(s) por proyecto")
        print("✓ Datos únicos por proyecto")
        print("✓ Sin reutilización de empleados")
        print("✓ Sin duplicados")
        print("✓ Validación de integridad")
        if not limpiar:
            print("✓ Modo INCREMENTAL - Agregando datos sin limpiar")
        print("="*70)
        
        if not self.conectar_bd():
            return False
        
        try:
            # 1. Limpiar (solo si se solicita)
            if limpiar:
                if not self.limpiar_tablas():
                    return False
            else:
                print("\n📝 Modo incremental: omitiendo limpieza de tablas")
                # Cargar nombres existentes para evitar duplicados
                self._cargar_nombres_existentes()
            
            # Obtener offset para numeración incremental
            if limpiar:
                offset = 0
            else:
                # Usar cursor normal (sin dictionary=True) para COUNT
                cursor_count = self.conn.cursor()
                cursor_count.execute("SELECT COUNT(*) FROM Proyecto")
                offset = cursor_count.fetchone()[0]
                cursor_count.close()
                print(f"\n📊 Proyectos existentes: {offset}")
            
            # 2. Generar clientes (1 por proyecto)
            clientes_ids = self.generar_clientes(cantidad_clientes)
            
            # 3. Generar cada proyecto con su equipo exclusivo
            print(f"\n🏗️  Generando {cantidad_proyectos} proyectos completos...")
            print(f"   Cada proyecto tendrá:")
            print(f"   • {empleados_por_proyecto} empleados exclusivos")
            print(f"   • {equipos_por_proyecto} equipo(s)")
            print(f"   • ~{TAREAS_POR_PROYECTO} tareas\n")
            
            for i in range(cantidad_proyectos):
                # Usar índice con offset para evitar duplicados en nombres
                indice = offset + i
                
                # Cliente para este proyecto (cíclico si hay menos clientes que proyectos)
                id_cliente = clientes_ids[i % len(clientes_ids)]
                
                # Empleados exclusivos para este proyecto
                empleados = self.generar_empleados_por_proyecto(indice, empleados_por_proyecto)
                
                # Proyecto completo (retorna: id_proyecto, fecha_fin_real, estado)
                id_proyecto, fecha_fin_proyecto, estado_proyecto = self.generar_proyecto_base(
                    indice, id_cliente, empleados
                )
                
                # Equipo exclusivo para este proyecto (con info del proyecto)
                id_equipo = self.generar_equipo_por_proyecto(
                    indice, empleados, fecha_fin_proyecto, estado_proyecto
                )
                
                # Actualizar proyecto con el equipo y generar tareas
                self.completar_proyecto(id_proyecto, id_equipo, empleados, estado_proyecto)
                
                # Commit cada 10 proyectos
                if (i + 1) % 10 == 0:
                    self.conn.commit()
                    print(f"  ✓ {i + 1}/{cantidad_proyectos} proyectos generados...")
            
            # Commit final
            self.conn.commit()
            print(f"   {cantidad_proyectos} proyectos completados\n")
            
            # 4. Validar
            if self.validar_integridad():
                print("\n Validación exitosa - Todos los datos son únicos")
            else:
                print("\n⚠️  Algunas validaciones fallaron")
            
            # 5. Mostrar resumen
            self.mostrar_resumen()
            
            print("\n" + "="*70)
            print("🎉 ¡GENERACIÓN COMPLETADA EXITOSAMENTE!")
            print("="*70)
            print("✓ Cada proyecto tiene su propio equipo")
            print("✓ Sin duplicación de recursos")
            print("✓ Datos listos para ETL")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n Error en la generación: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False
        
        finally:
            self.cerrar_conexion()

def main():
    """Función principal"""
    generador = GeneradorDatosFinal()
    exito = generador.ejecutar()
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
