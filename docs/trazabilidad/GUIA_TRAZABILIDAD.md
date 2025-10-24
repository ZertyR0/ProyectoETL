# Guía de Trazabilidad y Control de Duplicados

## 📋 Descripción General

Este documento describe las mejoras implementadas en el sistema ETL para garantizar:
- ✅ **Trazabilidad completa** de los datos
- ✅ **Eliminación de duplicados** (excepto fechas)
- ✅ **Búsqueda entre bases de datos**
- ✅ **Validación de integridad**

## 🆕 Nuevos Scripts

### 1. Generador de Datos Mejorado
**Ubicación**: `01_GestionProyectos/scripts/generar_datos_mejorado.py`

#### Características:
- ✨ **Nombres únicos garantizados** para clientes, empleados y equipos
- ✨ **Emails únicos** para todos los clientes
- ✨ **Proyectos únicos** basados en tipo y cliente
- ✨ **Tareas únicas** por proyecto
- ✨ **Validación automática** de integridad después de generar datos
- ✨ **Hashing interno** para prevenir duplicados

#### Uso:
```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar generador mejorado
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

#### Salida Esperada:
```
🚀 Generador de Datos MEJORADO - Sistema de Gestión de Proyectos
   ✓ Con trazabilidad
   ✓ Sin duplicados
   ✓ Validación de integridad
======================================================================
✅ Conectado a BD Origen (gestionproyectos_hist)
🧹 Limpiando tablas existentes...
👥 Generando 8 clientes...
  ✅ 8 clientes únicos creados
👨‍💼 Generando 15 empleados...
  ✅ 15 empleados únicos creados
...
🔍 Validando integridad de datos...
  ✅ Clientes únicos: 8/8
  ✅ Emails únicos: 8/8
  ✅ Empleados únicos: 15/15
  ✅ Equipos únicos: 5/5
  ✅ Proyectos únicos: 12/12
  ✅ Asignaciones equipo-empleado únicas: 25/25
  ✅ Asignaciones historial únicas: 52/52

✅ Todos los datos pasaron las validaciones de integridad
```

### 2. Verificador de Trazabilidad
**Ubicación**: `verificar_trazabilidad.py`

#### Características:
- 🔍 **Búsqueda por ID de proyecto** en ambas bases de datos
- 🔍 **Búsqueda por nombre de cliente** con resultados parciales
- 🔍 **Búsqueda por nombre de empleado** con resultados parciales
- 📊 **Verificación de conteos** entre BD origen y destino
- 🚨 **Detección de duplicados** en BD origen
- 📋 **Listado de proyectos no migrados** y razones

#### Uso Interactivo:
```bash
# Modo menú interactivo
python verificar_trazabilidad.py
```

#### Uso por Línea de Comandos:
```bash
# Generar reporte completo
python verificar_trazabilidad.py reporte

# Solo verificar conteos
python verificar_trazabilidad.py conteos

# Solo buscar duplicados
python verificar_trazabilidad.py duplicados

# Listar proyectos no migrados
python verificar_trazabilidad.py no-migrados
```

## 🔄 Flujo de Trabajo Completo

### Paso 1: Generar Datos Limpios
```bash
# Generar datos SIN duplicados
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

### Paso 2: Ejecutar ETL
```bash
# Ejecutar proceso ETL
python 02_ETL/scripts/etl_principal.py
```

### Paso 3: Verificar Trazabilidad
```bash
# Verificar que todo se migró correctamente
python verificar_trazabilidad.py reporte
```

## 📊 Validaciones Implementadas

### En el Generador de Datos:

1. **Clientes**:
   - ✅ Nombres únicos
   - ✅ Emails únicos
   - ✅ Sin duplicados por sector

2. **Empleados**:
   - ✅ Nombres únicos
   - ✅ Sin duplicados por departamento
   - ✅ Salarios coherentes según puesto

3. **Proyectos**:
   - ✅ Nombres únicos (tipo + cliente)
   - ✅ Fechas coherentes (inicio < fin)
   - ✅ Presupuestos realistas

4. **Tareas**:
   - ✅ Únicas por proyecto
   - ✅ Fechas dentro del rango del proyecto
   - ✅ Horas y costos coherentes

5. **Asignaciones**:
   - ✅ Sin duplicados equipo-empleado
   - ✅ Sin duplicados tarea-equipo
   - ✅ Fechas válidas

## 🔍 Ejemplos de Búsqueda

### Buscar un Proyecto Específico:
```bash
python verificar_trazabilidad.py
# Seleccionar opción 2
# Ingresar ID: 5
```

**Resultado**:
```
🔍 Buscando Proyecto ID: 5
======================================================================

📦 BD ORIGEN (gestionproyectos_hist):
----------------------------------------------------------------------
  id_proyecto                  : 5
  nombre                       : Sistema Web - Constructora ABC
  fecha_inicio                 : 2024-03-15
  presupuesto                  : 150000.00
  costo_real                   : 148500.00
  ...

📦 BD DESTINO (dw_proyectos_hist):
----------------------------------------------------------------------
  id_proyecto                  : 5
  nombre_proyecto              : Sistema Web - Constructora ABC
  duracion_planificada         : 90
  duracion_real                : 87
  cumplimiento_tiempo          : 1
  cumplimiento_presupuesto     : 1
  ...

✅ Proyecto encontrado en ambas bases de datos
```

