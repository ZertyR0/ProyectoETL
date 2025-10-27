# 🌐 Configuración Específica - Tu Red

## 📊 Resumen de Tu Configuración

```
┌─────────────────────────────────────────────────────────────────┐
│                    TU RED CONFIGURADA                           │
└─────────────────────────────────────────────────────────────────┘

Servidor 1 (Módulo 1)         Tu Computadora               Servidor 3 (Módulo 3)
172.26.163.247                172.31.5.36                  172.26.167.211

┌──────────────────┐          ┌──────────────────┐         ┌──────────────────┐
│  BASE DE DATOS   │◄─────────┤    DASHBOARD     │─────────►│ DATA WAREHOUSE   │
│     ORIGEN       │  MySQL   │                  │  MySQL  │                  │
│                  │  :3306   │  Backend :5001   │  :3306  │                  │
│gestionproyectos_ │          │  Frontend :8080  │         │ dw_proyectos_    │
│      hist        │          │                  │         │      hist        │
└──────────────────┘          └──────────────────┘         └──────────────────┘
```

---

## ✅ Archivos YA CONFIGURADOS

### ✅ 1. Archivo `.env` - CREADO
**Ubicación:** `03_Dashboard/.env`

```bash
# Conexiones configuradas:
DB_ORIGEN_HOST=172.26.163.247      ✅ Módulo 1
DB_DW_HOST=172.26.167.211          ✅ Módulo 3
API_BASE_URL=http://172.31.5.36:5001  ✅ Tu Dashboard
```

### ✅ 2. Archivo `app.js` - ACTUALIZADO
**Ubicación:** `03_Dashboard/frontend/app.js`

```javascript
const API_BASE = 'http://172.31.5.36:5001';  ✅
const API_URL = 'http://172.31.5.36:5001/api';  ✅
```

---

## 🔐 LO QUE NECESITAS HACER EN LOS SERVIDORES

### 📍 Servidor 1 (172.26.163.247) - Módulo 1

**1. Crear usuario con acceso remoto:**

```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar estos comandos:
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON gestionproyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

**2. Configurar MySQL para aceptar conexiones remotas:**

```bash
# Editar configuración
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Buscar y cambiar:
bind-address = 127.0.0.1
# POR:
bind-address = 0.0.0.0

# Guardar (Ctrl+O, Enter, Ctrl+X)

# Reiniciar MySQL
sudo systemctl restart mysql
```

**3. Abrir puerto en firewall:**

```bash
# Ubuntu/Debian
sudo ufw allow from 172.31.5.36 to any port 3306
sudo ufw status

# O permitir a todos (menos seguro):
sudo ufw allow 3306/tcp
```

**4. Verificar que el servicio esté escuchando:**

```bash
sudo netstat -tulpn | grep 3306
# Debe mostrar: 0.0.0.0:3306
```

---

### 📍 Servidor 3 (172.26.167.211) - Módulo 3

**1. Crear usuario con acceso remoto:**

```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar estos comandos:
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON dw_proyectos_hist.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

**2. Configurar MySQL para aceptar conexiones remotas:**

```bash
# Editar configuración
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Buscar y cambiar:
bind-address = 127.0.0.1
# POR:
bind-address = 0.0.0.0

# Guardar (Ctrl+O, Enter, Ctrl+X)

# Reiniciar MySQL
sudo systemctl restart mysql
```

**3. Abrir puerto en firewall:**

```bash
# Ubuntu/Debian
sudo ufw allow from 172.31.5.36 to any port 3306
sudo ufw status

# O permitir a todos (menos seguro):
sudo ufw allow 3306/tcp
```

**4. Verificar que el servicio esté escuchando:**

```bash
sudo netstat -tulpn | grep 3306
# Debe mostrar: 0.0.0.0:3306
```

---

## 🧪 PROBAR CONEXIONES DESDE TU COMPUTADORA

### Probar Servidor 1 (Módulo 1):

```bash
# Prueba 1: Ping
ping -c 3 172.26.163.247

# Prueba 2: Puerto MySQL
telnet 172.26.163.247 3306
# O con nc:
nc -zv 172.26.163.247 3306

# Prueba 3: Conexión MySQL
mysql -h 172.26.163.247 -u etl_user -p gestionproyectos_hist
# Password: etl_password_123
```

### Probar Servidor 3 (Módulo 3):

```bash
# Prueba 1: Ping
ping -c 3 172.26.167.211

# Prueba 2: Puerto MySQL
telnet 172.26.167.211 3306
# O con nc:
nc -zv 172.26.167.211 3306

# Prueba 3: Conexión MySQL
mysql -h 172.26.167.211 -u etl_user -p dw_proyectos_hist
# Password: etl_password_123
```

**✅ Si ambas pruebas funcionan, estás listo!**

---

## 🚀 INICIAR EL DASHBOARD

```bash
cd 03_Dashboard

# Verificar que .env existe
ls -la .env

# Iniciar dashboard
./iniciar_dashboard.sh
```

**El script va a:**
1. ✅ Verificar puertos disponibles
2. ✅ Iniciar backend Flask en :5001
3. ✅ Iniciar frontend en :8080
4. ✅ Abrir navegador automáticamente

---

## 🌐 ACCEDER AL DASHBOARD

### Desde tu computadora:
```
http://localhost:8080/index.html
http://172.31.5.36:8080/index.html
```

### Desde otra computadora en tu red:
```
http://172.31.5.36:8080/index.html
```

---

## 📋 CHECKLIST ANTES DE INICIAR

