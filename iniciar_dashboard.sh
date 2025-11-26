#!/bin/bash
# ============================================================
# Script para iniciar el Dashboard DSS en modo local
# ============================================================

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                🚀 INICIANDO DASHBOARD DSS - MODO LOCAL               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Configurar ambiente
export ETL_AMBIENTE=local

# Directorio base
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASEDIR"s

# Crear directorio de logs si no existe
mkdir -p 03_Dashboard/logs

# Detener procesos previos
echo "🛑 Deteniendo procesos previos..."
pkill -f "python.*03_Dashboard/backend/app.py" 2>/dev/null
pkill -f "python.*http.server 8080" 2>/dev/null
sleep 2

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🐍 Activando entorno virtual Python..."
    source .venv/bin/activate
fi

# Iniciar backend
echo "🔧 Iniciando Backend DSS (Puerto 5001)..."
python 03_Dashboard/backend/app.py > 03_Dashboard/logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "    Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que el backend esté listo
sleep 3

# Verificar que el backend está corriendo
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "    Backend verificado y funcionando"
else
    echo "    Error: Backend no está corriendo"
    exit 1
fi

# Iniciar frontend
echo "🌐 Iniciando Frontend (Puerto 8080)..."
cd "$BASEDIR/03_Dashboard/frontend"
python3 -m http.server 8080 > "$BASEDIR/03_Dashboard/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$BASEDIR"
echo "    Frontend iniciado (PID: $FRONTEND_PID)"

sleep 2

# Verificar que el frontend está corriendo
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "    Frontend verificado y funcionando"
else
    echo "    Error: Frontend no está corriendo"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Guardar PIDs
echo $BACKEND_PID > .dashboard.pid
echo $FRONTEND_PID >> .dashboard.pid

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                   SISTEMA DSS INICIADO CORRECTAMENTE               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 ACCEDE AL DASHBOARD DSS EN:"
echo "   http://localhost:8080"
echo ""
echo "📊 API BACKEND DSS:"
echo "   http://localhost:5001"
echo ""
echo "🎯 MÓDULOS DSS DISPONIBLES:"
echo "   • 📊 Dashboard Principal & Análisis"
echo "   • 🗄️ Control de Datos Origen"
echo "   • ⚙️ Gestión ETL Automática"
echo "   • 🏢 DataWarehouse & Reports"
echo "   • 📈 KPIs OLAP con Cubo Multidimensional"
echo "   • 🎯 Balanced Scorecard (BSC) con OKR"
echo "   • � Predicción Rayleigh de Defectos"
echo "   • 🔍 Trazabilidad Completa"
echo ""
echo " LOGS:"
echo "   Backend:  tail -f 03_Dashboard/logs/backend.log"
echo "   Frontend: tail -f 03_Dashboard/logs/frontend.log"
echo ""
echo "🛑 PARA DETENER:"
echo "   ./detener_dashboard.sh"
echo ""
echo "⚙️  CONFIGURACIÓN LOCAL:"
echo "   BD Origen: localhost:3306 (gestionproyectos_hist)"
echo "   DataWarehouse: localhost:3306 (dw_proyectos_hist)"
echo ""

# Abrir navegador automáticamente (macOS)
sleep 1
open http://localhost:8080 2>/dev/null || echo "💡 Abre manualmente: http://localhost:8080"
