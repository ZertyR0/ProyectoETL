-- Procedimientos ETL completo migrados a src/dw/sql/procedimientos_etl_completo.sql
-- Fuente original: 02_ETL/scripts/procedimientos_etl_completo.sql

USE gestionproyectos_hist;

DELIMITER //
DROP PROCEDURE IF EXISTS sp_etl_extraer_clientes//
CREATE PROCEDURE sp_etl_extraer_clientes()
BEGIN
    SELECT id_cliente,nombre,sector,contacto,telefono,email,direccion,fecha_registro,activo
    FROM Cliente WHERE activo=1 ORDER BY id_cliente;
END//

DROP PROCEDURE IF EXISTS sp_etl_extraer_empleados//
CREATE PROCEDURE sp_etl_extraer_empleados()
BEGIN
    SELECT id_empleado,nombre,puesto,departamento,salario_base,fecha_ingreso,activo
    FROM Empleado WHERE activo=1 ORDER BY id_empleado;
END//

DROP PROCEDURE IF EXISTS sp_etl_extraer_equipos//
CREATE PROCEDURE sp_etl_extraer_equipos()
BEGIN
    SELECT id_equipo,nombre_equipo,descripcion,fecha_creacion,activo
    FROM Equipo WHERE activo=1 ORDER BY id_equipo;
END//

DROP PROCEDURE IF EXISTS sp_etl_extraer_proyectos//
CREATE PROCEDURE sp_etl_extraer_proyectos()
BEGIN
    SELECT p.id_proyecto,p.nombre,p.descripcion,p.fecha_inicio,p.fecha_fin_plan,p.fecha_fin_real,
           p.presupuesto,p.costo_real,p.id_cliente,p.id_estado,p.id_empleado_gerente,p.prioridad,
           p.progreso_porcentaje,c.nombre AS nombre_cliente,e.nombre AS nombre_gerente,est.nombre_estado
    FROM Proyecto p
    LEFT JOIN Cliente c ON p.id_cliente=c.id_cliente
    LEFT JOIN Empleado e ON p.id_empleado_gerente=e.id_empleado
    LEFT JOIN Estado est ON p.id_estado=est.id_estado
    WHERE p.id_estado IN (3,4) ORDER BY p.id_proyecto;
END//

DROP PROCEDURE IF EXISTS sp_etl_extraer_tareas//
CREATE PROCEDURE sp_etl_extraer_tareas()
BEGIN
    SELECT t.id_tarea,t.nombre_tarea,t.descripcion,t.fecha_inicio_plan,t.fecha_fin_plan,t.fecha_inicio_real,
           t.fecha_fin_real,t.horas_plan,t.horas_reales,t.costo_estimado,t.costo_real,t.progreso_porcentaje,
           t.id_proyecto,t.id_empleado,t.id_estado,p.nombre AS nombre_proyecto,e.nombre AS nombre_empleado,
           est.nombre_estado
    FROM Tarea t
    LEFT JOIN Proyecto p ON t.id_proyecto=p.id_proyecto
    LEFT JOIN Empleado e ON t.id_empleado=e.id_empleado
    LEFT JOIN Estado est ON t.id_estado=est.id_estado
    WHERE p.id_estado IN (3,4) ORDER BY t.id_tarea;
END//

CREATE TABLE IF NOT EXISTS AuditoriaETL (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operacion VARCHAR(50),
    tabla VARCHAR(50),
    registros_procesados INT DEFAULT 0,
    estado VARCHAR(20),
    mensaje TEXT,
    usuario_etl VARCHAR(100),
    INDEX idx_fecha (fecha_hora),
    INDEX idx_operacion (operacion),
    INDEX idx_estado (estado)
) ENGINE=InnoDB//

DROP PROCEDURE IF EXISTS sp_etl_registrar_inicio//
CREATE PROCEDURE sp_etl_registrar_inicio(IN p_operacion VARCHAR(50),IN p_tabla VARCHAR(50))
BEGIN
    INSERT INTO AuditoriaETL (operacion,tabla,estado,usuario_etl)
    VALUES (p_operacion,p_tabla,'INICIADO',USER());
    SELECT LAST_INSERT_ID() AS id_auditoria;
END//

DROP PROCEDURE IF EXISTS sp_etl_registrar_fin//
CREATE PROCEDURE sp_etl_registrar_fin(IN p_id_auditoria INT,IN p_registros INT,IN p_estado VARCHAR(20),IN p_mensaje TEXT)
BEGIN
    UPDATE AuditoriaETL SET registros_procesados=p_registros,estado=p_estado,mensaje=p_mensaje
    WHERE id_auditoria=p_id_auditoria;
END//
DELIMITER ;

