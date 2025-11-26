-- PROCEDIMIENTO ETL ADAPTADO A ESTRUCTURAS REALES
-- Compatible con las tablas tal como están ahora

USE dw_proyectos_hist;

DELIMITER //

DROP PROCEDURE IF EXISTS sp_etl_adaptado//

CREATE PROCEDURE sp_etl_adaptado()
BEGIN
    DECLARE v_clientes INT DEFAULT 0;
    DECLARE v_empleados INT DEFAULT 0;
    DECLARE v_equipos INT DEFAULT 0;
    DECLARE v_proyectos INT DEFAULT 0;
    DECLARE v_tareas INT DEFAULT 0;
    DECLARE v_tiempo INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 
            'ERROR' AS estado,
            CONCAT('Error en línea: ', @error_msg) AS mensaje,
            NOW() AS fecha_hora;
    END;
    
    START TRANSACTION;
    
    -- PASO 1: LIMPIAR DATAWAREHOUSE
    SET FOREIGN_KEY_CHECKS = 0;
    
    DELETE FROM HechoOKR;
    DELETE FROM HechoTarea;
    DELETE FROM HechoProyecto;
    DELETE FROM DimTiempo;
    DELETE FROM DimProyecto;
    DELETE FROM DimEquipo;
    DELETE FROM DimEmpleado;
    DELETE FROM DimCliente;
    
    SET FOREIGN_KEY_CHECKS = 1;
    
    -- PASO 2: GENERAR DIMENSIÓN TIEMPO (con DATE, no INT)
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
    
    -- PASO 3: CARGAR DIMENSIONES DESDE BD ORIGEN (estructuras reales)
    
    -- DimCliente (solo 3 columnas: id_cliente, nombre, sector)
    INSERT INTO DimCliente (id_cliente, nombre, sector)
    SELECT id_cliente, nombre, sector
    FROM gestionproyectos_hist.cliente;
    
    SET v_clientes = ROW_COUNT();
    
    -- DimEmpleado (solo 3 columnas: id_empleado, nombre, puesto)
    INSERT INTO DimEmpleado (id_empleado, nombre, puesto)
    SELECT id_empleado, nombre, puesto
    FROM gestionproyectos_hist.empleado;
    
    SET v_empleados = ROW_COUNT();
    
    -- DimEquipo (3 columnas: id_equipo, nombre_equipo, descripcion)
    INSERT INTO DimEquipo (id_equipo, nombre_equipo, descripcion)
    SELECT id_equipo, nombre_equipo, descripcion
    FROM gestionproyectos_hist.equipo;
    
    SET v_equipos = ROW_COUNT();
    
    -- DimProyecto (mapear columnas correctas)
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
        -- Calcular progreso basado en tareas completadas
        IFNULL(
            (SELECT (COUNT(CASE WHEN t.id_estado = 4 THEN 1 END) * 100.0 / COUNT(*))
             FROM gestionproyectos_hist.tarea t
             WHERE t.id_proyecto = p.id_proyecto),
            0
        )
    FROM gestionproyectos_hist.proyecto p
    LEFT JOIN gestionproyectos_hist.estado e ON p.id_estado = e.id_estado
    WHERE p.id_estado IN (4, 5);  -- Solo completados y cancelados
    
    SET v_proyectos = ROW_COUNT();
    
    -- PASO 4: CARGAR HECHOS (adaptado a estructuras reales)
    
    -- HechoProyecto
    INSERT INTO HechoProyecto (
        id_proyecto,
        id_cliente,
        id_empleado_gerente,
        id_equipo,
        id_tiempo_fin_real,
        presupuesto,
        costo_real_proy,
        variacion_costos,
        cumplimiento_presupuesto,
        duracion_planificada,
        duracion_real,
        variacion_cronograma,
        cumplimiento_tiempo,
        tareas_total,
        tareas_completadas,
        tareas_canceladas,
        horas_plan_total,
        horas_reales_total,
        variacion_horas,
        cambios_equipo_proy
    )
    SELECT 
        p.id_proyecto,
        p.id_cliente,
        p.id_empleado_gerente,
        -- Equipo principal del proyecto
        (SELECT teh.id_equipo 
         FROM gestionproyectos_hist.tareaequipohist teh
         INNER JOIN gestionproyectos_hist.tarea t ON teh.id_tarea = t.id_tarea
         WHERE t.id_proyecto = p.id_proyecto
         GROUP BY teh.id_equipo
         ORDER BY COUNT(*) DESC
         LIMIT 1),
        -- id_tiempo_fin_real (usando fecha_fin_real o fecha_fin_plan)
        IFNULL(p.fecha_fin_real, p.fecha_fin_plan),
        -- Métricas financieras
        p.presupuesto,
        IFNULL(p.costo_real, 0),
        IFNULL(p.costo_real, 0) - p.presupuesto,
        IF(IFNULL(p.costo_real, 0) <= p.presupuesto, 1, 0),
        -- Métricas de tiempo
        DATEDIFF(p.fecha_fin_plan, p.fecha_inicio),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio), 0),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio), 0),
        IF(p.fecha_fin_real IS NULL, 0, IF(p.fecha_fin_real <= p.fecha_fin_plan, 1, 0)),
        -- Métricas de tareas (subquery)
        IFNULL(t.total, 0),
        IFNULL(t.completadas, 0),
        IFNULL(t.canceladas, 0),
        IFNULL(t.horas_plan_total, 0),
        IFNULL(t.horas_reales_total, 0),
        IFNULL(t.horas_reales_total, 0) - IFNULL(t.horas_plan_total, 0),
        0  -- cambios_equipo_proy (lo dejamos en 0 por ahora)
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
    WHERE p.id_estado IN (4, 5);  -- Solo completados y cancelados
    
    -- HechoTarea
    INSERT INTO HechoTarea (
        id_tarea,
        id_proyecto,
        id_equipo,
        id_tiempo_fin_real,
        horas_plan,
        horas_reales,
        variacion_horas,
        cumplimiento_tiempo,
        costo_real_tarea
    )
    SELECT 
        t.id_tarea,
        t.id_proyecto,
        -- Equipo asignado a la tarea
        (SELECT teh.id_equipo 
         FROM gestionproyectos_hist.tareaequipohist teh
         WHERE teh.id_tarea = t.id_tarea
         ORDER BY teh.fecha_asignacion DESC
         LIMIT 1),
        -- id_tiempo_fin_real
        IFNULL(t.fecha_fin_real, t.fecha_fin_plan),
        -- Métricas
        IFNULL(t.horas_plan, 0),
        IFNULL(t.horas_reales, 0),
        IFNULL(t.horas_reales, 0) - IFNULL(t.horas_plan, 0),
        IF(t.fecha_fin_real IS NULL, 0, IF(t.fecha_fin_real <= t.fecha_fin_plan, 1, 0)),
        0  -- costo_real_tarea (lo calculamos después si es necesario)
    FROM gestionproyectos_hist.tarea t
    INNER JOIN gestionproyectos_hist.proyecto p ON t.id_proyecto = p.id_proyecto
    WHERE p.id_estado IN (4, 5);  -- Solo tareas de proyectos completados/cancelados
    
    SET v_tareas = ROW_COUNT();
    
    COMMIT;
    
    -- RETORNAR RESULTADO EXITOSO
    SELECT 
        'EXITOSO' AS estado,
        'ETL adaptado ejecutado completamente' AS mensaje,
        v_clientes AS clientes,
        v_empleados AS empleados,
        v_equipos AS equipos,
        v_proyectos AS proyectos,
        v_tareas AS tareas,
        v_tiempo AS registros_tiempo,
        NOW() AS fecha_hora;
        
END//

DELIMITER ;

-- Crear el procedimiento
SELECT 'Procedimiento ETL adaptado creado' AS resultado;
