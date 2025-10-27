# 🔧 Instrucciones para Configurar Servidores MySQL

## ⚠️ Estado Actual

❌ **Los servidores MySQL NO están aceptando conexiones remotas**

El script de verificación detectó que:
- ❌ Módulo 1 (172.20.10.3): No responde
- ❌ Módulo 3 (172.20.10.2): No responde

---

## 📋 Instrucciones para el Servidor del Módulo 1 (172.20.10.3)

### Conectarse al servidor:
```bash
ssh usuario@172.20.10.3
```

### 1️⃣ Verificar que MySQL esté corriendo:
```bash
sudo systemctl status mysql
# O en macOS:
brew services list | grep mysql
```

Si no está corriendo:
```bash
sudo systemctl start mysql
# O en macOS:
brew services start mysql
```

### 2️⃣ Configurar MySQL para aceptar conexiones remotas:

**Linux (Ubuntu/Debian):**
```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

**Linux (CentOS/RHEL):**
```bash
sudo nano /etc/my.cnf
```

**macOS:**
```bash
nano /usr/local/etc/my.cnf
```

**Buscar y cambiar:**
```ini
# ANTES:
bind-address = 127.0.0.1

# DESPUÉS:
bind-address = 0.0.0.0
```

### 3️⃣ Crear usuario con permisos remotos:
```bash
mysql -u root -p
```

Dentro de MySQL:
```sql
-- Crear usuario (si no existe)
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';

-- Dar permisos
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* TO 'etl_user'@'%';

-- Si la base de datos no existe, crearla:
CREATE DATABASE IF NOT EXISTS gestionproyectos_hist;

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar usuario
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';

-- Salir
EXIT;
```

### 4️⃣ Reiniciar MySQL:
```bash
sudo systemctl restart mysql
# O en macOS:
brew services restart mysql
```

### 5️⃣ Abrir firewall:

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

**macOS:**
```bash
# Abrir Preferencias del Sistema > Seguridad > Firewall
# Agregar excepción para MySQL
```

---

## 📋 Instrucciones para el Servidor del Módulo 3 (172.20.10.2)

### Conectarse al servidor:
```bash
ssh usuario@172.20.10.2
```

### Repetir los mismos pasos del Módulo 1, pero con la base de datos del Data Warehouse:

```sql
-- En MySQL
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT ALL PRIVILEGES ON dw_proyectos_hist.* TO 'etl_user'@'%';
CREATE DATABASE IF NOT EXISTS dw_proyectos_hist;
FLUSH PRIVILEGES;
```

---

## ✅ Verificar que Funcione

Después de configurar ambos servidores, desde tu Dashboard ejecuta:

```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard
python3 verificar_conexiones.py
```

Deberías ver:
```
✅ OK - Módulo 1 - Base de Datos Gestión
✅ OK - Módulo 3 - Data Warehouse
🎉 ¡Todas las conexiones funcionan correctamente!
```

---

## 🔍 Comandos de Diagnóstico

### En cada servidor, ejecutar:

```bash
# Ver si MySQL está escuchando en todas las interfaces
sudo netstat -tlnp | grep 3306

# Debería mostrar:
# 0.0.0.0:3306 (no 127.0.0.1:3306)

# Ver logs de MySQL
sudo tail -f /var/log/mysql/error.log
```

### Desde tu Dashboard:

```bash
# Probar conectividad de red
ping 172.20.10.3
ping 172.20.10.2

# Probar puerto MySQL
nc -zv 172.20.10.3 3306
nc -zv 172.20.10.2 3306

# Probar conexión MySQL directa
mysql -h 172.20.10.3 -u etl_user -p gestionproyectos_hist
mysql -h 172.20.10.2 -u etl_user -p dw_proyectos_hist
```

---

## 📝 Resumen de Configuración

| Componente | IP | Puerto | Usuario | Password | Base de Datos |
|------------|-----|--------|---------|----------|---------------|
| **Módulo 1** | 172.20.10.3 | 3306 | etl_user | etl_password_123 | gestionproyectos_hist |
| **Módulo 3** | 172.20.10.2 | 3306 | etl_user | etl_password_123 | dw_proyectos_hist |
| **Dashboard** | 172.31.5.36 | 5001/8080 | - | - | - |

---

## ⚡ Una Vez Configurado

Cuando ambos servidores estén listos:

```bash
# Iniciar el Dashboard
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard
./iniciar_dashboard.sh

# Acceder en navegador:
http://172.31.5.36:8080
```

---

## 🆘 Problemas Comunes

### "Can't connect to MySQL server"
- MySQL no está corriendo
- Firewall bloqueando puerto 3306
- bind-address no configurado en 0.0.0.0

### "Access denied for user"
- Usuario no creado con '@%'
- Password incorrecto
- Permisos no otorgados correctamente

### "Unknown database"
- Base de datos no existe
- Crear con: `CREATE DATABASE nombre_bd;`

---

**Una vez configurados los servidores, ejecuta:**
```bash
python3 verificar_conexiones.py
```

**Para ver si todo está listo!** ✅