USE dw_proyectos_hist;
DELIMITER //
DROP PROCEDURE IF EXISTS sp_dw_limpiar//
CREATE PROCEDURE sp_dw_limpiar()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; SELECT 'ERROR' AS resultado,'Error al limpiar DataWarehouse' AS mensaje; END;
    START TRANSACTION; SET FOREIGN_KEY_CHECKS=0;
    DELETE FROM HechoTarea; DELETE FROM HechoProyecto; DELETE FROM DimTiempo; DELETE FROM DimProyecto; DELETE FROM DimEquipo; DELETE FROM DimEmpleado; DELETE FROM DimCliente;
    ALTER TABLE HechoTarea AUTO_INCREMENT=1; ALTER TABLE HechoProyecto AUTO_INCREMENT=1;
    SET FOREIGN_KEY_CHECKS=1; COMMIT;
    SELECT 'EXITOSO' AS resultado,'DataWarehouse limpiado correctamente' AS mensaje,NOW() AS fecha_hora;
END//

DROP PROCEDURE IF EXISTS sp_dw_cargar_dim_tiempo//
CREATE PROCEDURE sp_dw_cargar_dim_tiempo(IN p_fecha_min DATE,IN p_fecha_max DATE)
BEGIN
    DECLARE v_fecha DATE; DECLARE v_id_tiempo INT; DECLARE v_contador INT DEFAULT 0;
    SET v_fecha=p_fecha_min; SET v_id_tiempo=YEAR(v_fecha)*10000+MONTH(v_fecha)*100+DAY(v_fecha);
    WHILE v_fecha <= p_fecha_max DO
        INSERT INTO DimTiempo (id_tiempo,fecha,anio,trimestre,mes,semana,dia,dia_semana,nombre_mes,nombre_dia_semana)
        VALUES (v_id_tiempo,v_fecha,YEAR(v_fecha),QUARTER(v_fecha),MONTH(v_fecha),WEEK(v_fecha),DAY(v_fecha),DAYOFWEEK(v_fecha),DATE_FORMAT(v_fecha,'%M'),DATE_FORMAT(v_fecha,'%W'))
        ON DUPLICATE KEY UPDATE fecha=v_fecha;
        SET v_contador=v_contador+1; SET v_fecha=DATE_ADD(v_fecha,INTERVAL 1 DAY);
        SET v_id_tiempo=YEAR(v_fecha)*10000+MONTH(v_fecha)*100+DAY(v_fecha);
    END WHILE;
    SELECT 'EXITOSO' AS resultado,v_contador AS registros_insertados;
END//

