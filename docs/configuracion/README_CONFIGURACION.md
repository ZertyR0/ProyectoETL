# ETL Distribuido - Proyecto de 3 Máquinas

## Arquitectura del Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   MÁQUINA 1     │────▶│   MÁQUINA 2     │────▶│   MÁQUINA 3     │
│ GestionProyectos│     │      ETL        │     │  Datawarehouse  │
│                 │     │                 │     │                 │
│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │
│ │ MySQL       │ │     │ │ Python ETL  │ │     │ │ MySQL       │ │
│ │ BD Origen   │ │     │ │ Procesador  │ │     │ │ BD Destino  │ │
│ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      📊 Datos              ⚙️ Transformar           🏗️ Datawarehouse
```

## Configuración por Máquina

### 🖥️ MÁQUINA 1 - Servidor de Gestión de Proyectos

**Responsabilidades:**
- Hospedar la base de datos origen `gestionproyectos_hist`
- Generar y mantener datos operacionales
- Permitir conexiones remotas del ETL

**Archivos importantes:**
- `GestionProyectos/setup_servidor_bd.py` - Configuración automática
- `Datawarehouse/script_creacion_db.sql` - Estructura BD origen
- `Datawarehouse/generacion_datos.py` - Datos de prueba

**Pasos de configuración:**

1. **Instalar MySQL/XAMPP**
   ```bash
   # Asegurar que MySQL esté funcionando en puerto 3306
   ```

2. **Ejecutar configuración**
   ```bash
   cd GestionProyectos
   python3 setup_servidor_bd.py
   ```

3. **Configurar firewall**
   ```bash
   # Permitir conexiones MySQL desde otras máquinas
   # Puerto 3306 TCP
   ```

4. **Configurar MySQL para conexiones remotas**
   - Editar `my.cnf` o `my.ini`
   - Comentar `bind-address = 127.0.0.1`
   - Reiniciar MySQL

### 🖥️ MÁQUINA 2 - Procesador ETL

**Responsabilidades:**
- Ejecutar el proceso ETL
- Conectarse remotamente a ambas bases de datos
- Transformar y migrar datos

**Archivos importantes:**
- `ETL/etl_distribuido.py` - ETL principal para 3 máquinas
- `GestionProyectos/config_conexion.py` - Configuración de conexiones
- `ETL/etl_remoto_portable.py` - ETL portable alternativo

**Pasos de configuración:**

1. **Instalar Python y dependencias**
   ```bash
   # Python 3.6+
   pip install pandas sqlalchemy mysql-connector-python
   ```

2. **Configurar IPs de conexión**
   ```bash
   # Editar config_conexion.py con las IPs reales
   HOST_ORIGEN = "192.168.1.100"   # IP de Máquina 1
   HOST_DESTINO = "192.168.1.102"  # IP de Máquina 3
   ```

3. **Ejecutar ETL**
   ```bash
   cd ETL
   python3 etl_distribuido.py
   ```

### 🖥️ MÁQUINA 3 - Servidor Datawarehouse

**Responsabilidades:**
- Hospedar el datawarehouse `dw_proyectos_hist`
- Recibir datos transformados del ETL
- Mantener datos históricos para análisis

**Archivos importantes:**
- `Datawarehouse/setup_datawarehouse.py` - Configuración automática
- `Datawarehouse/script_datawarehouse.sql` - Estructura del DW

**Pasos de configuración:**

1. **Instalar MySQL/XAMPP**
   ```bash
   # Asegurar que MySQL esté funcionando en puerto 3306
   ```

2. **Ejecutar configuración**
   ```bash
   cd Datawarehouse
   python3 setup_datawarehouse.py
   ```

3. **Configurar firewall**
   ```bash
   # Permitir conexiones MySQL desde la máquina ETL
   # Puerto 3306 TCP
   ```

## Configuración de Red

### IPs de Ejemplo
```
Máquina 1 (GestionProyectos): 192.168.1.100
Máquina 2 (ETL):             192.168.1.101
Máquina 3 (Datawarehouse):   192.168.1.102
```

### Puertos Necesarios
- **3306/TCP** - MySQL (ambas máquinas con BD)
- **8081/TCP** - Servidor ETL HTTP (opcional)

### Usuarios de Base de Datos
- **Usuario:** `etl_user`
- **Password:** `etl_password_123`
- **Permisos:** Acceso remoto completo a las bases correspondientes

## Flujo de Ejecución

### 1. Preparación Inicial
```bash
# Máquina 1
cd GestionProyectos
python3 setup_servidor_bd.py

# Máquina 3
cd Datawarehouse
python3 setup_datawarehouse.py
```

### 2. Configuración de Red
```bash
# Editar config_conexion.py en Máquina 2 con IPs reales
```

### 3. Ejecución ETL
```bash
# Máquina 2
cd ETL
python3 etl_distribuido.py
```

## Verificación del Sistema

### Comprobar Conectividad
```bash
# Desde Máquina 2, probar conexión a Máquina 1
mysql -h 192.168.1.100 -u etl_user -p gestionproyectos_hist

# Desde Máquina 2, probar conexión a Máquina 3
mysql -h 192.168.1.102 -u etl_user -p dw_proyectos_hist
```

### Verificar Datos
```sql
-- En Máquina 1 (origen)
USE gestionproyectos_hist;
SELECT COUNT(*) FROM Proyecto WHERE fecha_fin_real IS NOT NULL;

-- En Máquina 3 (destino)
USE dw_proyectos_hist;
SELECT COUNT(*) FROM HechoProyecto;
```

## Solución de Problemas Comunes

### Error de Conexión Rechazada
- Verificar que MySQL esté funcionando
- Comprobar firewall/puertos abiertos
- Revisar configuración de bind-address en MySQL

### Error de Permisos
- Verificar usuario `etl_user` en ambas máquinas
- Comprobar permisos GRANT para acceso remoto
- Ejecutar `FLUSH PRIVILEGES` en MySQL

### Error de Datos Faltantes
- Ejecutar generación de datos en Máquina 1
- Verificar que haya proyectos cerrados
- Comprobar filtros de fecha en el ETL

## Monitoreo

### Logs del ETL
- El ETL muestra progreso detallado en consola
- Verificar conexiones a ambas bases
- Comprobar cantidad de registros procesados

### Estado de las Bases
```bash
# Script de verificación rápida
python3 -c "
import mysql.connector
# Verificar ambas conexiones...
"
```

## Seguridad

### Recomendaciones
- Cambiar passwords por defecto
- Usar VPN para conexiones entre máquinas
- Configurar firewall restrictivo
- Monitorear conexiones MySQL
- Backup regular de ambas bases de datos

---

**Autor:** Sistema ETL Distribuido  
**Versión:** 1.0  
**Fecha:** Octubre 2025
