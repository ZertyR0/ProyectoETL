#!/bin/bash

# Script de inicio para Railway/Cloud
echo "🚀 Iniciando ETL Dashboard..."
echo "📍 Directorio actual: $(pwd)"
echo "📂 Contenido:"
ls -la

# Configurar variables de entorno
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5001}

echo "🔧 Variables de entorno:"
echo "   FLASK_ENV: $FLASK_ENV"
echo "   PORT: $PORT"
echo "   DB_HOST_ORIGEN: ${DB_HOST_ORIGEN:-not_set}"

# Verificar que estamos en el directorio correcto
if [ ! -d "03_Dashboard" ]; then
    echo "❌ Error: No se encuentra el directorio 03_Dashboard"
    echo "📂 Contenido del directorio actual:"
    ls -la
    exit 1
fi

# Ir al directorio del backend
cd 03_Dashboard/backend
echo "📍 Ahora en: $(pwd)"

# Ejecutar Flask con Gunicorn en producción
if [ "$FLASK_ENV" = "production" ]; then
    echo "🚀 Modo producción: usando Gunicorn"
    echo "🌐 Iniciando en 0.0.0.0:$PORT"
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app
else
    echo "🔧 Modo desarrollo: usando Flask dev server"
    exec python3 app.py
fi
