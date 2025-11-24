"""Legacy script eliminado.

Este archivo formaba parte de una versión antigua del ETL local simplificado.
Ha sido desactivado y mantenido únicamente como marcador para evitar usos
accidentales. Usa en su lugar:

  python src/etl/etl_incremental.py   # ETL incremental activo
  python src/etl/etl_final.py         # ETL completo vía procedimiento

Si ves este archivo todavía en el repositorio y necesitas borrarlo físicamente,
puedes eliminarlo con git rm etl_local_simple.py.
"""

raise RuntimeError("etl_local_simple.py está obsoleto. Usa src/etl/etl_incremental.py")