# 🔍 Sistema de Trazabilidad y Control de Calidad de Datos

## 🎯 Objetivo

Este sistema proporciona herramientas para garantizar la **trazabilidad completa** de los datos en el pipeline ETL y **eliminar duplicados** que puedan afectar la integridad de los análisis.

## 🆕 Componentes Nuevos

### 1. **Generador de Datos Mejorado** 
📁 `01_GestionProyectos/scripts/generar_datos_mejorado.py`

**Mejoras sobre el generador original:**
- ✅ Validación de unicidad en tiempo de generación
- ✅ Hashing de registros para prevenir duplicados
- ✅ Emails únicos garantizados
- ✅ Nombres de proyectos únicos basados en tipo + cliente
- ✅ Validación automática post-generación
- ✅ Reporte de integridad de datos

**Diferencias con el generador original:**

| Característica | Original | Mejorado |
|---|---|---|
| Nombres de clientes | Pueden duplicarse | Únicos garantizados |
| Emails | Pueden duplicarse | Únicos garantizados |
| Proyectos | Pueden tener nombres similares | Únicos por tipo-cliente |
| Validación | Manual | Automática |
| Asignaciones | Posibles duplicados | Sin duplicados |
| Reporte | Básico | Completo con estadísticas |

### 2. **Verificador de Trazabilidad**
📁 `verificar_trazabilidad.py`

**Funcionalidades:**
- 🔍 Búsqueda de registros entre BD origen y destino
- 📊 Comparación de conteos
- 🚨 Detección de duplicados
- 📋 Identificación de datos no migrados
- 📈 Reportes de auditoría

## 🚀 Inicio Rápido

### Instalación de Dependencias
```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias (si no está instalado)
pip install -r requirements.txt
```

### Generar Datos Limpios
```bash
# Usar el generador mejorado
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

**Output esperado:**
```
🚀 Generador de Datos MEJORADO - Sistema de Gestión de Proyectos
   ✓ Con trazabilidad
   ✓ Sin duplicados
   ✓ Validación de integridad
======================================================================
✅ Conectado a BD: gestionproyectos_hist
...
🔍 Validando integridad de datos...
  ✅ Clientes únicos: 8/8
  ✅ Emails únicos: 8/8
  ✅ Empleados únicos: 15/15
  ...
🎉 ¡Datos de prueba generados exitosamente!
```

### Ejecutar ETL
```bash
python 02_ETL/scripts/etl_principal.py
```

### Verificar Trazabilidad
```bash
# Opción 1: Modo interactivo
python verificar_trazabilidad.py

# Opción 2: Reporte completo
python verificar_trazabilidad.py reporte
```

## 📊 Verificaciones Implementadas

### 1. Control de Duplicados en Origen

El generador mejorado previene duplicados en:

#### Clientes:
- **Nombre de empresa**: Único por cliente
- **Email**: Único en toda la tabla
- **Validación**: Usa set() para tracking en memoria

```python
# Ejemplo de implementación
clientes_generados = set()

def generar_nombre_unico_cliente():
    nombre = fake.company()
    while nombre in clientes_generados:
        nombre = f"{fake.company()} {random.randint(100, 999)}"
    clientes_generados.add(nombre)
    return nombre
```

#### Empleados:
- **Nombre completo**: Único por empleado
- **Validación**: Similar a clientes

#### Proyectos:
- **Nombre**: Combinación única de tipo + cliente
- **Hash tracking**: Para prevenir duplicados complejos

```python
# Formato: "Tipo - Cliente"
nombre = f"{tipo} - {empresa}"
while nombre in proyectos_generados:
    nombre = f"{tipo} - {empresa} v{contador}"
    contador += 1
```

#### Asignaciones:
- **Equipo-Empleado**: Un empleado no se asigna dos veces al mismo equipo
- **Tarea-Equipo**: Una tarea no se asigna dos veces al mismo equipo
- **Hash-based tracking**: Para validación eficiente

### 2. Trazabilidad entre Bases de Datos

El verificador permite rastrear cualquier registro desde origen hasta destino:

#### Ejemplo: Buscar un proyecto
```bash
python verificar_trazabilidad.py
# Opción 2: Buscar proyecto por ID
# Ingresar: 5
```

**Resultado:**
```
🔍 Buscando Proyecto ID: 5
======================================================================

📦 BD ORIGEN (gestionproyectos_hist):
----------------------------------------------------------------------
  id_proyecto                  : 5
  nombre                       : Sistema Web - Tech Corp
  fecha_inicio                 : 2024-01-15
  presupuesto                  : 200000.00
  id_estado                    : 3
  nombre_estado                : Completado

