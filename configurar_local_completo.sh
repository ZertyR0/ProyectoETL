#!/bin/bash

# ===============================================
# CONFIGURACIÓN COMPLETA DSS - DESARROLLO LOCAL
# ===============================================
# 
# Este script configura todo el sistema DSS para
# ejecución local desde cero
#

echo "🚀 INICIANDO CONFIGURACIÓN DEL SISTEMA DSS"
echo "============================================="

# Verificar prerrequisitos
echo ""
echo "1️⃣ VERIFICANDO PRERREQUISITOS..."

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "    Python encontrado: $PYTHON_VERSION"
else
    echo "    Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

# Verificar MySQL
if command -v mysql &> /dev/null; then
    echo "    MySQL encontrado"
else
    echo "    MySQL no encontrado. Por favor instálalo primero."
    echo "   💡 Sugerencia: Instala XAMPP o MySQL Community Server"
    exit 1
fi

# Activar entorno virtual
echo ""
echo "2️⃣ CONFIGURANDO ENTORNO PYTHON..."
if [ -d ".venv" ]; then
    echo "    Entorno virtual ya existe"
    source .venv/bin/activate
else
    echo "   🔧 Creando entorno virtual..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Instalar dependencias
echo "   📦 Instalando dependencias Python..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "3️⃣ CONFIGURANDO BASES DE DATOS..."

# Detectar socket de MySQL (XAMPP vs sistema)
MYSQL_SOCKET=""
MYSQL_CMD=""

if [ -S "/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock" ]; then
    # XAMPP detectado
    MYSQL_SOCKET="/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock"
    MYSQL_CMD="mysql -u root -S $MYSQL_SOCKET"
    echo "   🎯 XAMPP MySQL detectado"
elif [ -S "/tmp/mysql.sock" ]; then
    # MySQL sistema
    MYSQL_CMD="mysql -u root"
    echo "   🎯 MySQL del sistema detectado"
else
    # Intentar conexión estándar
    MYSQL_CMD="mysql -u root"
    echo "   ⚠️  Socket MySQL no detectado, usando conexión estándar"
fi

# Verificar conexión MySQL
echo "   🔍 Verificando conexión a MySQL..."
$MYSQL_CMD -e "SELECT 'Conexión MySQL exitosa' AS resultado;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "    Conexión MySQL exitosa"
else
    echo "    Error de conexión MySQL"
    echo "   💡 Si usas XAMPP: Inicia MySQL desde el panel de control"
    echo "   💡 Si usas MySQL sistema: Verifica que esté ejecutándose"
    echo "   💡 Revisa el archivo config_mysql_xampp.md para más ayuda"
    read -p "   ¿Continuar con la configuración? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Crear bases de datos
echo "   🗄️ Creando base de datos origen..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS gestionproyectos_hist;" 2>/dev/null

echo "   🏢 Creando base de datos datawarehouse..."
$MYSQL_CMD -e "CREATE DATABASE IF NOT EXISTS datawarehouse;" 2>/dev/null

# Ejecutar scripts SQL
echo "   📊 Configurando esquemas de bases de datos..."
$MYSQL_CMD gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql 2>/dev/null
$MYSQL_CMD datawarehouse < 04_Datawarehouse/scripts/crear_datawarehouse.sql 2>/dev/null

# Configurar módulos DSS
echo "   🎯 Configurando módulos DSS (OLAP + BSC)..."
$MYSQL_CMD datawarehouse < 04_Datawarehouse/scripts/olap_views.sql 2>/dev/null
$MYSQL_CMD datawarehouse < 04_Datawarehouse/scripts/crear_bsc.sql 2>/dev/null

echo ""
echo "4️⃣ GENERANDO DATOS DE DEMOSTRACIÓN..."
echo "   🎲 Generando 300 proyectos + 1500 empleados + BSC data..."

# Configurar ambiente local
export ETL_AMBIENTE=local

# Generar datos
python generar_datos_completos.py

echo ""
echo "5️⃣ VERIFICANDO CONFIGURACIÓN..."

# Verificar conexiones
echo "   🔍 Probando conexiones del sistema..."
python 02_ETL/config/config_conexion.py local

echo ""
echo " CONFIGURACIÓN COMPLETADA"
echo "========================="
echo ""
echo "🎉 El Sistema DSS está listo para usar!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Iniciar dashboard: ./iniciar_dashboard.sh"
echo "   2. Abrir navegador: http://localhost:5001"
echo "   3. Explorar las 7 secciones del DSS:"
echo "      • 📊 Dashboard Principal"
echo "      • 🗄️ Datos Origen"  
echo "      • ⚙️ Control ETL"
echo "      • 🏢 DataWarehouse"
echo "      • 📈 Análisis"
echo "      • 📊 KPIs OLAP (NUEVO)"
echo "      • 🎯 BSC/OKR (NUEVO)" 
echo "      • 📈 Predicción Rayleigh (NUEVO)"
echo "      • 🔍 Trazabilidad"
echo ""
echo "🚨 IMPORTANTE:"
echo "   • Para Predicción Rayleigh: usar 'Simular Acceso PM'"
echo "   • Los datos incluyen objetivos BSC pre-configurados"
echo "   • El cubo OLAP tiene datos históricos listos"
echo ""
echo "🆘 SI HAY PROBLEMAS:"
echo "   • Verificar que MySQL esté ejecutándose"
echo "   • Revisar contraseñas de MySQL en config_conexion.py"
echo "   • Ejecutar: python 02_ETL/config/config_conexion.py local"
echo ""