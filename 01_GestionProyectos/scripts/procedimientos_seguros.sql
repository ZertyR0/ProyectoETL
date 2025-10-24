-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS Y TRIGGERS - SEGURIDAD
-- Sistema de Gestión de Proyectos
-- Prevención de acceso directo a datos sensibles
-- =========================================================

USE gestionproyectos_hist;

-- Eliminar procedimientos existentes si existen
DROP PROCEDURE IF EXISTS sp_generar_cliente;
DROP PROCEDURE IF EXISTS sp_generar_empleado;
DROP PROCEDURE IF EXISTS sp_generar_equipo;
DROP PROCEDURE IF EXISTS sp_generar_proyecto;
DROP PROCEDURE IF EXISTS sp_generar_tarea;
DROP PROCEDURE IF EXISTS sp_generar_miembro_equipo;
DROP PROCEDURE IF EXISTS sp_generar_tarea_equipo;
DROP PROCEDURE IF EXISTS sp_validar_integridad;
DROP PROCEDURE IF EXISTS sp_obtener_resumen;
DROP PROCEDURE IF EXISTS sp_limpiar_datos;
DROP PROCEDURE IF EXISTS sp_verificar_duplicados;

-- Eliminar triggers existentes
DROP TRIGGER IF EXISTS trg_cliente_antes_insertar;
DROP TRIGGER IF EXISTS trg_empleado_antes_insertar;
DROP TRIGGER IF EXISTS trg_proyecto_antes_insertar;
DROP TRIGGER IF EXISTS trg_tarea_antes_insertar;
DROP TRIGGER IF EXISTS trg_miembro_equipo_antes_insertar;

-- Eliminar vistas existentes
DROP VIEW IF EXISTS v_resumen_datos;
DROP VIEW IF EXISTS v_validacion_clientes;
DROP VIEW IF EXISTS v_validacion_empleados;
DROP VIEW IF EXISTS v_estadisticas_proyectos;

-- =========================================================
-- TABLAS DE AUDITORÍA Y CONTROL
-- =========================================================

-- Tabla para auditoría de operaciones
CREATE TABLE IF NOT EXISTS AuditoriaOperaciones (
    id_auditoria BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_operacion VARCHAR(50) NOT NULL,
    tabla_afectada VARCHAR(50) NOT NULL,
    usuario VARCHAR(100) DEFAULT USER(),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalles TEXT,
    ip_origen VARCHAR(45),
    exito TINYINT(1) DEFAULT 1,
    mensaje_error TEXT,
    INDEX idx_fecha (fecha_hora),
    INDEX idx_tabla (tabla_afectada),
    INDEX idx_usuario (usuario)
) ENGINE=InnoDB;

-- Tabla para control de duplicados
CREATE TABLE IF NOT EXISTS ControlDuplicados (
    id_control BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_entidad VARCHAR(50) NOT NULL,
    hash_registro VARCHAR(64) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tipo_hash (tipo_entidad, hash_registro),
    INDEX idx_tipo (tipo_entidad)
) ENGINE=InnoDB;

-- =========================================================
-- TRIGGERS DE VALIDACIÓN
-- =========================================================

DELIMITER //

-- Trigger: Validar cliente antes de insertar
CREATE TRIGGER trg_cliente_antes_insertar
BEFORE INSERT ON Cliente
FOR EACH ROW
BEGIN
    DECLARE duplicado_nombre INT;
    DECLARE duplicado_email INT;
    
    -- Validar nombre único
    SELECT COUNT(*) INTO duplicado_nombre
    FROM Cliente
    WHERE nombre = NEW.nombre;
    
    IF duplicado_nombre > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cliente con este nombre ya existe';
    END IF;
    
    -- Validar email único
    IF NEW.email IS NOT NULL AND NEW.email != '' THEN
        SELECT COUNT(*) INTO duplicado_email
        FROM Cliente
        WHERE email = NEW.email;
        
        IF duplicado_email > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: Email ya registrado';
        END IF;
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('INSERT', 'Cliente', CONCAT('Cliente: ', NEW.nombre));
END//

