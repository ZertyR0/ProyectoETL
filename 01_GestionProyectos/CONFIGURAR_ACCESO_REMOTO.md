# 🔐 Configurar Acceso Remoto a MySQL/MariaDB

**Fecha:** 27 de octubre de 2025  
**Problema detectado:** Host 'MAC-4D2E8F' no tiene permisos para conectarse

---

## ❌ Error Actual

```
ERROR 1130 (HY000): Host 'MAC-4D2E8F' is not allowed to connect to this MariaDB server
```

**Causa:** El usuario `etl_user` no tiene permisos para conectarse desde hosts remotos.

---

## ✅ Solución

### En la MÁQUINA REMOTA (172.20.10.3)

Ejecuta los siguientes comandos SQL en el servidor MySQL/MariaDB:

```sql
-- 1. Conectarse como root
mysql -u root -p

-- 2. Otorgar permisos al usuario etl_user desde la IP específica
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'172.20.10.12' 
IDENTIFIED BY 'etl_password_123';

-- O si quieres permitir desde cualquier host de la red 172.20.10.x
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'172.20.10.%' 
IDENTIFIED BY 'etl_password_123';

-- O para permitir desde cualquier host (menos seguro)
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'%' 
IDENTIFIED BY 'etl_password_123';

-- 3. Aplicar los cambios
FLUSH PRIVILEGES;

-- 4. Verificar los permisos
SELECT user, host FROM mysql.user WHERE user='etl_user';

-- 5. Mostrar privilegios del usuario
SHOW GRANTS FOR 'etl_user'@'172.20.10.12';
-- o
SHOW GRANTS FOR 'etl_user'@'%';

-- 6. Salir
EXIT;
```

### Script Completo (Copiar y Pegar)

```bash
# Opción 1: Acceso desde IP específica (más seguro)
sudo mysql -u root -p << 'EOF'
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'172.20.10.12' 
IDENTIFIED BY 'etl_password_123';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user='etl_user';
EOF

# Opción 2: Acceso desde toda la red 172.20.10.x
sudo mysql -u root -p << 'EOF'
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'172.20.10.%' 
IDENTIFIED BY 'etl_password_123';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user='etl_user';
EOF

# Opción 3: Acceso desde cualquier host (solo para desarrollo)
sudo mysql -u root -p << 'EOF'
GRANT ALL PRIVILEGES ON gestionproyectos_hist.* 
TO 'etl_user'@'%' 
IDENTIFIED BY 'etl_password_123';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user='etl_user';
EOF
```

---

## 🔧 Configuración del Servidor MySQL/MariaDB

### 1. Verificar que MySQL escucha en todas las interfaces

Edita el archivo de configuración:

```bash
# Para MySQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Para MariaDB
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Busca la línea:
```ini
bind-address = 127.0.0.1
```

Cámbiala a:
```ini
bind-address = 0.0.0.0
```

O comenta la línea:
```ini
# bind-address = 127.0.0.1
```

### 2. Reiniciar el servicio

```bash
# Para MySQL
sudo systemctl restart mysql

# Para MariaDB
sudo systemctl restart mariadb

# Verificar estado
sudo systemctl status mysql
# o
sudo systemctl status mariadb
```

### 3. Verificar que el puerto esté abierto

```bash
# Ver puertos en escucha
sudo netstat -tulpn | grep 3306

# Debe mostrar algo como:
# tcp        0      0 0.0.0.0:3306            0.0.0.0:*               LISTEN      12345/mysqld
```

### 4. Configurar Firewall (si está activo)

```bash
# Para UFW (Ubuntu/Debian)
sudo ufw allow from 172.20.10.12 to any port 3306
# o para toda la red
sudo ufw allow from 172.20.10.0/24 to any port 3306

# Para firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="172.20.10.12" port protocol="tcp" port="3306" accept'
sudo firewall-cmd --reload

# Para iptables
sudo iptables -A INPUT -p tcp -s 172.20.10.12 --dport 3306 -j ACCEPT
```

---

## 🧪 Probar la Conexión

### Desde la máquina CLIENTE (172.20.10.12)

```bash
# Probar con mysql client
mysql -h 172.20.10.3 -P 3306 -u etl_user -p
# Password: etl_password_123

# Probar con telnet
telnet 172.20.10.3 3306

# Probar con nc (netcat)
nc -zv 172.20.10.3 3306

# Probar con Python
python3 << 'EOF'
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='172.20.10.3',
        port=3306,
        user='etl_user',
        password='etl_password_123',
        database='gestionproyectos_hist'
    )
    print("✅ Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

---

## 📊 Datos de Conexión

| Parámetro | Valor |
|-----------|-------|
| **Host** | 172.20.10.3 |
| **Puerto** | 3306 |
| **Base de datos** | gestionproyectos_hist |
| **Usuario** | etl_user |
| **Contraseña** | etl_password_123 |
| **Cliente (tu máquina)** | 172.20.10.12 (MAC-4D2E8F) |

---

## 🔍 Diagnóstico de Problemas

### Problema: "Host is not allowed to connect"
**Causa:** Permisos de usuario incorrectos  
**Solución:** Ejecutar los GRANT statements arriba

### Problema: "Can't connect to MySQL server"
**Causa:** Servidor no accesible o firewall bloqueando  
**Solución:** 
1. Verificar que MySQL esté corriendo: `sudo systemctl status mysql`
2. Verificar bind-address: debe ser `0.0.0.0`
3. Verificar firewall: `sudo ufw status` o `sudo firewall-cmd --list-all`

### Problema: "Connection timed out"
**Causa:** Red no alcanzable o firewall  
**Solución:**
1. Ping a la IP: `ping 172.20.10.3`
2. Verificar conectividad: `telnet 172.20.10.3 3306`
3. Verificar que ambas máquinas estén en la misma red

---

## ✅ Checklist de Verificación

En el SERVIDOR (172.20.10.3):
- [ ] MySQL/MariaDB está corriendo
- [ ] bind-address = 0.0.0.0 (o comentado)
- [ ] Puerto 3306 está abierto en el firewall
- [ ] Usuario 'etl_user' tiene permisos remotos
- [ ] GRANT ejecutado correctamente
- [ ] FLUSH PRIVILEGES ejecutado

En el CLIENTE (172.20.10.12):
- [ ] Puede hacer ping a 172.20.10.3
- [ ] Puede conectarse al puerto 3306
- [ ] Tiene las credenciales correctas

---

## 📞 Siguiente Paso

**Una vez configurado el acceso remoto en el servidor, ejecuta:**

```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL
python3 -c "
import mysql.connector
conn = mysql.connector.connect(
    host='172.20.10.3',
    port=3306,
    user='etl_user',
    password='etl_password_123',
    database='gestionproyectos_hist'
)
print('✅ CONEXIÓN EXITOSA!')
cursor = conn.cursor()
cursor.execute('SHOW TABLES')
print('📊 Tablas:', [t[0] for t in cursor.fetchall()])
conn.close()
"
```

---

**¿Necesitas ayuda para ejecutar estos comandos en el servidor remoto?** 
Comparte pantalla o acceso SSH y te ayudo a configurarlo.
