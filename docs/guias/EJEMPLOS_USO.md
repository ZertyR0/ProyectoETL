# 🎯 EJEMPLOS DE USO - ProyectoETL

## 🚀 Escenarios Comunes

### Escenario 1: Primera vez usando el proyecto

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
cd ~/Documents/GitHub
git clone <url-del-repo>
cd ProyectoETL

# 2. Verificar requisitos
python3 --version  # Debe ser 3.8+
mysql --version    # Debe estar instalado

# 3. Verificar el sistema
./verificar_sistema.sh

# 4. Configurar todo automáticamente
./setup_local.sh

# 5. Iniciar el dashboard
./iniciar_dashboard.sh

# El navegador se abrirá automáticamente en http://localhost:8080
```

---

### Escenario 2: Uso diario del dashboard

```bash
# Día 1
./iniciar_dashboard.sh
# Trabajar con el dashboard...
./detener_dashboard.sh

# Día 2
./iniciar_dashboard.sh
# Seguir trabajando...
./detener_dashboard.sh
```

---

### Escenario 3: Generar nuevos datos y procesarlos

```bash
# 1. Iniciar el dashboard
./iniciar_dashboard.sh

# 2. En el navegador (http://localhost:8080):
#    - Click en "Insertar Datos" (genera más clientes, proyectos, tareas)
#    - Click en "Ejecutar ETL" (procesa los nuevos datos)
#    - Ver las métricas actualizadas

# 3. Ver datos directamente en MySQL
mysql -u root gestionproyectos_hist -e "SELECT COUNT(*) as total_proyectos FROM Proyecto"
mysql -u root dw_proyectos_hist -e "SELECT COUNT(*) as hechos_proyectos FROM HechoProyecto"
```

---

### Escenario 4: Análisis de datos en el DW

```bash
# Conectar al datawarehouse
mysql -u root dw_proyectos_hist

# Dentro de MySQL, ejecutar consultas:
```

```sql
-- 1. Resumen general
SELECT * FROM v_resumen_proyectos LIMIT 10;

-- 2. Proyectos con sobrecosto
SELECT 
    dp.nombre_proyecto,
    hp.presupuesto,
    hp.costo_real,
    hp.porcentaje_sobrecosto
FROM HechoProyecto hp
JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
WHERE hp.porcentaje_sobrecosto > 10
ORDER BY hp.porcentaje_sobrecosto DESC;

-- 3. Eficiencia por empleado
SELECT 
    de.nombre,
    de.puesto,
    COUNT(*) as proyectos,
    AVG(hp.eficiencia_horas) as eficiencia_promedio
FROM HechoProyecto hp
JOIN DimEmpleado de ON hp.id_empleado_gerente = de.id_empleado
GROUP BY de.id_empleado, de.nombre, de.puesto
ORDER BY eficiencia_promedio DESC;

-- 4. Tendencia por mes
SELECT 
    dt.anio,
    dt.nombre_mes,
    COUNT(*) as proyectos_finalizados,
    AVG(hp.duracion_real) as duracion_promedio
FROM HechoProyecto hp
JOIN DimTiempo dt ON hp.id_tiempo_fin_real = dt.id_tiempo
GROUP BY dt.anio, dt.mes, dt.nombre_mes
ORDER BY dt.anio, dt.mes;

-- 5. Clientes más rentables
SELECT 
    dc.nombre as cliente,
    dc.sector,
    COUNT(*) as proyectos_totales,
    SUM(hp.presupuesto) as presupuesto_total,
    SUM(hp.costo_real) as costo_total,
    SUM(hp.presupuesto - hp.costo_real) as margen_total
FROM HechoProyecto hp
JOIN DimCliente dc ON hp.id_cliente = dc.id_cliente
GROUP BY dc.id_cliente, dc.nombre, dc.sector
ORDER BY margen_total DESC;
```

---

### Escenario 5: Ejecutar ETL manualmente

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar ETL con logs detallados
python3 02_ETL/scripts/etl_principal.py local 2>&1 | tee etl_$(date +%Y%m%d_%H%M%S).log

# Ver el log generado
ls -lh etl_*.log
cat etl_*.log
```

---

### Escenario 6: Generar más datos de prueba

```bash
# Opción A: Desde el dashboard
./iniciar_dashboard.sh
# Click en "Insertar Datos" en el navegador

# Opción B: Manualmente
source venv/bin/activate
python3 01_GestionProyectos/scripts/generar_datos.py
```

---

### Escenario 7: Limpiar y reiniciar todo

```bash
# 1. Detener el dashboard si está corriendo
./detener_dashboard.sh

# 2. Limpiar bases de datos
mysql -u root -e "DROP DATABASE IF EXISTS gestionproyectos_hist"
mysql -u root -e "DROP DATABASE IF EXISTS dw_proyectos_hist"

# 3. Reconfigurar todo
./setup_local.sh

# 4. Iniciar de nuevo
./iniciar_dashboard.sh
```

---

### Escenario 8: Depurar problemas

```bash
# 1. Verificar estado del sistema
./verificar_sistema.sh

# 2. Ver procesos corriendo
ps aux | grep python

# 3. Ver puertos ocupados
lsof -i :5001
lsof -i :8080

# 4. Ver logs del backend
cat 03_Dashboard/backend/backend.log

# 5. Probar conexión MySQL
mysql -u root -e "SELECT 1"
mysql -u root gestionproyectos_hist -e "SHOW TABLES"
mysql -u root dw_proyectos_hist -e "SHOW TABLES"

# 6. Verificar dependencias Python
source venv/bin/activate
pip list | grep -i flask
pip list | grep -i pandas
pip list | grep -i mysql
```