📦 BD DESTINO (dw_proyectos_hist):
----------------------------------------------------------------------
  id_proyecto                  : 5
  nombre_proyecto              : Sistema Web - Tech Corp
  duracion_planificada         : 120
  duracion_real                : 118
  cumplimiento_tiempo          : 1
  cumplimiento_presupuesto     : 1
  porcentaje_completado        : 100.00

✅ Proyecto encontrado en ambas bases de datos
```

## 🔧 Uso del Verificador de Trazabilidad

### Modo Interactivo
```bash
python verificar_trazabilidad.py
```

**Menú:**
```
🔍 VERIFICADOR DE TRAZABILIDAD - Sistema ETL
======================================================================
1. Verificar conteos generales
2. Buscar proyecto por ID
3. Buscar cliente por nombre
4. Buscar empleado por nombre
5. Verificar duplicados en BD Origen
6. Listar proyectos no migrados
7. Generar reporte completo
0. Salir
```

### Modo Línea de Comandos
```bash
# Reporte completo de trazabilidad
python verificar_trazabilidad.py reporte

# Solo verificar conteos
python verificar_trazabilidad.py conteos

# Buscar duplicados
python verificar_trazabilidad.py duplicados

# Proyectos no migrados
python verificar_trazabilidad.py no-migrados
```

## 📈 Casos de Uso

### Caso 1: Validar Generación de Datos
**Problema**: Quiero asegurarme de que no hay duplicados después de generar datos.

**Solución**:
```bash
# 1. Generar datos
python 01_GestionProyectos/scripts/generar_datos_mejorado.py

# 2. Verificar duplicados
python verificar_trazabilidad.py duplicados
```

**Resultado esperado**: ✅ Todos los checks en verde

### Caso 2: Verificar ETL Exitoso
**Problema**: El ETL terminó pero quiero confirmar que todos los datos se migraron.

**Solución**:
```bash
python verificar_trazabilidad.py conteos
```

**Resultado esperado**:
```
📊 VERIFICACIÓN DE CONTEOS
======================================================================
| Entidad                       | BD Origen | BD Destino | Estado |
|-------------------------------|-----------|------------|--------|
| Clientes                      | 8         | 8          | ✅     |
| Empleados                     | 15        | 15         | ✅     |
| Proyectos                     | 8         | 8          | ✅     |
| HechoProyecto                 | 8         | 8          | ✅     |
```

### Caso 3: Buscar un Cliente Específico
**Problema**: Un usuario reporta que los datos de "Tech Corp" no aparecen en el dashboard.

**Solución**:
```bash
python verificar_trazabilidad.py
# Opción 3: Buscar cliente por nombre
# Ingresar: Tech Corp
```

**Posibles resultados**:
- ✅ Cliente encontrado en ambas BD → El problema es del dashboard
- ❌ Cliente no en DW → Ejecutar ETL nuevamente
- ❌ Cliente no en origen → Regenerar datos

### Caso 4: Auditoría Completa
**Problema**: Necesito un reporte completo del estado del sistema.

**Solución**:
```bash
python verificar_trazabilidad.py reporte > auditoria_$(date +%Y%m%d).txt
```

Esto genera un archivo con:
- Conteos de todas las entidades
- Lista de duplicados (si existen)
- Proyectos no migrados
- Timestamp del reporte

## 🛠️ Solución de Problemas

### Problema 1: Duplicados Detectados

**Síntoma**:
```
❌ Clientes duplicados encontrados:
  • Acme Corp: 2 veces
```

**Causa**: Se usó el generador original en lugar del mejorado.

**Solución**:
```bash
# 1. Limpiar BD origen
mysql -u root -p gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql

# 2. Usar generador mejorado
python 01_GestionProyectos/scripts/generar_datos_mejorado.py

# 3. Verificar
python verificar_trazabilidad.py duplicados
```

### Problema 2: Conteos No Coinciden

**Síntoma**:
```
| Clientes | 10 | 8 | ❌ |
```

**Posibles causas**:
1. Clientes inactivos en origen (solo se migran activos)
2. Error en el ETL
3. ETL no se ejecutó después de regenerar datos

**Diagnóstico**:
```bash
# Verificar clientes activos en origen
mysql -u root -p -e "USE gestionproyectos_hist; 
SELECT COUNT(*) as total, 
       SUM(activo) as activos,
       COUNT(*) - SUM(activo) as inactivos 
