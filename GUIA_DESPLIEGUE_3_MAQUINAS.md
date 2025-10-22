# 🚀 Guía de Despliegue en 3 Máquinas

Esta guía te ayudará a configurar tu sistema ETL en 3 máquinas diferentes para máximo rendimiento y separación de responsabilidades.

## 🏗️ Arquitectura de 3 Máquinas

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   MÁQUINA 1        │    │   MÁQUINA 2        │    │   MÁQUINA 3        │
│   BD ORIGEN        │◄──►│   ETL + DASHBOARD   │◄──►│   DATAWAREHOUSE    │
│                    │    │                    │    │                    │
│ • MySQL Server     │    │ • Python ETL       │    │ • MySQL Server     │
│ • gestionproyectos │    │ • Flask API        │    │ • dw_proyectos_hist│
│ • Puerto 3306      │    │ • Dashboard Web    │    │ • Puerto 3306      │
│ • Usuario: etl_user│    │ • Puerto 5001      │    │ • Usuario: etl_user│
│                    │    │                    │    │                    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
       172.26.163.200           172.26.163.201           172.26.164.100
```

## 📋 Pre-requisitos

### En todas las máquinas:
- MySQL Server 8.0+
- Python 3.8+
- Git

### Puertos que deben estar abiertos:
- **3306**: MySQL (en máquinas 1 y 3)
- **5001**: Flask API (en máquina 2)
- **8000**: Frontend web (en máquina 2, opcional)

## 🔧 Configuración por Máquina

### 🖥️ MÁQUINA 1: Base de Datos Origen
**IP: 172.26.163.200**

#### 1. Instalar MySQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS
brew install mysql
```

#### 2. Configurar MySQL para acceso remoto
```bash
sudo mysql -u root -p
```

```sql
-- Crear usuario ETL
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';

-- Crear base de datos
CREATE DATABASE gestionproyectos_hist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;

-- Verificar usuario
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';
```

#### 3. Configurar MySQL para conexiones remotas
```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

Cambiar:
```ini
bind-address = 0.0.0.0  # Era 127.0.0.1
```

```bash
sudo systemctl restart mysql
sudo systemctl enable mysql
```

#### 4. Configurar firewall
```bash
# Ubuntu/Debian
sudo ufw allow 3306

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

#### 5. Crear estructura de BD
```bash
# Clonar proyecto
git clone https://github.com/ZertyR0/ProyectoETL.git
cd ProyectoETL

# Crear estructura
mysql -u etl_user -petl_password_123 gestionproyectos_hist < 01_GestionProyectos/scripts/crear_bd_origen.sql
```

#### 6. Generar datos de prueba
```bash
cd 01_GestionProyectos/scripts
pip install -r requirements.txt
python generar_datos.py
```

### 🔄 MÁQUINA 2: ETL + Dashboard
**IP: 172.26.163.201**

#### 1. Clonar proyecto
```bash
git clone https://github.com/ZertyR0/ProyectoETL.git
cd ProyectoETL
```

#### 2. Configurar ambiente Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configurar variables de ambiente
```bash
nano ~/.bashrc
```

Agregar:
```bash
# Configuración ETL Distribuido
export ETL_AMBIENTE=distribuido

# Base de datos origen (Máquina 1)
export ETL_HOST_ORIGEN=172.26.163.200
export ETL_PORT_ORIGEN=3306
export ETL_USER_ORIGEN=etl_user
export ETL_PASSWORD_ORIGEN=etl_password_123
export ETL_DB_ORIGEN=gestionproyectos_hist

# Datawarehouse (Máquina 3)
export ETL_HOST_DESTINO=172.26.164.100
export ETL_PORT_DESTINO=3306
export ETL_USER_DESTINO=etl_user
export ETL_PASSWORD_DESTINO=etl_password_123
export ETL_DB_DESTINO=dw_proyectos_hist
```

```bash
source ~/.bashrc
```

#### 4. Probar conexiones
```bash
cd 02_ETL/config
python config_conexion.py distribuido
```

#### 5. Configurar servicios
```bash
# Crear archivo de servicio para ETL
sudo nano /etc/systemd/system/etl-dashboard.service
```

```ini
[Unit]
Description=ETL Dashboard Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ProyectoETL/03_Dashboard/backend
Environment=ETL_AMBIENTE=distribuido
Environment=ETL_HOST_ORIGEN=172.26.163.200
Environment=ETL_HOST_DESTINO=172.26.164.100
Environment=ETL_USER_ORIGEN=etl_user
Environment=ETL_PASSWORD_ORIGEN=etl_password_123
Environment=ETL_USER_DESTINO=etl_user
Environment=ETL_PASSWORD_DESTINO=etl_password_123
Environment=ETL_DB_ORIGEN=gestionproyectos_hist
Environment=ETL_DB_DESTINO=dw_proyectos_hist
ExecStart=/home/ubuntu/ProyectoETL/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable etl-dashboard
```

#### 6. Configurar firewall
```bash
# Ubuntu/Debian
sudo ufw allow 5001
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 🏢 MÁQUINA 3: Datawarehouse
**IP: 172.26.164.100**

#### 1. Instalar MySQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
```

#### 2. Configurar MySQL
```bash
sudo mysql -u root -p
```

