#!/bin/bash
###############################################################################
# DEMO RÁPIDA - Sistema de Trazabilidad
# Este script ejecuta una demostración completa del sistema
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${MAGENTA}💡 $1${NC}"
}

pause() {
    echo ""
    read -p "Presiona ENTER para continuar..."
    echo ""
}

# Banner inicial
clear
print_header "DEMOSTRACIÓN DEL SISTEMA DE TRAZABILIDAD"
echo -e "${CYAN}Esta demo te mostrará:${NC}"
echo "  1. Generación de datos sin duplicados"
echo "  2. Validación automática"
echo "  3. Verificación de trazabilidad"
echo "  4. Búsqueda entre bases de datos"
echo ""
print_warning "Asegúrate de tener MySQL corriendo y las bases de datos creadas"
pause

# Verificar entorno
print_header "PASO 1: Verificación del Entorno"

print_step "Verificando entorno virtual..."
if [ -d ".venv" ]; then
    print_success "Entorno virtual encontrado"
    source .venv/bin/activate
else
    print_warning "No se encuentra .venv, usando Python del sistema"
fi

print_step "Verificando dependencias..."
if python -c "import mysql.connector, pandas, faker, tabulate" 2>/dev/null; then
    print_success "Todas las dependencias están instaladas"
else
    print_warning "Instalando dependencias faltantes..."
    pip install -r requirements.txt
fi

pause

# Generar datos
print_header "PASO 2: Generación de Datos sin Duplicados"

print_info "Ejecutando: generar_datos_mejorado.py"
echo ""

python 01_GestionProyectos/scripts/generar_datos_mejorado.py

print_success "Datos generados con validación automática"
pause

# Verificar duplicados
print_header "PASO 3: Verificación de Duplicados"

print_info "Buscando duplicados en la base de datos origen..."
echo ""

python verificar_trazabilidad.py duplicados

print_success "Verificación de duplicados completada"
pause

# Ejecutar ETL
print_header "PASO 4: Proceso ETL (Opcional)"

echo -e "${YELLOW}¿Deseas ejecutar el proceso ETL ahora? (s/n)${NC}"
read -p "Respuesta: " respuesta

if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    print_step "Ejecutando ETL..."
    echo ""
    python 02_ETL/scripts/etl_principal.py
    print_success "ETL completado"
    
    pause
    
    # Verificar conteos
    print_header "PASO 5: Verificación de Conteos Post-ETL"
    
    print_info "Comparando conteos entre BD Origen y BD Destino..."
    echo ""
    
    python verificar_trazabilidad.py conteos
    
    print_success "Verificación de conteos completada"
else
    print_warning "ETL omitido. Puedes ejecutarlo más tarde con:"
    echo "  python 02_ETL/scripts/etl_principal.py"
fi

pause

# Demo de búsqueda
print_header "PASO 6: Demo de Búsqueda de Trazabilidad"

print_info "Iniciando modo interactivo..."
echo ""
echo -e "${CYAN}Podrás buscar proyectos, clientes o empleados entre ambas BD${NC}"
echo ""

sleep 2
python verificar_trazabilidad.py

# Resumen final
clear
print_header "DEMOSTRACIÓN COMPLETADA"

echo -e "${GREEN}✅ Sistema de Trazabilidad demostrado exitosamente${NC}"
echo ""
echo -e "${CYAN}Resumen de lo que vimos:${NC}"
echo "  1. ✅ Generación de datos sin duplicados"
echo "  2. ✅ Validación automática integrada"
echo "  3. ✅ Verificación de duplicados"
if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    echo "  4. ✅ Proceso ETL ejecutado"
    echo "  5. ✅ Verificación de conteos"
fi
echo "  6. ✅ Búsqueda interactiva entre BD"
echo ""

print_info "Documentación disponible:"
echo "  • GUIA_TRAZABILIDAD.md         - Guía paso a paso"
echo "  • README_TRAZABILIDAD.md       - Documentación completa"
echo "  • RESUMEN_FINAL_IMPLEMENTACION.md - Resumen ejecutivo"
echo "  • DIAGRAMA_FLUJO_TRAZABILIDAD.md  - Diagramas visuales"
echo ""

print_info "Comandos útiles:"
echo "  • ./validar_trazabilidad.sh              - Menú de validación"
echo "  • python verificar_trazabilidad.py       - Modo interactivo"
echo "  • python verificar_trazabilidad.py reporte - Reporte completo"
echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       ¡Gracias por probar el Sistema de Trazabilidad!         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
