# Sistema de Soporte de Decisiones (DSS) - ProyectoETL

**Sistema Integral de Business Intelligence con Cubo OLAP, BSC/OKR y Modelo de Predicción Rayleigh**

Sistema completo de ETL (Extract, Transform, Load) con **Data Warehouse**, **Cubo OLAP**, **Balanced Scorecard/OKR** y **Modelo de Predicción de Defectos** usando distribución de Rayleigh. Diseñado para la **transformación digital** y **excelencia operacional**.

## INICIO RÁPIDO - CONFIGURACIÓN LOCAL

```bash
# 1. Clonar el repositorio
git clone [url-del-repo]
cd ProyectoETL

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar bases de datos MySQL
mysql -u root -p < 01_GestionProyectos/scripts/crear_bd_origen.sql
mysql -u root -p < 04_Datawarehouse/scripts/crear_datawarehouse.sql
mysql -u root -p < 04_Datawarehouse/scripts/olap_views.sql
mysql -u root -p < 04_Datawarehouse/scripts/crear_bsc.sql

# 4. Generar datos de demostración
python 01_GestionProyectos/datos/generar_datos_final.py

# 5. Ejecutar ETL inicial
python src/etl/etl_incremental.py

# 6. Iniciar Dashboard DSS
cd 03_Dashboard
./iniciar_dashboard.sh

# 7. Acceder al sistema
open http://localhost:8080
```

**En pocos minutos tienes el DSS completo funcionando.**

## Visión Estratégica

**"Transformación Digital para la Excelencia Operacional"**

Liderar la transformación digital mediante sistemas de soporte de decisiones, procesos automatizados y analítica avanzada para entregar valor superior a nuestros clientes.

### Arquitectura del Sistema de Soporte de Decisiones (DSS)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD DSS INTEGRADO                          │
├─────────────────┬─────────────────┬─────────────────┬──────────────┤
│   CUBO OLAP     │   BSC/OKR       │  PREDICCIÓN     │   ETL        │
│                 │                 │   (Rayleigh)    │              │
│ • Drill-down    │ • 4 Perspectivas│ • Modelo        │ • Monitoreo  │
│ • Roll-up       │ • Objetivos     │   Estadístico   │ • Control    │
│ • Filtros       │ • Key Results   │ • Control PM    │ • Trazab.    │
│ • Series Temp.  │ • Semáforos     │ • Cronograma    │              │
└─────────────────┴─────────────────┴─────────────────┴──────────────┘
                                │
                    ┌───────────────────────┐
                    │    DATA WAREHOUSE     │
                    │   Esquema Estrella    │
                    ├───────────────────────┤
                    │ • Dimensiones         │
                    │ • Tablas de Hechos    │
                    │ • Vistas OLAP         │
                    │ • Tablas BSC/OKR      │
                    │ • Procedimientos      │
                    └───────────────────────┘
                                │
                    ┌───────────────────────┐
                    │     PROCESO ETL       │
                    │   (02_ETL/scripts/)   │
                    └───────────────────────┘
                                │
                    ┌───────────────────────┐
                    │   BASE DE DATOS       │
                    │      ORIGEN           │
                    │ (01_GestionProyectos) │
                    └───────────────────────┘
