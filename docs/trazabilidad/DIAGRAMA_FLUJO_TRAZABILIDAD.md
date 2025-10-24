# 🗺️ Diagrama de Flujo - Sistema de Trazabilidad

## 📊 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE TRAZABILIDAD                          │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐   ┌──────────────┐  │
│  │  BD ORIGEN       │    │   PROCESO ETL    │   │  BD DESTINO  │  │
│  │ gestionproyectos │───>│  etl_principal   │──>│ dw_proyectos │  │
│  │      _hist       │    │                  │   │    _hist     │  │
│  └──────────────────┘    └──────────────────┘   └──────────────┘  │
│           │                       │                      │          │
│           │                       │                      │          │
│           ▼                       ▼                      ▼          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          VERIFICADOR DE TRAZABILIDAD                         │  │
│  │        verificar_trazabilidad.py                             │  │
│  │                                                              │  │
│  │  • Búsqueda entre BD                                         │  │
│  │  • Verificación de conteos                                   │  │
│  │  • Detección de duplicados                                   │  │
│  │  • Reportes de auditoría                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Trabajo Completo

### Fase 1: Generación de Datos
```
┌────────────────────────────────────────────────────────────┐
│  INICIO: Generación de Datos                              │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  Ejecutar: generar_datos_mejorado.py                      │
│  ──────────────────────────────────────────────────────── │
│  • Limpiar tablas existentes                              │
│  • Generar clientes únicos (set tracking)                 │
│  • Generar empleados únicos (set tracking)                │
│  • Generar equipos únicos                                 │
│  • Generar proyectos únicos (hash-based)                  │
│  • Generar tareas únicas por proyecto                     │
│  • Generar asignaciones sin duplicados                    │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  Validación Automática Integrada                          │
│  ──────────────────────────────────────────────────────── │
│  ✅ Clientes únicos: X/X                                  │
│  ✅ Emails únicos: X/X                                    │
│  ✅ Empleados únicos: X/X                                 │
│  ✅ Proyectos únicos: X/X                                 │
│  ✅ Asignaciones únicas: X/X                              │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │ ¿Válido?│
                    └─────────┘
                      │      │
                  Sí  │      │ No
                      ▼      ▼
              [Continuar] [Revisar Error]
```

### Fase 2: Verificación Pre-ETL
```
┌────────────────────────────────────────────────────────────┐
│  Verificación Opcional (Recomendada)                      │
│  ──────────────────────────────────────────────────────── │
│  Comando: python verificar_trazabilidad.py duplicados     │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  Reporte de Duplicados en BD Origen                       │
│  ──────────────────────────────────────────────────────── │
│  • Clientes duplicados                                    │
│  • Empleados duplicados                                   │
│  • Emails duplicados                                      │
│  • Proyectos duplicados                                   │
│  • Asignaciones duplicadas                                │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │¿Limpio? │
                    └─────────┘
                      │      │
                  Sí  │      │ No
                      ▼      ▼
              [ETL Ready] [Regenerar]
```

### Fase 3: Proceso ETL
```
┌────────────────────────────────────────────────────────────┐
│  Ejecutar: etl_principal.py                               │
│  ──────────────────────────────────────────────────────── │
│  1. Extract: Leer de BD Origen                            │
│     • Clientes activos                                    │
│     • Empleados activos                                   │
│     • Proyectos completados/cancelados                    │
│     • Tareas relacionadas                                 │
│                                                            │
│  2. Transform: Limpiar y calcular métricas                │
│     • Crear dimensión tiempo                              │
│     • Calcular cumplimientos                              │
│     • Calcular variaciones                                │
│     • Generar indicadores                                 │
│                                                            │
│  3. Load: Cargar a DataWarehouse                          │
│     • DimCliente, DimEmpleado, DimEquipo                  │
│     • DimProyecto, DimTiempo                              │
│     • HechoProyecto, HechoTarea                           │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
                  [ETL Completo]
```

### Fase 4: Verificación Post-ETL
```
┌────────────────────────────────────────────────────────────┐
│  Verificación Obligatoria                                 │
│  ──────────────────────────────────────────────────────── │
│  Opción A: ./validar_trazabilidad.sh → Opción 1          │
│  Opción B: python verificar_trazabilidad.py reporte      │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  1. Verificación de Conteos                               │
│  ┌──────────────────┬───────────┬────────────┬─────────┐  │
│  │ Entidad          │ BD Origen │ BD Destino │ Estado  │  │
│  ├──────────────────┼───────────┼────────────┼─────────┤  │
│  │ Clientes         │     8     │      8     │   ✅    │  │
│  │ Empleados        │    15     │     15     │   ✅    │  │
│  │ Proyectos        │     8     │      8     │   ✅    │  │
│  │ HechoProyecto    │     8     │      8     │   ✅    │  │
│  └──────────────────┴───────────┴────────────┴─────────┘  │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  2. Detección de Duplicados en Origen                     │
│  ──────────────────────────────────────────────────────── │
│  ✅ No hay clientes duplicados                            │
│  ✅ No hay empleados duplicados                           │
│  ✅ No hay emails duplicados                              │
│  ✅ No hay proyectos duplicados                           │
│  ✅ No hay asignaciones duplicadas                        │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  3. Proyectos No Migrados                                 │
│  ──────────────────────────────────────────────────────── │
│  ⚠️  4 proyecto(s) NO migrado(s):                         │
│  • ID 1: Portal Admin (En Progreso - 45%)                │
│  • ID 3: App Mobile (En Progreso - 60%)                  │
│  • ID 9: Sistema CRM (Pendiente - 0%)                    │
│  • ID 11: Plataforma BI (En Pausa - 25%)                 │
│                                                            │
│  💡 Nota: Solo se migran Completados/Cancelados          │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
                    ┌─────────┐
                    │¿Todo OK?│
                    └─────────┘
                      │      │
                  Sí  │      │ No
                      ▼      ▼
            [Sistema Listo] [Investigar]
```

