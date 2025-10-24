#!/bin/bash

# Script para empaquetar los 3 módulos independientes
# Uso: ./empaquetar_modulos.sh

# Colores para output
VERDE='\033[0;32m'
AZUL='\033[0;34m'
AMARILLO='\033[1;33m'
RESET='\033[0m'

echo -e "${AZUL}========================================${RESET}"
echo -e "${AZUL}  Empaquetador de Módulos Independientes${RESET}"
echo -e "${AZUL}========================================${RESET}"
echo ""

# Crear carpeta para los ZIPs
CARPETA_SALIDA="modulos_empaquetados"
mkdir -p "$CARPETA_SALIDA"

# Función para calcular tamaño
calcular_tamaño() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        du -sh "$1" | awk '{print $1}'
    else
        # Linux
        du -sh "$1" | awk '{print $1}'
    fi
}

echo -e "${AMARILLO}Empaquetando módulos...${RESET}"
echo ""

# ============================================
# MÓDULO 1: Base de Datos de Gestión
# ============================================
echo -e "${VERDE}[1/3] Empaquetando Módulo 1: Base de Datos de Gestión...${RESET}"

if [ -d "01_GestionProyectos" ]; then
    zip -r "$CARPETA_SALIDA/Modulo1_BD_Origen.zip" 01_GestionProyectos/ \
        -x "*/venv/*" \
        -x "*/datos/*" \
        -x "*/__pycache__/*" \
        -x "*.pyc" \
        -x "*/.env" \
        -x "*/.DS_Store" \
        -q
    
    TAMANO1=$(calcular_tamaño "$CARPETA_SALIDA/Modulo1_BD_Origen.zip")
    echo -e "   ✅ Creado: Modulo1_BD_Origen.zip (${TAMANO1})"
    
    # Listar contenido
    echo -e "   📦 Incluye:"
    echo "      - Scripts SQL (crear_bd_origen.sql, procedimientos_seguros.sql)"
    echo "      - Scripts Python (generar_datos_seguro.py)"
    echo "      - requirements.txt"
    echo "      - .env.example"
    echo "      - setup_bd_origen.sh"
    echo "      - INSTALACION.md"
else
    echo -e "   ❌ ERROR: No se encontró la carpeta 01_GestionProyectos"
fi

echo ""

# ============================================
# MÓDULO 2: Dashboard
# ============================================
echo -e "${VERDE}[2/3] Empaquetando Módulo 2: Dashboard...${RESET}"

if [ -d "03_Dashboard" ]; then
    zip -r "$CARPETA_SALIDA/Modulo2_Dashboard.zip" 03_Dashboard/ \
        -x "*/venv/*" \
        -x "*/logs/*" \
        -x "*/__pycache__/*" \
        -x "*.pyc" \
        -x "*/.env" \
        -x "*/.DS_Store" \
        -x "*/dashboard.pid" \
        -q
    
    TAMANO2=$(calcular_tamaño "$CARPETA_SALIDA/Modulo2_Dashboard.zip")
    echo -e "   ✅ Creado: Modulo2_Dashboard.zip (${TAMANO2})"
    
    # Listar contenido
    echo -e "   📦 Incluye:"
    echo "      - Backend Flask (app.py)"
    echo "      - Frontend (index.html, app.js, styles.css)"
    echo "      - requirements.txt"
    echo "      - .env.example"
    echo "      - setup_dashboard.sh"
    echo "      - iniciar_dashboard.sh / detener_dashboard.sh"
    echo "      - INSTALACION.md"
else
    echo -e "   ❌ ERROR: No se encontró la carpeta 03_Dashboard"
fi

echo ""

# ============================================
# MÓDULO 3: Data Warehouse
# ============================================
echo -e "${VERDE}[3/3] Empaquetando Módulo 3: Data Warehouse...${RESET}"

if [ -d "04_Datawarehouse" ]; then
    # Incluir también el código ETL de 02_ETL
    zip -r "$CARPETA_SALIDA/Modulo3_DataWarehouse.zip" 04_Datawarehouse/ 02_ETL/ \
        -x "*/venv/*" \
        -x "*/__pycache__/*" \
        -x "*.pyc" \
        -x "*/.env" \
        -x "*/.DS_Store" \
        -q
    
    TAMANO3=$(calcular_tamaño "$CARPETA_SALIDA/Modulo3_DataWarehouse.zip")
    echo -e "   ✅ Creado: Modulo3_DataWarehouse.zip (${TAMANO3})"
    
    # Listar contenido
    echo -e "   📦 Incluye:"
    echo "      - Scripts SQL (crear_datawarehouse.sql, procedimientos_seguros_dw.sql)"
    echo "      - Consultas de análisis (consultas_analisis.sql)"
    echo "      - Código ETL (de 02_ETL/)"
    echo "      - requirements.txt"
    echo "      - .env.example"
    echo "      - setup_dw.sh"
    echo "      - INSTALACION.md"
