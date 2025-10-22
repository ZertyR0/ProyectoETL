# 🚀 Guía Rápida de Prueba Local

## Configuración Inicial (Una sola vez)

### 1. Ejecutar script de configuración

Este script hará todo automáticamente:
- Crear las bases de datos (origen y datawarehouse)
- Instalar dependencias Python
- Generar datos de prueba
- Ejecutar el ETL inicial

```bash
./setup_local.sh
```

**⚠️ Requisitos previos:**
- MySQL instalado y corriendo
- Python 3.x instalado
- Usuario MySQL `root` sin contraseña (o modificar configs)

---

## Uso del Dashboard

### Iniciar el Dashboard

```bash
./iniciar_dashboard.sh
```

Esto iniciará:
- **Backend API**: `http://localhost:5001`
- **Frontend Dashboard**: `http://localhost:8080`

El navegador se abrirá automáticamente.

### Detener el Dashboard

```bash
./detener_dashboard.sh
```

---

## Estructura del Proyecto

```
ProyectoETL/
├── 01_GestionProyectos/    # Base de datos origen
│   └── scripts/
│       ├── crear_bd_origen.sql      # Crear BD
│       └── generar_datos.py         # Datos de prueba
│
├── 02_ETL/                  # Proceso ETL
│   ├── config/
│   │   └── config_conexion.py       # Configuración
│   └── scripts/
│       ├── etl_principal.py         # ETL completo
│       └── etl_utils.py             # Utilidades
│
├── 03_Dashboard/            # Interfaz web
│   ├── backend/
│   │   └── app.py                   # API Flask
│   └── frontend/
│       ├── index.html               # UI
│       ├── app.js                   # Lógica
│       └── styles.css               # Estilos
│
└── 04_Datawarehouse/        # Data Warehouse
    └── scripts/
        └── crear_datawarehouse.sql  # Crear DW
```

---

## Funciones del Dashboard

### 1. 📊 Insertar Datos
- Genera datos de prueba en la base de datos origen
- Crea clientes, empleados, proyectos y tareas

### 2. ⚙️ Ejecutar ETL
- Extrae datos de la base origen
- Transforma y limpia los datos
- Carga en el datawarehouse
- Muestra estadísticas del proceso

### 3. 🗑️ Limpiar Datos
- Elimina todos los datos de ambas bases
- Útil para reiniciar las pruebas

---

## Comandos Manuales

### Verificar Bases de Datos

```bash
# Conectar a BD origen
mysql -u root gestionproyectos_hist

# Conectar a datawarehouse
mysql -u root dw_proyectos_hist
```

### Ejecutar ETL manualmente

```bash
source venv/bin/activate
python3 02_ETL/scripts/etl_principal.py local
```

### Generar datos de prueba

```bash
source venv/bin/activate
python3 01_GestionProyectos/scripts/generar_datos.py
```

---

## Solución de Problemas

### El dashboard no abre

1. Verifica que MySQL esté corriendo:
   ```bash
   mysql --version
   mysql -u root -e "SELECT 1"
   ```

2. Verifica los puertos:
   ```bash
   lsof -i :5001  # Backend
   lsof -i :8080  # Frontend
   ```

3. Revisa los logs:
   ```bash
   cat 03_Dashboard/backend/backend.log
   cat 03_Dashboard/frontend/frontend.log
   ```

### Error de conexión a MySQL

Edita el archivo de configuración:
```bash
nano 02_ETL/config/config_conexion.py
```

Modifica la sección `CONFIG_LOCAL` con tus credenciales.

### Reinstalar dependencias

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Limpiar y reiniciar todo

```bash
./detener_dashboard.sh
rm -rf venv
./setup_local.sh
./iniciar_dashboard.sh
```

---

## URLs Útiles

| Servicio | URL |
|----------|-----|
| Dashboard | http://localhost:8080 |
| API Backend | http://localhost:5001 |
| API Status | http://localhost:5001/status |
| API Docs | http://localhost:5001/ |

---

## Bases de Datos

### BD Origen: `gestionproyectos_hist`

Tablas principales:
- `Cliente` - Información de clientes
- `Empleado` - Empleados y recursos
- `Proyecto` - Proyectos activos
- `Tarea` - Tareas de proyectos
- `Equipo` - Equipos de trabajo

### Datawarehouse: `dw_proyectos_hist`

Dimensiones:
- `DimCliente` - Dimensión de clientes
- `DimEmpleado` - Dimensión de empleados
- `DimProyecto` - Dimensión de proyectos
- `DimEquipo` - Dimensión de equipos
- `DimTiempo` - Dimensión temporal

Hechos:
- `HechoProyecto` - Métricas de proyectos
- `HechoTarea` - Métricas de tareas

---

## Flujo de Trabajo Típico

1. **Configuración inicial** (una vez):
   ```bash
   ./setup_local.sh
   ```

2. **Iniciar dashboard**:
   ```bash
   ./iniciar_dashboard.sh
   ```

3. **En el navegador** (http://localhost:8080):
   - Click en "Insertar Datos" para generar datos
   - Click en "Ejecutar ETL" para procesar
   - Ver las métricas y resultados

4. **Detener** cuando termines:
   ```bash
   ./detener_dashboard.sh
   ```

---

## Ambiente Distribuido

Para configurar el ambiente en 3 máquinas, consulta:
- `GUIA_DESPLIEGUE_3_MAQUINAS.md`
- `README_CONFIGURACION.md`

---

## Soporte

Si tienes problemas:

1. Verifica que MySQL esté corriendo
2. Revisa los logs del backend
3. Verifica que los puertos 5001 y 8080 estén libres
4. Ejecuta `./setup_local.sh` de nuevo

---

## Licencia

Proyecto educativo - ETL Sistema de Gestión de Proyectos