-- Trigger: Validar empleado antes de insertar
CREATE TRIGGER trg_empleado_antes_insertar
BEFORE INSERT ON Empleado
FOR EACH ROW
BEGIN
    DECLARE duplicado_nombre INT;
    
    -- Validar nombre único
    SELECT COUNT(*) INTO duplicado_nombre
    FROM Empleado
    WHERE nombre = NEW.nombre;
    
    IF duplicado_nombre > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Empleado con este nombre ya existe';
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('INSERT', 'Empleado', CONCAT('Empleado: ', NEW.nombre));
END//

-- Trigger: Validar proyecto antes de insertar
CREATE TRIGGER trg_proyecto_antes_insertar
BEFORE INSERT ON Proyecto
FOR EACH ROW
BEGIN
    DECLARE duplicado_nombre INT;
    
    -- Validar nombre único
    SELECT COUNT(*) INTO duplicado_nombre
    FROM Proyecto
    WHERE nombre = NEW.nombre;
    
    IF duplicado_nombre > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Proyecto con este nombre ya existe';
    END IF;
    
    -- Validar fechas coherentes
    IF NEW.fecha_fin_plan IS NOT NULL AND NEW.fecha_inicio > NEW.fecha_fin_plan THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Fecha de inicio posterior a fecha fin planificada';
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('INSERT', 'Proyecto', CONCAT('Proyecto: ', NEW.nombre));
END//

-- Trigger: Validar tarea antes de insertar
CREATE TRIGGER trg_tarea_antes_insertar
BEFORE INSERT ON Tarea
FOR EACH ROW
BEGIN
    -- Validar fechas coherentes
    IF NEW.fecha_fin_plan IS NOT NULL AND NEW.fecha_inicio_plan > NEW.fecha_fin_plan THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Fecha de inicio posterior a fecha fin en tarea';
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('INSERT', 'Tarea', CONCAT('Tarea: ', NEW.nombre_tarea, ' - Proyecto: ', NEW.id_proyecto));
END//

-- Trigger: Validar miembro equipo antes de insertar
CREATE TRIGGER trg_miembro_equipo_antes_insertar
BEFORE INSERT ON MiembroEquipo
FOR EACH ROW
BEGIN
    DECLARE duplicado INT;
    
    -- Validar que no exista la misma asignación activa
    SELECT COUNT(*) INTO duplicado
    FROM MiembroEquipo
    WHERE id_equipo = NEW.id_equipo 
      AND id_empleado = NEW.id_empleado
      AND (fecha_fin IS NULL OR fecha_fin > CURDATE());
    
    IF duplicado > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Esta asignación equipo-empleado ya existe y está activa';
    END IF;
    
    -- Registrar en auditoría
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('INSERT', 'MiembroEquipo', CONCAT('Equipo: ', NEW.id_equipo, ' - Empleado: ', NEW.id_empleado));
END//

DELIMITER ;

-- =========================================================
-- PROCEDIMIENTOS ALMACENADOS SEGUROS
-- =========================================================

DELIMITER //

-- Procedimiento: Limpiar todos los datos
CREATE PROCEDURE sp_limpiar_datos()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, exito, mensaje_error)
        VALUES ('LIMPIAR', 'TODAS', 0, 'Error al limpiar datos');
    END;
    
    START TRANSACTION;
    
    SET FOREIGN_KEY_CHECKS = 0;
    
    DELETE FROM TareaEquipoHist;
    DELETE FROM MiembroEquipo;
    DELETE FROM Tarea;
    DELETE FROM Proyecto;
    DELETE FROM Equipo;
    DELETE FROM Empleado;
    DELETE FROM Cliente;
    DELETE FROM ControlDuplicados;
    
    ALTER TABLE Cliente AUTO_INCREMENT = 1;
    ALTER TABLE Empleado AUTO_INCREMENT = 1;
    ALTER TABLE Equipo AUTO_INCREMENT = 1;
    ALTER TABLE Proyecto AUTO_INCREMENT = 1;
    ALTER TABLE Tarea AUTO_INCREMENT = 1;
    ALTER TABLE MiembroEquipo AUTO_INCREMENT = 1;
    ALTER TABLE TareaEquipoHist AUTO_INCREMENT = 1;
    
    SET FOREIGN_KEY_CHECKS = 1;
    
    INSERT INTO AuditoriaOperaciones (tipo_operacion, tabla_afectada, detalles)
    VALUES ('LIMPIAR', 'TODAS', 'Datos limpiados exitosamente');
    
    COMMIT;
    
    SELECT 'Datos limpiados exitosamente' AS resultado;
