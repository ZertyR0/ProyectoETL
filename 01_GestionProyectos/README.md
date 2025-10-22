# 📊 Sistema de Gestión de Proyectos (Base de Datos Origen)

Esta carpeta contiene todos los elementos relacionados con la base de datos origen del sistema ETL.

## 📁 Estructura

```
01_GestionProyectos/
├── README.md                    # Este archivo
├── scripts/
│   ├── crear_bd_origen.sql     # Script para crear la base de datos
│   └── generar_datos.py        # Script para generar datos de prueba
└── datos/
    └── datos_ejemplo.sql       # Datos de ejemplo (opcional)
```

## 🎯 Propósito

La base de datos **gestionproyectos_hist** almacena:
- **Clientes**: Información de clientes
- **Empleados**: Datos de empleados y roles
- **Equipos**: Equipos de trabajo
- **Proyectos**: Información completa de proyectos
- **Tareas**: Tareas asociadas a proyectos
- **Estados**: Estados de proyectos y tareas
- **Relaciones**: Asignaciones de equipos y miembros

## 🚀 Uso

1. **Crear la base de datos:**
   ```bash
   mysql -u root -p < scripts/crear_bd_origen.sql
   ```

2. **Generar datos de prueba:**
   ```bash
   python scripts/generar_datos.py
   ```

## 📋 Tablas Principales

- `Cliente` - Información de clientes
- `Empleado` - Datos de empleados 
- `Equipo` - Equipos de trabajo
- `Proyecto` - Proyectos principales
- `Tarea` - Tareas de proyectos
- `Estado` - Estados del sistema
- `MiembroEquipo` - Asignaciones de equipo
- `TareaEquipoHist` - Historial de asignaciones
