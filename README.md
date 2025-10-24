# 🚀 ProyectoETL - Sistema de Gestión de Proyectos

Sistema completo de ETL (Extract, Transform, Load) con Data Warehouse y Dashboard Web interactivo.

## 📦 Proyecto Modular - 3 Módulos Independientes

Este proyecto está estructurado en **3 módulos completamente independientes** que pueden ser:
- ✅ Enviados por separado
- ✅ Instalados independientemente  
- ✅ Desplegados en máquinas diferentes
- ✅ Mantenidos de forma aislada

### Los 3 Módulos:

| Módulo | Carpeta | Descripción | Independiente |
|--------|---------|-------------|---------------|
| **1** | `01_GestionProyectos/` | Base de Datos Transaccional (OLTP) | ✅ Sí |
| **2** | `03_Dashboard/` | Dashboard Web (Frontend + Backend Flask) | ⚠️  Requiere Módulos 1 y 3 |
| **3** | `04_Datawarehouse/` | Data Warehouse + ETL | ⚠️  Requiere Módulo 1 |

### 📖 Documentación de Módulos:

- **[RESUMEN_MODULAR.md](RESUMEN_MODULAR.md)** - ⭐ Empieza aquí: Resumen ejecutivo
- **[GUIA_MODULOS_INDEPENDIENTES.md](GUIA_MODULOS_INDEPENDIENTES.md)** - Guía completa de uso
- **[VERIFICACION_MODULOS.md](VERIFICACION_MODULOS.md)** - Checklist de independencia
- **[INDICE_MODULAR.md](INDICE_MODULAR.md)** - Índice completo de documentación

---

## ⚡ Inicio Rápido

# Sistema ETL de Gestión de Proyectos con Seguridad Avanzada

## 🎯 Descripción del Proyecto

Sistema completo de **ETL (Extract, Transform, Load)** para gestión de proyectos históricos con implementación de seguridad mediante **Stored Procedures** y **Triggers**, incluyendo un **Dashboard Web** interactivo para monitoreo y análisis.

### Características Principales

- ✅ **Seguridad por Diseño**: Todo el acceso a datos mediante stored procedures
- ✅ **Trazabilidad Completa**: Sistema de auditoría con triggers automáticos
- ✅ **ETL Robusto**: Transformación y carga de datos con validaciones
- ✅ **Dashboard Interactivo**: Visualización en tiempo real con gráficos
- ✅ **Multi-entorno**: Configuración para desarrollo y producción

---

## 📁 Estructura del Proyecto

```
ProyectoETL/
│
├── 01_GestionProyectos/        # Base de datos origen
│   ├── scripts/                 # Scripts SQL y Python
│   │   ├── crear_bd_origen.sql
│   │   ├── generar_datos.py
│   │   ├── procedimientos_seguros.sql
│   │   └── generar_datos_seguro.py
│   └── datos/                   # Datos generados
│
├── 02_ETL/                      # Proceso ETL
│   ├── config/                  # Configuraciones
│   │   └── config_conexion.py
│   └── scripts/                 # Scripts ETL
│       ├── etl_principal.py
│       ├── etl_principal_seguro.py
│       ├── etl_utils.py
│       └── procedimientos_etl.sql
│
├── 03_Dashboard/               # Dashboard Web
│   ├── backend/                # API Flask
│   │   ├── app.py
│   │   └── requirements.txt
│   └── frontend/               # Interfaz HTML/CSS/JS
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── 04_Datawarehouse/           # Data Warehouse destino
│   └── scripts/                # Scripts SQL
│       ├── crear_datawarehouse.sql
│       ├── procedimientos_seguros_dw.sql
│       └── consultas_analisis.sql
│
└── docs/                       # Documentación completa
    ├── guias/                  # Guías de usuario
    ├── configuracion/          # Documentación técnica
    ├── analisis/               # Análisis y mejoras
    ├── seguridad/              # Documentación de seguridad
    └── resumen/                # Resúmenes ejecutivos
```

---

## 🚀 Inicio Rápido

### Pre-requisitos

- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes Python)

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd ProyectoETL

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
./setup_local.sh

