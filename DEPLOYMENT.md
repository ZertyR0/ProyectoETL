# 🚀 Guía de Deployment - ETL Dashboard

Este documento te guía para desplegar el dashboard en la nube.

## 📋 Prerrequisitos

- Cuenta en GitHub (donde está tu código)
- Cuenta en el servicio cloud de tu elección

---

## ⭐ Opción 1: Railway.app (RECOMENDADO)

### Ventajas:
- ✅ $5 USD gratis al mes
- ✅ MySQL incluido gratis
- ✅ Deploy automático desde GitHub
- ✅ HTTPS automático
- ✅ Logs en tiempo real

### Pasos:

#### 1. Preparar el repositorio GitHub
```bash
cd /Users/andrescruzortiz/Documents/GitHub/ProyectoETL

# Agregar archivos al repositorio
git add .
git commit -m "Preparar para deployment en Railway"
git push origin main
```

#### 2. Crear cuenta en Railway
1. Ve a [railway.app](https://railway.app)
2. Haz clic en "Start a New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona el repositorio `ProyectoETL`

#### 3. Agregar base de datos MySQL
1. En tu proyecto Railway, haz clic en "+ New"
2. Selecciona "Database" → "MySQL"
3. Railway creará automáticamente:
   - `MYSQL_URL`
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`

#### 4. Configurar variables de entorno
En Railway, ve a tu servicio → Settings → Variables:

```env
# Flask
FLASK_ENV=production
SECRET_KEY=genera_algo_aleatorio_aqui
PORT=5001

# Base de datos (usa las credenciales de MySQL de Railway)
DB_HOST_ORIGEN=${{MySQL.MYSQL_HOST}}
DB_PORT_ORIGEN=${{MySQL.MYSQL_PORT}}
DB_USER_ORIGEN=${{MySQL.MYSQL_USER}}
DB_PASSWORD_ORIGEN=${{MySQL.MYSQL_PASSWORD}}
DB_NAME_ORIGEN=gestionproyectos_hist

# Datawarehouse (misma BD para simplificar)
DB_HOST_DESTINO=${{MySQL.MYSQL_HOST}}
DB_PORT_DESTINO=${{MySQL.MYSQL_PORT}}
DB_USER_DESTINO=${{MySQL.MYSQL_USER}}
DB_PASSWORD_DESTINO=${{MySQL.MYSQL_PASSWORD}}
DB_NAME_DESTINO=dw_proyectos_hist

# Seguridad
PM_TOKEN=tu_token_aqui
ADMIN_TOKEN=tu_token_admin_aqui
```

#### 5. Migrar datos a Railway MySQL
```bash
# Exportar datos locales
mysqldump -u root gestionproyectos_hist > backup_origen.sql
mysqldump -u root dw_proyectos_hist > backup_dw.sql

# Importar a Railway (usa las credenciales de Railway)
mysql -h railway_host -P railway_port -u railway_user -p railway_db < backup_origen.sql
mysql -h railway_host -P railway_port -u railway_user -p railway_db < backup_dw.sql
```

#### 6. Desplegar
Railway automáticamente detectará `railway.json` y desplegará tu app.

Tu dashboard estará disponible en: `https://tu-proyecto.up.railway.app`

---

## 🎨 Opción 2: Render.com

### Ventajas:
- ✅ Completamente gratis (con limitaciones)
- ✅ PostgreSQL gratuito
- ❌ Requiere migrar de MySQL a PostgreSQL

### Pasos:

#### 1. Crear cuenta en Render
1. Ve a [render.com](https://render.com)
2. Conecta tu cuenta GitHub

#### 2. Crear servicio Web
1. New → Web Service
2. Conecta tu repositorio `ProyectoETL`
3. Configuración:
   - **Build Command**: `pip install -r requirements-all.txt`
   - **Start Command**: `bash start.sh`
   - **Environment**: Python 3

#### 3. Crear base de datos PostgreSQL
1. New → PostgreSQL
2. Nombre: `etl-dashboard-db`
3. Plan: Free

#### 4. Configurar variables de entorno
En tu Web Service → Environment:

```env
FLASK_ENV=production
PORT=10000
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
```

**Nota**: Necesitarías convertir tu código de MySQL a PostgreSQL (usar SQLAlchemy).

---

## 🐍 Opción 3: PythonAnywhere

### Ventajas:
- ✅ MySQL incluido gratis
- ✅ Gratis permanentemente
- ❌ Configuración más manual

### Pasos:

1. Crea cuenta en [pythonanywhere.com](https://pythonanywhere.com)
2. Ve a "Web" → "Add a new web app"
3. Selecciona "Flask" con Python 3.11
4. Sube tu código vía Git o Files tab
5. Configura WSGI file para apuntar a `app.py`
6. Crea bases de datos MySQL en "Databases" tab
7. Importa tus `.sql` files

---

## 🔧 Opción 4: Google Cloud Run (Avanzado)

Requiere Dockerfile. Si te interesa, puedo crear uno.

### Costo estimado:
- Primeros 2M requests/mes: **GRATIS**
- Cloud SQL MySQL: ~$10/mes

---

## 📝 Notas Importantes

### Seguridad
1. **NUNCA** commitees passwords al repositorio
2. Usa variables de entorno para credenciales
3. Genera tokens seguros: `python -c "import secrets; print(secrets.token_hex(32))"`

### Performance
- Railway y Render tienen límites de memoria (512MB free tier)
- Si tu BD crece mucho, considera upgrade a plan pagado

### Mantenimiento
- Railway duerme apps después de 5 min inactividad (plan free)
- Render duerme después de 15 min inactividad
- Considera ping cada 10 min con UptimeRobot (gratis)

---

## 🆘 Troubleshooting

### Error: "Module not found"
```bash
# Verificar que requirements-all.txt tiene todas las dependencias
pip freeze > requirements-all.txt
```

### Error: "Connection refused" MySQL
- Verifica que las variables de entorno estén configuradas
- Chequea que MySQL service esté corriendo en Railway/Render

### App no inicia
- Revisa logs en tu plataforma cloud
- Verifica que `start.sh` tenga permisos de ejecución

---

## 📞 Soporte

Si tienes problemas:
1. Revisa logs en tu plataforma cloud
2. Verifica variables de entorno
3. Prueba localmente primero: `bash start.sh`

## 🎉 ¡Listo!

Tu dashboard ETL ahora está en la nube y accesible desde cualquier lugar.
