# 🔄 Sistema ETL (Extract, Transform, Load)

Esta carpeta contiene todos los componentes del proceso ETL que transforma los datos del sistema de gestión de proyectos al datawarehouse.

## 📁 Estructura

```
02_ETL/
├── README.md                 # Este archivo
├── scripts/
│   ├── etl_principal.py     # Script ETL principal
│   └── etl_utils.py         # Utilidades y funciones auxiliares
└── config/
    └── config_conexion.py   # Configuración de conexiones
```

## 🎯 Propósito

El proceso ETL realiza:

### 🔍 Extract (Extracción)
- Extrae datos de `gestionproyectos_hist` (origen)
- Maneja múltiples tablas relacionadas
- Aplica filtros y validaciones

### 🔄 Transform (Transformación)
- Limpia y normaliza datos
- Calcula métricas y KPIs
- Crea dimensiones de tiempo
- Aplica reglas de negocio

### 📊 Load (Carga)
- Carga datos al datawarehouse `dw_proyectos_hist`
- Maneja dimensiones y tablas de hechos
- Implementa estrategias SCD (Slowly Changing Dimensions)

## 🚀 Uso

1. **Configurar conexiones:**
   ```bash
   # Editar config/config_conexion.py con tus credenciales
   ```

2. **Ejecutar ETL:**
   ```bash
   python scripts/etl_principal.py
   ```

## 📋 Procesos ETL

### Dimensiones
- **DimCliente**: Datos de clientes
- **DimEmpleado**: Información de empleados
- **DimEquipo**: Equipos de trabajo
- **DimProyecto**: Datos de proyectos
- **DimTiempo**: Dimensión temporal

### Hechos
- **HechoProyecto**: Métricas de proyectos
- **HechoTarea**: Métricas de tareas

## 🔧 Configuración

El ETL soporta:
- ✅ Ejecución local
- ✅ Ejecución distribuida (3 máquinas)
- ✅ Logging detallado
- ✅ Manejo de errores
- ✅ Validación de datos
