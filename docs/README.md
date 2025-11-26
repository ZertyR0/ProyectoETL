# Documentación del Proyecto ETL

Bienvenido a la documentación del Sistema ETL de Gestión de Proyectos.

---

## Documentación por Módulo

Cada módulo del proyecto tiene su propia documentación:

### 01_GestionProyectos - Base de Datos Origen
**Documentación:** [01_GestionProyectos/README.md](../01_GestionProyectos/README.md)

- Base de datos transaccional (OLTP)
- Scripts de creación de BD
- Generación de datos de prueba
- Procedimientos almacenados seguros

### 02_ETL - Proceso ETL
**Documentación:** [02_ETL/README.md](../02_ETL/README.md)

- Scripts ETL (incremental y procedimientos)
- Configuración de conexiones
- Transformación de datos

### 03_Dashboard - Dashboard Web
**Documentación:** [03_Dashboard/README.md](../03_Dashboard/README.md)

- Backend Flask con API REST
- Frontend HTML/CSS/JS
- Cubo OLAP
- Balanced Scorecard (BSC/OKR)
- Predicción Rayleigh
- Scripts de inicio/parada

### 04_Datawarehouse - Data Warehouse
**Documentación:** [04_Datawarehouse/README.md](../04_Datawarehouse/README.md)

- Esquema estrella
- Vistas OLAP
- Tablas BSC/OKR
- Consultas de análisis
- Procedimientos seguros

---

## Inicio Rápido

Para empezar con el sistema:

1. **Lee el README principal:** [../README.md](../README.md)
2. **Instala dependencias:** `pip install -r requirements.txt`
3. **Configura las bases de datos:**
   ```bash
   mysql -u root -p < 01_GestionProyectos/scripts/crear_bd_origen.sql
   mysql -u root -p < 04_Datawarehouse/scripts/crear_datawarehouse.sql
   ```
4. **Genera datos:** `python 01_GestionProyectos/datos/generar_datos_final.py`
5. **Ejecuta ETL:** `python src/etl/etl_incremental.py`
6. **Inicia Dashboard:** `cd 03_Dashboard && ./iniciar_dashboard.sh`
7. **Accede:** http://localhost:8080

---

## Navegación Rápida por Tarea

### Instalación y Configuración
- **README Principal:** [../README.md](../README.md) - Guía completa de instalación
- **Configuración ETL:** [../src/config/config_conexion.py](../src/config/config_conexion.py) - Variables de ambiente

### Usar el Sistema
- **Dashboard:** http://localhost:8080 (después de iniciar)
- **API Backend:** http://localhost:5001/status
- **Generar Datos:** `python 01_GestionProyectos/datos/generar_datos_final.py`
- **Ejecutar ETL:** `python src/etl/etl_incremental.py`

### Scripts Disponibles
```bash
# Iniciar Dashboard
cd 03_Dashboard
./iniciar_dashboard.sh

# Detener Dashboard
cd 03_Dashboard
./detener_dashboard.sh

# ETL Incremental
python src/etl/etl_incremental.py

# ETL con Procedimiento Almacenado
python 02_ETL/scripts/etl_final.py

# Generar Datos
python 01_GestionProyectos/datos/generar_datos_final.py
```

---

## Estructura del Proyecto

```
ProyectoETL/
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias consolidadas
│
├── src/                         # Código fuente principal
│   ├── config/
│   │   └── config_conexion.py  # Configuración centralizada
│   ├── etl/
│   │   └── etl_incremental.py  # ETL incremental
│   └── origen/
│       └── generar_datos.py    # Generador de datos
│
├── 01_GestionProyectos/         # BD Origen (OLTP)
│   ├── README.md
│   ├── datos/
│   └── scripts/
│
├── 02_ETL/                      # Proceso ETL
│   ├── README.md
│   └── scripts/
│
├── 03_Dashboard/                # Dashboard DSS
│   ├── README.md
│   ├── iniciar_dashboard.sh
│   ├── detener_dashboard.sh
│   ├── backend/
│   └── frontend/
│
├── 04_Datawarehouse/            # Data Warehouse + OLAP
│   ├── README.md
│   └── scripts/
│
├── docs/                        # Documentación (este archivo)
│   └── README.md
│
└── logs/                        # Logs del sistema
```

---

## Componentes Principales

### Variables de Entorno

El sistema utiliza variables de entorno para configuración:

| Variable | Valores | Default | Descripción |
|----------|---------|---------|-------------|
| `ETL_AMBIENTE` | local, distribuido, test | local | Configuración de conexiones |
| `ETL_DRY_RUN` | 0, 1 | 0 | Modo simulación (sin escritura) |
| `ETL_LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR | INFO | Nivel de detalle de logs |

### Archivos Clave

- **Configuración:** `src/config/config_conexion.py`
- **ETL Incremental:** `src/etl/etl_incremental.py`
- **ETL Procedimientos:** `02_ETL/scripts/etl_final.py`
- **Backend API:** `03_Dashboard/backend/app.py`
- **Frontend:** `03_Dashboard/frontend/index.html`

---

## Niveles de Conocimiento

### Nivel Básico (5-10 minutos)
1. Lee [../README.md](../README.md) - Inicio Rápido
2. Sigue los pasos de instalación
3. Accede al Dashboard en http://localhost:8080

### Nivel Intermedio (20-30 minutos)
1. Revisa cada README de módulo
2. Explora la configuración en `src/config/config_conexion.py`
3. Examina el código ETL en `src/etl/etl_incremental.py`

### Nivel Avanzado (1-2 horas)
1. Estudia los procedimientos almacenados SQL
2. Analiza el esquema del Data Warehouse
3. Explora el código del backend y frontend
4. Modifica y extiende el sistema

---

## Solución de Problemas

### Error de Conexión a MySQL
```bash
# Verificar que MySQL está corriendo
mysql -u root -p

# Verificar configuración
cat src/config/config_conexion.py
```

### Dashboard no Inicia
```bash
# Verificar puertos ocupados
lsof -i :5001  # Backend
lsof -i :8080  # Frontend

# Matar procesos si es necesario
cd 03_Dashboard
./detener_dashboard.sh
./iniciar_dashboard.sh
```

### ETL Falla
```bash
# Verificar logs
tail -f 03_Dashboard/logs/backend.log

# Ejecutar con más detalle
ETL_LOG_LEVEL=DEBUG python src/etl/etl_incremental.py
```

### Sin Datos
```bash
# Generar datos de prueba
python 01_GestionProyectos/datos/generar_datos_final.py

