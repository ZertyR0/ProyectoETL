#!/bin/bash

# ============================================================================
# INSTALADOR DE SISTEMA SEGURO - ProyectoETL
# ============================================================================
# Este script instala y configura todo el sistema con seguridad completa:
# - Procedimientos almacenados
# - Triggers de validación
# - Auditoría automática
# - Sin SELECT directos
# ============================================================================

set -e  # Detener en errores

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "================================================================"
echo "  🔒 INSTALADOR DE SISTEMA SEGURO - ProyectoETL"
echo "================================================================"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde el directorio raíz del proyecto${NC}"
    exit 1
fi

# ============================================================================
# FUNCIÓN: Solicitar credenciales MySQL
# ============================================================================
solicitar_credenciales() {
    echo -e "\n${YELLOW}📝 Configuración de MySQL${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    read -p "Host MySQL [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Puerto MySQL [3306]: " DB_PORT
    DB_PORT=${DB_PORT:-3306}
    
    read -p "Usuario MySQL [root]: " DB_USER
    DB_USER=${DB_USER:-root}
    
    read -sp "Contraseña MySQL: " DB_PASS
    echo
    
    # Verificar conexión
    if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Conexión exitosa a MySQL${NC}"
        return 0
    else
        echo -e "${RED}❌ No se pudo conectar a MySQL${NC}"
        return 1
    fi
}

# ============================================================================
# FUNCIÓN: Crear bases de datos
# ============================================================================
crear_bases_datos() {
    echo -e "\n${YELLOW}🗄️  Creando bases de datos...${NC}"
    
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" <<EOF
CREATE DATABASE IF NOT EXISTS gestionproyectos_hist;
CREATE DATABASE IF NOT EXISTS dw_proyectos_hist;
EOF
    
    echo -e "${GREEN}✅ Bases de datos creadas${NC}"
}

# ============================================================================
# FUNCIÓN: Instalar procedimientos BD Origen
# ============================================================================
instalar_procedimientos_origen() {
    echo -e "\n${YELLOW}🔧 Instalando procedimientos seguros en BD Origen...${NC}"
    
    ARCHIVO="01_GestionProyectos/scripts/procedimientos_seguros.sql"
    
    if [ ! -f "$ARCHIVO" ]; then
        echo -e "${RED}❌ No se encuentra: $ARCHIVO${NC}"
        return 1
    fi
    
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" < "$ARCHIVO"
    
    # Verificar
    PROCS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='gestionproyectos_hist'")
    
    echo -e "${GREEN}✅ Instalados $PROCS procedimientos en gestionproyectos_hist${NC}"
    
    # Verificar triggers
    TRIGGERS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='gestionproyectos_hist'")
    
    echo -e "${GREEN}✅ Instalados $TRIGGERS triggers${NC}"
}

# ============================================================================
# FUNCIÓN: Instalar procedimientos ETL
# ============================================================================
instalar_procedimientos_etl() {
    echo -e "\n${YELLOW}⚙️  Instalando procedimientos ETL...${NC}"
    
    ARCHIVO="02_ETL/scripts/procedimientos_etl.sql"
    
    if [ ! -f "$ARCHIVO" ]; then
        echo -e "${RED}❌ No se encuentra: $ARCHIVO${NC}"
        return 1
    fi
    
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" < "$ARCHIVO"
    
    # Verificar extracción
    EXTRACT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='gestionproyectos_hist' AND ROUTINE_NAME LIKE 'sp_etl_%'")
    
    echo -e "${GREEN}✅ Instalados $EXTRACT procedimientos de extracción${NC}"
    
    # Verificar carga
    LOAD=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='dw_proyectos_hist' AND ROUTINE_NAME LIKE 'sp_dw_cargar_%'")
    
    echo -e "${GREEN}✅ Instalados $LOAD procedimientos de carga${NC}"
}

# ============================================================================
# FUNCIÓN: Instalar procedimientos DW
# ============================================================================
instalar_procedimientos_dw() {
    echo -e "\n${YELLOW}📊 Instalando procedimientos DW...${NC}"
    
    ARCHIVO="04_Datawarehouse/scripts/procedimientos_seguros_dw.sql"
    
    if [ ! -f "$ARCHIVO" ]; then
        echo -e "${RED}❌ No se encuentra: $ARCHIVO${NC}"
        return 1
    fi
    
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" < "$ARCHIVO"
    
    # Verificar
    PROCS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='dw_proyectos_hist' AND ROUTINE_NAME LIKE 'sp_dw_%'")
    
    echo -e "${GREEN}✅ Instalados $PROCS procedimientos DW${NC}"
}

# ============================================================================
# FUNCIÓN: Crear estructura de tablas
# ============================================================================
crear_estructura_tablas() {
    echo -e "\n${YELLOW}🗂️  Creando estructura de tablas...${NC}"
    
    # BD Origen
    ARCHIVO_ORIGEN="01_GestionProyectos/scripts/crear_bd_origen.sql"
    if [ -f "$ARCHIVO_ORIGEN" ]; then
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" < "$ARCHIVO_ORIGEN"
        echo -e "${GREEN}✅ Tablas de origen creadas${NC}"
    fi
    
    # DW
    ARCHIVO_DW="04_Datawarehouse/scripts/crear_datawarehouse.sql"
    if [ -f "$ARCHIVO_DW" ]; then
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" < "$ARCHIVO_DW"
        echo -e "${GREEN}✅ Tablas de DW creadas${NC}"
    fi
}

# ============================================================================
# FUNCIÓN: Verificar dependencias Python
# ============================================================================
verificar_python() {
    echo -e "\n${YELLOW}🐍 Verificando Python y dependencias...${NC}"
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no está instalado${NC}"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
    
    # Verificar/instalar dependencias
    if [ -f "requirements.txt" ]; then
        echo "   Instalando dependencias..."
        pip3 install -r requirements.txt --quiet
        echo -e "${GREEN}✅ Dependencias instaladas${NC}"
    fi
}

# ============================================================================
# FUNCIÓN: Generar datos de prueba
# ============================================================================
generar_datos_prueba() {
    echo -e "\n${YELLOW}📝 ¿Desea generar datos de prueba?${NC}"
    echo "   1) Sí - Dataset pequeño (10 clientes, 5 empleados, 3 proyectos)"
    echo "   2) Sí - Dataset mediano (100 clientes, 50 empleados, 30 proyectos)"
    echo "   3) No - Omitir"
    
    read -p "Seleccione opción [1]: " OPCION
    OPCION=${OPCION:-1}
    
    case $OPCION in
        1)
            echo -e "${BLUE}Generando datos pequeños...${NC}"
            python3 01_GestionProyectos/scripts/generar_datos_seguro.py \
                --clientes 10 --empleados 5 --proyectos 3
            ;;
        2)
            echo -e "${BLUE}Generando datos medianos...${NC}"
            python3 01_GestionProyectos/scripts/generar_datos_seguro.py \
                --clientes 100 --empleados 50 --proyectos 30
            ;;
        3)
            echo -e "${YELLOW}⏭️  Omitiendo generación de datos${NC}"
            return 0
            ;;
        *)
            echo -e "${YELLOW}Opción inválida, omitiendo...${NC}"
            return 0
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Datos generados exitosamente${NC}"
    else
        echo -e "${RED}❌ Error generando datos${NC}"
        return 1
    fi
}

