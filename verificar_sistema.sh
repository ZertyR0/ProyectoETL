#!/bin/bash

# ===================================================================
# VERIFICACIÓN DE PORTABILIDAD
# Ejecuta tests para validar que el sistema funciona correctamente
# ===================================================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           VERIFICACIÓN DEL SISTEMA ETL + BSC                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Función de test
run_test() {
    local test_name="$1"
    local expected="$2"
    local result="$3"
    
    if [ "$result" -eq "$expected" ]; then
        echo -e "${GREEN}✓${NC} $test_name: $result (esperado: $expected)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name: $result (esperado: $expected)"
        ((TESTS_FAILED++))
    fi
}

# ===================================================================
# TEST 1: Base de datos de origen
# ===================================================================
echo "📊 Verificando base de datos ORIGEN (gestionproyectos_hist)..."

clientes=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.cliente;" 2>/dev/null || echo "0")
run_test "Clientes en origen" 50 "$clientes"

empleados=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.empleado;" 2>/dev/null || echo "0")
run_test "Empleados en origen" 250 "$empleados"

proyectos=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.proyecto;" 2>/dev/null || echo "0")
run_test "Proyectos en origen" 50 "$proyectos"

defectos=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.defecto;" 2>/dev/null || echo "0")
run_test "Defectos en origen" 135 "$defectos"

capacitaciones=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.capacitacion;" 2>/dev/null || echo "0")
run_test "Capacitaciones en origen" 351 "$capacitaciones"

satisfacciones=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.satisfaccion_cliente;" 2>/dev/null || echo "0")
run_test "Satisfacciones en origen" 21 "$satisfacciones"

movimientos=$(mysql -u root -N -e "SELECT COUNT(*) FROM gestionproyectos_hist.movimiento_empleado;" 2>/dev/null || echo "0")
run_test "Movimientos empleados en origen" 282 "$movimientos"

# ===================================================================
# TEST 2: DataWarehouse
# ===================================================================
echo ""
echo "🏭 Verificando DATAWAREHOUSE (dw_proyectos_hist)..."

dim_clientes=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.DimCliente;" 2>/dev/null || echo "0")
run_test "DimCliente en DW" 50 "$dim_clientes"

dim_empleados=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.DimEmpleado;" 2>/dev/null || echo "0")
run_test "DimEmpleado en DW" 250 "$dim_empleados"

hecho_proyectos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoProyecto;" 2>/dev/null || echo "0")
run_test "HechoProyecto en DW (solo completados)" 26 "$hecho_proyectos"

hecho_defectos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoDefecto;" 2>/dev/null || echo "0")
run_test "HechoDefecto en DW" 135 "$hecho_defectos"

hecho_capacitaciones=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoCapacitacion;" 2>/dev/null || echo "0")
run_test "HechoCapacitacion en DW" 351 "$hecho_capacitaciones"

hecho_satisfacciones=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoSatisfaccion;" 2>/dev/null || echo "0")
run_test "HechoSatisfaccion en DW" 21 "$hecho_satisfacciones"

hecho_movimientos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoMovimientoEmpleado;" 2>/dev/null || echo "0")
run_test "HechoMovimientoEmpleado en DW" 282 "$hecho_movimientos"

# ===================================================================
# TEST 3: BSC y OKRs
# ===================================================================
echo ""
echo "🎯 Verificando BSC y OKRs..."

objetivos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.DimObjetivo;" 2>/dev/null || echo "0")
run_test "Objetivos BSC" 5 "$objetivos"

krs=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.DimKR;" 2>/dev/null || echo "0")
run_test "Key Results (KRs)" 10 "$krs"

mediciones=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoOKR;" 2>/dev/null || echo "0")
run_test "Mediciones OKR" 10 "$mediciones"

# Verificar que NO hay valores NULL en métricas críticas
valores_nulos=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.HechoOKR WHERE valor_observado IS NULL OR progreso_hacia_meta IS NULL;" 2>/dev/null || echo "0")
run_test "Valores NULL en OKRs (debe ser 0)" 0 "$valores_nulos"

# ===================================================================
# TEST 4: Métricas calculadas
# ===================================================================
echo ""
echo "📈 Verificando métricas calculadas..."

# Verificar que las métricas están en rangos razonables
costo_promedio=$(mysql -u root -N -e "SELECT ROUND(AVG(costo_real_proy)) FROM dw_proyectos_hist.HechoProyecto;" 2>/dev/null || echo "0")
if [ "$costo_promedio" -gt 100000 ] && [ "$costo_promedio" -lt 500000 ]; then
    echo -e "${GREEN}✓${NC} Costo promedio proyecto: \$$costo_promedio (rango válido)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Costo promedio proyecto: \$$costo_promedio (fuera de rango)"
    ((TESTS_FAILED++))
fi

satisfaccion=$(mysql -u root -N -e "SELECT ROUND(AVG(calificacion), 2) FROM dw_proyectos_hist.HechoSatisfaccion;" 2>/dev/null || echo "0")
if (( $(echo "$satisfaccion >= 3.5 && $satisfaccion <= 5.0" | bc -l) )); then
    echo -e "${GREEN}✓${NC} Satisfacción cliente promedio: $satisfaccion/5.0 (rango válido)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Satisfacción cliente promedio: $satisfaccion/5.0 (fuera de rango)"
    ((TESTS_FAILED++))
fi

# ===================================================================
# TEST 5: Vistas del dashboard
# ===================================================================
echo ""
echo "👁️  Verificando vistas del dashboard..."

vista_consolidada=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.vw_bsc_tablero_consolidado;" 2>/dev/null || echo "0")
run_test "Vista tablero consolidado" 5 "$vista_consolidada"

vista_detalle=$(mysql -u root -N -e "SELECT COUNT(*) FROM dw_proyectos_hist.vw_bsc_krs_detalle;" 2>/dev/null || echo "0")
run_test "Vista KRs detalle" 10 "$vista_detalle"

# ===================================================================
# TEST 6: Dashboard (si está corriendo)
# ===================================================================
echo ""
echo "🌐 Verificando Dashboard..."

if curl -s http://localhost:5000/api/estado > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend Flask respondiendo en http://localhost:5000"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Backend no está corriendo (ejecuta: cd 03_Dashboard && ./iniciar_dashboard.sh)"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend respondiendo en http://localhost:3000"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Frontend no está corriendo (ejecuta: cd 03_Dashboard && ./iniciar_dashboard.sh)"
fi

# ===================================================================
# RESUMEN FINAL
# ===================================================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    RESUMEN DE VERIFICACIÓN                    ║"
echo "╠════════════════════════════════════════════════════════════════╣"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "║  ${GREEN}✓ TODOS LOS TESTS PASARON${NC}                                   ║"
    echo "║                                                                ║"
    echo "║  Tests exitosos: $TESTS_PASSED                                           ║"
    echo "║  Tests fallidos: $TESTS_FAILED                                            ║"
    echo "║                                                                ║"
    echo "║  🎉 Sistema funcionando correctamente                          ║"
    echo "║  🚀 Listo para producción o demostración                       ║"
else
    echo -e "║  ${RED}✗ ALGUNOS TESTS FALLARON${NC}                                    ║"
    echo "║                                                                ║"
    echo "║  Tests exitosos: $TESTS_PASSED                                           ║"
    echo "║  Tests fallidos: $TESTS_FAILED                                            ║"
    echo "║                                                                ║"
    echo "║  ⚠️  Revisa los errores arriba                                 ║"
fi

echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Retornar código de salida apropiado
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
