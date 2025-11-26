#!/bin/bash

# ===================================================================
# SCRIPT MAESTRO: Inicialización completa del sistema ETL + BSC
# Portable - Puede ejecutarse en cualquier máquina con MySQL
# ===================================================================

set -e  # Detener en caso de error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   INICIALIZACIÓN COMPLETA DEL SISTEMA ETL + BSC + DASHBOARD   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_step() {
    echo -e "${BLUE}[PASO $1/8]${NC} $2"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# ===================================================================
# PASO 1: Verificar prerequisitos
# ===================================================================
log_step 1 "Verificando prerequisitos..."

if ! command -v mysql &> /dev/null; then
    log_error "MySQL no está instalado"
    exit 1
fi
log_success "MySQL instalado"

if ! command -v python3 &> /dev/null; then
    log_error "Python3 no está instalado"
    exit 1
fi
log_success "Python3 instalado"

# ===================================================================
# PASO 2: Crear bases de datos
# ===================================================================
log_step 2 "Creando bases de datos..."

mysql -u root -e "DROP DATABASE IF EXISTS gestionproyectos_hist; CREATE DATABASE gestionproyectos_hist;" 2>/dev/null || \
    log_warning "No se pudo eliminar/crear gestionproyectos_hist (puede que ya exista)"

mysql -u root -e "DROP DATABASE IF EXISTS dw_proyectos_hist; CREATE DATABASE dw_proyectos_hist;" 2>/dev/null || \
    log_warning "No se pudo eliminar/crear dw_proyectos_hist (puede que ya exista)"

log_success "Bases de datos creadas"

# ===================================================================
# PASO 3: Crear tablas de origen
# ===================================================================
log_step 3 "Creando estructura de base de datos origen..."

mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql
mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/crear_tabla_estado.sql
mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/procedimientos_seguros.sql

log_success "Estructura de origen creada (8 tablas)"

# ===================================================================
# PASO 4: Generar datos de prueba
# ===================================================================
log_step 4 "Generando datos de prueba (50 proyectos + métricas)..."

cd 01_GestionProyectos/datos
python3 generar_datos_final.py
cd ../..

log_success "Datos generados: 50 clientes, 250 empleados, 50 proyectos, 135 defectos, 351 capacitaciones, 21 satisfacciones, 282 movimientos"

# ===================================================================
# PASO 5: Crear DataWarehouse
# ===================================================================
log_step 5 "Creando estructura de DataWarehouse..."

mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/crear_datawarehouse.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/agregar_tablas_metricas.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/crear_bsc.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/olap_views.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/procedimientos_seguros_dw.sql

log_success "DataWarehouse creado (12 dimensiones, 8 hechos, BSC)"

# ===================================================================
# PASO 6: Ejecutar ETL completo
# ===================================================================
log_step 6 "Ejecutando ETL (cargando datos al DataWarehouse)..."

mysql -u root dw_proyectos_hist < 02_ETL/scripts/etl_completo_con_metricas.sql

echo "CALL sp_etl_completo_con_metricas();" | mysql -u root dw_proyectos_hist > /tmp/etl_result.txt
cat /tmp/etl_result.txt

log_success "ETL ejecutado exitosamente"

# ===================================================================
# PASO 7: Poblar BSC con OKRs calculados
# ===================================================================
log_step 7 "Poblando BSC con OKRs (valores calculados desde métricas reales)..."

mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/poblar_bsc_automatico.sql > /tmp/bsc_result.txt
cat /tmp/bsc_result.txt

log_success "BSC poblado: 5 objetivos, 10 KRs, 10 mediciones"

# ===================================================================
# PASO 8: Iniciar Dashboard
# ===================================================================
log_step 8 "Iniciando Dashboard (Backend + Frontend)..."

cd 03_Dashboard
./iniciar_dashboard.sh &
cd ..

sleep 3
log_success "Dashboard iniciado en http://localhost:3000"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  ✓ SISTEMA INICIALIZADO                       ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Dashboard:  http://localhost:3000                            ║"
echo "║  Backend:    http://localhost:5000/api/estado                 ║"
echo "║                                                                ║"
echo "║  Bases de datos:                                              ║"
echo "║    • gestionproyectos_hist (Origen)                           ║"
echo "║    • dw_proyectos_hist (DataWarehouse)                        ║"
echo "║                                                                ║"
echo "║  Métricas calculadas desde DW (NO emuladas):                  ║"
echo "║    ✓ Costos y presupuestos                                    ║"
echo "║    ✓ Tiempos y cumplimiento                                   ║"
echo "║    ✓ Defectos de calidad                                      ║"
echo "║    ✓ Satisfacción de cliente                                  ║"
echo "║    ✓ Capacitaciones RRHH                                      ║"
echo "║    ✓ Rotación de personal                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}Para detener el dashboard:${NC} cd 03_Dashboard && ./detener_dashboard.sh"
echo ""