# ============================================================================
# FUNCIÓN: Ejecutar ETL inicial
# ============================================================================
ejecutar_etl_inicial() {
    echo -e "\n${YELLOW}🔄 ¿Desea ejecutar ETL inicial?${NC}"
    read -p "   (s/n) [s]: " EJECUTAR
    EJECUTAR=${EJECUTAR:-s}
    
    if [[ "$EJECUTAR" =~ ^[Ss]$ ]]; then
        echo -e "${BLUE}Ejecutando ETL...${NC}"
        python3 02_ETL/scripts/etl_principal_seguro.py --limpiar
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ETL completado${NC}"
        else
            echo -e "${RED}❌ Error en ETL${NC}"
            return 1
        fi
    fi
}

# ============================================================================
# FUNCIÓN: Mostrar resumen de instalación
# ============================================================================
mostrar_resumen() {
    echo -e "\n${GREEN}================================================================"
    echo "  ✅ INSTALACIÓN COMPLETADA"
    echo "================================================================${NC}"
    echo
    echo -e "${YELLOW}📊 Componentes Instalados:${NC}"
    echo "   • Procedimientos almacenados (BD Origen)"
    echo "   • Procedimientos ETL (Extracción/Carga)"
    echo "   • Procedimientos DW (Consultas seguras)"
    echo "   • Triggers de validación"
    echo "   • Tablas de auditoría"
    echo
    echo -e "${YELLOW}🔧 Próximos Pasos:${NC}"
    echo
    echo "1. Generar datos (si no se hizo):"
    echo -e "   ${BLUE}python3 generar_datos_seguro.py --clientes 100 --empleados 50${NC}"
    echo
    echo "2. Ejecutar ETL:"
    echo -e "   ${BLUE}python3 02_ETL/scripts/etl_principal_seguro.py --limpiar${NC}"
    echo
    echo "3. Verificar trazabilidad:"
    echo -e "   ${BLUE}python3 verificar_trazabilidad_seguro.py${NC}"
    echo
    echo "4. Ver auditoría:"
    echo -e "   ${BLUE}mysql -u $DB_USER -p -e \"SELECT * FROM gestionproyectos_hist.AuditoriaOperaciones LIMIT 10\"${NC}"
    echo
    echo -e "${YELLOW}📚 Documentación:${NC}"
    echo "   • GUIA_SEGURIDAD_COMPLETA.md - Guía completa de seguridad"
    echo "   • GUIA_TRAZABILIDAD.md - Uso del sistema de trazabilidad"
    echo "   • README.md - Documentación general"
    echo
    echo -e "${GREEN}🔒 Sistema seguro instalado - Sin SELECT directos ✅${NC}"
    echo
}