FROM Cliente;"
```

**Solución**: Re-ejecutar ETL
```bash
python 02_ETL/scripts/etl_principal.py
python verificar_trazabilidad.py conteos
```

### Problema 3: Proyecto No Migrado

**Síntoma**:
```
⚠️  4 proyecto(s) NO migrado(s):
| ID | Nombre               | Estado      | Progreso |
|----|---------------------|-------------|----------|
| 3  | Portal Web ABC      | En Progreso | 65%      |
```

**Causa**: Solo se migran proyectos **Completados** o **Cancelados** (estados 3 y 4).

**Solución**: 
Esto es comportamiento esperado. Si necesitas migrar todos los proyectos:

1. Modificar filtro en ETL:
```python
# En etl_principal.py, línea ~200
# Cambiar:
WHERE p.id_estado IN (3, 4)
# Por:
WHERE 1=1  # Migrar todos
```

2. Re-ejecutar ETL

### Problema 4: No Se Puede Conectar a BD

**Síntoma**:
```
❌ Error conectando: Access denied for user 'root'@'localhost'
```

**Solución**:
```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# Verificar credenciales en el script
# Editar verificar_trazabilidad.py líneas 19-25
```

## 📚 Estructura de Datos

### Garantías de Unicidad

| Tabla | Campo Único | Método | Nivel |
|-------|------------|---------|-------|
| Cliente | nombre | Set tracking | Aplicación |
| Cliente | email | Set tracking | Aplicación |
| Empleado | nombre | Set tracking | Aplicación |
| Equipo | nombre_equipo | Set tracking | Aplicación |
| Proyecto | nombre | Hash-based | Aplicación |
| MiembroEquipo | (id_equipo, id_empleado) | Hash-based | Aplicación |
| TareaEquipoHist | (id_tarea, id_equipo, fecha) | Hash-based | Aplicación |

**Nota**: Las validaciones se hacen a nivel de aplicación (Python) durante la generación. Para garantías a nivel de BD, se pueden agregar constraints UNIQUE en los scripts SQL.

## 🔐 Mejores Prácticas

### 1. Siempre Usar el Generador Mejorado
❌ **No hacer**:
```bash
python 01_GestionProyectos/scripts/generar_datos.py
```

✅ **Hacer**:
```bash
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

### 2. Verificar Después de Cada ETL
```bash
# Después de ejecutar ETL
python 02_ETL/scripts/etl_principal.py

# Siempre verificar
python verificar_trazabilidad.py conteos
```

### 3. Reporte Periódico
```bash
# Agregar a cron para ejecución diaria
0 9 * * * cd /ruta/proyecto && python verificar_trazabilidad.py reporte >> logs/trazabilidad_$(date +\%Y\%m\%d).log
```

### 4. Backup Antes de Regenerar
```bash
# Backup de BD origen
mysqldump -u root -p gestionproyectos_hist > backup_origen_$(date +%Y%m%d).sql

# Backup de DW
mysqldump -u root -p dw_proyectos_hist > backup_dw_$(date +%Y%m%d).sql

# Luego regenerar
python 01_GestionProyectos/scripts/generar_datos_mejorado.py
```

## 📖 Documentación Adicional

- 📄 **Guía Completa**: `GUIA_TRAZABILIDAD.md`
- 📄 **README Principal**: `README.md`
- 📄 **Documentación ETL**: `02_ETL/README.md`
- 📄 **Ejemplos de Uso**: `EJEMPLOS_USO.md`

## 🎓 Preguntas Frecuentes

**P: ¿Puedo usar ambos generadores?**
R: No recomendado. El generador mejorado reemplaza al original. Usar solo uno para consistencia.

**P: ¿Qué pasa con las fechas? ¿Pueden duplicarse?**
R: Sí, las fechas **pueden y deben** duplicarse. La validación de unicidad excluye fechas intencionalmente.

**P: ¿Se validan duplicados en el DataWarehouse?**
R: El verificador detecta duplicados en **origen**. El DW debería heredar la limpieza del origen. Si hay duplicados en DW, indica un problema en el ETL.

**P: ¿Cómo agrego validaciones personalizadas?**
R: Modifica `validar_integridad_datos()` en `generar_datos_mejorado.py`:
```python
def validar_integridad_datos(cursor):
    # Agregar tu validación
    cursor.execute("SELECT ... tu query ...")
    # Procesar resultados
```

**P: ¿Funciona con BD distribuida (3 máquinas)?**
R: Sí, pero debes modificar las credenciales de conexión en cada script según tu configuración.

## 🤝 Contribuciones

Para mejorar el sistema de trazabilidad:
1. Documenta el problema o mejora
2. Crea tests si es posible
3. Actualiza esta documentación

---

**Última actualización**: Octubre 2025  
**Versión**: 2.0  
**Autor**: Sistema ETL - Gestión de Proyectos
