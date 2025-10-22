#!/bin/bash

echo "🚀 Iniciando Dashboard ETL..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "Ejecuta primero: ./setup_local.sh"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar que las bases de datos existen
echo "📊 Verificando bases de datos..."
if ! mysql -u root -e "USE gestionproyectos_hist" &> /dev/null; then
    echo "❌ Base de datos origen no existe. Ejecuta: ./setup_local.sh"
    exit 1
fi

if ! mysql -u root -e "USE dw_proyectos_hist" &> /dev/null; then
    echo "❌ Datawarehouse no existe. Ejecuta: ./setup_local.sh"
    exit 1
fi

echo "✅ Bases de datos verificadas"
echo ""

# Iniciar backend en background
echo "🔧 Iniciando backend API..."
cd 03_Dashboard/backend
python app.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

# Esperar a que el backend inicie
sleep 3

# Verificar que el backend está corriendo
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
else
    echo "❌ Error iniciando el backend"
    exit 1
fi

# Iniciar servidor web para el frontend
echo "🌐 Iniciando servidor web..."
cd 03_Dashboard/frontend
python3 -m http.server 8080 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

# Esperar a que el frontend inicie
sleep 2

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"
else
    echo "❌ Error iniciando el frontend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "======================================================"
echo "🎉 DASHBOARD ETL INICIADO"
echo "======================================================"
echo ""
echo "📊 URLs disponibles:"
echo -e "   Frontend: ${BLUE}http://localhost:8080${NC}"
echo -e "   Backend:  ${BLUE}http://localhost:5001${NC}"
echo ""
echo "📝 Logs:"
echo "   Backend:  03_Dashboard/backend/backend.log"
echo "   Frontend: 03_Dashboard/frontend/frontend.log"
echo ""
echo "⚠️  Para detener el dashboard, ejecuta:"
echo -e "   ${GREEN}kill $BACKEND_PID $FRONTEND_PID${NC}"
echo ""
echo "O guarda estos PIDs en un archivo:"
echo $BACKEND_PID > .dashboard.pid
echo $FRONTEND_PID >> .dashboard.pid
echo "   Guardados en .dashboard.pid"
echo ""
echo "======================================================"
echo ""

# Abrir navegador automáticamente (macOS)
sleep 2
open http://localhost:8080 2>/dev/null || echo "Abre manualmente: http://localhost:8080"
