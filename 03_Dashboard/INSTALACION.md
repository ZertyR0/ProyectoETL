# 📦 Instalación - Módulo 2: Dashboard

## 🎯 Descripción

Este módulo contiene el **Dashboard Web** con:
- **Backend**: API REST con Flask
- **Frontend**: Interfaz web HTML/CSS/JavaScript
- **Gestión de procesos**: Scripts de inicio/detención automáticos

⚠️ **Importante**: Este módulo requiere acceso a **Módulo 1** (BD Origen) y **Módulo 3** (Data Warehouse).

---

## 📋 Requisitos Previos

- **Python 3.8+**
- **pip** (gestor de paquetes Python)
- Acceso a **Módulo 1** instalado (BD Origen)
- Acceso a **Módulo 3** instalado (Data Warehouse)
- Navegador web moderno

---

## 🚀 Instalación Rápida (Automática)

```bash
# 1. Entrar a la carpeta del módulo
cd 03_Dashboard

# 2. Ejecutar script de instalación
./setup_dashboard.sh

# 3. Seguir las instrucciones en pantalla
```

El script hará:
- ✅ Verificar Python
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Configurar archivo `.env`
- ✅ Verificar conexiones a BD Origen y Data Warehouse

---

## 🔧 Instalación Manual

### Paso 1: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Conexiones

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con las IPs de tus módulos:
```bash
# Configuración del Backend Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False

# Conexión a Base de Datos Origen (Módulo 1)
DB_ORIGEN_HOST=localhost       # Cambiar si está en otro servidor
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password_123

# Conexión a Data Warehouse (Módulo 3)
DB_DW_HOST=localhost           # Cambiar si está en otro servidor
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=etl_user
DB_DW_PASSWORD=etl_password_123

# Configuración del Frontend
FRONTEND_PORT=8080
API_BASE_URL=http://localhost:5001

# CORS (opcional)
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

---

## 🗂️ Estructura de Archivos

```
03_Dashboard/
├── README.md                    # Documentación general
├── INSTALACION.md              # Esta guía
├── requirements.txt            # Dependencias Python
├── .env.example               # Plantilla de configuración
├── .env                       # Tu configuración (no subir a Git)
├── setup_dashboard.sh         # Instalación automática
├── iniciar_dashboard.sh       # Script para iniciar
├── detener_dashboard.sh       # Script para detener
├── backend/
│   ├── app.py                 # API Flask
│   └── requirements.txt       # Dependencias específicas
├── frontend/
│   ├── index.html             # Interfaz web
│   ├── app.js                 # Lógica JavaScript
│   └── styles.css             # Estilos
└── logs/                      # Logs de ejecución
```

---

## ▶️ Iniciar el Dashboard

### Método 1: Script Automático (Recomendado)

```bash
./iniciar_dashboard.sh
```

Esto:
- ✅ Verifica que los puertos estén libres (5001 y 8080)
- ✅ Inicia el backend Flask en segundo plano
- ✅ Inicia el frontend en segundo plano
- ✅ Guarda logs en `logs/backend.log` y `logs/frontend.log`
- ✅ Abre el dashboard en tu navegador

### Método 2: Manual (2 Terminales)

**Terminal 1 - Backend**:
```bash
source venv/bin/activate
cd backend
python app.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend
python -m http.server 8080
```

**Abrir en navegador**:
```
http://localhost:8080/index.html
```

---

## ⏹️ Detener el Dashboard

### Método 1: Script Automático

```bash
./detener_dashboard.sh
```

### Método 2: Manual

```bash
# Encontrar procesos
ps aux | grep "python.*app.py"
ps aux | grep "http.server 8080"

# Matar procesos
kill <PID_backend>
kill <PID_frontend>
```

---

## 🧪 Verificar Instalación

### 1. Verificar Backend

```bash
# Backend debe responder
curl http://localhost:5001/

# Respuesta esperada: {"message": "API funcionando"}
```

### 2. Verificar Frontend

Abre en navegador:
```
http://localhost:8080/index.html
```

Deberías ver:
- ✅ Dashboard con gráficos
- ✅ Tabs de navegación
- ✅ Datos de proyectos

### 3. Verificar Conexiones a BD

```bash
# Ver logs del backend
tail -f logs/backend.log

