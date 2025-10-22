#!/bin/bash

echo "🚀 ======================================================"
echo "   CONFIGURACIÓN LOCAL DEL PROYECTO ETL"
echo "======================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Verificar que MySQL está corriendo
log_info "Verificando MySQL..."
if ! mysql --version &> /dev/null; then
    log_error "MySQL no está instalado o no está en el PATH"
    exit 1
fi

if ! mysql -h 127.0.0.1 -u root -e "SELECT 1" &> /dev/null; then
    log_error "No se puede conectar a MySQL. Verifica que el servidor esté corriendo."
    exit 1
fi
log_success "MySQL está disponible"

# 2. Crear entorno virtual si no existe
log_info "Configurando entorno virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Entorno virtual creado"
else
    log_info "Entorno virtual ya existe"
fi

# 3. Activar entorno virtual e instalar dependencias
source venv/bin/activate
log_info "Instalando dependencias Python..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
log_success "Dependencias instaladas"

# 4. Crear base de datos origen
log_info "Creando base de datos origen (gestionproyectos_hist)..."
mysql -h 127.0.0.1 -u root < 01_GestionProyectos/scripts/crear_bd_origen.sql
if [ $? -eq 0 ]; then
    log_success "Base de datos origen creada"
else
    log_error "Error creando base de datos origen"
    exit 1
fi

# 5. Crear datawarehouse
log_info "Creando datawarehouse (dw_proyectos_hist)..."
mysql -h 127.0.0.1 -u root < 04_Datawarehouse/scripts/crear_datawarehouse.sql
if [ $? -eq 0 ]; then
    log_success "Datawarehouse creado"
else
    log_error "Error creando datawarehouse"
    exit 1
fi

# 6. Generar datos de prueba
log_info "Generando datos de prueba..."
python3 01_GestionProyectos/scripts/generar_datos.py
if [ $? -eq 0 ]; then
    log_success "Datos de prueba generados"
else
    log_error "Error generando datos de prueba"
    exit 1
fi

# 7. Ejecutar ETL inicial
log_info "Ejecutando proceso ETL inicial..."
python3 02_ETL/scripts/etl_principal.py local
if [ $? -eq 0 ]; then
    log_success "ETL ejecutado correctamente"
else
    log_warning "Error en ETL (puedes intentar ejecutarlo manualmente)"
fi

echo ""
echo "🎉 ======================================================"
echo "   CONFIGURACIÓN COMPLETADA"
echo "======================================================"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1️⃣  Iniciar el backend (en una terminal):"
echo "   ${GREEN}cd 03_Dashboard/backend${NC}"
echo "   ${GREEN}source ../../venv/bin/activate${NC}"
echo "   ${GREEN}python app.py${NC}"
echo ""
echo "2️⃣  Abrir el dashboard (en otra terminal):"
echo "   ${GREEN}cd 03_Dashboard/frontend${NC}"
echo "   ${GREEN}python3 -m http.server 8080${NC}"
echo ""
echo "3️⃣  Acceder al dashboard:"
echo "   ${BLUE}http://localhost:8080${NC}"
echo ""
echo "📊 Bases de datos disponibles:"
echo "   - Origen: gestionproyectos_hist"
echo "   - Destino: dw_proyectos_hist"
echo ""
echo "======================================================"
