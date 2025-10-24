# 🔍 Documentación de Trazabilidad

## 📋 Índice de Documentos de Trazabilidad

Esta carpeta contiene toda la documentación relacionada con el sistema de trazabilidad y auditoría.

---

## 📚 Documentos Disponibles

| Documento | Descripción | Nivel |
|-----------|-------------|-------|
| [GUIA_TRAZABILIDAD.md](GUIA_TRAZABILIDAD.md) | Guía completa de trazabilidad | ⭐⭐⭐ Avanzado |
| [INICIO_RAPIDO_TRAZABILIDAD.md](INICIO_RAPIDO_TRAZABILIDAD.md) | Inicio rápido de trazabilidad | ⭐ Básico |
| [README_TRAZABILIDAD.md](README_TRAZABILIDAD.md) | README de trazabilidad | ⭐⭐ Intermedio |
| [INDICE_ARCHIVOS_TRAZABILIDAD.md](INDICE_ARCHIVOS_TRAZABILIDAD.md) | Índice de archivos | ⭐ Básico |
| [DIAGRAMA_FLUJO_TRAZABILIDAD.md](DIAGRAMA_FLUJO_TRAZABILIDAD.md) | Diagrama de flujo | ⭐⭐ Intermedio |
| [RESUMEN_MEJORAS_TRAZABILIDAD.md](RESUMEN_MEJORAS_TRAZABILIDAD.md) | Resumen de mejoras | ⭐ Básico |

---

## 🎯 Sistema de Trazabilidad

### Características Principales

- ✅ **Auditoría Automática**: Triggers que registran todas las operaciones
- ✅ **Logs Detallados**: Registro completo de cambios
- ✅ **Rastreo de Datos**: Seguimiento desde origen hasta DW
- ✅ **Reportes**: Consultas de auditoría predefinidas
- ✅ **Verificación**: Scripts de verificación automática

### Qué se Rastrea

1. **Base de Datos Origen**
   - Inserciones, actualizaciones, eliminaciones
   - Usuario y timestamp
   - Valores antes/después

2. **Proceso ETL**
   - Ejecuciones del ETL
   - Registros procesados
   - Errores y warnings
   - Tiempo de ejecución

3. **Data Warehouse**
   - Cargas de datos
   - Transformaciones aplicadas
   - Datos insertados/actualizados

---

## 🚀 Inicio Rápido

### Para Usuarios

1. Lee [INICIO_RAPIDO_TRAZABILIDAD.md](INICIO_RAPIDO_TRAZABILIDAD.md)
2. Usa el dashboard para ver logs
3. Revisa reportes de auditoría

### Para Desarrolladores

1. Lee [GUIA_TRAZABILIDAD.md](GUIA_TRAZABILIDAD.md)
2. Revisa [DIAGRAMA_FLUJO_TRAZABILIDAD.md](DIAGRAMA_FLUJO_TRAZABILIDAD.md)
3. Implementa auditoría en nuevos procesos

### Para Administradores

1. Implementa triggers de auditoría
2. Configura tablas de logs
3. Programa reportes de auditoría

---

## 📖 Guías Relacionadas

- [Documentación Principal](../README.md)
- [Guía de Seguridad](../seguridad/README.md)
- [01_GestionProyectos README](../../01_GestionProyectos/README.md)
- [02_ETL README](../../02_ETL/README.md)

---

## 🔍 Verificación de Trazabilidad

### Script de Verificación

```bash
# Ejecutar verificación completa
python verificar_trazabilidad_seguro.py
```

### Consultas de Auditoría

```sql
-- Ver últimos cambios en proyectos
SELECT * FROM AuditoriaProyectos 
ORDER BY FechaHora DESC 
LIMIT 20;

-- Ver operaciones por usuario
SELECT Usuario, Operacion, COUNT(*) as Total
FROM AuditoriaProyectos
GROUP BY Usuario, Operacion;

-- Ver cambios en las últimas 24 horas
SELECT * FROM AuditoriaProyectos 
WHERE FechaHora >= NOW() - INTERVAL 24 HOUR
ORDER BY FechaHora DESC;
```

### Verificar Ejecuciones ETL

```sql
-- Ver ejecuciones ETL
SELECT * FROM AuditoriaETL 
ORDER BY FechaEjecucion DESC 
LIMIT 10;

-- Estadísticas de ETL
SELECT 
    DATE(FechaEjecucion) as Fecha,
    COUNT(*) as Ejecuciones,
    SUM(RegistrosProcesados) as TotalRegistros
FROM AuditoriaETL
GROUP BY DATE(FechaEjecucion);
```

---

## 📊 Tablas de Trazabilidad

### Base de Datos Origen

| Tabla | Descripción |
|-------|-------------|
| **AuditoriaProyectos** | Cambios en proyectos |
| **AuditoriaEmpleados** | Cambios en empleados |
| **AuditoriaClientes** | Cambios en clientes |
| **AuditoriaTareas** | Cambios en tareas |

### Estructura de Tabla de Auditoría

