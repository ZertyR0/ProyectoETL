#!/usr/bin/env python3
"""
ETL Principal - Sistema de Gestión de Proyectos
Proceso completo de Extract, Transform, Load
"""

import sys
import os
from pathlib import Path

# Agregar el directorio config al path
sys.path.append(str(Path(__file__).parent.parent / 'config'))

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime, date, timedelta
import logging

# Importar configuraciones y utilidades
from config_conexion import get_config, get_connection_string
from etl_utils import (
    configurar_logging, validar_dataframe, limpiar_datos,
    calcular_diferencia_dias, calcular_cumplimiento_tiempo,
    calcular_cumplimiento_presupuesto, crear_dimension_tiempo,
    obtener_id_tiempo, generar_metricas_proyecto, 
    formatear_salida_consola, ETLStats
)

class ETLProyectos:
    """Clase principal para el proceso ETL"""
    
    def __init__(self, ambiente='local'):
        self.ambiente = ambiente
        self.config = get_config(ambiente)
        self.stats = ETLStats()
        self.logger = configurar_logging('INFO')
        
        # Engines de base de datos
        self.engine_origen = None
        self.engine_destino = None
        
        # DataFrames para dimensiones
        self.dim_tiempo = None
        
        print(formatear_salida_consola(f"ETL inicializado - Ambiente: {ambiente}", 'info'))
    
    def conectar_bases_datos(self):
        """Establecer conexiones a las bases de datos"""
        try:
            print(formatear_salida_consola("Conectando a bases de datos...", 'proceso'))
            
            # Conexión origen
            conn_str_origen = get_connection_string('origen', self.ambiente)
            self.engine_origen = create_engine(conn_str_origen, pool_pre_ping=True)
            
            # Conexión destino
            conn_str_destino = get_connection_string('destino', self.ambiente)
            self.engine_destino = create_engine(conn_str_destino, pool_pre_ping=True)
            
            # Probar conexiones
            with self.engine_origen.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            with self.engine_destino.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print(formatear_salida_consola("Conexiones establecidas exitosamente", 'success'))
            return True
            
        except Exception as e:
            error_msg = f"Error conectando a bases de datos: {e}"
            print(formatear_salida_consola(error_msg, 'error'))
            self.stats.agregar_error(error_msg)
            return False
    
    def extraer_datos_origen(self):
        """Extraer datos de la base de datos origen"""
        try:
            print(formatear_salida_consola("Extrayendo datos de origen...", 'proceso'))
            
            # Extraer clientes
            self.df_clientes = pd.read_sql("""
                SELECT id_cliente, nombre, sector, contacto, telefono, email, 
                       direccion, fecha_registro, activo
                FROM Cliente 
                WHERE activo = 1
            """, self.engine_origen)
            
            # Extraer empleados
            self.df_empleados = pd.read_sql("""
                SELECT id_empleado, nombre, puesto, departamento, salario_base, 
                       fecha_ingreso, activo
                FROM Empleado 
                WHERE activo = 1
            """, self.engine_origen)
            
            # Extraer equipos
            self.df_equipos = pd.read_sql("""
                SELECT id_equipo, nombre_equipo, descripcion, fecha_creacion, activo
                FROM Equipo 
                WHERE activo = 1
            """, self.engine_origen)
            
            # Extraer proyectos (solo completados o cancelados para el datawarehouse)
            self.df_proyectos = pd.read_sql("""
                SELECT p.*, c.nombre as nombre_cliente, e.nombre as nombre_gerente,
                       est.nombre_estado
                FROM Proyecto p
                LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
                LEFT JOIN Empleado e ON p.id_empleado_gerente = e.id_empleado
                LEFT JOIN Estado est ON p.id_estado = est.id_estado
                WHERE p.id_estado IN (3, 4)  -- 3=Completado, 4=Cancelado
            """, self.engine_origen)
            
            # Extraer tareas (solo de proyectos completados o cancelados)
            self.df_tareas = pd.read_sql("""
                SELECT t.*, p.nombre as nombre_proyecto, e.nombre as nombre_empleado,
                       est.nombre_estado
                FROM Tarea t
                LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
                LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
                LEFT JOIN Estado est ON t.id_estado = est.id_estado
                WHERE p.id_estado IN (3, 4)  -- Solo tareas de proyectos completados o cancelados
            """, self.engine_origen)
            
            # Validar extracciones
            validaciones = [
                (self.df_clientes, "Clientes", ['id_cliente', 'nombre']),
                (self.df_empleados, "Empleados", ['id_empleado', 'nombre']),
                (self.df_equipos, "Equipos", ['id_equipo', 'nombre_equipo']),
                (self.df_proyectos, "Proyectos", ['id_proyecto', 'nombre']),
                (self.df_tareas, "Tareas", ['id_tarea', 'nombre_tarea'])
            ]
            
            for df, nombre, columnas in validaciones:
                if not validar_dataframe(df, nombre, columnas):
                    return False
            
            print(formatear_salida_consola("Extracción completada exitosamente", 'success'))
            return True
            
        except Exception as e:
            error_msg = f"Error en extracción: {e}"
            print(formatear_salida_consola(error_msg, 'error'))
            self.stats.agregar_error(error_msg)
            return False
    
    def transformar_datos(self):
        """Transformar y limpiar los datos extraídos"""
        try:
            print(formatear_salida_consola("Transformando datos...", 'proceso'))
            
            # Limpiar datos básicos
            self.df_clientes = limpiar_datos(self.df_clientes)
            self.df_empleados = limpiar_datos(self.df_empleados)
            self.df_equipos = limpiar_datos(self.df_equipos)
            self.df_proyectos = limpiar_datos(self.df_proyectos)
            self.df_tareas = limpiar_datos(self.df_tareas)
            
            # Crear dimensión tiempo
            self.crear_dimension_tiempo()
            
            # Preparar dimensiones
            self.preparar_dimensiones()
            
            # Preparar hechos
            self.preparar_hechos()
            
            print(formatear_salida_consola("Transformación completada", 'success'))
            return True
            
        except Exception as e:
            error_msg = f"Error en transformación: {e}"
            print(formatear_salida_consola(error_msg, 'error'))
            self.stats.agregar_error(error_msg)
            return False
    
    def crear_dimension_tiempo(self):
        """Crear la dimensión tiempo basada en las fechas de los datos"""
        try:
            # Encontrar rango de fechas
            fechas_proyectos = pd.concat([
                self.df_proyectos['fecha_inicio'].dropna(),
                self.df_proyectos['fecha_fin_plan'].dropna(),
                self.df_proyectos['fecha_fin_real'].dropna()
            ])
            
            fechas_tareas = pd.concat([
                self.df_tareas['fecha_inicio_plan'].dropna(),
                self.df_tareas['fecha_fin_plan'].dropna(),
                self.df_tareas['fecha_inicio_real'].dropna(),
                self.df_tareas['fecha_fin_real'].dropna()
            ])
            
            todas_fechas = pd.concat([fechas_proyectos, fechas_tareas]).dropna()
            
            if not todas_fechas.empty:
                fecha_min = todas_fechas.min().date()
                fecha_max = todas_fechas.max().date()
                
                # Extender rango para incluir contexto
                fecha_min = fecha_min - timedelta(days=365)
                fecha_max = fecha_max + timedelta(days=365)
            else:
                # Fechas por defecto si no hay datos
                fecha_min = date.today() - timedelta(days=1095)  # 3 años atrás
                fecha_max = date.today() + timedelta(days=365)   # 1 año adelante
            
            self.dim_tiempo = crear_dimension_tiempo(fecha_min, fecha_max)
            
            print(formatear_salida_consola(
                f"Dimensión tiempo creada: {len(self.dim_tiempo)} registros ({fecha_min} a {fecha_max})", 
                'datos'
            ))
            
        except Exception as e:
            self.stats.agregar_error(f"Error creando dimensión tiempo: {e}")
            # Crear dimensión mínima como fallback
            hoy = date.today()
            self.dim_tiempo = crear_dimension_tiempo(
                hoy - timedelta(days=365), 
                hoy + timedelta(days=365)
            )
    
    def preparar_dimensiones(self):
        """Preparar DataFrames de dimensiones para carga"""
        
        # DimCliente
        self.dim_cliente = self.df_clientes[[
            'id_cliente', 'nombre', 'sector', 'contacto', 
            'telefono', 'email', 'direccion', 'fecha_registro', 'activo'
        ]].copy()
        
        # DimEmpleado
        self.dim_empleado = self.df_empleados[[
            'id_empleado', 'nombre', 'puesto', 'departamento', 
            'salario_base', 'fecha_ingreso', 'activo'
        ]].copy()
        
        # DimEquipo
        self.dim_equipo = self.df_equipos[[
            'id_equipo', 'nombre_equipo', 'descripcion', 
            'fecha_creacion', 'activo'
        ]].copy()
        
        # DimProyecto
        self.dim_proyecto = self.df_proyectos[[
            'id_proyecto', 'nombre', 'descripcion', 'fecha_inicio', 
            'fecha_fin_plan', 'presupuesto', 'prioridad'
        ]].copy()
        self.dim_proyecto.rename(columns={'nombre': 'nombre_proyecto', 'presupuesto': 'presupuesto_plan'}, inplace=True)
    
    def preparar_hechos(self):
        """Preparar tablas de hechos con métricas calculadas"""
        
        # Generar métricas para proyectos
        df_proyectos_con_metricas = generar_metricas_proyecto(self.df_proyectos, self.df_tareas)
        
        # Preparar HechoProyecto
        self.preparar_hecho_proyecto(df_proyectos_con_metricas)
        
        # Preparar HechoTarea
        self.preparar_hecho_tarea()
    
    def preparar_hecho_proyecto(self, df_proyectos):
        """Preparar tabla de hechos de proyectos"""
        
        self.hecho_proyecto = df_proyectos.copy()
        
        # Calcular métricas de tiempo
        self.hecho_proyecto['duracion_planificada'] = calcular_diferencia_dias(
            self.hecho_proyecto['fecha_inicio'], 
            self.hecho_proyecto['fecha_fin_plan']
        )
        
        self.hecho_proyecto['duracion_real'] = calcular_diferencia_dias(
            self.hecho_proyecto['fecha_inicio'], 
            self.hecho_proyecto['fecha_fin_real']
        )
        
        self.hecho_proyecto['variacion_cronograma'] = (
            self.hecho_proyecto['duracion_real'] - self.hecho_proyecto['duracion_planificada']
        )
        
        # Calcular cumplimientos
        self.hecho_proyecto['cumplimiento_tiempo'] = calcular_cumplimiento_tiempo(
            self.hecho_proyecto['fecha_fin_plan'],
            self.hecho_proyecto['fecha_fin_real']
        )
        
        self.hecho_proyecto['cumplimiento_presupuesto'] = calcular_cumplimiento_presupuesto(
            self.hecho_proyecto['presupuesto'],
            self.hecho_proyecto['costo_real']
        )
        
        # Calcular métricas financieras
        self.hecho_proyecto['variacion_costos'] = (
            self.hecho_proyecto['costo_real'] - self.hecho_proyecto['presupuesto']
        )
        
        self.hecho_proyecto['porcentaje_sobrecosto'] = np.where(
            self.hecho_proyecto['presupuesto'] > 0,
            (self.hecho_proyecto['variacion_costos'] / self.hecho_proyecto['presupuesto']) * 100,
            0
        )
        
        # Calcular métricas de trabajo
        self.hecho_proyecto['porcentaje_completado'] = np.where(
            self.hecho_proyecto['tareas_total'] > 0,
            (self.hecho_proyecto['tareas_completadas'] / self.hecho_proyecto['tareas_total']) * 100,
            0
        )
        
        # Calcular eficiencia de horas
        self.hecho_proyecto['eficiencia_horas'] = np.where(
            self.hecho_proyecto['horas_estimadas_total'] > 0,
            (self.hecho_proyecto['horas_estimadas_total'] / self.hecho_proyecto['horas_reales_total']) * 100,
            0
        )
        
        # Obtener IDs de tiempo
        self.hecho_proyecto = self.agregar_ids_tiempo(self.hecho_proyecto, [
            'fecha_inicio', 'fecha_fin_plan', 'fecha_fin_real'
        ], ['id_tiempo_inicio', 'id_tiempo_fin_plan', 'id_tiempo_fin_real'])
        
        # Seleccionar columnas finales
        columnas_hecho = [
            'id_proyecto', 'id_cliente', 'id_empleado_gerente',
            'id_tiempo_inicio', 'id_tiempo_fin_plan', 'id_tiempo_fin_real',
            'duracion_planificada', 'duracion_real', 'variacion_cronograma', 'cumplimiento_tiempo',
            'presupuesto', 'costo_real', 'variacion_costos', 'cumplimiento_presupuesto', 'porcentaje_sobrecosto',
            'tareas_total', 'tareas_completadas', 'tareas_canceladas', 'tareas_pendientes', 'porcentaje_completado',
            'horas_estimadas_total', 'horas_reales_total', 'variacion_horas', 'eficiencia_horas'
        ]
        
        # Filtrar solo columnas que existen
        columnas_existentes = [col for col in columnas_hecho if col in self.hecho_proyecto.columns]
        self.hecho_proyecto = self.hecho_proyecto[columnas_existentes]
    
    def preparar_hecho_tarea(self):
        """Preparar tabla de hechos de tareas"""
        
        self.hecho_tarea = self.df_tareas.copy()
        
        # Calcular métricas de tiempo
        self.hecho_tarea['duracion_planificada'] = calcular_diferencia_dias(
            self.hecho_tarea['fecha_inicio_plan'], 
            self.hecho_tarea['fecha_fin_plan']
        )
        
        self.hecho_tarea['duracion_real'] = calcular_diferencia_dias(
            self.hecho_tarea['fecha_inicio_real'], 
            self.hecho_tarea['fecha_fin_real']
        )
        
        self.hecho_tarea['variacion_cronograma'] = (
            self.hecho_tarea['duracion_real'] - self.hecho_tarea['duracion_planificada']
        )
        
        # Calcular cumplimiento
        self.hecho_tarea['cumplimiento_tiempo'] = calcular_cumplimiento_tiempo(
            self.hecho_tarea['fecha_fin_plan'],
            self.hecho_tarea['fecha_fin_real']
        )
        
        # Calcular métricas de trabajo
        self.hecho_tarea['variacion_horas'] = (
            self.hecho_tarea['horas_reales'] - self.hecho_tarea['horas_plan']
        )
        
        self.hecho_tarea['eficiencia_horas'] = np.where(
            self.hecho_tarea['horas_plan'] > 0,
            (self.hecho_tarea['horas_plan'] / self.hecho_tarea['horas_reales']) * 100,
            0
        )
        
        # Calcular métricas financieras
        self.hecho_tarea['variacion_costo'] = (
            self.hecho_tarea['costo_real'] - self.hecho_tarea['costo_estimado']
        )
        
        # Obtener IDs de tiempo
        self.hecho_tarea = self.agregar_ids_tiempo(self.hecho_tarea, [
            'fecha_inicio_plan', 'fecha_fin_plan', 'fecha_inicio_real', 'fecha_fin_real'
        ], ['id_tiempo_inicio_plan', 'id_tiempo_fin_plan', 'id_tiempo_inicio_real', 'id_tiempo_fin_real'])
        
        # Seleccionar columnas finales
        columnas_hecho = [
            'id_tarea', 'id_proyecto', 'id_empleado',
            'id_tiempo_inicio_plan', 'id_tiempo_fin_plan', 'id_tiempo_inicio_real', 'id_tiempo_fin_real',
            'duracion_planificada', 'duracion_real', 'variacion_cronograma', 'cumplimiento_tiempo',
            'horas_plan', 'horas_reales', 'variacion_horas', 'eficiencia_horas',
            'costo_estimado', 'costo_real', 'variacion_costo',
            'progreso_porcentaje'
        ]
        
        # Renombrar para coincidir con esquema del DW
        self.hecho_tarea.rename(columns={'costo_estimado': 'costo_real_tarea'}, inplace=True)
        
        # Filtrar solo columnas que existen
        columnas_existentes = [col for col in columnas_hecho if col in self.hecho_tarea.columns]
        self.hecho_tarea = self.hecho_tarea[columnas_existentes]
    
    def agregar_ids_tiempo(self, df, columnas_fecha, columnas_id):
        """Agregar IDs de tiempo al DataFrame"""
        df_resultado = df.copy()
        
        for col_fecha, col_id in zip(columnas_fecha, columnas_id):
            if col_fecha in df_resultado.columns:
                # Convertir fechas a IDs, manteniendo NULL para fechas vacías
                df_resultado[col_id] = df_resultado[col_fecha].apply(
                    lambda fecha: obtener_id_tiempo(fecha.date() if pd.notna(fecha) else None, self.dim_tiempo)
                )
                # Asegurar que los NULL se mantengan como None en vez de 0.0
                df_resultado[col_id] = df_resultado[col_id].where(pd.notna(df_resultado[col_id]), None)
            else:
                df_resultado[col_id] = None
        
        return df_resultado
    
    def cargar_datos(self):
        """Cargar datos transformados al datawarehouse"""
        try:
            print(formatear_salida_consola("Cargando datos al datawarehouse...", 'proceso'))
            
            # Limpiar tablas de destino
            self.limpiar_datawarehouse()
            
            # Cargar dimensión tiempo
            self.cargar_tabla(self.dim_tiempo, 'DimTiempo', 'Dimensión Tiempo')
            
            # Cargar dimensiones
            self.cargar_tabla(self.dim_cliente, 'DimCliente', 'Dimensión Cliente')
            self.cargar_tabla(self.dim_empleado, 'DimEmpleado', 'Dimensión Empleado')
            self.cargar_tabla(self.dim_equipo, 'DimEquipo', 'Dimensión Equipo')
            self.cargar_tabla(self.dim_proyecto, 'DimProyecto', 'Dimensión Proyecto')
            
            # Cargar hechos
            self.cargar_tabla(self.hecho_proyecto, 'HechoProyecto', 'Hechos Proyecto')
            self.cargar_tabla(self.hecho_tarea, 'HechoTarea', 'Hechos Tarea')
            
            print(formatear_salida_consola("Carga completada exitosamente", 'success'))
            return True
            
        except Exception as e:
            error_msg = f"Error en carga: {e}"
            print(formatear_salida_consola(error_msg, 'error'))
            self.stats.agregar_error(error_msg)
            return False
    
    def limpiar_datawarehouse(self):
        """Limpiar tablas del datawarehouse antes de cargar"""
        tablas = ['HechoTarea', 'HechoProyecto', 'DimTiempo', 'DimProyecto', 'DimEquipo', 'DimEmpleado', 'DimCliente']
        
        with self.engine_destino.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            for tabla in tablas:
                try:
                    conn.execute(text(f"DELETE FROM {tabla}"))
                    conn.execute(text(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1"))
                except Exception as e:
                    self.stats.agregar_warning(f"No se pudo limpiar tabla {tabla}: {e}")
            
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()
    
    def cargar_tabla(self, df, nombre_tabla, descripcion):
        """Cargar un DataFrame a una tabla específica"""
        try:
            if df is not None and not df.empty:
                # Rellenar valores nulos según el tipo de columna
                df_carga = df.copy()
                
                # Rellenar valores nulos
                for col in df_carga.columns:
                    if df_carga[col].dtype in ['object']:
                        df_carga[col] = df_carga[col].fillna('')
                    elif df_carga[col].dtype in ['int64', 'float64']:
                        df_carga[col] = df_carga[col].fillna(0)
                    elif df_carga[col].dtype == 'datetime64[ns]':
                        # Mantener nulos para fechas
                        pass
                
                # Cargar datos
                registros_cargados = df_carga.to_sql(
                    nombre_tabla, 
                    self.engine_destino, 
                    if_exists='append', 
                    index=False,
                    method='multi',
                    chunksize=1000
                )
                
                self.stats.agregar_procesados(nombre_tabla, len(df_carga))
                print(formatear_salida_consola(
                    f"{descripcion}: {len(df_carga)} registros cargados", 
                    'datos'
                ))
                
            else:
                self.stats.agregar_warning(f"{descripcion}: No hay datos para cargar")
                
        except Exception as e:
            error_msg = f"Error cargando {descripcion}: {e}"
            self.stats.agregar_error(error_msg)
            print(formatear_salida_consola(error_msg, 'error'))
    
    def ejecutar_etl_completo(self):
        """Ejecutar el proceso ETL completo"""
        print(formatear_salida_consola("Iniciando proceso ETL completo", 'info'))
        print("=" * 60)
        
        # Paso 1: Conectar
        if not self.conectar_bases_datos():
            return False
        
        # Paso 2: Extraer
        if not self.extraer_datos_origen():
            return False
        
        # Paso 3: Transformar
        if not self.transformar_datos():
            return False
        
        # Paso 4: Cargar
        if not self.cargar_datos():
            return False
        
        # Mostrar resumen
        print(self.stats.get_resumen())
        
        return True

def main():
    """Función principal"""
    # Determinar ambiente
    ambiente = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    # Crear y ejecutar ETL
    etl = ETLProyectos(ambiente)
    
    try:
        exito = etl.ejecutar_etl_completo()
        exit_code = 0 if exito else 1
        
    except KeyboardInterrupt:
        print(formatear_salida_consola("Proceso ETL interrumpido por el usuario", 'warning'))
        exit_code = 2
        
    except Exception as e:
        print(formatear_salida_consola(f"Error inesperado: {e}", 'error'))
        exit_code = 3
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
