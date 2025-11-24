#!/usr/bin/env python3
"""
Generador de datos completos para BD remota
Adaptado a la estructura real de la base de datos
"""

import mysql.connector
import random
"""Legacy script eliminado.

Este generador completo remoto fue reemplazado por un flujo unificado:
  - src/origen/generar_datos.py (parametrizable por argumentos / API)
  - 01_GestionProyectos/datos/generar_datos_final.py (dataset estándar)

El archivo se mantiene sólo como marcador para evitar ejecuciones accidentales
en clones viejos. Elimínalo con: git rm generar_datos_completos.py
"""

raise RuntimeError("generar_datos_completos.py obsoleto. Usa generar_datos_final.py")

