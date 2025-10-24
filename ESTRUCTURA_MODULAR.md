# 📦 ESTRUCTURA MODULAR DEL PROYECTO

## 🎯 División del Proyecto en 3 Partes Independientes

El proyecto está dividido en **3 módulos independientes** que pueden ser enviados, desplegados y mantenidos por separado.

---

## 📊 Análisis de la Estructura Actual

### ✅ Estado Actual

La estructura actual **YA está dividida en componentes separados**:

```
ProyectoETL/
├── 01_GestionProyectos/    → MÓDULO 1: Base de Datos Origen
├── 03_Dashboard/           → MÓDULO 2: Vista/Frontend
└── 04_Datawarehouse/       → MÓDULO 3: Data Warehouse
```

### 🔄 Ajustes Necesarios

Para hacer los módulos completamente independientes, necesitamos:

1. ✅ **Separar dependencias** - Cada módulo con su propio `requirements.txt`
2. ✅ **Separar configuraciones** - Cada módulo con su propia configuración
3. ✅ **Documentación individual** - README completo por módulo
4. ✅ **Scripts de instalación** - Setup independiente por módulo

---

## 📦 MÓDULO 1: Base de Datos de Gestión (Origen)

### Estructura

```
01_GestionProyectos/
├── README.md ✅                    # Documentación completa
├── requirements.txt ⭐             # Dependencias del módulo
├── .env.example ⭐                 # Configuración de ejemplo
├── setup_bd_origen.sh ⭐           # Script de instalación
│
├── scripts/
│   ├── crear_bd_origen.sql        # Creación de BD
│   ├── procedimientos_seguros.sql # Stored procedures
│   ├── generar_datos.py           # Generador de datos
│   ├── generar_datos_seguro.py    # Generador seguro
│   └── config_bd.py ⭐            # Configuración BD
│
├── datos/
│   └── (datos generados)
│
└── docs/ ⭐
    ├── INSTALACION.md             # Guía de instalación
    ├── API_PROCEDURES.md          # Documentación de procedures
    └── ESTRUCTURA_BD.md           # Esquema de BD
```

### Contenido Necesario

- ✅ Base de datos transaccional (OLTP)
- ✅ Stored procedures seguros
- ✅ Triggers de auditoría
- ✅ Generación de datos de prueba
- ⭐ Configuración independiente
- ⭐ Scripts de instalación propios

### Dependencias

```txt
mysql-connector-python==9.4.0
faker==37.11.0
python-dotenv==1.0.0
```

---

## 📦 MÓDULO 2: Vista/Dashboard (Frontend + Backend)

### Estructura

```
03_Dashboard/
├── README.md ✅                    # Documentación completa
├── requirements.txt ⭐             # Dependencias del módulo
├── .env.example ⭐                 # Configuración de ejemplo
├── setup_dashboard.sh ⭐           # Script de instalación
├── docker-compose.yml ⭐           # Docker opcional
│
├── backend/
│   ├── app.py ✅                  # API Flask
│   ├── requirements.txt ✅        # Dependencias backend
│   ├── config.py ⭐               # Configuración backend
│   ├── routes/ ⭐                 # Rutas organizadas
│   │   ├── __init__.py
│   │   ├── datos.py
│   │   ├── etl.py
│   │   └── dashboard.py
│   └── utils/ ⭐
│       ├── __init__.py
│       ├── db_connection.py
│       └── validators.py
│
├── frontend/
│   ├── index.html ✅
│   ├── app.js ✅
│   ├── styles.css ✅
│   ├── config.js ⭐               # Configuración frontend
│   ├── components/ ⭐
│   │   ├── dashboard.js
│   │   ├── charts.js
│   │   └── tables.js
│   └── assets/
│       ├── images/
│       └── fonts/
│
└── docs/ ⭐
    ├── INSTALACION.md
    ├── API_ENDPOINTS.md
    ├── CONFIGURACION.md
    └── DESARROLLO.md
```

