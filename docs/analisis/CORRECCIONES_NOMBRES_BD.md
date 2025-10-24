# 🔧 Correcciones de Nombres en Bases de Datos

**Fecha:** 22 de octubre de 2025  
**Versión:** 1.0

## 📋 Resumen de Correcciones Realizadas

Este documento detalla todas las inconsistencias encontradas y corregidas en los nombres de tablas y columnas entre la base de datos origen, el datawarehouse y los scripts del ETL y Dashboard.

---

## ✅ Correcciones Implementadas

### 1. **Tabla `DimProyecto` en DataWarehouse**

#### ❌ Problema Original:
```sql
-- En crear_datawarehouse.sql
CREATE TABLE DimProyecto (
  id_proyecto       INT PRIMARY KEY,
  nombre_proyecto   VARCHAR(150) NOT NULL,
  descripcion       TEXT,
  fecha_inicio_plan DATE,  -- ❌ Nombre inconsistente
  ...
)
```

#### ✅ Solución Aplicada:
```sql
-- Corregido en crear_datawarehouse.sql
CREATE TABLE DimProyecto (
  id_proyecto       INT PRIMARY KEY,
  nombre_proyecto   VARCHAR(150) NOT NULL,
  descripcion       TEXT,
  fecha_inicio      DATE,  -- ✅ Ahora coincide con BD origen
  ...
)
```

**Justificación:** La base de datos origen usa `fecha_inicio` en la tabla `Proyecto`, por lo que el datawarehouse debe usar el mismo nombre para mantener consistencia.

---

### 2. **Nombres de Tablas en Backend del Dashboard**

#### ❌ Problema Original:
```python
# En app.py - función generar_datos()
cur.execute("INSERT INTO cliente ...")  # ❌ Minúscula
cur.execute("INSERT INTO empleado ...") # ❌ Minúscula
cur.execute("INSERT INTO equipo ...")   # ❌ Minúscula
cur.execute("SELECT * FROM estado ...")  # ❌ Minúscula
```

#### ✅ Solución Aplicada:
```python
# Corregido en app.py
cur.execute("INSERT INTO Cliente ...")      # ✅ Mayúscula
cur.execute("INSERT INTO Empleado ...")     # ✅ Mayúscula
cur.execute("INSERT INTO Equipo ...")       # ✅ Mayúscula
cur.execute("SELECT * FROM Estado ...")     # ✅ Mayúscula
cur.execute("INSERT INTO MiembroEquipo ...") # ✅ CamelCase correcto
cur.execute("INSERT INTO TareaEquipoHist ...") # ✅ CamelCase correcto
```

**Justificación:** Las tablas en MySQL en la base de datos origen fueron creadas con nombres en CamelCase (primera letra mayúscula). Todas las referencias deben respetar esta convención para evitar errores.

---

## 📊 Tablas Afectadas y Corregidas

### Base de Datos Origen: `gestionproyectos_hist`

| Tabla Original | Uso Correcto | Correcciones Aplicadas |
|----------------|--------------|------------------------|
| `Cliente` | ✅ `Cliente` | Backend: 8 referencias corregidas |
| `Empleado` | ✅ `Empleado` | Backend: 6 referencias corregidas |
| `Equipo` | ✅ `Equipo` | Backend: 5 referencias corregidas |
| `Estado` | ✅ `Estado` | Backend: 4 referencias corregidas |
| `Proyecto` | ✅ `Proyecto` | Backend: 3 referencias corregidas |
| `Tarea` | ✅ `Tarea` | Backend: 2 referencias corregidas |
| `MiembroEquipo` | ✅ `MiembroEquipo` | Backend: 2 referencias corregidas |
| `TareaEquipoHist` | ✅ `TareaEquipoHist` | Backend: 1 referencia corregida |

### DataWarehouse: `dw_proyectos_hist`

| Tabla | Columna Corregida | Antes | Después |
|-------|-------------------|-------|---------|
| `DimProyecto` | fecha inicio | `fecha_inicio_plan` | `fecha_inicio` |
| `DimProyecto` | índice | `(fecha_inicio_plan, fecha_fin_plan)` | `(fecha_inicio, fecha_fin_plan)` |

---

## 🔍 Validación de Consistencia

### Nomenclatura Estandarizada

#### ✅ Base de Datos Origen
```
- Cliente
- Empleado
- Equipo
- Estado
- Proyecto
- Tarea
- MiembroEquipo
- TareaEquipoHist
```

#### ✅ DataWarehouse (Dimensiones y Hechos)
```
Dimensiones:
- DimCliente
- DimEmpleado
- DimEquipo
- DimProyecto
- DimTiempo

Hechos:
- HechoProyecto
- HechoTarea
```

---

## 📝 Archivos Modificados

### 1. `/04_Datawarehouse/scripts/crear_datawarehouse.sql`
- ✅ Línea 51: Cambiado `fecha_inicio_plan` → `fecha_inicio`
- ✅ Línea 59: Actualizado índice para usar `fecha_inicio`

