# 🌐 Guía de Conexión Remota - Dashboard

## 🎯 Objetivo

Esta guía te explica **exactamente qué cambiar** en el Módulo 2 (Dashboard) para conectarlo a bases de datos en otras computadoras.

---

## 📋 Escenario

Tienes 3 computadoras:
- **Computadora A (192.168.1.100)**: Módulo 1 - Base de Datos Origen
- **Computadora B (192.168.1.101)**: Módulo 2 - Dashboard (TU COMPUTADORA)
- **Computadora C (192.168.1.102)**: Módulo 3 - Data Warehouse

---

## ⚙️ Configuración Paso a Paso

### 📍 Paso 1: Obtener las IPs de las Otras Computadoras

#### En Computadora A (Módulo 1):
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4
```

**Anota la IP**, por ejemplo: `192.168.1.100`

#### En Computadora C (Módulo 3):
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr IPv4
```

**Anota la IP**, por ejemplo: `192.168.1.102`

---

### 📝 Paso 2: Crear/Editar el Archivo `.env`

En tu computadora (Módulo 2 - Dashboard):

```bash
cd 03_Dashboard
cp .env.example .env
nano .env  # O usa tu editor favorito
```

**Edita estos valores:**

```bash
# ============================================
# CONFIGURACIÓN PARA CONEXIÓN REMOTA
# ============================================

# Backend API - DEJAR ASÍ para aceptar conexiones
FLASK_HOST=0.0.0.0          # ✅ NO cambiar (acepta conexiones de cualquier IP)
FLASK_PORT=5001             # ✅ Puerto del backend
FLASK_DEBUG=False           # ⚠️  Cambiar a False en producción
FLASK_ENV=production        # ⚠️  Cambiar a production

# ============================================
# CONEXIÓN A MÓDULO 1 (Base de Datos Origen)
# ============================================
DB_ORIGEN_HOST=192.168.1.100    # 🔴 CAMBIAR: IP de Computadora A
DB_ORIGEN_PORT=3306             # ✅ Puerto MySQL (default 3306)
DB_ORIGEN_NAME=gestionproyectos_hist
DB_ORIGEN_USER=etl_user         # 🔴 CAMBIAR: Usuario creado en Módulo 1
DB_ORIGEN_PASSWORD=etl_password_123  # 🔴 CAMBIAR: Password del usuario

# ============================================
# CONEXIÓN A MÓDULO 3 (Data Warehouse)
# ============================================
DB_DW_HOST=192.168.1.102        # 🔴 CAMBIAR: IP de Computadora C
DB_DW_PORT=3306                 # ✅ Puerto MySQL (default 3306)
DB_DW_NAME=dw_proyectos_hist
DB_DW_USER=etl_user             # 🔴 CAMBIAR: Usuario creado en Módulo 3
DB_DW_PASSWORD=etl_password_123 # 🔴 CAMBIAR: Password del usuario

# ============================================
# FRONTEND
# ============================================
FRONTEND_PORT=8080
API_BASE_URL=http://192.168.1.101:5001  # 🔴 CAMBIAR: Tu IP (Computadora B)

# ============================================
# CORS (permitir acceso desde otras IPs)
# ============================================
CORS_ORIGINS=http://192.168.1.101:8080,http://localhost:8080  # 🔴 CAMBIAR: Tu IP

LOG_LEVEL=INFO
```

---

### 🌐 Paso 3: Editar el Frontend (app.js)

Edita `03_Dashboard/frontend/app.js`:

```javascript
// LÍNEA 2: Cambiar localhost por tu IP
const API_BASE = 'http://192.168.1.101:5001';  // 🔴 CAMBIAR por tu IP

// LÍNEA 31: También cambiar aquí
const API_URL = 'http://192.168.1.101:5001/api';  // 🔴 CAMBIAR por tu IP
```

**Comando rápido para cambiar:**
```bash
cd 03_Dashboard/frontend
sed -i.bak "s|http://localhost:5001|http://192.168.1.101:5001|g" app.js
```

---

### 🔐 Paso 4: Configurar Usuarios en las Otras Computadoras

#### En Computadora A (Módulo 1):

Conectarse a MySQL y ejecutar:

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear usuario con acceso remoto
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';

