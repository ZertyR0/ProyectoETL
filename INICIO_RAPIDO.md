# ⚡ INICIO RÁPIDO - ProyectoETL

## 🎯 Tu sistema está al 92% listo

Solo necesitas ejecutar un comando para tener todo funcionando.

---

## 📋 Pasos para Iniciar

### 1️⃣ Verificar el Sistema (Opcional)

```bash
./verificar_sistema.sh
```

Este script te muestra el estado actual del sistema.

---

### 2️⃣ Configurar Todo Automáticamente

```bash
./setup_local.sh
```

**Este comando hace:**
- ✅ Crea la base de datos origen (`gestionproyectos_hist`)
- ✅ Crea el datawarehouse (`dw_proyectos_hist`)
- ✅ Genera datos de prueba (clientes, empleados, proyectos, tareas)
- ✅ Ejecuta el proceso ETL inicial
- ✅ Instala todas las dependencias Python

**Tiempo estimado:** 2-3 minutos

---

### 3️⃣ Iniciar el Dashboard

```bash
./iniciar_dashboard.sh
```

**Este comando:**
- 🚀 Inicia el backend API en `http://localhost:5001`
- 🌐 Inicia el frontend en `http://localhost:8080`
- 🔓 Abre automáticamente el navegador

---

### 4️⃣ Usar el Dashboard

En el navegador (http://localhost:8080):

1. **Ver el estado** de las conexiones (deberían estar en verde ✅)

2. **Explorar los datos** existentes en las tablas

3. **Probar las funciones:**
   - 📊 **"Insertar Datos"** → Genera más datos de prueba
   - ⚙️ **"Ejecutar ETL"** → Procesa los datos del origen al DW
   - 📈 Ver las métricas calculadas
   - 🗑️ **"Limpiar Datos"** → Reinicia todo (opcional)

---

### 5️⃣ Detener el Dashboard

Cuando termines:

```bash
./detener_dashboard.sh
```

---

## 🔍 Comandos Útiles

### Ver datos en MySQL

```bash
# Base de datos origen
mysql -u root gestionproyectos_hist

# Datawarehouse
mysql -u root dw_proyectos_hist
```

### Consultas de ejemplo

```sql
-- Ver proyectos
USE gestionproyectos_hist;
SELECT * FROM Proyecto LIMIT 5;

-- Ver métricas del DW
USE dw_proyectos_hist;
SELECT * FROM HechoProyecto LIMIT 5;

-- Ver resumen de proyectos
SELECT * FROM v_resumen_proyectos;
```

### Ejecutar ETL manualmente

```bash
source venv/bin/activate
python3 02_ETL/scripts/etl_principal.py local
```

---

## 🐛 Si Algo Sale Mal

### MySQL no está corriendo

```bash
# macOS
brew services start mysql

# Verificar
mysql -u root -e "SELECT 1"
```

### Puerto ocupado

```bash
# Ver qué está usando el puerto
lsof -i :5001  # Backend
lsof -i :8080  # Frontend

# Matar proceso
kill -9 <PID>
```

### Reinstalar todo

```bash
./detener_dashboard.sh
rm -rf venv
./setup_local.sh
```

---

## 📖 Documentación Completa

Para más detalles, consulta:

- `README_COMPLETO.md` - Documentación completa del proyecto
- `GUIA_PRUEBA_LOCAL.md` - Guía detallada paso a paso
- `GUIA_DESPLIEGUE_3_MAQUINAS.md` - Para ambiente distribuido

---

## 🎓 ¿Qué puedes hacer con este proyecto?

✅ Aprender conceptos de ETL  
✅ Entender modelado dimensional  
✅ Practicar con Python, SQL y APIs  
✅ Ver un proyecto full-stack funcionando  
✅ Experimentar con datos y análisis  

---

## ⚡ Resumen de Comandos

```bash
# 1. Verificar (opcional)
./verificar_sistema.sh

# 2. Configurar (solo la primera vez)
./setup_local.sh

# 3. Iniciar
./iniciar_dashboard.sh

# 4. Navegar a http://localhost:8080 y usar el dashboard

# 5. Detener
./detener_dashboard.sh
```

---

## 🎉 ¡Listo!

Ahora tienes un sistema ETL completo funcionando en tu máquina local.

**¿Preguntas?** Revisa la documentación en `README_COMPLETO.md`

---

**Última actualización:** 22 de octubre de 2025
