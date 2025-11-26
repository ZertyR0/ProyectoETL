#  Dashboard ETL - Sistema de Monitoreo

Esta carpeta contiene el dashboard web para monitorear y controlar el proceso ETL.

##  Estructura

```
03_Dashboard/
├── README.md                 # Este archivo
├── backend/
│   ├── app.py               # API Flask para el backend
│   └── requirements.txt     # Dependencias del backend
└── frontend/
    ├── index.html          # Interfaz web principal
    ├── app.js              # Lógica JavaScript
    └── styles.css          # Estilos CSS
```

##  Propósito

El dashboard proporciona:

###  Frontend (Web)
- **Interfaz Visual**: Dashboard responsive con Bootstrap
- **Monitoreo en Tiempo Real**: Estado de conexiones y procesos
- **Control de Procesos**: Ejecutar ETL, insertar datos, limpiar tablas
- **Visualización de Datos**: Tablas y métricas del sistema
- **Logs en Vivo**: Seguimiento de la ejecución

###  Backend (API Flask)
- **API REST**: Endpoints para todas las operaciones
- **Conexión a BD**: Integración con origen y datawarehouse
- **Control ETL**: Ejecución y monitoreo de procesos
- **Validación**: Verificación de datos y estados
- **CORS**: Soporte para requests desde el frontend

##  Uso

### 1. Configurar Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Abrir Frontend
```bash
# Abrir index.html en el navegador
# O usar un servidor local:
python -m http.server 8000
```

##  Funcionalidades

###  Monitoreo
-  Estado de conexiones a BD
-  Estadísticas de tablas origen y destino
-  Métricas del datawarehouse
-  Historial de ejecuciones

###  Control
-  Generar datos de prueba
-  Ejecutar proceso ETL
-  Limpiar bases de datos
-  Reiniciar sistema

###  Visualización
-  Tablas de datos origen
-  Métricas de proyectos
-  Gráficos de rendimiento
-  Logs detallados

##  Endpoints API

- `GET /` - Información de la API
- `GET /status` - Estado de conexiones
- `GET /datos-origen` - Datos de BD origen
- `GET /datos-datawarehouse` - Datos del DW
- `POST /insertar-datos` - Generar datos de prueba
- `POST /ejecutar-etl` - Ejecutar proceso ETL
- `DELETE /limpiar-datos` - Limpiar tablas

##  Configuración

### Variables de Ambiente
```bash
ETL_AMBIENTE=local|distribuido|test
ETL_HOST_ORIGEN=localhost
ETL_HOST_DESTINO=localhost
# ... más configuraciones
```

### Puertos
- Backend: `5001` (Flask)
- Frontend: `8000` (HTTP Server) o archivo local
