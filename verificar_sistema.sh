#!/bin/bash

echo "🔍 ======================================================"
echo "   VERIFICADOR DEL SISTEMA ETL"
echo "======================================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
total_checks=0
passed_checks=0
failed_checks=0

check() {
    total_checks=$((total_checks + 1))
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

# 1. Verificar Python
echo "🐍 Verificando Python..."
python3 --version > /dev/null 2>&1
check "Python 3 está instalado"

# 2. Verificar MySQL
echo ""
echo "🗄️  Verificando MySQL..."
mysql --version > /dev/null 2>&1
check "MySQL está instalado"

mysql -u root -e "SELECT 1" > /dev/null 2>&1
check "MySQL está accesible"

# 3. Verificar bases de datos
echo ""
echo "💾 Verificando Bases de Datos..."

if mysql -u root -e "USE gestionproyectos_hist" > /dev/null 2>&1; then
    proyectos=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.Proyecto" 2>/dev/null)
    check "BD Origen existe (gestionproyectos_hist)"
    if [ ! -z "$proyectos" ]; then
        echo -e "   ${BLUE}ℹ️  Proyectos en BD: $proyectos${NC}"
    fi
else
    total_checks=$((total_checks + 1))
    failed_checks=$((failed_checks + 1))
    echo -e "${YELLOW}⚠️  BD Origen no existe (ejecuta ./setup_local.sh)${NC}"
fi

if mysql -u root -e "USE dw_proyectos_hist" > /dev/null 2>&1; then
    hechos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoProyecto" 2>/dev/null)
    check "Datawarehouse existe (dw_proyectos_hist)"
    if [ ! -z "$hechos" ]; then
        echo -e "   ${BLUE}ℹ️  Hechos en DW: $hechos${NC}"
    fi
else
    total_checks=$((total_checks + 1))
    failed_checks=$((failed_checks + 1))
    echo -e "${YELLOW}⚠️  Datawarehouse no existe (ejecuta ./setup_local.sh)${NC}"
fi

# 4. Verificar entorno virtual
echo ""
echo "📦 Verificando Entorno Virtual..."
if [ -d "venv" ]; then
    check "Entorno virtual existe"
    
    # Verificar dependencias clave
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        python3 -c "import flask" > /dev/null 2>&1
        check "Flask instalado"
        
        python3 -c "import pandas" > /dev/null 2>&1
        check "Pandas instalado"
        
        python3 -c "import mysql.connector" > /dev/null 2>&1
        check "MySQL Connector instalado"
        
        python3 -c "import faker" > /dev/null 2>&1
        check "Faker instalado"
        
        deactivate
    fi
else
    total_checks=$((total_checks + 4))
    failed_checks=$((failed_checks + 4))
    echo -e "${YELLOW}⚠️  Entorno virtual no existe (ejecuta ./setup_local.sh)${NC}"
fi

# 5. Verificar archivos principales
echo ""
echo "📁 Verificando Archivos..."

archivos_criticos=(
    "01_GestionProyectos/scripts/crear_bd_origen.sql"
    "01_GestionProyectos/scripts/generar_datos.py"
    "02_ETL/config/config_conexion.py"
    "02_ETL/scripts/etl_principal.py"
    "02_ETL/scripts/etl_utils.py"
    "03_Dashboard/backend/app.py"
    "03_Dashboard/frontend/index.html"
    "03_Dashboard/frontend/app.js"
    "04_Datawarehouse/scripts/crear_datawarehouse.sql"
    "requirements.txt"
)

for archivo in "${archivos_criticos[@]}"; do
    total_checks=$((total_checks + 1))
    if [ -f "$archivo" ]; then
        passed_checks=$((passed_checks + 1))
        echo -e "${GREEN}✅${NC} $archivo"
    else
        failed_checks=$((failed_checks + 1))
        echo -e "${RED}❌${NC} $archivo ${RED}(faltante)${NC}"
    fi
done

# 6. Verificar scripts ejecutables
echo ""
echo "🔧 Verificando Scripts..."

scripts=(
    "setup_local.sh"
    "iniciar_dashboard.sh"
    "detener_dashboard.sh"
)

for script in "${scripts[@]}"; do
    total_checks=$((total_checks + 1))
    if [ -x "$script" ]; then
        passed_checks=$((passed_checks + 1))
        echo -e "${GREEN}✅${NC} $script es ejecutable"
    else
        failed_checks=$((failed_checks + 1))
        echo -e "${YELLOW}⚠️${NC} $script no es ejecutable (ejecuta: chmod +x $script)"
    fi
done

# 7. Verificar puertos disponibles
echo ""
echo "🌐 Verificando Puertos..."

if ! lsof -i :5001 > /dev/null 2>&1; then
    check "Puerto 5001 disponible (Backend)"
else
    total_checks=$((total_checks + 1))
    failed_checks=$((failed_checks + 1))
    echo -e "${YELLOW}⚠️  Puerto 5001 está ocupado${NC}"
    echo -e "   ${BLUE}ℹ️  Proceso: $(lsof -i :5001 | tail -1)${NC}"
fi

if ! lsof -i :8080 > /dev/null 2>&1; then
    check "Puerto 8080 disponible (Frontend)"
else
    total_checks=$((total_checks + 1))
    failed_checks=$((failed_checks + 1))
    echo -e "${YELLOW}⚠️  Puerto 8080 está ocupado${NC}"
    echo -e "   ${BLUE}ℹ️  Proceso: $(lsof -i :8080 | tail -1)${NC}"
fi

# Resumen
echo ""
echo "======================================================"
echo "📊 RESUMEN DE VERIFICACIÓN"
echo "======================================================"
echo -e "Total de verificaciones: ${BLUE}$total_checks${NC}"
echo -e "Verificaciones exitosas: ${GREEN}$passed_checks${NC}"
echo -e "Verificaciones fallidas: ${RED}$failed_checks${NC}"
echo ""

# Calcular porcentaje
percentage=$((passed_checks * 100 / total_checks))

if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡Todo listo! El sistema está 100% configurado${NC}"
    echo ""
    echo "Puedes ejecutar:"
    echo -e "  ${GREEN}./iniciar_dashboard.sh${NC}"
elif [ $percentage -ge 80 ]; then
    echo -e "${YELLOW}⚠️  Sistema casi listo ($percentage%)${NC}"
    echo ""
    echo "Recomendaciones:"
    if ! mysql -u root -e "USE gestionproyectos_hist" > /dev/null 2>&1; then
        echo "  1. Ejecuta: ${GREEN}./setup_local.sh${NC}"
    fi
    if ! [ -x "iniciar_dashboard.sh" ]; then
        echo "  2. Ejecuta: ${GREEN}chmod +x *.sh${NC}"
    fi
elif [ $percentage -ge 50 ]; then
    echo -e "${YELLOW}⚠️  Configuración incompleta ($percentage%)${NC}"
    echo ""
    echo "Ejecuta la configuración inicial:"
    echo -e "  ${GREEN}./setup_local.sh${NC}"
else
    echo -e "${RED}❌ Sistema no configurado ($percentage%)${NC}"
    echo ""
    echo "Pasos a seguir:"
    echo "  1. Asegúrate de que MySQL esté corriendo"
    echo "  2. Ejecuta: ${GREEN}chmod +x *.sh${NC}"
    echo "  3. Ejecuta: ${GREEN}./setup_local.sh${NC}"
fi

echo ""
echo "======================================================"

# Exit code basado en el resultado
if [ $failed_checks -eq 0 ]; then
    exit 0
else
    exit 1
fi
