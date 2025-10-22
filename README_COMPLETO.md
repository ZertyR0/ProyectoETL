# 🎯 Proyecto ETL - Sistema de Gestión de Proyectos

## 📋 Descripción

Sistema completo de ETL (Extract, Transform, Load) para análisis de gestión de proyectos con:
- **Base de datos origen** con datos transaccionales
- **Proceso ETL** automatizado para transformación de datos
- **Data Warehouse** optimizado para análisis
- **Dashboard web** interactivo para visualización

---

## 🚀 Inicio Rápido

### Opción 1: Configuración Automática (Recomendado)

```bash
# 1. Configurar todo el ambiente (solo la primera vez)
./setup_local.sh

# 2. Iniciar el dashboard
./iniciar_dashboard.sh

# 3. Abrir en el navegador
# http://localhost:8080

# 4. Cuando termines, detener el dashboard
./detener_dashboard.sh
```

### Opción 2: Configuración Manual

Ver archivo `GUIA_PRUEBA_LOCAL.md` para instrucciones detalladas.

---

## 📁 Estructura del Proyecto

```
ProyectoETL/
│
├── 01_GestionProyectos/         # 📊 Base de Datos Origen
│   ├── datos/                    # Datos generados
│   └── scripts/
│       ├── crear_bd_origen.sql   # Schema de la BD origen
│       └── generar_datos.py      # Generador de datos de prueba
│
├── 02_ETL/                       # ⚙️ Proceso ETL
│   ├── config/
│   │   └── config_conexion.py    # Configuración de conexiones
│   └── scripts/
│       ├── etl_principal.py      # ETL principal
│       └── etl_utils.py          # Utilidades de ETL
│
├── 03_Dashboard/                 # 📈 Dashboard Web
│   ├── backend/
│   │   ├── app.py                # API Flask
│   │   └── requirements.txt      # Dependencias backend
│   └── frontend/
│       ├── index.html            # Interfaz de usuario
│       ├── app.js                # Lógica del dashboard
│       └── styles.css            # Estilos
│
├── 04_Datawarehouse/             # 🏢 Data Warehouse
│   └── scripts/
│       ├── crear_datawarehouse.sql    # Schema del DW
│       └── consultas_analisis.sql     # Consultas de ejemplo
│
├── setup_local.sh                # 🔧 Configuración automática
├── iniciar_dashboard.sh          # ▶️ Iniciar dashboard
├── detener_dashboard.sh          # ⏹️ Detener dashboard
├── GUIA_PRUEBA_LOCAL.md         # 📖 Guía detallada
└── requirements.txt              # Dependencias Python
```

---

## 🔧 Requisitos Previos

### Software Necesario

- **Python 3.8+**
- **MySQL 5.7+** o **MariaDB 10.3+**
- **pip** (gestor de paquetes Python)

### Instalación de MySQL (macOS)

```bash
# Usando Homebrew
brew install mysql

# Iniciar MySQL
brew services start mysql
```

### Verificación

```bash
# Python
python3 --version

# MySQL
mysql --version
mysql -u root -e "SELECT 1"
```

---

## 📊 Base de Datos

### BD Origen: `gestionproyectos_hist`

Simula un sistema OLTP con las siguientes tablas:

| Tabla | Descripción | Registros (ejemplo) |
|-------|-------------|---------------------|
| **Cliente** | Información de clientes | ~10 |
| **Empleado** | Empleados y recursos | ~15 |
| **Equipo** | Equipos de trabajo | ~5 |
| **Estado** | Estados de proyectos/tareas | 6 |
| **Proyecto** | Proyectos principales | ~15 |
| **Tarea** | Tareas de proyectos | ~100 |
| **MiembroEquipo** | Asignaciones a equipos | ~30 |
| **TareaEquipoHist** | Historial tarea-equipo | ~70 |

### Data Warehouse: `dw_proyectos_hist`

Modelo dimensional tipo estrella:

**Dimensiones:**
- `DimCliente` - Clientes
- `DimEmpleado` - Empleados
- `DimProyecto` - Proyectos
- `DimEquipo` - Equipos
- `DimTiempo` - Dimensión temporal

**Tablas de Hechos:**
- `HechoProyecto` - Métricas de proyectos (KPIs principales)
- `HechoTarea` - Métricas de tareas (nivel detallado)

---

## ⚙️ Proceso ETL

### Características

✅ **Extracción** desde múltiples tablas relacionadas  
✅ **Transformación** con cálculo de métricas (KPIs)  
✅ **Carga** optimizada al data warehouse  
✅ **Validación** de datos en cada etapa  
✅ **Logging** detallado del proceso  
✅ **Manejo de errores** robusto  

### Métricas Calculadas

**Proyectos:**
- Duración planificada vs real
- Variación de cronograma
- Cumplimiento de tiempo y presupuesto
- Porcentaje de sobrecosto
- Eficiencia de horas
- Progreso y completitud

**Tareas:**
- Métricas de tiempo y costos
- Eficiencia por tarea
- Cumplimiento de plazos
- Variaciones de estimación

### Ejecución Manual

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar ETL completo
python3 02_ETL/scripts/etl_principal.py local