# Buscar mensajes de conexión exitosa
# "Conectado a BD Origen"
# "Conectado a Data Warehouse"
```

---

## 🌐 Configurar para Acceso Remoto

### 1. Modificar `.env`

```bash
# Cambiar localhost por 0.0.0.0 para aceptar conexiones remotas
FLASK_HOST=0.0.0.0
API_BASE_URL=http://TU_IP_PUBLICA:5001
```

### 2. Abrir puertos en firewall

```bash
# Ubuntu/Debian
sudo ufw allow 5001/tcp
sudo ufw allow 8080/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=5001/tcp --permanent
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

### 3. Actualizar CORS en backend

Edita `backend/app.py`:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])  # O especifica dominios: ["http://192.168.1.100:8080"]
```

### 4. Actualizar Frontend

Edita `frontend/app.js`:
```javascript
const API_BASE_URL = 'http://192.168.1.101:5001';  // Tu IP del servidor
```

### 5. Acceder desde otra máquina

```
http://192.168.1.101:8080/index.html
```

---

## 📊 Uso del Dashboard

### Funcionalidades Disponibles

1. **Vista General**
   - Total de proyectos
   - Total de empleados
   - Total de clientes
   - Gráficos de distribución

2. **Proyectos**
   - Listado completo
   - Filtros por estado
   - Detalles individuales

3. **Análisis**
   - Proyectos por estado
   - Empleados por proyecto
   - Presupuesto vs. Real

4. **Data Warehouse**
   - Análisis dimensional
   - KPIs históricos
   - Tendencias temporales

---

## 🔄 Reiniciar Dashboard

```bash
# Detener
./detener_dashboard.sh

# Esperar 2 segundos
sleep 2

# Iniciar
./iniciar_dashboard.sh
```

---

## 🗑️ Desinstalar

```bash
# 1. Detener servicios
./detener_dashboard.sh

# 2. Eliminar entorno virtual
rm -rf venv/

# 3. Eliminar archivos de configuración
rm .env

# 4. Eliminar logs
rm -rf logs/
```

---

## 🐛 Solución de Problemas

### Error: "Address already in use" (Puerto ocupado)

**Causa**: Los puertos 5001 o 8080 están siendo usados.

**Solución**:
```bash
# Ver qué está usando el puerto
lsof -i :5001
lsof -i :8080

# Matar proceso
kill -9 <PID>

# O usar el script
./detener_dashboard.sh
```

### Error: "Connection refused" a BD

**Causa**: No puede conectarse a Módulo 1 o Módulo 3.

**Solución**:
1. Verifica que los módulos estén corriendo
2. Verifica las IPs en `.env`
3. Verifica los firewalls
4. Verifica los usuarios de BD

```bash
# Probar conexión manual
mysql -h <IP_MODULO1> -u etl_user -p gestionproyectos_hist
mysql -h <IP_MODULO3> -u etl_user -p dw_proyectos_hist
```

### Error: "No module named 'flask'"

**Causa**: Dependencias no instaladas.

**Solución**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend no carga datos

**Causa**: Backend no está corriendo o URL incorrecta.

**Solución**:
1. Verifica que el backend esté corriendo: `curl http://localhost:5001/`
2. Abre la consola del navegador (F12) y busca errores
3. Verifica `API_BASE_URL` en `frontend/app.js`

### Error: CORS Policy

**Causa**: El navegador bloquea peticiones por CORS.

**Solución**:
```bash
# En backend/app.py, asegúrate de tener:
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
```

---

## 📈 Próximos Pasos

1. ✅ Dashboard instalado correctamente
2. ⬜ Personalizar gráficos
3. ⬜ Agregar nuevos endpoints
4. ⬜ Configurar SSL/HTTPS

---

## 📞 Información de Acceso

Una vez instalado, accede al dashboard en:

```
Frontend: http://localhost:8080/index.html
Backend API: http://localhost:5001/

Endpoints principales:
- GET  /proyectos              → Lista proyectos
- GET  /empleados              → Lista empleados
- GET  /clientes               → Lista clientes
- GET  /dw/proyectos_estado    → Análisis DW
- GET  /dw/empleados_proyecto  → Análisis DW
```

---

## 📚 Documentación Adicional

- [README del Módulo](README.md)
- [Documentación de API](API_ENDPOINTS.md)
- [Guía de Módulos Independientes](../GUIA_MODULOS_INDEPENDIENTES.md)

---

**¿Instalación exitosa?** → Explora el dashboard y personaliza según tus necesidades 🎉