# 4. Iniciar el dashboard
./iniciar_dashboard.sh
```

### Acceso al Dashboard

Después de iniciar, accede a:
- **Frontend**: http://localhost:8080/index.html
- **Backend API**: http://localhost:5001

---

## 📚 Documentación

### Guías Principales

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **Inicio Rápido** | Guía para empezar en 5 minutos | [docs/guias/INICIO_RAPIDO.md](docs/guias/INICIO_RAPIDO.md) |
| **Guía Local** | Instalación y prueba local | [docs/guias/GUIA_PRUEBA_LOCAL.md](docs/guias/GUIA_PRUEBA_LOCAL.md) |
| **Guía Distribuida** | Despliegue en 3 máquinas | [docs/guias/GUIA_DESPLIEGUE_3_MAQUINAS.md](docs/guias/GUIA_DESPLIEGUE_3_MAQUINAS.md) |
| **Ejemplos de Uso** | Casos prácticos | [docs/guias/EJEMPLOS_USO.md](docs/guias/EJEMPLOS_USO.md) |
| **Guía de Datos** | Estructura de datos origen | [docs/guias/GUIA_DATOS_ORIGEN.md](docs/guias/GUIA_DATOS_ORIGEN.md) |

### Documentación Técnica

| Categoría | Documentos | Ubicación |
|-----------|-----------|-----------|
| **Configuración** | README completo, configuración avanzada | [docs/configuracion/](docs/configuracion/) |
| **Análisis** | Consistencia BD, correcciones, filtros | [docs/analisis/](docs/analisis/) |
| **Resumen** | Resumen de archivos e implementación | [docs/resumen/](docs/resumen/) |

### Documentación por Componente

- **01_GestionProyectos**: [01_GestionProyectos/README.md](01_GestionProyectos/README.md)
- **02_ETL**: [02_ETL/README.md](02_ETL/README.md)
- **03_Dashboard**: [03_Dashboard/README.md](03_Dashboard/README.md)
- **04_Datawarehouse**: [04_Datawarehouse/README.md](04_Datawarehouse/README.md)

---

## 🔐 Seguridad

El sistema implementa múltiples capas de seguridad:

1. **Stored Procedures**: Todo el acceso a datos es mediante procedures
2. **Triggers de Auditoría**: Registro automático de todas las operaciones
3. **Validación de Datos**: Validaciones antes de insertar/actualizar
4. **Control de Acceso**: Permisos granulares por tabla y operación
5. **Trazabilidad**: Logs completos de todas las transacciones

### Scripts de Seguridad

- `01_GestionProyectos/scripts/procedimientos_seguros.sql` - Procedures BD origen
- `02_ETL/scripts/procedimientos_etl.sql` - Procedures para ETL
- `04_Datawarehouse/scripts/procedimientos_seguros_dw.sql` - Procedures DW
- `verificar_trazabilidad_seguro.py` - Verificación de auditoría

---

## 📊 Funcionalidades del Dashboard

### Visualizaciones Disponibles

- 📈 **Estadísticas Generales**: Total de proyectos, empleados, tareas
- 📊 **Gráficos Interactivos**: 
  - Distribución de proyectos por estado
  - Asignación de empleados por departamento
  - Evolución temporal de proyectos
- 🔄 **Operaciones ETL**: Ejecución y monitoreo en tiempo real
- 🗄️ **Gestión de Datos**: Generación y limpieza de datos de prueba

### Operaciones Disponibles

- ✅ Visualizar datos de origen y Data Warehouse
- ✅ Ejecutar proceso ETL manualmente
- ✅ Generar datos de prueba
- ✅ Limpiar bases de datos
- ✅ Monitorear estado del sistema

---

## 🛠️ Scripts de Utilidad

### Scripts de Instalación

| Script | Descripción | Uso |
|--------|-------------|-----|
| `setup_local.sh` | Configuración completa local | `./setup_local.sh` |
| `setup_proyecto.py` | Instalación automatizada Python | `python setup_proyecto.py` |
| `instalar_sistema_seguro.sh` | Instalación con seguridad | `./instalar_sistema_seguro.sh` |

### Scripts de Operación

| Script | Descripción | Uso |
|--------|-------------|-----|
| `iniciar_dashboard.sh` | Iniciar backend y frontend | `./iniciar_dashboard.sh` |
| `detener_dashboard.sh` | Detener todos los servicios | `./detener_dashboard.sh` |
| `verificar_sistema.sh` | Verificar estado del sistema | `./verificar_sistema.sh` |
| `configurar_distribuido.sh` | Configurar ambiente distribuido | `./configurar_distribuido.sh` |

### Scripts de Validación

| Script | Descripción | Uso |
|--------|-------------|-----|
| `validar_consistencia.py` | Validar consistencia de datos | `python validar_consistencia.py` |
| `verificar_distribuido.py` | Verificar configuración distribuida | `python verificar_distribuido.py` |
| `verificar_trazabilidad_seguro.py` | Verificar auditoría | `python verificar_trazabilidad_seguro.py` |

---

## 📋 Flujo de Trabajo Típico

### 1. Instalación Inicial

```bash
# Instalar sistema completo
./setup_local.sh

