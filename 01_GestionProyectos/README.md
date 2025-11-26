#  Base de Datos Origen - Gestión de Proyectos

##  Descripción

Esta carpeta contiene la **base de datos transaccional (OLTP)** que sirve como origen de datos para el sistema ETL. Almacena información operativa de gestión de proyectos con **seguridad implementada mediante Stored Procedures y Triggers**.

**Base de Datos:** `gestionproyectos_hist`

---

##  Estructura de Archivos

```
01_GestionProyectos/
├── README.md                         # Este archivo
├── scripts/
│   ├── crear_bd_origen.sql          # Creación de BD y tablas
│   ├── procedimientos_seguros.sql   # Stored procedures con seguridad
│   ├── generar_datos.py             # Generador de datos (versión básica)
│   └── generar_datos_seguro.py      # Generador con stored procedures
└── datos/
    └── (Datos generados automáticamente)
```

---

##  Esquema de Base de Datos

### Tablas Principales

| Tabla | Descripción | Registros Típicos |
|-------|-------------|-------------------|
| **Cliente** | Información de clientes | ~100-500 |
| **Empleado** | Datos de empleados y roles | ~50-200 |
| **Equipo** | Equipos de trabajo | ~10-50 |
| **Estado** | Estados de proyectos/tareas | ~10 (catálogo) |
| **Proyecto** | Información de proyectos | ~100-1000 |
| **Tarea** | Tareas de proyectos | ~500-5000 |
| **MiembroEquipo** | Relación empleado-equipo | ~100-500 |
| **TareaEquipoHist** | Historial de asignaciones | ~500-5000 |

### Tablas de Auditoría (con Seguridad)

| Tabla | Descripción |
|-------|-------------|
| **AuditoriaProyectos** | Log de cambios en proyectos |
| **AuditoriaEmpleados** | Log de cambios en empleados |
| **AuditoriaClientes** | Log de cambios en clientes |

---

##  Seguridad Implementada

### Stored Procedures

Todos los accesos a datos se realizan mediante procedures:

#### Lectura (SELECT)
- `ObtenerProyectos()` - Listar todos los proyectos
- `ObtenerProyectoPorID(IN p_id INT)` - Proyecto específico
- `ObtenerEmpleados()` - Listar empleados
- `ObtenerClientes()` - Listar clientes
- `ObtenerTareas()` - Listar tareas

#### Escritura (INSERT)
- `InsertarProyecto(...)` - Crear nuevo proyecto
- `InsertarEmpleado(...)` - Crear empleado
- `InsertarCliente(...)` - Crear cliente
- `InsertarTarea(...)` - Crear tarea

#### Modificación (UPDATE)
- `ActualizarProyecto(...)` - Actualizar proyecto
- `ActualizarEmpleado(...)` - Actualizar empleado
- `ActualizarCliente(...)` - Actualizar cliente

#### Eliminación (DELETE)
- `EliminarProyecto(IN p_id INT)` - Borrar proyecto
- `EliminarEmpleado(IN p_id INT)` - Borrar empleado
- `LimpiarProyectos()` - Limpiar tabla proyectos

### Triggers de Auditoría

Registro automático de todas las operaciones:

- **AFTER INSERT**: Registra inserciones
- **AFTER UPDATE**: Registra modificaciones
- **AFTER DELETE**: Registra eliminaciones

**Ejemplo de Trigger:**
```sql
CREATE TRIGGER audit_proyecto_insert
AFTER INSERT ON Proyecto
FOR EACH ROW
INSERT INTO AuditoriaProyectos (...)
```

---

##  Instalación y Configuración

### Opción 1: Instalación Básica

```bash
# 1. Crear la base de datos y tablas
mysql -u root -p < scripts/crear_bd_origen.sql

# 2. Generar datos de prueba
cd scripts
python generar_datos.py
```

### Opción 2: Instalación con Seguridad (Recomendado)

```bash
# 1. Crear la base de datos
mysql -u root -p < scripts/crear_bd_origen.sql

# 2. Instalar stored procedures y triggers
mysql -u root -p < scripts/procedimientos_seguros.sql

# 3. Generar datos usando procedures
cd scripts
python generar_datos_seguro.py
```

### Opción 3: Instalación Automatizada

```bash
# Desde la raíz del proyecto
./setup_local.sh
```

---

##  Generación de Datos

### Script Básico: `generar_datos.py`

Genera datos usando SQL directo:

```bash
cd scripts
python generar_datos.py
```

**Genera:**
- 100 clientes
- 50 empleados
- 10 equipos
- 100 proyectos
- 500 tareas

### Script Seguro: `generar_datos_seguro.py`

Genera datos usando **solo stored procedures**:

```bash
cd scripts
python generar_datos_seguro.py
```

**Ventajas:**
-  Mayor seguridad
-  Auditoría automática
-  Validaciones integradas
-  Trazabilidad completa

