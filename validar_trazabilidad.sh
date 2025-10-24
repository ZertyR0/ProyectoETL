#!/bin/bash
###############################################################################
# Script de Validación de Trazabilidad - Sistema ETL
# Ejecuta todas las validaciones y genera un reporte completo
###############################################################################

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Banner
print_color "$BLUE" "╔══════════════════════════════════════════════════════════════════╗"
print_color "$BLUE" "║   Sistema de Validación de Trazabilidad y Calidad de Datos      ║"
print_color "$BLUE" "║   Proyecto ETL - Gestión de Proyectos                           ║"
print_color "$BLUE" "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "verificar_trazabilidad.py" ]; then
    print_color "$RED" "❌ Error: No se encuentra verificar_trazabilidad.py"
    print_color "$YELLOW" "   Ejecute este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    print_color "$RED" "❌ Error: No se encuentra el entorno virtual"
    print_color "$YELLOW" "   Ejecute: python -m venv .venv"
    exit 1
fi

# Activar entorno virtual
print_color "$BLUE" "🔧 Activando entorno virtual..."
source .venv/bin/activate

# Verificar dependencias
print_color "$BLUE" "📦 Verificando dependencias..."
if ! python -c "import tabulate" 2>/dev/null; then
    print_color "$YELLOW" "⚠️  Instalando dependencia faltante: tabulate"
    pip install tabulate
fi

# Crear directorio de reportes si no existe
REPORTS_DIR="reportes_trazabilidad"
mkdir -p "$REPORTS_DIR"

# Timestamp para el reporte
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORTS_DIR/reporte_$TIMESTAMP.txt"

print_color "$GREEN" "✅ Preparación completada"
echo ""

# Menú de opciones
print_color "$BLUE" "Seleccione una opción:"
echo "1) Reporte completo (recomendado)"
echo "2) Solo verificar conteos"
echo "3) Solo buscar duplicados"
echo "4) Solo listar proyectos no migrados"
echo "5) Modo interactivo"
echo "0) Salir"
echo ""

read -p "Opción: " opcion

case $opcion in
    1)
        print_color "$BLUE" "📊 Generando reporte completo..."
        echo ""
        python verificar_trazabilidad.py reporte | tee "$REPORT_FILE"
        echo ""
        print_color "$GREEN" "✅ Reporte guardado en: $REPORT_FILE"
        ;;
    
    2)
        print_color "$BLUE" "📊 Verificando conteos..."
        echo ""
        python verificar_trazabilidad.py conteos | tee "$REPORT_FILE"
        echo ""
        print_color "$GREEN" "✅ Resultados guardados en: $REPORT_FILE"
        ;;
    
    3)
        print_color "$BLUE" "🔍 Buscando duplicados..."
        echo ""
        python verificar_trazabilidad.py duplicados | tee "$REPORT_FILE"
        echo ""
        print_color "$GREEN" "✅ Resultados guardados en: $REPORT_FILE"
        ;;
    
    4)
        print_color "$BLUE" "📋 Listando proyectos no migrados..."
        echo ""
        python verificar_trazabilidad.py no-migrados | tee "$REPORT_FILE"
        echo ""
        print_color "$GREEN" "✅ Resultados guardados en: $REPORT_FILE"
        ;;
    
    5)
        print_color "$BLUE" "🎮 Iniciando modo interactivo..."
        echo ""
        python verificar_trazabilidad.py
        ;;
    
    0)
        print_color "$YELLOW" "👋 Saliendo..."
        exit 0
        ;;
    
    *)
        print_color "$RED" "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
print_color "$BLUE" "╔══════════════════════════════════════════════════════════════════╗"
print_color "$BLUE" "║                     Proceso Completado                           ║"
print_color "$BLUE" "╚══════════════════════════════════════════════════════════════════╝"
