# ProyectoETL

Sistema completo de ETL (Extract, Transform, Load) para gestión de proyectos con Data Warehouse.

## 📋 Descripción

Este proyecto implementa un sistema ETL completo que:
- Extrae datos de una base de datos transaccional de gestión de proyectos
- Transforma y limpia los datos 
- Carga los datos en un Data Warehouse optimizado para análisis

## 🏗️ Arquitectura

### Bases de Datos
- **gestionproyectos_hist**: Base de datos transaccional (fuente)
- **dw_proyectos_hist**: Data Warehouse (destino)

### Componentes
- **ETL Principal**: Proceso completo de extracción, transformación y carga
- **ETL Remoto Portable**: Versión independiente para ejecución remota
- **Servidor ETL**: API HTTP para ejecución remota del ETL
- **Generación de Datos**: Script para poblar la base de datos de prueba

## 📁 Estructura del Proyecto

```
ProyectoETL/
├── README.md                    # Este archivo
├── generacion_datos.py          # Script para generar datos de prueba
├── etl_principal.py             # ETL principal local
├── etl_remoto_portable.py       # ETL portable para ejecución remota
├── servidor_etl_simple.py       # Servidor HTTP para ETL remoto
├── config_conexion.py           # Configuración de conexiones
├── script_creacion_db.sql       # Script de creación de BD transaccional
└── script_datawarehouse.sql     # Script de creación del Data Warehouse
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

### Dependencias de Python
```bash
pip install pandas sqlalchemy mysql-connector-python
```

### Configuración de Base de Datos

1. **Crear las bases de datos**:
   ```sql
   -- Ejecutar script_creacion_db.sql
   -- Ejecutar script_datawarehouse.sql
   ```

2. **Configurar conexiones**:
   Editar `config_conexion.py` con tus credenciales de MySQL.

## 📊 Uso

### 1. Generación de Datos de Prueba
```bash
python generacion_datos.py
```

### 2. Ejecución del ETL Local
```bash
python etl_principal.py
```

### 3. ETL Remoto Portable
```bash
python etl_remoto_portable.py
```

### 4. Servidor ETL (para acceso HTTP)
```bash
python servidor_etl_simple.py
```
Luego acceder a: `http://localhost:8081`

## 📈 Data Warehouse - Esquema Dimensional

### Tablas de Dimensiones
- **DimCliente**: Información de clientes
- **DimEmpleado**: Datos de empleados  
- **DimEquipo**: Información de equipos
- **DimProyecto**: Detalles de proyectos
- **DimTiempo**: Dimensión temporal

### Tabla de Hechos
- **FactTareas**: Métricas y KPIs de tareas

## 🔧 Configuración Avanzada

### Conexión Remota
Para habilitar conexiones remotas a MySQL:
1. Configurar `bind-address = 0.0.0.0` en MySQL
2. Crear usuario con permisos remotos
3. Abrir puerto 3306 en firewall

### Variables de Entorno
El sistema soporta configuración via variables de entorno:
- `DB_HOST`: Host de la base de datos
- `DB_PORT`: Puerto de MySQL  
- `DB_USER`: Usuario de base de datos
- `DB_PASSWORD`: Contraseña

## 📋 Funcionalidades

### ETL Principal
- ✅ Extracción de datos transaccionales
- ✅ Transformación y limpieza de datos
- ✅ Carga incremental en Data Warehouse
- ✅ Manejo de dimensiones SCD (Slowly Changing Dimensions)
- ✅ Logging y monitoreo

### ETL Remoto
- ✅ Ejecución independiente
- ✅ Auto-instalación de dependencias
- ✅ Configuración flexible
- ✅ Manejo de errores robusto

### Servidor ETL
- ✅ API REST para ejecución remota
- ✅ Interface web simple
- ✅ Logs de ejecución
- ✅ Estado de procesos

## 🛠️ Tecnologías Utilizadas

- **Python**: Lenguaje principal
- **Pandas**: Manipulación de datos
- **SQLAlchemy**: ORM y conexiones de base de datos
- **MySQL**: Sistema de gestión de base de datos
- **HTTP Server**: Para API remota

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver archivo LICENSE para detalles.

## 👥 Contribución

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📞 Soporte

Para soporte técnico o preguntas, crear un issue en el repositorio.
