#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              🚀 INICIANDO DASHBOARD 🚀                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si el archivo .env existe
if [ ! -f .env ]; then
    echo -e "${RED}✗${NC} Archivo .env no encontrado"
    echo -e "${YELLOW}⚠${NC}  Ejecuta primero: ./setup_dashboard.sh"
    exit 1
fi

# Verificar si el puerto 5001 está libre
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠${NC}  El puerto 5001 ya está en uso"
    read -p "¿Quieres matar el proceso existente? (s/n): " KILL_PROCESS
    if [ "$KILL_PROCESS" = "s" ] || [ "$KILL_PROCESS" = "S" ]; then
        lsof -ti:5001 | xargs kill -9
        echo -e "${GREEN}✓${NC} Proceso anterior terminado"
    fi
fi

# Verificar si el puerto 8080 está libre
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠${NC}  El puerto 8080 ya está en uso"
    read -p "¿Quieres matar el proceso existente? (s/n): " KILL_PROCESS
    if [ "$KILL_PROCESS" = "s" ] || [ "$KILL_PROCESS" = "S" ]; then
        lsof -ti:8080 | xargs kill -9
        echo -e "${GREEN}✓${NC} Proceso anterior terminado"
    fi
fi

# Iniciar backend
echo ""
echo "📡 Iniciando Backend API..."
cd backend
nohup python3 app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Backend iniciado (PID: $BACKEND_PID)"
echo "   Log: logs/backend.log"
echo "   URL: http://localhost:5001"

# Esperar un momento para que el backend inicie
sleep 2

# Verificar que el backend esté corriendo
if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}✗${NC} Error: Backend no pudo iniciar"
    echo "   Revisa el log: tail -f logs/backend.log"
    exit 1
fi

# Iniciar frontend
echo ""
echo "🌐 Iniciando Frontend..."
cd frontend
nohup python3 -m http.server 8080 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Frontend iniciado (PID: $FRONTEND_PID)"
echo "   Log: logs/frontend.log"
echo "   URL: http://localhost:8080"

# Guardar PIDs para detener después
mkdir -p logs
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

# Resumen
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              DASHBOARD INICIADO                            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend:    http://localhost:8080/index.html"
echo "📡 Backend API: http://localhost:5001"
echo ""
echo "📊 Ver logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 Para detener:"
echo "   ./detener_dashboard.sh"
echo ""
echo "🎉 ¡Dashboard listo para usar!"

# Abrir en navegador (opcional)
if command -v open &> /dev/null; then
    read -p "¿Abrir en navegador? (s/n): " OPEN_BROWSER
    if [ "$OPEN_BROWSER" = "s" ] || [ "$OPEN_BROWSER" = "S" ]; then
        sleep 1
        open http://localhost:8080/index.html
    fi
fi
