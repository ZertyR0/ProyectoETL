#!/bin/bash

# Script de prueba de conexiones
# Para el Dashboard en 172.31.5.36

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║              🔍 PRUEBA DE CONEXIONES - DASHBOARD                     ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
VERDE='\033[0;32m'
ROJO='\033[0;31m'
AMARILLO='\033[1;33m'
RESET='\033[0m'

# Función para probar conexión
probar_conexion() {
    local host=$1
    local puerto=$2
    local nombre=$3
    
    echo -n "Probando $nombre ($host:$puerto)... "
    
    if nc -zv -w 3 $host $puerto 2>/dev/null; then
        echo -e "${VERDE}✅ ÉXITO${RESET}"
        return 0
    else
        echo -e "${ROJO}❌ FALLO${RESET}"
        return 1
    fi
}

# Función para probar MySQL
probar_mysql() {
    local host=$1
    local db=$2
    local nombre=$3
    
    echo -n "Probando MySQL en $nombre ($host)... "
    
    if mysql -h $host -u etl_user -petl_password_123 -D $db -e "SELECT 1;" 2>/dev/null >/dev/null; then
        echo -e "${VERDE}✅ ÉXITO${RESET}"
        return 0
    else
        echo -e "${ROJO}❌ FALLO${RESET}"
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════════════════"
echo "  PRUEBA 1: Conectividad de Red (ping)"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

echo -n "Servidor 1 (BD Origen - 172.26.163.247)... "
if ping -c 1 -W 1 172.26.163.247 >/dev/null 2>&1; then
    echo -e "${VERDE}✅ Responde${RESET}"
    SERVER1_PING=1
else
    echo -e "${ROJO}❌ No responde${RESET}"
    SERVER1_PING=0
fi

echo -n "Servidor 3 (Data Warehouse - 172.26.167.211)... "
if ping -c 1 -W 1 172.26.167.211 >/dev/null 2>&1; then
    echo -e "${VERDE}✅ Responde${RESET}"
    SERVER3_PING=1
else
    echo -e "${ROJO}❌ No responde${RESET}"
    SERVER3_PING=0
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  PRUEBA 2: Puertos MySQL Abiertos"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

probar_conexion "172.26.163.247" "3306" "Servidor 1 (BD Origen)"
SERVER1_PORT=$?

probar_conexion "172.26.167.211" "3306" "Servidor 3 (Data Warehouse)"
SERVER3_PORT=$?

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  PRUEBA 3: Autenticación MySQL"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

if command -v mysql >/dev/null 2>&1; then
    probar_mysql "172.26.163.247" "gestionproyectos_hist" "Servidor 1"
    SERVER1_MYSQL=$?
    
    probar_mysql "172.26.167.211" "dw_proyectos_hist" "Servidor 3"
    SERVER3_MYSQL=$?
else
    echo -e "${AMARILLO}⚠️  Cliente MySQL no instalado${RESET}"
    echo "   Instalar: sudo apt install mysql-client"
    SERVER1_MYSQL=2
    SERVER3_MYSQL=2
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  PRUEBA 4: Archivos de Configuración"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

echo -n "Archivo .env existe... "
if [ -f ".env" ]; then
    echo -e "${VERDE}✅ Sí${RESET}"
    ENV_EXISTS=1
else
    echo -e "${ROJO}❌ No${RESET}"
    ENV_EXISTS=0
fi

if [ $ENV_EXISTS -eq 1 ]; then
    echo -n "IP de BD Origen en .env... "
    if grep -q "DB_ORIGEN_HOST=172.26.163.247" .env; then
        echo -e "${VERDE}✅ Correcta${RESET}"
    else
        echo -e "${ROJO}❌ Incorrecta${RESET}"
    fi
    
    echo -n "IP de Data Warehouse en .env... "
    if grep -q "DB_DW_HOST=172.26.167.211" .env; then
        echo -e "${VERDE}✅ Correcta${RESET}"
    else
        echo -e "${ROJO}❌ Incorrecta${RESET}"
    fi
fi

echo -n "Archivo app.js actualizado... "
if grep -q "172.31.5.36" frontend/app.js; then
    echo -e "${VERDE}✅ Sí${RESET}"
else
    echo -e "${AMARILLO}⚠️  Revisar${RESET}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  RESUMEN"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Calcular estado total
TOTAL_OK=0
TOTAL_FAIL=0

if [ $SERVER1_PING -eq 0 ] || [ $SERVER1_PORT -ne 0 ]; then
    echo -e "${ROJO}❌ Servidor 1 (172.26.163.247): PROBLEMAS${RESET}"
    echo "   → Verificar que el servidor esté encendido"
    echo "   → Verificar firewall (sudo ufw allow 3306/tcp)"
    echo "   → Verificar MySQL bind-address = 0.0.0.0"
    TOTAL_FAIL=$((TOTAL_FAIL + 1))
else
    echo -e "${VERDE}✅ Servidor 1 (172.26.163.247): OK${RESET}"
    TOTAL_OK=$((TOTAL_OK + 1))
fi

if [ $SERVER3_PING -eq 0 ] || [ $SERVER3_PORT -ne 0 ]; then
    echo -e "${ROJO}❌ Servidor 3 (172.26.167.211): PROBLEMAS${RESET}"
    echo "   → Verificar que el servidor esté encendido"
    echo "   → Verificar firewall (sudo ufw allow 3306/tcp)"
    echo "   → Verificar MySQL bind-address = 0.0.0.0"
    TOTAL_FAIL=$((TOTAL_FAIL + 1))
else
    echo -e "${VERDE}✅ Servidor 3 (172.26.167.211): OK${RESET}"
    TOTAL_OK=$((TOTAL_OK + 1))
fi

echo ""

if [ $TOTAL_FAIL -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo -e "║              ${VERDE}✅ TODAS LAS CONEXIONES OK${RESET}                           ║"
    echo "║                                                                      ║"
    echo "║              Puedes iniciar el dashboard con:                        ║"
    echo "║              ./iniciar_dashboard.sh                                  ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
else
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                      ║"
    echo -e "║              ${ROJO}❌ HAY PROBLEMAS DE CONEXIÓN${RESET}                         ║"
    echo "║                                                                      ║"
    echo "║              Revisa los mensajes arriba y soluciona                 ║"
    echo "║              los problemas antes de iniciar el dashboard             ║"
    echo "║                                                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
fi

echo ""
echo "📖 Ver guía completa: CONFIGURACION_TU_RED.md"
echo ""