```

## Componentes del DSS

### 1. **Cubo OLAP** - Análisis Multidimensional
- **Vistas Materializadas** con `ROLLUP` para agregaciones
- **Drill-down** por Cliente, Equipo, Tiempo
- **Roll-up** automático con niveles de agregación
- **Series Temporales** (mensual, trimestral, anual)
- **KPIs Ejecutivos** en tiempo real

**Endpoints:**
- `GET /olap/kpis` - KPIs con filtros multidimensionales
- `GET /olap/series` - Series temporales configurables
- `GET /olap/kpis-ejecutivos` - Dashboard ejecutivo
- `GET /olap/dimensiones` - Valores para filtros

### 2. **BSC/OKR** - Balanced Scorecard con Objectives & Key Results
- **4 Perspectivas del BSC**: Financiera, Clientes, Procesos Internos, Aprendizaje/Innovación  
- **Objetivos Estratégicos** vinculados con la visión
- **Key Results** con semáforos (verdeamarillorojo)
- **Seguimiento** automático con umbrales
- **Mapa Estratégico** visual interactivo

**Componentes de la Visión:**
- Transformación Digital
- Confiabilidad y Calidad  
- Analítica Avanzada
- Automatización de Procesos
- Excelencia Operacional

**Endpoints:**
- `GET /bsc/okr` - Tablero BSC consolidado
- `POST /bsc/medicion` - Registrar mediciones
- `GET /bsc/vision-estrategica` - Resumen de visión
- `GET /bsc/historico-kr/{id}` - Histórico de KRs

### 3. **Modelo de Predicción Rayleigh** - Predicción de Defectos
- **Distribución de Rayleigh** para modelado de defectos en software
- **Control de Acceso** - Solo Project Managers
- **Predicción Semanal** de defectos esperados
- **Cronograma de Testing** optimizado
- **Métricas de Riesgo** del proyecto

**Fórmulas Implementadas:**
- Función de densidad: `f(t) = (t/σ²) * exp(-t²/(2σ²))`
- Función acumulativa: `F(t) = 1 - exp(-t²/(2σ²))`
- Tasa de fallas: `h(t) = t/σ²`

**Endpoints:**
- `POST /prediccion/defectos-rayleigh` - Generar predicción (requiere PM)
- `GET /prediccion/historico` - Histórico de predicciones
- `GET /prediccion/validar-acceso` - Validar permisos PM

### 4. **ETL y Monitoreo** - Proceso de Datos
- **Monitoreo ETL** en tiempo real
- **Trazabilidad** completa de datos
- **Control de Calidad** automatizado
- **Alertas** y notificaciones

## Arquitectura Modular

El sistema está estructurado en **4 módulos independientes**:

| Módulo | Carpeta | Descripción | Tecnología |
|--------|---------|-------------|------------|
| **1** | `01_GestionProyectos/` | BD Transaccional (OLTP) | MySQL + Python |
| **2** | `02_ETL/` | Scripts SQL y Procedimientos ETL | SQL |
| **3** | `03_Dashboard/` | Dashboard DSS | Flask + HTML/JS |
| **4** | `04_Datawarehouse/` | Data Warehouse + OLAP | MySQL + SQL |

### Estructura Actualizada

```
ProyectoETL/
├── README.md                       # Este archivo
├── requirements.txt                # Dependencias consolidadas
│
├── src/                           # Código fuente principal
│   ├── config/
│   │   └── config_conexion.py    # Configuración centralizada
│   ├── etl/
│   │   └── etl_incremental.py    # ETL incremental con logging
│   └── origen/
│       └── generar_datos.py      # Generador de datos
│
├── 01_GestionProyectos/          # BD Origen (OLTP)
│   ├── datos/
│   │   └── generar_datos_final.py
│   └── scripts/
│       ├── crear_bd_origen.sql
│       ├── crear_estado_remoto.py
│       ├── crear_tabla_estado.sql
│       └── procedimientos_seguros.sql
│
├── 02_ETL/                        # Proceso ETL
│   ├── README.md
│   └── scripts/
│       ├── etl_final.py          # ETL con procedimiento almacenado
│       ├── procedimientos_etl_completo.sql
│       └── procedimientos_etl_final.sql
│
├── 03_Dashboard/                  # Dashboard DSS
│   ├── README.md
│   ├── iniciar_dashboard.sh      # Script de inicio
│   ├── detener_dashboard.sh      # Script de parada
│   ├── backend/
│   │   ├── app.py               # Flask API con todos los endpoints
│   │   ├── rayleigh.py          # Modelo de Predicción Rayleigh
│   │   └── requirements.txt
│   └── frontend/
│       ├── index.html           # UI con módulos integrados
│       ├── app.js
│       └── styles.css
│
├── 04_Datawarehouse/             #  Data Warehouse + OLAP + BSC
│   ├── README.md
│   └── scripts/
│       ├── crear_datawarehouse.sql
│       ├── olap_views.sql       # Cubo OLAP con ROLLUP
│       ├── crear_bsc.sql        # Tablas BSC/OKR
│       ├── consultas_analisis.sql
│       └── procedimientos_seguros_dw.sql
│
├── docs/                         # Documentación
│   └── README.md
│
└── logs/                         #  Archivos de log
```

---

## Variables de Entorno

El sistema utiliza variables de entorno para controlar su comportamiento:

| Variable | Valores | Default | Descripción |
|----------|---------|---------|-------------|
| `ETL_AMBIENTE` | local, distribuido, test | local | Selecciona configuración de conexiones |
| `ETL_DRY_RUN` | 0, 1 | 0 | Modo simulación (no escribe en BD) |
| `ETL_LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR | INFO | Nivel de detalle de logs |

### Ejemplo de uso:

```bash
# macOS / zsh
export ETL_AMBIENTE=local
export ETL_DRY_RUN=0
export ETL_LOG_LEVEL=DEBUG
python src/etl/etl_incremental.py

# Para una sola ejecución
ETL_LOG_LEVEL=WARNING ETL_DRY_RUN=1 python src/etl/etl_incremental.py
```

