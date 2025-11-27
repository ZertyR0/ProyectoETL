# 🚀 Guía Completa de Despliegue - Dashboard ETL

## Estado Actual ✅

### Datos Importados
- **BD Origen** (gestionproyectos_hist): 1,616 registros
  - 16 Clientes
  - 250 Empleados
  - 50 Equipos
  - 50 Proyectos
  - 500 Tareas
  - 250 Miembros de Equipo
  - 500 Historial Tarea-Equipo

### ETL Ejecutado
- **BD Destino** (dw_proyectos_hist): 28 proyectos completados/cancelados
  - DimCliente: 16 registros
  - DimEmpleado: 250 registros
  - DimEquipo: 50 registros
  - DimProyecto: 28 registros
  - HechoProyecto: 28 registros
  - DimTiempo: 1,560 registros

### Vistas OLAP/BSC Creadas
- `vw_olap_kpis_ejecutivos`: 28 filas (métricas por fecha)
- `vw_olap_sector_performance`: 19 filas (análisis sectorial)
- `vw_olap_equipo_performance`: 28 filas (performance de gerentes)
- `vw_olap_proyectos_rollup`: Análisis con ROLLUP
- `vw_bsc_tablero_consolidado`: 3 perspectivas BSC
  - **Financiera F1**: 50% avance (🔴 Rojo) - Cumplimiento presupuesto
  - **Procesos P1**: 46% avance (🔴 Rojo) - Cumplimiento tiempo
  - **Cliente C1**: 75% avance (🟡 Amarillo) - Tareas completadas

---

## 📋 Pasos de Despliegue

### PASO 1: Desplegar Backend a Railway

#### 1.1 Acceder a Railway
```
https://railway.app
```

#### 1.2 Crear Nuevo Servicio
1. Click en **New Project**
2. Seleccionar **Deploy from GitHub repo**
3. Autorizar acceso a GitHub si es necesario
4. Seleccionar repositorio: **ProyectoETL**

#### 1.3 Configurar Root Directory
1. En **Settings** del servicio
2. Buscar **Root Directory**
3. Ingresar: `03_Dashboard/backend`
4. Click **Save**

#### 1.4 Configurar Variables de Entorno
En **Variables** tab, agregar una por una:

```bash
DB_HOST_ORIGEN=interchange.proxy.rlwy.net
DB_PORT_ORIGEN=22434
DB_USER_ORIGEN=etl_user
DB_PASSWORD_ORIGEN=ETL_Pass_2025!
DB_NAME_ORIGEN=gestionproyectos_hist

DB_HOST_DESTINO=interchange.proxy.rlwy.net
DB_PORT_DESTINO=22434
DB_USER_DESTINO=etl_user
DB_PASSWORD_DESTINO=ETL_Pass_2025!
DB_NAME_DESTINO=dw_proyectos_hist

FLASK_ENV=production
ETL_AMBIENTE=distribuido
PORT=5000
```

#### 1.5 Desplegar
Railway detectará automáticamente:
- `requirements.txt` → Instalar dependencias
- `Procfile` → Comando de inicio: `python app.py`
- `runtime.txt` → Python 3.11

El despliegue tomará ~2-3 minutos.

#### 1.6 Obtener URL Pública
Una vez desplegado:
1. Click en **Settings**
2. Buscar **Domains**
3. Click **Generate Domain**
4. Railway asignará una URL tipo:
   ```
   https://proyectoetl-backend-production.up.railway.app
   ```
5. **COPIAR ESTA URL** para el siguiente paso

---

### PASO 2: Verificar Backend

Probar endpoints con la URL de Railway:

```bash
# Reemplazar TU-URL con la URL real de Railway
export BACKEND_URL="https://TU-URL.railway.app"

# Test 1: Status
curl $BACKEND_URL/status

# Respuesta esperada:
# {
#   "success": true,
#   "message": "API funcionando correctamente",
#   "conexion_origen": "OK",
#   "conexion_destino": "OK"
# }

# Test 2: DataWarehouse
curl $BACKEND_URL/datos-datawarehouse | python3 -m json.tool

# Respuesta esperada: 28 proyectos con métricas

# Test 3: OLAP KPIs
curl $BACKEND_URL/olap/kpis | python3 -m json.tool

# Respuesta esperada: 28 filas con proyectos_total, duracion_promedio, etc.

# Test 4: BSC
curl $BACKEND_URL/bsc/okr | python3 -m json.tool

# Respuesta esperada: 3 perspectivas (Financiera, Procesos, Cliente)
```

---

### PASO 3: Configurar Frontend

#### 3.1 Actualizar URL del Backend

Usar el script automatizado:

```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/frontend

# Reemplazar con tu URL de Railway
./configurar_frontend.sh https://TU-URL.railway.app
```

O manualmente editar `app.js`:

```javascript
// Línea 2
const API_BASE = 'https://TU-URL.railway.app';

// Línea 31
const API_URL = 'https://TU-URL.railway.app/api';
```

#### 3.2 Probar Localmente

Abrir en navegador:
```bash
open /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/frontend/index.html
```

Verificar:
- ✅ Dashboard carga sin errores
- ✅ Tablas muestran datos del DataWarehouse
- ✅ Gráficos OLAP funcionan
- ✅ BSC muestra 3 perspectivas con semáforos

---

### PASO 4: Desplegar Frontend (Opcional)

#### Opción A: Railway Static Site