### Verificar Duplicados:
```bash
python verificar_trazabilidad.py duplicados
```

**Resultado sin duplicados**:
```
🔍 VERIFICACIÓN DE DUPLICADOS EN BD ORIGEN
======================================================================

✅ No hay clientes duplicados
✅ No hay empleados duplicados
✅ No hay emails duplicados
✅ No hay proyectos duplicados
✅ No hay asignaciones equipo-empleado duplicadas
```

## 📈 Reporte Completo de Trazabilidad

### Ejecutar:
```bash
python verificar_trazabilidad.py reporte
```

### Contenido del Reporte:

1. **Verificación de Conteos**:
   - Clientes: Origen vs Destino
   - Empleados: Origen vs Destino
   - Equipos: Origen vs Destino
   - Proyectos: Origen vs Destino
   - Hechos: Validación de carga

2. **Detección de Duplicados**:
   - Clientes duplicados
   - Empleados duplicados
   - Emails duplicados
   - Proyectos duplicados
   - Asignaciones duplicadas

3. **Proyectos No Migrados**:
   - Lista de proyectos en origen pero no en DW
   - Razón de no migración (estado)
   - Progreso actual

## 🛠️ Solución de Problemas

### Problema: "No hay clientes únicos"
**Solución**: Regenerar datos con el script mejorado
```bash
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

### Problema: "Conteos no coinciden"
**Diagnóstico**:
1. Verificar que el ETL se ejecutó correctamente
2. Revisar logs del ETL
3. Verificar filtros (solo proyectos completados/cancelados)

**Solución**:
```bash
# Re-ejecutar ETL
python 02_ETL/scripts/etl_principal.py

# Verificar nuevamente
python verificar_trazabilidad.py conteos
```

### Problema: "Se encontraron duplicados"
**Solución**: Limpiar y regenerar datos
```bash
# 1. Limpiar BD origen
mysql -u root -p -e "USE gestionproyectos_hist; 
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE TareaEquipoHist;
TRUNCATE TABLE MiembroEquipo;
TRUNCATE TABLE Tarea;
TRUNCATE TABLE Proyecto;
TRUNCATE TABLE Equipo;
TRUNCATE TABLE Empleado;
TRUNCATE TABLE Cliente;
SET FOREIGN_KEY_CHECKS = 1;"

# 2. Regenerar datos
python 01_GestionProyectos/scripts/generar_datos_mejorado.py

# 3. Re-ejecutar ETL
python 02_ETL/scripts/etl_principal.py
```

## 📝 Logs y Auditoría

### Campos de Auditoría en Dimensiones:
- `fecha_carga`: Timestamp de cuando se cargó el registro
- `fecha_actualizacion`: Timestamp de última actualización

### Consultas de Auditoría:

#### Ver últimas cargas en el DW:
```sql
USE dw_proyectos_hist;

-- Últimos clientes cargados
SELECT id_cliente, nombre, fecha_carga
FROM DimCliente
ORDER BY fecha_carga DESC
LIMIT 10;

-- Últimos proyectos cargados
SELECT id_proyecto, nombre_proyecto, fecha_carga
FROM DimProyecto
ORDER BY fecha_carga DESC
LIMIT 10;

-- Hechos más recientes
SELECT id_hecho_proyecto, id_proyecto, fecha_carga
FROM HechoProyecto
ORDER BY fecha_carga DESC
LIMIT 10;
```

#### Verificar integridad referencial:
```sql
-- Proyectos huérfanos (sin cliente)
SELECT hp.id_proyecto, hp.id_cliente
FROM HechoProyecto hp
LEFT JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
WHERE dc.id_cliente IS NULL;

-- Proyectos sin gerente
SELECT hp.id_proyecto, hp.id_empleado_gerente
FROM HechoProyecto hp
LEFT JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
WHERE hp.id_empleado_gerente IS NOT NULL 
  AND de.id_empleado IS NULL;
```

## 🎯 Mejores Prácticas

### 1. Antes de Ejecutar ETL:
- ✅ Verificar que no hay duplicados en origen
- ✅ Validar integridad de datos de origen
- ✅ Hacer backup de DW si contiene datos importantes

### 2. Durante el ETL:
- ✅ Monitorear logs en tiempo real
- ✅ Verificar que no hay errores de conexión
- ✅ Observar las métricas de carga

### 3. Después del ETL:
- ✅ Ejecutar verificador de trazabilidad
- ✅ Revisar conteos de registros
- ✅ Validar que los datos tienen sentido

### 4. Periodicidad:
- 📅 **Diario**: Verificar duplicados en origen
- 📅 **Semanal**: Reporte completo de trazabilidad
- 📅 **Mensual**: Auditoría completa de datos

## 📚 Referencias

- Script generador: `01_GestionProyectos/scripts/generar_datos_mejorado.py`
- Script verificador: `verificar_trazabilidad.py`
- Script ETL: `02_ETL/scripts/etl_principal.py`
- Documentación adicional: `README_COMPLETO.md`

## 🆘 Soporte

Para reportar problemas o sugerencias:
1. Ejecutar: `python verificar_trazabilidad.py reporte`
2. Guardar el output
3. Incluir logs del ETL
4. Reportar con contexto completo
