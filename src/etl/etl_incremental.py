"""ETL incremental con logging seguro y sin volcado de datos sensibles.

Características añadidas:
 - Usa configuración central (get_config)
 - Logging con nivel controlado por ETL_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR)
 - Modo ETL_DRY_RUN (no aplica commits) para validación.
 - No imprime valores individuales de filas (solo métricas agregadas).
"""
import os, sys, logging
from pathlib import Path
from datetime import datetime, date
from typing import Any
import mysql.connector

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_ROOT = SCRIPT_DIR.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:
    from src.config.config_conexion import get_config  # type: ignore
    AMBIENTE = os.environ.get('ETL_AMBIENTE', 'local')
    cfg = get_config(AMBIENTE)
    def _make(prefix):
        base = {
            'user': cfg[f'user_{prefix}'],
            'password': cfg[f'password_{prefix}'],
            'database': cfg[f'database_{prefix}']
        }
        if cfg.get('unix_socket'):
            base['unix_socket'] = cfg['unix_socket']
        else:
            base['host'] = cfg[f'host_{prefix}']
            base['port'] = cfg[f'port_{prefix}']
        return base
    CONFIG_ORIGEN = _make('origen'); CONFIG_DESTINO = _make('destino')
except Exception as e:
    print(f" Config por defecto ({e})")
    CONFIG_ORIGEN = {'user':'root','password':'','database':'gestionproyectos_hist','unix_socket':'/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'}
    CONFIG_DESTINO = {'user':'root','password':'','database':'dw_proyectos_hist','unix_socket':'/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'}

LOG_LEVEL = os.getenv("ETL_LOG_LEVEL", "INFO").upper()
DRY_RUN = os.getenv("ETL_DRY_RUN", "0") in {"1", "true", "True"}
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger("etl.incremental")