```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/frontend

# Instalar Railway CLI si no está instalado
brew install railway

# Login
railway login

# Vincular proyecto
railway link

# Desplegar
railway up
```

#### Opción B: Vercel (Más Simple)

```bash
# Instalar Vercel CLI
npm install -g vercel

cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/frontend

# Desplegar
vercel

# Seguir prompts:
# - Set up and deploy? Yes
# - Scope: Tu cuenta
# - Link to existing project? No
# - Project name: proyectoetl-dashboard
# - Directory: ./
```

#### Opción C: Netlify Drop

1. Ir a https://app.netlify.com/drop
2. Arrastrar la carpeta `03_Dashboard/frontend`
3. Netlify generará URL automáticamente

---

## 🧪 Testing Completo

### Test de Integración End-to-End

```bash
# 1. Backend Status
curl https://TU-BACKEND.railway.app/status

# 2. Datos Origen
curl https://TU-BACKEND.railway.app/datos-origen

# 3. Datos DataWarehouse
curl https://TU-BACKEND.railway.app/datos-datawarehouse

# 4. OLAP KPIs
curl https://TU-BACKEND.railway.app/olap/kpis

# 5. OLAP Series Temporales
curl https://TU-BACKEND.railway.app/olap/series

# 6. BSC OKR
curl https://TU-BACKEND.railway.app/bsc/okr

# 7. BSC Visión Estratégica
curl https://TU-BACKEND.railway.app/bsc/vision-estrategica
```

### Test desde Frontend

1. Abrir dashboard en navegador
2. Verificar secciones:
   - **Inicio**: Muestra métricas generales
   - **OLAP**: Gráficos interactivos con drill-down
   - **BSC**: Tablero con semáforos (Rojo/Amarillo/Verde)
3. Probar funcionalidad:
   - Click en sectores → filtrar proyectos
   - Cambiar rango de fechas
   - Exportar reportes

---

## 🔧 Troubleshooting

### Error: "Failed to fetch"
**Causa**: CORS bloqueando peticiones del frontend al backend.

**Solución**: Verificar que `app.py` tiene:
```python
from flask_cors import CORS
CORS(app)
```

### Error: "Connection refused"
**Causa**: Backend no está corriendo o URL incorrecta.

**Solución**:
1. Verificar que Railway backend está activo
2. Revisar logs en Railway dashboard
3. Confirmar URL en `app.js`

### Error: "No data available"
**Causa**: Vistas OLAP/BSC no existen o están vacías.

**Solución**:
```bash
# Conectar a Railway MySQL
mysql -h interchange.proxy.rlwy.net \
      -P 22434 \
      -u etl_user \
      -p'ETL_Pass_2025!' \
      dw_proyectos_hist

# Verificar vistas
SHOW TABLES LIKE 'vw_%';

# Verificar datos
SELECT COUNT(*) FROM vw_bsc_tablero_consolidado;
```

### Railway Build Falla
**Causa**: `requirements.txt` con errores o Python version incompatible.

**Solución**:
1. Revisar logs de build en Railway
2. Verificar `runtime.txt` tiene `python-3.11`
3. Revisar `requirements.txt` no tiene dependencias conflictivas

---

## 📊 Monitoreo Post-Despliegue

### Métricas Esperadas

**BSC Tablero Consolidado:**
```
Perspectiva: Financiera F1
- Objetivo: Rentabilidad de Proyectos
- Avance: 50%
- Estado: 🔴 Rojo
- Proyectos: 28
- Presupuesto Total: $11.9M

Perspectiva: Procesos P1
- Objetivo: Eficiencia Operativa
- Avance: 46.43%
- Estado: 🔴 Rojo
- Duración Promedio: 124.96 días

Perspectiva: Cliente C1
- Objetivo: Satisfacción del Cliente
- Avance: 75.36%
- Estado: 🟡 Amarillo
- Clientes: 14
- Proyectos: 28
```

**OLAP KPIs Ejecutivos:**
- 28 períodos de tiempo
- Proyectos totales por fecha
- Proyectos a tiempo (%)
- Duración promedio
- Eficiencia presupuestaria

---

## 🎯 Checklist Final

- [ ] Backend desplegado en Railway
- [ ] Variables de entorno configuradas
- [ ] URL pública generada
- [ ] Endpoint `/status` retorna OK
- [ ] Endpoint `/datos-datawarehouse` retorna 28 proyectos
- [ ] Endpoint `/olap/kpis` retorna 28 filas
- [ ] Endpoint `/bsc/okr` retorna 3 perspectivas
- [ ] Frontend actualizado con URL de backend
- [ ] Dashboard carga correctamente
- [ ] Gráficos OLAP muestran datos
- [ ] BSC muestra semáforos
- [ ] Frontend desplegado (opcional)

---

## 📞 Soporte

Para issues o preguntas:
1. Revisar logs en Railway: **Deployments** → **View Logs**
2. Verificar conexiones a BD con script de prueba
3. Revisar documentación técnica en `/docs`

---

## 🎉 ¡Listo!

El sistema ETL con Dashboard está completamente desplegado y funcional.

**URLs Finales:**
- Backend API: `https://TU-BACKEND.railway.app`
- Frontend: `https://TU-FRONTEND.vercel.app` (si se desplegó)
- BD Railway: `interchange.proxy.rlwy.net:22434`

**Próximos Pasos:**
1. Configurar refresh automático del ETL (cron job)
2. Agregar más métricas a BSC
3. Crear alertas para proyectos en riesgo
4. Implementar autenticación de usuarios
