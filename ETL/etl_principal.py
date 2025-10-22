import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Configuración para acceso remoto
# Para localhost (desarrollo)
# SRC_URL = "mysql+mysqlconnector://root:@localhost/gestionproyectos_hist"
# DW_URL  = "mysql+mysqlconnector://root:@localhost/dw_proyectos_hist"

# Para acceso remoto (producción)
SERVER_IP = "172.26.163.200"  # IP de tu servidor XAMPP
SRC_URL = f"mysql+mysqlconnector://etl_user:etl_password_123@{SERVER_IP}/gestionproyectos_hist"
DW_URL  = f"mysql+mysqlconnector://etl_user:etl_password_123@{SERVER_IP}/dw_proyectos_hist"

engine_src = create_engine(SRC_URL, pool_pre_ping=True)
engine_dw  = create_engine(DW_URL,  pool_pre_ping=True)

pd.set_option("display.max_columns", 100)
def find_col(df, candidates, required=True):
    for c in candidates:
        if c in df.columns: 
            return c
    if required:
        raise KeyError(f"No se encontró ninguna de {candidates} en: {list(df.columns)}")
    return None

# Tablas base
df_cliente  = pd.read_sql("SELECT id_cliente, nombre, sector FROM cliente", engine_src)
df_empleado = pd.read_sql("SELECT id_empleado, nombre, puesto FROM empleado", engine_src)
df_equipo   = pd.read_sql("SELECT id_equipo, nombre_equipo, descripcion FROM equipo", engine_src)
df_estado   = pd.read_sql("SELECT id_estado, nombre_estado FROM estado", engine_src)

# Proyectos cerrados
df_proyecto = pd.read_sql("""
    SELECT * FROM proyecto
     WHERE fecha_fin_real IS NOT NULL
       AND id_estado IN (
           SELECT id_estado FROM estado
           WHERE nombre_estado IN ('Completado','Cancelado')
       )
""", engine_src)
if df_proyecto.empty:
    raise ValueError("No hay proyectos cerrados en la base origen.")

# Columnas robustas en PROYECTO
proj_inicio_col   = find_col(df_proyecto, ["fecha_inicio","fecha_inicio_plan","inicio_plan","fecha_ini_plan"])
proj_fin_plan_col = find_col(df_proyecto, ["fecha_fin_plan","fin_plan","fecha_fin_prevista","fecha_termino_plan"])
proj_fin_real_col = find_col(df_proyecto, ["fecha_fin_real","fin_real","fecha_termino_real"])

# Tareas cerradas de esos proyectos
ids_str = ",".join(map(str, df_proyecto["id_proyecto"].tolist()))
df_tarea = pd.read_sql(f"""
    SELECT * FROM tarea
     WHERE id_proyecto IN ({ids_str})
       AND id_estado IN (
           SELECT id_estado FROM estado
           WHERE nombre_estado IN ('Completado','Cancelado')
       )
""", engine_src)

# Columnas robustas en TAREA
task_ini_plan_col = find_col(df_tarea, ["fecha_inicio_plan","inicio_plan","fecha_ini_plan","fecha_inicio"])
task_fin_plan_col = find_col(df_tarea, ["fecha_fin_plan","fin_plan","fecha_fin_prevista","fecha_termino_plan"])
task_fin_real_col = find_col(df_tarea, ["fecha_fin_real","fin_real","fecha_termino_real"])

# Historial de asignaciones de tareas (puede estar vacío)
df_tarea_hist = pd.read_sql("SELECT * FROM tareaequipohist", engine_src)
# Copia directa de catálogos
dim_cliente  = df_cliente.copy()
dim_empleado = df_empleado.copy()
dim_equipo   = df_equipo.copy()

# DimProyecto
dim_proyecto = df_proyecto[["id_proyecto","nombre",proj_inicio_col,proj_fin_plan_col,"presupuesto"]].copy()
dim_proyecto.rename(columns={
    "nombre": "nombre_proyecto",
    proj_inicio_col: "fecha_inicio_plan",
    proj_fin_plan_col: "fecha_fin_plan"
}, inplace=True)
for c in ["fecha_inicio_plan","fecha_fin_plan"]:
    dim_proyecto[c] = pd.to_datetime(dim_proyecto[c]).dt.date

# Construcción de DimTiempo
fechas = set()
for col in [proj_inicio_col, proj_fin_plan_col, proj_fin_real_col]:
    fechas.update(pd.to_datetime(df_proyecto[col]).dt.date.tolist())
