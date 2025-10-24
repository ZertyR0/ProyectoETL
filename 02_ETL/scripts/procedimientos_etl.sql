-- ===========================================================================
-- PROCEDIMIENTOS ALMACENADOS PARA ETL SEGURO
-- ===========================================================================
-- Objetivo: Proporcionar una capa segura para extracción y carga de datos
-- Sin acceso directo a tablas mediante SELECT/INSERT
-- ===========================================================================

USE gestionproyectos_hist;

DELIMITER //

-- ===========================================================================
-- PROCEDIMIENTOS DE EXTRACCIÓN (ORIGEN)
-- ===========================================================================

-- Procedimiento: Extraer datos de clientes para ETL
DROP PROCEDURE IF EXISTS sp_etl_extraer_clientes//
CREATE PROCEDURE sp_etl_extraer_clientes()
BEGIN
    -- Solo datos necesarios, sin campos sensibles
    SELECT 
        ClienteID,
        NombreCompleto,
        Industria,
        PaisOrigen,
        FechaRegistro,
        hash_unico
    FROM Cliente
    ORDER BY ClienteID;
END//

-- Procedimiento: Extraer datos de empleados para ETL
DROP PROCEDURE IF EXISTS sp_etl_extraer_empleados//
CREATE PROCEDURE sp_etl_extraer_empleados()
BEGIN
    SELECT 
        EmpleadoID,
        NombreCompleto,
        Especialidad,
        NivelExperiencia,
        Disponibilidad,
        FechaContratacion,
        hash_unico
    FROM Empleado
    ORDER BY EmpleadoID;
END//

-- Procedimiento: Extraer datos de equipos para ETL
DROP PROCEDURE IF EXISTS sp_etl_extraer_equipos//
CREATE PROCEDURE sp_etl_extraer_equipos()
BEGIN
    SELECT 
        EquipoID,
        NombreEquipo,
        LiderID,
        TipoProyecto,
        Ubicacion,
        FechaFormacion,
        hash_unico
    FROM Equipo
    ORDER BY EquipoID;
END//

-- Procedimiento: Extraer datos de proyectos COMPLETADOS para ETL
DROP PROCEDURE IF EXISTS sp_etl_extraer_proyectos//
CREATE PROCEDURE sp_etl_extraer_proyectos()
BEGIN
    SELECT 
        ProyectoID,
        NombreProyecto,
        ClienteID,
        EquipoID,
        FechaInicio,
        FechaFinReal,
        PresupuestoAsignado,
        CostoTotal,
        Estado,
        Complejidad,
        hash_unico
    FROM Proyecto
    WHERE Estado = 'Completado'  -- Solo proyectos completados
    ORDER BY ProyectoID;
END//

-- Procedimiento: Extraer relaciones de proyectos con empleados
DROP PROCEDURE IF EXISTS sp_etl_extraer_proyecto_empleados//
CREATE PROCEDURE sp_etl_extraer_proyecto_empleados()
BEGIN
    SELECT DISTINCT
        p.ProyectoID,
        t.EmpleadoID
    FROM Proyecto p
    INNER JOIN Tarea t ON p.ProyectoID = t.ProyectoID
    WHERE p.Estado = 'Completado'
    ORDER BY p.ProyectoID, t.EmpleadoID;
END//

-- ===========================================================================
-- FUNCIONES DE AUDITORÍA ETL
-- ===========================================================================

-- Tabla de auditoría para ETL
DROP TABLE IF EXISTS AuditoriaETL//
CREATE TABLE AuditoriaETL (
    AuditoriaID INT AUTO_INCREMENT PRIMARY KEY,
    FechaHora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Operacion VARCHAR(50),
    Tabla VARCHAR(50),
    RegistrosProcesados INT,
    Estado VARCHAR(20),
    Mensaje TEXT,
    UsuarioETL VARCHAR(100),
    INDEX idx_fecha (FechaHora),
    INDEX idx_operacion (Operacion)
)//