# O usar el instalador Python
python setup_proyecto.py
```

### 2. Generar Datos de Prueba

```bash
# Opción A: Usar script directo
cd 01_GestionProyectos/scripts
python generar_datos_seguro.py

# Opción B: Desde el dashboard
# Acceder a http://localhost:8080 y usar "Generar Datos"
```

### 3. Ejecutar ETL

```bash
# Opción A: Script directo
cd 02_ETL/scripts
python etl_principal_seguro.py

# Opción B: Desde el dashboard
# Usar el botón "Ejecutar ETL"
```

### 4. Analizar Resultados

```bash
# Ver dashboard
http://localhost:8080/index.html

# O ejecutar consultas SQL directamente
mysql -u root -p < 04_Datawarehouse/scripts/consultas_analisis.sql
```

### 5. Verificar Trazabilidad

```bash
# Verificar auditoría
python verificar_trazabilidad_seguro.py
```

---

## 🔧 Configuración

### Configuración de Base de Datos

Editar: `02_ETL/config/config_conexion.py`

```python
ORIGEN_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_password',
    'database': 'gestionproyectos_hist'
}

DESTINO_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_password',
    'database': 'dw_proyectos_hist'
}
```

### Configuración del Dashboard

Editar: `03_Dashboard/frontend/app.js`

```javascript
const API_BASE_URL = 'http://localhost:5001';
```

---

## 📝 Mantenimiento

### Limpieza de Datos

```bash
# Desde el dashboard: Usar botón "Limpiar Datos"

# O desde terminal
mysql -u root -p gestionproyectos_hist -e "
CALL LimpiarProyectos();
CALL LimpiarEmpleados();
CALL LimpiarClientes();
"
```

### Actualización de Dependencias

```bash
pip install -r requirements.txt --upgrade
```

### Backup de Base de Datos

```bash
# Backup BD Origen
mysqldump -u root -p gestionproyectos_hist > backup_origen.sql

# Backup Data Warehouse
mysqldump -u root -p dw_proyectos_hist > backup_dw.sql
```

---

## 🐛 Solución de Problemas

### El Dashboard no Inicia

```bash
# Verificar que los puertos estén libres
lsof -i :5001  # Backend
lsof -i :8080  # Frontend

# Si están ocupados, matar procesos
lsof -ti:5001 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Reiniciar dashboard
./iniciar_dashboard.sh
```

### Error de Conexión a MySQL

```bash
# Verificar que MySQL esté corriendo
mysql -u root -p

# Verificar configuración
cat 02_ETL/config/config_conexion.py
```

### ETL Falla

```bash
# Verificar logs
tail -f /tmp/backend_flask.log

# Verificar datos de origen
python validar_consistencia.py
```

---

## 📈 Métricas del Sistema

### Base de Datos Origen

- Proyectos históricos con múltiples versiones
- Empleados con roles y departamentos
- Clientes con información de contacto
- Tareas con asignaciones y estados

### Data Warehouse

- Dimensiones: Proyectos, Empleados, Clientes, Tiempo
- Hechos: Proyectos, Tareas
- Agregaciones y métricas calculadas

### Dashboard

- Visualizaciones en tiempo real
- Gráficos interactivos con Chart.js
- API RESTful con Flask
- Frontend responsivo con Bootstrap

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📞 Soporte

Para reportar problemas o solicitar ayuda:

1. Revisar la documentación en [docs/](docs/)
2. Consultar ejemplos en [docs/guias/EJEMPLOS_USO.md](docs/guias/EJEMPLOS_USO.md)
3. Verificar logs del sistema
4. Contactar al equipo de desarrollo

---

## 🎓 Recursos Adicionales

### Tutoriales

- [Guía de Inicio Rápido](docs/guias/INICIO_RAPIDO.md) - 5 minutos
- [Guía de Prueba Local](docs/guias/GUIA_PRUEBA_LOCAL.md) - 15 minutos
- [Guía de Despliegue Distribuido](docs/guias/GUIA_DESPLIEGUE_3_MAQUINAS.md) - 30 minutos

### Referencias

- [Resumen de Implementación](docs/resumen/RESUMEN_IMPLEMENTACION.md)
- [Análisis de Consistencia](docs/analisis/ANALISIS_CONSISTENCIA_BD.md)
- [Filtros ETL](docs/analisis/FILTROS_ETL_DATAWAREHOUSE.md)

---

## ✨ Últimas Actualizaciones

- ✅ Sistema de seguridad con stored procedures
- ✅ Dashboard web completo
- ✅ Documentación reorganizada
- ✅ Scripts de instalación automatizados
- ✅ Sistema de trazabilidad completo

---

## 📄 Licencia

Este proyecto es parte de un sistema académico/empresarial de gestión de proyectos.

---

**¡Gracias por usar nuestro Sistema ETL de Gestión de Proyectos!** 🚀

**[📖 Ver Guía de Inicio Rápido Completa →](INICIO_RAPIDO.md)**

---

## � Instalación por Módulos

### Opción 1: Instalación de Todos los Módulos (Local)

```bash
# Módulo 1: Base de Datos
cd 01_GestionProyectos
./setup_bd_origen.sh