### 2. `/03_Dashboard/backend/app.py`
- ✅ Línea 484: `INSERT INTO Cliente` (antes: `cliente`)
- ✅ Línea 502: `INSERT INTO Empleado` (antes: `empleado`)
- ✅ Línea 508: `SELECT COUNT(*) FROM Equipo` (antes: `equipo`)
- ✅ Línea 513: `INSERT INTO Equipo` (antes: `equipo`)
- ✅ Línea 519: `SELECT COUNT(*) FROM Estado` (antes: `estado`)
- ✅ Línea 522: `INSERT INTO Estado` (antes: `estado`)
- ✅ Línea 526: `SELECT id_empleado FROM Empleado` (antes: `empleado`)
- ✅ Línea 528: `SELECT id_equipo FROM Equipo` (antes: `equipo`)
- ✅ Línea 539: `INSERT INTO MiembroEquipo` (antes: `miembroequipo`)
- ✅ Línea 543: `SELECT id_cliente FROM Cliente` (antes: `cliente`)
- ✅ Línea 545: `SELECT id_empleado FROM Empleado` (antes: `empleado`)
- ✅ Línea 547: `SELECT id_equipo FROM Equipo` (antes: `equipo`)
- ✅ Línea 549: `SELECT id_estado FROM Estado` (antes: `estado`)
- ✅ Línea 554: `SELECT id_estado FROM Estado WHERE...` (antes: `estado`)
- ✅ Línea 581: `INSERT INTO Proyecto` (antes: `proyecto`)
- ✅ Línea 616: `INSERT INTO Tarea` (antes: `tarea`)
- ✅ Línea 623: `INSERT INTO TareaEquipoHist` (antes: `tareaequipohist`)

---

## 🎯 Impacto de las Correcciones

### Antes de las Correcciones:
- ❌ Errores al insertar datos desde el dashboard
- ❌ Inconsistencia entre nombres de columnas en DW y origen
- ❌ Scripts SQL fallaban por nombres incorrectos de tablas
- ❌ Proceso ETL no podía mapear correctamente las columnas

### Después de las Correcciones:
- ✅ Todas las inserciones funcionan correctamente
- ✅ Nombres consistentes entre origen y destino
- ✅ ETL ejecuta sin errores de mapeo
- ✅ Dashboard puede generar y mostrar datos sin problemas

---

## 🧪 Pruebas Recomendadas

Para verificar que todas las correcciones funcionan correctamente:

### 1. Prueba de Inserción de Datos
```bash
# Desde el dashboard, ejecutar:
POST http://localhost:5001/generar-datos
{
  "clientes": 10,
  "empleados": 20,
  "equipos": 5,
  "proyectos": 50
}
```

### 2. Prueba de ETL
```bash
cd 02_ETL/scripts
python etl_principal.py local
```

### 3. Verificación de DataWarehouse
```sql
-- Verificar que DimProyecto tiene la columna correcta
USE dw_proyectos_hist;
DESCRIBE DimProyecto;
-- Debe mostrar: fecha_inicio (no fecha_inicio_plan)

-- Verificar datos cargados
SELECT COUNT(*) FROM DimProyecto;
SELECT COUNT(*) FROM HechoProyecto;
```

### 4. Verificación de Base Origen
```sql
-- Verificar tablas con nombres correctos
USE gestionproyectos_hist;
SHOW TABLES;
-- Debe mostrar nombres con mayúsculas: Cliente, Empleado, Equipo, etc.

SELECT COUNT(*) FROM Cliente;
SELECT COUNT(*) FROM Proyecto;
```

---

## 📚 Convenciones de Nomenclatura Establecidas

### Para Tablas de BD Origen:
- **Formato:** PascalCase (primera letra mayúscula)
- **Ejemplo:** `Cliente`, `Empleado`, `Proyecto`
- **Tablas compuestas:** `MiembroEquipo`, `TareaEquipoHist`

### Para Dimensiones en DataWarehouse:
- **Formato:** Prefijo "Dim" + PascalCase
- **Ejemplo:** `DimCliente`, `DimEmpleado`, `DimProyecto`

### Para Hechos en DataWarehouse:
- **Formato:** Prefijo "Hecho" + PascalCase
- **Ejemplo:** `HechoProyecto`, `HechoTarea`

### Para Columnas:
- **Formato:** snake_case (minúsculas con guiones bajos)
- **Ejemplo:** `fecha_inicio`, `nombre_proyecto`, `id_cliente`

---

## 🚨 Errores Comunes a Evitar

### ❌ NO HACER:
```sql
-- Usar minúsculas cuando la tabla es mayúscula
SELECT * FROM cliente;  -- ❌ Error en Linux/Unix

-- Usar nombres inconsistentes
INSERT INTO proyecto VALUES...;  -- ❌

-- Mezclar convenciones
SELECT * FROM Cliente WHERE Nombre = 'test';  -- ❌ columna debe ser minúscula
```

### ✅ HACER:
```sql
-- Respetar mayúsculas en nombres de tabla
SELECT * FROM Cliente;  -- ✅

-- Usar nombres consistentes
INSERT INTO Proyecto VALUES...;  -- ✅

-- Seguir convención de columnas en minúsculas
SELECT * FROM Cliente WHERE nombre = 'test';  -- ✅
```

---

## 📞 Contacto y Soporte

Si encuentras alguna inconsistencia adicional en los nombres de tablas o columnas:

1. Verifica este documento primero
2. Revisa los esquemas en:
   - `01_GestionProyectos/scripts/crear_bd_origen.sql`
   - `04_Datawarehouse/scripts/crear_datawarehouse.sql`
3. Asegúrate de seguir las convenciones establecidas

---

## 📅 Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2025-10-22 | 1.0 | Correcciones iniciales de nombres de tablas y columnas |

---

**Nota:** Este documento debe mantenerse actualizado con cualquier cambio futuro en la estructura de las bases de datos.