# Verificar en BD
mysql -u root -p gestionproyectos_hist -e "SELECT COUNT(*) FROM Proyecto;"
```

---

## API Endpoints Principales

El backend expone los siguientes endpoints:

### Estado y Monitoreo
- `GET /status` - Estado de conexiones
- `GET /datos-origen` - Datos de la BD origen
- `GET /datos-datawarehouse` - Datos del DW

### Operaciones ETL
- `POST /ejecutar-etl` - Ejecutar proceso ETL
- `POST /generar-datos` - Generar datos de prueba
- `DELETE /limpiar-datos` - Limpiar bases de datos

### Análisis OLAP
- `GET /olap/kpis` - KPIs con filtros multidimensionales
- `GET /olap/series` - Series temporales
- `GET /olap/kpis-ejecutivos` - Dashboard ejecutivo

### BSC/OKR
- `GET /bsc/okr` - Tablero BSC completo
- `POST /bsc/medicion` - Registrar mediciones
- `GET /bsc/vision-estrategica` - Resumen de visión

### Predicción Rayleigh
- `POST /prediccion/defectos-rayleigh` - Generar predicción
- `GET /prediccion/historico` - Histórico de predicciones

---

## 🤝 Contribuir

Para contribuir al proyecto:

1. Fork del repositorio
2. Crea una rama de feature
3. Realiza tus cambios
4. Actualiza la documentación relevante
5. Envía un Pull Request

---

## Soporte

Para soporte técnico:

1. **Primero:** Revisa esta documentación
2. **Segundo:** Consulta los READMEs de cada módulo
3. **Tercero:** Verifica los logs del sistema
4. **Último:** Contacta al equipo de desarrollo

---

## • Actualizaciones

**Última actualización:** Noviembre 2025

### Cambios Recientes
-  Limpieza de archivos obsoletos
-  Centralización de configuración en `src/config/`
-  Actualización de dependencias
-  Simplificación de documentación
-  Eliminación de referencias a modo distribuido no usado

---

**Para volver al README principal:** [../README.md](../README.md)

**Gracias por usar nuestro Sistema ETL.**

---

## • Búsqueda de Información

### Por Palabra Clave

| Buscas | Consulta |
|--------|----------|
| **Instalación** | [INICIO_RAPIDO.md](guias/INICIO_RAPIDO.md), [GUIA_PRUEBA_LOCAL.md](guias/GUIA_PRUEBA_LOCAL.md) |
| **Configuración** | [README_CONFIGURACION.md](configuracion/README_CONFIGURACION.md) |
| **Dashboard** | [../03_Dashboard/README.md](../03_Dashboard/README.md), [EJEMPLOS_USO.md](guias/EJEMPLOS_USO.md) |
| **ETL** | [../02_ETL/README.md](../02_ETL/README.md), [FILTROS_ETL_DATAWAREHOUSE.md](analisis/FILTROS_ETL_DATAWAREHOUSE.md) |
| **Base de Datos** | [GUIA_DATOS_ORIGEN.md](guias/GUIA_DATOS_ORIGEN.md), [ANALISIS_CONSISTENCIA_BD.md](analisis/ANALISIS_CONSISTENCIA_BD.md) |
| **Seguridad** | [../README.md](../README.md#seguridad) |
| **Problemas** | [CORRECCIONES_REALIZADAS.md](analisis/CORRECCIONES_REALIZADAS.md) |
| **Ejemplos** | [EJEMPLOS_USO.md](guias/EJEMPLOS_USO.md) |

---

## 📱 Documentación por Componente

### 01_GestionProyectos - Base de Datos Origen
- **README**: [../01_GestionProyectos/README.md](../01_GestionProyectos/README.md)
- **Guía de Datos**: [guias/GUIA_DATOS_ORIGEN.md](guias/GUIA_DATOS_ORIGEN.md)
- **Scripts SQL**: `crear_bd_origen.sql`, `procedimientos_seguros.sql`

### 02_ETL - Proceso ETL
- **README**: [../02_ETL/README.md](../02_ETL/README.md)
- **Filtros**: [analisis/FILTROS_ETL_DATAWAREHOUSE.md](analisis/FILTROS_ETL_DATAWAREHOUSE.md)
- **Scripts Python**: `etl_principal.py`, `etl_principal_seguro.py`

### 03_Dashboard - Dashboard Web
- **README**: [../03_Dashboard/README.md](../03_Dashboard/README.md)
- **Ejemplos**: [guias/EJEMPLOS_USO.md](guias/EJEMPLOS_USO.md)
- **Backend**: Flask API en `app.py`
- **Frontend**: HTML/CSS/JS en `index.html`

### 04_Datawarehouse - Data Warehouse
- **README**: [../04_Datawarehouse/README.md](../04_Datawarehouse/README.md)
- **Scripts SQL**: `crear_datawarehouse.sql`, `procedimientos_seguros_dw.sql`
- **Consultas**: `consultas_analisis.sql`

---

## 🎓 Tutoriales y Guías de Aprendizaje

### Nivel Principiante
1. • [INICIO_RAPIDO.md](guias/INICIO_RAPIDO.md) - 5 minutos
2. • [EJEMPLOS_USO.md](guias/EJEMPLOS_USO.md) - 10 minutos
3. 🎮 Usa el dashboard en http://localhost:8080

### Nivel Intermedio
1. • [GUIA_PRUEBA_LOCAL.md](guias/GUIA_PRUEBA_LOCAL.md) - 20 minutos
2. • [GUIA_DATOS_ORIGEN.md](guias/GUIA_DATOS_ORIGEN.md) - 15 minutos
3. • [FILTROS_ETL_DATAWAREHOUSE.md](analisis/FILTROS_ETL_DATAWAREHOUSE.md) - 30 minutos

### Nivel Avanzado
1. • [GUIA_DESPLIEGUE_3_MAQUINAS.md](guias/GUIA_DESPLIEGUE_3_MAQUINAS.md) - 45 minutos
2. • [README_COMPLETO.md](configuracion/README_COMPLETO.md) - 1 hora
3. • [RESUMEN_IMPLEMENTACION.md](resumen/RESUMEN_IMPLEMENTACION.md) - 30 minutos

---

## 📞 Ayuda y Soporte

### ¿Necesitas Ayuda?

1. **Primero**: Busca en esta documentación usando el índice arriba
2. **Segundo**: Revisa las guías según tu nivel de experiencia
3. **Tercero**: Consulta los ejemplos de uso prácticos
4. **Último**: Contacta al equipo de desarrollo

### Reportar Problemas

Si encuentras un problema:
1. Verifica [CORRECCIONES_REALIZADAS.md](analisis/CORRECCIONES_REALIZADAS.md)
2. Consulta [ANALISIS_CONSISTENCIA_BD.md](analisis/ANALISIS_CONSISTENCIA_BD.md)
3. Revisa los logs del sistema
4. Reporta el issue con detalles

---

## • Actualizaciones de Documentación

**Última actualización**: Enero 2025

### Cambios Recientes
-  Reorganización completa de documentación
-  Creación de categorías (guias, analisis, configuracion, resumen)
-  Índice maestro con navegación mejorada
-  Enlaces cruzados entre documentos
-  Guías por nivel de experiencia

---

## 🤝 Contribuir a la Documentación

Para mejorar esta documentación:
1. Identifica áreas que necesitan clarificación
2. Crea o edita documentos según la estructura
3. Actualiza este índice si agregas nuevos documentos
4. Mantén la consistencia en formato y estilo

---

**Gracias por usar nuestro Sistema ETL de Gestión de Proyectos** 

Para volver al README principal: [../README.md](../README.md)