def ejecutar_etl_incremental() -> bool:
    logger.info("Inicio ETL incremental (dry-run=%s, log-level=%s)", DRY_RUN, LOG_LEVEL)
    inicio_total = datetime.now()
    try:
        co = mysql.connector.connect(**CONFIG_ORIGEN)
        cd = mysql.connector.connect(**CONFIG_DESTINO)
        o: Any = co.cursor(); d: Any = cd.cursor()  # type: ignore
        resumen = {}

        # DimCliente
        o.execute("SELECT id_cliente, nombre, sector FROM Cliente")
        clientes = o.fetchall(); nuevos_clientes = 0
        for (id_cli, nombre, sector) in clientes:
            d.execute(
                """INSERT INTO DimCliente (id_cliente,nombre,sector)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre),sector=VALUES(sector)""",
                (id_cli, nombre, sector)
            )
            if d.rowcount == 1:  # Inserción nueva (heurística)
                nuevos_clientes += 1
        if not DRY_RUN: cd.commit()
        resumen['DimCliente'] = {'procesados': len(clientes), 'nuevos_aprox': nuevos_clientes}

        # DimEmpleado
        o.execute("SELECT id_empleado,nombre,puesto FROM Empleado")
        empleados = o.fetchall(); nuevos_empleados = 0
        for (id_emp, nombre_emp, puesto) in empleados:
            d.execute(
                """INSERT INTO DimEmpleado (id_empleado,nombre,puesto)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE nombre=VALUES(nombre),puesto=VALUES(puesto)""",
                (id_emp, nombre_emp, puesto)
            )
            if d.rowcount == 1:
                nuevos_empleados += 1
        if not DRY_RUN: cd.commit()
        resumen['DimEmpleado'] = {'procesados': len(empleados), 'nuevos_aprox': nuevos_empleados}

        # DimProyecto (estado finalizado/cancelado)
        o.execute("SELECT id_proyecto,nombre,fecha_inicio,fecha_fin_plan,presupuesto FROM Proyecto WHERE id_estado IN (3,4)")
        proyectos = o.fetchall(); nuevos_proyectos = 0
        for (id_proy_dim, nombre_proy, fecha_inicio, fecha_fin_plan, presupuesto) in proyectos:
            d.execute(
                """INSERT INTO DimProyecto (id_proyecto,nombre_proyecto,fecha_inicio_plan,fecha_fin_plan,presupuesto)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE nombre_proyecto=VALUES(nombre_proyecto),fecha_inicio_plan=VALUES(fecha_inicio_plan),fecha_fin_plan=VALUES(fecha_fin_plan),presupuesto=VALUES(presupuesto)""",
                (id_proy_dim, nombre_proy, fecha_inicio, fecha_fin_plan, presupuesto)
            )
            if d.rowcount == 1:
                nuevos_proyectos += 1
        if not DRY_RUN: cd.commit()
        resumen['DimProyecto'] = {'procesados': len(proyectos), 'nuevos_aprox': nuevos_proyectos}

        # DimTiempo
        o.execute("""SELECT DISTINCT fecha_inicio FROM Proyecto WHERE fecha_inicio IS NOT NULL
                  UNION SELECT DISTINCT fecha_fin_plan FROM Proyecto WHERE fecha_fin_plan IS NOT NULL
                  UNION SELECT DISTINCT fecha_fin_real FROM Proyecto WHERE fecha_fin_real IS NOT NULL""")
        fechas_raw = o.fetchall(); nuevas_fechas = 0
        for (fecha_raw,) in fechas_raw:
            if isinstance(fecha_raw, datetime):
                fecha_val = fecha_raw.date()
            elif isinstance(fecha_raw, date):
                fecha_val = fecha_raw
            else:
                continue
            d.execute("INSERT IGNORE INTO DimTiempo (id_tiempo,fecha,anio,mes,trimestre) VALUES (%s,%s,%s,%s,%s)",
                      (fecha_val, fecha_val, fecha_val.year, fecha_val.month, (fecha_val.month-1)//3+1))
            if d.rowcount > 0:
                nuevas_fechas += 1
        if not DRY_RUN: cd.commit()
        resumen['DimTiempo'] = {'fechas_total': len(fechas_raw), 'nuevas': nuevas_fechas}

        # HechoProyecto - procesar todos los proyectos finalizados/cancelados
        o.execute("""SELECT p.id_proyecto,p.id_cliente,p.id_empleado_gerente,p.fecha_inicio,p.fecha_fin_plan,p.fecha_fin_real,p.presupuesto,p.costo_real,
                    DATEDIFF(p.fecha_fin_plan,p.fecha_inicio),DATEDIFF(COALESCE(p.fecha_fin_real,CURDATE()),p.fecha_inicio),
                    (SELECT COUNT(*) FROM Tarea t WHERE t.id_proyecto=p.id_proyecto),
                    (SELECT COUNT(*) FROM Tarea t WHERE t.id_proyecto=p.id_proyecto AND t.id_estado=3),
                    (SELECT COUNT(*) FROM Tarea t WHERE t.id_proyecto=p.id_proyecto AND t.id_estado=4),
                    (SELECT COALESCE(SUM(horas_plan),0) FROM Tarea t WHERE t.id_proyecto=p.id_proyecto),
                    (SELECT COALESCE(SUM(horas_reales),0) FROM Tarea t WHERE t.id_proyecto=p.id_proyecto)
                    FROM Proyecto p WHERE p.id_estado IN (3,4)""")
        hp_cnt = 0
        for row in o.fetchall():
            hp_cnt += 1
            (id_proy,id_cli,id_ger,f_ini,f_fin_plan,f_fin_real,presu,c_real,dur_plan,dur_real,tot,comp,canc,hrs_plan,hrs_real) = row
            dur_plan_val = int(dur_plan or 0)
            dur_real_val = int(dur_real or 0)
            def id_ti(fecha):
                if not fecha: return None
                d.execute("SELECT id_tiempo FROM DimTiempo WHERE fecha=%s", (fecha,))
                r = d.fetchone(); return r[0] if r else None
            id_ti_real = id_ti(f_fin_real)
            if not id_ti_real:
                continue  # Skip si no hay fecha_fin_real
            variacion = dur_real_val - dur_plan_val
            cumplimiento_tiempo = 1 if variacion <= 0 else 0
            presupuesto = float(presu or 0); costo_real = float(c_real or 0)
            var_cost = costo_real - presupuesto
            cumplimiento_pres = 1 if var_cost <= 0 else 0
            tareas_total = int(tot or 0); tareas_completadas = int(comp or 0); tareas_canceladas = int(canc or 0)
            horas_plan_total = int(hrs_plan or 0); horas_reales_total = int(hrs_real or 0)
            var_horas = horas_reales_total - horas_plan_total
            cambios_equipo = 0  # No tenemos esta info en origen
            
            d.execute("SELECT id_hecho_proyecto FROM HechoProyecto WHERE id_proyecto=%s", (id_proy,))
            existe = d.fetchone()
            if existe:
                d.execute("""UPDATE HechoProyecto SET id_cliente=%s,id_empleado_gerente=%s,id_tiempo_fin_real=%s,presupuesto=%s,costo_real=%s,variacion_costos=%s,cumplimiento_presupuesto=%s,duracion_planificada=%s,duracion_real=%s,variacion_cronograma=%s,cumplimiento_tiempo=%s,tareas_total=%s,tareas_completadas=%s,tareas_canceladas=%s,horas_estimadas_total=%s,horas_reales_total=%s,variacion_horas=%s,cambios_equipo_proy=%s WHERE id_proyecto=%s""",
                          (id_cli,id_ger,id_ti_real,presupuesto,costo_real,var_cost,cumplimiento_pres,dur_plan_val,dur_real_val,variacion,cumplimiento_tiempo,tareas_total,tareas_completadas,tareas_canceladas,horas_plan_total,horas_reales_total,var_horas,cambios_equipo,id_proy))
            else:
                d.execute("""INSERT INTO HechoProyecto (id_proyecto,id_cliente,id_empleado_gerente,id_tiempo_fin_real,presupuesto,costo_real,variacion_costos,cumplimiento_presupuesto,duracion_planificada,duracion_real,variacion_cronograma,cumplimiento_tiempo,tareas_total,tareas_completadas,tareas_canceladas,horas_estimadas_total,horas_reales_total,variacion_horas,cambios_equipo_proy) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                          (id_proy,id_cli,id_ger,id_ti_real,presupuesto,costo_real,var_cost,cumplimiento_pres,dur_plan_val,dur_real_val,variacion,cumplimiento_tiempo,tareas_total,tareas_completadas,tareas_canceladas,horas_plan_total,horas_reales_total,var_horas,cambios_equipo))
        if not DRY_RUN: cd.commit()
        resumen['HechoProyecto'] = {'procesados': hp_cnt}

        # HechoTarea - omitido por ahora, requiere refactorización completa
        # TODO: Implementar HechoTarea correctamente cuando se definan las columnas reales
        resumen['HechoTarea'] = {'procesados': 0, 'nota': 'Omitido - requiere refactorización'}
        
        o.close(); d.close(); co.close(); cd.close()
        dur = (datetime.now() - inicio_total).total_seconds()
        logger.info("ETL incremental completado en %.2fs", dur)
        for k,v in resumen.items():
            logger.info("Resumen %s: %s", k, v)
        if DRY_RUN:
            logger.warning("Modo DRY-RUN: no se aplicaron commits en destino")
        return True
    except Exception as e:
        logger.error("Fallo ETL incremental: %s", e, exc_info=LOG_LEVEL=='DEBUG')
        return False

if __name__ == '__main__':
    ejecutar_etl_incremental()
