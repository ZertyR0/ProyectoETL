# 🚀 Guía de Portabilidad - Sistema ETL + BSC

## 📋 Requisitos Previos

Para ejecutar este proyecto en **cualquier máquina**, necesitas:

1. **MySQL 8.0+**
2. **Python 3.8+**
3. **Navegador web** (Chrome, Firefox, Safari, etc.)

## 📦 Transferencia a otra computadora

### Opción 1: Clonar repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd ProyectoETL
```

### Opción 2: Copiar carpeta completa
Simplemente copia la carpeta `ProyectoETL` a la nueva máquina.

## ⚡ Inicialización Rápida (1 comando)

```bash
./inicializar_sistema_completo.sh
```

Este script ejecutará automáticamente:
1. ✅ Verificación de prerequisitos
2. ✅ Creación de bases de datos
3. ✅ Creación de tablas de origen (8 tablas)
4. ✅ Generación de 50 proyectos + métricas
5. ✅ Creación de DataWarehouse (12 dimensiones, 8 hechos)
6. ✅ Ejecución de ETL completo
7. ✅ Población de BSC con OKRs calculados
8. ✅ Inicio de Dashboard

**Tiempo estimado:** 30-60 segundos

## 🔧 Inicialización Manual (paso a paso)

Si prefieres ejecutar cada paso manualmente:

### 1️⃣ Crear bases de datos
```bash
mysql -u root -e "CREATE DATABASE gestionproyectos_hist;"
mysql -u root -e "CREATE DATABASE dw_proyectos_hist;"
```

### 2️⃣ Crear estructura de origen
```bash
mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql
mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/crear_tabla_estado.sql
mysql -u root gestionproyectos_hist < 01_GestionProyectos/scripts/procedimientos_seguros.sql
```

### 3️⃣ Generar datos de prueba
```bash
cd 01_GestionProyectos/datos
python3 generar_datos_final.py
cd ../..
```

**Datos generados:**
- 50 clientes
- 250 empleados
- 50 equipos
- 50 proyectos (con tareas)
- 135 defectos de calidad
- 351 registros de capacitación
- 21 evaluaciones de satisfacción
- 282 movimientos de empleados

### 4️⃣ Crear DataWarehouse
```bash
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/crear_datawarehouse.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/agregar_tablas_metricas.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/crear_bsc.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/olap_views.sql
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/procedimientos_seguros_dw.sql
```

### 5️⃣ Ejecutar ETL
```bash
mysql -u root dw_proyectos_hist < 02_ETL/scripts/etl_completo_con_metricas.sql
echo "CALL sp_etl_completo_con_metricas();" | mysql -u root dw_proyectos_hist
```

### 6️⃣ Poblar BSC con OKRs
```bash
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/poblar_bsc_automatico.sql
```

### 7️⃣ Iniciar Dashboard
```bash
cd 03_Dashboard
./iniciar_dashboard.sh
```

Abrir en navegador: **http://localhost:3000**

## 🎯 Métricas Calculadas (100% desde DW)

El sistema calcula **automáticamente** las siguientes métricas desde el DataWarehouse:

### Perspectiva Financiera 💰
- **Costos promedio** de proyectos
- **Rentabilidad promedio** (margen sobre presupuesto)
- **% proyectos dentro de presupuesto**

### Perspectiva de Clientes 😊
- **Defectos por proyecto** (de tabla `HechoDefecto`)
- **Satisfacción promedio** (de tabla `HechoSatisfaccion`)

### Perspectiva de Procesos Internos ⚙️
- **Horas promedio por tarea**
- **Duración promedio de proyectos**
- **% cumplimiento de tiempos**

### Perspectiva de Aprendizaje e Innovación 📚
- **Horas de capacitación por empleado** (de tabla `HechoCapacitacion`)
- **% rotación de personal** (de tabla `HechoMovimientoEmpleado`)

## 🔄 Actualización de Datos

Para regenerar datos y actualizar métricas:

```bash
# 1. Regenerar datos en origen
cd 01_GestionProyectos/datos
python3 generar_datos_final.py
cd ../..

# 2. Re-ejecutar ETL
echo "CALL sp_etl_completo_con_metricas();" | mysql -u root dw_proyectos_hist

# 3. Actualizar OKRs
mysql -u root dw_proyectos_hist < 04_Datawarehouse/scripts/poblar_bsc_automatico.sql

# 4. Refrescar dashboard (Ctrl+R en navegador)
```

## 🛠️ Solución de Problemas

### ❌ Error: "Access denied for user 'root'"
**Solución:** Verifica tu usuario de MySQL. Si usas otro usuario:
```bash
# Edita los scripts y reemplaza "-u root" por "-u TU_USUARIO"
sed -i '' 's/-u root/-u TU_USUARIO/g' inicializar_sistema_completo.sh
```

### ❌ Error: "Can't connect to MySQL server"
**Solución:** Verifica que MySQL esté corriendo:
```bash
# macOS
brew services start mysql