-- Dar permisos de lectura
GRANT SELECT ON gestionproyectos_hist.* TO 'etl_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar usuario
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';
```

#### En Computadora C (Módulo 3):

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear usuario con acceso remoto
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';

-- Dar permisos de lectura
GRANT SELECT ON dw_proyectos_hist.* TO 'etl_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar usuario
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';
```

---

### 🔥 Paso 5: Configurar Firewall en las Otras Computadoras

#### En Computadora A (Módulo 1):

**Ubuntu/Debian:**
```bash
sudo ufw allow 3306/tcp
sudo ufw status
```

**CentOS/RHEL:**
```bash
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload
```

**Windows:**
```powershell
# En PowerShell como Administrador
New-NetFirewallRule -DisplayName "MySQL" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Allow
```

**macOS:**
```bash
# Abrir Preferencias del Sistema > Seguridad > Firewall > Opciones
# Permitir conexiones entrantes para MySQL
```

#### En Computadora C (Módulo 3):

**Mismo procedimiento que en Computadora A.**

---

### 🗄️ Paso 6: Configurar MySQL para Aceptar Conexiones Remotas

#### En Computadoras A y C:

**Editar configuración de MySQL:**

```bash
# Ubuntu/Debian
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# CentOS/RHEL
sudo nano /etc/my.cnf

# macOS (con Homebrew)
nano /usr/local/etc/my.cnf

# Windows (XAMPP)
# C:\xampp\mysql\bin\my.ini
```

**Buscar y cambiar:**

```ini
# ANTES:
bind-address = 127.0.0.1

# DESPUÉS:
bind-address = 0.0.0.0
```

**Reiniciar MySQL:**

```bash
# Ubuntu/Debian
sudo systemctl restart mysql

# CentOS/RHEL
sudo systemctl restart mysqld

# macOS
brew services restart mysql

# Windows (XAMPP)
# Detener y reiniciar desde el panel de XAMPP
```

---

### 🧪 Paso 7: Probar Conexiones

#### Desde tu Computadora (B), probar conexión a A:

```bash
# Probar puerto abierto
telnet 192.168.1.100 3306

# O con MySQL client
mysql -h 192.168.1.100 -u etl_user -p -D gestionproyectos_hist
```

#### Desde tu Computadora (B), probar conexión a C:

```bash
# Probar puerto abierto
telnet 192.168.1.102 3306

# O con MySQL client
mysql -h 192.168.1.102 -u etl_user -p -D dw_proyectos_hist
```

**Si funciona, verás algo como:**
```
Welcome to the MySQL monitor...
```

---

### 🚀 Paso 8: Iniciar el Dashboard

```bash
cd 03_Dashboard

# Opción 1: Con script automático
./iniciar_dashboard.sh

# Opción 2: Manual
source venv/bin/activate
cd backend && python app.py &
cd ../frontend && python -m http.server 8080 &
```

---

### 🌐 Paso 9: Acceder al Dashboard

#### Desde tu misma computadora:
```
http://localhost:8080/index.html
```

#### Desde otra computadora en la red:
```
http://192.168.1.101:8080/index.html
```

---

## 📊 Resumen de IPs

| Componente | Computadora | IP | Puerto | Cambiar en |
|------------|-------------|-------|--------|------------|
| **Módulo 1** | A | 192.168.1.100 | 3306 | `.env` → `DB_ORIGEN_HOST` |
| **Módulo 2 (Backend)** | B (Tuya) | 192.168.1.101 | 5001 | `app.js` → `API_BASE` |
| **Módulo 2 (Frontend)** | B (Tuya) | 192.168.1.101 | 8080 | `.env` → `API_BASE_URL` |
| **Módulo 3** | C | 192.168.1.102 | 3306 | `.env` → `DB_DW_HOST` |

---

## 🔧 Archivos que DEBES Modificar

### ✅ Obligatorios:

1. **`03_Dashboard/.env`** (crear desde `.env.example`)
   - Línea 11: `DB_ORIGEN_HOST=192.168.1.100`
   - Línea 16: `DB_DW_HOST=192.168.1.102`
   - Línea 24: `API_BASE_URL=http://192.168.1.101:5001`
   - Línea 27: `CORS_ORIGINS=http://192.168.1.101:8080`

2. **`03_Dashboard/frontend/app.js`**
   - Línea 2: `const API_BASE = 'http://192.168.1.101:5001';`
   - Línea 31: `const API_URL = 'http://192.168.1.101:5001/api';`