# Ver logs detallados
python3 02_ETL/scripts/etl_principal.py local 2>&1 | tee etl.log
```

---

## 📈 Dashboard Web

### Características

- **Monitoreo en tiempo real** de conexiones
- **Visualización** de datos origen y DW
- **Ejecución interactiva** del ETL
- **Gestión de datos** (insertar, limpiar)
- **Logs en tiempo real** del proceso
- **Métricas calculadas** automáticamente

### URLs

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Dashboard | http://localhost:8080 | Interfaz principal |
| API Backend | http://localhost:5001 | API REST |
| API Status | http://localhost:5001/status | Estado de conexiones |
| API Docs | http://localhost:5001/ | Documentación endpoints |

### Endpoints API

```
GET  /                   - Info de la API
GET  /status             - Estado de conexiones
GET  /datos-origen       - Datos de la BD origen
GET  /datos-datawarehouse - Datos del DW
POST /insertar-datos     - Generar datos de prueba
POST /ejecutar-etl       - Ejecutar proceso ETL
DELETE /limpiar-datos    - Limpiar todas las tablas
```

---

## 🔍 Ejemplos de Uso

### 1. Configurar y Probar el Sistema

```bash
# Configuración inicial
./setup_local.sh

# Verificar que todo funciona
mysql -u root gestionproyectos_hist -e "SELECT COUNT(*) FROM Proyecto"
mysql -u root dw_proyectos_hist -e "SELECT COUNT(*) FROM HechoProyecto"
```

### 2. Usar el Dashboard

```bash
# Iniciar dashboard
./iniciar_dashboard.sh

# En el navegador (http://localhost:8080):
# 1. Click en "Insertar Datos" para generar datos
# 2. Click en "Ejecutar ETL" para procesar
# 3. Ver métricas y resultados

# Detener cuando termines
./detener_dashboard.sh
```

### 3. Consultas de Análisis

```sql
-- Conectar al datawarehouse
USE dw_proyectos_hist;

-- Proyectos con problemas de presupuesto
SELECT 
    dp.nombre_proyecto,
    hp.presupuesto,
    hp.costo_real,
    hp.variacion_costos,
    hp.porcentaje_sobrecosto
FROM HechoProyecto hp
JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
WHERE hp.cumplimiento_presupuesto = 0
ORDER BY hp.porcentaje_sobrecosto DESC;

-- Eficiencia promedio por mes
SELECT 
    dt.anio,
    dt.mes,
    dt.nombre_mes,
    AVG(hp.eficiencia_horas) as eficiencia_promedio,
    COUNT(*) as proyectos_finalizados
FROM HechoProyecto hp
JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
GROUP BY dt.anio, dt.mes, dt.nombre_mes
ORDER BY dt.anio, dt.mes;

-- Top empleados por proyectos gestionados
SELECT 
    de.nombre,
    de.puesto,
    COUNT(*) as proyectos_gestionados,
    AVG(hp.cumplimiento_tiempo) * 100 as pct_tiempo,
    AVG(hp.cumplimiento_presupuesto) * 100 as pct_presupuesto
FROM HechoProyecto hp
JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
GROUP BY de.id_empleado, de.nombre, de.puesto
ORDER BY proyectos_gestionados DESC;
```

---

## 🐛 Solución de Problemas

### Error: "MySQL no está corriendo"

```bash
# macOS
brew services start mysql

# Verificar
mysql -u root -e "SELECT 1"
```

### Error: "Puerto 5001 o 8080 ocupado"

```bash
# Ver qué está usando el puerto
lsof -i :5001
lsof -i :8080

# Matar el proceso
kill -9 <PID>
```

### Error: "No se puede conectar a MySQL"

Editar credenciales en `02_ETL/config/config_conexion.py`:

```python
CONFIG_LOCAL = {
    'user_origen': 'tu_usuario',
    'password_origen': 'tu_password',
    # ...
}
```

### Reinstalar todo

```bash
./detener_dashboard.sh
rm -rf venv
rm .dashboard.pid
./setup_local.sh
```

---

## 📚 Documentación Adicional

- `GUIA_PRUEBA_LOCAL.md` - Guía detallada de prueba local
- `GUIA_DESPLIEGUE_3_MAQUINAS.md` - Configuración distribuida
- `README_CONFIGURACION.md` - Configuración avanzada
- `README_PRINCIPAL.md` - Documentación del proyecto

---

## 🎓 Conceptos Aprendidos

Este proyecto demuestra:

✅ Diseño de bases de datos relacionales (OLTP)  
✅ Modelado dimensional (Data Warehouse)  
✅ Procesos ETL con Python  
✅ Transformación y limpieza de datos  
✅ Cálculo de KPIs y métricas de negocio  
✅ APIs RESTful con Flask  
✅ Frontend interactivo con JavaScript  
✅ Integración full-stack  
✅ Automatización con scripts Bash  

---

## 📝 Notas Importantes

⚠️ **Ambiente Local**: Esta configuración es para desarrollo/pruebas  
⚠️ **Seguridad**: En producción, usar credenciales seguras  
⚠️ **Datos**: Los datos generados son ficticios para prueba  
⚠️ **Performance**: Optimizado para datasets pequeños/medianos  

---

## 🤝 Contribuciones

Proyecto educativo para demostración de conceptos ETL y Data Warehouse.

---

## 📄 Licencia

Proyecto educativo - Libre uso para aprendizaje

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa `GUIA_PRUEBA_LOCAL.md`
2. Verifica los logs en `03_Dashboard/backend/backend.log`
3. Asegúrate de que MySQL esté corriendo
4. Verifica que los puertos 5001 y 8080 estén libres

---

**Última actualización:** 22 de octubre de 2025
