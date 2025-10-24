-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS SEGUROS - DATAWAREHOUSE
-- Prevención de acceso directo a datos
-- =========================================================

USE dw_proyectos_hist;

-- Eliminar procedimientos existentes
DROP PROCEDURE IF EXISTS sp_dw_obtener_conteos;
DROP PROCEDURE IF EXISTS sp_dw_buscar_proyecto;
DROP PROCEDURE IF EXISTS sp_dw_buscar_cliente;
DROP PROCEDURE IF EXISTS sp_dw_buscar_empleado;
DROP PROCEDURE IF EXISTS sp_dw_validar_migracion;
DROP PROCEDURE IF EXISTS sp_dw_obtener_metricas;

-- Eliminar vistas existentes
DROP VIEW IF EXISTS v_dw_resumen;
DROP VIEW IF EXISTS v_dw_metricas_generales;

-- =========================================================
-- TABLA DE AUDITORÍA
-- =========================================================

CREATE TABLE IF NOT EXISTS AuditoriaConsultas (
    id_auditoria BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_consulta VARCHAR(50) NOT NULL,
    usuario VARCHAR(100) DEFAULT USER(),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parametros TEXT,
    resultados_count INT DEFAULT 0,
    INDEX idx_fecha (fecha_hora),
    INDEX idx_tipo (tipo_consulta)
) ENGINE=InnoDB;

-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =========================================================

DELIMITER //

-- Procedimiento: Obtener conteos generales (sin datos sensibles)
CREATE PROCEDURE sp_dw_obtener_conteos()
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('CONTEOS', 'General');
    
    -- Retornar solo conteos
    SELECT 
        'DimCliente' AS tabla,
        COUNT(*) AS total
    FROM DimCliente
    
    UNION ALL
    
    SELECT 'DimEmpleado', COUNT(*)
    FROM DimEmpleado
    
    UNION ALL
    
    SELECT 'DimEquipo', COUNT(*)
    FROM DimEquipo
    
    UNION ALL
    
    SELECT 'DimProyecto', COUNT(*)
    FROM DimProyecto
    
    UNION ALL
    
    SELECT 'DimTiempo', COUNT(*)
    FROM DimTiempo
    
    UNION ALL
    
    SELECT 'HechoProyecto', COUNT(*)
    FROM HechoProyecto
    
    UNION ALL
    
    SELECT 'HechoTarea', COUNT(*)
    FROM HechoTarea;
END//

-- Procedimiento: Buscar proyecto por ID (datos limitados)
CREATE PROCEDURE sp_dw_buscar_proyecto(
    IN p_id_proyecto INT
)
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros, resultados_count)
    SELECT 'BUSCAR_PROYECTO', p_id_proyecto, COUNT(*)
    FROM DimProyecto WHERE id_proyecto = p_id_proyecto;
    
    -- Retornar datos del proyecto (solo DimProyecto, no datos sensibles)
    SELECT 
        dp.id_proyecto,
        dp.nombre_proyecto,
        dp.descripcion,
        dp.fecha_inicio,
        dp.fecha_fin_plan,
        dp.presupuesto_plan,
        dp.prioridad
    FROM DimProyecto dp
    WHERE dp.id_proyecto = p_id_proyecto;
    
    -- Retornar métricas del HechoProyecto
    SELECT 
        hp.id_proyecto,
        hp.duracion_planificada,
        hp.duracion_real,
        hp.cumplimiento_tiempo,
        hp.presupuesto,
        hp.costo_real,
        hp.cumplimiento_presupuesto,
        hp.porcentaje_completado,
        hp.tareas_total,
        hp.tareas_completadas
    FROM HechoProyecto hp
    WHERE hp.id_proyecto = p_id_proyecto;
END//