```sql
CREATE TABLE AuditoriaProyectos (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    IdProyecto INT,
    Operacion VARCHAR(10),      -- INSERT, UPDATE, DELETE
    Usuario VARCHAR(100),
    FechaHora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DatosAnteriores JSON,       -- Valores antes del cambio
    DatosNuevos JSON           -- Valores después del cambio
);
```

### Data Warehouse

| Tabla | Descripción |
|-------|-------------|
| **AuditoriaETL** | Ejecuciones del ETL |
| **AuditoriaCargas** | Cargas de datos |
| **LogTransformaciones** | Transformaciones aplicadas |

---

## 🛠️ Scripts de Trazabilidad

| Script | Ubicación | Descripción |
|--------|-----------|-------------|
| `verificar_trazabilidad_seguro.py` | Raíz | Verificador completo |
| `demo_trazabilidad.sh` | Raíz | Demostración de trazabilidad |
| `consultas_trazabilidad.sql` | `04_Datawarehouse/scripts/` | Consultas de auditoría |

---

## 📈 Reportes de Trazabilidad

### Reporte de Actividad

```sql
-- Actividad por tabla
SELECT 
    'Proyectos' as Tabla,
    COUNT(*) as TotalOperaciones
FROM AuditoriaProyectos
UNION ALL
SELECT 
    'Empleados',
    COUNT(*)
FROM AuditoriaEmpleados;
```

### Reporte de Cambios Recientes

```sql
-- Cambios en las últimas 24 horas
SELECT 
    Operacion,
    COUNT(*) as Total,
    MIN(FechaHora) as PrimerCambio,
    MAX(FechaHora) as UltimoCambio
FROM AuditoriaProyectos
WHERE FechaHora >= NOW() - INTERVAL 24 HOUR
GROUP BY Operacion;
```

### Reporte de Usuarios Activos

```sql
-- Usuarios más activos
SELECT 
    Usuario,
    COUNT(*) as TotalOperaciones,
    MAX(FechaHora) as UltimaActividad
FROM AuditoriaProyectos
GROUP BY Usuario
ORDER BY TotalOperaciones DESC
LIMIT 10;
```

---

## 🔄 Flujo de Trazabilidad

```
┌─────────────────────┐
│   Operación en BD   │ (INSERT/UPDATE/DELETE)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Trigger Dispara   │ (AFTER INSERT/UPDATE/DELETE)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Inserta en Tabla   │ (AuditoriaProyectos)
│     de Auditoría    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Registro con:      │
│  - Operación        │
│  - Usuario          │
│  - Timestamp        │
│  - Datos Anteriores │
│  - Datos Nuevos     │
└─────────────────────┘
```

---

## 📱 Dashboard de Trazabilidad

### Sección de Auditoría

El dashboard incluye:
- 📊 Gráfico de operaciones por tipo
- 📈 Línea de tiempo de cambios
- 🔍 Búsqueda de auditoría por fecha/usuario
- 📋 Tabla de últimos cambios
- 🎯 Estadísticas de trazabilidad

### Acceso

```
http://localhost:8080/index.html#auditoria
```

---

## 🔒 Seguridad de Logs

### Protección de Tablas de Auditoría

```sql
-- Solo lectura para usuarios normales
GRANT SELECT ON AuditoriaProyectos TO 'usuario'@'localhost';

-- Solo admin puede modificar
GRANT ALL ON AuditoriaProyectos TO 'admin'@'localhost';
```

### Backup de Logs

```bash
# Backup solo de auditoría
mysqldump -u root -p gestionproyectos_hist \
  AuditoriaProyectos \
  AuditoriaEmpleados \
  AuditoriaClientes \
  > backup_auditoria.sql
```

---

## 🐛 Solución de Problemas

### No se registran cambios

```sql
-- Verificar que los triggers existan
SHOW TRIGGERS FROM gestionproyectos_hist;

-- Si no existen, crearlos
SOURCE 01_GestionProyectos/scripts/procedimientos_seguros.sql;
```

### Tabla de auditoría llena

```sql
-- Archivar registros antiguos
CREATE TABLE AuditoriaProyectos_archivo AS
SELECT * FROM AuditoriaProyectos
WHERE FechaHora < NOW() - INTERVAL 1 YEAR;

-- Limpiar registros archivados
DELETE FROM AuditoriaProyectos
WHERE FechaHora < NOW() - INTERVAL 1 YEAR;
```

### Verificar integridad

```bash
# Ejecutar verificación
python verificar_trazabilidad_seguro.py

# Ver resultados
cat verificacion_trazabilidad.log
```

---

## 📞 Soporte

Para problemas de trazabilidad:
1. Revisa [GUIA_TRAZABILIDAD.md](GUIA_TRAZABILIDAD.md)
2. Ejecuta `verificar_trazabilidad_seguro.py`
3. Revisa logs de auditoría
4. Contacta al equipo de desarrollo

---

**Volver a Documentación Principal**: [../README.md](../README.md)  
**Ver Seguridad**: [../seguridad/README.md](../seguridad/README.md)
