# 📦 GUÍA DE MÓDULOS INDEPENDIENTES

## 🎯 Objetivo

Esta guía explica cómo usar cada módulo del proyecto de forma **completamente independiente**, permitiendo que cada parte se despliegue y mantenga por separado.

---

## 📊 Resumen de Módulos

| Módulo | Nombre | Propósito | Puede funcionar solo |
|--------|--------|-----------|---------------------|
| **1** | Base de Datos Origen | BD transaccional (OLTP) | ✅ Sí |
| **2** | Dashboard | Vista/Frontend + API | ⚠️  Requiere acceso a Módulos 1 y 3 |
| **3** | Data Warehouse | BD analítica + ETL | ⚠️  Requiere acceso a Módulo 1 |

---

## 📦 MÓDULO 1: Base de Datos de Gestión

### Descripción
Base de datos transaccional que almacena proyectos, empleados, clientes y tareas con seguridad mediante stored procedures.

### Archivos Incluidos
```
01_GestionProyectos/
├── README.md
├── requirements.txt           ⭐ Nuevo
├── .env.example              ⭐ Nuevo
├── setup_bd_origen.sh        ⭐ Nuevo
├── scripts/
│   ├── crear_bd_origen.sql
│   ├── procedimientos_seguros.sql
│   ├── generar_datos.py
│   └── generar_datos_seguro.py
└── datos/
```

### Instalación Independiente

```bash
# 1. Copiar la carpeta 01_GestionProyectos a cualquier ubicación
cp -r 01_GestionProyectos /ruta/destino/

# 2. Entrar a la carpeta
cd /ruta/destino/01_GestionProyectos

# 3. Ejecutar instalación
./setup_bd_origen.sh
```

### Configuración

Edita el archivo `.env`:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestionproyectos_hist
DB_USER=root
DB_PASSWORD=tu_password
```

### Uso

```bash
# Generar datos de prueba
python scripts/generar_datos_seguro.py

# Consultar datos (usando MySQL)
mysql -u root -p gestionproyectos_hist
```

### Expone

- **Host**: `localhost` (o IP del servidor)
- **Puerto**: `3306`
- **Base de datos**: `gestionproyectos_hist`
- **Usuario para otros módulos**: `etl_user` (crear con permisos de lectura)

### Dependencias
- Python 3.8+
- MySQL 8.0+
- Ver `requirements.txt`

---

## 📦 MÓDULO 2: Dashboard (Frontend + Backend)

### Descripción
Dashboard web interactivo con API Flask que permite visualizar y gestionar datos de los módulos 1 y 3.

### Archivos Incluidos
```
03_Dashboard/
├── README.md
├── requirements.txt           ⭐ Nuevo
├── .env.example              ⭐ Nuevo
├── setup_dashboard.sh        ⭐ Nuevo
├── iniciar_dashboard.sh      ⭐ Nuevo
├── detener_dashboard.sh      ⭐ Nuevo
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── logs/                     ⭐ Nuevo
```

### Instalación Independiente

```bash
# 1. Copiar la carpeta 03_Dashboard a cualquier ubicación
cp -r 03_Dashboard /ruta/destino/

# 2. Entrar a la carpeta
cd /ruta/destino/03_Dashboard

# 3. Ejecutar instalación
./setup_dashboard.sh
```

### Configuración

Edita el archivo `.env`:
```bash
# Backend
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Conexión a BD Origen (Módulo 1)
DB_ORIGEN_HOST=192.168.1.100  # IP del servidor del Módulo 1
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password

# Conexión a Data Warehouse (Módulo 3)
DB_DW_HOST=192.168.1.102      # IP del servidor del Módulo 3
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=etl_user
DB_DW_PASSWORD=etl_password
```

### Uso

```bash
# Iniciar dashboard completo
./iniciar_dashboard.sh

# O iniciar manualmente:

# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
python -m http.server 8080

# Acceder en navegador
http://localhost:8080/index.html
```

### Detener

```bash
./detener_dashboard.sh
```

### Requiere Acceso a

- **Módulo 1**: Para leer datos origen
- **Módulo 3**: Para leer datos del Data Warehouse

### Dependencias
- Python 3.8+
- Ver `requirements.txt`
- Acceso a BD del Módulo 1 (lectura)
- Acceso a BD del Módulo 3 (lectura)

---

## 📦 MÓDULO 3: Data Warehouse

### Descripción
Data Warehouse con modelo dimensional para análisis y proceso ETL integrado.

### Archivos Incluidos
```
04_Datawarehouse/
├── README.md
├── requirements.txt           ⭐ Nuevo
├── .env.example              ⭐ Nuevo
├── setup_dw.sh               ⭐ Nuevo
├── scripts/
│   ├── crear_datawarehouse.sql
│   ├── procedimientos_seguros_dw.sql
│   └── consultas_analisis.sql
└── etl/                      ⭐ Nuevo (copiar de 02_ETL)
    ├── etl_dw.py
    └── config_conexion.py
```

### Instalación Independiente

```bash
# 1. Copiar la carpeta 04_Datawarehouse a cualquier ubicación
cp -r 04_Datawarehouse /ruta/destino/

