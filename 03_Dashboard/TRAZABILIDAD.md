# 🔍 Búsqueda y Trazabilidad - Dashboard ETL

**Fecha:** 27 de octubre de 2025  
**Versión:** 1.0

---

## 📋 Descripción

La funcionalidad de **Búsqueda y Trazabilidad** permite buscar registros específicos en la **Base de Datos Origen** y verificar automáticamente si están presentes en el **DataWarehouse**.

Esta herramienta es útil para:
- ✅ Verificar que un registro se haya procesado correctamente en el ETL
- ✅ Auditar la trazabilidad de datos entre BD Origen y DW
- ✅ Diagnosticar problemas de sincronización
- ✅ Validar que los filtros del ETL funcionan correctamente

---

## 🎯 Tipos de Búsqueda Soportados

### 1. **Proyectos**
- Buscar por **ID** (ejemplo: `1`, `25`, `100`)
- Buscar por **Nombre** (ejemplo: `Sistema ERP`, `Desarrollo`)

**Datos mostrados:**
- BD Origen: ID, nombre, cliente, gerente, estado, fechas, presupuesto, costo real, prioridad
- DataWarehouse: ID, nombre, presupuesto, costo real, duración planificada, duración real, cumplimiento, tareas

### 2. **Clientes**
- Buscar por **ID** (ejemplo: `1`, `10`, `50`)
- Buscar por **Nombre** (ejemplo: `Acme Corp`, `TechSolutions`)

**Datos mostrados:**
- Ambas BD: ID, nombre, sector, contacto, teléfono, email, dirección, fecha registro, activo

### 3. **Empleados**
- Buscar por **ID** (ejemplo: `1`, `25`, `75`)
- Buscar por **Nombre** (ejemplo: `Juan Pérez`, `María`)

**Datos mostrados:**
- Ambas BD: ID, nombre, puesto, departamento, salario base, fecha ingreso, activo

### 4. **Tareas**
- Buscar por **ID** (ejemplo: `1`, `500`, `1000`)
- Buscar por **Nombre** (ejemplo: `Desarrollo Frontend`, `Testing`)

**Datos mostrados:**
- BD Origen: ID, nombre, proyecto, empleado, estado, fechas, horas, costos, progreso
- DataWarehouse: ID, proyecto, empleado, duración, horas, costos, progreso

---

## 🚀 Cómo Usar

### Paso 1: Acceder a la Sección
1. Abre el dashboard: `http://localhost:8080`
2. En el menú lateral, haz clic en **"Trazabilidad"** (ícono de lupa 🔍)

### Paso 2: Configurar la Búsqueda
Complete los 3 campos del formulario:

1. **Tipo de Registro**
   - Selecciona: Proyecto, Cliente, Empleado o Tarea

2. **Buscar por**
   - `ID (número)`: Para búsquedas exactas por identificador
   - `Nombre (texto)`: Para búsquedas parciales por nombre (usa LIKE)

3. **Valor a buscar**
   - Si buscas por ID: escribe el número (ejemplo: `25`)
   - Si buscas por nombre: escribe el texto (ejemplo: `Sistema`)

### Paso 3: Ejecutar la Búsqueda
- Haz clic en el botón **"Buscar"** 🔍

### Paso 4: Interpretar Resultados
La búsqueda mostrará:

#### ✅ **Mensaje de Estado** (color-coded)
- 🟢 **Verde (Éxito)**: Encontrado en ambas BD
- 🟡 **Amarillo (Advertencia)**: Encontrado solo en BD Origen
- 🔴 **Rojo (Error)**: No encontrado en BD Origen

#### 📊 **Dos Tarjetas Comparativas**
- **Izquierda (Azul)**: Datos de la BD Origen
- **Derecha (Verde)**: Datos del DataWarehouse