END//

-- Procedimiento: Generar cliente con validación
CREATE PROCEDURE sp_generar_cliente(
    IN p_nombre VARCHAR(100),
    IN p_sector VARCHAR(50),
    IN p_contacto VARCHAR(100),
    IN p_telefono VARCHAR(20),
    IN p_email VARCHAR(100),
    IN p_direccion VARCHAR(200)
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar cliente' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    -- Generar hash para control de duplicados
    SET hash_registro = SHA2(CONCAT('cliente:', p_nombre, ':', p_email), 256);
    
    -- Registrar en control de duplicados
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('CLIENTE', hash_registro);
    
    -- Insertar cliente (el trigger validará duplicados)
    INSERT INTO Cliente (nombre, sector, contacto, telefono, email, direccion)
    VALUES (p_nombre, p_sector, p_contacto, p_telefono, p_email, p_direccion);
    
    COMMIT;
    
    SELECT 'Cliente creado exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar empleado con validación
CREATE PROCEDURE sp_generar_empleado(
    IN p_nombre VARCHAR(100),
    IN p_puesto VARCHAR(50),
    IN p_departamento VARCHAR(50),
    IN p_salario_base DECIMAL(10,2),
    IN p_fecha_ingreso DATE
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar empleado' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    -- Generar hash
    SET hash_registro = SHA2(CONCAT('empleado:', p_nombre), 256);
    
    -- Registrar en control
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('EMPLEADO', hash_registro);
    
    -- Insertar empleado
    INSERT INTO Empleado (nombre, puesto, departamento, salario_base, fecha_ingreso)
    VALUES (p_nombre, p_puesto, p_departamento, p_salario_base, p_fecha_ingreso);
    
    COMMIT;
    
    SELECT 'Empleado creado exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar equipo
CREATE PROCEDURE sp_generar_equipo(
    IN p_nombre_equipo VARCHAR(100),
    IN p_descripcion VARCHAR(200)
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar equipo' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    SET hash_registro = SHA2(CONCAT('equipo:', p_nombre_equipo), 256);
    
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('EQUIPO', hash_registro);
    
    INSERT INTO Equipo (nombre_equipo, descripcion)
    VALUES (p_nombre_equipo, p_descripcion);
    
    COMMIT;
    
    SELECT 'Equipo creado exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar proyecto
CREATE PROCEDURE sp_generar_proyecto(
    IN p_nombre VARCHAR(150),
    IN p_descripcion TEXT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin_plan DATE,
    IN p_fecha_fin_real DATE,
    IN p_presupuesto DECIMAL(12,2),
    IN p_costo_real DECIMAL(12,2),
    IN p_id_cliente INT,
    IN p_id_estado INT,
    IN p_id_empleado_gerente INT,
    IN p_prioridad VARCHAR(20),
    IN p_progreso INT
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar proyecto' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    SET hash_registro = SHA2(CONCAT('proyecto:', p_nombre), 256);
    
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('PROYECTO', hash_registro);
    
    INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin_plan, fecha_fin_real,
                         presupuesto, costo_real, id_cliente, id_estado, id_empleado_gerente,
                         prioridad, progreso_porcentaje)
    VALUES (p_nombre, p_descripcion, p_fecha_inicio, p_fecha_fin_plan, p_fecha_fin_real,
            p_presupuesto, p_costo_real, p_id_cliente, p_id_estado, p_id_empleado_gerente,
            p_prioridad, p_progreso);
    
    COMMIT;
    
    SELECT 'Proyecto creado exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar tarea
CREATE PROCEDURE sp_generar_tarea(
    IN p_nombre_tarea VARCHAR(150),
    IN p_descripcion TEXT,
    IN p_fecha_inicio_plan DATE,
    IN p_fecha_fin_plan DATE,
    IN p_fecha_inicio_real DATE,
    IN p_fecha_fin_real DATE,
    IN p_horas_plan INT,
    IN p_horas_reales INT,
    IN p_id_proyecto INT,
    IN p_id_empleado INT,
    IN p_id_estado INT,
    IN p_prioridad VARCHAR(20),
    IN p_progreso INT,
    IN p_costo_estimado DECIMAL(10,2),
    IN p_costo_real DECIMAL(10,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar tarea' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    INSERT INTO Tarea (nombre_tarea, descripcion, fecha_inicio_plan, fecha_fin_plan,
                      fecha_inicio_real, fecha_fin_real, horas_plan, horas_reales,
                      id_proyecto, id_empleado, id_estado, prioridad, progreso_porcentaje,
                      costo_estimado, costo_real)
    VALUES (p_nombre_tarea, p_descripcion, p_fecha_inicio_plan, p_fecha_fin_plan,
            p_fecha_inicio_real, p_fecha_fin_real, p_horas_plan, p_horas_reales,
            p_id_proyecto, p_id_empleado, p_id_estado, p_prioridad, p_progreso,
            p_costo_estimado, p_costo_real);
    
    COMMIT;
    
    SELECT 'Tarea creada exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar miembro equipo
CREATE PROCEDURE sp_generar_miembro_equipo(
    IN p_id_equipo INT,
    IN p_id_empleado INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_rol_miembro VARCHAR(50),
    IN p_activo TINYINT
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar miembro equipo' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    SET hash_registro = SHA2(CONCAT('miembro:', p_id_equipo, ':', p_id_empleado), 256);
    
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('MIEMBRO_EQUIPO', hash_registro);
    
    INSERT INTO MiembroEquipo (id_equipo, id_empleado, fecha_inicio, fecha_fin, rol_miembro, activo)
    VALUES (p_id_equipo, p_id_empleado, p_fecha_inicio, p_fecha_fin, p_rol_miembro, p_activo);
    
    COMMIT;
    
    SELECT 'Miembro equipo creado exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Generar tarea equipo historial
CREATE PROCEDURE sp_generar_tarea_equipo(
    IN p_id_tarea INT,
    IN p_id_equipo INT,
    IN p_fecha_asignacion DATE,
    IN p_fecha_liberacion DATE,
    IN p_horas_asignadas INT,
    IN p_notas TEXT
)
BEGIN
    DECLARE hash_registro VARCHAR(64);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error al insertar tarea equipo' AS resultado, 0 AS id_generado;
    END;
    
    START TRANSACTION;
    
    SET hash_registro = SHA2(CONCAT('tarea_equipo:', p_id_tarea, ':', p_id_equipo, ':', p_fecha_asignacion), 256);
    
    INSERT INTO ControlDuplicados (tipo_entidad, hash_registro)
    VALUES ('TAREA_EQUIPO', hash_registro);
    
    INSERT INTO TareaEquipoHist (id_tarea, id_equipo, fecha_asignacion, fecha_liberacion, horas_asignadas, notas)
    VALUES (p_id_tarea, p_id_equipo, p_fecha_asignacion, p_fecha_liberacion, p_horas_asignadas, p_notas);
    
    COMMIT;
    
    SELECT 'Tarea equipo creada exitosamente' AS resultado, LAST_INSERT_ID() AS id_generado;
END//

-- Procedimiento: Obtener IDs disponibles (SIN DATOS SENSIBLES)
CREATE PROCEDURE sp_obtener_ids_disponibles()
BEGIN
    -- Solo retornar IDs, no datos
    SELECT 'CLIENTES' AS tipo, id_cliente AS id FROM Cliente WHERE activo = 1
    UNION ALL
    SELECT 'EMPLEADOS' AS tipo, id_empleado AS id FROM Empleado WHERE activo = 1
    UNION ALL
    SELECT 'EQUIPOS' AS tipo, id_equipo AS id FROM Equipo WHERE activo = 1
    UNION ALL
    SELECT 'PROYECTOS' AS tipo, id_proyecto AS id FROM Proyecto
    ORDER BY tipo, id;
END//

-- Procedimiento: Obtener resumen (solo conteos)
CREATE PROCEDURE sp_obtener_resumen()
BEGIN
    SELECT 'Cliente' AS tabla, COUNT(*) AS total FROM Cliente
    UNION ALL
    SELECT 'Empleado', COUNT(*) FROM Empleado
    UNION ALL
    SELECT 'Equipo', COUNT(*) FROM Equipo
    UNION ALL
    SELECT 'Proyecto', COUNT(*) FROM Proyecto
    UNION ALL
    SELECT 'Tarea', COUNT(*) FROM Tarea
    UNION ALL
    SELECT 'MiembroEquipo', COUNT(*) FROM MiembroEquipo
    UNION ALL
    SELECT 'TareaEquipoHist', COUNT(*) FROM TareaEquipoHist;
END//

-- Procedimiento: Validar integridad
CREATE PROCEDURE sp_validar_integridad()
BEGIN
    SELECT 
        'Clientes únicos' AS validacion,
        COUNT(*) AS total,
        COUNT(DISTINCT nombre) AS unicos,
        IF(COUNT(*) = COUNT(DISTINCT nombre), 'OK', 'ERROR') AS estado
    FROM Cliente
    
    UNION ALL
    
    SELECT 
        'Emails únicos',
        COUNT(*),
        COUNT(DISTINCT email),
        IF(COUNT(*) = COUNT(DISTINCT email), 'OK', 'ERROR')
    FROM Cliente WHERE email IS NOT NULL
    
    UNION ALL
    
    SELECT 
        'Empleados únicos',
        COUNT(*),
        COUNT(DISTINCT nombre),
        IF(COUNT(*) = COUNT(DISTINCT nombre), 'OK', 'ERROR')
    FROM Empleado
    
    UNION ALL
    
    SELECT 
        'Equipos únicos',
        COUNT(*),
        COUNT(DISTINCT nombre_equipo),
        IF(COUNT(*) = COUNT(DISTINCT nombre_equipo), 'OK', 'ERROR')
    FROM Equipo
    
    UNION ALL
    
    SELECT 
        'Proyectos únicos',
        COUNT(*),
        COUNT(DISTINCT nombre),
        IF(COUNT(*) = COUNT(DISTINCT nombre), 'OK', 'ERROR')
    FROM Proyecto;
END//

-- Procedimiento: Verificar duplicados
CREATE PROCEDURE sp_verificar_duplicados()
BEGIN
    -- Clientes duplicados
    SELECT 'CLIENTE' AS tipo, nombre AS valor, COUNT(*) AS cantidad
    FROM Cliente
    GROUP BY nombre
    HAVING COUNT(*) > 1
    
    UNION ALL
    
    -- Empleados duplicados
    SELECT 'EMPLEADO', nombre, COUNT(*)
    FROM Empleado
    GROUP BY nombre
    HAVING COUNT(*) > 1
    
    UNION ALL
    
    -- Emails duplicados
    SELECT 'EMAIL', email, COUNT(*)
    FROM Cliente
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING COUNT(*) > 1;
END//

-- Procedimiento: Obtener estadísticas por estado
CREATE PROCEDURE sp_estadisticas_proyectos()
BEGIN
    SELECT 
        e.nombre_estado,
        COUNT(*) AS cantidad_proyectos,
        ROUND(AVG(p.progreso_porcentaje), 2) AS progreso_promedio
    FROM Proyecto p
    JOIN Estado e ON p.id_estado = e.id_estado
    GROUP BY e.nombre_estado
    ORDER BY cantidad_proyectos DESC;
END//

DELIMITER ;

-- =========================================================
-- VISTAS SEGURAS (SOLO INFORMACIÓN NO SENSIBLE)
-- =========================================================

-- Vista: Resumen de datos (solo conteos)
CREATE VIEW v_resumen_datos AS
SELECT 
    (SELECT COUNT(*) FROM Cliente) AS total_clientes,
    (SELECT COUNT(*) FROM Empleado) AS total_empleados,
    (SELECT COUNT(*) FROM Equipo) AS total_equipos,
    (SELECT COUNT(*) FROM Proyecto) AS total_proyectos,
    (SELECT COUNT(*) FROM Tarea) AS total_tareas,
    (SELECT COUNT(*) FROM MiembroEquipo) AS total_asignaciones;

-- Vista: Validación de clientes (solo métricas)
CREATE VIEW v_validacion_clientes AS
SELECT 
    COUNT(*) AS total,
    COUNT(DISTINCT nombre) AS nombres_unicos,
    COUNT(DISTINCT email) AS emails_unicos,
    IF(COUNT(*) = COUNT(DISTINCT nombre), 'OK', 'DUPLICADOS') AS estado_nombres,
    IF(COUNT(*) = COUNT(DISTINCT email), 'OK', 'DUPLICADOS') AS estado_emails
FROM Cliente;

-- Vista: Validación de empleados (solo métricas)
CREATE VIEW v_validacion_empleados AS
SELECT 
    COUNT(*) AS total,
    COUNT(DISTINCT nombre) AS nombres_unicos,
    IF(COUNT(*) = COUNT(DISTINCT nombre), 'OK', 'DUPLICADOS') AS estado
FROM Empleado;

-- Vista: Estadísticas de proyectos (agregados, no datos individuales)
CREATE VIEW v_estadisticas_proyectos AS
SELECT 
    e.nombre_estado,
    COUNT(*) AS cantidad,
    ROUND(AVG(p.progreso_porcentaje), 2) AS progreso_promedio,
    ROUND(AVG(p.presupuesto), 2) AS presupuesto_promedio
FROM Proyecto p
JOIN Estado e ON p.id_estado = e.id_estado
GROUP BY e.nombre_estado;

-- =========================================================
-- PERMISOS Y SEGURIDAD
-- =========================================================

-- Comentar/Descomentar según necesidad de crear usuario específico
/*
-- Crear usuario con permisos limitados
DROP USER IF EXISTS 'etl_user'@'localhost';
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'password_seguro_aqui';

-- Revocar todos los permisos
REVOKE ALL PRIVILEGES ON gestionproyectos_hist.* FROM 'etl_user'@'localhost';

-- Otorgar solo EXECUTE en procedimientos
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_limpiar_datos TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_cliente TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_empleado TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_equipo TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_proyecto TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_tarea TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_miembro_equipo TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_generar_tarea_equipo TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_obtener_ids_disponibles TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_obtener_resumen TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_validar_integridad TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_verificar_duplicados TO 'etl_user'@'localhost';
GRANT EXECUTE ON PROCEDURE gestionproyectos_hist.sp_estadisticas_proyectos TO 'etl_user'@'localhost';

-- Otorgar SELECT solo en vistas
GRANT SELECT ON gestionproyectos_hist.v_resumen_datos TO 'etl_user'@'localhost';
GRANT SELECT ON gestionproyectos_hist.v_validacion_clientes TO 'etl_user'@'localhost';
GRANT SELECT ON gestionproyectos_hist.v_validacion_empleados TO 'etl_user'@'localhost';
GRANT SELECT ON gestionproyectos_hist.v_estadisticas_proyectos TO 'etl_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;
*/

-- =========================================================
-- VERIFICACIÓN FINAL
-- =========================================================

SELECT 'Procedimientos almacenados y triggers creados exitosamente' AS resultado;

-- Listar procedimientos creados
SELECT ROUTINE_NAME, ROUTINE_TYPE 
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'gestionproyectos_hist' 
  AND ROUTINE_TYPE = 'PROCEDURE'
ORDER BY ROUTINE_NAME;

-- Listar triggers creados
SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = 'gestionproyectos_hist'
ORDER BY TRIGGER_NAME;

-- Listar vistas creadas
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.VIEWS
WHERE TABLE_SCHEMA = 'gestionproyectos_hist'
ORDER BY TABLE_NAME;
