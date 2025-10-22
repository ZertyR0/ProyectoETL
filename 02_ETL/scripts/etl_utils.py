#!/usr/bin/env python3
"""
Utilidades para el proceso ETL
Funciones auxiliares para transformación, validación y logging
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import logging

def configurar_logging(nivel: str = 'INFO', archivo: Optional[str] = None) -> logging.Logger:
    """
    Configura el sistema de logging para el ETL
    
    Args:
        nivel: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        archivo: Ruta del archivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger('ETL')
    logger.setLevel(getattr(logging, nivel.upper()))
    
    # Limpiar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    if archivo:
        file_handler = logging.FileHandler(archivo)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def validar_dataframe(df: pd.DataFrame, nombre: str, columnas_requeridas: List[str]) -> bool:
    """
    Valida que un DataFrame tenga la estructura esperada
    
    Args:
        df: DataFrame a validar
        nombre: Nombre descriptivo del DataFrame
        columnas_requeridas: Lista de columnas que deben existir
    
    Returns:
        True si la validación es exitosa
    """
    logger = logging.getLogger('ETL')
    
    if df.empty:
        logger.warning(f"⚠️ {nombre}: DataFrame está vacío")
        return False
    
    columnas_faltantes = set(columnas_requeridas) - set(df.columns)
    if columnas_faltantes:
        logger.error(f"❌ {nombre}: Columnas faltantes: {columnas_faltantes}")
        return False
    
    logger.info(f"✅ {nombre}: Validación exitosa ({len(df)} registros)")
    return True

