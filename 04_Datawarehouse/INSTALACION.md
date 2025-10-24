# 📦 Instalación - Módulo 3: Data Warehouse

## 🎯 Descripción

Este módulo contiene:
- **Data Warehouse**: Base de datos dimensional para análisis (OLAP)
- **Proceso ETL**: Extracción y carga desde Módulo 1
- **Consultas de análisis**: Queries preconfigurados

⚠️ **Importante**: Este módulo requiere acceso a **Módulo 1** (BD Origen) para ejecutar el ETL.

---

## 📋 Requisitos Previos

- **Python 3.8+**
- **MySQL 8.0+**
- **pip** (gestor de paquetes Python)
- Acceso a **Módulo 1** instalado (BD Origen)

---

## 🚀 Instalación Rápida (Automática)

```bash
# 1. Entrar a la carpeta del módulo
cd 04_Datawarehouse

# 2. Ejecutar script de instalación
./setup_dw.sh

# 3. Seguir las instrucciones en pantalla
```

El script hará:
- ✅ Verificar Python y MySQL
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Configurar archivo `.env`
- ✅ Crear Data Warehouse
- ✅ Instalar stored procedures
- ✅ Verificar conexión a BD Origen

---

## 🔧 Instalación Manual

### Paso 1: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Conexiones

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```bash
# Configuración del Data Warehouse
DB_DW_HOST=localhost
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=root
DB_DW_PASSWORD=tu_password_mysql

# Conexión a BD Origen (para ETL)
DB_ORIGEN_HOST=localhost       # Cambiar si Módulo 1 está en otro servidor
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password_123

# Configuración del ETL
ETL_BATCH_SIZE=1000
ETL_LOG_LEVEL=INFO
```

### Paso 4: Crear Data Warehouse

```bash
mysql -u root -p < scripts/crear_datawarehouse.sql
```

### Paso 5: Instalar Stored Procedures

```bash
mysql -u root -p dw_proyectos_hist < scripts/procedimientos_seguros_dw.sql
```

### Paso 6: Copiar Código ETL

```bash
# Si tienes acceso al Módulo ETL original (02_ETL)
mkdir -p etl
cp ../02_ETL/scripts/etl_principal.py etl/
cp ../02_ETL/scripts/etl_utils.py etl/
cp ../02_ETL/config/config_conexion.py etl/
```

---

## 🗂️ Estructura de Archivos

```
04_Datawarehouse/
├── README.md                           # Documentación general
├── INSTALACION.md                     # Esta guía
├── requirements.txt                   # Dependencias Python
├── .env.example                      # Plantilla de configuración
├── .env                              # Tu configuración (no subir a Git)
├── setup_dw.sh                       # Instalación automática
├── scripts/
│   ├── crear_datawarehouse.sql       # Crear DW y modelo dimensional
│   ├── procedimientos_seguros_dw.sql # Stored procedures
│   └── consultas_analisis.sql        # Queries de análisis
└── etl/
    ├── etl_principal.py              # Proceso ETL principal
    ├── etl_utils.py                  # Utilidades ETL
    └── config_conexion.py            # Configuración de conexiones
```

---

## 🔄 Ejecutar ETL (Cargar Datos)

### Primera Carga (Completa)

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar ETL
python etl/etl_principal.py
```

**Esto hará**:
1. Conectar a BD Origen (Módulo 1)
2. Extraer datos de tablas transaccionales
3. Transformar datos al modelo dimensional
4. Cargar en dimensiones y hechos del Data Warehouse

### Cargas Incrementales

```bash
# Ejecutar ETL periódicamente (ej: cada hora)
python etl/etl_principal.py

# O configurar cron job
crontab -e

# Agregar línea (ejecutar cada hora):
0 * * * * cd /ruta/04_Datawarehouse && ./venv/bin/python etl/etl_principal.py >> logs/etl.log 2>&1
```

---

## 🧪 Verificar Instalación

### 1. Verificar Data Warehouse

```bash
mysql -u root -p

USE dw_proyectos_hist;
SHOW TABLES;
```

Deberías ver:
```
+---------------------------+
| Tables_in_dw_proyectos_hist|
+---------------------------+
| dim_clientes               |
| dim_empleados              |
| dim_proyectos              |
| dim_tiempo                 |
| hecho_tareas               |
| hecho_proyectos            |
+---------------------------+
```

### 2. Verificar Stored Procedures

```sql
SHOW PROCEDURE STATUS WHERE Db = 'dw_proyectos_hist';
```

### 3. Verificar Datos Cargados

```sql
SELECT COUNT(*) FROM dim_proyectos;
SELECT COUNT(*) FROM dim_empleados;
SELECT COUNT(*) FROM dim_clientes;
SELECT COUNT(*) FROM hecho_tareas;
```

### 4. Ejecutar Consultas de Análisis

```bash
mysql -u root -p dw_proyectos_hist < scripts/consultas_analisis.sql
```

---

## 🔐 Crear Usuario para Otros Módulos

Si vas a conectar el Dashboard (Módulo 2) a este Data Warehouse:

```sql
-- Conectar a MySQL como root
mysql -u root -p

-- Crear usuario con permisos de lectura
USE dw_proyectos_hist;

CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON dw_proyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

---

## 🌐 Configurar para Acceso Remoto

Si este módulo estará en un servidor diferente:

### 1. Configurar MySQL para aceptar conexiones remotas

