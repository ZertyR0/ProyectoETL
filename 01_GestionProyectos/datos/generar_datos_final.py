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

import os

# Cantidades configurables (con soporte de variables de entorno)
CANTIDAD_PROYECTOS = int(os.getenv('CANTIDAD_PROYECTOS', '50'))
EMPLEADOS_POR_PROYECTO = int(os.getenv('EMPLEADOS_POR_PROYECTO', '5'))
EQUIPOS_POR_PROYECTO = 1  # Cada proyecto tendrá su equipo propio
TAREAS_POR_PROYECTO = int(os.getenv('TAREAS_POR_PROYECTO', '10'))
LIMPIAR_TABLAS = os.getenv('LIMPIAR_TABLAS', 'true').lower() in ('true', '1', 'yes')

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
    
    def inicializar_estados(self):
        """Inicializar/actualizar tabla Estado con los 5 estados requeridos"""
        print("\n Verificando estados del sistema...")
        
        try:
            # Estados requeridos: 1=Planificación, 2=En Progreso, 3=En Pausa, 4=Completado, 5=Cancelado
            estados_requeridos = [
                (1, 'Planificación'),
                (2, 'En Progreso'),
                (3, 'En Pausa'),
                (4, 'Completado'),
                (5, 'Cancelado')
            ]
            
            for id_estado, nombre in estados_requeridos:
                self.cursor.execute("""
                    INSERT INTO Estado (id_estado, nombre_estado)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE 
                        nombre_estado = VALUES(nombre_estado)
                """, (id_estado, nombre))
            
            self.conn.commit()
            print("  ✓ Estados inicializados correctamente")
            return True
            
        except Exception as e:
            print(f"  ✗ Error inicializando estados: {e}")
            self.conn.rollback()
            return False
    
    def _cargar_nombres_existentes(self):
        """Cargar nombres existentes en la BD para evitar duplicados en modo incremental"""
        print(" Cargando nombres existentes para evitar duplicados...")
        
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
            
        print(f"\n Generando {cantidad} clientes (1 por proyecto)...")
        
        sectores = ['Tecnología', 'Finanzas', 'Salud', 'Educación', 'Retail', 
                   'Manufactura', 'Servicios', 'Telecomunicaciones', 'Gobierno', 'Energía']
        
        clientes_ids = []
        
        for i in range(cantidad):
            nombre = self.generar_nombre_unico('clientes', fake.company)
            sector = random.choice(sectores)
            contacto = fake.name()
            telefono = fake.phone_number()[:20]
            email = self.generar_email_unico(nombre)
            
            self.cursor.execute("""
                INSERT INTO Cliente (nombre, sector, contacto, telefono, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, sector, contacto, telefono, email))
            
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
            
            self.cursor.execute("""
                INSERT INTO Empleado (nombre, puesto)
                VALUES (%s, %s)
            """, (nombre, puesto))
            
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
            
            # Si el proyecto está completado/cancelado, fecha_hasta
            if estado_proyecto in [3, 4] and fecha_fin_proyecto:
                dias_variacion = random.randint(-5, 10)
                fecha_hasta = fecha_fin_proyecto + timedelta(days=dias_variacion)
            else:
                fecha_hasta = None
            
            self.cursor.execute("""
                INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_hasta, 
                                          rol_miembro)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_equipo, empleado['id'], fecha_inicio, fecha_hasta, rol))
            
            self.stats['asignaciones'] += 1
        
        return id_equipo
    
    def generar_proyecto_base(self, num_proyecto, id_cliente, empleados):
        """Generar un proyecto base (sin equipo ni tareas) y retornar sus datos clave
        
        Returns:
            tuple: (id_proyecto, fecha_fin_real, estado)
        """
        # Tipos de proyecto y sus posibles nombres creativos
        tipos_proyecto = [
            ('Sistema Web', ['Portal', 'Plataforma', 'Sistema', 'Aplicación Web']),
            ('Aplicación Móvil', ['App', 'Aplicación', 'Mobile App', 'Sistema Móvil']),
            ('E-commerce', ['Tienda Online', 'Marketplace', 'Portal de Ventas', 'E-Shop']),
            ('CRM', ['Sistema CRM', 'Plataforma de Clientes', 'Gestor CRM', 'Portal CRM']),
            ('ERP', ['Sistema ERP', 'Plataforma Empresarial', 'Suite Corporativa', 'Sistema Integrado']),
            ('Dashboard', ['Panel de Control', 'Dashboard Analytics', 'Portal de Métricas', 'Centro de Análisis']),
            ('API', ['API REST', 'Servicio Web', 'Microservicio', 'API Gateway']),
            ('IoT', ['Plataforma IoT', 'Sistema de Sensores', 'Hub IoT', 'Control de Dispositivos']),
        ]
        
        tipo_categoria, variantes = random.choice(tipos_proyecto)
        tipo_nombre = random.choice(variantes)
        
        # Obtener el nombre del cliente de la BD
        cursor_temp = self.conn.cursor()
        cursor_temp.execute("SELECT nombre FROM Cliente WHERE id_cliente = %s", (id_cliente,))
        result = cursor_temp.fetchone()
        cliente_nombre = result[0] if result else "Cliente"
        cursor_temp.close()
        
        # Generar nombre creativo del proyecto
        adjetivos = ['Integral', 'Avanzado', 'Corporativo', 'Digital', 'Inteligente', 'Cloud', 
                     'Empresarial', 'Automatizado', 'Optimizado', 'Moderno', 'Next-Gen']
        
        # 60% con adjetivo, 40% simple
        if random.random() < 0.6:
            nombre = self.generar_nombre_unico('proyectos', 
                lambda: f"{tipo_nombre} {random.choice(adjetivos)} {cliente_nombre.split()[0]}")
        else:
            nombre = self.generar_nombre_unico('proyectos', 
                lambda: f"{tipo_nombre} para {cliente_nombre.split()[0]}")
        
        # Generar descripción contextual basada en el tipo de proyecto
        descripciones_base = {
            'Sistema Web': [
                "Desarrollo de plataforma web escalable con arquitectura moderna",
                "Implementación de portal web responsive con gestión de contenidos",
                "Creación de sistema web empresarial con módulos integrados"
            ],
            'Aplicación Móvil': [
                "Desarrollo de aplicación móvil nativa para iOS y Android",
                "Implementación de app móvil multiplataforma con React Native",
                "Creación de aplicación móvil con integración a servicios cloud"
            ],
            'E-commerce': [
                "Desarrollo de plataforma e-commerce con pasarela de pagos",
                "Implementación de marketplace con gestión de inventarios",
                "Creación de tienda online con carrito inteligente y analytics"
            ],
            'CRM': [
                "Implementación de sistema CRM con automatización de ventas",
                "Desarrollo de plataforma de gestión de clientes y seguimiento",
                "Creación de CRM personalizado con inteligencia de negocios"
            ],
            'ERP': [
                "Implementación de sistema ERP integral para gestión empresarial",
                "Desarrollo de solución ERP modular con control financiero",
                "Creación de plataforma ERP cloud con reportería avanzada"
            ],
            'Dashboard': [
                "Desarrollo de dashboard analytics con visualización de datos",
                "Implementación de panel de control ejecutivo con KPIs",
                "Creación de centro de métricas con reportes en tiempo real"
            ],
            'API': [
                "Desarrollo de API REST con arquitectura de microservicios",
                "Implementación de servicio web escalable con documentación Swagger",
                "Creación de API Gateway con autenticación OAuth2"
            ],
            'IoT': [
                "Desarrollo de plataforma IoT para monitoreo de sensores",
                "Implementación de hub IoT con gestión de dispositivos",
                "Creación de sistema de control IoT con analytics predictivo"
            ]
        }
        
        # Seleccionar descripción base según categoría
        desc_base = random.choice(descripciones_base.get(tipo_categoria, [
            "Desarrollo de solución tecnológica empresarial",
            "Implementación de sistema digital corporativo"
        ]))
        
        # Agregar detalles contextuales
        detalles = [
            "con enfoque en experiencia de usuario",
            "orientado a optimización de procesos",
            "con integración a sistemas legacy",
            "utilizando tecnologías de vanguardia",
            "con soporte 24/7 y documentación completa",
            "incluyendo capacitación y transferencia de conocimiento",
            "con garantía de calidad y pruebas exhaustivas"
        ]
        
        descripcion = f"{desc_base}, {random.choice(detalles)}."
        
        # Fechas del proyecto - RANGO AMPLIADO: 2020-2026 (6 años de historia)
        # Distribución: 40% histórico (2020-2023), 35% reciente (2024-2025), 25% futuro (2025-2026)
        rand_tiempo = random.random()
        if rand_tiempo < 0.40:  # 40% proyectos históricos
            fecha_inicio = fake.date_between(start_date=date(2020, 1, 1), end_date=date(2023, 12, 31))
        elif rand_tiempo < 0.75:  # 35% proyectos recientes
            fecha_inicio = fake.date_between(start_date=date(2024, 1, 1), end_date=date(2025, 10, 31))
        else:  # 25% proyectos futuros/actuales
            fecha_inicio = fake.date_between(start_date=date(2025, 11, 1), end_date=date(2026, 6, 30))
        
        duracion_plan = random.randint(60, 180)
        fecha_fin_plan = fecha_inicio + timedelta(days=duracion_plan)
        
        # Distribución realista de estados:
        # 35% Completado (4) - proyectos finalizados exitosamente
        # 10% Cancelado (5) - proyectos cancelados
        # 25% En Progreso (2) - proyectos activos
        # 20% Planificación (1) - proyectos iniciando
        # 10% En Pausa (3) - proyectos pausados
        rand_estado = random.random()
        if rand_estado < 0.35:
            estado = 4  # Completado
            variacion = random.randint(-15, 30)
            fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
        elif rand_estado < 0.45:
            estado = 5  # Cancelado
            # Cancelado antes de terminar
            dias_transcurridos = random.randint(30, duracion_plan - 10)
            fecha_fin_real = fecha_inicio + timedelta(days=dias_transcurridos)
        elif rand_estado < 0.70:
            estado = 2  # En Progreso
            fecha_fin_real = None
        elif rand_estado < 0.90:
            estado = 1  # Planificación
            fecha_fin_real = None
        else:
            estado = 3  # En Pausa
            fecha_fin_real = None
        
        presupuesto = random.randint(100000, 800000)
        
        # Costo real según estado:
        # - Completado: 80-120% del presupuesto
        # - Cancelado: 30-70% del presupuesto (gasto parcial)
        # - En Progreso: 20-80% del presupuesto (avance parcial)
        # - En Pausa: 10-50% del presupuesto (algo ejecutado antes de pausar)
        # - Planificación: 0-10% del presupuesto (costos iniciales mínimos)
        if estado == 4:  # Completado
            costo_real = int(presupuesto * random.uniform(0.80, 1.20))
        elif estado == 5:  # Cancelado
            costo_real = int(presupuesto * random.uniform(0.30, 0.70))
        elif estado == 2:  # En Progreso
            costo_real = int(presupuesto * random.uniform(0.20, 0.80))
        elif estado == 3:  # En Pausa
            costo_real = int(presupuesto * random.uniform(0.10, 0.50))
        else:  # Planificación
            costo_real = int(presupuesto * random.uniform(0.0, 0.10))
        
        # Gerente del proyecto (el primer empleado con puesto de gerente)
        gerente = next((e for e in empleados if e['es_gerente']), empleados[0])
        
        # Insertar proyecto
        self.cursor.execute("""
            INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, 
                                fecha_fin_real, presupuesto, costo_real, id_cliente, 
                                id_estado, id_empleado_gerente)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
              presupuesto, costo_real, id_cliente, estado, gerente['id']))
        
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
            
            # Estado de la tarea coherente con el proyecto:
            # 1=Planificación, 2=En Progreso, 3=En Pausa, 4=Completado, 5=Cancelado
            if estado_proyecto == 4:  # Proyecto Completado
                # La mayoría de tareas completadas, algunas canceladas
                estado = random.choices([4, 5], weights=[85, 15])[0]
                fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 3))
                variacion = random.randint(-3, 7)
                fecha_fin_real = fecha_fin_plan + timedelta(days=variacion)
            elif estado_proyecto == 5:  # Proyecto Cancelado
                # Mix de estados (algunas completadas antes de cancelar)
                estado = random.choices([4, 5, 2, 3], weights=[30, 40, 20, 10])[0]
                if estado in [4, 5]:  # Completada o cancelada
                    fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 3))
                    fecha_fin_real = fecha_fin_plan + timedelta(days=random.randint(-3, 7))
                else:
                    fecha_inicio_real = fecha_inicio_plan if estado == 2 else None
                    fecha_fin_real = None
            elif estado_proyecto == 2:  # Proyecto En Progreso
                # Mix de estados activos
                estado = random.choices([4, 2, 1], weights=[40, 50, 10])[0]
                if estado == 4:  # Algunas ya completadas
                    fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 3))
                    fecha_fin_real = fecha_fin_plan + timedelta(days=random.randint(-3, 7))
                elif estado == 2:  # En progreso
                    fecha_inicio_real = fecha_inicio_plan
                    fecha_fin_real = None
                else:  # Planificación
                    fecha_inicio_real = None
                    fecha_fin_real = None
            elif estado_proyecto == 3:  # Proyecto En Pausa
                # Tareas pausadas o algunas completadas antes
                estado = random.choices([3, 4, 2], weights=[60, 30, 10])[0]
                if estado == 4:
                    fecha_inicio_real = fecha_inicio_plan + timedelta(days=random.randint(-2, 3))
                    fecha_fin_real = fecha_fin_plan + timedelta(days=random.randint(-3, 7))
                else:
                    fecha_inicio_real = fecha_inicio_plan if estado == 2 else None
                    fecha_fin_real = None
            else:  # Proyecto en Planificación (1)
                estado = 1
                fecha_inicio_real = None
                fecha_fin_real = None
            
            horas_plan = random.randint(16, 120)
            # Horas reales según estado de la tarea
            if estado == 4:  # Completado
                horas_reales = horas_plan + random.randint(-10, 30)
            elif estado == 5:  # Cancelado
                horas_reales = int(horas_plan * random.uniform(0.3, 0.8))
            elif estado == 2:  # En Progreso
                horas_reales = int(horas_plan * random.uniform(0.2, 0.7))
            elif estado == 3:  # En Pausa
                horas_reales = int(horas_plan * random.uniform(0.1, 0.5))
            else:  # Planificación
                horas_reales = 0
            
            self.cursor.execute("""
                INSERT INTO Tarea (nombre_tarea, fecha_inicio_plan, fecha_fin_plan,
                                 fecha_fin_real, horas_plan, horas_reales,
                                 id_proyecto, id_estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre_completo, fecha_inicio_plan, fecha_fin_plan,
                  fecha_fin_real, horas_plan, horas_reales,
                  id_proyecto, estado))
            
            id_tarea = self.cursor.lastrowid
            self.stats['tareas'] += 1
            
            # Asignar tarea al equipo del proyecto (CRITICAL)
            fecha_asignacion = fecha_inicio_plan
            fecha_liberacion = fecha_fin_real if estado in [3, 4] else None
            
            self.cursor.execute("""
                INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, 
                                            fecha_liberacion)
                VALUES (%s, %s, %s, %s)
            """, (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion))
    
    def validar_integridad(self):
        """Validar integridad y unicidad de los datos"""
        print("\n Validando integridad...")
        
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
        
        return todas_ok
    
    def mostrar_resumen(self):
        """Mostrar resumen detallado"""
        print("\n" + "="*70)
        print(" RESUMEN FINAL DE GENERACIÓN")
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
        
        print("\n Estadísticas por proyecto:")
        print(f"  • Clientes:           {self.stats['clientes']}")
        print(f"  • Empleados totales:  {self.stats['empleados']}")
        print(f"  • Empleados/proyecto: {EMPLEADOS_POR_PROYECTO}")
        print(f"  • Equipos:            {self.stats['equipos']}")
        print(f"  • Proyectos:          {self.stats['proyectos']}")
        print(f"  • Tareas totales:     {self.stats['tareas']}")
        print(f"  • Tareas/proyecto:    ~{self.stats['tareas']//self.stats['proyectos']}")
        
        # Distribución por estado
        print("\n Proyectos por estado:")
        self.cursor.execute("""
            SELECT e.nombre_estado, COUNT(*) as cantidad
            FROM Proyecto p
            JOIN Estado e ON p.id_estado = e.id_estado
            GROUP BY e.id_estado, e.nombre_estado
            ORDER BY e.id_estado
        """)
        for row in self.cursor.fetchall():
            print(f"  • {row['nombre_estado']:15} {row['cantidad']:>3} proyectos")
    
    def generar_metricas_calidad(self):
        """Generar defectos para proyectos completados"""
        print("\n5. Generando métricas de calidad (defectos)...")
        
        # Obtener proyectos completados
        self.cursor.execute("""
            SELECT id_proyecto, fecha_inicio, fecha_fin_real 
            FROM proyecto 
            WHERE id_estado IN (4, 5) AND fecha_fin_real IS NOT NULL
        """)
        proyectos = self.cursor.fetchall()
        
        total_defectos = 0
        for row in proyectos:
            id_proyecto = row['id_proyecto']
            fecha_inicio = row['fecha_inicio']
            fecha_fin = row['fecha_fin_real']
            
            # Generar entre 2 y 8 defectos por proyecto
            num_defectos = random.randint(2, 8)
            
            for _ in range(num_defectos):
                severidad = random.choices(
                    ['Baja', 'Media', 'Alta', 'Crítica'],
                    weights=[40, 35, 20, 5]
                )[0]
                
                fecha_reporte = fecha_inicio + timedelta(days=random.randint(5, 60))
                estado = random.choices(
                    ['Resuelto', 'Cerrado', 'Abierto'],
                    weights=[60, 30, 10]
                )[0]
                
                fecha_resolucion = None
                if estado in ['Resuelto', 'Cerrado']:
                    fecha_resolucion = fecha_reporte + timedelta(days=random.randint(1, 15))
                
                self.cursor.execute("""
                    INSERT INTO defecto (id_proyecto, descripcion, severidad, fecha_reporte, fecha_resolucion, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_proyecto, f"Defecto {severidad} en proyecto", severidad, fecha_reporte, fecha_resolucion, estado))
                total_defectos += 1
        
        self.conn.commit()
        print(f"   {total_defectos} defectos generados")
    
    def generar_capacitaciones(self):
        """Generar capacitaciones para empleados"""
        print("\n6. Generando capacitaciones de empleados...")
        
        self.cursor.execute("SELECT id_empleado FROM empleado")
        empleados = [row['id_empleado'] for row in self.cursor.fetchall()]
        
        cursos = [
            'Metodologías Ágiles', 'Gestión de Proyectos', 'Liderazgo',
            'Comunicación Efectiva', 'Excel Avanzado', 'Power BI',
            'Python para Análisis', 'SQL Avanzado', 'Scrum Master'
        ]
        
        total_capacitaciones = 0
        for id_empleado in empleados:
            # 70% de empleados tienen al menos una capacitación
            if random.random() < 0.7:
                num_cursos = random.randint(1, 3)
                for _ in range(num_cursos):
                    curso = random.choice(cursos)
                    horas = random.choice([8, 16, 24, 40])
                    fecha_inicio = date.today() - timedelta(days=random.randint(30, 365))
                    fecha_fin = fecha_inicio + timedelta(days=horas//8)
                    estado = random.choices(
                        ['Completada', 'En Curso', 'Planificada'],
                        weights=[70, 20, 10]
                    )[0]
                    
                    self.cursor.execute("""
                        INSERT INTO capacitacion (id_empleado, nombre_curso, horas_duracion, fecha_inicio, fecha_fin, estado)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (id_empleado, curso, horas, fecha_inicio, fecha_fin, estado))
                    total_capacitaciones += 1
        
        self.conn.commit()
        print(f"   {total_capacitaciones} capacitaciones generadas")
    
    def generar_satisfaccion_cliente(self):
        """Generar evaluaciones de satisfacción por proyecto completado"""
        print("\n7. Generando satisfacción de clientes...")
        
        self.cursor.execute("""
            SELECT p.id_proyecto, p.id_cliente, p.fecha_fin_real
            FROM proyecto p
            WHERE p.id_estado IN (4, 5) AND p.fecha_fin_real IS NOT NULL
        """)
        proyectos = self.cursor.fetchall()
        
        total_evaluaciones = 0
        for row in proyectos:
            id_proyecto = row['id_proyecto']
            id_cliente = row['id_cliente']
            fecha_fin = row['fecha_fin_real']
            
            # 80% de proyectos tienen evaluación
            if random.random() < 0.8:
                # Distribución realista de calificaciones (sesgo positivo)
                calificacion = round(random.uniform(3.5, 5.0), 2)
                fecha_evaluacion = fecha_fin + timedelta(days=random.randint(1, 7))
                
                self.cursor.execute("""
                    INSERT INTO satisfaccion_cliente (id_proyecto, id_cliente, calificacion, fecha_evaluacion)
                    VALUES (%s, %s, %s, %s)
                """, (id_proyecto, id_cliente, calificacion, fecha_evaluacion))
                total_evaluaciones += 1
        
        self.conn.commit()
        print(f"   {total_evaluaciones} evaluaciones generadas")
    
    def generar_movimientos_empleados(self):
        """Generar movimientos de empleados (ingresos/egresos)"""
        print("\n8. Generando movimientos de empleados...")
        
        self.cursor.execute("SELECT id_empleado FROM empleado")
        empleados = [row['id_empleado'] for row in self.cursor.fetchall()]
        
        total_movimientos = 0
        # Registrar ingresos de todos los empleados
        for id_empleado in empleados:
            fecha_ingreso = date.today() - timedelta(days=random.randint(180, 1095))
            self.cursor.execute("""
                INSERT INTO movimiento_empleado (id_empleado, tipo_movimiento, fecha_movimiento, motivo)
                VALUES (%s, 'Ingreso', %s, 'Contratación')
            """, (id_empleado, fecha_ingreso))
            total_movimientos += 1
            
            # 12% de rotación - algunos empleados han egresado
            if random.random() < 0.12:
                fecha_egreso = fecha_ingreso + timedelta(days=random.randint(90, 365))
                motivos = ['Renuncia voluntaria', 'Mejor oportunidad', 'Fin de contrato', 'Despido']
                self.cursor.execute("""
                    INSERT INTO movimiento_empleado (id_empleado, tipo_movimiento, fecha_movimiento, motivo)
                    VALUES (%s, 'Egreso', %s, %s)
                """, (id_empleado, fecha_egreso, random.choice(motivos)))
                total_movimientos += 1
        
        self.conn.commit()
        print(f"   {total_movimientos} movimientos registrados")
    
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
        print(" GENERADOR DE DATOS FINAL")
        print("="*70)
        print(f" Configuración:")
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
            # 0. Inicializar/verificar estados (SIEMPRE, antes de cualquier operación)
            if not self.inicializar_estados():
                return False
            
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
                print(f"\n Proyectos existentes: {offset}")
            
            # 2. Generar clientes (15-20 clientes para 50 proyectos = 2-4 proyectos por cliente)
            # Esto hace más realista: un cliente grande tiene varios proyectos
            num_clientes = max(12, cantidad_clientes // 3)  # ~17 clientes para 50 proyectos
            clientes_ids = self.generar_clientes(num_clientes)
            
            # 3. Generar cada proyecto con su equipo exclusivo
            print(f"\n Generando {cantidad_proyectos} proyectos completos...")
            print(f"   Distribuidos entre {num_clientes} clientes (~{cantidad_proyectos//num_clientes} proyectos/cliente)")
            print(f"   Cada proyecto tendrá:")
            print(f"   • {empleados_por_proyecto} empleados exclusivos")
            print(f"   • {equipos_por_proyecto} equipo(s)")
            print(f"   • ~{TAREAS_POR_PROYECTO} tareas\n")
            
            for i in range(cantidad_proyectos):
                # Usar índice con offset para evitar duplicados en nombres
                indice = offset + i
                
                # Cliente para este proyecto (cíclico con distribución uniforme)
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
            
            # 4. Generar métricas adicionales
            self.generar_metricas_calidad()
            self.generar_capacitaciones()
            self.generar_satisfaccion_cliente()
            self.generar_movimientos_empleados()
            
            # 5. Validar
            if self.validar_integridad():
                print("\n Validación exitosa - Todos los datos son únicos")
            else:
                print("\n⚠️  Algunas validaciones fallaron")
            
            # 5. Mostrar resumen
            self.mostrar_resumen()
            
            print("\n" + "="*70)
            print(" ¡GENERACIÓN COMPLETADA EXITOSAMENTE!")
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
    # Usar variable de entorno LIMPIAR_TABLAS
    exito = generador.ejecutar(limpiar=LIMPIAR_TABLAS)
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