-- Procedimiento: Buscar cliente por ID (solo métricas)
CREATE PROCEDURE sp_dw_buscar_cliente(
    IN p_id_cliente INT
)
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('BUSCAR_CLIENTE', p_id_cliente);
    
    -- Solo retornar si existe y métricas básicas
    SELECT 
        id_cliente,
        'EXISTE' AS estado,
        activo,
        fecha_carga
    FROM DimCliente
    WHERE id_cliente = p_id_cliente;
    
    -- Contar proyectos del cliente
    SELECT 
        COUNT(*) AS total_proyectos,
        SUM(CASE WHEN cumplimiento_tiempo = 1 THEN 1 ELSE 0 END) AS proyectos_a_tiempo,
        SUM(CASE WHEN cumplimiento_presupuesto = 1 THEN 1 ELSE 0 END) AS proyectos_en_presupuesto
    FROM HechoProyecto
    WHERE id_cliente = p_id_cliente;
END//

-- Procedimiento: Buscar empleado por ID (solo métricas)
CREATE PROCEDURE sp_dw_buscar_empleado(
    IN p_id_empleado INT
)
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('BUSCAR_EMPLEADO', p_id_empleado);
    
    -- Solo retornar si existe
    SELECT 
        id_empleado,
        'EXISTE' AS estado,
        puesto,
        departamento,
        activo,
        fecha_carga
    FROM DimEmpleado
    WHERE id_empleado = p_id_empleado;
    
    -- Contar proyectos gestionados
    SELECT 
        COUNT(*) AS proyectos_gestionados,
        ROUND(AVG(porcentaje_completado), 2) AS promedio_completitud
    FROM HechoProyecto
    WHERE id_empleado_gerente = p_id_empleado;
END//

-- Procedimiento: Validar migración (comparar conteos)
CREATE PROCEDURE sp_dw_validar_migracion()
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('VALIDAR_MIGRACION', 'Comparación de conteos');
    
    -- Retornar resumen de validación
    SELECT 
        'DimCliente' AS dimension,
        COUNT(*) AS registros,
        MIN(fecha_carga) AS primera_carga,
        MAX(fecha_carga) AS ultima_carga
    FROM DimCliente
    
    UNION ALL
    
    SELECT 
        'DimEmpleado',
        COUNT(*),
        MIN(fecha_carga),
        MAX(fecha_carga)
    FROM DimEmpleado
    
    UNION ALL
    
    SELECT 
        'DimProyecto',
        COUNT(*),
        MIN(fecha_carga),
        MAX(fecha_carga)
    FROM DimProyecto
    
    UNION ALL
    
    SELECT 
        'HechoProyecto',
        COUNT(*),
        MIN(fecha_carga),
        MAX(fecha_carga)
    FROM HechoProyecto;
END//

-- Procedimiento: Obtener métricas generales (agregadas)
CREATE PROCEDURE sp_dw_obtener_metricas()
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('OBTENER_METRICAS', 'Métricas generales');
    
    -- Métricas de proyectos
    SELECT 
        'PROYECTOS' AS categoria,
        COUNT(*) AS total,
        ROUND(AVG(porcentaje_completado), 2) AS promedio_completitud,
        SUM(CASE WHEN cumplimiento_tiempo = 1 THEN 1 ELSE 0 END) AS total_a_tiempo,
        SUM(CASE WHEN cumplimiento_presupuesto = 1 THEN 1 ELSE 0 END) AS total_en_presupuesto,
        ROUND(AVG(duracion_real), 2) AS promedio_duracion_dias
    FROM HechoProyecto
    
    UNION ALL
    
    -- Métricas de tareas
    SELECT 
        'TAREAS',
        COUNT(*),
        ROUND(AVG(progreso_porcentaje), 2),
        SUM(CASE WHEN cumplimiento_tiempo = 1 THEN 1 ELSE 0 END),
        0,
        ROUND(AVG(duracion_real), 2)
    FROM HechoTarea;
END//