### En Servidor 1 (172.26.163.247):
- [ ] Usuario `etl_user@'%'` creado
- [ ] Permisos SELECT otorgados
- [ ] `bind-address = 0.0.0.0` configurado
- [ ] MySQL reiniciado
- [ ] Puerto 3306 abierto en firewall
- [ ] Probada conexión desde tu PC

### En Servidor 3 (172.26.167.211):
- [ ] Usuario `etl_user@'%'` creado
- [ ] Permisos SELECT otorgados
- [ ] `bind-address = 0.0.0.0` configurado
- [ ] MySQL reiniciado
- [ ] Puerto 3306 abierto en firewall
- [ ] Probada conexión desde tu PC

### En Tu Computadora (172.31.5.36):
- [x] Archivo `.env` creado ✅
- [x] Archivo `app.js` actualizado ✅
- [ ] Conexiones probadas con `mysql` o `telnet`
- [ ] Dashboard iniciado con `./iniciar_dashboard.sh`

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Connection refused" al probar MySQL

**Causa:** Firewall bloqueando o MySQL no escuchando en todas las interfaces.

**Solución:**
```bash
# En el servidor con problemas:

# 1. Verificar que MySQL escucha en 0.0.0.0
sudo netstat -tulpn | grep 3306
# Debe mostrar: 0.0.0.0:3306 (NO 127.0.0.1:3306)

# 2. Si muestra 127.0.0.1, editar config:
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Cambiar bind-address = 0.0.0.0
sudo systemctl restart mysql

# 3. Verificar firewall
sudo ufw status
sudo ufw allow 3306/tcp
```

### ❌ Error: "Access denied for user"

**Causa:** Usuario no existe con permisos remotos o password incorrecto.

**Solución:**
```sql
-- En el servidor:
mysql -u root -p

-- Verificar usuarios
SELECT User, Host FROM mysql.user WHERE User = 'etl_user';

-- Debe mostrar Host = '%', si no:
DROP USER IF EXISTS 'etl_user'@'localhost';
CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123';
GRANT SELECT ON *.* TO 'etl_user'@'%';
FLUSH PRIVILEGES;
```

### ❌ Dashboard se inicia pero no carga datos

**Causa:** Backend no puede conectarse a los servidores.

**Solución:**
```bash
# Ver logs del backend
tail -f 03_Dashboard/logs/backend.log

# Buscar errores de conexión
# Si hay errores, verificar .env y conexiones MySQL
```

### ❌ "CORS policy" error en navegador

**Causa:** CORS mal configurado.

**Solución:**
```bash
# Verificar .env
cat 03_Dashboard/.env | grep CORS

# Debe incluir tu IP:
# CORS_ORIGINS=http://172.31.5.36:8080,...

# Si no, editar y reiniciar:
nano 03_Dashboard/.env
./03_Dashboard/detener_dashboard.sh
./03_Dashboard/iniciar_dashboard.sh
```

---

## 📞 SCRIPT DE DIAGNÓSTICO RÁPIDO

Guarda esto como `test_conexiones.sh` y ejecútalo:

```bash
#!/bin/bash

echo "🔍 Probando conexiones..."
echo ""

echo "📍 Servidor 1 (BD Origen):"
nc -zv 172.26.163.247 3306 2>&1
echo ""

echo "📍 Servidor 3 (Data Warehouse):"
nc -zv 172.26.167.211 3306 2>&1
echo ""

echo "📍 Intentando conexión MySQL a Servidor 1:"
mysql -h 172.26.163.247 -u etl_user -petl_password_123 -e "SHOW DATABASES;" 2>&1 | head -5
echo ""

echo "📍 Intentando conexión MySQL a Servidor 3:"
mysql -h 172.26.167.211 -u etl_user -petl_password_123 -e "SHOW DATABASES;" 2>&1 | head -5
echo ""

echo "✅ Si ambas conexiones funcionan, estás listo para iniciar el dashboard!"
```

```bash
chmod +x test_conexiones.sh
./test_conexiones.sh
```

---

## 🎯 RESUMEN DE COMANDOS CLAVE

### Para ejecutar en CADA servidor (1 y 3):

```bash
# 1. Crear usuario
mysql -u root -p -e "CREATE USER 'etl_user'@'%' IDENTIFIED BY 'etl_password_123'; GRANT SELECT ON *.* TO 'etl_user'@'%'; FLUSH PRIVILEGES;"

# 2. Configurar MySQL
sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql

# 3. Abrir firewall
sudo ufw allow 3306/tcp
```

### Para ejecutar en TU computadora:

```bash
# 1. Probar conexiones
mysql -h 172.26.163.247 -u etl_user -p gestionproyectos_hist
mysql -h 172.26.167.211 -u etl_user -p dw_proyectos_hist

# 2. Iniciar dashboard
cd 03_Dashboard
./iniciar_dashboard.sh

# 3. Acceder
# http://172.31.5.36:8080/index.html
```

---

## ✨ TODO ESTÁ CONFIGURADO

**Archivos modificados:**
- ✅ `03_Dashboard/.env` - Creado con tus IPs
- ✅ `03_Dashboard/frontend/app.js` - Actualizado con tu IP

**Solo necesitas:**
1. Configurar usuarios en Servidores 1 y 3
2. Abrir puertos en firewalls
3. Iniciar el dashboard

---

**¿Listo?** Ejecuta los comandos en los servidores y luego inicia el dashboard! 🚀

[Volver a INSTALACION.md](INSTALACION.md)