---

### Escenario 9: Exportar datos para análisis

```bash
# Exportar proyectos a CSV
mysql -u root dw_proyectos_hist -e "
    SELECT * FROM v_resumen_proyectos
" | sed 's/\t/,/g' > resumen_proyectos.csv

# Exportar métricas a JSON
mysql -u root dw_proyectos_hist -e "
    SELECT 
        dp.nombre_proyecto,
        hp.presupuesto,
        hp.costo_real,
        hp.duracion_real,
        hp.porcentaje_completado
    FROM HechoProyecto hp
    JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
" --json > metricas.json

# Ver archivos generados
ls -lh *.csv *.json
```

---

### Escenario 10: Monitoreo continuo

```bash
# Terminal 1: Iniciar dashboard
./iniciar_dashboard.sh

# Terminal 2: Ver logs en tiempo real
tail -f 03_Dashboard/backend/backend.log

# Terminal 3: Monitorear bases de datos
watch -n 5 "mysql -u root gestionproyectos_hist -e 'SELECT COUNT(*) as proyectos FROM Proyecto'"
```

---

## 🔧 Comandos Útiles MySQL

```sql
-- Ver estructura de la BD origen
USE gestionproyectos_hist;
SHOW TABLES;
DESCRIBE Proyecto;
DESCRIBE Tarea;

-- Ver estructura del DW
USE dw_proyectos_hist;
SHOW TABLES;
DESCRIBE HechoProyecto;
DESCRIBE DimTiempo;

-- Ver índices
SHOW INDEX FROM HechoProyecto;

-- Estadísticas de tablas
SELECT 
    table_name,
    table_rows,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'dw_proyectos_hist'
ORDER BY (data_length + index_length) DESC;
```

---

## 📊 API del Dashboard

```bash
# Verificar que la API está corriendo
curl http://localhost:5001/

# Ver estado de conexiones
curl http://localhost:5001/status

# Obtener datos de origen
curl http://localhost:5001/datos-origen

# Obtener datos del datawarehouse
curl http://localhost:5001/datos-datawarehouse

# Ejecutar ETL via API
curl -X POST http://localhost:5001/ejecutar-etl

# Insertar datos via API
curl -X POST http://localhost:5001/insertar-datos

# Limpiar datos via API
curl -X DELETE http://localhost:5001/limpiar-datos
```

---

## 🎓 Ejercicios Sugeridos

### Ejercicio 1: Análisis Básico
1. Inicia el dashboard
2. Inserta datos
3. Ejecuta el ETL
4. Identifica los 3 proyectos con mayor sobrecosto
5. Calcula la eficiencia promedio de todos los proyectos

### Ejercicio 2: Análisis Temporal
1. Genera datos para diferentes meses
2. Ejecuta el ETL
3. Analiza tendencias mensuales de duración de proyectos
4. Identifica qué meses tienen mejor cumplimiento

### Ejercicio 3: Análisis por Cliente
1. Identifica qué sectores son más rentables
2. Calcula el margen promedio por sector
3. Encuentra los clientes más problemáticos (retrasos, sobrecostos)

### Ejercicio 4: Optimización
1. Mide el tiempo de ejecución del ETL
2. Analiza qué tablas tienen más registros
3. Propón optimizaciones

---

## 💡 Tips y Trucos

### Tip 1: Desarrollo Rápido
```bash
# Alias útiles (agregar a ~/.zshrc o ~/.bashrc)
alias etl-start="cd ~/Documents/GitHub/ProyectoETL && ./iniciar_dashboard.sh"
alias etl-stop="cd ~/Documents/GitHub/ProyectoETL && ./detener_dashboard.sh"
alias etl-verify="cd ~/Documents/GitHub/ProyectoETL && ./verificar_sistema.sh"
```

### Tip 2: Ver logs en tiempo real con colores
```bash
tail -f 03_Dashboard/backend/backend.log | grep --color=always -E "ERROR|WARNING|INFO"
```

### Tip 3: Backup rápido de datos
```bash
# Backup
mysqldump -u root gestionproyectos_hist > backup_origen_$(date +%Y%m%d).sql
mysqldump -u root dw_proyectos_hist > backup_dw_$(date +%Y%m%d).sql

# Restore
mysql -u root gestionproyectos_hist < backup_origen_20251022.sql
mysql -u root dw_proyectos_hist < backup_dw_20251022.sql
```

### Tip 4: Monitor de recursos
```bash
# Ver uso de MySQL
ps aux | grep mysql
top -p $(pgrep mysql)

# Ver uso de Python
ps aux | grep python
```

---

## 🎯 Próximos Pasos

Una vez que domines el uso local, puedes:

1. **Explorar configuración distribuida** - Ver `GUIA_DESPLIEGUE_3_MAQUINAS.md`
2. **Agregar más visualizaciones** - Modificar el frontend
3. **Crear nuevas consultas** - Agregar análisis personalizados
4. **Optimizar el ETL** - Mejorar performance
5. **Automatizar con cron** - Ejecutar ETL periódicamente

---

**¿Preguntas?** Consulta `README_COMPLETO.md` o `GUIA_PRUEBA_LOCAL.md`
