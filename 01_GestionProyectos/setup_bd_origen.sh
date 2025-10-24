#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   MÓDULO 1: BASE DE DATOS DE GESTIÓN (ORIGEN)              ║"
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
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Paso 6: Crear base de datos
echo ""
echo "📋 Paso 6: Creando base de datos..."
echo "Por favor, ingresa la contraseña de MySQL root:"
mysql -u root -p < scripts/crear_bd_origen.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Base de datos creada correctamente"
else
    echo -e "${RED}✗${NC} Error creando base de datos"
    exit 1
fi

# Paso 7: Instalar stored procedures y triggers
echo ""
echo "📋 Paso 7: Instalando stored procedures y triggers..."
echo "Por favor, ingresa la contraseña de MySQL root:"
mysql -u root -p < scripts/procedimientos_seguros.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Stored procedures y triggers instalados"
else
    echo -e "${RED}✗${NC} Error instalando stored procedures"
    exit 1
fi

# Paso 8: Generar datos de prueba
echo ""
echo "📋 Paso 8: Generando datos de prueba..."
read -p "¿Quieres generar datos de prueba? (s/n): " GENERAR_DATOS
if [ "$GENERAR_DATOS" = "s" ] || [ "$GENERAR_DATOS" = "S" ]; then
    python3 scripts/generar_datos_seguro.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Datos de prueba generados"
    else
        echo -e "${YELLOW}⚠${NC}  Error generando datos (puedes hacerlo después)"
    fi
fi

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║             ✅ INSTALACIÓN COMPLETADA                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Base de Datos: gestionproyectos_hist"
echo "📝 Usuario: root (o el configurado en .env)"
echo ""
echo "🔍 Verificar instalación:"
echo "   mysql -u root -p -e 'USE gestionproyectos_hist; SHOW TABLES;'"
echo ""
echo "📚 Ver procedures instalados:"
echo "   mysql -u root -p -e 'SHOW PROCEDURE STATUS WHERE Db = \"gestionproyectos_hist\";'"
echo ""
echo "🎉 ¡Módulo 1 listo para usar!"