def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpieza general a un DataFrame
    
    Args:
        df: DataFrame a limpiar
    
    Returns:
        DataFrame limpio
    """
    df_limpio = df.copy()
    
    # Limpiar strings
    for col in df_limpio.select_dtypes(include=['object']).columns:
        if df_limpio[col].dtype == 'object':
            df_limpio[col] = df_limpio[col].astype(str).str.strip()
            df_limpio[col] = df_limpio[col].replace('nan', None)
            df_limpio[col] = df_limpio[col].replace('', None)
    
    # Convertir fechas vacías a None
    for col in df_limpio.columns:
        if 'fecha' in col.lower():
            df_limpio[col] = pd.to_datetime(df_limpio[col], errors='coerce')
    
    return df_limpio

def calcular_diferencia_dias(fecha_inicio: pd.Series, fecha_fin: pd.Series) -> pd.Series:
    """
    Calcula la diferencia en días entre dos fechas
    
    Args:
        fecha_inicio: Serie con fechas de inicio
        fecha_fin: Serie con fechas de fin
    
    Returns:
        Serie con diferencias en días
    """
    diferencia = (fecha_fin - fecha_inicio).dt.days
    return diferencia.fillna(0).astype(int)

def calcular_cumplimiento_tiempo(fecha_plan: pd.Series, fecha_real: pd.Series) -> pd.Series:
    """
    Calcula si se cumplió el tiempo planificado
    
    Args:
        fecha_plan: Fecha planificada de finalización
        fecha_real: Fecha real de finalización
    
    Returns:
        Serie con 1 si se cumplió, 0 si no
    """
    # Si no hay fecha real, no se puede evaluar (consideramos como no cumplido)
    cumplimiento = np.where(
        (fecha_real.notna()) & (fecha_real <= fecha_plan), 1, 0
    )
    return pd.Series(cumplimiento, index=fecha_plan.index)

def calcular_cumplimiento_presupuesto(presupuesto: pd.Series, costo_real: pd.Series, tolerancia: float = 0.1) -> pd.Series:
    """
    Calcula si se cumplió el presupuesto
    
    Args:
        presupuesto: Presupuesto planificado
        costo_real: Costo real
        tolerancia: Porcentaje de tolerancia (default: 10%)
    
    Returns:
        Serie con 1 si se cumplió, 0 si no
    """
    limite = presupuesto * (1 + tolerancia)
    cumplimiento = np.where(
        (costo_real.notna()) & (costo_real <= limite), 1, 0
    )
    return pd.Series(cumplimiento, index=presupuesto.index)

def crear_dimension_tiempo(fecha_inicio: date, fecha_fin: date) -> pd.DataFrame:
    """
    Crea la dimensión tiempo para el rango de fechas especificado
    
    Args:
        fecha_inicio: Fecha de inicio del rango
        fecha_fin: Fecha de fin del rango
    
    Returns:
        DataFrame con la dimensión tiempo
    """
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    
    dim_tiempo = pd.DataFrame({
        'fecha': fechas,
        'anio': fechas.year,
        'mes': fechas.month,
        'dia': fechas.day,
        'nombre_mes': fechas.strftime('%B'),
        'trimestre': fechas.quarter,
        'semestre': np.where(fechas.month <= 6, 1, 2),
        'dia_semana': fechas.dayofweek + 1,  # 1=Lunes, 7=Domingo
        'nombre_dia_semana': fechas.strftime('%A'),
        'es_fin_semana': np.where(fechas.dayofweek >= 5, 1, 0),
        'numero_semana': fechas.isocalendar().week
    })
    
    # Agregar ID único para cada fecha
    dim_tiempo['id_tiempo'] = range(1, len(dim_tiempo) + 1)
    
    # Marcar feriados comunes (simplificado)
    dim_tiempo['es_feriado'] = 0
    feriados_fijos = [
        (1, 1),   # Año Nuevo
        (5, 1),   # Día del Trabajo
        (9, 16),  # Independencia
        (12, 25)  # Navidad
    ]
    
    for mes, dia in feriados_fijos:
        mask = (dim_tiempo['mes'] == mes) & (dim_tiempo['dia'] == dia)
        dim_tiempo.loc[mask, 'es_feriado'] = 1
    
    return dim_tiempo

def obtener_id_tiempo(fecha: date, dim_tiempo: pd.DataFrame) -> Optional[int]:
    """
    Obtiene el ID de tiempo para una fecha específica
    
    Args:
        fecha: Fecha a buscar
        dim_tiempo: DataFrame con la dimensión tiempo cargada
    
    Returns:
        ID de tiempo o None si no se encuentra
    """
    if pd.isna(fecha) or fecha is None:
        return None
    
    mask = dim_tiempo['fecha'].dt.date == fecha
    resultado = dim_tiempo.loc[mask, 'id_tiempo']
    
    return resultado.iloc[0] if not resultado.empty else None

def generar_metricas_proyecto(df_proyecto: pd.DataFrame, df_tareas: pd.DataFrame) -> pd.DataFrame:
    """
    Genera métricas agregadas para los proyectos
    
    Args:
        df_proyecto: DataFrame con datos de proyectos
        df_tareas: DataFrame con datos de tareas
    
    Returns:
        DataFrame con métricas calculadas
    """
    logger = logging.getLogger('ETL')
    
    # Agrupar tareas por proyecto
    tareas_por_proyecto = df_tareas.groupby('id_proyecto').agg({
        'id_tarea': 'count',
        'horas_plan': 'sum',
        'horas_reales': 'sum',
        'costo_estimado': 'sum',
        'costo_real': 'sum',
        'id_estado': lambda x: (x == 3).sum(),  # Tareas completadas (estado 3)
        'progreso_porcentaje': 'mean'
    }).rename(columns={
        'id_tarea': 'tareas_total',
        'horas_plan': 'horas_estimadas_total',
        'horas_reales': 'horas_reales_total',
        'costo_estimado': 'costo_estimado_tareas',
        'costo_real': 'costo_real_tareas',
        'id_estado': 'tareas_completadas'
    })
    
    # Calcular tareas canceladas (estado 4)
    tareas_canceladas = df_tareas.groupby('id_proyecto')['id_estado'].apply(lambda x: (x == 4).sum())
    tareas_por_proyecto['tareas_canceladas'] = tareas_canceladas
    
    # Calcular tareas pendientes
    tareas_por_proyecto['tareas_pendientes'] = (
        tareas_por_proyecto['tareas_total'] - 
        tareas_por_proyecto['tareas_completadas'] - 
        tareas_por_proyecto['tareas_canceladas']
    )
    
    # Merge con datos de proyecto
    resultado = df_proyecto.merge(tareas_por_proyecto, on='id_proyecto', how='left')
    
    # Rellenar valores nulos
    columnas_numericas = ['tareas_total', 'tareas_completadas', 'tareas_canceladas', 'tareas_pendientes',
                         'horas_estimadas_total', 'horas_reales_total', 'costo_estimado_tareas', 'costo_real_tareas']
    for col in columnas_numericas:
        if col in resultado.columns:
            resultado[col] = resultado[col].fillna(0)
    
    # IMPORTANTE: NO sobrescribir costo_real del proyecto
    # El costo_real del proyecto viene de la tabla Proyecto y es el valor correcto
    # El costo_real_tareas es solo la suma de costos de tareas individuales
    # Mantener el costo_real original del proyecto
    
    logger.info(f"✅ Métricas generadas para {len(resultado)} proyectos")
    return resultado

def formatear_salida_consola(mensaje: str, tipo: str = 'info') -> str:
    """
    Formatea mensajes para salida en consola con colores y emojis
    
    Args:
        mensaje: Mensaje a formatear
        tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')
    
    Returns:
        Mensaje formateado
    """
    emojis = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'proceso': '🔄',
        'datos': '📊',
        'tiempo': '⏰'
    }
    
    emoji = emojis.get(tipo, 'ℹ️')
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    return f"[{timestamp}] {emoji} {mensaje}"

class ETLStats:
    """Clase para mantener estadísticas del proceso ETL"""
    
    def __init__(self):
        self.inicio = datetime.now()
        self.registros_procesados = {}
        self.errores = []
        self.warnings = []
    
    def agregar_procesados(self, tabla: str, cantidad: int):
        """Agregar registros procesados"""
        self.registros_procesados[tabla] = cantidad
    
    def agregar_error(self, error: str):
        """Agregar error"""
        self.errores.append(f"{datetime.now().strftime('%H:%M:%S')} - {error}")
    
    def agregar_warning(self, warning: str):
        """Agregar warning"""
        self.warnings.append(f"{datetime.now().strftime('%H:%M:%S')} - {warning}")
    
    def get_resumen(self) -> str:
        """Obtener resumen del proceso"""
        duracion = datetime.now() - self.inicio
        
        resumen = f"\n{'='*50}\n"
        resumen += f"📊 RESUMEN DEL PROCESO ETL\n"
        resumen += f"{'='*50}\n"
        resumen += f"⏰ Duración: {duracion}\n"
        resumen += f"📈 Registros procesados:\n"
        
        for tabla, cantidad in self.registros_procesados.items():
            resumen += f"  - {tabla}: {cantidad:,}\n"
        
        total = sum(self.registros_procesados.values())
        resumen += f"  📊 Total: {total:,} registros\n"
        
        if self.warnings:
            resumen += f"\n⚠️ Warnings ({len(self.warnings)}):\n"
            for warning in self.warnings[-5:]:  # Últimos 5
                resumen += f"  - {warning}\n"
        
        if self.errores:
            resumen += f"\n❌ Errores ({len(self.errores)}):\n"
            for error in self.errores[-3:]:  # Últimos 3
                resumen += f"  - {error}\n"
        
        estado = "✅ EXITOSO" if not self.errores else "⚠️ CON ERRORES"
        resumen += f"\n🎯 Estado: {estado}\n"
        resumen += f"{'='*50}\n"
        
        return resumen
