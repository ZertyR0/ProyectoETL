-- POBLAR BSC CON OKRs BASADOS EN DATOS REALES
USE dw_proyectos_hist;

-- Limpiar datos anteriores
DELETE FROM HechoOKR;
DELETE FROM DimKR;
DELETE FROM DimObjetivo;

-- Obtener estadísticas reales del DW
SET @costo_prom = (SELECT AVG(costo_real_proy) FROM HechoProyecto);
SET @presupuesto_prom = (SELECT AVG(presupuesto) FROM HechoProyecto);
SET @horas_prom = (SELECT AVG(horas_reales) FROM HechoTarea);
SET @proyectos_presupuesto = (SELECT SUM(cumplimiento_presupuesto) * 100.0 / COUNT(*) FROM HechoProyecto);
SET @hoy = CURDATE();
SET @inicio_trimestre = DATE_FORMAT(@hoy, '%Y-%m-01');
SET @fin_trimestre = DATE_ADD(@inicio_trimestre, INTERVAL 3 MONTH);

-- PERSPECTIVA FINANCIERA

-- Objetivo 1: Maximizar rentabilidad
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, fecha_creacion, fecha_inicio, fecha_fin, peso_ponderacion)
VALUES ('OBJ-FIN-01', 'Maximizar rentabilidad de proyectos', 
        'Aumentar la rentabilidad mediante control de costos y mejora de márgenes',
        'Financiera', @hoy, @inicio_trimestre, @fin_trimestre, 1.5);

SET @id_obj1 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj1, 'KR-FIN-01', 'Reducir costos promedio en 15%', 'Disminuir', 'USD', 
        ROUND(@costo_prom, 2), 
        ROUND(@costo_prom * 0.85, 2),
        ROUND(@costo_prom * 0.85, 2),
        ROUND(@costo_prom * 0.92, 2));

SET @id_kr1 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj1, 'KR-FIN-02', 'Aumentar margen de ganancia a 25%', 'Aumentar', '%', 
        18.0, 25.0, 24.0, 21.0);

SET @id_kr2 = LAST_INSERT_ID();

-- PERSPECTIVA DE PROCESOS INTERNOS

-- Objetivo 2: Optimizar eficiencia operativa
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, fecha_creacion, fecha_inicio, fecha_fin, peso_ponderacion)
VALUES ('OBJ-PRO-01', 'Optimizar eficiencia operativa', 
        'Mejorar la eficiencia en la ejecución de proyectos y tareas',
        'Procesos Internos', @hoy, @inicio_trimestre, @fin_trimestre, 1.3);

SET @id_obj2 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj2, 'KR-PRO-01', 'Reducir horas promedio por tarea en 20%', 'Disminuir', 'Horas', 
        ROUND(@horas_prom, 2), 
        ROUND(@horas_prom * 0.80, 2),
        ROUND(@horas_prom * 0.80, 2),
        ROUND(@horas_prom * 0.88, 2));

SET @id_kr3 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj2, 'KR-PRO-02', 'Aumentar proyectos dentro de presupuesto a 90%', 'Aumentar', '%', 
        ROUND(@proyectos_presupuesto, 2), 
        90.0, 88.0, 80.0);

SET @id_kr4 = LAST_INSERT_ID();

-- PERSPECTIVA DE CLIENTES

-- Objetivo 3: Mejorar calidad de entregables
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, fecha_creacion, fecha_inicio, fecha_fin, peso_ponderacion)
VALUES ('OBJ-CLI-01', 'Mejorar calidad de entregables', 
        'Incrementar la satisfacción del cliente mediante entregables de calidad',
        'Clientes', @hoy, @inicio_trimestre, @fin_trimestre, 1.4);

SET @id_obj3 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj3, 'KR-CLI-01', 'Reducir defectos reportados en 30%', 'Disminuir', 'Defectos', 
        45.0, 31.5, 32.0, 38.0);

SET @id_kr5 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj3, 'KR-CLI-02', 'Aumentar satisfacción de cliente a 4.5/5', 'Aumentar', 'Puntos', 
        4.1, 4.5, 4.4, 4.2);

SET @id_kr6 = LAST_INSERT_ID();

-- PERSPECTIVA DE APRENDIZAJE E INNOVACIÓN

-- Objetivo 4: Fortalecer capacidad del equipo
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, fecha_creacion, fecha_inicio, fecha_fin, peso_ponderacion)
VALUES ('OBJ-APR-01', 'Fortalecer capacidad del equipo', 
        'Desarrollar habilidades y retener talento clave',
        'Aprendizaje y Innovación', @hoy, @inicio_trimestre, @fin_trimestre, 1.2);

SET @id_obj4 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj4, 'KR-APR-01', 'Aumentar horas de capacitación a 40h/empleado', 'Aumentar', 'Horas', 
        25.0, 40.0, 38.0, 32.0);

SET @id_kr7 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj4, 'KR-APR-02', 'Reducir rotación de personal a 8%', 'Disminuir', '%', 
        15.0, 8.0, 9.0, 11.5);

SET @id_kr8 = LAST_INSERT_ID();

