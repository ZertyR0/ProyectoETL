"""
Modelo de Predicción de Defectos con Distribución de Rayleigh
Sistema de Soporte de Decisiones (DSS)

Implementación de la distribución de Rayleigh para modelado de fallas/defectos
en proyectos de software según el ciclo de vida del desarrollo.

La distribución de Rayleigh es ampliamente utilizada en ingeniería de software
para predecir la tasa de detección de defectos a lo largo del tiempo.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import mysql.connector
import os

class RayleighModel:
    """
    Clase para modelado de defectos usando distribución de Rayleigh
    
    Ecuaciones:
    - Función de densidad: f(t) = (t/σ²) * exp(-t²/(2σ²))
    - Función acumulativa: F(t) = 1 - exp(-t²/(2σ²))
    - Tasa de fallas: h(t) = t/σ²
    """
    
    def __init__(self):
        self.sigma = None
        self.total_defectos = None
        self.fecha_inicio = None
        self.duracion_total = None
        
    def calibrar_modelo(self, 
                       tamanio_proyecto: float,
                       duracion_semanas: int,
                       complejidad: str = 'media',
                       tipo_proyecto: str = 'web') -> Dict:
        """
        Calibra el modelo de Rayleigh basado en características del proyecto
        
        Args:
            tamanio_proyecto: Tamaño estimado (puntos de función, KLOC, etc.)
            duracion_semanas: Duración estimada del proyecto en semanas
            complejidad: 'baja', 'media', 'alta'
            tipo_proyecto: 'web', 'movil', 'sistema', 'api'
            
        Returns:
            Dict con parámetros calibrados del modelo
        """
        
        # Factores de calibración basados en literatura e industria
        factores_complejidad = {
            'baja': 0.7,
            'media': 1.0,
            'alta': 1.4
        }
        
        factores_tipo = {
            'web': 1.0,
            'movil': 1.2,
            'sistema': 1.5,
            'api': 0.8
        }
        
        # Estimar total de defectos basado en tamaño
        # Aproximación: 2-8 defectos por punto de función según complejidad
        defectos_base_por_unidad = {
            'baja': 2.0,
            'media': 4.0,
            'alta': 6.5
        }
        
        factor_comp = factores_complejidad.get(complejidad, 1.0)
        factor_tipo = factores_tipo.get(tipo_proyecto, 1.0)
        defectos_por_unidad = defectos_base_por_unidad.get(complejidad, 4.0)
        
        # Calcular total de defectos esperados
        self.total_defectos = int(
            tamanio_proyecto * defectos_por_unidad * factor_tipo
        )
        
        # Calcular σ (sigma) - parámetro de forma de Rayleigh
        # El pico de defectos ocurre típicamente en el 60-70% del proyecto
        tiempo_pico = duracion_semanas * 0.65
        
        # Para Rayleigh: el pico ocurre en t = σ
        self.sigma = tiempo_pico
        self.duracion_total = duracion_semanas
        
        return {
            'sigma': self.sigma,
            'total_defectos_estimado': self.total_defectos,
            'tiempo_pico_semanas': tiempo_pico,
            'duracion_total': duracion_semanas,
            'factor_complejidad': factor_comp,
            'factor_tipo_proyecto': factor_tipo
        }
    
    def densidad_probabilidad(self, t: float) -> float:
        """
        Calcula la función de densidad de probabilidad de Rayleigh en tiempo t
        
        Args:
            t: Tiempo en semanas
            
        Returns:
            Valor de la función de densidad
        """
        if self.sigma is None:
            raise ValueError("Modelo no calibrado. Ejecutar calibrar_modelo() primero.")
        
        if t <= 0:
            return 0.0
            
        return (t / (self.sigma ** 2)) * math.exp(-(t ** 2) / (2 * (self.sigma ** 2)))
    
    def funcion_acumulativa(self, t: float) -> float:
        """
        Calcula la función acumulativa de Rayleigh en tiempo t
        
        Args:
            t: Tiempo en semanas
            
        Returns:
            Probabilidad acumulada hasta el tiempo t
        """
        if self.sigma is None:
            raise ValueError("Modelo no calibrado.")
        
        if t <= 0:
            return 0.0
            
        return 1 - math.exp(-(t ** 2) / (2 * (self.sigma ** 2)))
    
    def tasa_defectos_instantanea(self, t: float) -> float:
        """
        Calcula la tasa instantánea de defectos (hazard rate)
        
        Args:
            t: Tiempo en semanas
            
        Returns:
            Tasa de defectos por semana en el tiempo t
        """
        if self.sigma is None:
            raise ValueError("Modelo no calibrado.")
        
        return t / (self.sigma ** 2)
    
    def predecir_defectos_por_periodo(self, 
                                    inicio_semana: int = 1,
                                    fin_semana: Optional[int] = None) -> List[Dict]:
        """
        Predice defectos esperados por semana en un rango de tiempo
        
        Args:
            inicio_semana: Semana de inicio (base 1)
            fin_semana: Semana de fin (si None, usa duración total)
            
        Returns:
            Lista de predicciones por semana
        """
        if self.sigma is None or self.total_defectos is None:
            raise ValueError("Modelo no calibrado.")
        
        if fin_semana is None:
            fin_semana = int(self.duracion_total) if self.duracion_total is not None else 16
        
        predicciones = []
        
        for semana in range(inicio_semana, fin_semana + 1):
            # Defectos acumulados hasta esta semana
            acum_actual = self.funcion_acumulativa(semana) * self.total_defectos
            
            # Defectos acumulados hasta semana anterior
            acum_anterior = self.funcion_acumulativa(semana - 1) * self.total_defectos if semana > 1 else 0
            
            # Defectos esperados en esta semana
            defectos_semana = acum_actual - acum_anterior
            
            # Tasa instantánea
            tasa_instantanea = self.tasa_defectos_instantanea(semana)
            
            predicciones.append({
                'semana': semana,
                'defectos_esperados_semana': round(defectos_semana, 2),
                'defectos_acumulados': round(acum_actual, 2),
                'tasa_instantanea': round(tasa_instantanea, 4),
                'porcentaje_completado': round(self.funcion_acumulativa(semana) * 100, 2)
            })
        
        return predicciones
    
    def calcular_metricas_proyecto(self) -> Dict:
        """
        Calcula métricas clave del proyecto basadas en el modelo
        
        Returns:
            Dict con métricas del proyecto
        """
        if self.sigma is None or self.total_defectos is None:
            raise ValueError("Modelo no calibrado.")
        
        # Tiempo del pico de defectos
        tiempo_pico = self.sigma
        
        # Defectos esperados al 50%, 75%, 90% del proyecto
        duracion = self.duracion_total if self.duracion_total is not None else 16
        defectos_50 = self.funcion_acumulativa(duracion * 0.5) * self.total_defectos
        defectos_75 = self.funcion_acumulativa(duracion * 0.75) * self.total_defectos
        defectos_90 = self.funcion_acumulativa(duracion * 0.9) * self.total_defectos
        
        # Tasa máxima de defectos (en el pico)
        tasa_maxima = self.tasa_defectos_instantanea(tiempo_pico)
        
        return {
            'total_defectos_estimado': self.total_defectos,
            'tiempo_pico_semanas': round(tiempo_pico, 1),
            'tasa_maxima_defectos_semana': round(tasa_maxima * self.total_defectos / duracion, 2),
            'defectos_al_50_pct': round(defectos_50, 0),
            'defectos_al_75_pct': round(defectos_75, 0),
            'defectos_al_90_pct': round(defectos_90, 0),
            'porcentaje_defectos_primera_mitad': round((defectos_50 / self.total_defectos) * 100, 1),
            'sigma_parametro': round(self.sigma, 2)
        }
    
    def generar_cronograma_testing(self, 
                                  fecha_inicio: datetime,
                                  esfuerzo_testing_disponible: float) -> List[Dict]:
        """
        Genera cronograma sugerido de testing basado en la curva de defectos
        
        Args:
            fecha_inicio: Fecha de inicio del proyecto
            esfuerzo_testing_disponible: Horas totales disponibles para testing
            
        Returns:
            Lista con cronograma de testing por semana
        """
        if self.sigma is None:
            raise ValueError("Modelo no calibrado.")
        
        cronograma = []
        predicciones = self.predecir_defectos_por_periodo()
        
        # Distribución del esfuerzo proporcional a defectos esperados
        total_defectos = sum(p['defectos_esperados_semana'] for p in predicciones)
        
        for pred in predicciones:
            fecha_semana = fecha_inicio + timedelta(weeks=pred['semana'] - 1)
            
            # Asignar esfuerzo proporcional a defectos esperados
            if total_defectos > 0:
                esfuerzo_semana = (pred['defectos_esperados_semana'] / total_defectos) * esfuerzo_testing_disponible
            else:
                esfuerzo_semana = esfuerzo_testing_disponible / len(predicciones)
            
            # Recomendar intensidad de testing
            if pred['defectos_esperados_semana'] > total_defectos * 0.1:  # >10% del total
                intensidad = 'Alta'
            elif pred['defectos_esperados_semana'] > total_defectos * 0.05:  # >5% del total
                intensidad = 'Media'
            else:
                intensidad = 'Baja'
            
            cronograma.append({
                'semana': pred['semana'],
                'fecha_inicio_semana': fecha_semana.strftime('%Y-%m-%d'),
                'defectos_esperados': pred['defectos_esperados_semana'],
                'esfuerzo_testing_horas': round(esfuerzo_semana, 1),
                'intensidad_recomendada': intensidad,
                'porcentaje_proyecto': pred['porcentaje_completado'],
                'acumulado_defectos': pred['defectos_acumulados']
            })
        
        return cronograma

def obtener_datos_proyectos_reales():
    """
    Obtiene datos históricos reales de HechoProyecto para calibrar el modelo
    
    Returns:
        Dict con estadísticas de proyectos reales
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_DESTINO', 'dw_proyectos_hist')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estadísticas de proyectos completados
        query = """
        SELECT 
            AVG(hp.duracion_real) as duracion_promedio_dias,
            AVG(hp.duracion_planificada) as duracion_plan_promedio_dias,
            AVG(hp.tareas_total) as tareas_promedio,
            AVG(hp.tareas_completadas) as tareas_completadas_promedio,
            AVG(hp.tareas_canceladas) as tareas_canceladas_promedio,
            AVG(hp.horas_plan_total) as horas_plan_promedio,
            AVG(hp.horas_reales_total) as horas_reales_promedio,
            AVG(hp.presupuesto) as presupuesto_promedio,
            AVG(hp.costo_real_proy) as costo_real_promedio,
            COUNT(hp.id_hecho_proyecto) as total_proyectos,
            SUM(CASE WHEN hp.cumplimiento_tiempo = 1 THEN 1 ELSE 0 END) as proyectos_a_tiempo,
            SUM(CASE WHEN hp.cumplimiento_presupuesto = 1 THEN 1 ELSE 0 END) as proyectos_en_presupuesto
        FROM HechoProyecto hp
        WHERE hp.tareas_total > 0
        """
        
        cursor.execute(query)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if stats and stats['total_proyectos'] > 0:
            # Convertir días a semanas
            duracion_semanas = (stats['duracion_promedio_dias'] or 0) / 7
            
            # Estimar defectos basados en tareas canceladas como proxy
            # Ratio típico: tareas canceladas pueden indicar problemas/defectos
            defectos_estimados_por_proyecto = (stats['tareas_canceladas_promedio'] or 0) * 3
            
            return {
                'tiene_datos': True,
                'total_proyectos': stats['total_proyectos'],
                'duracion_promedio_semanas': round(duracion_semanas, 1),
                'tareas_promedio': round(stats['tareas_promedio'] or 0, 1),
                'defectos_estimados_promedio': round(defectos_estimados_por_proyecto, 1),
                'tasa_cumplimiento_tiempo': round((stats['proyectos_a_tiempo'] / stats['total_proyectos']) * 100, 1) if stats['total_proyectos'] > 0 else 0,
                'tasa_cumplimiento_presupuesto': round((stats['proyectos_en_presupuesto'] / stats['total_proyectos']) * 100, 1) if stats['total_proyectos'] > 0 else 0,
                'horas_promedio': round(stats['horas_reales_promedio'] or 0, 1)
            }
    except Exception as e:
        print(f"Error obteniendo datos reales: {e}")
        return {'tiene_datos': False}
    
    return {'tiene_datos': False}