```sql
-- Crear usuario ETL
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';

-- Crear base de datos
CREATE DATABASE dw_proyectos_hist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON dw_proyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

#### 3. Configurar acceso remoto
```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

```ini
bind-address = 0.0.0.0
```

```bash
sudo systemctl restart mysql
sudo systemctl enable mysql
```

#### 4. Configurar firewall
```bash
# Ubuntu/Debian
sudo ufw allow 3306

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

#### 5. Crear estructura del datawarehouse
```bash
# Clonar proyecto
git clone https://github.com/ZertyR0/ProyectoETL.git
cd ProyectoETL

# Crear estructura
mysql -u etl_user -petl_password_123 dw_proyectos_hist < 04_Datawarehouse/scripts/crear_datawarehouse.sql
```

## 🚀 Despliegue y Ejecución

### 1. Iniciar servicios en orden:

#### Máquina 1 (BD Origen):
```bash
sudo systemctl start mysql
sudo systemctl status mysql
```

#### Máquina 3 (Datawarehouse):
```bash
sudo systemctl start mysql
sudo systemctl status mysql
```

#### Máquina 2 (ETL + Dashboard):
```bash
# Activar ambiente
source venv/bin/activate

# Probar conexiones
cd 02_ETL/config
python config_conexion.py distribuido

# Iniciar dashboard
sudo systemctl start etl-dashboard
sudo systemctl status etl-dashboard

# O ejecutar manualmente
cd 03_Dashboard/backend
python app.py
```

### 2. Verificar funcionamiento:

#### Acceder al dashboard:
```
http://172.26.163.201:5001
```

#### Probar ETL desde la máquina 2:
```bash
cd 02_ETL/scripts
python etl_principal.py
```

## 🔍 Verificación y Monitoreo

### Verificar conexiones desde máquina 2:
```bash
# Probar conexión a BD origen
mysql -h 172.26.163.200 -u etl_user -petl_password_123 gestionproyectos_hist -e "SELECT COUNT(*) FROM Proyecto;"

# Probar conexión a datawarehouse
mysql -h 172.26.164.100 -u etl_user -petl_password_123 dw_proyectos_hist -e "SELECT COUNT(*) FROM HechoProyecto;"
```

### Logs del sistema:
```bash
# Logs del servicio ETL
sudo journalctl -u etl-dashboard -f

# Logs de MySQL (máquinas 1 y 3)
sudo tail -f /var/log/mysql/error.log
```

## 🛡️ Seguridad

### 1. Configurar SSL para MySQL (recomendado):
```bash
# En máquinas 1 y 3
mysql -u root -p -e "ALTER USER 'etl_user'@'%' REQUIRE SSL;"
```

### 2. Configurar firewall restrictivo:
```bash
# Máquina 1: Solo permitir conexiones desde máquina 2
sudo ufw allow from 172.26.163.201 to any port 3306

# Máquina 3: Solo permitir conexiones desde máquina 2
sudo ufw allow from 172.26.163.201 to any port 3306

# Máquina 2: Permitir acceso web desde red local
sudo ufw allow from 172.26.163.0/24 to any port 5001
sudo ufw allow from 172.26.163.0/24 to any port 8000
```

### 3. Backup automático:
```bash
# Script de backup para máquinas 1 y 3
nano backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Máquina 1
mysqldump -u etl_user -petl_password_123 gestionproyectos_hist > backup_origen_$DATE.sql

# Máquina 3
mysqldump -u etl_user -petl_password_123 dw_proyectos_hist > backup_dw_$DATE.sql
```

## 🚨 Solución de Problemas

### Problema: No se puede conectar a base de datos
```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql

# Verificar puertos
netstat -tlnp | grep 3306

# Verificar firewall
sudo ufw status
```

### Problema: ETL falla
```bash
# Verificar variables de ambiente
env | grep ETL

# Probar conexiones manualmente
cd 02_ETL/config
python config_conexion.py distribuido
```

### Problema: Dashboard no responde
```bash
# Verificar servicio
sudo systemctl status etl-dashboard

# Verificar puertos
netstat -tlnp | grep 5001

# Revisar logs
sudo journalctl -u etl-dashboard --since "10 minutes ago"
```

## 📊 Monitoreo de Rendimiento

### Métricas importantes:
- Tiempo de ejecución ETL
- Uso de CPU/RAM en cada máquina
- Conexiones MySQL activas
- Velocidad de transferencia de datos

### Scripts de monitoreo:
```bash
# CPU y memoria
top -p $(pgrep -f "python.*app.py")

# Conexiones MySQL
mysql -u etl_user -p -e "SHOW PROCESSLIST;"

# Espacio en disco
df -h
```

## ✅ Checklist de Despliegue

### Pre-despliegue:
- [ ] Las 3 máquinas tienen conectividad de red
- [ ] MySQL instalado en máquinas 1 y 3
- [ ] Python 3.8+ instalado en máquina 2
- [ ] Firewall configurado correctamente
- [ ] Usuarios ETL creados

### Post-despliegue:
- [ ] Conexiones de BD funcionando
- [ ] ETL ejecuta sin errores
- [ ] Dashboard accesible vía web
- [ ] Datos se cargan correctamente
- [ ] Logs funcionando
- [ ] Backups configurados

---

**🎉 ¡Tu sistema ETL distribuido está listo para producción!**

Para más ayuda, consulta los archivos README en cada directorio o contacta al equipo de desarrollo.
