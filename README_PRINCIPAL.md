# 🚀 Sistema ETL Distribuido - Gestión de Proyectos

Sistema completo de ETL (Extract, Transform, Load) para análisis de datos de gestión de proyectos, con soporte para arquitectura distribuida y dashboard de monitoreo.

## 📁 Estructura del Proyecto

```
ProyectoETL/
├── README.md                           # Este archivo
├── setup_proyecto.py                   # Script de configuración automática
├── requirements.txt                    # Dependencias globales
├── 01_GestionProyectos/               # 📊 Base de Datos Origen
│   ├── README.md
│   ├── scripts/
│   │   ├── crear_bd_origen.sql
│   │   └── generar_datos.py
│   └── datos/
├── 02_ETL/                            # 🔄 Proceso ETL
│   ├── README.md
│   ├── scripts/
│   │   ├── etl_principal.py
│   │   └── etl_utils.py
│   └── config/
│       └── config_conexion.py
├── 03_Dashboard/                      # 📊 Dashboard Web
│   ├── README.md
│   ├── backend/
│   │   ├── app.py
│   │   └── requirements.txt
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── styles.css
└── 04_Datawarehouse/                 # 🏢 Datawarehouse
    ├── README.md
    └── scripts/
        ├── crear_datawarehouse.sql
        └── consultas_analisis.sql
```

## 🎯 Descripción General

### 🏗️ Arquitectura del Sistema

El sistema está diseñado para funcionar en **3 configuraciones**:

1. **🖥️ Local**: Todo en una máquina (desarrollo/testing)
2. **🌐 Distribuido**: 3 máquinas separadas (producción)
3. **🧪 Testing**: Ambiente de pruebas aislado

### 📊 Flujo de Datos

```
[BD Origen] ➜ [Proceso ETL] ➜ [Datawarehouse] ➜ [Dashboard]
     ↑              ↓              ↓              ↓
Gestión de     Transform &     Business       Monitoreo
Proyectos      Calculate      Intelligence    & Control
```

## 🚀 Inicio Rápido

### 1. Configuración Automática
```bash
# Configurar todo el proyecto automáticamente
python setup_proyecto.py

# O paso a paso:
python setup_proyecto.py --solo-dependencias
python setup_proyecto.py --solo-bases-datos
python setup_proyecto.py --solo-datos
```

### 2. Configuración Manual

#### Paso 1: Dependencias
```bash
pip install -r requirements.txt
```

#### Paso 2: Bases de Datos
```bash
# Crear BD origen
mysql -u root -p < 01_GestionProyectos/scripts/crear_bd_origen.sql

# Crear datawarehouse
mysql -u root -p < 04_Datawarehouse/scripts/crear_datawarehouse.sql
```

#### Paso 3: Datos de Prueba
```bash
cd 01_GestionProyectos/scripts
python generar_datos.py
```

#### Paso 4: Ejecutar ETL
```bash
cd 02_ETL/scripts
python etl_principal.py
```

#### Paso 5: Dashboard
```bash
# Terminal 1: Backend
cd 03_Dashboard/backend
python app.py

# Terminal 2: Frontend (opcional)
cd 03_Dashboard/frontend
python -m http.server 8000
```

## 🔧 Configuración

### Variables de Ambiente

```bash
# Tipo de ambiente
export ETL_AMBIENTE=local          # local|distribuido|test

# Base de datos origen
export ETL_HOST_ORIGEN=localhost
export ETL_USER_ORIGEN=root
export ETL_PASSWORD_ORIGEN=
export ETL_DB_ORIGEN=gestionproyectos_hist

# Datawarehouse
export ETL_HOST_DESTINO=localhost
export ETL_USER_DESTINO=root
export ETL_PASSWORD_DESTINO=
export ETL_DB_DESTINO=dw_proyectos_hist
```

### Configuración Distribuida (3 Máquinas)

#### Máquina 1: Base de Datos Origen
```bash
# IP: 172.26.163.200
# Contiene: gestionproyectos_hist
# Usuario: etl_user / etl_password_123
```

