# 🎯 Filtros ETL - Datawarehouse

## 📋 Resumen

El proceso ETL ha sido configurado para que el **datawarehouse solo contenga datos históricos** de proyectos que ya han finalizado, ya sea completados exitosamente o cancelados.

## ✅ Reglas de Negocio Implementadas

### Estados de Proyectos en BD Origen

| ID Estado | Nombre Estado | ¿Se incluye en DW? |
|-----------|---------------|-------------------|
| 1 | Pendiente | ❌ NO |
| 2 | En Progreso | ❌ NO |
| 3 | **Completado** | ✅ **SÍ** |
| 4 | **Cancelado** | ✅ **SÍ** |
| 5 | En Pausa | ❌ NO |
| 6 | En Revisión | ❌ NO |

### Filtros Aplicados en el ETL

#### 1. **Proyectos**
```sql
SELECT p.*, c.nombre as nombre_cliente, e.nombre as nombre_gerente,
       est.nombre_estado
FROM Proyecto p
LEFT JOIN Cliente c ON p.id_cliente = c.id_cliente
LEFT JOIN Empleado e ON p.id_empleado_gerente = e.id_empleado
LEFT JOIN Estado est ON p.id_estado = est.id_estado
WHERE p.id_estado IN (3, 4)  -- 3=Completado, 4=Cancelado
```

#### 2. **Tareas**
```sql
SELECT t.*, p.nombre as nombre_proyecto, e.nombre as nombre_empleado,
       est.nombre_estado
FROM Tarea t
LEFT JOIN Proyecto p ON t.id_proyecto = p.id_proyecto
LEFT JOIN Empleado e ON t.id_empleado = e.id_empleado
LEFT JOIN Estado est ON t.id_estado = est.id_estado
WHERE p.id_estado IN (3, 4)  -- Solo tareas de proyectos completados o cancelados
```

**Nota importante:** Las tareas se filtran por el estado del **proyecto**, no por el estado de la tarea misma. Esto significa que se incluyen **todas las tareas** de un proyecto (completadas, pendientes, canceladas, etc.) siempre que el proyecto esté completado o cancelado.

## 📊 Ejemplo de Ejecución Actual

### Datos en BD Origen
- Total de proyectos: **12**
- Proyectos en estado Completado: **1**
- Proyectos en estado Cancelado: **2**
- Proyectos en otros estados: **9**

### Datos en Datawarehouse
- Total de proyectos: **3** (solo completados y cancelados)
- Total de tareas: **18** (todas las tareas de esos 3 proyectos)

### Proyectos Incluidos en el DW

| ID | Nombre | Estado | Razón |
|----|--------|--------|-------|
| 5 | Proyecto enfoque transicional ergonómico | Cancelado | Proyecto finalizado (cancelado) |
| 10 | Proyecto monitorizar uniforme cara a cara | Cancelado | Proyecto finalizado (cancelado) |
| 12 | Proyecto funcionalidad dedicada intuitivo | Completado | Proyecto finalizado exitosamente |

## 🔄 Comportamiento del ETL

### Cuándo se Carga un Proyecto al DW

1. El proyecto cambia su estado a **Completado** (id_estado = 3)
2. El proyecto cambia su estado a **Cancelado** (id_estado = 4)

### Qué Datos se Cargan

Cuando un proyecto califica:
- ✅ Datos del proyecto (HechoProyecto)
- ✅ **Todas** las tareas del proyecto (HechoTarea) - sin importar su estado individual
- ✅ Dimensiones relacionadas (Cliente, Empleado, Equipo, Tiempo)

### Qué NO se Carga

- ❌ Proyectos en desarrollo activo
- ❌ Proyectos pendientes de iniciar
- ❌ Proyectos en pausa
- ❌ Proyectos en revisión
- ❌ Tareas de proyectos que no están completados/cancelados

## 🎯 Justificación

Esta configuración sigue las mejores prácticas de diseño de datawarehouse:

1. **Datos Históricos**: El DW contiene solo información de proyectos finalizados, permitiendo análisis históricos precisos
2. **Estabilidad**: Los datos no cambian constantemente como en la BD operacional
3. **Análisis de Rendimiento**: Se pueden analizar solo proyectos que tienen métricas completas (inicio y fin reales)
4. **Lecciones Aprendidas**: Tanto proyectos exitosos como cancelados proveen información valiosa para análisis futuros

## 🔧 Modificar el Comportamiento

Si necesitas cambiar qué proyectos se incluyen, edita el archivo:
```
02_ETL/scripts/etl_principal.py
```

Busca las líneas que contienen:
```python
WHERE p.id_estado IN (3, 4)
```

Y modifica los IDs de estado según tus necesidades.

## 📝 Notas Adicionales

- El ETL debe ejecutarse periódicamente para capturar proyectos recién completados/cancelados
- Las dimensiones (Cliente, Empleado, Equipo) siempre se cargan completamente para mantener consistencia
- La dimensión tiempo se crea dinámicamente basada en las fechas de los proyectos incluidos

---

**Última actualización**: 22 de octubre de 2025
**Versión**: 1.0
