# 🚀 ProyectoETL - Sistema de Gestión de Proyectos

Sistema completo de ETL (Extract, Transform, Load) con Data Warehouse y Dashboard Web interactivo.

## ⚡ Inicio Rápido

```bash
# 1. Configurar todo (solo la primera vez)
./setup_local.sh

# 2. Iniciar el dashboard
./iniciar_dashboard.sh

# 3. Abrir en el navegador: http://localhost:8080

# 4. Detener cuando termines
./detener_dashboard.sh
```

**[📖 Ver Guía de Inicio Rápido Completa →](INICIO_RAPIDO.md)**

---

## 📚 Documentación

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