else
    echo -e "   ❌ ERROR: No se encontró la carpeta 04_Datawarehouse"
fi

echo ""
echo -e "${AZUL}========================================${RESET}"
echo -e "${VERDE}✅ Empaquetado completado${RESET}"
echo -e "${AZUL}========================================${RESET}"
echo ""
echo -e "📁 Archivos creados en: ${AMARILLO}$CARPETA_SALIDA/${RESET}"
echo ""
ls -lh "$CARPETA_SALIDA"/*.zip
echo ""

# ============================================
# Instrucciones de uso
# ============================================
echo -e "${AZUL}========================================${RESET}"
echo -e "${AZUL}  Instrucciones de Envío${RESET}"
echo -e "${AZUL}========================================${RESET}"
echo ""
echo "Para enviar cada módulo por separado:"
echo ""
echo -e "${VERDE}Módulo 1 (BD Origen):${RESET}"
echo "   - Enviar: $CARPETA_SALIDA/Modulo1_BD_Origen.zip"
echo "   - Receptor ejecuta: unzip Modulo1_BD_Origen.zip && cd 01_GestionProyectos && ./setup_bd_origen.sh"
echo ""
echo -e "${VERDE}Módulo 2 (Dashboard):${RESET}"
echo "   - Enviar: $CARPETA_SALIDA/Modulo2_Dashboard.zip"
echo "   - Receptor ejecuta: unzip Modulo2_Dashboard.zip && cd 03_Dashboard && ./setup_dashboard.sh"
echo "   - Configurar .env con IPs de Módulos 1 y 3"
echo ""
echo -e "${VERDE}Módulo 3 (Data Warehouse):${RESET}"
echo "   - Enviar: $CARPETA_SALIDA/Modulo3_DataWarehouse.zip"
echo "   - Receptor ejecuta: unzip Modulo3_DataWarehouse.zip && cd 04_Datawarehouse && ./setup_dw.sh"
echo "   - Configurar .env con IP de Módulo 1"
echo ""
echo -e "${AMARILLO}📖 Ver documentación completa:${RESET} GUIA_MODULOS_INDEPENDIENTES.md"
echo ""

# ============================================
# Crear README para los ZIPs
# ============================================
cat > "$CARPETA_SALIDA/README.txt" << 'EOF'
================================================================================
  MÓDULOS INDEPENDIENTES - PROYECTO ETL
================================================================================

Este paquete contiene 3 módulos independientes que pueden ser instalados
y ejecutados por separado:

📦 Modulo1_BD_Origen.zip
   - Base de Datos Transaccional (OLTP)
   - Puede funcionar completamente solo
   - Prerequisitos: Python 3.8+, MySQL 8.0+

📦 Modulo2_Dashboard.zip
   - Dashboard Web (Frontend + Backend Flask)
   - Requiere acceso a Módulo 1 y Módulo 3
   - Prerequisitos: Python 3.8+

📦 Modulo3_DataWarehouse.zip
   - Data Warehouse + ETL
   - Requiere acceso a Módulo 1 para extraer datos
   - Prerequisitos: Python 3.8+, MySQL 8.0+

================================================================================
  INSTALACIÓN
================================================================================

1. Descomprimir el módulo deseado:
   unzip ModuloX_*.zip

2. Entrar a la carpeta:
   cd 01_GestionProyectos    # o 03_Dashboard o 04_Datawarehouse

3. Ejecutar script de instalación:
   ./setup_*.sh

4. Seguir las instrucciones en pantalla

Cada módulo incluye un archivo INSTALACION.md con instrucciones detalladas.

================================================================================
  ORDEN DE INSTALACIÓN RECOMENDADO
================================================================================

1. Primero: Módulo 1 (BD Origen)
2. Segundo: Módulo 3 (Data Warehouse)
3. Tercero: Módulo 2 (Dashboard)

================================================================================
  CONFIGURACIÓN MULTI-SERVIDOR
================================================================================

Si despliegas los módulos en servidores diferentes:

1. Edita el archivo .env de cada módulo
2. Configura las IPs correctas:
   - Módulo 2 necesita IPs de Módulos 1 y 3
   - Módulo 3 necesita IP de Módulo 1
3. Crea usuarios de BD con acceso remoto (ver INSTALACION.md)

================================================================================
  SOPORTE
================================================================================

Ver documentación completa en cada módulo:
- 01_GestionProyectos/INSTALACION.md
- 03_Dashboard/INSTALACION.md
- 04_Datawarehouse/INSTALACION.md

O consultar: GUIA_MODULOS_INDEPENDIENTES.md

================================================================================
EOF

echo -e "${VERDE}✅ README.txt creado en $CARPETA_SALIDA/${RESET}"
echo ""
echo -e "${AZUL}🎉 Listo para enviar!${RESET}"
