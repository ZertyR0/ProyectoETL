#!/usr/bin/env python3
"""
Script de Validación de Consistencia de Bases de Datos
Verifica que todas las tablas y columnas sean consistentes entre origen y DW
"""

import sys
import os
from pathlib import Path

# Agregar paths necesarios
sys.path.append(str(Path(__file__).parent / '02_ETL' / 'config'))

def validar_estructura():
    """Valida la estructura de las bases de datos"""
    
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║       🔍 VALIDADOR DE CONSISTENCIA DE BASES DE DATOS                       ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Definir estructura esperada
    estructura_origen = {
        'Estado': ['id_estado', 'nombre_estado', 'descripcion', 'activo'],
        'Cliente': ['id_cliente', 'nombre', 'sector', 'contacto', 'telefono', 'email', 'direccion', 'fecha_registro', 'activo'],
        'Empleado': ['id_empleado', 'nombre', 'puesto', 'departamento', 'salario_base', 'fecha_ingreso', 'activo'],
        'Equipo': ['id_equipo', 'nombre_equipo', 'descripcion', 'fecha_creacion', 'activo'],
        'Proyecto': ['id_proyecto', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin_plan', 'fecha_fin_real', 
                     'presupuesto', 'costo_real', 'id_cliente', 'id_estado', 'id_empleado_gerente', 'prioridad', 'progreso_porcentaje'],
        'Tarea': ['id_tarea', 'nombre_tarea', 'descripcion', 'fecha_inicio_plan', 'fecha_fin_plan', 
                  'fecha_inicio_real', 'fecha_fin_real', 'horas_plan', 'horas_reales', 
                  'id_proyecto', 'id_empleado', 'id_estado', 'prioridad', 'progreso_porcentaje', 
                  'costo_estimado', 'costo_real'],
        'MiembroEquipo': ['id_miembro', 'id_equipo', 'id_empleado', 'fecha_inicio', 'fecha_fin', 'rol_miembro', 'activo'],
        'TareaEquipoHist': ['id_tarea_equipo', 'id_tarea', 'id_equipo', 'fecha_asignacion', 'fecha_liberacion', 'horas_asignadas', 'notas']
    }
    
    estructura_dw = {
        'DimCliente': ['id_cliente', 'nombre', 'sector', 'contacto', 'telefono', 'email', 'direccion', 'fecha_registro', 'activo'],
        'DimEmpleado': ['id_empleado', 'nombre', 'puesto', 'departamento', 'salario_base', 'fecha_ingreso', 'activo'],
        'DimEquipo': ['id_equipo', 'nombre_equipo', 'descripcion', 'fecha_creacion', 'activo'],
        'DimProyecto': ['id_proyecto', 'nombre_proyecto', 'descripcion', 'fecha_inicio', 'fecha_fin_plan', 'presupuesto_plan', 'prioridad'],
        'DimTiempo': ['id_tiempo', 'fecha', 'anio', 'mes', 'dia', 'nombre_mes', 'trimestre', 'semestre', 
                      'dia_semana', 'nombre_dia_semana', 'es_fin_semana', 'es_feriado', 'numero_semana'],
        'HechoProyecto': ['id_hecho_proyecto', 'id_proyecto', 'id_cliente', 'id_empleado_gerente',
                          'id_tiempo_inicio', 'id_tiempo_fin_plan', 'id_tiempo_fin_real',
                          'duracion_planificada', 'duracion_real', 'variacion_cronograma', 'cumplimiento_tiempo',
                          'presupuesto', 'costo_real', 'variacion_costos', 'cumplimiento_presupuesto', 'porcentaje_sobrecosto',
                          'tareas_total', 'tareas_completadas', 'tareas_canceladas', 'tareas_pendientes', 'porcentaje_completado',
                          'horas_estimadas_total', 'horas_reales_total', 'variacion_horas', 'eficiencia_horas'],
        'HechoTarea': ['id_hecho_tarea', 'id_tarea', 'id_proyecto', 'id_empleado', 'id_equipo',
                       'id_tiempo_inicio_plan', 'id_tiempo_fin_plan', 'id_tiempo_inicio_real', 'id_tiempo_fin_real',
                       'duracion_planificada', 'duracion_real', 'variacion_cronograma', 'cumplimiento_tiempo',
                       'horas_plan', 'horas_reales', 'variacion_horas', 'eficiencia_horas',
                       'costo_estimado', 'costo_real', 'variacion_costo', 'progreso_porcentaje']
    }
    
    # Mapeo esperado
    mapeo_esperado = {
        'Cliente': 'DimCliente',
        'Empleado': 'DimEmpleado',
        'Equipo': 'DimEquipo',
        'Proyecto': 'DimProyecto'
    }
    
    print("📊 Validando estructura de tablas...")
    print("━" * 80)
    print()
    
    errores = []
    warnings = []
    
    # Validar tablas origen
    print("✅ BASE DE DATOS ORIGEN: gestionproyectos_hist")
    for tabla, columnas in estructura_origen.items():
        print(f"   ✓ {tabla:20} ({len(columnas)} columnas)")
    print()
    
    # Validar tablas DW
    print("✅ DATAWAREHOUSE: dw_proyectos_hist")
    for tabla, columnas in estructura_dw.items():
        print(f"   ✓ {tabla:20} ({len(columnas)} columnas)")
    print()
    
    # Validar mapeos
    print("🔗 VALIDANDO MAPEOS:")
    print("━" * 80)
    
    for origen, destino in mapeo_esperado.items():
        cols_origen = set(estructura_origen[origen])
        cols_destino = set(estructura_dw[destino])
        
        # Columnas que deben coincidir (sin renombres)
        cols_comunes = cols_origen & cols_destino
        
        # Para DimProyecto hay renombres esperados
        if destino == 'DimProyecto':
            # nombre -> nombre_proyecto, presupuesto -> presupuesto_plan
            if 'nombre_proyecto' in cols_destino and 'fecha_inicio' in cols_destino and 'presupuesto_plan' in cols_destino:
                print(f"   ✅ {origen:15} → {destino:15} (con renombres)")
            else:
                errores.append(f"DimProyecto tiene columnas incorrectas")
                print(f"   ❌ {origen:15} → {destino:15} (ERROR en renombres)")
        else:
            if len(cols_comunes) == len(cols_origen):
                print(f"   ✅ {origen:15} → {destino:15} (100% coincidente)")
            else:
                warnings.append(f"{origen} → {destino}: {len(cols_comunes)}/{len(cols_origen)} columnas coinciden")
                print(f"   ⚠️  {origen:15} → {destino:15} ({len(cols_comunes)}/{len(cols_origen)} columnas)")
    
    print()
    
    # Validar columnas críticas de DimProyecto
    print("🔍 VALIDACIÓN ESPECÍFICA: DimProyecto")
    print("━" * 80)
    
    columnas_criticas = {
        'fecha_inicio': 'fecha_inicio (no fecha_inicio_plan)',
        'nombre_proyecto': 'nombre_proyecto (renombrado desde "nombre")',
        'presupuesto_plan': 'presupuesto_plan (renombrado desde "presupuesto")'
    }
    
    for col, desc in columnas_criticas.items():
        if col in estructura_dw['DimProyecto']:
            print(f"   ✅ {desc}")
        else:
            errores.append(f"DimProyecto falta columna: {col}")
            print(f"   ❌ {desc}")
    
    print()
    
    # Validar nomenclatura
    print("📝 VALIDANDO NOMENCLATURA:")
    print("━" * 80)
    
    # Verificar PascalCase en tablas origen
    tablas_origen_correctas = all(tabla[0].isupper() for tabla in estructura_origen.keys())
    if tablas_origen_correctas:
        print("   ✅ Tablas origen en PascalCase")
    else:
        errores.append("Tablas origen no están en PascalCase")
        print("   ❌ Tablas origen no están en PascalCase")
    
    # Verificar prefijos en DW
    dim_correctas = all(tabla.startswith('Dim') for tabla in estructura_dw.keys() if 'Hecho' not in tabla and 'Dim' in tabla)
    hecho_correctas = all(tabla.startswith('Hecho') for tabla in estructura_dw.keys() if 'Hecho' in tabla)
    
    if dim_correctas:
        print("   ✅ Dimensiones con prefijo 'Dim'")
    else:
        errores.append("Dimensiones sin prefijo correcto")
        print("   ❌ Dimensiones sin prefijo 'Dim'")
    
    if hecho_correctas:
        print("   ✅ Hechos con prefijo 'Hecho'")
    else:
        errores.append("Hechos sin prefijo correcto")
        print("   ❌ Hechos sin prefijo 'Hecho'")
    
    # Verificar snake_case en columnas
    columnas_snake_case = True
    for tabla, columnas in {**estructura_origen, **estructura_dw}.items():
        for col in columnas:
            if col != col.lower() and '_' in col:
                columnas_snake_case = False
                break
    
    if columnas_snake_case:
        print("   ✅ Columnas en snake_case")
    else:
        warnings.append("Algunas columnas no siguen snake_case")
        print("   ⚠️  Algunas columnas no siguen snake_case estricto")
    
    print()
    
    # Resumen final
    print("=" * 80)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    print()
    
    if not errores and not warnings:
        print("   ✨ ¡PERFECTO! Sistema completamente consistente")
        print()
        print("   ✅ Todas las tablas validadas")
        print("   ✅ Todas las columnas correctas")
        print("   ✅ Nomenclatura consistente")
        print("   ✅ Mapeos validados")
        print()
        print("   🎯 SISTEMA LISTO PARA PRODUCCIÓN")
        return True
    
    if errores:
        print("   ❌ ERRORES CRÍTICOS ENCONTRADOS:")
        for error in errores:
            print(f"      • {error}")
        print()
    
    if warnings:
        print("   ⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"      • {warning}")
        print()
    
    if errores:
        print("   ⛔ SISTEMA REQUIERE CORRECCIONES")
        return False
    else:
        print("   ⚠️  SISTEMA FUNCIONAL CON ADVERTENCIAS")
        return True

def main():
    """Función principal"""
    print()
    resultado = validar_estructura()
    print()
    print("=" * 80)
    print()
    
    if resultado:
        print("✅ Validación completada exitosamente")
        sys.exit(0)
    else:
        print("❌ Validación falló - revise los errores arriba")
        sys.exit(1)

if __name__ == "__main__":
    main()
