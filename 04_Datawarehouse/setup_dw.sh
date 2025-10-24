#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            MÓDULO 3: DATA WAREHOUSE                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paso 1: Verificar Python
echo "📋 Paso 1: Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python encontrado: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 no encontrado. Por favor, instálalo primero."
    exit 1
fi

# Paso 2: Verificar MySQL
echo ""
echo "📋 Paso 2: Verificando MySQL..."
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓${NC} MySQL encontrado"
else
    echo -e "${RED}✗${NC} MySQL no encontrado. Por favor, instálalo primero."
    exit 1
fi

# Paso 3: Crear entorno virtual (opcional)
echo ""
echo "📋 Paso 3: Entorno virtual..."
read -p "¿Quieres crear un entorno virtual? (s/n): " CREATE_VENV
if [ "$CREATE_VENV" = "s" ] || [ "$CREATE_VENV" = "S" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Entorno virtual creado"
    fi
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Entorno virtual activado"
fi

# Paso 4: Instalar dependencias
echo ""
echo "📋 Paso 4: Instalando dependencias..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencias instaladas correctamente"
else
    echo -e "${RED}✗${NC} Error instalando dependencias"
    exit 1
fi

# Paso 5: Configurar variables de entorno
echo ""
echo "📋 Paso 5: Configuración..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC}  Archivo .env creado desde .env.example"
    echo -e "${YELLOW}⚠${NC}  Por favor, edita el archivo .env con tus credenciales:"
    echo "    nano .env"
    echo ""
    echo "  Necesitas configurar:"
    echo "  - DB_DW_HOST: IP del servidor de Data Warehouse"
    echo "  - DB_DW_USER: Usuario de DW"
    echo "  - DB_DW_PASSWORD: Password de DW"
    echo "  - DB_ORIGEN_HOST: IP del servidor de BD Origen"
    echo "  - DB_ORIGEN_USER: Usuario de BD Origen (con permisos de lectura)"
    echo "  - DB_ORIGEN_PASSWORD: Password de BD Origen"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Paso 6: Crear data warehouse
echo ""
echo "📋 Paso 6: Creando Data Warehouse..."
echo "Por favor, ingresa la contraseña de MySQL root:"
mysql -u root -p < scripts/crear_datawarehouse.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Data Warehouse creado correctamente"
else
    echo -e "${RED}✗${NC} Error creando Data Warehouse"
    exit 1
fi

# Paso 7: Instalar stored procedures
echo ""
echo "📋 Paso 7: Instalando stored procedures..."
echo "Por favor, ingresa la contraseña de MySQL root:"
mysql -u root -p < scripts/procedimientos_seguros_dw.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Stored procedures instalados"
else
    echo -e "${RED}✗${NC} Error instalando stored procedures"
    exit 1
fi

# Paso 8: Verificar conexión a BD Origen
echo ""
echo "📋 Paso 8: Verificando conexión a BD Origen..."
echo -e "${YELLOW}⚠${NC}  Asegúrate de que:"
echo "  1. El servidor de BD Origen esté accesible"
echo "  2. El usuario tenga permisos de lectura"
echo "  3. La BD 'gestionproyectos_hist' exista"
echo ""
read -p "¿Conexión verificada? (s/n): " VERIFIED
if [ "$VERIFIED" != "s" ] && [ "$VERIFIED" != "S" ]; then
    echo -e "${YELLOW}⚠${NC}  Por favor, verifica la conexión antes de ejecutar ETL"
fi

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║             ✅ INSTALACIÓN COMPLETADA                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Data Warehouse: dw_proyectos_hist"
echo "📝 Usuario: root (o el configurado en .env)"
echo ""
echo "🔍 Verificar instalación:"
echo "   mysql -u root -p -e 'USE dw_proyectos_hist; SHOW TABLES;'"
echo ""
echo "📚 Ver procedures instalados:"
echo "   mysql -u root -p -e 'SHOW PROCEDURE STATUS WHERE Db = \"dw_proyectos_hist\";'"
echo ""
echo "⚙️  Para ejecutar ETL:"
echo "   python etl/etl_dw.py"
echo ""
echo "🎉 ¡Módulo 3 listo para usar!"
