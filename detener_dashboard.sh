#!/bin/bash

echo "🛑 Deteniendo Dashboard ETL..."
echo ""

# Leer PIDs del archivo
if [ -f ".dashboard.pid" ]; then
    BACKEND_PID=$(sed -n '1p' .dashboard.pid)
    FRONTEND_PID=$(sed -n '2p' .dashboard.pid)
    
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && echo " Backend detenido (PID: $BACKEND_PID)"
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && echo " Frontend detenido (PID: $FRONTEND_PID)"
    fi
    
    rm .dashboard.pid
    echo ""
    echo " Dashboard detenido completamente"
else
    # Buscar procesos manualmente
    echo "⚠️  Archivo .dashboard.pid no encontrado"
    echo "Buscando procesos..."
    
    # Buscar y matar procesos del backend
    BACKEND_PIDS=$(ps aux | grep "[p]ython.*app.py" | awk '{print $2}')
    if [ -n "$BACKEND_PIDS" ]; then
        echo "$BACKEND_PIDS" | xargs kill 2>/dev/null
        echo " Backend detenido"
    fi
    
    # Buscar y matar procesos del frontend
    FRONTEND_PIDS=$(ps aux | grep "[p]ython.*http.server.*8080" | awk '{print $2}')
    if [ -n "$FRONTEND_PIDS" ]; then
        echo "$FRONTEND_PIDS" | xargs kill 2>/dev/null
        echo " Frontend detenido"
    fi
    
    if [ -z "$BACKEND_PIDS" ] && [ -z "$FRONTEND_PIDS" ]; then
        echo "⚠️  No se encontraron procesos del dashboard"
    fi
fi

echo ""
echo "======================================================"