Cada tarjeta muestra:
- Badge de estado (ENCONTRADO / NO ENCONTRADO)
- Tabla con todos los campos relevantes
- Valores formateados según tipo (moneda, fecha, booleano)

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Buscar Proyecto por ID
```
Tipo: Proyecto
Buscar por: ID (número)
Valor: 25
```

**Resultado esperado:**
- ✅ BD Origen: Proyecto #25 con todos sus datos
- ✅ DataWarehouse: Hecho del proyecto #25 (solo si está completado/cancelado)

### Ejemplo 2: Buscar Cliente por Nombre
```
Tipo: Cliente
Buscar por: Nombre (texto)
Valor: Acme
```

**Resultado esperado:**
- ✅ Encuentra clientes cuyo nombre contenga "Acme"
- ✅ Muestra si están en el DW

### Ejemplo 3: Buscar Empleado por ID
```
Tipo: Empleado
Buscar por: ID (número)
Valor: 10
```

**Resultado esperado:**
- ✅ BD Origen: Empleado #10 con su información
- ✅ DataWarehouse: DimEmpleado #10 (si está activo y participó en proyectos finalizados)

### Ejemplo 4: Buscar Tarea por Nombre
```
Tipo: Tarea
Buscar por: Nombre (texto)
Valor: Testing
```

**Resultado esperado:**
- ✅ Encuentra tareas con "Testing" en su nombre
- ✅ Verifica si están en HechoTarea del DW

---

## 🔍 Casos de Uso Prácticos

### 1. **Verificar que un Proyecto se procesó en el ETL**
```
Escenario: Acabas de ejecutar el ETL y quieres verificar que el proyecto #100 se cargó correctamente.

Pasos:
1. Tipo: Proyecto
2. Buscar por: ID
3. Valor: 100
4. Click "Buscar"

Resultado esperado:
✅ Verde - Encontrado en ambas BD (si el proyecto está completado/cancelado)
⚠️ Amarillo - Solo en origen (si el proyecto está en progreso)
```

### 2. **Auditar Clientes activos en el DW**
```
Escenario: Necesitas verificar qué clientes están en el DataWarehouse.

Pasos:
1. Tipo: Cliente
2. Buscar por: ID o Nombre
3. Valor: (ID o nombre del cliente)
4. Click "Buscar"

Resultado esperado:
✅ Cliente activo → Debe estar en DimCliente
❌ Cliente inactivo → Puede no estar en DW
```

### 3. **Diagnosticar Tareas faltantes en el DW**
```
Escenario: Algunas tareas no aparecen en los reportes del DW.

Pasos:
1. Tipo: Tarea
2. Buscar por: ID
3. Valor: (ID de la tarea problema)
4. Click "Buscar"

Diagnóstico:
✅ Verde → La tarea está en el DW (buscar en otra parte)
⚠️ Amarillo → La tarea NO está en el DW
   → Verificar si el proyecto padre está completado/cancelado
   → Revisar filtros del ETL
```

---

## ⚙️ Detalles Técnicos

### Endpoint API
```
POST /buscar-trazabilidad
Content-Type: application/json

{
  "tipo": "proyecto|cliente|empleado|tarea",
  "criterio": "id|nombre",
  "valor": "valor a buscar"
}
```

### Respuesta
```json
{
  "success": true,
  "tipo": "proyecto",
  "encontrado_origen": true,
  "encontrado_dw": true,
  "datos_origen": { ... },
  "datos_dw": { ... },
  "mensaje": "✅ Proyecto encontrado en ambas bases de datos"
}
```

### Filtros del ETL (Recordatorio)
El DataWarehouse solo contiene:
- ✅ **Clientes activos** (`activo = 1`)
- ✅ **Empleados activos** (`activo = 1`)
- ✅ **Proyectos completados o cancelados** (`id_estado IN (3, 4)`)
- ✅ **Tareas de proyectos finalizados**

Por eso es normal que algunos registros estén en Origen pero NO en DW.

---

## 📊 Estados de Búsqueda