### ⚠️ Opcionales (para producción):

3. **`03_Dashboard/backend/app.py`** (si necesitas más control de CORS)
   ```python
   # Buscar la línea de CORS y agregar tus IPs:
   CORS(app, origins=["http://192.168.1.101:8080", "http://192.168.1.101"])
   ```

---

## 🐛 Solución de Problemas

### ❌ Error: "Connection refused"

**Causa:** Firewall bloqueando o MySQL no acepta conexiones remotas.

**Solución:**
1. Verificar firewall en Computadoras A y C
2. Verificar `bind-address = 0.0.0.0` en MySQL
3. Reiniciar MySQL

### ❌ Error: "Access denied for user"

**Causa:** Usuario no tiene permisos remotos o password incorrecto.

**Solución:**
```sql
-- En Computadora A o C:
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';

-- Debe mostrar Host = '%' (no 'localhost')
-- Si no, crear usuario correctamente:
DROP USER 'etl_user'@'localhost';
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON *.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

### ❌ Error: "CORS policy"

**Causa:** Frontend no puede acceder al backend por CORS.

**Solución:**
Editar `03_Dashboard/.env`:
```bash
CORS_ORIGINS=http://192.168.1.101:8080,http://localhost:8080,*
```

### ❌ Dashboard no carga datos

**Causa:** Backend no puede conectarse a las bases de datos.

**Solución:**
1. Verificar logs: `tail -f 03_Dashboard/logs/backend.log`
2. Probar conexión manual con MySQL client
3. Verificar IPs y passwords en `.env`

---

## 📝 Checklist Final

Antes de iniciar, verifica:

- [ ] Obtuve las IPs de Computadoras A y C
- [ ] Creé el archivo `.env` en `03_Dashboard/`
- [ ] Cambié `DB_ORIGEN_HOST` a la IP de Computadora A
- [ ] Cambié `DB_DW_HOST` a la IP de Computadora C
- [ ] Cambié `API_BASE_URL` a mi IP (Computadora B)
- [ ] Edité `app.js` con mi IP
- [ ] Creé usuarios `etl_user` con `%` en Computadoras A y C
- [ ] Configuré `bind-address = 0.0.0.0` en MySQL (A y C)
- [ ] Abrí puertos 3306 en firewall (A y C)
- [ ] Reinicié MySQL en Computadoras A y C
- [ ] Probé conexiones con `telnet` o `mysql` client
- [ ] Inicié el dashboard con `./iniciar_dashboard.sh`

---

## 🎯 Comando Rápido (Resumen)

```bash
# 1. Crear configuración
cd 03_Dashboard
cp .env.example .env

# 2. Editar .env (usar tu editor)
nano .env
# Cambiar:
# - DB_ORIGEN_HOST=192.168.1.100
# - DB_DW_HOST=192.168.1.102
# - API_BASE_URL=http://192.168.1.101:5001

# 3. Editar app.js
cd frontend
sed -i.bak 's|localhost|192.168.1.101|g' app.js

# 4. Iniciar dashboard
cd ..
./iniciar_dashboard.sh

# 5. Acceder
# http://192.168.1.101:8080/index.html
```

---

## 📞 Preguntas Frecuentes

### ¿Qué pasa si solo tengo 2 computadoras?

Si solo tienes el Dashboard y un módulo de BD:
- Cambiar solo una IP (`DB_ORIGEN_HOST` o `DB_DW_HOST`)
- La otra puede quedar como `localhost` si no la usas

### ¿Puedo usar nombres de host en lugar de IPs?

Sí, si tienes DNS o editas `/etc/hosts`:
```bash
# En /etc/hosts
192.168.1.100  servidor-bd-origen
192.168.1.102  servidor-dw

# En .env
DB_ORIGEN_HOST=servidor-bd-origen
DB_DW_HOST=servidor-dw
```

### ¿Funciona en WiFi?

Sí, siempre que las computadoras estén en la misma red (mismo router).

### ¿Y en Internet?

Necesitas:
- IPs públicas o túnel VPN
- Configuración de router (port forwarding)
- Certificados SSL para seguridad

---

**¿Listo para conectar?** 🚀  
**Sigue los pasos y tendrás tu dashboard conectado a las otras computadoras!**

[Volver a Instalación](INSTALACION.md) | [Ver Guía Completa](../GUIA_MODULOS_INDEPENDIENTES.md)