## Comandos Principales

```bash
# Generar datos de prueba
python 01_GestionProyectos/datos/generar_datos_final.py

# Ejecutar ETL incremental
python src/etl/etl_incremental.py

# Ejecutar ETL con procedimiento almacenado
python 02_ETL/scripts/etl_final.py

# Iniciar Dashboard DSS
cd 03_Dashboard
./iniciar_dashboard.sh

# Detener Dashboard
cd 03_Dashboard
./detener_dashboard.sh
```

---

## Documentación Adicional

Ver cada módulo para documentación específica:
- [01_GestionProyectos/README.md](01_GestionProyectos/README.md) - Base de datos origen
- [02_ETL/README.md](02_ETL/README.md) - Proceso ETL
- [03_Dashboard/README.md](03_Dashboard/README.md) - Dashboard web
- [04_Datawarehouse/README.md](04_Datawarehouse/README.md) - Data Warehouse

---

## Licencia

Proyecto educativo para demostración de conceptos ETL y Data Warehouse.

---

**Si te resulta útil, dale una estrella al repositorio.**

Este proyecto implementa un sistema ETL (Extract, Transform, Load) distribuido que opera en 3 máquinas independientes para procesar datos de gestión de proyectos.

## 🏗 Arquitectura del Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   MÁQUINA 1     │────▶│   MÁQUINA 2     │────▶│   MÁQUINA 3     │
│ GestionProyectos│     │      ETL        │     │  Datawarehouse  │
│                 │     │                 │     │                 │
│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │
│ │ MySQL       │ │     │ │ Python ETL  │ │     │ │ MySQL       │ │
│ │ BD Origen   │ │     │ │ Procesador  │ │     │ │ BD Destino  │ │
│ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      Datos              Transformar           Datawarehouse
```

## Estructura del Proyecto

```
ProyectoETL/
├── README.md                           # Este archivo
├── README_CONFIGURACION.md             # Guía detallada de configuración
├── requirements.txt                    # Dependencias Python
│
├── GestionProyectos/                   #  MÁQUINA 1
│   ├── config_conexion.py             # Configuración de conexiones
│   └── setup_servidor_bd.py           # Configurador automático BD origen
│
├── ETL/                               # MÁQUINA 2
│   ├── etl_distribuido.py             # ETL principal para 3 máquinas
│   ├── etl_principal.py               # ETL original (mejorado)
│   ├── etl_remoto_portable.py         # ETL portable simplificado
│   ├── servidor_etl_simple.py         # Servidor HTTP para ETL
│   ├── setup_etl.py                   # Configurador automático ETL
│   ├── setup_local.py                 # 🧪 Setup para pruebas locales
│   ├── api_backend.py                 # API Flask para dashboard
│   └── web-dashboard/                 #  Dashboard Web
│       ├── index.html                 # Interface principal
│       └── dashboard.js               # Lógica del dashboard
│
└── Datawarehouse/                     # 🏗 MÁQUINA 3
    ├── generacion_datos.py            # Generador de datos de prueba
    ├── script_creacion_db.sql         # Script creación BD origen
    ├── script_datawarehouse.sql       # Script creación datawarehouse
    └── setup_datawarehouse.py         # Configurador automático DW
```

##  Configuración Rápida

### 🧪 Opción 1: Prueba Local (Recomendada para desarrollo)

**Una sola máquina - Todo local:**
```bash
cd ETL
python3 setup_local.py
```
Este comando:
-  Instala dependencias automáticamente
-  Configura bases de datos locales
-  Genera datos de prueba
-  Ejecuta ETL de prueba
-  Inicia dashboard web en http://localhost:5000
-  Abre interfaz visual en navegador

### 🏗 Opción 2: Configuración Distribuida (3 máquinas)

**Máquina 1 (GestionProyectos):**
```bash
cd GestionProyectos
python3 setup_servidor_bd.py
```

**Máquina 2 (ETL):**
```bash
cd ETL
python3 setup_etl.py
```

**Máquina 3 (Datawarehouse):**
```bash
cd Datawarehouse
python3 setup_datawarehouse.py
```

###  Opción 3: Configuración Manual

Ver [README_CONFIGURACION.md](README_CONFIGURACION.md) para pasos detallados.

##  Ejecución del ETL

### 🧪 Modo Local (Desarrollo):
```bash
cd ETL
python3 setup_local.py    # Setup completo con dashboard
# O componentes individuales:
python3 api_backend.py    # Solo API backend
python3 etl_principal.py  # Solo ETL
```

### 🏗 Modo Distribuido (Producción):
```bash
# Desde la Máquina ETL (Máquina 2):
python3 etl_distribuido.py    # ETL distribuido
python3 etl_remoto_portable.py # ETL portable alternativo
```

###  Dashboard Web:
- **Local:** http://localhost:5000 (se abre automáticamente)
- **API Endpoints:** http://localhost:5000/api/status
- **Dashboard:** Abrir `ETL/web-dashboard/index.html` en navegador

### 📡 Via HTTP (opcional):
```bash
# Iniciar servidor ETL
python3 servidor_etl_simple.py

