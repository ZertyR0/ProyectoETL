-- ===================================================================
-- PROCEDIMIENTO ETL COMPLETO CON MÉTRICAS
-- Incluye carga de defectos, capacitaciones, satisfacción y movimientos
-- Totalmente portable y autocontenido
-- ===================================================================

USE dw_proyectos_hist;

DELIMITER //

DROP PROCEDURE IF EXISTS sp_etl_completo_con_metricas//

CREATE PROCEDURE sp_etl_completo_con_metricas()
BEGIN
    DECLARE v_clientes INT DEFAULT 0;
    DECLARE v_empleados INT DEFAULT 0;
    DECLARE v_equipos INT DEFAULT 0;
    DECLARE v_proyectos INT DEFAULT 0;
    DECLARE v_tareas INT DEFAULT 0;
    DECLARE v_tiempo INT DEFAULT 0;
    DECLARE v_defectos INT DEFAULT 0;
    DECLARE v_capacitaciones INT DEFAULT 0;
    DECLARE v_satisfaccion INT DEFAULT 0;
    DECLARE v_movimientos INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 
            'ERROR' AS estado,
            'Fallo en proceso ETL' AS mensaje,
            NOW() AS fecha_hora;
    END;
    
    START TRANSACTION;
    
    -- ============================================================
    -- PASO 1: LIMPIAR DATAWAREHOUSE
    -- ============================================================
    SET FOREIGN_KEY_CHECKS = 0;
    
    DELETE FROM HechoMovimientoEmpleado;
    DELETE FROM HechoSatisfaccion;
    DELETE FROM HechoCapacitacion;
    DELETE FROM HechoDefecto;
    DELETE FROM HechoOKR;
    DELETE FROM HechoTarea;
    DELETE FROM HechoProyecto;
    DELETE FROM DimTiempo;
    DELETE FROM DimProyecto;
    DELETE FROM DimEquipo;
    DELETE FROM DimEmpleado;
    DELETE FROM DimCliente;
    
    SET FOREIGN_KEY_CHECKS = 1;
    
    -- ============================================================
    -- PASO 2: GENERAR DIMENSIÓN TIEMPO
    -- ============================================================
    SET @fecha = DATE_SUB(CURDATE(), INTERVAL 3 YEAR);
    SET @fecha_max = DATE_ADD(CURDATE(), INTERVAL 1 YEAR);
    
    WHILE @fecha <= @fecha_max DO
        INSERT INTO DimTiempo (id_tiempo, fecha, anio, trimestre, mes)
        VALUES (
            @fecha,
            @fecha,
            YEAR(@fecha),
            QUARTER(@fecha),
            MONTH(@fecha)
        )
        ON DUPLICATE KEY UPDATE fecha = @fecha;
        
        SET @fecha = DATE_ADD(@fecha, INTERVAL 1 DAY);
        SET v_tiempo = v_tiempo + 1;
    END WHILE;
    
    -- ============================================================
    -- PASO 3: CARGAR DIMENSIONES DESDE BD ORIGEN
    -- ============================================================
    
    INSERT INTO DimCliente (id_cliente, nombre, sector)
    SELECT id_cliente, nombre, sector
    FROM gestionproyectos_hist.cliente;
    SET v_clientes = ROW_COUNT();
    
    INSERT INTO DimEmpleado (id_empleado, nombre, puesto)
    SELECT id_empleado, nombre, puesto
    FROM gestionproyectos_hist.empleado;
    SET v_empleados = ROW_COUNT();
    
    INSERT INTO DimEquipo (id_equipo, nombre_equipo, descripcion)
    SELECT id_equipo, nombre_equipo, descripcion
    FROM gestionproyectos_hist.equipo;
    SET v_equipos = ROW_COUNT();
    
    INSERT INTO DimProyecto (
        id_proyecto, 
        nombre_proyecto, 
        fecha_inicio_plan, 
        fecha_fin_plan, 
        presupuesto, 
        estado,
        progreso_porcentaje
    )
    SELECT 
        p.id_proyecto,
        p.nombre,
        p.fecha_inicio,
        p.fecha_fin_plan,
        p.presupuesto,
        e.nombre_estado,
        IFNULL(
            (SELECT (COUNT(CASE WHEN t.id_estado = 4 THEN 1 END) * 100.0 / COUNT(*))
             FROM gestionproyectos_hist.tarea t
             WHERE t.id_proyecto = p.id_proyecto),
            0
        )
    FROM gestionproyectos_hist.proyecto p
    LEFT JOIN gestionproyectos_hist.estado e ON p.id_estado = e.id_estado
    WHERE p.id_estado IN (4, 5);
    SET v_proyectos = ROW_COUNT();
    
    -- ============================================================
    -- PASO 4: CARGAR HECHOS PRINCIPALES
    -- ============================================================
    
    -- HechoProyecto
    INSERT INTO HechoProyecto (
        id_proyecto, id_cliente, id_empleado_gerente, id_equipo,
        id_tiempo_fin_real, presupuesto, costo_real_proy,
        variacion_costos, cumplimiento_presupuesto,
        duracion_planificada, duracion_real, variacion_cronograma,
        cumplimiento_tiempo, tareas_total, tareas_completadas,
        tareas_canceladas, horas_plan_total, horas_reales_total,
        variacion_horas, cambios_equipo_proy
    )
    SELECT 
        p.id_proyecto, p.id_cliente, p.id_empleado_gerente,
        (SELECT teh.id_equipo 
         FROM gestionproyectos_hist.tareaequipohist teh
         INNER JOIN gestionproyectos_hist.tarea t ON teh.id_tarea = t.id_tarea
         WHERE t.id_proyecto = p.id_proyecto
         GROUP BY teh.id_equipo
         ORDER BY COUNT(*) DESC
         LIMIT 1),
        IFNULL(p.fecha_fin_real, p.fecha_fin_plan),
        p.presupuesto,
        IFNULL(p.costo_real, 0),
        IFNULL(p.costo_real, 0) - p.presupuesto,
        IF(IFNULL(p.costo_real, 0) <= p.presupuesto, 1, 0),
        DATEDIFF(p.fecha_fin_plan, p.fecha_inicio),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio), 0),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio), 0),
        IF(p.fecha_fin_real IS NULL, 0, IF(p.fecha_fin_real <= p.fecha_fin_plan, 1, 0)),
        IFNULL(t.total, 0),
        IFNULL(t.completadas, 0),
        IFNULL(t.canceladas, 0),
        IFNULL(t.horas_plan_total, 0),
        IFNULL(t.horas_reales_total, 0),
        IFNULL(t.horas_reales_total, 0) - IFNULL(t.horas_plan_total, 0),
        0
    FROM gestionproyectos_hist.proyecto p
    LEFT JOIN (
        SELECT 
            id_proyecto,
            COUNT(*) AS total,
            SUM(IF(id_estado = 4, 1, 0)) AS completadas,
            SUM(IF(id_estado = 5, 1, 0)) AS canceladas,
            SUM(horas_plan) AS horas_plan_total,
            SUM(horas_reales) AS horas_reales_total
        FROM gestionproyectos_hist.tarea
        GROUP BY id_proyecto
    ) t ON p.id_proyecto = t.id_proyecto
    WHERE p.id_estado IN (4, 5);
    
    -- HechoTarea
    INSERT INTO HechoTarea (
        id_tarea, id_proyecto, id_equipo, id_tiempo_fin_real,
        horas_plan, horas_reales, variacion_horas,
        cumplimiento_tiempo, costo_real_tarea
    )
    SELECT 
        t.id_tarea, t.id_proyecto,
        (SELECT teh.id_equipo 
         FROM gestionproyectos_hist.tareaequipohist teh
         WHERE teh.id_tarea = t.id_tarea
         ORDER BY teh.fecha_asignacion DESC
         LIMIT 1),
        IFNULL(t.fecha_fin_real, t.fecha_fin_plan),
        IFNULL(t.horas_plan, 0),
        IFNULL(t.horas_reales, 0),
        IFNULL(t.horas_reales, 0) - IFNULL(t.horas_plan, 0),
        IF(t.fecha_fin_real IS NULL, 0, IF(t.fecha_fin_real <= t.fecha_fin_plan, 1, 0)),
        0
    FROM gestionproyectos_hist.tarea t
    INNER JOIN gestionproyectos_hist.proyecto p ON t.id_proyecto = p.id_proyecto
    WHERE p.id_estado IN (4, 5);
    SET v_tareas = ROW_COUNT();
    
    -- ============================================================
    -- PASO 5: CARGAR HECHOS DE MÉTRICAS ADICIONALES
    -- ============================================================
    
    -- HechoDefecto
    INSERT INTO HechoDefecto (
        id_proyecto, id_tiempo_reporte, id_tiempo_resolucion,
        severidad, estado, dias_resolucion
    )
    SELECT 
        d.id_proyecto,
        d.fecha_reporte,
        d.fecha_resolucion,
        d.severidad,
        d.estado,
        IFNULL(DATEDIFF(d.fecha_resolucion, d.fecha_reporte), NULL)
    FROM gestionproyectos_hist.defecto d
    INNER JOIN gestionproyectos_hist.proyecto p ON d.id_proyecto = p.id_proyecto
    WHERE p.id_estado IN (4, 5);
    SET v_defectos = ROW_COUNT();
    
    -- HechoCapacitacion
    INSERT INTO HechoCapacitacion (
        id_empleado, id_tiempo_inicio, id_tiempo_fin,
        nombre_curso, horas_duracion, estado
    )
    SELECT 
        c.id_empleado,
        c.fecha_inicio,
        c.fecha_fin,
        c.nombre_curso,
        c.horas_duracion,
        c.estado
    FROM gestionproyectos_hist.capacitacion c;
    SET v_capacitaciones = ROW_COUNT();
    
    -- HechoSatisfaccion
    INSERT INTO HechoSatisfaccion (
        id_proyecto, id_cliente, id_tiempo_evaluacion, calificacion
    )
    SELECT 
        s.id_proyecto,
        s.id_cliente,
        s.fecha_evaluacion,
        s.calificacion
    FROM gestionproyectos_hist.satisfaccion_cliente s
    INNER JOIN gestionproyectos_hist.proyecto p ON s.id_proyecto = p.id_proyecto
    WHERE p.id_estado IN (4, 5);
    SET v_satisfaccion = ROW_COUNT();
    
    -- HechoMovimientoEmpleado
    INSERT INTO HechoMovimientoEmpleado (
        id_empleado, id_tiempo_movimiento, tipo_movimiento
    )
    SELECT 
        m.id_empleado,
        m.fecha_movimiento,
        m.tipo_movimiento
    FROM gestionproyectos_hist.movimiento_empleado m;
    SET v_movimientos = ROW_COUNT();
    
    COMMIT;
    
    -- RETORNAR RESULTADO EXITOSO
    SELECT 
        'EXITOSO' AS estado,
        'ETL completo con métricas ejecutado' AS mensaje,
        v_clientes AS clientes,
        v_empleados AS empleados,
        v_equipos AS equipos,
        v_proyectos AS proyectos,
        v_tareas AS tareas,
        v_tiempo AS registros_tiempo,
        v_defectos AS defectos,
        v_capacitaciones AS capacitaciones,
        v_satisfaccion AS evaluaciones_satisfaccion,
        v_movimientos AS movimientos_empleados,
        NOW() AS fecha_hora;
        
END//

DELIMITER ;

SELECT 'Procedimiento ETL completo con métricas creado' AS resultado;