-- Procedimiento: Registrar inicio de ETL
DROP PROCEDURE IF EXISTS sp_etl_registrar_inicio//
CREATE PROCEDURE sp_etl_registrar_inicio(
    IN p_operacion VARCHAR(50),
    IN p_tabla VARCHAR(50)
)
BEGIN
    INSERT INTO AuditoriaETL (Operacion, Tabla, Estado, UsuarioETL)
    VALUES (p_operacion, p_tabla, 'INICIADO', USER());
    
    SELECT LAST_INSERT_ID() AS auditoria_id;
END//

-- Procedimiento: Registrar fin de ETL
DROP PROCEDURE IF EXISTS sp_etl_registrar_fin//
CREATE PROCEDURE sp_etl_registrar_fin(
    IN p_auditoria_id INT,
    IN p_registros INT,
    IN p_estado VARCHAR(20),
    IN p_mensaje TEXT
)
BEGIN
    UPDATE AuditoriaETL
    SET RegistrosProcesados = p_registros,
        Estado = p_estado,
        Mensaje = p_mensaje
    WHERE AuditoriaID = p_auditoria_id;
END//

-- Procedimiento: Obtener estadísticas ETL
DROP PROCEDURE IF EXISTS sp_etl_obtener_estadisticas//
CREATE PROCEDURE sp_etl_obtener_estadisticas()
BEGIN
    SELECT 
        DATE(FechaHora) AS Fecha,
        Operacion,
        Tabla,
        COUNT(*) AS Ejecuciones,
        SUM(RegistrosProcesados) AS TotalRegistros,
        SUM(CASE WHEN Estado = 'EXITOSO' THEN 1 ELSE 0 END) AS Exitosos,
        SUM(CASE WHEN Estado = 'ERROR' THEN 1 ELSE 0 END) AS Errores
    FROM AuditoriaETL
    GROUP BY DATE(FechaHora), Operacion, Tabla
    ORDER BY Fecha DESC, Operacion, Tabla;
END//

DELIMITER ;

-- ===========================================================================
-- PROCEDIMIENTOS ALMACENADOS PARA DATAWAREHOUSE (CARGA)
-- ===========================================================================

USE dw_proyectos_hist;

DELIMITER //

-- ===========================================================================
-- PROCEDIMIENTOS DE CARGA
-- ===========================================================================

-- Procedimiento: Cargar dimension Cliente
DROP PROCEDURE IF EXISTS sp_dw_cargar_cliente//
CREATE PROCEDURE sp_dw_cargar_cliente(
    IN p_cliente_id INT,
    IN p_nombre VARCHAR(100),
    IN p_industria VARCHAR(50),
    IN p_pais VARCHAR(50),
    IN p_hash VARCHAR(64)
)
BEGIN
    DECLARE v_existe INT;
    
    -- Verificar si ya existe
    SELECT COUNT(*) INTO v_existe
    FROM DimCliente
    WHERE ClienteID = p_cliente_id;
    
    IF v_existe = 0 THEN
        INSERT INTO DimCliente (
            ClienteID, NombreCompleto, Industria, 
            PaisOrigen, hash_trazabilidad
        )
        VALUES (
            p_cliente_id, p_nombre, p_industria,
            p_pais, p_hash
        );
        SELECT 'INSERTADO' AS resultado;
    ELSE
        -- Actualizar si hay cambios
        UPDATE DimCliente
        SET NombreCompleto = p_nombre,
            Industria = p_industria,
            PaisOrigen = p_pais,
            hash_trazabilidad = p_hash
        WHERE ClienteID = p_cliente_id
        AND hash_trazabilidad != p_hash;
        
        SELECT 'ACTUALIZADO' AS resultado;
    END IF;
END//