# Módulo 3: Data Warehouse (requiere Módulo 1)
cd ../04_Datawarehouse
./setup_dw.sh
python etl/etl_principal.py  # Cargar datos

# Módulo 2: Dashboard (requiere Módulos 1 y 3)
cd ../03_Dashboard
./setup_dashboard.sh
./iniciar_dashboard.sh
```

Acceder al dashboard: **http://localhost:8080/index.html**

### Opción 2: Instalación Individual

#### Solo Módulo 1 (BD Origen):
```bash
cd 01_GestionProyectos
./setup_bd_origen.sh
```
Ver: **[01_GestionProyectos/INSTALACION.md](01_GestionProyectos/INSTALACION.md)**

#### Solo Módulo 2 (Dashboard):
```bash
cd 03_Dashboard
./setup_dashboard.sh
# Configurar .env con IPs de Módulos 1 y 3
./iniciar_dashboard.sh
```
Ver: **[03_Dashboard/INSTALACION.md](03_Dashboard/INSTALACION.md)**

#### Solo Módulo 3 (Data Warehouse):
```bash
cd 04_Datawarehouse
./setup_dw.sh
# Configurar .env con IP de Módulo 1
python etl/etl_principal.py
```
Ver: **[04_Datawarehouse/INSTALACION.md](04_Datawarehouse/INSTALACION.md)**

### Opción 3: Empaquetar para Envío

```bash
# Crear ZIPs de cada módulo
./empaquetar_modulos.sh

# Se crean en: modulos_empaquetados/
# - Modulo1_BD_Origen.zip
# - Modulo2_Dashboard.zip
# - Modulo3_DataWarehouse.zip
```

---

## �📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** | ⚡ Guía rápida de 5 minutos |
| **[README_COMPLETO.md](README_COMPLETO.md)** | 📖 Documentación completa del proyecto |
| **[GUIA_PRUEBA_LOCAL.md](GUIA_PRUEBA_LOCAL.md)** | 🔧 Guía detallada de configuración |
| **[GUIA_DESPLIEGUE_3_MAQUINAS.md](GUIA_DESPLIEGUE_3_MAQUINAS.md)** | 🌐 Configuración distribuida |

---

## 🎯 ¿Qué es este proyecto?

Un sistema ETL completo que incluye:

- **📊 Base de Datos Origen** - Sistema transaccional (OLTP)
- **⚙️ Proceso ETL** - Extracción, transformación y carga automatizada
- **🏢 Data Warehouse** - Modelo dimensional para análisis
- **📈 Dashboard Web** - Interfaz interactiva para visualización y control

---

## 🔧 Requisitos

- Python 3.8+
- MySQL 5.7+ o MariaDB 10.3+
- Navegador web moderno

---

## 📁 Estructura del Proyecto

```
ProyectoETL/
├── 01_GestionProyectos/    # BD Origen
├── 02_ETL/                  # Proceso ETL
├── 03_Dashboard/            # Dashboard Web
├── 04_Datawarehouse/        # Data Warehouse
├── setup_local.sh           # Configuración automática ⚡
├── iniciar_dashboard.sh     # Iniciar sistema
├── detener_dashboard.sh     # Detener sistema
└── verificar_sistema.sh     # Verificar estado
```

---

## 🎓 Características

✅ ETL automatizado con Python  
✅ Modelo dimensional (esquema estrella)  
✅ Cálculo de KPIs y métricas  
✅ Dashboard web interactivo  
✅ API REST con Flask  
✅ Generación de datos de prueba  
✅ Scripts de automatización  
✅ Documentación completa  

---

## 📊 Vista Previa del Dashboard

El dashboard permite:

- 🔍 Monitorear conexiones en tiempo real
- 📊 Ver datos de origen y datawarehouse
- ⚙️ Ejecutar el proceso ETL con un click
- 📈 Visualizar métricas y KPIs
- 🗑️ Gestionar datos de prueba

---

## 🚀 Empezar Ahora

### Opción 1: Configuración Automática (Recomendado)

```bash
./setup_local.sh
./iniciar_dashboard.sh
```

Abre tu navegador en `http://localhost:8080`

