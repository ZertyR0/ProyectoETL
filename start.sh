#!/bin/bash

# Script de inicio para Railway/Cloud
echo "🚀 Iniciando ETL Dashboard..."

# Configurar variables de entorno
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5001}

# Verificar que estamos en el directorio correcto
if [ ! -d "03_Dashboard" ]; then
    echo "❌ Error: No se encuentra el directorio 03_Dashboard"
    exit 1
fi

# Instalar dependencias si es necesario
if [ ! -f ".dependencies_installed" ]; then
    echo "📦 Instalando dependencias..."
    pip install -r requirements-all.txt
    touch .dependencies_installed
fi

# Iniciar solo el backend Flask (Railway usa un solo proceso)
echo "🔧 Iniciando backend Flask en puerto $PORT..."
cd 03_Dashboard/backend

# Ejecutar Flask con Gunicorn en producción
if [ "$FLASK_ENV" = "production" ]; then
    echo "🚀 Modo producción: usando Gunicorn"
    gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
else
    echo "🔧 Modo desarrollo: usando Flask dev server"
    python3 app.py
fi