for col in [task_ini_plan_col, task_fin_plan_col, task_fin_real_col]:
    fechas.update(pd.to_datetime(df_tarea[col]).dt.date.tolist())

# Limpiar valores nulos
fechas = {f for f in fechas if pd.notna(pd.to_datetime(f, errors="coerce"))}

# Crear DataFrame
dim_tiempo = pd.DataFrame(sorted(fechas), columns=["fecha"])
dim_tiempo["fecha"] = pd.to_datetime(dim_tiempo["fecha"])  # convertir a datetime64[ns]
dim_tiempo["anio"] = dim_tiempo["fecha"].dt.year
dim_tiempo["mes"] = dim_tiempo["fecha"].dt.month
dim_tiempo["trimestre"] = ((dim_tiempo["mes"] - 1) // 3) + 1
dim_tiempo["id_tiempo"] = dim_tiempo["fecha"].dt.date  # PK = fecha como DATE
dim_tiempo = dim_tiempo[["id_tiempo","fecha","anio","mes","trimestre"]]
# Equipo por tarea (primer registro histórico si existe)
if not df_tarea_hist.empty:
    first_assign = df_tarea_hist.sort_values(["id_tarea","id_tarea_equipo"]).drop_duplicates("id_tarea")
    tarea_eq = first_assign[["id_tarea","id_equipo"]]
else:
    tarea_eq = pd.DataFrame(columns=["id_tarea","id_equipo"])

# HechoTarea
fact_tarea = df_tarea.merge(tarea_eq, on="id_tarea", how="left")
# Por ahora, usar NULL para id_tiempo_fin_real hasta implementar lookup correcto
fact_tarea["id_tiempo_fin_real"] = None
fact_tarea["variacion_horas"] = fact_tarea["horas_reales"].astype(float) - fact_tarea["horas_plan"].astype(float)
fact_tarea["cumplimiento_tiempo"] = (
    pd.to_datetime(fact_tarea[task_fin_real_col]) <= pd.to_datetime(fact_tarea[task_fin_plan_col])
).astype(int)

proj_cost = df_proyecto.set_index("id_proyecto")["costo_real"]
hours_sum = df_tarea.groupby("id_proyecto")["horas_reales"].sum()

def _cost_tarea(row):
    total_h = float(hours_sum.get(row["id_proyecto"], 0) or 0)
    if total_h <= 0: return 0.0
    return float((proj_cost.get(row["id_proyecto"], 0) or 0) * row["horas_reales"] / total_h)

fact_tarea["costo_real_tarea"] = fact_tarea.apply(_cost_tarea, axis=1)
fact_tarea = fact_tarea[[
    "id_tarea","id_proyecto","id_equipo","id_tiempo_fin_real",
    "horas_plan","horas_reales","variacion_horas","cumplimiento_tiempo","costo_real_tarea"
]]

# HechoProyecto
fact_proyecto = pd.DataFrame()
fact_proyecto["id_proyecto"]         = df_proyecto["id_proyecto"]
fact_proyecto["id_cliente"]          = df_proyecto["id_cliente"]
fact_proyecto["id_empleado_gerente"] = df_proyecto["id_empleado_gerente"]
# Por ahora, usar NULL para id_tiempo_fin_real hasta implementar lookup correcto
fact_proyecto["id_tiempo_fin_real"] = None
fact_proyecto["presupuesto"]         = df_proyecto["presupuesto"]
fact_proyecto["costo_real_proy"]     = df_proyecto["costo_real"]

dur_plan = (pd.to_datetime(df_proyecto[proj_fin_plan_col]) - pd.to_datetime(df_proyecto[proj_inicio_col])).dt.days
dur_real = (pd.to_datetime(df_proyecto[proj_fin_real_col]) - pd.to_datetime(df_proyecto[proj_inicio_col])).dt.days
fact_proyecto["duracion_planificada"] = dur_plan
fact_proyecto["duracion_real"]        = dur_real
fact_proyecto["variacion_cronograma"] = dur_real - dur_plan
fact_proyecto["cumplimiento_tiempo"]  = (fact_proyecto["variacion_cronograma"] <= 0).astype(int)

tasks_by_proj = df_tarea.merge(df_estado, on="id_estado", how="left") \
                        .groupby("id_proyecto")["nombre_estado"].agg(list)
fact_proyecto["tareas_total"]       = tasks_by_proj.apply(len)
fact_proyecto["tareas_completadas"] = tasks_by_proj.apply(lambda l: sum(1 for x in l if x == "Completado"))
fact_proyecto["tareas_canceladas"]  = tasks_by_proj.apply(lambda l: sum(1 for x in l if x == "Cancelado"))

h_plan = df_tarea.groupby("id_proyecto")["horas_plan"].sum()
h_real = df_tarea.groupby("id_proyecto")["horas_reales"].sum()
fact_proyecto["horas_plan_total"]   = fact_proyecto["id_proyecto"].map(h_plan).fillna(0)
fact_proyecto["horas_reales_total"] = fact_proyecto["id_proyecto"].map(h_real).fillna(0)
fact_proyecto["variacion_horas"]    = fact_proyecto["horas_reales_total"] - fact_proyecto["horas_plan_total"]

if not df_tarea_hist.empty:
    asignaciones = df_tarea_hist.groupby("id_tarea").size()
    asig_df = pd.DataFrame({"id_tarea": asignaciones.index, "asignaciones": asignaciones.values}) \
                .merge(df_tarea[["id_tarea","id_proyecto"]], on="id_tarea", how="left")
    cambios_eq = asig_df.groupby("id_proyecto")["asignaciones"].sum() - asig_df.groupby("id_proyecto")["id_tarea"].count()
else:
    cambios_eq = pd.Series(dtype=float)

fact_proyecto["cambios_equipo_proy"]     = fact_proyecto["id_proyecto"].map(cambios_eq).fillna(0).astype(int)
fact_proyecto["variacion_costos"]         = fact_proyecto["costo_real_proy"] - fact_proyecto["presupuesto"]
fact_proyecto["cumplimiento_presupuesto"] = (fact_proyecto["costo_real_proy"] <= fact_proyecto["presupuesto"]).astype(int)

# Orden final de columnas (coincide con DDL)
fact_proyecto = fact_proyecto[[
    "id_proyecto","id_cliente","id_empleado_gerente","id_tiempo_fin_real",
    "presupuesto","costo_real_proy","variacion_costos","cumplimiento_presupuesto",
    "duracion_planificada","duracion_real","variacion_cronograma","cumplimiento_tiempo",
    "tareas_total","tareas_completadas","tareas_canceladas",
    "horas_plan_total","horas_reales_total","variacion_horas",
    "cambios_equipo_proy"
]]
# Limpiar tablas destino (orden seguro)
with engine_dw.begin() as conn:
    try:
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0;")
        for t in ["HechoTarea","HechoProyecto","DimTiempo","DimProyecto","DimEquipo","DimEmpleado","DimCliente"]:
            conn.exec_driver_sql(f"TRUNCATE TABLE `{t}`;")
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1;")
    except Exception as e:
        print("Aviso: no se pudo desactivar FK, se hará DELETE en orden inverso.", e)
        for t in ["HechoTarea","HechoProyecto","DimTiempo","DimProyecto","DimEquipo","DimEmpleado","DimCliente"]:
            conn.execute(text(f"DELETE FROM `{t}`"))

# Cargar dimensiones (en orden)
dim_cliente[["id_cliente","nombre","sector"]].to_sql("DimCliente", con=engine_dw, if_exists="append", index=False)
dim_empleado[["id_empleado","nombre","puesto"]].to_sql("DimEmpleado", con=engine_dw, if_exists="append", index=False)
dim_equipo[["id_equipo","nombre_equipo"]].to_sql("DimEquipo", con=engine_dw, if_exists="append", index=False)
dim_proyecto_final = dim_proyecto[["id_proyecto","nombre_proyecto","fecha_inicio_plan","fecha_fin_plan","presupuesto"]].copy()
dim_proyecto_final.rename(columns={"presupuesto": "costo_plan"}, inplace=True)
dim_proyecto_final.to_sql("DimProyecto", con=engine_dw, if_exists="append", index=False)
dim_tiempo[["fecha","anio","mes","trimestre"]].to_sql("DimTiempo", con=engine_dw, if_exists="append", index=False)

# Cargar hechos
fact_proyecto.to_sql("HechoProyecto", con=engine_dw, if_exists="append", index=False)
fact_tarea.to_sql("HechoTarea",       con=engine_dw, if_exists="append", index=False)

print("✅ ETL completado: DW cargado.")
