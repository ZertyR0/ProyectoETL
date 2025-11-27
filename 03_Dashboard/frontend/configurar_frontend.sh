#!/bin/bash

# Script para configurar el frontend con la URL de Railway
# Uso: ./configurar_frontend.sh https://tu-backend.railway.app

if [ -z "$1" ]; then
    echo "❌ Error: Debes proporcionar la URL del backend de Railway"
    echo "Uso: ./configurar_frontend.sh https://tu-backend.railway.app"
    exit 1
fi

BACKEND_URL=$1
FRONTEND_DIR="/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/frontend"

echo "🔧 Configurando frontend con backend: $BACKEND_URL"

# Actualizar app.js
sed -i '' "s|const API_BASE = 'http://localhost:5001'|const API_BASE = '$BACKEND_URL'|g" "$FRONTEND_DIR/app.js"
sed -i '' "s|const API_URL = 'http://localhost:5001/api'|const API_URL = '$BACKEND_URL/api'|g" "$FRONTEND_DIR/app.js"

echo "✅ Frontend configurado!"
echo "📁 Archivo actualizado: $FRONTEND_DIR/app.js"
echo ""
echo "Ahora puedes:"
echo "1. Abrir 03_Dashboard/frontend/index.html en tu navegador"
echo "2. O desplegar el frontend a un servicio como Vercel/Netlify"
echo ""
echo "Para desplegar a Railway:"
echo "  cd $FRONTEND_DIR"
echo "  railway up"