---

##  Consultas de Ejemplo

### Consulta Directa (NO RECOMENDADA en producción)

```sql
SELECT * FROM Proyecto WHERE IdEstado = 3;
```

### Consulta Segura (RECOMENDADA)

```sql
CALL ObtenerProyectos();
CALL ObtenerProyectoPorID(1);
```

### Verificar Auditoría

```sql
-- Ver cambios en proyectos
SELECT * FROM AuditoriaProyectos 
ORDER BY FechaHora DESC 
LIMIT 10;

-- Ver cambios por tipo de operación
SELECT Operacion, COUNT(*) as Total
FROM AuditoriaProyectos
GROUP BY Operacion;
```

---

##  Mantenimiento

### Limpiar Datos

```sql
-- Usando procedures seguros
CALL LimpiarProyectos();
CALL LimpiarEmpleados();
CALL LimpiarClientes();

-- O limpiar todo
TRUNCATE TABLE Proyecto;
TRUNCATE TABLE Empleado;
TRUNCATE TABLE Cliente;
```

### Backup

```bash
# Backup completo
mysqldump -u root -p gestionproyectos_hist > backup_origen.sql

# Backup solo estructura
mysqldump -u root -p --no-data gestionproyectos_hist > estructura.sql

# Backup solo datos
mysqldump -u root -p --no-create-info gestionproyectos_hist > datos.sql
```

### Restaurar

```bash
mysql -u root -p gestionproyectos_hist < backup_origen.sql
```

---

##  Métricas y Estadísticas

### Consultas de Análisis

```sql
-- Total de proyectos por estado
SELECT e.Nombre as Estado, COUNT(*) as Total
FROM Proyecto p
JOIN Estado e ON p.IdEstado = e.Id
GROUP BY e.Nombre;

-- Proyectos cerrados (listos para ETL)
SELECT COUNT(*) FROM Proyecto WHERE IdEstado = 3;

-- Tareas por proyecto
SELECT p.Nombre, COUNT(t.Id) as TotalTareas
FROM Proyecto p
LEFT JOIN Tarea t ON p.Id = t.IdProyecto
GROUP BY p.Id, p.Nombre;

-- Empleados por equipo
SELECT eq.Nombre, COUNT(me.IdEmpleado) as TotalEmpleados
FROM Equipo eq
LEFT JOIN MiembroEquipo me ON eq.Id = me.IdEquipo
GROUP BY eq.Id, eq.Nombre;
```

---

##  Relación con Otros Componentes

### Consumidores de Datos

- **02_ETL**: Lee datos de proyectos cerrados
- **03_Dashboard**: Muestra estadísticas en tiempo real
- **04_Datawarehouse**: Destino final de los datos transformados

### Scripts que Acceden a esta BD

- `02_ETL/scripts/etl_principal_seguro.py`
- `03_Dashboard/backend/app.py`
- `verificar_trazabilidad_seguro.py`

---

##  Solución de Problemas

### Error: Base de datos no existe

```bash
# Verificar que la BD existe
mysql -u root -p -e "SHOW DATABASES LIKE 'gestionproyectos_hist';"

# Si no existe, crearla
mysql -u root -p < scripts/crear_bd_origen.sql
```

### Error: Procedures no existen

```bash
# Instalar procedures
mysql -u root -p < scripts/procedimientos_seguros.sql

# Verificar procedures instalados
mysql -u root -p -e "SHOW PROCEDURE STATUS WHERE Db = 'gestionproyectos_hist';"
```

### No hay datos para ETL

```sql
-- Verificar proyectos cerrados
SELECT COUNT(*) FROM Proyecto WHERE IdEstado = 3;

-- Si es 0, generar más datos
CALL InsertarProyecto(...);
```

---

##  Documentación Relacionada

- **Guía de Datos Origen**: [/docs/guias/GUIA_DATOS_ORIGEN.md](../docs/guias/GUIA_DATOS_ORIGEN.md)
- **Análisis de Consistencia**: [/docs/analisis/ANALISIS_CONSISTENCIA_BD.md](../docs/analisis/ANALISIS_CONSISTENCIA_BD.md)
- **Correcciones Realizadas**: [/docs/analisis/CORRECCIONES_REALIZADAS.md](../docs/analisis/CORRECCIONES_REALIZADAS.md)

---

##  Características Destacadas

-  **Seguridad por Diseño**: Stored procedures para todo acceso
-  **Auditoría Completa**: Triggers automáticos de auditoría
-  **Datos Realistas**: Generador con Faker para datos de prueba
-  **Validaciones**: Validaciones en procedures
-  **Trazabilidad**: Log completo de todas las operaciones

---

**Volver al README Principal**: [../README.md](../README.md)  
**Ver Documentación Completa**: [../docs/README.md](../docs/README.md)
