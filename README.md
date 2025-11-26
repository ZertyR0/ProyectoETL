# 🚀 Sistema ETL + DataWarehouse + BSC Dashboard# Sistema de Soporte de Decisiones (DSS) - ProyectoETL



Sistema completo de **ETL**, **DataWarehouse** y **Balanced Scorecard** para gestión de proyectos con métricas calculadas en tiempo real.**Sistema Integral de Business Intelligence con Cubo OLAP, BSC/OKR y Modelo de Predicción Rayleigh**



[![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue.svg)](https://www.mysql.com/)Sistema completo de ETL (Extract, Transform, Load) con **Data Warehouse**, **Cubo OLAP**, **Balanced Scorecard/OKR** y **Modelo de Predicción de Defectos** usando distribución de Rayleigh. Diseñado para la **transformación digital** y **excelencia operacional**.

[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

[![Flask](https://img.shields.io/badge/Flask-Latest-red.svg)](https://flask.palletsprojects.com/)## INICIO RÁPIDO - CONFIGURACIÓN LOCAL



---```bash

# 1. Clonar el repositorio

## 📋 Características Principalesgit clone [url-del-repo]

cd ProyectoETL

✅ **Sistema ETL Completo** - Extracción, transformación y carga automatizada  

✅ **DataWarehouse Dimensional** - Modelo estrella con 12 dimensiones y 8 hechos  # 2. Instalar dependencias

✅ **Balanced Scorecard** - 5 objetivos estratégicos, 10 KRs calculados desde métricas reales  pip install -r requirements.txt

✅ **Dashboard Interactivo** - Visualización en tiempo real con Flask + HTML/JS  

✅ **100% Calculado** - Sin valores hardcodeados, todas las métricas desde el DW  # 3. Configurar bases de datos MySQL

✅ **Completamente Portable** - Inicialización con 1 comando  mysql -u root -p < 01_GestionProyectos/scripts/crear_bd_origen.sql

mysql -u root -p < 04_Datawarehouse/scripts/crear_datawarehouse.sql

---mysql -u root -p < 04_Datawarehouse/scripts/olap_views.sql

mysql -u root -p < 04_Datawarehouse/scripts/crear_bsc.sql

## ⚡ Inicio Rápido

# 4. Generar datos de demostración

### Opción 1: Inicialización Automática (Recomendada)python 01_GestionProyectos/datos/generar_datos_final.py



```bash# 5. Ejecutar ETL inicial

./inicializar_sistema_completo.shpython src/etl/etl_incremental.py

```

# 6. Iniciar Dashboard DSS

**Tiempo:** 30-60 segundos  cd 03_Dashboard

**Resultado:** Sistema completo funcionando en http://localhost:3000./iniciar_dashboard.sh



### Opción 2: Verificación del Sistema# 7. Acceder al sistema

open http://localhost:8080

```bash```

./verificar_sistema.sh

```**En pocos minutos tienes el DSS completo funcionando.**



**Tests:** 23 verificaciones automáticas  ## Visión Estratégica

**Validación:** Datos en origen, DW, BSC, vistas, y dashboard

**"Transformación Digital para la Excelencia Operacional"**

---

Liderar la transformación digital mediante sistemas de soporte de decisiones, procesos automatizados y analítica avanzada para entregar valor superior a nuestros clientes.

## 📊 Arquitectura del Sistema

### Arquitectura del Sistema de Soporte de Decisiones (DSS)

```

┌─────────────────┐```

│  ORIGEN (BD)    │  ← 8 tablas operacionales┌─────────────────────────────────────────────────────────────────────┐

│  50 proyectos   │     • cliente, empleado, equipo, proyecto, tarea│                    DASHBOARD DSS INTEGRADO                          │

│  135 defectos   │     • defecto, capacitacion, satisfaccion_cliente├─────────────────┬─────────────────┬─────────────────┬──────────────┤

│  351 trainings  │     • movimiento_empleado│   CUBO OLAP     │   BSC/OKR       │  PREDICCIÓN     │   ETL        │

└────────┬────────┘│                 │                 │   (Rayleigh)    │              │

         ││ • Drill-down    │ • 4 Perspectivas│ • Modelo        │ • Monitoreo  │

         ↓ ETL (sp_etl_completo_con_metricas)│ • Roll-up       │ • Objetivos     │   Estadístico   │ • Control    │

         ││ • Filtros       │ • Key Results   │ • Control PM    │ • Trazab.    │

┌────────┴────────┐│ • Series Temp.  │ • Semáforos     │ • Cronograma    │              │

│  DATAWAREHOUSE  │  ← Modelo estrella└─────────────────┴─────────────────┴─────────────────┴──────────────┘

│  26 proyectos   │     • 12 Dimensiones (Cliente, Empleado, Tiempo...)                                │

│  260 tareas     │     • 8 Hechos (Proyecto, Tarea, Defecto, Capacitacion...)                    ┌───────────────────────┐

│  135 defectos   │                    │    DATA WAREHOUSE     │

└────────┬────────┘                    │   Esquema Estrella    │

         │                    ├───────────────────────┤

         ↓ Cálculo automático (poblar_bsc_automatico.sql)                    │ • Dimensiones         │

         │                    │ • Tablas de Hechos    │

┌────────┴────────┐                    │ • Vistas OLAP         │

│  BSC + OKRs     │  ← 100% calculado desde DW                    │ • Tablas BSC/OKR      │

│  5 objetivos    │     • Perspectiva Financiera                    │ • Procedimientos      │

│  10 KRs         │     • Perspectiva de Clientes                    └───────────────────────┘

│  10 mediciones  │     • Perspectiva de Procesos Internos                                │

└────────┬────────┘     • Perspectiva de Aprendizaje e Innovación                    ┌───────────────────────┐

         │                    │     PROCESO ETL       │

         ↓ API REST (Flask) + Frontend                    │   (02_ETL/scripts/)   │

         │                    └───────────────────────┘

┌────────┴────────┐                                │

│   DASHBOARD     │  ← http://localhost:3000                    ┌───────────────────────┐

│   Visualización │     • Tablero consolidado                    │   BASE DE DATOS       │

│   Tiempo real   │     • Semáforos (🟢 🟡 🔴)                    │      ORIGEN           │

└─────────────────┘     • Progresos y tendencias                    │ (01_GestionProyectos) │

```                    └───────────────────────┘

```

---

## Componentes del DSS

## 🎯 Métricas Calculadas (Ejemplos Reales)

### 1. **Cubo OLAP** - Análisis Multidimensional

| Métrica | Valor | Fuente |- **Vistas Materializadas** con `ROLLUP` para agregaciones

|---------|-------|--------|- **Drill-down** por Cliente, Equipo, Tiempo

| Costo promedio proyecto | $340,079 | `AVG(costo_real_proy) FROM HechoProyecto` |- **Roll-up** automático con niveles de agregación

| Rentabilidad promedio | 12.64% | `AVG((presupuesto - costo) / presupuesto * 100)` |- **Series Temporales** (mensual, trimestral, anual)

| Defectos por proyecto | 5.19 | `COUNT(*) FROM HechoDefecto / COUNT(*) FROM HechoProyecto` |- **KPIs Ejecutivos** en tiempo real

| Satisfacción cliente | 4.22/5.0 | `AVG(calificacion) FROM HechoSatisfaccion` |

| Horas capacitación/empleado | 33.87h | `AVG(horas_duracion) FROM HechoCapacitacion` |**Endpoints:**

| Rotación de personal | 12.80% | `(COUNT egresos / total_empleados) * 100` |- `GET /olap/kpis` - KPIs con filtros multidimensionales

- `GET /olap/series` - Series temporales configurables

---- `GET /olap/kpis-ejecutivos` - Dashboard ejecutivo

- `GET /olap/dimensiones` - Valores para filtros

## 📂 Estructura del Proyecto

### 2. **BSC/OKR** - Balanced Scorecard con Objectives & Key Results

```- **4 Perspectivas del BSC**: Financiera, Clientes, Procesos Internos, Aprendizaje/Innovación  

ProyectoETL/- **Objetivos Estratégicos** vinculados con la visión

├── inicializar_sistema_completo.sh  ← Inicialización automática (1 comando)- **Key Results** con semáforos (verdeamarillorojo)

├── verificar_sistema.sh             ← 23 tests de validación- **Seguimiento** automático con umbrales

├── PORTABILIDAD.md                  ← Guía completa de transferencia- **Mapa Estratégico** visual interactivo

├── RESUMEN_CAMBIOS.md               ← Changelog detallado

│**Componentes de la Visión:**

├── 01_GestionProyectos/- Transformación Digital

│   ├── datos/- Confiabilidad y Calidad  

│   │   └── generar_datos_final.py   ← Generador de datos sintéticos- Analítica Avanzada

│   └── scripts/- Automatización de Procesos

│       ├── crear_bd_origen.sql      ← Estructura de 8 tablas- Excelencia Operacional

│       └── procedimientos_seguros.sql

│**Endpoints:**

├── 02_ETL/- `GET /bsc/okr` - Tablero BSC consolidado

│   └── scripts/- `POST /bsc/medicion` - Registrar mediciones

│       └── etl_completo_con_metricas.sql  ← ETL + métricas (350+ líneas)- `GET /bsc/vision-estrategica` - Resumen de visión

│- `GET /bsc/historico-kr/{id}` - Histórico de KRs

├── 03_Dashboard/

│   ├── iniciar_dashboard.sh### 3. **Modelo de Predicción Rayleigh** - Predicción de Defectos

│   ├── detener_dashboard.sh- **Distribución de Rayleigh** para modelado de defectos en software

│   ├── backend/- **Control de Acceso** - Solo Project Managers

│   │   └── app.py                   ← API Flask (endpoints REST)- **Predicción Semanal** de defectos esperados

│   └── frontend/- **Cronograma de Testing** optimizado

│       ├── index.html               ← Dashboard BSC- **Métricas de Riesgo** del proyecto

│       ├── app.js

│       └── styles.css**Fórmulas Implementadas:**

│- Función de densidad: `f(t) = (t/σ²) * exp(-t²/(2σ²))`

└── 04_Datawarehouse/- Función acumulativa: `F(t) = 1 - exp(-t²/(2σ²))`

    └── scripts/- Tasa de fallas: `h(t) = t/σ²`

        ├── crear_datawarehouse.sql        ← 12 dimensiones + hechos

        ├── agregar_tablas_metricas.sql    ← HechoDefecto, HechoCapacitacion...**Endpoints:**

        ├── crear_bsc.sql                  ← Estructura BSC- `POST /prediccion/defectos-rayleigh` - Generar predicción (requiere PM)

        └── poblar_bsc_automatico.sql      ← OKRs calculados 100% reales- `GET /prediccion/historico` - Histórico de predicciones

```- `GET /prediccion/validar-acceso` - Validar permisos PM



---### 4. **ETL y Monitoreo** - Proceso de Datos

- **Monitoreo ETL** en tiempo real

## 🛠️ Requisitos- **Trazabilidad** completa de datos

- **Control de Calidad** automatizado

- **MySQL 8.0+**- **Alertas** y notificaciones

- **Python 3.8+**

- **Navegador web** (Chrome, Firefox, Safari)## Arquitectura Modular



### Instalación de dependencias Python:El sistema está estructurado en **4 módulos independientes**:



```bash| Módulo | Carpeta | Descripción | Tecnología |

pip3 install -r requirements.txt|--------|---------|-------------|------------|

```| **1** | `01_GestionProyectos/` | BD Transaccional (OLTP) | MySQL + Python |

| **2** | `02_ETL/` | Scripts SQL y Procedimientos ETL | SQL |

---| **3** | `03_Dashboard/` | Dashboard DSS | Flask + HTML/JS |

| **4** | `04_Datawarehouse/` | Data Warehouse + OLAP | MySQL + SQL |

## 📖 Documentación Detallada

### Estructura Actualizada

- **[PORTABILIDAD.md](PORTABILIDAD.md)** - Guía completa para transferir a otra máquina

- **[RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)** - Changelog con todas las actualizaciones```

ProyectoETL/

---├── README.md                       # Este archivo

├── requirements.txt                # Dependencias consolidadas

## 🔄 Flujo de Actualización de Datos│

├── src/                           # Código fuente principal

Para regenerar datos y actualizar dashboard:│   ├── config/

│   │   └── config_conexion.py    # Configuración centralizada

```bash│   ├── etl/

# 1. Regenerar datos en origen│   │   └── etl_incremental.py    # ETL incremental con logging

cd 01_GestionProyectos/datos│   └── origen/

python3 generar_datos_final.py│       └── generar_datos.py      # Generador de datos

cd ../..│

├── 01_GestionProyectos/          # BD Origen (OLTP)

# 2. Re-ejecutar ETL│   ├── datos/

echo "CALL sp_etl_completo_con_metricas();" | mysql -u root dw_proyectos_hist│   │   └── generar_datos_final.py

│   └── scripts/

# 3. Actualizar OKRs│       ├── crear_bd_origen.sql

mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/poblar_bsc_automatico.sql│       ├── crear_estado_remoto.py

│       ├── crear_tabla_estado.sql

# 4. Refrescar dashboard (Ctrl+R en navegador)│       └── procedimientos_seguros.sql

```│

├── 02_ETL/                        # Proceso ETL

---│   ├── README.md

│   └── scripts/

## 🎯 10 Key Results (OKRs) Implementados│       ├── etl_final.py          # ETL con procedimiento almacenado

│       ├── procedimientos_etl_completo.sql

### Perspectiva Financiera 💰│       └── procedimientos_etl_final.sql

1. **KR-FIN-01** - Reducir costos promedio en 15%│

2. **KR-FIN-02** - Aumentar rentabilidad a 20%├── 03_Dashboard/                  # Dashboard DSS

│   ├── README.md

### Perspectiva de Clientes 😊│   ├── iniciar_dashboard.sh      # Script de inicio

3. **KR-CLI-01** - Reducir defectos por proyecto en 30%│   ├── detener_dashboard.sh      # Script de parada

4. **KR-CLI-02** - Aumentar satisfacción de cliente a 4.5/5│   ├── backend/

│   │   ├── app.py               # Flask API con todos los endpoints

### Perspectiva de Procesos Internos ⚙️│   │   ├── rayleigh.py          # Modelo de Predicción Rayleigh

5. **KR-PRO-01** - Reducir horas promedio por tarea en 20%│   │   └── requirements.txt

6. **KR-PRO-02** - Aumentar proyectos dentro de presupuesto a 90%│   └── frontend/

7. **KR-PRO-03** - Reducir ciclo promedio de proyecto en 25%│       ├── index.html           # UI con módulos integrados

8. **KR-PRO-04** - Aumentar proyectos entregados a tiempo a 85%│       ├── app.js

│       └── styles.css

### Perspectiva de Aprendizaje e Innovación 📚│

9. **KR-APR-01** - Aumentar horas de capacitación a 40h/empleado├── 04_Datawarehouse/             #  Data Warehouse + OLAP + BSC

10. **KR-APR-02** - Reducir rotación de personal a 8%│   ├── README.md

│   └── scripts/

---│       ├── crear_datawarehouse.sql

│       ├── olap_views.sql       # Cubo OLAP con ROLLUP

## 🌐 Endpoints API│       ├── crear_bsc.sql        # Tablas BSC/OKR

│       ├── consultas_analisis.sql

**Backend:** http://localhost:5000│       └── procedimientos_seguros_dw.sql

│

| Endpoint | Descripción |├── docs/                         # Documentación

|----------|-------------|│   └── README.md

| `/api/estado` | Estado del backend |│

| `/api/tablero` | Tablero consolidado BSC |└── logs/                         #  Archivos de log

| `/api/perspectivas/<nombre>` | Datos por perspectiva |```

| `/api/okr/<codigo_kr>` | Detalle de un KR específico |

| `/api/okr/<codigo_kr>/historial` | Historial de mediciones |---

| `/api/okr/<codigo_kr>/registrar` | Registrar nueva medición |

## Variables de Entorno

---

El sistema utiliza variables de entorno para controlar su comportamiento:

## 🔍 Consultas Útiles

| Variable | Valores | Default | Descripción |

```sql|----------|---------|---------|-------------|

-- Ver todos los OKRs con progreso| `ETL_AMBIENTE` | local, distribuido, test | local | Selecciona configuración de conexiones |

SELECT | `ETL_DRY_RUN` | 0, 1 | 0 | Modo simulación (no escribe en BD) |

    kr.codigo_kr,| `ETL_LOG_LEVEL` | DEBUG, INFO, WARNING, ERROR | INFO | Nivel de detalle de logs |

    kr.nombre,

    kr.valor_inicial,### Ejemplo de uso:

    kr.meta_objetivo,

    ho.valor_observado,```bash

    ROUND(ho.progreso_hacia_meta, 2) as progreso_pct,# macOS / zsh

    ho.estado_semaforoexport ETL_AMBIENTE=local

FROM HechoOKR hoexport ETL_DRY_RUN=0

INNER JOIN DimKR kr ON ho.id_kr = kr.id_kr;export ETL_LOG_LEVEL=DEBUG

python src/etl/etl_incremental.py

-- Ver resumen por perspectiva

SELECT # Para una sola ejecución

    perspectiva,ETL_LOG_LEVEL=WARNING ETL_DRY_RUN=1 python src/etl/etl_incremental.py

    COUNT(*) as total_objetivos,```

    ROUND(AVG(avance_objetivo_porcentaje), 2) as avance_promedio

FROM vw_bsc_tablero_consolidado## Comandos Principales

GROUP BY perspectiva;

```bash

-- Ver top defectos por proyecto# Generar datos de prueba

SELECT python 01_GestionProyectos/datos/generar_datos_final.py

    dp.nombre_proyecto,

    COUNT(*) as total_defectos,# Ejecutar ETL incremental

    SUM(CASE WHEN severidad = 'Crítica' THEN 1 ELSE 0 END) as criticospython src/etl/etl_incremental.py

FROM HechoDefecto hd

INNER JOIN DimProyecto dp ON hd.id_proyecto = dp.id_proyecto# Ejecutar ETL con procedimiento almacenado

GROUP BY dp.nombre_proyectopython 02_ETL/scripts/etl_final.py

ORDER BY total_defectos DESC

LIMIT 10;# Iniciar Dashboard DSS

```cd 03_Dashboard

./iniciar_dashboard.sh

---

# Detener Dashboard

## 🧪 Testingcd 03_Dashboard

./detener_dashboard.sh

Ejecuta el script de verificación completa:```



```bash---

./verificar_sistema.sh

```## Documentación Adicional



**Tests ejecutados:**Ver cada módulo para documentación específica:

- ✅ 7 tests de base de datos origen- [01_GestionProyectos/README.md](01_GestionProyectos/README.md) - Base de datos origen

- ✅ 7 tests de DataWarehouse- [02_ETL/README.md](02_ETL/README.md) - Proceso ETL

- ✅ 4 tests de BSC y OKRs- [03_Dashboard/README.md](03_Dashboard/README.md) - Dashboard web

- ✅ 2 tests de métricas calculadas- [04_Datawarehouse/README.md](04_Datawarehouse/README.md) - Data Warehouse

- ✅ 2 tests de vistas

- ✅ 1 test de dashboard---



**Total:** 23 tests automatizados## Licencia



---Proyecto educativo para demostración de conceptos ETL y Data Warehouse.



## 🚨 Solución de Problemas---



### Error: "Can't connect to MySQL server"**Si te resulta útil, dale una estrella al repositorio.**

```bash

# macOSEste proyecto implementa un sistema ETL (Extract, Transform, Load) distribuido que opera en 3 máquinas independientes para procesar datos de gestión de proyectos.

brew services start mysql

## 🏗 Arquitectura del Sistema

# Linux

sudo systemctl start mysql```

```┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐

│   MÁQUINA 1     │────▶│   MÁQUINA 2     │────▶│   MÁQUINA 3     │

### Dashboard no carga│ GestionProyectos│     │      ETL        │     │  Datawarehouse  │

```bash│                 │     │                 │     │                 │

cd 03_Dashboard│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │

./detener_dashboard.sh│ │ MySQL       │ │     │ │ Python ETL  │ │     │ │ MySQL       │ │

./iniciar_dashboard.sh│ │ BD Origen   │ │     │ │ Procesador  │ │     │ │ BD Destino  │ │

```│ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │

└─────────────────┘     └─────────────────┘     └─────────────────┘

### Ver logs      Datos              Transformar           Datawarehouse

```bash```

tail -f 03_Dashboard/logs/backend.log

```## Estructura del Proyecto



---```

ProyectoETL/

## 📊 Capturas de Dashboard├── README.md                           # Este archivo

├── README_CONFIGURACION.md             # Guía detallada de configuración

**Vista Consolidada:**├── requirements.txt                    # Dependencias Python

- Tablero con 5 objetivos estratégicos│

- Progresos por perspectiva (🟢 🟡 🔴)├── GestionProyectos/                   #  MÁQUINA 1

- Total de 10 Key Results monitoreados│   ├── config_conexion.py             # Configuración de conexiones

│   └── setup_servidor_bd.py           # Configurador automático BD origen

**Vista Detalle:**│

- Valores inicial, meta, y observado├── ETL/                               # MÁQUINA 2

- Cálculo automático de progreso│   ├── etl_distribuido.py             # ETL principal para 3 máquinas

- Historial de mediciones│   ├── etl_principal.py               # ETL original (mejorado)

│   ├── etl_remoto_portable.py         # ETL portable simplificado

---│   ├── servidor_etl_simple.py         # Servidor HTTP para ETL

│   ├── setup_etl.py                   # Configurador automático ETL

## 🤝 Contribuciones│   ├── setup_local.py                 # 🧪 Setup para pruebas locales

│   ├── api_backend.py                 # API Flask para dashboard

Este proyecto es educativo y está abierto a mejoras:│   └── web-dashboard/                 #  Dashboard Web

│       ├── index.html                 # Interface principal

1. **Fork** el repositorio│       └── dashboard.js               # Lógica del dashboard

2. **Crea** una rama feature (`git checkout -b feature/mejora`)│

3. **Commit** tus cambios (`git commit -am 'Agregar nueva métrica'`)└── Datawarehouse/                     # 🏗 MÁQUINA 3

4. **Push** a la rama (`git push origin feature/mejora`)    ├── generacion_datos.py            # Generador de datos de prueba

5. **Abre** un Pull Request    ├── script_creacion_db.sql         # Script creación BD origen

    ├── script_datawarehouse.sql       # Script creación datawarehouse

---    └── setup_datawarehouse.py         # Configurador automático DW

```

## 📝 Licencia

##  Configuración Rápida

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

### 🧪 Opción 1: Prueba Local (Recomendada para desarrollo)

---

**Una sola máquina - Todo local:**

## 👨‍💻 Autor```bash

cd ETL

Proyecto desarrollado como demostración de:python3 setup_local.py

- Arquitectura de DataWarehouse```

- Implementación de ETLEste comando:

- Balanced Scorecard (BSC)-  Instala dependencias automáticamente

- Dashboard interactivo-  Configura bases de datos locales

- Cálculo automático de métricas-  Genera datos de prueba

-  Ejecuta ETL de prueba

----  Inicia dashboard web en http://localhost:5000

-  Abre interfaz visual en navegador

## 🎓 Uso Educativo

### 🏗 Opción 2: Configuración Distribuida (3 máquinas)

Ideal para:

- ✅ Aprender diseño de DataWarehouse**Máquina 1 (GestionProyectos):**

- ✅ Practicar ETL y transformaciones```bash

- ✅ Implementar BSC con OKRscd GestionProyectos

- ✅ Desarrollar dashboards con Flaskpython3 setup_servidor_bd.py

- ✅ Entender arquitectura estrella```



---**Máquina 2 (ETL):**

```bash

**¡Sistema listo para producción o demostración!** 🚀cd ETL

python3 setup_etl.py

Para transferir a otra máquina, consulta **[PORTABILIDAD.md](PORTABILIDAD.md)**```


**Máquina 3 (Datawarehouse):**
```bash
cd Datawarehouse
python3 setup_datawarehouse.py
```

###  Opción 3: Configuración Manual

Ver [README_CONFIGURACION.md](README_CONFIGURACION.md) para pasos detallados.

##  Ejecución del ETL

### 🧪 Modo Local (Desarrollo):
```bash
cd ETL
python3 setup_local.py    # Setup completo con dashboard
# O componentes individuales:
python3 api_backend.py    # Solo API backend
python3 etl_principal.py  # Solo ETL
```

### 🏗 Modo Distribuido (Producción):
```bash
# Desde la Máquina ETL (Máquina 2):
python3 etl_distribuido.py    # ETL distribuido
python3 etl_remoto_portable.py # ETL portable alternativo
```

###  Dashboard Web:
- **Local:** http://localhost:5000 (se abre automáticamente)
- **API Endpoints:** http://localhost:5000/api/status
- **Dashboard:** Abrir `ETL/web-dashboard/index.html` en navegador

### 📡 Via HTTP (opcional):
```bash
# Iniciar servidor ETL
python3 servidor_etl_simple.py

# Ejecutar ETL remotamente
curl -X POST http://IP_MAQUINA_2:8081/ejecutar-etl
```

## Configuración de Red

### IPs de Ejemplo:
- **Máquina 1:** `192.168.1.100` (GestionProyectos)
- **Máquina 2:** `192.168.1.101` (ETL)
- **Máquina 3:** `192.168.1.102` (Datawarehouse)

### Puertos:
- **3306/TCP:** MySQL (Máquinas 1 y 3)
- **8081/TCP:** Servidor ETL HTTP (Máquina 2, opcional)

### Usuarios BD:
- **Usuario:** `etl_user`
- **Password:** `etl_password_123`

##  Bases de Datos

### Base Origen (Máquina 1): `gestionproyectos_hist`
- **Cliente:** Información de clientes
- **Empleado:** Datos de empleados
- **Equipo:** Equipos de trabajo
- **Estado:** Estados de proyectos/tareas
- **Proyecto:** Proyectos con fechas y costos
- **Tarea:** Tareas individuales de proyectos
- **TareaEquipoHist:** Historial de asignaciones

### Datawarehouse (Máquina 3): `dw_proyectos_hist`
- **DimCliente, DimEmpleado, DimEquipo:** Dimensiones
- **DimProyecto:** Dimensión de proyectos
- **DimTiempo:** Dimensión temporal
- **HechoProyecto:** Métricas de proyectos
- **HechoTarea:** Métricas de tareas

##  Verificación del Sistema

### Comprobar Conectividad:
```bash
# Desde Máquina 2 hacia Máquina 1
telnet 192.168.1.100 3306

# Desde Máquina 2 hacia Máquina 3
telnet 192.168.1.102 3306
```

### Verificar Datos:
```sql
-- En origen (Máquina 1)
SELECT COUNT(*) FROM gestionproyectos_hist.Proyecto;

-- En destino (Máquina 3)
SELECT COUNT(*) FROM dw_proyectos_hist.HechoProyecto;
```

##  Requisitos

### Software:
- **Python 3.6+** (Máquina 2)
- **MySQL/XAMPP** (Máquinas 1 y 3)

### Dependencias Python:
```bash
# Instalación automática en setup_local.py, o manual:
pip install pandas sqlalchemy mysql-connector-python numpy flask flask-cors faker
```

### Red:
- Conectividad TCP entre las 3 máquinas
- Puertos MySQL (3306) abiertos
- Permisos de firewall configurados

##  Solución de Problemas

### Error de Conexión:
1. Verificar que MySQL esté funcionando
2. Comprobar conectividad de red
3. Revisar configuración de firewall
4. Verificar usuarios y permisos MySQL

### Sin Datos en Origen:
1. Ejecutar `generacion_datos.py` en Máquina 1
2. Verificar que hay proyectos cerrados
3. Comprobar estructura de base de datos

### ETL Falla:
1. Verificar conectividad a ambas máquinas
2. Comprobar permisos de usuario `etl_user`
3. Revisar logs de error en consola
4. Verificar estructura del datawarehouse

##  Características del Dashboard Web

###  Interface Visual Completa:
- **Dashboard Principal:** Métricas en tiempo real y gráficos
- **Datos Origen:** Visualización de tablas de la BD transaccional
- **Control ETL:** Ejecución visual del ETL con logs en tiempo real
- **DataWarehouse:** Exploración de dimensiones y hechos
- **Análisis:** Reportes y gráficos de cumplimiento

### 🎮 Controles Interactivos:
-  **Generar Datos:** Botón para crear datos de prueba
-  **Ejecutar ETL:** Control visual con barra de progreso
-  **Visualizar Resultados:** Tablas dinámicas y gráficos
-  **Monitoreo:** Estado de conexiones en tiempo real
-  **Logs ETL:** Console log de la ejecución ETL

### 📱 Responsive Design:
- Interface adaptable a desktop y móvil
- Navegación por tabs y secciones
- Gráficos interactivos con Chart.js
- Bootstrap 5 para styling moderno

## * Seguridad

- Cambiar passwords por defecto en producción
- Usar VPN para conexiones entre máquinas
- Configurar firewall restrictivo
- Monitorear conexiones MySQL
- Realizar backups regulares

## Documentación Adicional

- [README_CONFIGURACION.md](README_CONFIGURACION.md) - Guía detallada de configuración
- Comentarios en código fuente para lógica específica
- Scripts de configuración automática incluidos

---

**Versión:** 1.0  
**Autor:** Sistema ETL Distribuido  
**Fecha:** Octubre 2025

##  Descripción

Este proyecto implementa un sistema ETL completo que:
- Extrae datos de una base de datos transaccional de gestión de proyectos
- Transforma y limpia los datos 
- Carga los datos en un Data Warehouse optimizado para análisis

## 🏗 Arquitectura

### Bases de Datos
- **gestionproyectos_hist**: Base de datos transaccional (fuente)
- **dw_proyectos_hist**: Data Warehouse (destino)

### Componentes
- **ETL Principal**: Proceso completo de extracción, transformación y carga
- **ETL Remoto Portable**: Versión independiente para ejecución remota
- **Servidor ETL**: API HTTP para ejecución remota del ETL
- **Generación de Datos**: Script para poblar la base de datos de prueba

## Estructura del Proyecto

```
ProyectoETL/
├── README.md                    # Este archivo
├── generacion_datos.py          # Script para generar datos de prueba
├── etl_principal.py             # ETL principal local
├── etl_remoto_portable.py       # ETL portable para ejecución remota
├── servidor_etl_simple.py       # Servidor HTTP para ETL remoto
├── config_conexion.py           # Configuración de conexiones
├── script_creacion_db.sql       # Script de creación de BD transaccional
└── script_datawarehouse.sql     # Script de creación del Data Warehouse
```

##  Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

### Dependencias de Python
```bash
pip install pandas sqlalchemy mysql-connector-python
```

### Configuración de Base de Datos

1. **Crear las bases de datos**:
   ```sql
   -- Ejecutar script_creacion_db.sql
   -- Ejecutar script_datawarehouse.sql
   ```

2. **Configurar conexiones**:
   Editar `config_conexion.py` con tus credenciales de MySQL.

##  Uso

### 1. Generación de Datos de Prueba
```bash
python generacion_datos.py
```

### 2. Ejecución del ETL Local
```bash
python etl_principal.py
```

### 3. ETL Remoto Portable
```bash
python etl_remoto_portable.py
```

### 4. Servidor ETL (para acceso HTTP)
```bash
python servidor_etl_simple.py
```
Luego acceder a: `http://localhost:8081`

##  Data Warehouse - Esquema Dimensional

### Tablas de Dimensiones
- **DimCliente**: Información de clientes
- **DimEmpleado**: Datos de empleados  
- **DimEquipo**: Información de equipos
- **DimProyecto**: Detalles de proyectos
- **DimTiempo**: Dimensión temporal

### Tabla de Hechos
- **FactTareas**: Métricas y KPIs de tareas

## Configuración Avanzada

### Conexión Remota
Para habilitar conexiones remotas a MySQL:
1. Configurar `bind-address = 0.0.0.0` en MySQL
2. Crear usuario con permisos remotos
3. Abrir puerto 3306 en firewall

### Variables de Entorno
El sistema soporta configuración via variables de entorno:
- `DB_HOST`: Host de la base de datos
- `DB_PORT`: Puerto de MySQL  
- `DB_USER`: Usuario de base de datos
- `DB_PASSWORD`: Contraseña

##  Funcionalidades

### ETL Principal
-  Extracción de datos transaccionales
-  Transformación y limpieza de datos
-  Carga incremental en Data Warehouse
-  Manejo de dimensiones SCD (Slowly Changing Dimensions)
-  Logging y monitoreo

### ETL Remoto
-  Ejecución independiente
-  Auto-instalación de dependencias
-  Configuración flexible
-  Manejo de errores robusto

### Servidor ETL
-  API REST para ejecución remota
-  Interface web simple
-  Logs de ejecución
-  Estado de procesos

##  Tecnologías Utilizadas

- **Python**: Lenguaje principal
- **Pandas**: Manipulación de datos
- **SQLAlchemy**: ORM y conexiones de base de datos
- **MySQL**: Sistema de gestión de base de datos
- **HTTP Server**: Para API remota

##  Licencia

Este proyecto está bajo la Licencia MIT - ver archivo LICENSE para detalles.

##  Contribución

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o preguntas, crear un issue en el repositorio.