-- Procedimiento: Cargar dimension Empleado
DROP PROCEDURE IF EXISTS sp_dw_cargar_empleado//
CREATE PROCEDURE sp_dw_cargar_empleado(
    IN p_empleado_id INT,
    IN p_nombre VARCHAR(100),
    IN p_especialidad VARCHAR(50),
    IN p_nivel VARCHAR(20),
    IN p_hash VARCHAR(64)
)
BEGIN
    DECLARE v_existe INT;
    
    SELECT COUNT(*) INTO v_existe
    FROM DimEmpleado
    WHERE EmpleadoID = p_empleado_id;
    
    IF v_existe = 0 THEN
        INSERT INTO DimEmpleado (
            EmpleadoID, NombreCompleto, Especialidad,
            NivelExperiencia, hash_trazabilidad
        )
        VALUES (
            p_empleado_id, p_nombre, p_especialidad,
            p_nivel, p_hash
        );
        SELECT 'INSERTADO' AS resultado;
    ELSE
        UPDATE DimEmpleado
        SET NombreCompleto = p_nombre,
            Especialidad = p_especialidad,
            NivelExperiencia = p_nivel,
            hash_trazabilidad = p_hash
        WHERE EmpleadoID = p_empleado_id
        AND hash_trazabilidad != p_hash;
        
        SELECT 'ACTUALIZADO' AS resultado;
    END IF;
END//

-- Procedimiento: Cargar dimension Equipo
DROP PROCEDURE IF EXISTS sp_dw_cargar_equipo//
CREATE PROCEDURE sp_dw_cargar_equipo(
    IN p_equipo_id INT,
    IN p_nombre VARCHAR(100),
    IN p_lider_id INT,
    IN p_tipo VARCHAR(50),
    IN p_ubicacion VARCHAR(100),
    IN p_hash VARCHAR(64)
)
BEGIN
    DECLARE v_existe INT;
    
    SELECT COUNT(*) INTO v_existe
    FROM DimEquipo
    WHERE EquipoID = p_equipo_id;
    
    IF v_existe = 0 THEN
        INSERT INTO DimEquipo (
            EquipoID, NombreEquipo, LiderID,
            TipoProyecto, Ubicacion, hash_trazabilidad
        )
        VALUES (
            p_equipo_id, p_nombre, p_lider_id,
            p_tipo, p_ubicacion, p_hash
        );
        SELECT 'INSERTADO' AS resultado;
    ELSE
        UPDATE DimEquipo
        SET NombreEquipo = p_nombre,
            LiderID = p_lider_id,
            TipoProyecto = p_tipo,
            Ubicacion = p_ubicacion,
            hash_trazabilidad = p_hash
        WHERE EquipoID = p_equipo_id
        AND hash_trazabilidad != p_hash;
        
        SELECT 'ACTUALIZADO' AS resultado;
    END IF;
END//

-- Procedimiento: Cargar dimension Proyecto
DROP PROCEDURE IF EXISTS sp_dw_cargar_proyecto//
CREATE PROCEDURE sp_dw_cargar_proyecto(
    IN p_proyecto_id INT,
    IN p_nombre VARCHAR(150),
    IN p_cliente_id INT,
    IN p_equipo_id INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_complejidad VARCHAR(20),
    IN p_hash VARCHAR(64)
)
BEGIN
    DECLARE v_existe INT;
    
    SELECT COUNT(*) INTO v_existe
    FROM DimProyecto
    WHERE ProyectoID = p_proyecto_id;
    
    IF v_existe = 0 THEN
        INSERT INTO DimProyecto (
            ProyectoID, NombreProyecto, ClienteID,
            EquipoID, FechaInicio, FechaFin,
            Complejidad, hash_trazabilidad
        )
        VALUES (
            p_proyecto_id, p_nombre, p_cliente_id,
            p_equipo_id, p_fecha_inicio, p_fecha_fin,
            p_complejidad, p_hash
        );
        SELECT 'INSERTADO' AS resultado;
    ELSE
        UPDATE DimProyecto
        SET NombreProyecto = p_nombre,
            ClienteID = p_cliente_id,
            EquipoID = p_equipo_id,
            FechaInicio = p_fecha_inicio,
            FechaFin = p_fecha_fin,
            Complejidad = p_complejidad,
            hash_trazabilidad = p_hash
        WHERE ProyectoID = p_proyecto_id
        AND hash_trazabilidad != p_hash;
        
        SELECT 'ACTUALIZADO' AS resultado;
    END IF;
END//

