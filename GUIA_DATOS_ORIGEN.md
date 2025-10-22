# 📊 Guía de Visualización de Datos Origen

## Vista Previa de Todas las Tablas

El dashboard ahora incluye una **vista completa** de todas las tablas de la base de datos origen (`gestionproyectos_hist`).

### 🎯 Características

1. **Vista Unificada**: Todas las tablas en una sola página
2. **Código de Colores**: Cada tabla tiene un borde de color diferente para fácil identificación
3. **Contador de Registros**: Muestra el total de registros en cada tabla
4. **Vista Previa Limitada**: Muestra los últimos 10-15 registros por tabla
5. **Formato Inteligente**: 
   - Números con formato de moneda
   - Fechas formateadas
   - Estados con badges de colores
   - Valores nulos claramente marcados

### 📋 Tablas Disponibles

| Tabla | Color | Descripción | Límite de Registros |
|-------|-------|-------------|---------------------|
| **Estado** | Azul (Primary) | Catálogo de estados | 10 |
| **Cliente** | Verde (Success) | Información de clientes | 10 |
| **Empleado** | Celeste (Info) | Datos de empleados | 10 |
| **Equipo** | Amarillo (Warning) | Equipos de trabajo | 10 |
| **Proyecto** | Rojo (Danger) | Proyectos registrados | 15 |
| **MiembroEquipo** | Gris (Secondary) | Asignación de empleados | 15 |
| **Tarea** | Negro (Dark) | Tareas de proyectos | 15 |

### 🎨 Navegación

1. Haz clic en **"Datos Origen"** en el menú lateral
2. La página carga automáticamente todas las tablas
3. Desplázate hacia abajo para ver cada tabla
4. Usa el botón de **actualizar** (🔄) en la esquina superior derecha para recargar

### 🔄 API Endpoint

**Endpoint:** `GET /datos-origen/todas-tablas`

**Respuesta:**
```json
{
  "success": true,
  "tablas": [
    {
      "tabla": "Estado",
      "total_registros": 6,
      "registros_mostrados": 6,
      "columnas": ["id_estado", "nombre_estado", "descripcion", "activo"],
      "datos": [
        {
          "id_estado": 1,
          "nombre_estado": "Pendiente",
          "descripcion": "Proyecto o tarea pendiente de iniciar",
          "activo": 1
        }
      ]
    }
  ]
}
```

### 💡 Consejos

- **Generación de Datos**: Usa el botón "Generar Datos" en el Control ETL para crear datos de prueba
- **Estados Aleatorios**: Los proyectos generados incluyen estados variados (no solo completados/cancelados)
- **Filtrado ETL**: El ETL filtra automáticamente solo proyectos Completados y Cancelados para el DataWarehouse
- **Actualización**: Los datos se muestran ordenados por ID descendente (más recientes primero)

### 🎯 Casos de Uso

1. **Verificación de Datos**: Confirmar que los datos se generaron correctamente
2. **Depuración**: Identificar problemas en los datos antes del ETL
3. **Análisis Exploratorio**: Entender la estructura y contenido de cada tabla
4. **Auditoría**: Revisar la calidad de los datos de origen

### 🔧 Personalización

Para cambiar los límites de registros mostrados, edita el archivo:
- **Backend**: `03_Dashboard/backend/app.py`
- **Función**: `obtener_todas_tablas_origen()`
- **Variable**: `tablas_config[]['limite']`

```python
tablas_config = [
    {'nombre': 'Estado', 'limite': 10},
    {'nombre': 'Proyecto', 'limite': 20},  # Cambiar aquí
    # ...
]
```

### 📱 Responsive Design

- En pantallas grandes: Tablas con scroll horizontal
- En móviles: Sidebar colapsado, tablas adaptativas
- Optimizado para tablets y desktops

---

**Última actualización:** 22 de octubre de 2025
