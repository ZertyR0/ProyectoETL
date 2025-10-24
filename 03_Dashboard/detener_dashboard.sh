#!/bin/bash

echo "🛑 Deteniendo Dashboard..."

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detener usando PIDs guardados
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓${NC} Backend detenido (PID: $BACKEND_PID)"
    fi
    rm logs/backend.pid
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓${NC} Frontend detenido (PID: $FRONTEND_PID)"
    fi
    rm logs/frontend.pid
fi

# Matar procesos en los puertos si todavía están corriendo
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    lsof -ti:5001 | xargs kill -9
    echo -e "${GREEN}✓${NC} Puerto 5001 liberado"
fi

if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    lsof -ti:8080 | xargs kill -9
    echo -e "${GREEN}✓${NC} Puerto 8080 liberado"
fi

echo ""
echo "✅ Dashboard detenido completamente"