-- Procedimiento: Obtener proyectos recientes (últimos N)
CREATE PROCEDURE sp_dw_obtener_proyectos_recientes(
    IN p_limite INT
)
BEGIN
    -- Registrar auditoría
    INSERT INTO AuditoriaConsultas (tipo_consulta, parametros)
    VALUES ('PROYECTOS_RECIENTES', p_limite);
    
    -- Solo IDs y métricas básicas
    SELECT 
        hp.id_proyecto,
        dp.nombre_proyecto,
        hp.cumplimiento_tiempo,
        hp.cumplimiento_presupuesto,
        hp.porcentaje_completado,
        hp.fecha_carga
    FROM HechoProyecto hp
    JOIN DimProyecto dp ON hp.id_proyecto = dp.id_proyecto
    ORDER BY hp.fecha_carga DESC
    LIMIT p_limite;
END//

DELIMITER ;

-- =========================================================
-- VISTAS SEGURAS (SOLO MÉTRICAS AGREGADAS)
-- =========================================================

-- Vista: Resumen general del DW
CREATE VIEW v_dw_resumen AS
SELECT 
    (SELECT COUNT(*) FROM DimCliente) AS total_clientes,
    (SELECT COUNT(*) FROM DimEmpleado) AS total_empleados,
    (SELECT COUNT(*) FROM DimEquipo) AS total_equipos,
    (SELECT COUNT(*) FROM DimProyecto) AS total_proyectos,
    (SELECT COUNT(*) FROM HechoProyecto) AS total_hechos_proyecto,
    (SELECT COUNT(*) FROM HechoTarea) AS total_hechos_tarea,
    (SELECT COUNT(*) FROM DimTiempo) AS total_registros_tiempo;

-- Vista: Métricas generales (agregadas)
CREATE VIEW v_dw_metricas_generales AS
SELECT 
    COUNT(*) AS total_proyectos,
    ROUND(AVG(porcentaje_completado), 2) AS promedio_completitud,
    SUM(CASE WHEN cumplimiento_tiempo = 1 THEN 1 ELSE 0 END) AS proyectos_a_tiempo,
    SUM(CASE WHEN cumplimiento_presupuesto = 1 THEN 1 ELSE 0 END) AS proyectos_en_presupuesto,
    ROUND(AVG(duracion_real), 2) AS promedio_duracion_dias,
    SUM(presupuesto) AS presupuesto_total,
    SUM(costo_real) AS costo_real_total,
    SUM(tareas_total) AS tareas_totales,
    SUM(tareas_completadas) AS tareas_completadas_totales
FROM HechoProyecto;

-- =========================================================
-- PERMISOS (Opcional - descomentar según necesidad)
-- =========================================================

/*
-- Usuario limitado para consultas DW
DROP USER IF EXISTS 'dw_readonly'@'localhost';
CREATE USER 'dw_readonly'@'localhost' IDENTIFIED BY 'password_seguro_dw';

-- Solo EXECUTE en procedimientos
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_obtener_conteos TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_buscar_proyecto TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_buscar_cliente TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_buscar_empleado TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_validar_migracion TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_obtener_metricas TO 'dw_readonly'@'localhost';
GRANT EXECUTE ON PROCEDURE dw_proyectos_hist.sp_dw_obtener_proyectos_recientes TO 'dw_readonly'@'localhost';

-- SELECT solo en vistas
GRANT SELECT ON dw_proyectos_hist.v_dw_resumen TO 'dw_readonly'@'localhost';
GRANT SELECT ON dw_proyectos_hist.v_dw_metricas_generales TO 'dw_readonly'@'localhost';

-- Sin acceso a tablas directamente
-- REVOKE ALL en tablas está implícito al no otorgar permisos

FLUSH PRIVILEGES;
*/

-- =========================================================
-- VERIFICACIÓN
-- =========================================================

SELECT 'Procedimientos almacenados DW creados exitosamente' AS resultado;

-- Listar procedimientos
SELECT ROUTINE_NAME, ROUTINE_TYPE
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'dw_proyectos_hist'
  AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

-- Listar vistas
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'dw_proyectos_hist'
ORDER BY TABLE_NAME;