DROP PROCEDURE IF EXISTS sp_etl_proceso_completo//
CREATE PROCEDURE sp_etl_proceso_completo()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; SELECT 'ERROR' AS resultado,'Error en proceso ETL completo' AS mensaje; END;
    START TRANSACTION;
    CALL sp_dw_limpiar();
    CALL sp_dw_cargar_dim_tiempo(DATE_SUB(CURDATE(),INTERVAL 3 YEAR),DATE_ADD(CURDATE(),INTERVAL 1 YEAR));
    INSERT INTO dw_proyectos_hist.DimCliente (id_cliente,nombre,sector,contacto,telefono,email,direccion,fecha_registro,activo)
    SELECT id_cliente,nombre,sector,contacto,telefono,email,direccion,fecha_registro,activo FROM gestionproyectos_hist.Cliente WHERE activo=1;
    INSERT INTO dw_proyectos_hist.DimEmpleado (id_empleado,nombre,puesto,departamento,salario_base,fecha_ingreso,activo)
    SELECT id_empleado,nombre,puesto,departamento,salario_base,fecha_ingreso,activo FROM gestionproyectos_hist.Empleado WHERE activo=1;
    INSERT INTO dw_proyectos_hist.DimEquipo (id_equipo,nombre_equipo,descripcion,fecha_creacion,activo)
    SELECT id_equipo,nombre_equipo,descripcion,fecha_creacion,activo FROM gestionproyectos_hist.Equipo WHERE activo=1;
    INSERT INTO dw_proyectos_hist.DimProyecto (id_proyecto,nombre_proyecto,descripcion,fecha_inicio,fecha_fin_plan,presupuesto_plan,prioridad)
    SELECT id_proyecto,nombre,descripcion,fecha_inicio,fecha_fin_plan,presupuesto,prioridad FROM gestionproyectos_hist.Proyecto WHERE id_estado IN (3,4);
    INSERT INTO dw_proyectos_hist.HechoProyecto (
        id_proyecto,id_cliente,id_empleado_gerente,id_tiempo_inicio,id_tiempo_fin_plan,id_tiempo_fin_real,duracion_planificada,duracion_real,variacion_cronograma,cumplimiento_tiempo,presupuesto,costo_real,variacion_costos,cumplimiento_presupuesto,porcentaje_sobrecosto,tareas_total,tareas_completadas,tareas_canceladas,tareas_pendientes,porcentaje_completado,horas_estimadas_total,horas_reales_total,variacion_horas,eficiencia_horas)
    SELECT p.id_proyecto,p.id_cliente,p.id_empleado_gerente,
        YEAR(p.fecha_inicio)*10000+MONTH(p.fecha_inicio)*100+DAY(p.fecha_inicio),
        YEAR(p.fecha_fin_plan)*10000+MONTH(p.fecha_fin_plan)*100+DAY(p.fecha_fin_plan),
        IF(p.fecha_fin_real IS NULL,NULL,YEAR(p.fecha_fin_real)*10000+MONTH(p.fecha_fin_real)*100+DAY(p.fecha_fin_real)),
        DATEDIFF(p.fecha_fin_plan,p.fecha_inicio),IFNULL(DATEDIFF(p.fecha_fin_real,p.fecha_inicio),0),IFNULL(DATEDIFF(p.fecha_fin_real,p.fecha_inicio)-DATEDIFF(p.fecha_fin_plan,p.fecha_inicio),0),
        IF(p.fecha_fin_real IS NULL,0,IF(p.fecha_fin_real <= p.fecha_fin_plan,1,0)),
        p.presupuesto,IFNULL(p.costo_real,0),IFNULL(p.costo_real,0)-p.presupuesto,IF(IFNULL(p.costo_real,0) <= p.presupuesto,1,0),
        IF(p.presupuesto>0,((IFNULL(p.costo_real,0)-p.presupuesto)/p.presupuesto*100),0),
        IFNULL(t.total,0),IFNULL(t.completadas,0),IFNULL(t.canceladas,0),IFNULL(t.pendientes,0),
        IF(IFNULL(t.total,0)>0,(IFNULL(t.completadas,0)/t.total*100),0),
        IFNULL(t.horas_plan_total,0),IFNULL(t.horas_reales_total,0),IFNULL(t.horas_reales_total,0)-IFNULL(t.horas_plan_total,0),
        IF(IFNULL(t.horas_reales_total,0)>0,(IFNULL(t.horas_plan_total,0)/t.horas_reales_total*100),0)
    FROM gestionproyectos_hist.Proyecto p
    LEFT JOIN (
        SELECT id_proyecto,COUNT(*) AS total,
               SUM(CASE WHEN id_estado=3 THEN 1 ELSE 0 END) AS completadas,
               SUM(CASE WHEN id_estado=4 THEN 1 ELSE 0 END) AS canceladas,
               SUM(CASE WHEN id_estado NOT IN (3,4) THEN 1 ELSE 0 END) AS pendientes,
               SUM(horas_plan) AS horas_plan_total,
               SUM(horas_reales) AS horas_reales_total
        FROM gestionproyectos_hist.Tarea GROUP BY id_proyecto
    ) t ON p.id_proyecto=t.id_proyecto
    WHERE p.id_estado IN (3,4);
    INSERT INTO dw_proyectos_hist.HechoTarea (
        id_tarea,id_proyecto,id_empleado,id_tiempo_inicio_plan,id_tiempo_fin_plan,id_tiempo_inicio_real,id_tiempo_fin_real,duracion_planificada,duracion_real,variacion_cronograma,cumplimiento_tiempo,horas_plan,horas_reales,variacion_horas,eficiencia_horas,costo_estimado,costo_real_tarea,variacion_costo,progreso_porcentaje)
    SELECT t.id_tarea,t.id_proyecto,t.id_empleado,
        IFNULL(YEAR(t.fecha_inicio_plan)*10000+MONTH(t.fecha_inicio_plan)*100+DAY(t.fecha_inicio_plan),NULL),
        IFNULL(YEAR(t.fecha_fin_plan)*10000+MONTH(t.fecha_fin_plan)*100+DAY(t.fecha_fin_plan),NULL),
        IFNULL(YEAR(t.fecha_inicio_real)*10000+MONTH(t.fecha_inicio_real)*100+DAY(t.fecha_inicio_real),NULL),
        IFNULL(YEAR(t.fecha_fin_real)*10000+MONTH(t.fecha_fin_real)*100+DAY(t.fecha_fin_real),NULL),
        IFNULL(DATEDIFF(t.fecha_fin_plan,t.fecha_inicio_plan),0),
        IFNULL(DATEDIFF(t.fecha_fin_real,t.fecha_inicio_real),0),
        IFNULL(DATEDIFF(t.fecha_fin_real,t.fecha_inicio_real)-DATEDIFF(t.fecha_fin_plan,t.fecha_inicio_plan),0),
        IF(t.fecha_fin_real IS NULL,0,IF(t.fecha_fin_real <= t.fecha_fin_plan,1,0)),
        IFNULL(t.horas_plan,0),IFNULL(t.horas_reales,0),IFNULL(t.horas_reales,0)-IFNULL(t.horas_plan,0),
        IF(IFNULL(t.horas_reales,0)>0,(IFNULL(t.horas_plan,0)/t.horas_reales*100),0),
        IFNULL(t.costo_estimado,0),IFNULL(t.costo_real,0),IFNULL(t.costo_real,0)-IFNULL(t.costo_estimado,0),IFNULL(t.progreso_porcentaje,0)
    FROM gestionproyectos_hist.Tarea t
    INNER JOIN gestionproyectos_hist.Proyecto p ON t.id_proyecto=p.id_proyecto
    WHERE p.id_estado IN (3,4);
    COMMIT;
    SELECT 'EXITOSO' AS resultado,'Proceso ETL completado exitosamente' AS mensaje,NOW() AS fecha_hora;
END//
DELIMITER ;

SELECT 'Procedimientos ETL COMPLETO migrados' AS resultado;