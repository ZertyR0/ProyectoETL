# 🔒 GUÍA COMPLETA DE SEGURIDAD - Sistema ETL

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura de Seguridad](#arquitectura-de-seguridad)
3. [Componentes Seguros](#componentes-seguros)
4. [Implementación Paso a Paso](#implementación-paso-a-paso)
5. [Uso del Sistema](#uso-del-sistema)
6. [Auditoría y Monitoreo](#auditoría-y-monitoreo)
7. [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Resumen Ejecutivo

### Problema Original
- ❌ SELECT directos exponían datos sensibles
- ❌ Riesgo de SQL injection
- ❌ Sin control de acceso granular
- ❌ No había auditoría de consultas

### Solución Implementada
- ✅ **100% Stored Procedures**: Todo acceso a datos mediante procedimientos
- ✅ **Triggers Automáticos**: Validación antes de cada INSERT
- ✅ **Auditoría Completa**: Log de todas las operaciones
- ✅ **Vistas Seguras**: Solo datos agregados/no sensibles
- ✅ **Control de Duplicados**: Prevención mediante hash

---

## 🏗️ Arquitectura de Seguridad

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                       │
│  Python Scripts (generar_datos_seguro.py, etl_principal)  │
│                          ↓                                  │
│              Solo llama a Stored Procedures                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE PROCEDIMIENTOS                      │
│  • sp_generar_cliente()    • sp_dw_cargar_cliente()        │
│  • sp_generar_empleado()   • sp_etl_extraer_clientes()     │
│  • sp_validar_integridad() • sp_dw_obtener_metricas()      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE TRIGGERS                          │
│  • trg_cliente_antes_insertar (validación)                 │
│  • trg_empleado_antes_insertar (duplicados)                │
│  • trg_proyecto_antes_insertar (integridad)                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
│  Tablas: Cliente, Empleado, Proyecto, etc.                 │
│  Audit: AuditoriaOperaciones, ControlDuplicados            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Componentes Seguros

### 1. Base de Datos Origen (gestionproyectos_hist)

#### Archivos SQL
- **`01_GestionProyectos/scripts/procedimientos_seguros.sql`**
  - 13 Stored Procedures
  - 5 Triggers
  - 2 Tablas de Auditoría
  - 4 Vistas Seguras

#### Procedimientos Principales

```sql
-- Generación de datos (sin SELECT directos)
sp_generar_cliente()
sp_generar_empleado()
sp_generar_equipo()
sp_generar_proyecto()
sp_generar_tarea()

-- Validación y control
sp_validar_integridad()
sp_verificar_duplicados()

-- Consultas seguras
sp_obtener_resumen()        -- Solo conteos
sp_obtener_metricas()       -- Solo agregados

-- Limpieza
sp_limpiar_datos()
```

#### Triggers de Validación

```sql
-- Antes de cada INSERT, validan:
trg_cliente_antes_insertar
trg_empleado_antes_insertar
trg_equipo_antes_insertar
trg_proyecto_antes_insertar
trg_tarea_antes_insertar

-- Verifican:
• Hash único (no duplicados)
• Integridad referencial
• Formato de datos
• Registran en auditoría
```

#### Tablas de Auditoría

```sql
AuditoriaOperaciones
├── OperacionID (PK)
├── FechaHora
├── TipoOperacion (INSERT/UPDATE/DELETE)
├── Tabla
├── RegistroID
├── Usuario
└── Hash

ControlDuplicados
├── ControlID (PK)
├── TipoEntidad
├── Hash
├── FechaRegistro
└── Estado
```

### 2. DataWarehouse (dw_proyectos_hist)

#### Archivos SQL
- **`04_Datawarehouse/scripts/procedimientos_seguros_dw.sql`**
  - 7 Stored Procedures
  - 2 Vistas Seguras
  - 1 Tabla de Auditoría

#### Procedimientos de Consulta

```sql
-- Solo datos agregados/no sensibles
sp_dw_obtener_conteos()
sp_dw_obtener_metricas()
sp_dw_buscar_proyecto()
sp_dw_buscar_cliente()
sp_dw_validar_migracion()
```

#### Vistas Seguras

```sql
v_dw_resumen
├── Solo conteos por tabla
└── Sin datos identificables

v_dw_metricas_generales
├── Promedios
├── Totales
└── Estadísticas agregadas
```

### 3. Scripts Python Seguros

#### generador_datos_seguro.py

```python
class GeneradorSeguro:
    def generar_cliente(self):
        # ❌ NO hace esto:
        # cursor.execute("INSERT INTO Cliente...")
        
        # ✅ Hace esto:
        cursor.callproc('sp_generar_cliente', params)
    
    # Sin SELECT directos
    # Solo callproc()
```

#### etl_principal_seguro.py

```python
class ETLSeguro:
    def extraer_clientes(self):
        # ❌ NO hace esto:
        # cursor.execute("SELECT * FROM Cliente")
        
        # ✅ Hace esto:
        cursor.callproc('sp_etl_extraer_clientes')
```

#### verificar_trazabilidad_seguro.py

```python
class VerificadorSeguro:
    def verificar_conteos(self):
        # Solo llama a procedimientos
        cursor.callproc('sp_obtener_resumen')
        cursor.callproc('sp_dw_obtener_conteos')
```

### 4. Procedimientos ETL

**`02_ETL/scripts/procedimientos_etl.sql`**

```sql
-- Extracción segura
sp_etl_extraer_clientes()      -- Solo campos necesarios
sp_etl_extraer_empleados()
sp_etl_extraer_proyectos()     -- Solo completados

-- Carga segura
sp_dw_cargar_cliente()
sp_dw_cargar_empleado()
sp_dw_cargar_proyecto()
sp_dw_cargar_hecho_proyecto()

-- Auditoría ETL
sp_etl_registrar_inicio()
sp_etl_registrar_fin()
```

---

## 🚀 Implementación Paso a Paso

### Paso 1: Crear Procedimientos en BD Origen

```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar procedimientos seguros
source 01_GestionProyectos/scripts/procedimientos_seguros.sql
```

Verificar:
```sql
USE gestionproyectos_hist;
SHOW PROCEDURE STATUS WHERE Db = 'gestionproyectos_hist';
SHOW TRIGGERS;
```

### Paso 2: Crear Procedimientos ETL

```bash
mysql -u root -p < 02_ETL/scripts/procedimientos_etl.sql
```

Verificar:
```sql
-- En gestionproyectos_hist
SHOW PROCEDURE STATUS WHERE Name LIKE 'sp_etl_%';

-- En dw_proyectos_hist
SHOW PROCEDURE STATUS WHERE Name LIKE 'sp_dw_%';
```

### Paso 3: Crear Procedimientos DW

```bash
mysql -u root -p < 04_Datawarehouse/scripts/procedimientos_seguros_dw.sql
```

### Paso 4: Generar Datos de Forma Segura

```bash
python3 01_GestionProyectos/scripts/generar_datos_seguro.py

# Opciones:
# --clientes N    : Número de clientes
# --empleados N   : Número de empleados
# --proyectos N   : Número de proyectos
```

Ejemplo:
```bash
python3 generar_datos_seguro.py --clientes 100 --empleados 50 --proyectos 30
```

### Paso 5: Ejecutar ETL Seguro

```bash
# Modo incremental
python3 02_ETL/scripts/etl_principal_seguro.py

# Modo limpieza completa
python3 02_ETL/scripts/etl_principal_seguro.py --limpiar
```

### Paso 6: Verificar Trazabilidad

```bash
# Modo interactivo
python3 verificar_trazabilidad_seguro.py

# Comandos directos
python3 verificar_trazabilidad_seguro.py reporte
python3 verificar_trazabilidad_seguro.py conteos
python3 verificar_trazabilidad_seguro.py duplicados
```

---

## 💻 Uso del Sistema

### Generar Datos

```bash
# Dataset pequeño (pruebas)
python3 generar_datos_seguro.py --clientes 10 --empleados 5 --proyectos 3

# Dataset mediano (desarrollo)
python3 generar_datos_seguro.py --clientes 100 --empleados 50 --proyectos 30

# Dataset grande (producción simulada)
python3 generar_datos_seguro.py --clientes 1000 --empleados 500 --proyectos 200
```

### Ejecutar ETL

```bash
# Primera vez (con limpieza)
python3 etl_principal_seguro.py --limpiar

# Ejecuciones siguientes (incremental)
python3 etl_principal_seguro.py
```

### Verificar Resultados

```python
# Opción 1: Menú interactivo
python3 verificar_trazabilidad_seguro.py

# Opción 2: Comandos directos
python3 verificar_trazabilidad_seguro.py reporte
```

### Consultar desde MySQL (Seguro)

```sql
-- ✅ PERMITIDO: Usar procedimientos
CALL sp_obtener_resumen();
CALL sp_dw_obtener_metricas();
CALL sp_dw_buscar_proyecto(1);

-- ✅ PERMITIDO: Usar vistas
SELECT * FROM v_dw_resumen;
SELECT * FROM v_dw_metricas_generales;

-- ❌ NO HACER: SELECT directos (solo con permisos admin)
SELECT * FROM Cliente;  -- Solo para administradores
```

---

## 📊 Auditoría y Monitoreo

### Verificar Auditoría de Operaciones

```sql
USE gestionproyectos_hist;

-- Ver últimas operaciones
SELECT * FROM AuditoriaOperaciones 
ORDER BY FechaHora DESC 
LIMIT 20;

-- Operaciones por tipo
SELECT TipoOperacion, COUNT(*) as Total
FROM AuditoriaOperaciones
GROUP BY TipoOperacion;

-- Operaciones por tabla
SELECT Tabla, COUNT(*) as Total
FROM AuditoriaOperaciones
GROUP BY Tabla
ORDER BY Total DESC;
```

### Verificar Control de Duplicados

```sql
-- Ver intentos de duplicados
SELECT * FROM ControlDuplicados
WHERE Estado = 'RECHAZADO'
ORDER BY FechaRegistro DESC;

-- Duplicados por entidad
SELECT TipoEntidad, COUNT(*) as Intentos
FROM ControlDuplicados
WHERE Estado = 'RECHAZADO'
GROUP BY TipoEntidad;
```

### Verificar Auditoría ETL

```sql
-- Ver últimas ejecuciones ETL
SELECT * FROM AuditoriaETL
ORDER BY FechaHora DESC
LIMIT 10;

-- Estadísticas ETL
SELECT 
    DATE(FechaHora) as Fecha,
    Operacion,
    SUM(RegistrosProcesados) as Total,
    COUNT(*) as Ejecuciones
FROM AuditoriaETL
WHERE Estado = 'EXITOSO'
GROUP BY DATE(FechaHora), Operacion;
```

### Verificar Auditoría de Consultas (DW)

```sql
USE dw_proyectos_hist;

-- Ver consultas recientes
SELECT * FROM AuditoriaConsultas
ORDER BY FechaHora DESC
LIMIT 20;

-- Consultas más usadas
SELECT Procedimiento, COUNT(*) as Usos
FROM AuditoriaConsultas
GROUP BY Procedimiento
ORDER BY Usos DESC;
```

---

## 🛡️ Mejores Prácticas

### 1. Configuración de Usuarios (Producción)

```sql
-- Usuario para ETL (solo ejecutar procedimientos)
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'etl_secure_pass_2024';

-- Permisos mínimos en BD Origen
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_etl_extraer_clientes TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_etl_extraer_empleados TO 'etl_user'@'localhost';
-- (etc. para cada procedimiento necesario)

-- Permisos en DW
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_cargar_cliente TO 'etl_user'@'localhost';
-- (etc.)

-- Usuario de solo lectura (reportes)
CREATE USER 'dw_readonly'@'localhost' IDENTIFIED BY 'readonly_pass_2024';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_obtener_metricas TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_obtener_conteos TO 'dw_readonly'@'localhost';
GRANT SELECT ON dw_proyectos_hist.v_dw_resumen TO 'dw_readonly'@'localhost';
GRANT SELECT ON dw_proyectos_hist.v_dw_metricas_generales TO 'dw_readonly'@'localhost';

FLUSH PRIVILEGES;
```

### 2. Conexiones en Python (Producción)

```python
# Usar usuarios limitados
conn = mysql.connector.connect(
    host='localhost',
    user='etl_user',         # NO usar 'root'
    password='etl_secure_pass_2024',
    database='gestionproyectos_hist'
)
```

### 3. Variables de Entorno

```bash
# Crear .env
DB_HOST=localhost
DB_USER=etl_user
DB_PASS=etl_secure_pass_2024
DB_NAME=gestionproyectos_hist

# En Python
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS'),
    database=os.getenv('DB_NAME')
)
```

### 4. Monitoreo Regular

```bash
# Crear script de monitoreo diario
#!/bin/bash
# monitor_seguridad.sh

echo "=== Auditoría Diaria $(date) ===" >> audit_log.txt

mysql -u root -p -e "
SELECT COUNT(*) as OperacionesHoy 
FROM gestionproyectos_hist.AuditoriaOperaciones 
WHERE DATE(FechaHora) = CURDATE()
" >> audit_log.txt

mysql -u root -p -e "
SELECT COUNT(*) as DuplicadosRechazados
FROM gestionproyectos_hist.ControlDuplicados
WHERE Estado = 'RECHAZADO' 
AND DATE(FechaRegistro) = CURDATE()
" >> audit_log.txt
```

### 5. Respaldos Regulares

```bash
# Backup de procedimientos
mysqldump -u root -p --routines --no-data gestionproyectos_hist > backup_procedures_$(date +%Y%m%d).sql

# Backup de auditoría
mysqldump -u root -p gestionproyectos_hist AuditoriaOperaciones ControlDuplicados > backup_audit_$(date +%Y%m%d).sql
```

---

## 🚨 Troubleshooting

### Problema: "Access Denied"

```sql
-- Verificar permisos
SHOW GRANTS FOR 'etl_user'@'localhost';

-- Otorgar permisos faltantes
GRANT EXECUTE ON PROCEDURE nombre_procedimiento TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
```

### Problema: "Procedure does not exist"

```sql
-- Listar procedimientos existentes
SHOW PROCEDURE STATUS WHERE Db = 'gestionproyectos_hist';

-- Re-crear si es necesario
source 01_GestionProyectos/scripts/procedimientos_seguros.sql
```

### Problema: Python no encuentra procedimientos

```python
# Verificar que los procedimientos existan
cursor = conn.cursor()
cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (database,))
procs = cursor.fetchall()
for proc in procs:
    print(proc)
```

---

## ✅ Checklist de Seguridad

- [ ] Procedimientos almacenados creados en BD Origen
- [ ] Procedimientos ETL creados
- [ ] Procedimientos DW creados
- [ ] Triggers de validación activos
- [ ] Tablas de auditoría existentes
- [ ] Scripts Python usan solo `callproc()`
- [ ] NO hay `cursor.execute("SELECT ...")` en código
- [ ] Usuarios limitados creados (producción)
- [ ] Contraseñas en variables de entorno
- [ ] Sistema de monitoreo configurado
- [ ] Respaldos automáticos activos

---

## 📚 Referencias

- **Procedimientos Origen**: `01_GestionProyectos/scripts/procedimientos_seguros.sql`
- **Procedimientos ETL**: `02_ETL/scripts/procedimientos_etl.sql`
- **Procedimientos DW**: `04_Datawarehouse/scripts/procedimientos_seguros_dw.sql`
- **Generador Seguro**: `generar_datos_seguro.py`
- **ETL Seguro**: `02_ETL/scripts/etl_principal_seguro.py`
- **Verificador Seguro**: `verificar_trazabilidad_seguro.py`

---

## 🔐 Resumen de Seguridad

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Acceso a Datos** | SELECT directo | Solo procedimientos |
| **Inserción** | INSERT directo | Solo procedimientos + triggers |
| **Validación** | En Python | En triggers MySQL |
| **Auditoría** | No existe | 3 tablas de auditoría |
| **Duplicados** | Sin control | Hash + triggers |
| **SQL Injection** | Vulnerable | Protegido |
| **Permisos** | Admin para todo | Granulares por procedimiento |

---

**🎯 Objetivo Cumplido**: Sistema 100% seguro sin SELECT/INSERT directos, con auditoría completa y prevención de filtración de datos.
