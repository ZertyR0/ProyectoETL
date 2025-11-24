# Reubicado desde 02_ETL/scripts/etl_final.py (procedimiento almacenado único)
#!/usr/bin/env python3
"""Ejecución del procedimiento almacenado completo con logging seguro.

Mejoras:
 - Usa `get_config` para credenciales (sin hardcode).
 - Logging con nivel controlado por ETL_LOG_LEVEL.
 - Modo ETL_DRY_RUN salta ejecución real del procedimiento.
 - No expone mensajes internos ni parámetros sensibles.
"""
import os, sys, logging, mysql.connector
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_ROOT = SCRIPT_DIR.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:
    from config.config_conexion import get_config  # type: ignore
    AMBIENTE = os.getenv('ETL_AMBIENTE','local')
    cfg = get_config(AMBIENTE)
    DEST = {
        'user': cfg['user_destino'],
        'password': cfg['password_destino'],
        'database': cfg['database_destino']
    }
    if cfg.get('unix_socket'):
        DEST['unix_socket'] = cfg['unix_socket']
    else:
        DEST['host'] = cfg['host_destino']; DEST['port'] = cfg['port_destino']
except Exception as e:
    print(f"⚠️ Config destino no disponible ({e}), fallback local")
    DEST = {'user':'root','password':'','database':'dw_proyectos_hist','unix_socket':'/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'}

LOG_LEVEL = os.getenv('ETL_LOG_LEVEL','INFO').upper()
DRY_RUN = os.getenv('ETL_DRY_RUN','0') in {'1','true','True'}
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format='[%(asctime)s] %(levelname)s etl.final: %(message)s',
                    datefmt='%H:%M:%S')
logger = logging.getLogger('etl.final')

def ejecutar_etl() -> bool:
    logger.info('Inicio ETL final (dry-run=%s, ambiente=%s)', DRY_RUN, os.getenv('ETL_AMBIENTE','local'))
    if DRY_RUN:
        logger.warning('DRY-RUN activado: se omite CALL sp_ejecutar_etl_completo()')
        return True
    inicio = datetime.now()
    try:
        conn = mysql.connector.connect(**DEST)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("CALL sp_ejecutar_etl_completo()")
        resultado = cursor.fetchone()
        cursor.nextset()
        cursor.close(); conn.close()
    except Exception as e:
        logger.error('Fallo ejecutando procedimiento: %s', e, exc_info=LOG_LEVEL=='DEBUG')
        return False
    dur = (datetime.now() - inicio).total_seconds()
    # Intento de obtener estado soportando distintos tipos de row; si no se puede, marcar DESCONOCIDO
    if isinstance(resultado, dict) and 'estado' in resultado:
        estado = resultado['estado']
    else:
        estado = 'DESCONOCIDO'
    if estado == 'EXITOSO':
        mensaje = (resultado['mensaje'] if isinstance(resultado, dict) and 'mensaje' in resultado else '(sin mensaje)')
        logger.info('ETL final OK en %.2fs - %s', dur, mensaje)
        return True
    logger.error('Procedimiento retornó estado no exitoso (%s) tras %.2fs', estado, dur)
    return False

if __name__=='__main__':
    sys.exit(0 if ejecutar_etl() else 1)
