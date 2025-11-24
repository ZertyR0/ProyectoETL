#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🔧 INSTALACIÓN LIMPIA DEL SISTEMA DSS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
MYSQL_SOCKET="/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock"
MYSQL_HOST="localhost"
MYSQL_USER="root"
MYSQL_CMD="mysql -u $MYSQL_USER -h $MYSQL_HOST --socket=$MYSQL_SOCKET"

echo -e "${BLUE}📋 PASO 1: Limpieza de bases de datos existentes${NC}"
echo "──────────────────────────────────────────────────────────────"

# Eliminar bases de datos si existen
echo "  Eliminando bases de datos antiguas..."
$MYSQL_CMD -e "DROP DATABASE IF EXISTS gestionproyectos_hist;" 2>/dev/null
$MYSQL_CMD -e "DROP DATABASE IF EXISTS dw_proyectos_hist;" 2>/dev/null
echo -e "${GREEN}  ✓ Bases de datos eliminadas${NC}"
echo ""

echo -e "${BLUE}📋 PASO 2: Creación de base de datos de origen${NC}"
echo "──────────────────────────────────────────────────────────────"

# Crear base de datos origen
echo "  Creando gestionproyectos_hist..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS gestionproyectos_hist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Ejecutar script de creación
echo "  Creando tablas..."
$MYSQL_CMD gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Base de datos origen creada correctamente${NC}"
else
    echo -e "${RED}  ✗ Error creando base de datos origen${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}📋 PASO 3: Creación de datawarehouse${NC}"
echo "──────────────────────────────────────────────────────────────"

# Crear datawarehouse
echo "  Creando dw_proyectos_hist..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS dw_proyectos_hist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Ejecutar script de creación
echo "  Creando tablas dimensionales y hechos..."
$MYSQL_CMD dw_proyectos_hist < 04_Datawarehouse/scripts/crear_datawarehouse.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Datawarehouse creado correctamente${NC}"
else
    echo -e "${RED}  ✗ Error creando datawarehouse${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}📋 PASO 4: Generación de datos de prueba${NC}"
echo "──────────────────────────────────────────────────────────────"

# Generar datos
echo "  Generando datos de prueba (10 proyectos, 100 tareas)..."
python generar_datos_completos.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Datos generados correctamente${NC}"
else
    echo -e "${RED}  ✗ Error generando datos${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}📋 PASO 5: Verificación de instalación${NC}"
echo "──────────────────────────────────────────────────────────────"

# Verificar tablas origen
echo "  Verificando base de datos origen..."
CLIENTES=$($MYSQL_CMD gestionproyectos_hist -e "SELECT COUNT(*) FROM Cliente;" -s -N)
EMPLEADOS=$($MYSQL_CMD gestionproyectos_hist -e "SELECT COUNT(*) FROM Empleado;" -s -N)
PROYECTOS=$($MYSQL_CMD gestionproyectos_hist -e "SELECT COUNT(*) FROM Proyecto;" -s -N)
TAREAS=$($MYSQL_CMD gestionproyectos_hist -e "SELECT COUNT(*) FROM Tarea;" -s -N)

echo "    - Clientes:  $CLIENTES"
echo "    - Empleados: $EMPLEADOS"
echo "    - Proyectos: $PROYECTOS"
echo "    - Tareas:    $TAREAS"

if [ "$PROYECTOS" -gt 0 ] && [ "$TAREAS" -gt 0 ]; then
    echo -e "${GREEN}  ✓ Datos verificados correctamente${NC}"
else
    echo -e "${YELLOW}  ⚠ Advertencia: Datos incompletos${NC}"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN} INSTALACIÓN COMPLETADA${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📌 Próximos pasos:"
echo "   1. Iniciar el dashboard: cd 03_Dashboard && ./iniciar_dashboard.sh"
echo "   2. Abrir en navegador: http://localhost:8080"
echo ""
echo "💡 Nota: El datawarehouse está vacío. Los datos se cargarán"
echo "   cuando ejecutes el ETL desde el dashboard."
echo ""
