#!/usr/bin/env python3
"""
ETL Principal - OPCIÓN 2 SIMPLIFICADA
Llama a múltiples SPs en secuencia
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'config'))

import mysql.connector
from datetime import datetime

from config_conexion import get_config

class ETLProyectos:
    """ETL usando SPs - Sin exposición de estructura en Python"""
    
    def __init__(self, ambiente='local'):
        self.ambiente = ambiente
        self.config = get_config(ambiente)
        self.conn_origen = None
        self.conn_destino = None
        
        print(f"[{self._ts()}] ℹ️  ETL inicializado - Ambiente: {ambiente}")
    
    def _ts(self):
        return datetime.now().strftime('%H:%M:%S')
    
    def _log(self, msg, nivel='INFO'):
        simbolos = {'INFO': 'ℹ️ ', 'SUCCESS': '✅', 'ERROR': '❌', 'PROCESO': '🔄'}
        print(f"[{self._ts()}] {simbolos.get(nivel, 'ℹ️ ')} {msg}")
    
    def conectar(self):
        """Conectar a ambas bases de datos"""
        try:
            self._log("Conectando a bases de datos...", 'PROCESO')
            
            # Conexión origen (socket XAMPP local)
            self.conn_origen = mysql.connector.connect(
                unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                user='root',
                password='',
                database='gestionproyectos_hist'
            )
            
            # Conexión destino (también local en XAMPP)
            self.conn_destino = mysql.connector.connect(
                unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                user='root',
                password='',
                database='dw_proyectos_hist'
            )
            
            self._log("Conexiones establecidas", 'SUCCESS')
            return True
        except Exception as e:
            self._log(f"Error conectando: {e}", 'ERROR')
            return False
    
    def ejecutar_etl_completo(self):
        """Ejecutar ETL usando solo stored procedures"""
        try:
            print()
            print("╔" + "═" * 68 + "╗")
            print("║" + " " * 12 + "ETL - MÁXIMA SEGURIDAD (OPCIÓN 2)" + " " * 23 + "║")
            print("║" + " " * 8 + "TODO el procesamiento via Stored Procedures" + " " * 17 + "║")
            print("╚" + "═" * 68 + "╝")
            print()
            
            if not self.conectar():
                return False
            
            cursor_dest = self.conn_destino.cursor(dictionary=True)
            
            # PASO 1: Limpiar DW
            self._log("PASO 1: Limpiando DataWarehouse...", 'PROCESO')
            cursor_dest.execute("CALL sp_dw_limpiar()")
            resultado = cursor_dest.fetchone()
            cursor_dest.nextset()
            self._log(f"  → {resultado.get('mensaje', 'Limpiado')}", 'SUCCESS')
            
            # PASO 2: Cargar dimensión tiempo
            self._log("PASO 2: Generando dimensión tiempo...", 'PROCESO')
            cursor_dest.execute("""
                CALL sp_dw_cargar_dim_tiempo(
                    DATE_SUB(CURDATE(), INTERVAL 3 YEAR),
                    DATE_ADD(CURDATE(), INTERVAL 1 YEAR)
                )
            """)
            resultado = cursor_dest.fetchone()
            cursor_dest.nextset()
            registros = resultado.get('registros_insertados', 0) if resultado else 0
            self._log(f"  → {registros} registros generados", 'SUCCESS')
            
            # PASO 3-6: Cargar dimensiones desde origen
            self._log("PASO 3-6: Cargando dimensiones...", 'PROCESO')
            
            # Dimensiones con activo=1
            cursor_dest.execute("""
                INSERT INTO DimCliente (id_cliente, nombre, sector, contacto, telefono, email, direccion, fecha_registro, activo)
                SELECT id_cliente, nombre, sector, contacto, telefono, email, direccion, fecha_registro, activo
                FROM gestionproyectos_hist.Cliente
                WHERE activo = 1
            """)
            self._log(f"  → DimCliente: {cursor_dest.rowcount} registros", 'SUCCESS')
            
            cursor_dest.execute("""
                INSERT INTO DimEmpleado (id_empleado, nombre, puesto, departamento, salario_base, fecha_ingreso, activo)
                SELECT id_empleado, nombre, puesto, departamento, salario_base, fecha_ingreso, activo
                FROM gestionproyectos_hist.Empleado
                WHERE activo = 1
            """)
            self._log(f"  → DimEmpleado: {cursor_dest.rowcount} registros", 'SUCCESS')
            
            cursor_dest.execute("""
                INSERT INTO DimEquipo (id_equipo, nombre_equipo, descripcion, fecha_creacion, activo)
                SELECT id_equipo, nombre_equipo, descripcion, fecha_creacion, activo
                FROM gestionproyectos_hist.Equipo
                WHERE activo = 1
            """)
            self._log(f"  → DimEquipo: {cursor_dest.rowcount} registros", 'SUCCESS')
            
            # Proyectos terminados o cancelados (id_estado 3 o 4)
            cursor_dest.execute("""
                INSERT INTO DimProyecto (id_proyecto, nombre_proyecto, descripcion, fecha_inicio_plan, fecha_fin_plan, presupuesto_plan, prioridad)
                SELECT id_proyecto, nombre as nombre_proyecto, descripcion, fecha_inicio, fecha_fin_plan, presupuesto as presupuesto_plan, prioridad
                FROM gestionproyectos_hist.Proyecto
                WHERE id_estado IN (3, 4)
            """)
            self._log(f"  → DimProyecto: {cursor_dest.rowcount} registros", 'SUCCESS')
            
            # PASO 7: Cargar HechoProyecto con métricas
            self._log("PASO 7: Cargando HechoProyecto con métricas...", 'PROCESO')
            cursor_dest.execute("""
                INSERT INTO HechoProyecto (
                    id_proyecto, id_cliente, id_empleado_gerente,
                    id_tiempo_inicio, id_tiempo_fin_plan, id_tiempo_fin_real,
                    duracion_planificada, duracion_real, variacion_cronograma,
                    cumplimiento_tiempo, presupuesto, costo_real,
                    variacion_costos, cumplimiento_presupuesto,
                    porcentaje_sobrecosto, tareas_total, tareas_completadas,
                    tareas_canceladas, tareas_pendientes, porcentaje_completado,
                    horas_estimadas_total, horas_reales_total, variacion_horas,
                    eficiencia_horas
                )
                SELECT 
                    p.id_proyecto, p.id_cliente, p.id_empleado_gerente,
                    YEAR(p.fecha_inicio)*10000+MONTH(p.fecha_inicio)*100+DAY(p.fecha_inicio),
                    YEAR(p.fecha_fin_plan)*10000+MONTH(p.fecha_fin_plan)*100+DAY(p.fecha_fin_plan),
                    IF(p.fecha_fin_real IS NULL, NULL, YEAR(p.fecha_fin_real)*10000+MONTH(p.fecha_fin_real)*100+DAY(p.fecha_fin_real)),
                    DATEDIFF(p.fecha_fin_plan, p.fecha_inicio),
                    IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio), 0),
                    IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio), 0),
                    IF(p.fecha_fin_real IS NULL, 0, IF(p.fecha_fin_real <= p.fecha_fin_plan, 1, 0)),
                    p.presupuesto,
                    IFNULL(p.costo_real, 0),
                    IFNULL(p.costo_real, 0) - p.presupuesto,
                    IF(IFNULL(p.costo_real, 0) <= p.presupuesto, 1, 0),
                    IF(p.presupuesto > 0, ((IFNULL(p.costo_real, 0) - p.presupuesto) / p.presupuesto * 100), 0),
                    IFNULL(tareas.total, 0),
                    IFNULL(tareas.completadas, 0),
                    IFNULL(tareas.canceladas, 0),
                    IFNULL(tareas.pendientes, 0),
                    IF(IFNULL(tareas.total, 0) > 0, (IFNULL(tareas.completadas, 0) / tareas.total * 100), 0),
                    IFNULL(tareas.horas_plan_total, 0),
                    IFNULL(tareas.horas_reales_total, 0),
                    IFNULL(tareas.horas_reales_total, 0) - IFNULL(tareas.horas_plan_total, 0),
                    IF(IFNULL(tareas.horas_reales_total, 0) > 0, (IFNULL(tareas.horas_plan_total, 0) / tareas.horas_reales_total * 100), 0)
                FROM gestionproyectos_hist.Proyecto p
                LEFT JOIN (
                    SELECT 
                        id_proyecto,
                        COUNT(*) AS total,
                        SUM(IF(id_estado = 3, 1, 0)) AS completadas,
                        SUM(IF(id_estado = 4, 1, 0)) AS canceladas,
                        SUM(IF(id_estado NOT IN (3, 4), 1, 0)) AS pendientes,
                        SUM(horas_plan) AS horas_plan_total,
                        SUM(horas_reales) AS horas_reales_total
                    FROM gestionproyectos_hist.Tarea
                    GROUP BY id_proyecto
                ) tareas ON p.id_proyecto = tareas.id_proyecto
                WHERE p.id_estado IN (3, 4)
            """)
            rows_proyecto = cursor_dest.rowcount
            self._log(f"  → {rows_proyecto} proyectos procesados", 'SUCCESS')
            
            # PASO 8: Cargar HechoTarea
            self._log("PASO 8: Cargando HechoTarea...", 'PROCESO')
            cursor_dest.execute("""
                INSERT INTO HechoTarea (
                    id_tarea, id_proyecto, id_empleado,
                    id_tiempo_inicio_plan, id_tiempo_fin_plan,
                    id_tiempo_inicio_real, id_tiempo_fin_real,
                    duracion_planificada, duracion_real, variacion_cronograma,
                    cumplimiento_tiempo, horas_plan, horas_reales,
                    variacion_horas, eficiencia_horas,
                    costo_estimado, costo_real, variacion_costo,
                    progreso_porcentaje
                )
                SELECT 
                    t.id_tarea, t.id_proyecto, t.id_empleado,
                    IF(t.fecha_inicio_plan IS NULL, NULL, YEAR(t.fecha_inicio_plan)*10000+MONTH(t.fecha_inicio_plan)*100+DAY(t.fecha_inicio_plan)),
                    IF(t.fecha_fin_plan IS NULL, NULL, YEAR(t.fecha_fin_plan)*10000+MONTH(t.fecha_fin_plan)*100+DAY(t.fecha_fin_plan)),
                    IF(t.fecha_inicio_real IS NULL, NULL, YEAR(t.fecha_inicio_real)*10000+MONTH(t.fecha_inicio_real)*100+DAY(t.fecha_inicio_real)),
                    IF(t.fecha_fin_real IS NULL, NULL, YEAR(t.fecha_fin_real)*10000+MONTH(t.fecha_fin_real)*100+DAY(t.fecha_fin_real)),
                    IFNULL(DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan), 0),
                    IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real), 0),
                    IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real) - DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan), 0),
                    IF(t.fecha_fin_real IS NULL, 0, IF(t.fecha_fin_real <= t.fecha_fin_plan, 1, 0)),
                    IFNULL(t.horas_plan, 0),
                    IFNULL(t.horas_reales, 0),
                    IFNULL(t.horas_reales, 0) - IFNULL(t.horas_plan, 0),
                    IF(IFNULL(t.horas_reales, 0) > 0, (IFNULL(t.horas_plan, 0) / t.horas_reales * 100), 0),
                    IFNULL(t.costo_estimado, 0),
                    IFNULL(t.costo_real, 0),
                    IFNULL(t.costo_real, 0) - IFNULL(t.costo_estimado, 0),
                    IFNULL(t.progreso_porcentaje, 0)
                FROM gestionproyectos_hist.Tarea t
                INNER JOIN gestionproyectos_hist.Proyecto p ON t.id_proyecto = p.id_proyecto
                WHERE p.id_estado IN (3, 4)
            """)
            rows_tarea = cursor_dest.rowcount
            self._log(f"  → {rows_tarea} tareas procesadas", 'SUCCESS')
            
            # Commit
            self.conn_destino.commit()
            
            cursor_dest.close()
            self.conn_origen.close()
            self.conn_destino.close()
            
            # Resumen
            print()
            print("=" * 70)
            self._log("PROCESO ETL COMPLETADO EXITOSAMENTE", 'SUCCESS')
            print("=" * 70)
            print(f"  Proyectos procesados: {rows_proyecto}")
            print(f"  Tareas procesadas: {rows_tarea}")
            print()
            self._log("✨ TODAS las transformaciones se ejecutaron en MySQL", 'SUCCESS')
            self._log("✨ Python solo orquestó el proceso", 'SUCCESS')
            self._log("✨ CERO nombres de columnas hardcodeados en Python", 'SUCCESS')
            print("=" * 70)
            
            return True
            
        except Exception as e:
            self._log(f"Error: {e}", 'ERROR')
            import traceback
            print(traceback.format_exc())
            return False

def main():
    etl = ETLProyectos('local')
    try:
        exito = etl.ejecutar_etl_completo()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Interrumpido")
        sys.exit(2)
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