## 🔍 Flujo de Búsqueda de Trazabilidad

### Búsqueda de Proyecto
```
[Usuario busca Proyecto ID: 5]
            │
            ▼
┌──────────────────────────────────┐
│ verificar_trazabilidad.py        │
│ buscar_proyecto_por_id(5)        │
└──────────────────────────────────┘
            │
            ├─────────────────────┐
            ▼                     ▼
   ┌─────────────────┐   ┌─────────────────┐
   │  BD ORIGEN      │   │  BD DESTINO     │
   │                 │   │                 │
   │ Query:          │   │ Query:          │
   │ SELECT * FROM   │   │ SELECT * FROM   │
   │ Proyecto p      │   │ DimProyecto dp  │
   │ JOIN Cliente c  │   │ JOIN            │
   │ JOIN Empleado e │   │ HechoProyecto hp│
   │ WHERE id = 5    │   │ WHERE id = 5    │
   └─────────────────┘   └─────────────────┘
            │                     │
            └─────────┬───────────┘
                      ▼
         ┌──────────────────────────┐
         │ Comparar y Mostrar       │
         │ ──────────────────────   │
         │ • Datos de origen        │
         │ • Datos de destino       │
         │ • Estado de migración    │
         └──────────────────────────┘
                      │
                      ▼
              [Resultado al Usuario]
```

### Búsqueda de Cliente
```
[Usuario busca Cliente: "Tech"]
            │
            ▼
┌──────────────────────────────────┐
│ verificar_trazabilidad.py        │
│ buscar_cliente_por_nombre("Tech")│
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│ BD ORIGEN: SELECT * FROM Cliente │
│ WHERE nombre LIKE '%Tech%'       │
└──────────────────────────────────┘
            │
            ├─> [Cliente 1: Tech Corp]
            ├─> [Cliente 2: TechStart Inc]
            └─> [Cliente 3: BioTech SA]
            │
            ▼
   Para cada cliente encontrado:
            │
            ▼
┌──────────────────────────────────┐
│ BD DESTINO: SELECT * FROM        │
│ DimCliente WHERE id_cliente = X  │
└──────────────────────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ ✅ Encontrado en DW     │
   │ ❌ NO encontrado en DW  │
   └─────────────────────────┘
```

## 📊 Flujo de Validación de Duplicados

```
[Ejecutar verificación de duplicados]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ Verificar Clientes Duplicados                         │
│ ────────────────────────────────────────────────────── │
│ SELECT nombre, COUNT(*) as cantidad                   │
│ FROM Cliente                                           │
│ GROUP BY nombre                                        │
│ HAVING COUNT(*) > 1                                    │
└────────────────────────────────────────────────────────┘
            │
            ├─> Duplicados encontrados? ─> [Listar]
            └─> No duplicados ──────────> [✅ OK]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ Verificar Emails Duplicados                           │
│ ────────────────────────────────────────────────────── │
│ SELECT email, COUNT(*) as cantidad                    │
│ FROM Cliente                                           │
│ WHERE email IS NOT NULL                                │
│ GROUP BY email                                         │
│ HAVING COUNT(*) > 1                                    │
└────────────────────────────────────────────────────────┘
            │
            ├─> Duplicados encontrados? ─> [Listar]
            └─> No duplicados ──────────> [✅ OK]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ Verificar Empleados Duplicados                        │
│ (Similar a clientes)                                   │
└────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ Verificar Asignaciones Duplicadas                     │
│ ────────────────────────────────────────────────────── │
│ SELECT id_equipo, id_empleado, COUNT(*)              │
│ FROM MiembroEquipo                                     │
│ GROUP BY id_equipo, id_empleado                       │
│ HAVING COUNT(*) > 1                                    │
└────────────────────────────────────────────────────────┘
            │
            ▼
      [Reporte Final]
```

## 🎯 Puntos de Control de Calidad