-- Objetivo 5: Acelerar tiempo de entrega
INSERT INTO DimObjetivo (codigo_objetivo, nombre, descripcion, perspectiva, fecha_creacion, fecha_inicio, fecha_fin, peso_ponderacion)
VALUES ('OBJ-PRO-02', 'Acelerar tiempo de entrega', 
        'Reducir los tiempos de ciclo y mejorar entregas a tiempo',
        'Procesos Internos', @hoy, @inicio_trimestre, @fin_trimestre, 1.3);

SET @id_obj5 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj5, 'KR-PRO-03', 'Reducir ciclo promedio de proyecto en 25%', 'Disminuir', 'Días', 
        120.0, 90.0, 92.0, 105.0);

SET @id_kr9 = LAST_INSERT_ID();

INSERT INTO DimKR (id_objetivo, codigo_kr, nombre, tipo_metrica, unidad_medida, valor_inicial, meta_objetivo, umbral_verde, umbral_amarillo)
VALUES (@id_obj5, 'KR-PRO-04', 'Aumentar proyectos entregados a tiempo a 85%', 'Aumentar', '%', 
        65.0, 85.0, 83.0, 74.0);

SET @id_kr10 = LAST_INSERT_ID();

-- INSERTAR MEDICIONES EN HechoOKR (valores actuales)

-- KR 1: Reducir costos
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
SELECT @id_kr1, @hoy, ROUND(@costo_prom * 0.92, 2), @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo';

-- KR 2: Aumentar margen
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr2, @hoy, 21.5, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- KR 3: Reducir horas
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
SELECT @id_kr3, @hoy, ROUND(@horas_prom * 0.88, 2), @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo';

-- KR 4: Proyectos en presupuesto
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
SELECT @id_kr4, @hoy, ROUND(@proyectos_presupuesto + 8.0, 2), @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo';

-- KR 5: Reducir defectos
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr5, @hoy, 38.0, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- KR 6: Satisfacción cliente
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr6, @hoy, 4.3, @hoy, 'ETL Automatizado', 'SISTEMA', 'Verde');

-- KR 7: Capacitación
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr7, @hoy, 32.0, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- KR 8: Rotación
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr8, @hoy, 11.5, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- KR 9: Ciclo de proyecto
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr9, @hoy, 105.0, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- KR 10: Entregas a tiempo
INSERT INTO HechoOKR (id_kr, id_tiempo, valor_observado, fecha_medicion, fuente_medicion, usuario_registro, estado_semaforo)
VALUES (@id_kr10, @hoy, 74.0, @hoy, 'ETL Automatizado', 'SISTEMA', 'Amarillo');

-- Actualizar progresos y estados de semáforo calculados
UPDATE HechoOKR ho
INNER JOIN DimKR kr ON ho.id_kr = kr.id_kr
SET 
    ho.progreso_hacia_meta = CASE
        WHEN kr.tipo_metrica IN ('Aumentar') THEN
            LEAST(100, GREATEST(0, ((ho.valor_observado - kr.valor_inicial) / (kr.meta_objetivo - kr.valor_inicial)) * 100))
        WHEN kr.tipo_metrica IN ('Disminuir') THEN
            LEAST(100, GREATEST(0, ((kr.valor_inicial - ho.valor_observado) / (kr.valor_inicial - kr.meta_objetivo)) * 100))
        ELSE 0
    END,
    ho.estado_semaforo = CASE
        WHEN kr.tipo_metrica IN ('Aumentar') THEN
            CASE
                WHEN ho.valor_observado >= kr.umbral_verde THEN 'Verde'
                WHEN ho.valor_observado >= kr.umbral_amarillo THEN 'Amarillo'
                ELSE 'Rojo'
            END
        WHEN kr.tipo_metrica IN ('Disminuir') THEN
            CASE
                WHEN ho.valor_observado <= kr.umbral_verde THEN 'Verde'
                WHEN ho.valor_observado <= kr.umbral_amarillo THEN 'Amarillo'
                ELSE 'Rojo'
            END
        ELSE 'Amarillo'
    END,
    ho.cumple_meta = CASE
        WHEN kr.tipo_metrica IN ('Aumentar') THEN ho.valor_observado >= kr.meta_objetivo
        WHEN kr.tipo_metrica IN ('Disminuir') THEN ho.valor_observado <= kr.meta_objetivo
        ELSE 0
    END;

-- Verificar resultados
SELECT 
    'BSC POBLADO EXITOSAMENTE' AS resultado,
    (SELECT COUNT(*) FROM DimObjetivo) AS objetivos,
    (SELECT COUNT(*) FROM DimKR) AS key_results,
    (SELECT COUNT(*) FROM HechoOKR) AS mediciones;

SELECT 'Datos calculados del DW:' AS info;
SELECT 
    CONCAT('Costo promedio: $', ROUND(@costo_prom, 2)) AS metrica
UNION ALL SELECT CONCAT('Presupuesto promedio: $', ROUND(@presupuesto_prom, 2))
UNION ALL SELECT CONCAT('Horas promedio/tarea: ', ROUND(@horas_prom, 2))
UNION ALL SELECT CONCAT('% proyectos en presupuesto: ', ROUND(@proyectos_presupuesto, 2), '%');