| Estado | Color | Ícono | Significado |
|--------|-------|-------|-------------|
| Encontrado en ambas BD | 🟢 Verde | ✅ | ETL funcionó correctamente |
| Solo en BD Origen | 🟡 Amarillo | ⚠️ | Normal si no cumple filtros ETL |
| No encontrado | 🔴 Rojo | ❌ | El registro no existe |

---

## 🎨 Formateo de Datos

La búsqueda formatea automáticamente los valores según tipo:

| Tipo de Campo | Formato |
|---------------|---------|
| Fechas | `27/10/2025` |
| Moneda | `$1,500.00 MXN` |
| Booleanos | Badge Verde (Sí) / Rojo (No) |
| Estado activo | Badge Verde (Activo) / Gris (Inactivo) |
| Números | `1,500` (con separador de miles) |
| NULL | `null` (en cursiva gris) |

---

## 🛠️ Solución de Problemas

### ❌ "Proyecto no encontrado en BD Origen"
- Verifica que el ID o nombre sea correcto
- Asegúrate de que el proyecto existe en la BD
- Intenta buscar por nombre parcial

### ⚠️ "Proyecto encontrado en BD Origen pero NO en DataWarehouse"
**Causas normales:**
- El proyecto está en progreso (no completado/cancelado)
- El ETL no se ha ejecutado después de completar el proyecto
- El proyecto se completó pero tiene `activo = 0`

**Solución:**
1. Verifica el estado del proyecto en BD Origen
2. Si está completado/cancelado, ejecuta el ETL
3. Vuelve a buscar

### 🔴 "Error de conexión"
- Verifica que el backend esté corriendo (`localhost:5001`)
- Verifica que MySQL esté activo
- Revisa los logs en la sección "Control ETL"

---

## 📝 Notas Importantes

1. **Búsqueda por nombre usa LIKE**
   - Busca coincidencias parciales
   - No distingue mayúsculas/minúsculas
   - Ejemplo: buscar "Sistema" encontrará "Sistema ERP", "Sistema CRM", etc.

2. **Búsqueda por ID es exacta**
   - Solo encuentra el registro con ese ID específico
   - Más rápida que búsqueda por nombre

3. **Resultados múltiples**
   - Si buscas por nombre y hay múltiples coincidencias
   - Se muestra solo el primer resultado
   - Para ver todos, usa la sección "Datos Origen" o "DataWarehouse"

4. **Performance**
   - La búsqueda es rápida incluso con miles de registros
   - Usa índices en las bases de datos

---

## 🎯 Próximas Mejoras (Futuras)

- [ ] Búsqueda múltiple (mostrar todos los resultados)
- [ ] Filtros avanzados (por rango de fechas, por estado, etc.)
- [ ] Exportar resultados a CSV/Excel
- [ ] Historial de búsquedas
- [ ] Comparación lado a lado de campos modificados
- [ ] Gráficos de trazabilidad visual

---

## ✅ Checklist de Verificación

Usa esta checklist para validar el sistema de trazabilidad:

- [ ] ¿Puedo buscar un proyecto por ID?
- [ ] ¿Puedo buscar un proyecto por nombre?
- [ ] ¿Se muestra correctamente si está en ambas BD?
- [ ] ¿Se advierte si solo está en BD Origen?
- [ ] ¿Puedo buscar clientes, empleados y tareas?
- [ ] ¿Los datos se formatean correctamente (moneda, fechas)?
- [ ] ¿Los badges de estado son claros y precisos?
- [ ] ¿El mensaje de resultado es informativo?

---

**¡Disfruta de la trazabilidad completa de tu sistema ETL!** 🎉

---

**Documentación relacionada:**
- `README.md` - Guía general del dashboard
- `ESTADO_FINAL_SISTEMA.md` - Estado completo del sistema
- `REFACTORIZACION_ETL_SPS.md` - Arquitectura de seguridad