# ============================================================================
# FUNCIÓN: Verificar instalación
# ============================================================================
verificar_instalacion() {
    echo -e "\n${YELLOW}🔍 Verificando instalación...${NC}"
    
    # Contar procedimientos
    TOTAL_PROCS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.ROUTINES 
            WHERE ROUTINE_SCHEMA IN ('gestionproyectos_hist', 'dw_proyectos_hist')")
    
    echo -e "   Total de procedimientos: ${GREEN}$TOTAL_PROCS${NC}"
    
    # Contar triggers
    TOTAL_TRIGGERS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.TRIGGERS 
            WHERE TRIGGER_SCHEMA = 'gestionproyectos_hist'")
    
    echo -e "   Total de triggers: ${GREEN}$TOTAL_TRIGGERS${NC}"
    
    # Verificar tablas de auditoría
    AUDIT_TABLES=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" -sN \
        -e "SELECT COUNT(*) FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'gestionproyectos_hist' 
            AND TABLE_NAME IN ('AuditoriaOperaciones', 'ControlDuplicados')")
    
    echo -e "   Tablas de auditoría: ${GREEN}$AUDIT_TABLES/2${NC}"
    
    if [ "$TOTAL_PROCS" -gt 20 ] && [ "$TOTAL_TRIGGERS" -ge 5 ] && [ "$AUDIT_TABLES" -eq 2 ]; then
        echo -e "\n${GREEN}✅ Instalación verificada correctamente${NC}"
        return 0
    else
        echo -e "\n${YELLOW}⚠️  Advertencia: Algunos componentes podrían estar incompletos${NC}"
        return 1
    fi
}

# ============================================================================
# MAIN - Proceso de instalación
# ============================================================================

main() {
    echo "Este script instalará el sistema completo con seguridad."
    echo
    
    # 1. Solicitar credenciales
    if ! solicitar_credenciales; then
        echo -e "${RED}❌ No se pudo conectar a MySQL. Abortando.${NC}"
        exit 1
    fi
    
    # 2. Crear bases de datos
    crear_bases_datos
    
    # 3. Crear estructura de tablas
    crear_estructura_tablas
    
    # 4. Instalar procedimientos origen
    instalar_procedimientos_origen
    
    # 5. Instalar procedimientos ETL
    instalar_procedimientos_etl
    
    # 6. Instalar procedimientos DW
    instalar_procedimientos_dw
    
    # 7. Verificar Python
    verificar_python
    
    # 8. Verificar instalación
    verificar_instalacion
    
    # 9. Generar datos de prueba (opcional)
    generar_datos_prueba
    
    # 10. Ejecutar ETL (opcional)
    ejecutar_etl_inicial
    
    # 11. Mostrar resumen
    mostrar_resumen
}

# Ejecutar
main
