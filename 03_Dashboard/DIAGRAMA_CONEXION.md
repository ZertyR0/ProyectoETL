# 🗺️ Diagrama de Conexión - Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                   CONFIGURACIÓN DE RED                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  COMPUTADORA A       │         │  COMPUTADORA B       │
│  192.168.1.100       │         │  192.168.1.101       │
│                      │         │  (TU COMPUTADORA)    │
│ ┌──────────────────┐ │         │ ┌──────────────────┐ │
│ │  MÓDULO 1        │◄├─────────┤►│  MÓDULO 2        │ │
│ │  BD Origen       │ │ MySQL   │ │  DASHBOARD       │ │
│ │                  │ │ :3306   │ │                  │ │
│ │ gestionproyectos │ │         │ │ Backend :5001    │ │
│ │ _hist            │ │         │ │ Frontend :8080   │ │
│ └──────────────────┘ │         │ └──────────────────┘ │
└──────────────────────┘         └──────────────────────┘
                                           │
                                           │ MySQL :3306
                                           │
                                           ▼
                                  ┌──────────────────────┐
                                  │  COMPUTADORA C       │
                                  │  192.168.1.102       │
                                  │                      │
                                  │ ┌──────────────────┐ │
                                  │ │  MÓDULO 3        │ │
                                  │ │  Data Warehouse  │ │
                                  │ │                  │ │
                                  │ │ dw_proyectos     │ │
                                  │ │ _hist            │ │
                                  │ └──────────────────┘ │
                                  └──────────────────────┘
```

---

## 📝 Archivos a Modificar en TU COMPUTADORA (B)

### 1️⃣ Archivo: `03_Dashboard/.env`

```bash
# Conexión a Computadora A (BD Origen)
DB_ORIGEN_HOST=192.168.1.100  ← Cambiar esta IP
DB_ORIGEN_PORT=3306
DB_ORIGEN_USER=etl_user
DB_ORIGEN_PASSWORD=etl_password_123

# Conexión a Computadora C (Data Warehouse)
DB_DW_HOST=192.168.1.102      ← Cambiar esta IP
DB_DW_PORT=3306
DB_DW_USER=etl_user
DB_DW_PASSWORD=etl_password_123

# Tu IP para el frontend
API_BASE_URL=http://192.168.1.101:5001  ← Cambiar a tu IP
CORS_ORIGINS=http://192.168.1.101:8080  ← Cambiar a tu IP
```

### 2️⃣ Archivo: `03_Dashboard/frontend/app.js`

```javascript
// Línea 2:
const API_BASE = 'http://192.168.1.101:5001';  ← Cambiar a tu IP

// Línea 31:
const API_URL = 'http://192.168.1.101:5001/api';  ← Cambiar a tu IP
```

---

## 🔐 Comandos en las Otras Computadoras

### En Computadora A (Módulo 1):

```sql
-- 1. Crear usuario con acceso remoto
mysql -u root -p
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON gestionproyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

```bash
# 2. Configurar MySQL para aceptar conexiones remotas
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Cambiar: bind-address = 0.0.0.0

# 3. Reiniciar MySQL
sudo systemctl restart mysql

# 4. Abrir firewall
sudo ufw allow 3306/tcp
```

### En Computadora C (Módulo 3):

```sql
-- 1. Crear usuario con acceso remoto
mysql -u root -p
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON dw_proyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

```bash
# 2. Configurar MySQL para aceptar conexiones remotas
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Cambiar: bind-address = 0.0.0.0

# 3. Reiniciar MySQL
sudo systemctl restart mysql

# 4. Abrir firewall
sudo ufw allow 3306/tcp
```

---

## ✅ Flujo de Datos

```
Usuario (Navegador)
    │
    │ HTTP :8080
    ▼
┌─────────────────┐
│   Frontend      │  Tu Computadora (B)
│  (HTML/CSS/JS)  │  192.168.1.101:8080
└────────┬────────┘
         │ HTTP :5001
         ▼
┌─────────────────┐
│   Backend       │  Tu Computadora (B)
│   (Flask API)   │  192.168.1.101:5001
└────┬──────┬─────┘
     │      │
     │      │ MySQL :3306
     │      ▼
     │  ┌──────────────────┐
     │  │  Data Warehouse  │  Computadora C
     │  │  (Módulo 3)      │  192.168.1.102
     │  └──────────────────┘
     │
     │ MySQL :3306
     ▼
┌──────────────────┐
│   BD Origen      │  Computadora A
│   (Módulo 1)     │  192.168.1.100
└──────────────────┘
```

---

## 🧪 Prueba de Conexión

### Desde tu Computadora (B):

```bash
# Probar conexión a Computadora A
ping 192.168.1.100
telnet 192.168.1.100 3306
mysql -h 192.168.1.100 -u etl_user -p gestionproyectos_hist

# Probar conexión a Computadora C
ping 192.168.1.102
telnet 192.168.1.102 3306
mysql -h 192.168.1.102 -u etl_user -p dw_proyectos_hist
```

---

## 🎯 Resumen en 3 Pasos

### Paso 1: Modificar en tu Computadora (B)
```bash
cd 03_Dashboard
cp .env.example .env
# Editar .env con las IPs correctas
# Editar frontend/app.js con tu IP
```

### Paso 2: Configurar en Computadoras A y C
```sql
-- Crear usuarios remotos
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON *.* TO 'etl_user'@'%';
```

```bash
# Configurar MySQL y Firewall
# bind-address = 0.0.0.0
# sudo ufw allow 3306/tcp
```

### Paso 3: Iniciar y Probar
```bash
cd 03_Dashboard
./iniciar_dashboard.sh
# Acceder: http://192.168.1.101:8080
```

---

**Ver guía detallada:** [GUIA_CONEXION_REMOTA.md](GUIA_CONEXION_REMOTA.md)