# Linux
sudo systemctl start mysql

# Windows
net start MySQL
```

### ❌ Error: "ModuleNotFoundError: No module named 'faker'"
**Solución:** Instala dependencias de Python:
```bash
pip3 install -r requirements.txt
```

### ❌ Dashboard no carga
**Solución:** Verifica que los puertos no estén ocupados:
```bash
# Verificar si puertos 3000 y 5000 están libres
lsof -i :3000
lsof -i :5000

# Si están ocupados, detén el proceso o cambia los puertos en:
# 03_Dashboard/backend/app.py (línea: app.run(port=5000))
# 03_Dashboard/frontend/app.js (línea: fetch('http://localhost:5000'))
```

## 📂 Estructura de Archivos Clave

```
ProyectoETL/
├── inicializar_sistema_completo.sh  ← SCRIPT MAESTRO
│
├── 01_GestionProyectos/
│   ├── datos/
│   │   └── generar_datos_final.py   ← Generador de datos con métricas
│   └── scripts/
│       ├── crear_bd_origen.sql      ← Estructura de 8 tablas origen
│       └── procedimientos_seguros.sql
│
├── 02_ETL/
│   └── scripts/
│       └── etl_completo_con_metricas.sql  ← ETL con carga de métricas
│
├── 03_Dashboard/
│   ├── iniciar_dashboard.sh         ← Inicia frontend + backend
│   ├── detener_dashboard.sh         ← Detiene servicios
│   ├── backend/
│   │   └── app.py                   ← API REST (Flask)
│   └── frontend/
│       └── index.html               ← Dashboard BSC
│
└── 04_Datawarehouse/
    └── scripts/
        ├── crear_datawarehouse.sql        ← 12 dimensiones + hechos
        ├── agregar_tablas_metricas.sql    ← 4 tablas de métricas
        ├── crear_bsc.sql                  ← Estructura BSC (objetivos/KRs)
        └── poblar_bsc_automatico.sql      ← OKRs calculados 100% reales
```

## 🔐 Credenciales por Defecto

**MySQL:**
- Usuario: `root`
- Password: (sin password en script, ajusta según tu instalación)

**Bases de datos:**
- Origen: `gestionproyectos_hist`
- DataWarehouse: `dw_proyectos_hist`

## 📊 Verificación de Instalación

Ejecuta estos comandos para verificar que todo funciona:

```bash
# 1. Verificar datos en origen
mysql -u root -e "SELECT COUNT(*) as proyectos FROM gestionproyectos_hist.proyecto;"
mysql -u root -e "SELECT COUNT(*) as defectos FROM gestionproyectos_hist.defecto;"

# 2. Verificar datos en DW
mysql -u root -e "SELECT COUNT(*) as proyectos FROM dw_proyectos_hist.HechoProyecto;"
mysql -u root -e "SELECT COUNT(*) as defectos FROM dw_proyectos_hist.HechoDefecto;"

# 3. Verificar OKRs
mysql -u root -e "SELECT COUNT(*) as okrs FROM dw_proyectos_hist.HechoOKR;"

# 4. Ver métricas calculadas
mysql -u root dw_proyectos_hist -e "SELECT * FROM vw_bsc_tablero_consolidado;"
```

**Salida esperada:**
- 50 proyectos en origen
- 26 proyectos en DW (solo completados/cancelados)
- 135 defectos en origen
- 135 defectos en DW
- 10 OKRs en BSC

## 🚦 Estados del Dashboard

- 🟢 **Verde:** Meta alcanzada o superada
- 🟡 **Amarillo:** Progreso intermedio (50-80% de meta)
- 🔴 **Rojo:** Bajo progreso (<50% de meta)

## 📝 Notas Importantes

1. **No hay valores hardcodeados:** Todas las métricas se calculan desde `HechoProyecto`, `HechoTarea`, `HechoDefecto`, `HechoCapacitacion`, `HechoSatisfaccion`, `HechoMovimientoEmpleado`.

2. **Datos sintéticos:** Los datos son generados con `Faker` para demostración. En producción, conecta con tus fuentes reales.

3. **Actualización automática:** Al ejecutar el generador + ETL + BSC, todas las métricas se recalculan automáticamente.

4. **Portabilidad:** Todo está contenido en archivos SQL y Python. No requiere configuraciones externas.

## 🎓 Uso Educativo

Este proyecto es ideal para:
- ✅ Aprender ETL y DataWarehouse
- ✅ Entender Balanced Scorecard (BSC)
- ✅ Practicar consultas SQL analíticas
- ✅ Visualizar KPIs en tiempo real
- ✅ Implementar arquitectura estrella

## 📞 Soporte

Si tienes problemas, verifica:
1. Logs del dashboard: `03_Dashboard/logs/backend.log`
2. Logs de MySQL: `sudo tail -f /var/log/mysql/error.log`
3. Estado de servicios: `ps aux | grep -E 'python|http-server'`

---

**¡Sistema listo para portar a cualquier máquina con MySQL + Python!** 🎉