def generar_prediccion_completa(tamanio_proyecto: float,
                              duracion_semanas: int,
                              complejidad: str = 'media',
                              tipo_proyecto: str = 'web',
                              fecha_inicio: Optional[datetime] = None,
                              esfuerzo_testing: float = 160.0,
                              usar_datos_reales: bool = True) -> Dict:
    """
    Función principal para generar predicción completa de defectos
    
    Args:
        tamanio_proyecto: Tamaño del proyecto (puntos de función, etc.)
        duracion_semanas: Duración estimada en semanas
        complejidad: Nivel de complejidad del proyecto
        tipo_proyecto: Tipo de proyecto
        fecha_inicio: Fecha de inicio (si None, usa fecha actual)
        esfuerzo_testing: Horas totales disponibles para testing
        usar_datos_reales: Si True, calibra con datos de HechoProyecto
        
    Returns:
        Dict con predicción completa
    """
    
    if fecha_inicio is None:
        fecha_inicio = datetime.now()
    
    # Obtener datos reales si está habilitado
    datos_reales = None
    if usar_datos_reales:
        datos_reales = obtener_datos_proyectos_reales()
        if datos_reales and datos_reales.get('tiene_datos'):
            # Ajustar parámetros basados en datos reales
            if datos_reales['duracion_promedio_semanas'] > 0:
                duracion_semanas = max(duracion_semanas, int(datos_reales['duracion_promedio_semanas']))
            
            # Ajustar estimación de tamaño basado en tareas promedio
            if datos_reales['tareas_promedio'] > 0:
                tamanio_proyecto = max(tamanio_proyecto, datos_reales['tareas_promedio'])
    
    # Crear y calibrar modelo
    modelo = RayleighModel()
    parametros = modelo.calibrar_modelo(
        tamanio_proyecto, duracion_semanas, complejidad, tipo_proyecto
    )
    
    # Ajustar defectos estimados con datos reales si existen
    if datos_reales and datos_reales.get('tiene_datos') and datos_reales['defectos_estimados_promedio'] > 0:
        # Promediar entre la estimación teórica y los datos reales
        modelo.total_defectos = int((modelo.total_defectos + datos_reales['defectos_estimados_promedio'] * datos_reales['total_proyectos']) / 2)
        parametros['total_defectos_estimado'] = modelo.total_defectos
        parametros['calibrado_con_datos_reales'] = True
        parametros['proyectos_historicos'] = datos_reales['total_proyectos']
    else:
        parametros['calibrado_con_datos_reales'] = False
        parametros['proyectos_historicos'] = 0
    
    # Generar predicciones
    predicciones_semanales = modelo.predecir_defectos_por_periodo()
    metricas = modelo.calcular_metricas_proyecto()
    cronograma_testing = modelo.generar_cronograma_testing(fecha_inicio, esfuerzo_testing)
    
    # Generar resumen ejecutivo
    resumen_ejecutivo = {
        'total_defectos_estimado': metricas['total_defectos_estimado'],
        'semana_pico_defectos': metricas['tiempo_pico_semanas'],
        'defectos_primera_mitad': metricas['defectos_al_50_pct'],
        'recomendacion_principal': f"Concentrar esfuerzo de testing en semana {metricas['tiempo_pico_semanas']:.0f}",
        'alerta_calidad': metricas['total_defectos_estimado'] > tamanio_proyecto * 5,
        'nivel_riesgo': 'Alto' if metricas['total_defectos_estimado'] > tamanio_proyecto * 6 else 
                       'Medio' if metricas['total_defectos_estimado'] > tamanio_proyecto * 3 else 'Bajo',
        'basado_en_datos_reales': parametros['calibrado_con_datos_reales']
    }
    
    # Agregar datos reales al resultado si existen
    resultado = {
        'success': True,
        'modelo': 'Distribución de Rayleigh',
        'parametros_calibracion': parametros,
        'metricas_proyecto': metricas,
        'predicciones_semanales': predicciones_semanales,
        'cronograma_testing': cronograma_testing,
        'resumen_ejecutivo': resumen_ejecutivo,
        'metadatos': {
            'fecha_generacion': datetime.now().isoformat(),
            'version_modelo': '1.1',
            'autor': 'DSS - Módulo Rayleigh',
            'usa_datos_historicos': parametros['calibrado_con_datos_reales']
        }
    }
    
    if datos_reales and datos_reales.get('tiene_datos'):
        resultado['datos_historicos'] = datos_reales
    
    return resultado

# Función de utilidad para validación de acceso PM
def validar_acceso_pm(headers: Dict) -> bool:
    """
    Valida si el usuario tiene permisos de Project Manager
    
    Args:
        headers: Headers de la request HTTP
        
    Returns:
        True si tiene acceso, False caso contrario
    """
    # Implementación simple para demo
    # En producción sería JWT/SSO/LDAP
    
    role = headers.get('X-ROLE', '').lower()
    pm_roles = ['pm', 'project_manager', 'gerente_proyecto', 'lead']
    
    return role in pm_roles or headers.get('X-PM-ACCESS') == 'granted'

if __name__ == '__main__':
    # Ejemplo de uso
    print("=== Predicción de Defectos con Modelo Rayleigh ===")
    
    resultado = generar_prediccion_completa(
        tamanio_proyecto=50,  # 50 puntos de función
        duracion_semanas=16,  # 4 meses
        complejidad='media',
        tipo_proyecto='web'
    )
    
    print(f"Total defectos estimados: {resultado['metricas_proyecto']['total_defectos_estimado']}")
    print(f"Semana pico: {resultado['metricas_proyecto']['tiempo_pico_semanas']}")
    print(f"Nivel de riesgo: {resultado['resumen_ejecutivo']['nivel_riesgo']}")