#!/bin/bash

# Script de inicio para Railway
echo "🚀 Iniciando ETL Dashboard..."

# Configurar variables de entorno si no existen
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5001}

# Iniciar backend Flask
echo "🔧 Iniciando backend Flask en puerto $PORT..."
cd 03_Dashboard/backend
python3 app.py &
BACKEND_PID=$!

# Iniciar frontend con servidor HTTP simple
echo "🌐 Iniciando frontend..."
cd ../frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

# Esperar a que ambos servicios inicien
sleep 3

echo "✅ Dashboard iniciado correctamente"
echo "   Backend: http://localhost:$PORT"
echo "   Frontend: http://localhost:8080"

# Mantener el script corriendo
wait $BACKEND_PID $FRONTEND_PID