Edita `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
# Cambiar esto:
bind-address = 127.0.0.1

# Por esto:
bind-address = 0.0.0.0
```

### 2. Reiniciar MySQL

```bash
sudo systemctl restart mysql
```

### 3. Abrir puerto en firewall

```bash
# Ubuntu/Debian
sudo ufw allow 3306/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload
```

### 4. Probar conexión desde otra máquina

```bash
mysql -h 192.168.1.102 -u etl_user -p dw_proyectos_hist
```

---

## 📊 Consultas de Análisis

### Proyectos por Estado

```sql
SELECT 
    p.estado,
    COUNT(*) as cantidad,
    SUM(p.presupuesto) as presupuesto_total
FROM dim_proyectos p
GROUP BY p.estado;
```

### Empleados Más Productivos

```sql
SELECT 
    e.nombre_empleado,
    COUNT(h.id_tarea) as tareas_completadas,
    AVG(h.horas_trabajadas) as promedio_horas
FROM dim_empleados e
JOIN hecho_tareas h ON e.id_empleado = h.id_empleado
WHERE h.estado_tarea = 'Completada'
GROUP BY e.id_empleado
ORDER BY tareas_completadas DESC
LIMIT 10;
```

### Análisis Temporal

```sql
SELECT 
    t.anio,
    t.trimestre,
    COUNT(DISTINCT h.id_proyecto) as proyectos_activos,
    SUM(h.horas_trabajadas) as horas_totales
FROM dim_tiempo t
JOIN hecho_tareas h ON t.id_tiempo = h.id_tiempo
GROUP BY t.anio, t.trimestre
ORDER BY t.anio, t.trimestre;
```

---

## 🔄 Automatizar ETL

### Opción 1: Cron Job (Linux/macOS)

```bash
# Editar crontab
crontab -e

# Ejecutar ETL cada hora
0 * * * * cd /ruta/04_Datawarehouse && ./venv/bin/python etl/etl_principal.py >> logs/etl.log 2>&1

# Ejecutar ETL cada día a las 2:00 AM
0 2 * * * cd /ruta/04_Datawarehouse && ./venv/bin/python etl/etl_principal.py >> logs/etl.log 2>&1
```

### Opción 2: Windows Task Scheduler

1. Abrir Task Scheduler
2. Crear nueva tarea
3. Trigger: Diario/Por hora
4. Acción: Ejecutar `python etl/etl_principal.py`

### Opción 3: Script de Monitoreo

Crear `ejecutar_etl.sh`:
```bash
#!/bin/bash
cd /ruta/04_Datawarehouse
source venv/bin/activate

while true; do
    echo "Ejecutando ETL: $(date)"
    python etl/etl_principal.py
    echo "ETL completado. Esperando 1 hora..."
    sleep 3600  # 1 hora
done
```

```bash
chmod +x ejecutar_etl.sh
./ejecutar_etl.sh &
```

---

## 🗑️ Desinstalar

```bash
# 1. Eliminar Data Warehouse
mysql -u root -p -e "DROP DATABASE IF EXISTS dw_proyectos_hist;"

# 2. Eliminar entorno virtual
rm -rf venv/

# 3. Eliminar archivos de configuración
rm .env

# 4. Eliminar logs (si existen)
rm -rf logs/
```

---

## 🐛 Solución de Problemas

### Error: "Can't connect to MySQL server" al ejecutar ETL

**Causa**: No puede conectarse a BD Origen (Módulo 1).

**Solución**:
```bash
# 1. Verificar que Módulo 1 esté corriendo
mysql -h <IP_MODULO1> -u etl_user -p gestionproyectos_hist

# 2. Verificar credenciales en .env
cat .env | grep DB_ORIGEN

# 3. Verificar firewall
# 4. Verificar que el usuario etl_user tenga permisos
```

### Error: "Table doesn't exist" en el Data Warehouse

**Causa**: No se creó el Data Warehouse correctamente.

**Solución**:
```bash
mysql -u root -p < scripts/crear_datawarehouse.sql
```

### ETL muy lento

**Causa**: Demasiados datos para procesar de una vez.

**Solución**:
```bash
# Aumentar el batch size en .env
ETL_BATCH_SIZE=5000

# O ejecutar ETL incremental más frecuentemente
```

### Error: "No module named 'pandas'"

**Causa**: Dependencias no instaladas.

**Solución**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📈 Próximos Pasos

1. ✅ Data Warehouse instalado correctamente
2. ✅ ETL ejecutado al menos una vez
3. ⬜ Automatizar ETL con cron
4. ⬜ Conectar con **Módulo 2** (Dashboard) para visualización
5. ⬜ Crear nuevas consultas de análisis

---

## 📞 Información de Conexión

Una vez instalado, anota esta información para configurar el Dashboard (Módulo 2):

```
Host: localhost (o tu IP: ifconfig / ipconfig)
Puerto: 3306
Base de Datos: dw_proyectos_hist
Usuario: etl_user
Password: etl_password_123
```

---

## 📚 Documentación Adicional

- [README del Módulo](README.md)
- [Modelo Dimensional](MODELO_DIMENSIONAL.md)
- [Guía de Consultas](scripts/consultas_analisis.sql)
- [Guía de Módulos Independientes](../GUIA_MODULOS_INDEPENDIENTES.md)

---

**¿Instalación exitosa?** → Continúa con [Módulo 2](../03_Dashboard/INSTALACION.md) para visualizar los datos 📊
