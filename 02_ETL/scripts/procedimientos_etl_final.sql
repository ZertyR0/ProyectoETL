-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS ETL - OPCIÓN 3: SEGURIDAD TOTAL
-- Python solo ejecuta: CALL sp_ejecutar_etl_completo()
-- CERO nombres de tablas/columnas en código Python
-- =========================================================

USE dw_proyectos_hist;

DELIMITER //

-- =====================================================
-- PROCEDIMIENTO MAESTRO - TODO EL ETL EN 1 LLAMADA
-- =====================================================

DROP PROCEDURE IF EXISTS sp_ejecutar_etl_completo//

CREATE PROCEDURE sp_ejecutar_etl_completo()
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
            'Fallo en proceso ETL' AS mensaje,
            NOW() AS fecha_hora;
    END;
    
    START TRANSACTION;
    
    -- ===================================================
    -- PASO 1: LIMPIAR DATAWAREHOUSE
    -- ===================================================
    
    SET FOREIGN_KEY_CHECKS = 0;
    
    DELETE FROM HechoTarea;
    DELETE FROM HechoProyecto;
    DELETE FROM DimTiempo;
    DELETE FROM DimProyecto;
    DELETE FROM DimEquipo;
    DELETE FROM DimEmpleado;
    DELETE FROM DimCliente;
    
    ALTER TABLE HechoTarea AUTO_INCREMENT = 1;
    ALTER TABLE HechoProyecto AUTO_INCREMENT = 1;
    
    SET FOREIGN_KEY_CHECKS = 1;
    
    -- ===================================================
    -- PASO 2: GENERAR DIMENSIÓN TIEMPO (4 años)
    -- ===================================================
    
    SET @fecha = DATE_SUB(CURDATE(), INTERVAL 3 YEAR);
    SET @fecha_max = DATE_ADD(CURDATE(), INTERVAL 1 YEAR);
    
    WHILE @fecha <= @fecha_max DO
        SET @id_tiempo = YEAR(@fecha) * 10000 + MONTH(@fecha) * 100 + DAY(@fecha);
        
        INSERT INTO DimTiempo (
            id_tiempo, fecha, anio, trimestre, mes, numero_semana,
            dia, dia_semana, nombre_mes, nombre_dia_semana
        )
        VALUES (
            @id_tiempo,
            @fecha,
            YEAR(@fecha),
            QUARTER(@fecha),
            MONTH(@fecha),
            WEEK(@fecha),
            DAY(@fecha),
            DAYOFWEEK(@fecha),
            DATE_FORMAT(@fecha, '%M'),
            DATE_FORMAT(@fecha, '%W')
        )
        ON DUPLICATE KEY UPDATE fecha = @fecha;
        
        SET @fecha = DATE_ADD(@fecha, INTERVAL 1 DAY);
        SET v_tiempo = v_tiempo + 1;
    END WHILE;
    
    -- ===================================================
    -- PASO 3: CARGAR DIMENSIONES DESDE BD ORIGEN
    -- ===================================================
    
    -- DimCliente
    INSERT INTO DimCliente (
        id_cliente, nombre, sector, contacto,
        telefono, email, direccion, fecha_registro, activo
    )
    SELECT 
        id_cliente, nombre, sector, contacto,
        telefono, email, direccion, fecha_registro, activo
    FROM gestionproyectos_hist.Cliente
    WHERE activo = 1;
    
    SET v_clientes = ROW_COUNT();
    
    -- DimEmpleado
    INSERT INTO DimEmpleado (
        id_empleado, nombre, puesto, departamento,
        salario_base, fecha_ingreso, activo
    )
    SELECT 
        id_empleado, nombre, puesto, departamento,
        salario_base, fecha_ingreso, activo
    FROM gestionproyectos_hist.Empleado
    WHERE activo = 1;
    
    SET v_empleados = ROW_COUNT();
    
    -- DimEquipo
    INSERT INTO DimEquipo (
        id_equipo, nombre_equipo, descripcion,
        fecha_creacion, activo
    )
    SELECT 
        id_equipo, nombre_equipo, descripcion,
        fecha_creacion, activo
    FROM gestionproyectos_hist.Equipo
    WHERE activo = 1;
    
    SET v_equipos = ROW_COUNT();
    
    -- DimProyecto (solo completados y cancelados)
    INSERT INTO DimProyecto (
        id_proyecto, nombre_proyecto, descripcion,
        fecha_inicio_plan, fecha_fin_plan, presupuesto_plan, prioridad
    )
    SELECT 
        id_proyecto, nombre, descripcion,
        fecha_inicio, fecha_fin_plan, presupuesto, prioridad
    FROM gestionproyectos_hist.Proyecto
    WHERE id_estado IN (3, 4);
    
    SET v_proyectos = ROW_COUNT();
    
    -- ===================================================
    -- PASO 4: CARGAR HECHOS CON MÉTRICAS CALCULADAS
    -- ===================================================
    
    -- HechoProyecto con todas las métricas
    INSERT INTO HechoProyecto (
        id_proyecto, id_cliente, id_empleado_gerente,
        id_tiempo_inicio, id_tiempo_fin_plan, id_tiempo_fin_real,
        duracion_planificada, duracion_real, variacion_cronograma,
        cumplimiento_tiempo, presupuesto, costo_real,
        variacion_costos, cumplimiento_presupuesto,
        porcentaje_sobrecosto, tareas_total, tareas_completadas,
        tareas_canceladas, tareas_pendientes, porcentaje_completado,
        horas_estimadas_total, horas_reales_total, variacion_horas,
        eficiencia_horas
    )
    SELECT 
        p.id_proyecto,
        p.id_cliente,
        p.id_empleado_gerente,
        -- Convertir fechas a IDs de tiempo
        YEAR(p.fecha_inicio)*10000 + MONTH(p.fecha_inicio)*100 + DAY(p.fecha_inicio),
        YEAR(p.fecha_fin_plan)*10000 + MONTH(p.fecha_fin_plan)*100 + DAY(p.fecha_fin_plan),
        IF(p.fecha_fin_real IS NULL, NULL, 
           YEAR(p.fecha_fin_real)*10000 + MONTH(p.fecha_fin_real)*100 + DAY(p.fecha_fin_real)),
        -- Métricas de tiempo
        DATEDIFF(p.fecha_fin_plan, p.fecha_inicio),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio), 0),
        IFNULL(DATEDIFF(p.fecha_fin_real, p.fecha_inicio) - DATEDIFF(p.fecha_fin_plan, p.fecha_inicio), 0),
        IF(p.fecha_fin_real IS NULL, 0, IF(p.fecha_fin_real <= p.fecha_fin_plan, 1, 0)),
        -- Métricas financieras
        p.presupuesto,
        IFNULL(p.costo_real, 0),
        IFNULL(p.costo_real, 0) - p.presupuesto,
        IF(IFNULL(p.costo_real, 0) <= p.presupuesto, 1, 0),
        IF(p.presupuesto > 0, 
           ((IFNULL(p.costo_real, 0) - p.presupuesto) / p.presupuesto * 100), 
           0),
        -- Métricas de tareas (subquery)
        IFNULL(t.total, 0),
        IFNULL(t.completadas, 0),
        IFNULL(t.canceladas, 0),
        IFNULL(t.pendientes, 0),
        IF(IFNULL(t.total, 0) > 0, (IFNULL(t.completadas, 0) / t.total * 100), 0),
        -- Métricas de horas
        IFNULL(t.horas_plan_total, 0),
        IFNULL(t.horas_reales_total, 0),
        IFNULL(t.horas_reales_total, 0) - IFNULL(t.horas_plan_total, 0),
        IF(IFNULL(t.horas_reales_total, 0) > 0, 
           (IFNULL(t.horas_plan_total, 0) / t.horas_reales_total * 100), 
           0)
    FROM gestionproyectos_hist.Proyecto p
    LEFT JOIN (
        SELECT 
            id_proyecto,
            COUNT(*) AS total,
            SUM(IF(id_estado = 3, 1, 0)) AS completadas,
            SUM(IF(id_estado = 4, 1, 0)) AS canceladas,
            SUM(IF(id_estado NOT IN (3, 4), 1, 0)) AS pendientes,
            SUM(horas_plan) AS horas_plan_total,
            SUM(horas_reales) AS horas_reales_total
        FROM gestionproyectos_hist.Tarea
        GROUP BY id_proyecto
    ) t ON p.id_proyecto = t.id_proyecto
    WHERE p.id_estado IN (3, 4);
    
    -- HechoTarea con métricas
    INSERT INTO HechoTarea (
        id_tarea, id_proyecto, id_empleado,
        id_tiempo_inicio_plan, id_tiempo_fin_plan,
        id_tiempo_inicio_real, id_tiempo_fin_real,
        duracion_planificada, duracion_real, variacion_cronograma,
        cumplimiento_tiempo, horas_plan, horas_reales,
        variacion_horas, eficiencia_horas,
        costo_estimado, costo_real, variacion_costo,
        progreso_porcentaje
    )
    SELECT 
        t.id_tarea,
        t.id_proyecto,
        t.id_empleado,
        -- IDs de tiempo
        IF(t.fecha_inicio_plan IS NULL, NULL, 
           YEAR(t.fecha_inicio_plan)*10000 + MONTH(t.fecha_inicio_plan)*100 + DAY(t.fecha_inicio_plan)),
        IF(t.fecha_fin_plan IS NULL, NULL, 
           YEAR(t.fecha_fin_plan)*10000 + MONTH(t.fecha_fin_plan)*100 + DAY(t.fecha_fin_plan)),
        IF(t.fecha_inicio_real IS NULL, NULL, 
           YEAR(t.fecha_inicio_real)*10000 + MONTH(t.fecha_inicio_real)*100 + DAY(t.fecha_inicio_real)),
        IF(t.fecha_fin_real IS NULL, NULL, 
           YEAR(t.fecha_fin_real)*10000 + MONTH(t.fecha_fin_real)*100 + DAY(t.fecha_fin_real)),
        -- Métricas de tiempo
        IFNULL(DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan), 0),
        IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real), 0),
        IFNULL(DATEDIFF(t.fecha_fin_real, t.fecha_inicio_real) - 
               DATEDIFF(t.fecha_fin_plan, t.fecha_inicio_plan), 0),
        IF(t.fecha_fin_real IS NULL, 0, IF(t.fecha_fin_real <= t.fecha_fin_plan, 1, 0)),
        -- Métricas de horas
        IFNULL(t.horas_plan, 0),
        IFNULL(t.horas_reales, 0),
        IFNULL(t.horas_reales, 0) - IFNULL(t.horas_plan, 0),
        IF(IFNULL(t.horas_reales, 0) > 0, 
           (IFNULL(t.horas_plan, 0) / t.horas_reales * 100), 
           0),
        -- Métricas financieras
        IFNULL(t.costo_estimado, 0),
        IFNULL(t.costo_real, 0),
        IFNULL(t.costo_real, 0) - IFNULL(t.costo_estimado, 0),
        IFNULL(t.progreso_porcentaje, 0)
    FROM gestionproyectos_hist.Tarea t
    INNER JOIN gestionproyectos_hist.Proyecto p ON t.id_proyecto = p.id_proyecto
    WHERE p.id_estado IN (3, 4);
    
    SET v_tareas = ROW_COUNT();
    
    COMMIT;
    
    -- ===================================================
    -- RETORNAR RESULTADO EXITOSO
    -- ===================================================
    
    SELECT 
        'EXITOSO' AS estado,
        'ETL ejecutado completamente' AS mensaje,
        v_clientes AS clientes,
        v_empleados AS empleados,
        v_equipos AS equipos,
        v_proyectos AS proyectos,
        v_tareas AS tareas,
        v_tiempo AS registros_tiempo,
        NOW() AS fecha_hora;
        
END//

DELIMITER ;

-- =====================================================
-- VERIFICACIÓN
-- =====================================================

SHOW PROCEDURE STATUS WHERE Db = 'dw_proyectos_hist' AND Name = 'sp_ejecutar_etl_completo';

SELECT '✅ Procedimiento maestro ETL creado' AS resultado;
SELECT '💡 Python solo necesita: CALL sp_ejecutar_etl_completo()' AS instruccion;