### Opción 2: Verificar Primero

```bash
./verificar_sistema.sh  # Ver estado del sistema
./setup_local.sh        # Si es necesario
./iniciar_dashboard.sh  # Iniciar
```

---

## 📖 Aprende Más

- [Inicio Rápido](INICIO_RAPIDO.md) - Comienza en 5 minutos
- [Documentación Completa](README_COMPLETO.md) - Toda la información
- [Guía de Prueba Local](GUIA_PRUEBA_LOCAL.md) - Instrucciones detalladas

---

## 🐛 Solución de Problemas

```bash
# Verificar estado del sistema
./verificar_sistema.sh

# Reinstalar si hay problemas
./detener_dashboard.sh
rm -rf venv
./setup_local.sh
```

---

## 📄 Licencia

Proyecto educativo para demostración de conceptos ETL y Data Warehouse.

---

## 🤝 Contribuciones

Este es un proyecto educativo. Siéntete libre de usarlo para aprender.

---

**⭐ Si te resulta útil, dale una estrella al repositorio!** Distribuido - Sistema de 3 Máquinas

Este proyecto implementa un sistema ETL (Extract, Transform, Load) distribuido que opera en 3 máquinas independientes para procesar datos de gestión de proyectos.

## 🏗️ Arquitectura del Sistema

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
      📊 Datos              ⚙️ Transformar           🏗️ Datawarehouse
```

## 📁 Estructura del Proyecto

```
ProyectoETL/
├── README.md                           # Este archivo
├── README_CONFIGURACION.md             # Guía detallada de configuración
├── requirements.txt                    # Dependencias Python
│
├── GestionProyectos/                   # 📊 MÁQUINA 1
│   ├── config_conexion.py             # Configuración de conexiones
│   └── setup_servidor_bd.py           # Configurador automático BD origen
│
├── ETL/                               # ⚙️ MÁQUINA 2
│   ├── etl_distribuido.py             # ETL principal para 3 máquinas
│   ├── etl_principal.py               # ETL original (mejorado)
│   ├── etl_remoto_portable.py         # ETL portable simplificado
│   ├── servidor_etl_simple.py         # Servidor HTTP para ETL
│   ├── setup_etl.py                   # Configurador automático ETL
│   ├── setup_local.py                 # 🧪 Setup para pruebas locales
│   ├── api_backend.py                 # 🌐 API Flask para dashboard
│   └── web-dashboard/                 # 📊 Dashboard Web
│       ├── index.html                 # Interface principal
│       └── dashboard.js               # Lógica del dashboard
│
└── Datawarehouse/                     # 🏗️ MÁQUINA 3
    ├── generacion_datos.py            # Generador de datos de prueba
    ├── script_creacion_db.sql         # Script creación BD origen
    ├── script_datawarehouse.sql       # Script creación datawarehouse
    └── setup_datawarehouse.py         # Configurador automático DW
