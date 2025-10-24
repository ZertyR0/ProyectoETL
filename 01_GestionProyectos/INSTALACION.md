# 📦 Instalación - Módulo 1: Base de Datos de Gestión

## 🎯 Descripción

Este módulo contiene la **Base de Datos Transaccional (OLTP)** del sistema de gestión de proyectos. Puede funcionar de forma **completamente independiente**.

---

## 📋 Requisitos Previos

- **Python 3.8+**
- **MySQL 8.0+**
- **pip** (gestor de paquetes Python)
- **Git** (opcional, para clonar)

---

## 🚀 Instalación Rápida (Automática)

```bash
# 1. Entrar a la carpeta del módulo
cd 01_GestionProyectos

# 2. Ejecutar script de instalación
./setup_bd_origen.sh

# 3. Seguir las instrucciones en pantalla
```

El script hará:
- ✅ Verificar Python y MySQL
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Configurar archivo `.env`
- ✅ Crear la base de datos
- ✅ Instalar stored procedures
- ✅ Generar datos de prueba (opcional)

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

### Paso 3: Configurar Conexión

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gestionproyectos_hist
DB_USER=root
DB_PASSWORD=tu_password_mysql

# Generación de datos
NUM_CLIENTES=20
NUM_PROYECTOS=15
NUM_EMPLEADOS=30
NUM_TAREAS_POR_PROYECTO=10
```

### Paso 4: Crear Base de Datos

```bash
mysql -u root -p < scripts/crear_bd_origen.sql
```

### Paso 5: Instalar Stored Procedures

```bash
mysql -u root -p gestionproyectos_hist < scripts/procedimientos_seguros.sql
```

### Paso 6: Generar Datos de Prueba

```bash
python scripts/generar_datos_seguro.py
```

---

## 🗂️ Estructura de Archivos

```
01_GestionProyectos/
├── README.md                      # Documentación general
├── INSTALACION.md                 # Esta guía
├── requirements.txt               # Dependencias Python
├── .env.example                   # Plantilla de configuración
├── .env                          # Tu configuración (no subir a Git)
├── setup_bd_origen.sh            # Instalación automática
├── scripts/
│   ├── crear_bd_origen.sql       # Crear base de datos y tablas
│   ├── procedimientos_seguros.sql # Stored procedures de seguridad
│   ├── generar_datos.py          # Generador simple
│   └── generar_datos_seguro.py   # Generador con SP seguros
└── datos/
    └── (archivos de prueba)
```

---

## 🧪 Verificar Instalación

### Verificar Base de Datos

```bash
mysql -u root -p

USE gestionproyectos_hist;
SHOW TABLES;
```

Deberías ver:
```
+------------------------------------+
| Tables_in_gestionproyectos_hist    |
+------------------------------------+
| clientes                           |
| empleados                          |
| proyectos                          |
| tareas                             |
| log_cambios                        |
+------------------------------------+
```

### Verificar Stored Procedures

```sql
SHOW PROCEDURE STATUS WHERE Db = 'gestionproyectos_hist';
```

Deberías ver ~10 procedures:
- `sp_insertar_proyecto`
- `sp_actualizar_proyecto`
- `sp_eliminar_proyecto`
- `sp_insertar_empleado`
- etc.

### Verificar Datos

```sql
SELECT COUNT(*) FROM proyectos;
SELECT COUNT(*) FROM empleados;
SELECT COUNT(*) FROM clientes;
SELECT COUNT(*) FROM tareas;
```

---

## 🔐 Crear Usuario para Otros Módulos

Si vas a conectar este módulo con otros (Módulo 2 o Módulo 3):

```sql
-- Conectar a MySQL como root
mysql -u root -p

-- Crear usuario con permisos de lectura
USE gestionproyectos_hist;

CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON gestionproyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

**Importante**: Anota estas credenciales para configurar los otros módulos.

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
mysql -h 192.168.1.100 -u etl_user -p gestionproyectos_hist
```

---

## 📊 Uso del Módulo

### Generar Más Datos

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar generador
python scripts/generar_datos_seguro.py
```

### Consultar Datos

```bash
mysql -u root -p gestionproyectos_hist

-- Proyectos activos
SELECT * FROM proyectos WHERE estado = 'En Progreso';

-- Empleados por proyecto
SELECT p.nombre_proyecto, COUNT(t.id_empleado) as num_empleados
FROM proyectos p
LEFT JOIN tareas t ON p.id_proyecto = t.id_proyecto
GROUP BY p.id_proyecto;
```

### Usar Stored Procedures

```sql
-- Insertar proyecto nuevo
CALL sp_insertar_proyecto(
    'Nuevo Proyecto',
    'Descripción del proyecto',
    '2024-01-01',
    '2024-12-31',
    500000.00,
    'En Progreso',
    1  -- ID del cliente
);

-- Actualizar proyecto
CALL sp_actualizar_proyecto(
    1,  -- ID del proyecto
    'Nombre Actualizado',
    'Nueva descripción',
    '2024-01-15',
    '2024-11-30',
    550000.00,
    'En Progreso'
);
```

---

## 🗑️ Desinstalar

```bash
# 1. Eliminar base de datos
mysql -u root -p -e "DROP DATABASE IF EXISTS gestionproyectos_hist;"

# 2. Eliminar entorno virtual
rm -rf venv/

# 3. Eliminar archivos de configuración
rm .env
```

---

## 🐛 Solución de Problemas

### Error: "Command 'mysql' not found"

**Causa**: MySQL no está instalado o no está en el PATH.

**Solución**:
```bash
# Ubuntu/Debian
sudo apt install mysql-server

# macOS
brew install mysql

# Iniciar MySQL
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS
```

### Error: "Access denied for user 'root'@'localhost'"

**Causa**: Contraseña incorrecta en `.env`.

**Solución**: Verifica la contraseña de MySQL y actualiza el archivo `.env`.

### Error: "Can't connect to MySQL server"

**Causa**: MySQL no está corriendo.

**Solución**:
```bash
# Verificar estado
sudo systemctl status mysql

# Iniciar MySQL
sudo systemctl start mysql
```

### Error: "Table 'gestionproyectos_hist.proyectos' doesn't exist"

**Causa**: No se ejecutó el script de creación de tablas.

**Solución**:
```bash
mysql -u root -p < scripts/crear_bd_origen.sql
```

---

## 📈 Próximos Pasos

1. ✅ Módulo instalado correctamente
2. ⬜ Conectar con **Módulo 3** (Data Warehouse) para análisis
3. ⬜ Conectar con **Módulo 2** (Dashboard) para visualización

---

## 📞 Información de Conexión

Una vez instalado, anota esta información para configurar otros módulos:

```
Host: localhost (o tu IP: ifconfig / ipconfig)
Puerto: 3306
Base de Datos: gestionproyectos_hist
Usuario: etl_user
Password: etl_password_123
```

---

## 📚 Documentación Adicional

- [README del Módulo](README.md)
- [Guía de Módulos Independientes](../GUIA_MODULOS_INDEPENDIENTES.md)
- [Documentación de Seguridad](../docs/seguridad/)

---

**¿Instalación exitosa?** → Continúa con [Módulo 3](../04_Datawarehouse/INSTALACION.md) o [Módulo 2](../03_Dashboard/INSTALACION.md)