### Contenido Necesario

- ✅ API RESTful (Flask)
- ✅ Frontend interactivo (HTML/CSS/JS)
- ⭐ Configuración de conexiones a BD externa
- ⭐ Scripts de instalación independientes
- ⭐ Variables de entorno para endpoints

### Dependencias

```txt
Flask==3.1.0
Flask-CORS==5.0.0
mysql-connector-python==9.4.0
python-dotenv==1.0.0
requests==2.32.0
```

---

## 📦 MÓDULO 3: Data Warehouse

### Estructura

```
04_Datawarehouse/
├── README.md ✅                    # Documentación completa
├── requirements.txt ⭐             # Dependencias del módulo
├── .env.example ⭐                 # Configuración de ejemplo
├── setup_dw.sh ⭐                  # Script de instalación
│
├── scripts/
│   ├── crear_datawarehouse.sql ✅
│   ├── procedimientos_seguros_dw.sql ✅
│   ├── consultas_analisis.sql ✅
│   ├── etl_dw.py ⭐               # ETL específico del DW
│   └── config_dw.py ⭐            # Configuración DW
│
├── etl/ ⭐                         # Proceso ETL integrado
│   ├── __init__.py
│   ├── extractor.py
│   ├── transformer.py
│   ├── loader.py
│   └── config_conexion.py
│
└── docs/ ⭐
    ├── INSTALACION.md
    ├── MODELO_DIMENSIONAL.md
    ├── CONSULTAS.md
    └── ETL_PROCESS.md
```

### Contenido Necesario

- ✅ Data Warehouse (modelo dimensional)
- ✅ Stored procedures seguros
- ✅ Consultas de análisis
- ⭐ ETL integrado
- ⭐ Configuración de conexión a BD origen
- ⭐ Scripts de instalación propios

### Dependencias

```txt
mysql-connector-python==9.4.0
pandas==2.2.0
numpy==1.26.0
sqlalchemy==2.0.44
python-dotenv==1.0.0
```

---

## 🔗 Comunicación Entre Módulos

### Configuración de Conexiones

Cada módulo necesita saber cómo conectarse a los otros:

#### MÓDULO 1 → Expone
- Host: `localhost` (o IP del servidor)
- Puerto: `3306`
- Base de datos: `gestionproyectos_hist`
- Usuario: `etl_user` (con permisos de lectura)

#### MÓDULO 2 → Conecta a
- **Módulo 1** para leer datos origen
- **Módulo 3** para leer datos del DW

#### MÓDULO 3 → Conecta a
- **Módulo 1** para extraer datos (ETL)

---

## 📋 Archivos de Configuración por Módulo

### MÓDULO 1: `.env`

```bash
# Base de Datos Origen
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestionproyectos_hist
DB_USER=root
DB_PASSWORD=tu_password

# Configuración
ENVIRONMENT=development
DEBUG=True
```

### MÓDULO 2: `.env`

```bash
# API Backend
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=True

# Base de Datos Origen
DB_ORIGEN_HOST=localhost
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password

# Data Warehouse
DB_DW_HOST=localhost
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=etl_user
DB_DW_PASSWORD=etl_password

# Frontend
FRONTEND_PORT=8080
```

### MÓDULO 3: `.env`

```bash
# Data Warehouse
DB_DW_HOST=localhost
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=root
DB_DW_PASSWORD=tu_password

# Base de Datos Origen (para ETL)
DB_ORIGEN_HOST=localhost
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password

# Configuración ETL
ETL_BATCH_SIZE=1000
ETL_LOG_LEVEL=INFO
```

---

## 🚀 Scripts de Instalación Independientes

### MÓDULO 1: `setup_bd_origen.sh`

```bash
#!/bin/bash
echo "=== Instalando Módulo 1: Base de Datos Origen ==="

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edita el archivo .env con tus credenciales"
fi

# Crear base de datos
mysql -u root -p < scripts/crear_bd_origen.sql

# Instalar stored procedures
mysql -u root -p < scripts/procedimientos_seguros.sql

# Generar datos de prueba
python scripts/generar_datos_seguro.py

echo "✅ Módulo 1 instalado correctamente"
```