# Ejecutar ETL remotamente
curl -X POST http://IP_MAQUINA_2:8081/ejecutar-etl
```

## Configuración de Red

### IPs de Ejemplo:
- **Máquina 1:** `192.168.1.100` (GestionProyectos)
- **Máquina 2:** `192.168.1.101` (ETL)
- **Máquina 3:** `192.168.1.102` (Datawarehouse)

### Puertos:
- **3306/TCP:** MySQL (Máquinas 1 y 3)
- **8081/TCP:** Servidor ETL HTTP (Máquina 2, opcional)

### Usuarios BD:
- **Usuario:** `etl_user`
- **Password:** `etl_password_123`

##  Bases de Datos

### Base Origen (Máquina 1): `gestionproyectos_hist`
- **Cliente:** Información de clientes
- **Empleado:** Datos de empleados
- **Equipo:** Equipos de trabajo
- **Estado:** Estados de proyectos/tareas
- **Proyecto:** Proyectos con fechas y costos
- **Tarea:** Tareas individuales de proyectos
- **TareaEquipoHist:** Historial de asignaciones

### Datawarehouse (Máquina 3): `dw_proyectos_hist`
- **DimCliente, DimEmpleado, DimEquipo:** Dimensiones
- **DimProyecto:** Dimensión de proyectos
- **DimTiempo:** Dimensión temporal
- **HechoProyecto:** Métricas de proyectos
- **HechoTarea:** Métricas de tareas

##  Verificación del Sistema

### Comprobar Conectividad:
```bash
# Desde Máquina 2 hacia Máquina 1
telnet 192.168.1.100 3306

# Desde Máquina 2 hacia Máquina 3
telnet 192.168.1.102 3306
```

### Verificar Datos:
```sql
-- En origen (Máquina 1)
SELECT COUNT(*) FROM gestionproyectos_hist.Proyecto;