-- Procedimiento: Cargar hecho de proyecto
DROP PROCEDURE IF EXISTS sp_dw_cargar_hecho_proyecto//
CREATE PROCEDURE sp_dw_cargar_hecho_proyecto(
    IN p_proyecto_id INT,
    IN p_cliente_id INT,
    IN p_equipo_id INT,
    IN p_empleado_id INT,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_presupuesto DECIMAL(15,2),
    IN p_costo DECIMAL(15,2)
)
BEGIN
    DECLARE v_existe INT;
    DECLARE v_duracion INT;
    DECLARE v_desviacion DECIMAL(15,2);
    DECLARE v_resultado VARCHAR(20);
    
    -- Calcular métricas
    SET v_duracion = DATEDIFF(p_fecha_fin, p_fecha_inicio);
    SET v_desviacion = p_costo - p_presupuesto;
    
    IF v_desviacion <= 0 THEN
        SET v_resultado = 'Bajo Presupuesto';
    ELSEIF v_desviacion <= (p_presupuesto * 0.1) THEN
        SET v_resultado = 'En Presupuesto';
    ELSE
        SET v_resultado = 'Sobre Presupuesto';
    END IF;
    
    -- Verificar si ya existe
    SELECT COUNT(*) INTO v_existe
    FROM HechoProyecto
    WHERE ProyectoID = p_proyecto_id
    AND EmpleadoID = p_empleado_id;
    
    IF v_existe = 0 THEN
        INSERT INTO HechoProyecto (
            ProyectoID, ClienteID, EquipoID, EmpleadoID,
            FechaInicio, FechaFin, DuracionDias,
            PresupuestoAsignado, CostoTotal, DesviacionPresupuesto,
            Resultado
        )
        VALUES (
            p_proyecto_id, p_cliente_id, p_equipo_id, p_empleado_id,
            p_fecha_inicio, p_fecha_fin, v_duracion,
            p_presupuesto, p_costo, v_desviacion,
            v_resultado
        );
        SELECT 'INSERTADO' AS resultado;
    ELSE
        SELECT 'YA_EXISTE' AS resultado;
    END IF;
END//

-- Procedimiento: Limpiar DataWarehouse
DROP PROCEDURE IF EXISTS sp_dw_limpiar//
CREATE PROCEDURE sp_dw_limpiar()
BEGIN
    -- Deshabilitar verificación de FK
    SET FOREIGN_KEY_CHECKS = 0;
    
    TRUNCATE TABLE HechoProyecto;
    TRUNCATE TABLE DimProyecto;
    TRUNCATE TABLE DimEquipo;
    TRUNCATE TABLE DimEmpleado;
    TRUNCATE TABLE DimCliente;
    
    -- Habilitar verificación de FK
    SET FOREIGN_KEY_CHECKS = 1;
    
    SELECT 'LIMPIADO' AS resultado, NOW() AS fecha_hora;
END//

DELIMITER ;

-- ===========================================================================
-- PERMISOS (Descomentar en producción)
-- ===========================================================================

-- Usuario ETL con permisos de extracción
-- CREATE USER IF NOT EXISTS 'etl_user'@'localhost' IDENTIFIED BY 'etl_secure_pass';

-- Permisos en BD Origen
-- USE gestionproyectos_hist;
-- GRANT EXECUTE ON PROCEDURE sp_etl_extraer_clientes TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_extraer_empleados TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_extraer_equipos TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_extraer_proyectos TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_extraer_proyecto_empleados TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_registrar_inicio TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_etl_registrar_fin TO 'etl_user'@'localhost';

-- Permisos en DW
-- USE dw_proyectos_hist;
-- GRANT EXECUTE ON PROCEDURE sp_dw_cargar_cliente TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_dw_cargar_empleado TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_dw_cargar_equipo TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_dw_cargar_proyecto TO 'etl_user'@'localhost';
-- GRANT EXECUTE ON PROCEDURE sp_dw_cargar_hecho_proyecto TO 'etl_user'@'localhost';

-- FLUSH PRIVILEGES;

SELECT '✅ Procedimientos ETL seguros creados exitosamente' AS estado;