# 2. Copiar también el código ETL
cp -r 02_ETL/scripts/* /ruta/destino/04_Datawarehouse/etl/
cp 02_ETL/config/config_conexion.py /ruta/destino/04_Datawarehouse/etl/

# 3. Entrar a la carpeta
cd /ruta/destino/04_Datawarehouse

# 4. Ejecutar instalación
./setup_dw.sh
```

### Configuración

Edita el archivo `.env`:
```bash
# Data Warehouse
DB_DW_HOST=localhost
DB_DW_PORT=3306
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=root
DB_DW_PASSWORD=tu_password

# Conexión a BD Origen (para ETL)
DB_ORIGEN_HOST=192.168.1.100  # IP del servidor del Módulo 1
DB_ORIGEN_PORT=3306
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password
```

### Uso

```bash
# Ejecutar ETL (cargar datos desde Módulo 1)
python etl/etl_dw.py

# Ejecutar consultas de análisis
mysql -u root -p < scripts/consultas_analisis.sql
```

### Expone

- **Host**: `localhost` (o IP del servidor)
- **Puerto**: `3306`
- **Base de datos**: `dw_proyectos_hist`
- **Usuario para otros módulos**: `etl_user` (crear con permisos de lectura)

### Requiere Acceso a

- **Módulo 1**: Para extraer datos (ETL)

### Dependencias
- Python 3.8+
- MySQL 8.0+
- Ver `requirements.txt`
- Acceso a BD del Módulo 1 (lectura)

---

## 🌐 Escenarios de Despliegue

### Escenario 1: Todo Local (Desarrollo)
```
Máquina Local
├── Módulo 1 (localhost:3306)
├── Módulo 2 (localhost:5001 + :8080)
└── Módulo 3 (localhost:3306)
```

### Escenario 2: 3 Máquinas Separadas (Producción)
```
Máquina 1 (192.168.1.100)
└── Módulo 1

Máquina 2 (192.168.1.101)
└── Módulo 2
    ├── Conecta a → 192.168.1.100 (Módulo 1)
    └── Conecta a → 192.168.1.102 (Módulo 3)

Máquina 3 (192.168.1.102)
└── Módulo 3
    └── Conecta a → 192.168.1.100 (Módulo 1)
```

### Escenario 3: Nube (AWS, Azure, GCP)
```
Servidor BD 1 (RDS/CloudSQL)
└── Módulo 1

Servidor Web (EC2/VM)
└── Módulo 2

Servidor BD 2 (RDS/CloudSQL)
└── Módulo 3
```

---

## 🔐 Crear Usuario para Conexiones Entre Módulos

```sql
-- En Módulo 1 (BD Origen)
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON gestionproyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;

-- En Módulo 3 (Data Warehouse)
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON dw_proyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

---

## 📦 Empaquetar para Envío

### Comprimir cada módulo

```bash
# Módulo 1
cd ProyectoETL
zip -r Modulo1_BD_Origen.zip 01_GestionProyectos/ -x "*/datos/*" "*/venv/*"

# Módulo 2
zip -r Modulo2_Dashboard.zip 03_Dashboard/ -x "*/logs/*" "*/venv/*"

# Módulo 3
zip -r Modulo3_DataWarehouse.zip 04_Datawarehouse/ 02_ETL/ -x "*/venv/*"
```

### Descomprimir en destino

```bash
# Receptor del Módulo 1
unzip Modulo1_BD_Origen.zip
cd 01_GestionProyectos
./setup_bd_origen.sh

# Receptor del Módulo 2
unzip Modulo2_Dashboard.zip
cd 03_Dashboard
./setup_dashboard.sh

# Receptor del Módulo 3
unzip Modulo3_DataWarehouse.zip
cd 04_Datawarehouse
./setup_dw.sh
```

---

## ✅ Checklist de Independencia

### Antes de Enviar Cada Módulo

- [ ] Incluir `requirements.txt`
- [ ] Incluir `.env.example`
- [ ] Incluir script de instalación (`setup_*.sh`)
- [ ] Incluir README con instrucciones
- [ ] Probar instalación en máquina limpia
- [ ] Documentar conexiones requeridas
- [ ] Verificar que no haya rutas absolutas hardcodeadas

---

## 🚀 Orden de Instalación Recomendado

1. **Primero**: Módulo 1 (BD Origen)
   - Es la base de datos fuente
   - No depende de nadie

2. **Segundo**: Módulo 3 (Data Warehouse)
   - Necesita conectarse al Módulo 1
   - Ejecutar ETL para poblar

3. **Tercero**: Módulo 2 (Dashboard)
   - Necesita ambos módulos funcionando
   - Configurar conexiones a ambos

---

## 📞 Preguntas Frecuentes

### ¿Puedo usar cada módulo por separado?

- **Módulo 1**: ✅ Sí, completamente independiente
- **Módulo 2**: ⚠️  No, necesita acceso a Módulos 1 y 3
- **Módulo 3**: ⚠️  No, necesita acceso a Módulo 1 para ETL

### ¿Cómo comunico los módulos en diferentes servidores?

1. Configura los archivos `.env` con las IPs correctas
2. Asegúrate de que los puertos MySQL (3306) estén abiertos
3. Crea usuarios con permisos de acceso remoto

### ¿Qué pasa si solo quiero enviar un módulo?

Cada módulo puede ser enviado por separado siempre que:
- Incluyas todos los archivos de ese módulo
- Documentes qué conexiones necesita
- El receptor configure el `.env` correctamente

---

**Estado**: ✅ Módulos preparados para independencia  
**Próximo paso**: Probar cada módulo en máquinas separadas

[Volver](README.md)
