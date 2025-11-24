# 🏢 Datawarehouse - Análisis y Business Intelligence

Esta carpeta contiene todos los elementos del datawarehouse del sistema ETL.

## 📁 Estructura

```
04_Datawarehouse/
├── README.md                    # Este archivo
└── scripts/
    ├── crear_datawarehouse.sql # Script de creación del DW
    └── consultas_analisis.sql  # Consultas de análisis y reportes
```

## 🎯 Propósito

El datawarehouse **dw_proyectos_hist** almacena:

### 📊 Dimensiones
- **DimCliente**: Información de clientes
- **DimEmpleado**: Datos de empleados
- **DimEquipo**: Equipos de trabajo  
- **DimProyecto**: Información de proyectos
- **DimTiempo**: Dimensión temporal completa

### 📈 Hechos
- **HechoProyecto**: Métricas y KPIs de proyectos
- **HechoTarea**: Métricas y KPIs de tareas

## 🚀 Uso

1. **Crear el datawarehouse:**
   ```bash
   mysql -u root -p < scripts/crear_datawarehouse.sql
   ```

2. **Ejecutar consultas de análisis:**
   ```bash
   mysql -u root -p dw_proyectos_hist < scripts/consultas_analisis.sql
   ```

## 📋 Esquema Estrella

```
         DimTiempo
             |
DimCliente - HechoProyecto - DimEmpleado
             |
         DimProyecto
```

```
         DimTiempo
             |
DimEmpleado - HechoTarea - DimEquipo
             |
         DimProyecto
```

## 📊 Métricas Principales

### Proyectos
-  Cumplimiento de tiempo y presupuesto
-  Variaciones de cronograma y costos
-  Eficiencia de recursos
-  Satisfacción del cliente
-  Métricas de calidad

### Tareas
-  Eficiencia de horas
-  Cumplimiento de plazos
-  Productividad por empleado
-  Utilización de equipos

## 🔍 Consultas Comunes

- **Top proyectos por rentabilidad**
- **Empleados más productivos**
- **Tendencias temporales**
- **Análisis de cumplimiento**
- **Métricas de equipos**
- **Reportes ejecutivos**

## 📈 Business Intelligence

El datawarehouse soporta:
-  Reportes ejecutivos
-  Dashboards interactivos
-  Análisis de tendencias
-  KPIs y métricas clave
-  Alertas automáticas
-  Forecasting
