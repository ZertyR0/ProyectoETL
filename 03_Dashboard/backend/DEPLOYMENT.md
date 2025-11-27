# Deployment del Backend a Railway

## Configuración Rápida

### 1. Push a GitHub
```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL
git add 03_Dashboard/backend/
git commit -m "Backend configurado para Railway"
git push origin main
```

### 2. Crear Servicio en Railway

1. **Ir a Railway Dashboard**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Seleccionar**: `ProyectoETL`
4. **Root Directory**: `03_Dashboard/backend`
5. Click **Deploy**

### 3. Configurar Variables de Entorno

En Railway Settings → Variables, agregar:

```bash
# Database Origen (gestionproyectos_hist)
DB_HOST_ORIGEN=interchange.proxy.rlwy.net
DB_PORT_ORIGEN=22434
DB_USER_ORIGEN=etl_user
DB_PASSWORD_ORIGEN=ETL_Pass_2025!
DB_NAME_ORIGEN=gestionproyectos_hist

# Database Destino (dw_proyectos_hist)
DB_HOST_DESTINO=interchange.proxy.rlwy.net
DB_PORT_DESTINO=22434
DB_USER_DESTINO=etl_user
DB_PASSWORD_DESTINO=ETL_Pass_2025!
DB_NAME_DESTINO=dw_proyectos_hist

# Flask Config
FLASK_ENV=production
ETL_AMBIENTE=distribuido
PORT=5000
```

### 4. Verificar Deployment

Una vez desplegado, Railway te dará una URL pública tipo:
```
https://proyectoetl-backend-production.up.railway.app
```

Prueba los endpoints:
```bash
curl https://TU-URL.railway.app/status
curl https://TU-URL.railway.app/datos-datawarehouse
curl https://TU-URL.railway.app/olap/kpis
curl https://TU-URL.railway.app/bsc/okr
```

### 5. Actualizar Frontend

Editar `03_Dashboard/frontend/app.js`:
```javascript
const API_BASE_URL = 'https://TU-URL.railway.app';
```

## Estructura de Archivos para Railway

```
03_Dashboard/backend/
├── app.py              # Aplicación Flask principal
├── rayleigh.py         # Utilidades Rayleigh
├── requirements.txt    # Dependencias Python
├── .env               # Variables locales (NO se sube a Railway)
├── Procfile           # Comando start para Railway
├── runtime.txt        # Versión de Python
├── railway.json       # Configuración Railway
└── DEPLOYMENT.md      # Este archivo
```

## Logs y Debugging

Ver logs en Railway:
1. Click en tu servicio
2. Tab **Deployments**
3. Click en el deployment activo
4. Ver **Logs** en tiempo real

## Troubleshooting

### Error de Conexión a BD
- Verificar que todas las variables DB_* estén configuradas
- Verificar que Railway tenga acceso a interchange.proxy.rlwy.net:22434
- Revisar logs: `Error al conectar con MySQL`

### Puerto Incorrecto
- Railway asigna PORT automáticamente
- app.py ya está configurado: `port = int(os.getenv('PORT', 5001))`

### Módulos Faltantes
- Verificar que requirements.txt esté completo
- Railway instala automáticamente con: `pip install -r requirements.txt`
