#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          MÓDULO 2: DASHBOARD (FRONTEND + BACKEND)          ║"
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

# Paso 2: Crear entorno virtual (opcional)
echo ""
echo "📋 Paso 2: Entorno virtual..."
read -p "¿Quieres crear un entorno virtual? (s/n): " CREATE_VENV
if [ "$CREATE_VENV" = "s" ] || [ "$CREATE_VENV" = "S" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Entorno virtual creado"
    fi
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Entorno virtual activado"
fi

# Paso 3: Instalar dependencias principales
echo ""
echo "📋 Paso 3: Instalando dependencias principales..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencias principales instaladas"
else
    echo -e "${RED}✗${NC} Error instalando dependencias principales"
    exit 1
fi

# Paso 4: Instalar dependencias del backend
echo ""
echo "📋 Paso 4: Instalando dependencias del backend..."
pip install -r backend/requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencias del backend instaladas"
else
    echo -e "${RED}✗${NC} Error instalando dependencias del backend"
    exit 1
fi

# Paso 5: Configurar variables de entorno
echo ""
echo "📋 Paso 5: Configuración..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC}  Archivo .env creado desde .env.example"
    echo -e "${YELLOW}⚠${NC}  Por favor, edita el archivo .env con las conexiones a BD:"
    echo "    nano .env"
    echo ""
    echo "  Necesitas configurar:"
    echo "  - DB_ORIGEN_HOST: IP del servidor de BD Origen"
    echo "  - DB_ORIGEN_USER: Usuario de BD Origen"
    echo "  - DB_ORIGEN_PASSWORD: Password de BD Origen"
    echo "  - DB_DW_HOST: IP del servidor de Data Warehouse"
    echo "  - DB_DW_USER: Usuario de DW"
    echo "  - DB_DW_PASSWORD: Password de DW"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Paso 6: Verificar conexiones
echo ""
echo "📋 Paso 6: Verificando conexiones..."
echo -e "${YELLOW}⚠${NC}  Asegúrate de que:"
echo "  1. El servidor de BD Origen esté accesible"
echo "  2. El servidor de Data Warehouse esté accesible"
echo "  3. Los usuarios tengan permisos de lectura"
echo ""
read -p "¿Conexiones verificadas? (s/n): " VERIFIED
if [ "$VERIFIED" != "s" ] && [ "$VERIFIED" != "S" ]; then
    echo -e "${YELLOW}⚠${NC}  Por favor, verifica las conexiones antes de continuar"
fi

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║             ✅ INSTALACIÓN COMPLETADA                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Para iniciar el dashboard:"
echo ""
echo "   1. Backend API:"
echo "      cd backend"
echo "      python app.py"
echo "      (Se ejecutará en http://localhost:5001)"
echo ""
echo "   2. Frontend (en otra terminal):"
echo "      cd frontend"
echo "      python -m http.server 8080"
echo "      (Se ejecutará en http://localhost:8080)"
echo ""
echo "   O usa el script completo:"
echo "   ./iniciar_dashboard.sh"
echo ""
echo "🌐 Accede al dashboard en: http://localhost:8080/index.html"
echo ""
echo "🎉 ¡Módulo 2 listo para usar!"
