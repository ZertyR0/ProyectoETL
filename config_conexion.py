# CONFIGURACIÓN DE CONEXIÓN REMOTA
# =====================================
# Edita estos valores para conectarte a tu propio servidor

# Información del servidor de base de datos
HOST = "172.26.163.200"
PUERTO = 3306
USUARIO = "etl_user"
PASSWORD = "etl_password_123"

# Nombres de las bases de datos
BD_ORIGEN = "gestionproyectos_hist"
BD_DESTINO = "dw_proyectos_hist"

# Configuración adicional
TIMEOUT_CONEXION = 30  # segundos
REINTENTOS_CONEXION = 3

# =================================
# NO MODIFICAR DEBAJO DE ESTA LÍNEA
# =================================

def get_config():
    """Retorna la configuración como diccionario"""
    return {
        'host': HOST,
        'port': PUERTO,
        'user': USUARIO,
        'password': PASSWORD,
        'db_origen': BD_ORIGEN,
        'db_destino': BD_DESTINO,
        'timeout': TIMEOUT_CONEXION,
        'reintentos': REINTENTOS_CONEXION
    }