```

## 🚀 Configuración Rápida

### 🧪 Opción 1: Prueba Local (Recomendada para desarrollo)

**Una sola máquina - Todo local:**
```bash
cd ETL
python3 setup_local.py
```
Este comando:
- ✅ Instala dependencias automáticamente
- ✅ Configura bases de datos locales
- ✅ Genera datos de prueba
- ✅ Ejecuta ETL de prueba
- ✅ Inicia dashboard web en http://localhost:5000
- ✅ Abre interfaz visual en navegador

### 🏗️ Opción 2: Configuración Distribuida (3 máquinas)

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

### 📖 Opción 3: Configuración Manual

Ver [README_CONFIGURACION.md](README_CONFIGURACION.md) para pasos detallados.

## ⚡ Ejecución del ETL

### 🧪 Modo Local (Desarrollo):
```bash
cd ETL
python3 setup_local.py    # Setup completo con dashboard
# O componentes individuales:
python3 api_backend.py    # Solo API backend
python3 etl_principal.py  # Solo ETL
```

### 🏗️ Modo Distribuido (Producción):
```bash
# Desde la Máquina ETL (Máquina 2):
python3 etl_distribuido.py    # ETL distribuido
python3 etl_remoto_portable.py # ETL portable alternativo
```

### 🌐 Dashboard Web:
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

## 🔧 Configuración de Red

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

## 📊 Bases de Datos

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

## 🔍 Verificación del Sistema

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

## 📋 Requisitos

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

## 🛠️ Solución de Problemas

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

## 🎯 Características del Dashboard Web

### 📊 Interface Visual Completa:
- **Dashboard Principal:** Métricas en tiempo real y gráficos
- **Datos Origen:** Visualización de tablas de la BD transaccional
- **Control ETL:** Ejecución visual del ETL con logs en tiempo real
- **DataWarehouse:** Exploración de dimensiones y hechos
- **Análisis:** Reportes y gráficos de cumplimiento

### 🎮 Controles Interactivos:
- ✅ **Generar Datos:** Botón para crear datos de prueba
- ✅ **Ejecutar ETL:** Control visual con barra de progreso
- ✅ **Visualizar Resultados:** Tablas dinámicas y gráficos
- ✅ **Monitoreo:** Estado de conexiones en tiempo real
- ✅ **Logs ETL:** Console log de la ejecución ETL

### 📱 Responsive Design:
- Interface adaptable a desktop y móvil
- Navegación por tabs y secciones
- Gráficos interactivos con Chart.js
- Bootstrap 5 para styling moderno

## 🔒 Seguridad

- Cambiar passwords por defecto en producción
- Usar VPN para conexiones entre máquinas
- Configurar firewall restrictivo
- Monitorear conexiones MySQL
- Realizar backups regulares

## 📚 Documentación Adicional

- [README_CONFIGURACION.md](README_CONFIGURACION.md) - Guía detallada de configuración
- Comentarios en código fuente para lógica específica
- Scripts de configuración automática incluidos

---

**Versión:** 1.0  
**Autor:** Sistema ETL Distribuido  
**Fecha:** Octubre 2025

## 📋 Descripción

Este proyecto implementa un sistema ETL completo que:
- Extrae datos de una base de datos transaccional de gestión de proyectos
- Transforma y limpia los datos 
- Carga los datos en un Data Warehouse optimizado para análisis

## 🏗️ Arquitectura

### Bases de Datos
- **gestionproyectos_hist**: Base de datos transaccional (fuente)
- **dw_proyectos_hist**: Data Warehouse (destino)

### Componentes
- **ETL Principal**: Proceso completo de extracción, transformación y carga
- **ETL Remoto Portable**: Versión independiente para ejecución remota
- **Servidor ETL**: API HTTP para ejecución remota del ETL
- **Generación de Datos**: Script para poblar la base de datos de prueba

## 📁 Estructura del Proyecto

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

## 🚀 Instalación y Configuración

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

## 📊 Uso

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

## 📈 Data Warehouse - Esquema Dimensional

### Tablas de Dimensiones
- **DimCliente**: Información de clientes
- **DimEmpleado**: Datos de empleados  
- **DimEquipo**: Información de equipos
- **DimProyecto**: Detalles de proyectos
- **DimTiempo**: Dimensión temporal

### Tabla de Hechos
- **FactTareas**: Métricas y KPIs de tareas

## 🔧 Configuración Avanzada

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

## 📋 Funcionalidades

### ETL Principal
- ✅ Extracción de datos transaccionales
- ✅ Transformación y limpieza de datos
- ✅ Carga incremental en Data Warehouse
- ✅ Manejo de dimensiones SCD (Slowly Changing Dimensions)
- ✅ Logging y monitoreo

### ETL Remoto
- ✅ Ejecución independiente
- ✅ Auto-instalación de dependencias
- ✅ Configuración flexible
- ✅ Manejo de errores robusto

### Servidor ETL
- ✅ API REST para ejecución remota
- ✅ Interface web simple
- ✅ Logs de ejecución
- ✅ Estado de procesos

## 🛠️ Tecnologías Utilizadas

- **Python**: Lenguaje principal
- **Pandas**: Manipulación de datos
- **SQLAlchemy**: ORM y conexiones de base de datos
- **MySQL**: Sistema de gestión de base de datos
- **HTTP Server**: Para API remota

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver archivo LICENSE para detalles.

## 👥 Contribución

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o preguntas, crear un issue en el repositorio.
