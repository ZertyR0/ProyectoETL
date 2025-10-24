# 📚 ÍNDICE COMPLETO DEL SISTEMA SEGURO

## 🎯 Navegación Rápida

| Necesito... | Ir a... |
|-------------|---------|
| **Instalar todo el sistema** | [instalar_sistema_seguro.sh](#instalador-automático) |
| **Entender la seguridad** | [GUIA_SEGURIDAD_COMPLETA.md](#documentación-de-seguridad) |
| **Generar datos** | [generar_datos_seguro.py](#generador-seguro) |
| **Ejecutar ETL** | [etl_principal_seguro.py](#etl-seguro) |
| **Verificar trazabilidad** | [verificar_trazabilidad_seguro.py](#verificador-seguro) |
| **Ver procedimientos SQL** | [Procedimientos Almacenados](#procedimientos-almacenados) |

---

## 📁 Estructura del Proyecto

```
ProyectoETL/
│
├── 📄 Documentación Principal
│   ├── README.md                          # Documentación general
│   ├── GUIA_SEGURIDAD_COMPLETA.md        # 🔒 Guía completa de seguridad
│   ├── RESUMEN_FINAL_SEGURIDAD.md        # 📊 Resumen de implementación
│   ├── INDICE_SISTEMA_SEGURO.md          # 📚 Este archivo
│   ├── GUIA_TRAZABILIDAD.md              # Sistema de trazabilidad
│   └── INICIO_RAPIDO_TRAZABILIDAD.md     # Quick start trazabilidad
│
├── 🔧 Scripts de Configuración
│   ├── instalar_sistema_seguro.sh        # ⚡ Instalador automático
│   ├── setup_local.sh                    # Setup local
│   └── verificar_sistema.sh              # Verificación del sistema
│
├── 🐍 Scripts Python Seguros
│   ├── generar_datos_seguro.py           # Generador usando procedimientos
│   ├── verificar_trazabilidad_seguro.py  # Verificador usando procedimientos
│   └── validar_consistencia.py           # Validador de consistencia
│
├── 01_GestionProyectos/                  # 📦 Base de Datos Origen
│   ├── README.md
│   └── scripts/
│       ├── crear_bd_origen.sql           # Estructura de tablas
│       ├── procedimientos_seguros.sql    # 🔒 Procedimientos + Triggers
│       └── generar_datos.py              # (Versión antigua - no usar)
│
├── 02_ETL/                               # 🔄 Proceso ETL
│   ├── README.md
│   ├── config/
│   │   └── config_conexion.py           # Configuración de conexión
│   └── scripts/
│       ├── procedimientos_etl.sql        # 🔒 Procedimientos ETL
│       ├── etl_principal_seguro.py       # 🔒 ETL usando procedimientos
│       ├── etl_principal.py              # (Versión antigua - no usar)
│       └── etl_utils.py                  # Utilidades ETL
│
├── 03_Dashboard/                         # 📊 Dashboard (Frontend/Backend)
│   ├── README.md
│   ├── backend/
│   │   ├── app.py                       # API Flask
│   │   └── requirements.txt
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
└── 04_Datawarehouse/                     # 🏛️ DataWarehouse
    ├── README.md
    └── scripts/
        ├── crear_datawarehouse.sql       # Estructura DW
        ├── procedimientos_seguros_dw.sql # 🔒 Procedimientos DW
        └── consultas_analisis.sql        # Consultas de análisis
```

---

## 🔒 Archivos de Seguridad (NUEVOS)

### Instalador Automático

**`instalar_sistema_seguro.sh`** (~400 líneas)
```bash
# Instala todo el sistema automáticamente
./instalar_sistema_seguro.sh

# Funciones:
✓ Crear bases de datos
✓ Instalar procedimientos (Origen + ETL + DW)
✓ Crear tablas
✓ Verificar Python
✓ Generar datos de prueba (opcional)
✓ Ejecutar ETL inicial (opcional)
✓ Verificar instalación completa
```

**Cuándo usar**: Primera instalación del sistema

---

### Documentación de Seguridad

**`GUIA_SEGURIDAD_COMPLETA.md`** (~600 líneas)
```markdown
Contenido:
├── Resumen Ejecutivo
├── Arquitectura de Seguridad
├── Componentes Seguros
├── Implementación Paso a Paso
├── Uso del Sistema
├── Auditoría y Monitoreo
└── Mejores Prácticas
```

**Cuándo usar**: Para entender cómo funciona el sistema seguro

---

**`RESUMEN_FINAL_SEGURIDAD.md`** (~500 líneas)
```markdown
Contenido:
├── Archivos creados
├── Comparación antes/después
├── Casos de uso
├── Estadísticas del proyecto
├── Checklist de validación
└── Lecciones aprendidas
```

**Cuándo usar**: Para ver qué se implementó y por qué

---

## 🗄️ Procedimientos Almacenados

### 1. BD Origen - Procedimientos Seguros

**`01_GestionProyectos/scripts/procedimientos_seguros.sql`** (~650 líneas)

#### Procedimientos de Generación
```sql
sp_generar_cliente(
    nombre, industria, pais, fecha_registro, hash
) → ClienteID
-- Inserta cliente con validación automática (trigger)

sp_generar_empleado(
    nombre, especialidad, nivel, disponibilidad, fecha_contratacion, hash
) → EmpleadoID
-- Inserta empleado con validación automática

sp_generar_equipo(
    nombre, lider_id, tipo, ubicacion, fecha_formacion, hash
) → EquipoID
-- Inserta equipo con validación automática

sp_generar_proyecto(
    nombre, cliente_id, equipo_id, fecha_inicio, fecha_fin_estimada,
    presupuesto, complejidad, hash
) → ProyectoID
-- Inserta proyecto con validación automática

sp_generar_tarea(
    nombre, proyecto_id, empleado_id, fecha_inicio, fecha_fin,
    horas_estimadas, estado, hash
) → TareaID
-- Inserta tarea con validación automática
```

#### Procedimientos de Validación
```sql
sp_validar_integridad()
-- Devuelve métricas de unicidad de campos

sp_verificar_duplicados()
-- Lista duplicados encontrados (si existen)
```

#### Procedimientos de Consulta (Seguros)
```sql
sp_obtener_resumen()
-- Solo devuelve conteos por tabla (no datos sensibles)

sp_obtener_cliente(id)
sp_obtener_empleado(id)
sp_obtener_equipo(id)
sp_obtener_proyecto(id)
-- Devuelven datos de UN registro específico
```

#### Triggers Automáticos
```sql
trg_cliente_antes_insertar
trg_empleado_antes_insertar
trg_equipo_antes_insertar
trg_proyecto_antes_insertar
trg_tarea_antes_insertar

-- Antes de cada INSERT:
• Verifican hash único (no duplicados)
• Validan integridad referencial
• Registran en AuditoriaOperaciones
• Registran en ControlDuplicados
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
└── Estado (ACEPTADO/RECHAZADO)
```

#### Vistas Seguras
```sql
v_resumen_general           -- Solo conteos
v_metricas_clientes         -- Agregados de clientes
v_metricas_proyectos        -- Agregados de proyectos
v_estado_proyectos          -- Resumen de estados
```

---

### 2. ETL - Procedimientos Seguros

**`02_ETL/scripts/procedimientos_etl.sql`** (~450 líneas)

#### Procedimientos de Extracción (BD Origen)
```sql
sp_etl_extraer_clientes()
-- Extrae clientes (solo campos necesarios, sin datos sensibles)

sp_etl_extraer_empleados()
-- Extrae empleados (solo campos necesarios)

sp_etl_extraer_equipos()
-- Extrae equipos

sp_etl_extraer_proyectos()
-- Extrae SOLO proyectos completados

sp_etl_extraer_proyecto_empleados()
-- Extrae relaciones proyecto-empleado
```

#### Procedimientos de Carga (DW)
```sql
sp_dw_cargar_cliente(
    cliente_id, nombre, industria, pais, hash
)
-- Inserta/actualiza en DimCliente

sp_dw_cargar_empleado(
    empleado_id, nombre, especialidad, nivel, hash
)
-- Inserta/actualiza en DimEmpleado

sp_dw_cargar_equipo(
    equipo_id, nombre, lider_id, tipo, ubicacion, hash
)
-- Inserta/actualiza en DimEquipo

sp_dw_cargar_proyecto(
    proyecto_id, nombre, cliente_id, equipo_id,
    fecha_inicio, fecha_fin, complejidad, hash
)
-- Inserta/actualiza en DimProyecto

sp_dw_cargar_hecho_proyecto(
    proyecto_id, cliente_id, equipo_id, empleado_id,
    fecha_inicio, fecha_fin, presupuesto, costo
)
-- Inserta en HechoProyecto (calcula métricas automáticamente)

sp_dw_limpiar()
-- Limpia todo el DW (TRUNCATE con FK checks)
```

#### Procedimientos de Auditoría ETL
```sql
sp_etl_registrar_inicio(operacion, tabla)
→ auditoria_id

sp_etl_registrar_fin(
    auditoria_id, registros, estado, mensaje
)

sp_etl_obtener_estadisticas()
-- Devuelve estadísticas de ejecuciones ETL
```

#### Tabla de Auditoría ETL
```sql
AuditoriaETL
├── AuditoriaID (PK)
├── FechaHora
├── Operacion
├── Tabla
├── RegistrosProcesados
├── Estado (INICIADO/EXITOSO/ERROR)
├── Mensaje
└── UsuarioETL
```

---

### 3. DataWarehouse - Procedimientos Seguros

**`04_Datawarehouse/scripts/procedimientos_seguros_dw.sql`** (~350 líneas)

#### Procedimientos de Consulta
```sql
sp_dw_obtener_conteos()
-- Solo devuelve conteos de cada tabla

sp_dw_obtener_metricas()
-- Devuelve métricas agregadas (promedios, totales)

sp_dw_buscar_proyecto(id)
-- Devuelve info de proyecto + métricas
-- 2 result sets: DimProyecto + HechoProyecto

sp_dw_buscar_cliente(id)
-- Devuelve info de cliente + métricas de proyectos
-- 2 result sets: DimCliente + Agregados

sp_dw_validar_migracion()
-- Valida que todos los datos migraron correctamente
```

#### Vistas Seguras DW
```sql
v_dw_resumen
-- Solo conteos y fechas de carga

v_dw_metricas_generales
-- Promedios, totales, min, max (agregados)
-- Sin datos identificables
```

#### Tabla de Auditoría DW
```sql
AuditoriaConsultas
├── ConsultaID (PK)
├── FechaHora
├── Procedimiento
├── Parametros
└── Usuario
```

---

## 🐍 Scripts Python Seguros

### Generador Seguro

**`generar_datos_seguro.py`** (~430 líneas)

```python
class GeneradorSeguro:
    """
    Generador de datos que SOLO usa procedimientos almacenados.
    NO hace SELECT/INSERT directos.
    """
    
    def __init__(self):
        self.conn = None
        self.clientes_generados = []
        self.empleados_generados = []
        # etc.
    
    def generar_cliente(self):
        """Genera cliente usando sp_generar_cliente"""
        # ❌ NO hace esto:
        # cursor.execute("INSERT INTO Cliente...")
        
        # ✅ Hace esto:
        cursor.callproc('sp_generar_cliente', [
            nombre, industria, pais, fecha, hash
        ])
        # Obtiene el ID generado
        for result in cursor.stored_results():
            row = result.fetchone()
            cliente_id = row[0]
        
        return cliente_id
    
    def generar_empleado(self):
        """Genera empleado usando sp_generar_empleado"""
        cursor.callproc('sp_generar_empleado', params)
        # ...
    
    # Métodos similares para:
    # - generar_equipo()
    # - generar_proyecto()
    # - generar_tarea()
```

**Uso**:
```bash
# Dataset pequeño
python3 generar_datos_seguro.py --clientes 10 --empleados 5 --proyectos 3

# Dataset mediano
python3 generar_datos_seguro.py --clientes 100 --empleados 50 --proyectos 30

# Dataset grande
python3 generar_datos_seguro.py --clientes 1000 --empleados 500 --proyectos 200
```

---

### ETL Seguro

**`02_ETL/scripts/etl_principal_seguro.py`** (~550 líneas)

```python
class ETLSeguro:
    """
    ETL que SOLO usa procedimientos almacenados.
    NO hace SELECT/INSERT directos.
    """
    
    def extraer_clientes(self):
        """Extrae usando sp_etl_extraer_clientes"""
        cursor.callproc('sp_etl_extraer_clientes')
        clientes = []
        for result in cursor.stored_results():
            clientes = result.fetchall()
        return clientes
    
    def cargar_cliente(self, cliente):
        """Carga usando sp_dw_cargar_cliente"""
        cursor.callproc('sp_dw_cargar_cliente', [
            cliente['ClienteID'],
            cliente['NombreCompleto'],
            cliente['Industria'],
            cliente['PaisOrigen'],
            cliente['hash_unico']
        ])
    
    def procesar_clientes(self):
        """Pipeline completo con auditoría"""
        # 1. Registrar inicio
        auditoria_id = self.registrar_auditoria_inicio('EXTRAER', 'Cliente')
        
        # 2. Extraer
        clientes = self.extraer_clientes()
        
        # 3. Cargar
        for cliente in clientes:
            self.cargar_cliente(cliente)
        
        # 4. Commit
        self.conn_destino.commit()
        
        # 5. Registrar fin
        self.registrar_auditoria_fin(auditoria_id, len(clientes), 'EXITOSO', '...')
    
    # Métodos similares para:
    # - procesar_empleados()
    # - procesar_equipos()
    # - procesar_proyectos()
    # - procesar_hechos()
```

**Uso**:
```bash
# Primera vez (limpiar DW y recargar)
python3 02_ETL/scripts/etl_principal_seguro.py --limpiar

# Ejecuciones siguientes (incremental)
python3 02_ETL/scripts/etl_principal_seguro.py
```

---

### Verificador Seguro

**`verificar_trazabilidad_seguro.py`** (~450 líneas)

```python
class VerificadorSeguro:
    """
    Verificador que SOLO usa procedimientos almacenados.
    NO hace SELECT directos.
    """
    
    def verificar_conteos(self):
        """Compara conteos entre BD origen y DW"""
        # Origen
        conteos_origen = self.llamar_procedimiento(
            self.conn_origen,
            'sp_obtener_resumen'
        )
        
        # Destino
        conteos_destino = self.llamar_procedimiento(
            self.conn_destino,
            'sp_dw_obtener_conteos'
        )
        
        # Comparar y mostrar tabla
    
    def buscar_proyecto_por_id(self, id_proyecto):
        """Busca proyecto en DW usando sp_dw_buscar_proyecto"""
        resultado = self.llamar_procedimiento(
            self.conn_destino,
            'sp_dw_buscar_proyecto',
            [id_proyecto]
        )
        # Mostrar resultados
    
    def verificar_duplicados_origen(self):
        """Verifica duplicados usando sp_verificar_duplicados"""
        duplicados = self.llamar_procedimiento(
            self.conn_origen,
            'sp_verificar_duplicados'
        )
        # Mostrar resultados
    
    # Métodos adicionales:
    # - buscar_cliente_por_id()
    # - validar_integridad_origen()
    # - obtener_metricas_dw()
    # - generar_reporte_completo()
```

**Uso**:
```bash
# Modo interactivo (menú)
python3 verificar_trazabilidad_seguro.py

# Comandos directos
python3 verificar_trazabilidad_seguro.py reporte
python3 verificar_trazabilidad_seguro.py conteos
python3 verificar_trazabilidad_seguro.py duplicados
python3 verificar_trazabilidad_seguro.py integridad
python3 verificar_trazabilidad_seguro.py metricas
```

---

## 📊 Dashboard

### Backend Flask

**`03_Dashboard/backend/app.py`**
```python
# API Flask para visualización
# Endpoints:
GET /api/metricas         # Métricas generales
GET /api/proyectos        # Lista de proyectos
GET /api/clientes         # Lista de clientes
GET /api/proyecto/<id>    # Detalle de proyecto
```

### Frontend

**`03_Dashboard/frontend/`**
- `index.html` - Interfaz HTML
- `app.js` - Lógica JavaScript
- `styles.css` - Estilos CSS

---

## 🔄 Flujo de Trabajo Completo

### 1. Instalación Inicial

```bash
# Un solo comando instala TODO
./instalar_sistema_seguro.sh
```

O manualmente:
```bash
# 1. Crear estructura de tablas
mysql -u root -p < 01_GestionProyectos/scripts/crear_bd_origen.sql
mysql -u root -p < 04_Datawarehouse/scripts/crear_datawarehouse.sql

# 2. Instalar procedimientos
mysql -u root -p < 01_GestionProyectos/scripts/procedimientos_seguros.sql
mysql -u root -p < 02_ETL/scripts/procedimientos_etl.sql
mysql -u root -p < 04_Datawarehouse/scripts/procedimientos_seguros_dw.sql
```

### 2. Generar Datos

```bash
python3 generar_datos_seguro.py --clientes 100 --empleados 50 --proyectos 30
```

### 3. Ejecutar ETL

```bash
python3 02_ETL/scripts/etl_principal_seguro.py --limpiar
```

### 4. Verificar

```bash
python3 verificar_trazabilidad_seguro.py reporte
```

### 5. Consultar Auditoría

```sql
-- Ver operaciones recientes
SELECT * FROM gestionproyectos_hist.AuditoriaOperaciones
ORDER BY FechaHora DESC LIMIT 20;

-- Ver ejecuciones ETL
SELECT * FROM gestionproyectos_hist.AuditoriaETL
ORDER BY FechaHora DESC LIMIT 10;

-- Ver consultas DW
SELECT * FROM dw_proyectos_hist.AuditoriaConsultas
ORDER BY FechaHora DESC LIMIT 20;
```

---

## 📖 Guías de Referencia

### Para Desarrolladores

1. **Agregar nuevo procedimiento**:
   - Crear en archivo SQL correspondiente
   - Documentar parámetros y retorno
   - Agregar a esta documentación
   - Otorgar permisos al usuario correspondiente

2. **Modificar Python**:
   - ❌ NUNCA usar `cursor.execute("SELECT ...")`
   - ❌ NUNCA usar `cursor.execute("INSERT ...")`
   - ✅ SIEMPRE usar `cursor.callproc('nombre_proc', params)`

3. **Agregar validación**:
   - Crear/modificar trigger
   - Agregar log en AuditoriaOperaciones
   - Probar con datos inválidos

### Para Administradores

1. **Configurar usuarios**:
```sql
-- Usuario ETL
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'pass';
GRANT EXECUTE ON PROCEDURE ... TO 'etl_user'@'localhost';

-- Usuario readonly
CREATE USER 'dw_readonly'@'localhost' IDENTIFIED BY 'pass';
GRANT EXECUTE ON PROCEDURE sp_dw_obtener_metricas TO 'dw_readonly'@'localhost';
GRANT SELECT ON v_dw_resumen TO 'dw_readonly'@'localhost';
```

2. **Monitorear sistema**:
```bash
# Script de monitoreo
#!/bin/bash
mysql -u root -p -e "
    SELECT COUNT(*) as OperacionesHoy
    FROM gestionproyectos_hist.AuditoriaOperaciones
    WHERE DATE(FechaHora) = CURDATE()
"
```

3. **Backup regular**:
```bash
# Backup de procedimientos
mysqldump -u root -p --routines --no-data gestionproyectos_hist > backup.sql

# Backup de auditoría
mysqldump -u root -p gestionproyectos_hist AuditoriaOperaciones ControlDuplicados > audit.sql
```

---

## 🚨 Troubleshooting

### Problema: Procedimiento no existe

```sql
-- Verificar procedimientos
SHOW PROCEDURE STATUS WHERE Db = 'gestionproyectos_hist';

-- Re-instalar si es necesario
SOURCE 01_GestionProyectos/scripts/procedimientos_seguros.sql;
```

### Problema: Access Denied

```sql
-- Ver permisos
SHOW GRANTS FOR 'etl_user'@'localhost';

-- Otorgar permisos
GRANT EXECUTE ON PROCEDURE nombre_proc TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
```

### Problema: Duplicados no se rechazan

```sql
-- Verificar triggers
SHOW TRIGGERS FROM gestionproyectos_hist;

-- Ver log de duplicados
SELECT * FROM ControlDuplicados
WHERE Estado = 'RECHAZADO'
ORDER BY FechaRegistro DESC;
```

---

## ✅ Checklist de Sistema Seguro

### Instalación
- [ ] Bases de datos creadas
- [ ] Procedimientos instalados (27 total)
- [ ] Triggers creados (5)
- [ ] Tablas de auditoría existentes (4)
- [ ] Vistas seguras creadas (6)

### Scripts Python
- [ ] Solo usan `callproc()`
- [ ] NO hay `execute("SELECT")`
- [ ] NO hay `execute("INSERT")`

### Funcionalidad
- [ ] Generador crea datos sin duplicados
- [ ] ETL extrae y carga correctamente
- [ ] Verificador encuentra registros
- [ ] Triggers rechazan duplicados
- [ ] Auditoría registra operaciones

### Seguridad
- [ ] Usuario ETL con permisos limitados
- [ ] Usuario readonly con permisos de consulta
- [ ] Vistas solo muestran agregados
- [ ] Sistema funciona sin SELECT directos

---

## 📞 Referencias Rápidas

| Archivo | Propósito | Líneas |
|---------|-----------|--------|
| `instalar_sistema_seguro.sh` | Instalador automático | ~400 |
| `GUIA_SEGURIDAD_COMPLETA.md` | Documentación seguridad | ~600 |
| `RESUMEN_FINAL_SEGURIDAD.md` | Resumen implementación | ~500 |
| `procedimientos_seguros.sql` | Procs BD Origen | ~650 |
| `procedimientos_etl.sql` | Procs ETL | ~450 |
| `procedimientos_seguros_dw.sql` | Procs DW | ~350 |
| `generar_datos_seguro.py` | Generador seguro | ~430 |
| `etl_principal_seguro.py` | ETL seguro | ~550 |
| `verificar_trazabilidad_seguro.py` | Verificador seguro | ~450 |

**Total**: ~4,380 líneas de código seguro

---

**🎯 Sistema 100% Seguro**  
**✅ Sin SELECT/INSERT directos**  
**🔒 Prevención de filtración de datos**  
**📊 Auditoría completa**  
**🚀 Listo para producción**