### MÓDULO 2: `setup_dashboard.sh`

```bash
#!/bin/bash
echo "=== Instalando Módulo 2: Dashboard ==="

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edita el archivo .env con las conexiones a BD"
fi

# Instalar dependencias de backend
cd backend
pip install -r requirements.txt
cd ..

echo "✅ Módulo 2 instalado correctamente"
echo "📝 Configura las conexiones en .env"
echo "🚀 Inicia con: ./iniciar_dashboard.sh"
```

### MÓDULO 3: `setup_dw.sh`

```bash
#!/bin/bash
echo "=== Instalando Módulo 3: Data Warehouse ==="

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edita el archivo .env con tus credenciales"
fi

# Crear data warehouse
mysql -u root -p < scripts/crear_datawarehouse.sql

# Instalar stored procedures
mysql -u root -p < scripts/procedimientos_seguros_dw.sql

echo "✅ Módulo 3 instalado correctamente"
echo "📝 Configura la conexión a BD origen en .env"
echo "🚀 Ejecuta ETL con: python etl/etl_dw.py"
```

---

## 📦 Empaquetado para Envío

### Opción 1: Archivos ZIP Separados

```bash
# Módulo 1
zip -r Modulo1_BD_Origen.zip 01_GestionProyectos/

# Módulo 2
zip -r Modulo2_Dashboard.zip 03_Dashboard/

# Módulo 3
zip -r Modulo3_DataWarehouse.zip 04_Datawarehouse/
```

### Opción 2: Repositorios Git Separados

```bash
# Crear 3 repositorios independientes
ProyectoETL-BD-Origen/
ProyectoETL-Dashboard/
ProyectoETL-DataWarehouse/
```

### Opción 3: Carpetas Compartidas

Compartir cada carpeta por separado en Google Drive, Dropbox, etc.

---

## ✅ Checklist de Independencia

### MÓDULO 1 ✅
- [x] README.md completo
- [ ] requirements.txt propio
- [ ] .env.example
- [ ] setup_bd_origen.sh
- [ ] config_bd.py
- [ ] Documentación en docs/

### MÓDULO 2 ✅
- [x] README.md completo
- [x] requirements.txt en backend
- [ ] .env.example
- [ ] setup_dashboard.sh
- [ ] Configuración separada
- [ ] Documentación en docs/

### MÓDULO 3 ✅
- [x] README.md completo
- [ ] requirements.txt propio
- [ ] .env.example
- [ ] setup_dw.sh
- [ ] ETL integrado
- [ ] Documentación en docs/

---

## 🎯 Recomendaciones

### Para Desarrollo Distribuido

1. **Usa variables de entorno** (`.env`) para configuración
2. **Documenta las APIs** entre módulos
3. **Versionado independiente** para cada módulo
4. **Testing independiente** por módulo

### Para Despliegue

1. **Módulo 1**: Servidor de BD dedicado
2. **Módulo 2**: Servidor web/aplicación
3. **Módulo 3**: Servidor de análisis/DW

### Para Mantenimiento

1. Cada módulo puede actualizarse **independientemente**
2. Documentación **autocontenida** en cada módulo
3. Scripts de instalación **específicos** por módulo

---

## 📞 Siguiente Paso

¿Quieres que implemente estos ajustes ahora? Los pasos serían:

1. ✅ Crear `requirements.txt` individual por módulo
2. ✅ Crear `.env.example` por módulo
3. ✅ Crear scripts de instalación independientes
4. ✅ Reorganizar código para independencia
5. ✅ Actualizar documentación por módulo

---

**Estado Actual**: ✅ Estructura base correcta, necesita ajustes de independencia  
**Acción Recomendada**: Implementar archivos de configuración y scripts individuales

[Volver al README Principal](README.md)