```
CHECKPOINT 1: Post-Generación
┌─────────────────────────────────────┐
│ ✓ Nombres únicos                    │
│ ✓ Emails únicos                     │
│ ✓ Asignaciones sin duplicados       │
│ ✓ Datos coherentes                  │
└─────────────────────────────────────┘
           │
           ▼
CHECKPOINT 2: Pre-ETL
┌─────────────────────────────────────┐
│ ✓ Verificar duplicados en origen    │
│ ✓ Validar integridad referencial    │
│ ✓ Confirmar datos de prueba         │
└─────────────────────────────────────┘
           │
           ▼
CHECKPOINT 3: Post-ETL
┌─────────────────────────────────────┐
│ ✓ Conteos coinciden                 │
│ ✓ Todos los registros migrados      │
│ ✓ Sin errores en log ETL            │
│ ✓ Métricas calculadas correctamente │
└─────────────────────────────────────┘
           │
           ▼
CHECKPOINT 4: Pre-Dashboard
┌─────────────────────────────────────┐
│ ✓ Datos disponibles en DW           │
│ ✓ Vistas funcionando                │
│ ✓ Consultas optimizadas             │
│ ✓ Reporte de trazabilidad OK        │
└─────────────────────────────────────┘
```

## 🔄 Ciclo de Vida del Dato

```
┌──────────┐
│  ORIGEN  │  1. Generación con validación
└──────────┘     • generar_datos_mejorado.py
     │           • Sin duplicados garantizado
     │           • Validación automática
     ▼
┌──────────┐
│VALIDACIÓN│  2. Verificación pre-ETL
└──────────┘     • verificar_trazabilidad.py duplicados
     │           • Confirmación de limpieza
     │
     ▼
┌──────────┐
│    ETL   │  3. Proceso de transformación
└──────────┘     • etl_principal.py
     │           • Extract, Transform, Load
     │           • Cálculo de métricas
     ▼
┌──────────┐
│VALIDACIÓN│  4. Verificación post-ETL
└──────────┘     • verificar_trazabilidad.py conteos
     │           • Confirmación de migración
     │
     ▼
┌──────────┐
│    DW    │  5. Datos listos para análisis
└──────────┘     • Datos íntegros y trazables
     │           • Métricas calculadas
     │           • Sin duplicados
     ▼
┌──────────┐
│DASHBOARD │  6. Visualización
└──────────┘     • Reportes confiables
                 • Análisis precisos
                 • Decisiones informadas
```

## 🛠️ Herramientas y Sus Roles

```
┌──────────────────────────────────────────────────────────────┐
│                    HERRAMIENTAS DEL SISTEMA                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  generar_datos_mejorado.py                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ROL: Generador de datos sin duplicados                 │ │
│  │ ENTRADA: Configuración de cantidades                   │ │
│  │ SALIDA: BD Origen con datos limpios                    │ │
│  │ GARANTIZA: Unicidad de registros                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  verificar_trazabilidad.py                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ROL: Auditor y buscador entre BD                       │ │
│  │ ENTRADA: Ambas bases de datos                          │ │
│  │ SALIDA: Reportes de trazabilidad                       │ │
│  │ GARANTIZA: Visibilidad total del pipeline              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  validar_trazabilidad.sh                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ROL: Facilitador de ejecución                          │ │
│  │ ENTRADA: Selección de usuario                          │ │
│  │ SALIDA: Reportes guardados automáticamente             │ │
│  │ GARANTIZA: Facilidad de uso                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 📈 Mejora en el Proceso

### ANTES: Proceso Sin Trazabilidad
```
Generar Datos
     │
     ▼
   (???)  ← ¿Hay duplicados?
     │
     ▼
Ejecutar ETL
     │
     ▼
   (???)  ← ¿Se migró todo?
     │
     ▼
Dashboard
     │
     ▼
   (???)  ← ¿Datos correctos?

⏱️  Tiempo de debugging: ALTO
🎯 Confianza en datos: BAJA
🔍 Visibilidad: MÍNIMA
```

### AHORA: Proceso Con Trazabilidad
```
Generar Datos Mejorado
     │
     ▼
   ✅ Validación Automática
     │
     ▼
Verificar Duplicados
     │
     ▼
   ✅ Sin Duplicados
     │
     ▼
Ejecutar ETL
     │
     ▼
Verificar Conteos
     │
     ▼
   ✅ Todo Migrado
     │
     ▼
Dashboard
     │
     ▼
   ✅ Datos Confiables

⏱️  Tiempo de debugging: BAJO
🎯 Confianza en datos: ALTA
🔍 Visibilidad: TOTAL
```

---

## 📝 Leyenda de Símbolos

- ✅ : Validación exitosa / Paso completado
- ❌ : Error / Validación fallida
- ⚠️  : Advertencia / Revisar
- 🔍 : Búsqueda / Investigación
- 📊 : Reporte / Estadísticas
- 🔄 : Proceso / Ciclo
- 💡 : Información / Nota
- 🎯 : Objetivo / Meta
- 🛠️ : Herramienta / Utilidad

---

**Nota**: Este diagrama representa el flujo completo del sistema de trazabilidad implementado. Cada paso incluye validaciones automáticas para garantizar la integridad de los datos.