-- En destino (Máquina 3)
SELECT COUNT(*) FROM dw_proyectos_hist.HechoProyecto;
```

##  Requisitos

### Software:
- **Python 3.6+** (Máquina 2)
- **MySQL/XAMPP** (Máquinas 1 y 3)

### Dependencias Python:
```bash
# Instalación automática en setup_local.py, o manual:
pip install pandas sqlalchemy mysql-connector-python numpy flask flask-cors faker
```

### Red:
- Conectividad TCP entre las 3 máquinas
- Puertos MySQL (3306) abiertos
- Permisos de firewall configurados

##  Solución de Problemas

### Error de Conexión:
1. Verificar que MySQL esté funcionando
2. Comprobar conectividad de red
3. Revisar configuración de firewall
4. Verificar usuarios y permisos MySQL

### Sin Datos en Origen:
1. Ejecutar `generacion_datos.py` en Máquina 1
2. Verificar que hay proyectos cerrados
3. Comprobar estructura de base de datos

### ETL Falla:
1. Verificar conectividad a ambas máquinas
2. Comprobar permisos de usuario `etl_user`
3. Revisar logs de error en consola
4. Verificar estructura del datawarehouse

##  Características del Dashboard Web

###  Interface Visual Completa:
- **Dashboard Principal:** Métricas en tiempo real y gráficos
- **Datos Origen:** Visualización de tablas de la BD transaccional
- **Control ETL:** Ejecución visual del ETL con logs en tiempo real
- **DataWarehouse:** Exploración de dimensiones y hechos
- **Análisis:** Reportes y gráficos de cumplimiento

### 🎮 Controles Interactivos:
-  **Generar Datos:** Botón para crear datos de prueba
-  **Ejecutar ETL:** Control visual con barra de progreso
-  **Visualizar Resultados:** Tablas dinámicas y gráficos
-  **Monitoreo:** Estado de conexiones en tiempo real
-  **Logs ETL:** Console log de la ejecución ETL

### 📱 Responsive Design:
- Interface adaptable a desktop y móvil
- Navegación por tabs y secciones
- Gráficos interactivos con Chart.js
- Bootstrap 5 para styling moderno

## * Seguridad

- Cambiar passwords por defecto en producción
- Usar VPN para conexiones entre máquinas
- Configurar firewall restrictivo
- Monitorear conexiones MySQL
- Realizar backups regulares

## Documentación Adicional

- [README_CONFIGURACION.md](README_CONFIGURACION.md) - Guía detallada de configuración
- Comentarios en código fuente para lógica específica
- Scripts de configuración automática incluidos

---

**Versión:** 1.0  
**Autor:** Sistema ETL Distribuido  
**Fecha:** Octubre 2025

##  Descripción

Este proyecto implementa un sistema ETL completo que:
- Extrae datos de una base de datos transaccional de gestión de proyectos
- Transforma y limpia los datos 
- Carga los datos en un Data Warehouse optimizado para análisis

## 🏗 Arquitectura

### Bases de Datos
- **gestionproyectos_hist**: Base de datos transaccional (fuente)
- **dw_proyectos_hist**: Data Warehouse (destino)

### Componentes
- **ETL Principal**: Proceso completo de extracción, transformación y carga
- **ETL Remoto Portable**: Versión independiente para ejecución remota
- **Servidor ETL**: API HTTP para ejecución remota del ETL
- **Generación de Datos**: Script para poblar la base de datos de prueba

## Estructura del Proyecto

```
ProyectoETL/
├── README.md                    # Este archivo
├── generacion_datos.py          # Script para generar datos de prueba
├── etl_principal.py             # ETL principal local
├── etl_remoto_portable.py       # ETL portable para ejecución remota
├── servidor_etl_simple.py       # Servidor HTTP para ETL remoto
├── config_conexion.py           # Configuración de conexiones
├── script_creacion_db.sql       # Script de creación de BD transaccional
└── script_datawarehouse.sql     # Script de creación del Data Warehouse
```

##  Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

### Dependencias de Python
```bash
pip install pandas sqlalchemy mysql-connector-python
```

### Configuración de Base de Datos

1. **Crear las bases de datos**:
   ```sql
   -- Ejecutar script_creacion_db.sql
   -- Ejecutar script_datawarehouse.sql
   ```

2. **Configurar conexiones**:
   Editar `config_conexion.py` con tus credenciales de MySQL.

##  Uso

### 1. Generación de Datos de Prueba
```bash
python generacion_datos.py
```

### 2. Ejecución del ETL Local
```bash
python etl_principal.py
```

### 3. ETL Remoto Portable
```bash
python etl_remoto_portable.py
```

### 4. Servidor ETL (para acceso HTTP)
```bash
python servidor_etl_simple.py
```
Luego acceder a: `http://localhost:8081`

##  Data Warehouse - Esquema Dimensional

### Tablas de Dimensiones
- **DimCliente**: Información de clientes
- **DimEmpleado**: Datos de empleados  
- **DimEquipo**: Información de equipos
- **DimProyecto**: Detalles de proyectos
- **DimTiempo**: Dimensión temporal

### Tabla de Hechos
- **FactTareas**: Métricas y KPIs de tareas

## Configuración Avanzada

### Conexión Remota
Para habilitar conexiones remotas a MySQL:
1. Configurar `bind-address = 0.0.0.0` en MySQL
2. Crear usuario con permisos remotos
3. Abrir puerto 3306 en firewall

### Variables de Entorno
El sistema soporta configuración via variables de entorno:
- `DB_HOST`: Host de la base de datos
- `DB_PORT`: Puerto de MySQL  
- `DB_USER`: Usuario de base de datos
- `DB_PASSWORD`: Contraseña

##  Funcionalidades

### ETL Principal
-  Extracción de datos transaccionales
-  Transformación y limpieza de datos
-  Carga incremental en Data Warehouse
-  Manejo de dimensiones SCD (Slowly Changing Dimensions)
-  Logging y monitoreo

### ETL Remoto
-  Ejecución independiente
-  Auto-instalación de dependencias
-  Configuración flexible
-  Manejo de errores robusto

### Servidor ETL
-  API REST para ejecución remota
-  Interface web simple
-  Logs de ejecución
-  Estado de procesos

##  Tecnologías Utilizadas

- **Python**: Lenguaje principal
- **Pandas**: Manipulación de datos
- **SQLAlchemy**: ORM y conexiones de base de datos
- **MySQL**: Sistema de gestión de base de datos
- **HTTP Server**: Para API remota

##  Licencia

Este proyecto está bajo la Licencia MIT - ver archivo LICENSE para detalles.

##  Contribución

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o preguntas, crear un issue en el repositorio.