#### Máquina 2: Proceso ETL + Dashboard
```bash
# IP: 172.26.163.201 (esta máquina)
# Ejecuta: ETL + Dashboard
# Se conecta a máquinas 1 y 3
```

#### Máquina 3: Datawarehouse
```bash
# IP: 172.26.164.100
# Contiene: dw_proyectos_hist
# Usuario: etl_user / etl_password_123
```

## 📋 Componentes Principales

### 📊 01_GestionProyectos
- **Base de datos origen** con datos operacionales
- **Tablas**: Cliente, Empleado, Equipo, Proyecto, Tarea, Estado
- **Scripts de creación** y generación de datos

### 🔄 02_ETL
- **Proceso ETL completo** con logging avanzado
- **Configuración flexible** para diferentes ambientes
- **Transformaciones complejas** y cálculo de métricas
- **Manejo de errores** y validaciones

### 📊 03_Dashboard
- **API REST** (Flask) para control del ETL
- **Interfaz web** responsiva para monitoreo
- **Visualización en tiempo real** del proceso
- **Control de ejecución** y gestión de datos

### 🏢 04_Datawarehouse
- **Esquema estrella** optimizado para análisis
- **Dimensiones** (Cliente, Empleado, Equipo, Proyecto, Tiempo)
- **Hechos** (Métricas de Proyectos y Tareas)
- **Consultas de análisis** predefinidas

## 🎯 Funcionalidades

### ✅ Proceso ETL
- [x] Extracción desde BD origen
- [x] Transformación y cálculo de métricas
- [x] Carga a datawarehouse
- [x] Validación de datos
- [x] Logging detallado
- [x] Manejo de errores

### ✅ Dashboard
- [x] Monitoreo de conexiones
- [x] Control de procesos ETL
- [x] Visualización de datos
- [x] Generación de datos de prueba
- [x] Limpieza de tablas
- [x] Logs en tiempo real

### ✅ Business Intelligence
- [x] Métricas de proyectos
- [x] Análisis de cumplimiento
- [x] Productividad de empleados
- [x] Tendencias temporales
- [x] Reportes ejecutivos

## 📊 Métricas y KPIs

### Proyectos
- Cumplimiento de tiempo y presupuesto
- Variaciones de cronograma y costos
- Eficiencia de recursos
- Rentabilidad por proyecto
- Satisfacción del cliente

### Empleados
- Productividad por empleado
- Eficiencia en horas
- Cumplimiento de plazos
- Carga de trabajo

### Equipos
- Utilización de equipos
- Eficiencia por departamento
- Colaboración en proyectos

## 🐛 Solución de Problemas

### Conexión a Base de Datos
```bash
# Verificar configuración
cd 02_ETL/config
python config_conexion.py local

# Probar conexiones
python config_conexion.py distribuido
```

### Errores en ETL
```bash
# Ejecutar con logging detallado
cd 02_ETL/scripts
python etl_principal.py local

# Verificar datos origen
python -c "from etl_utils import configurar_logging; logger = configurar_logging('DEBUG')"
```

### Problemas de Dashboard
```bash
# Verificar backend
cd 03_Dashboard/backend
python app.py

# Verificar frontend (abrir en navegador)
file:///ruta/al/03_Dashboard/frontend/index.html
```

## 📈 Próximas Mejoras

- [ ] Autenticación y autorización
- [ ] Scheduled ETL (cron jobs)
- [ ] Alertas automáticas
- [ ] Exportación de reportes
- [ ] API para terceros
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring avanzado

## 👥 Equipo

- **Desarrollador Principal**: [Tu nombre]
- **Proyecto**: Sistema ETL Distribuido
- **Fecha**: Octubre 2025
- **Versión**: 1.0

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

---

**🎉 ¡Gracias por usar nuestro Sistema ETL Distribuido!**

Para más información, consulta los README específicos en cada carpeta o contacta al equipo de desarrollo.
