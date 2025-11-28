#!/usr/bin/env python3
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv('/Users/andrescruzortiz/Documents/GitHub/ProyectoETL/03_Dashboard/backend/.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST_DESTINO'),
    port=int(os.getenv('DB_PORT_DESTINO', '3306')),
    user=os.getenv('DB_USER_DESTINO'),
    password=os.getenv('DB_PASSWORD_DESTINO'),
    database=os.getenv('DB_NAME_DESTINO')
)

cursor = conn.cursor(dictionary=True)

print('=' * 60)
print('VERIFICACIÓN VISTAS OLAP')
print('=' * 60)

# 1. Por Cliente
cursor.execute('SELECT * FROM vw_olap_por_cliente LIMIT 3')
clientes = cursor.fetchall()
print(f'\n1. Por Cliente ({len(clientes)} primeros):')
for c in clientes:
    print(f"  {c['cliente']:30} | Proyectos: {c['total_proyectos']} | Presupuesto: ${c['presupuesto_total']:,.0f}")

# 2. Por Año
cursor.execute('SELECT * FROM vw_olap_por_anio')
anios = cursor.fetchall()
print(f'\n2. Por Año ({len(anios)} registros):')
for a in anios:
    print(f"  Año {a['anio']} | Proyectos: {a['total_proyectos']} | Presupuesto: ${a['presupuesto_total']:,.0f}")

# 3. Total
cursor.execute('SELECT * FROM vw_olap_total')
total = cursor.fetchone()
print(f'\n3. Total Global:')
print(f"  Proyectos: {total['total_proyectos']}")
print(f"  Presupuesto: ${total['presupuesto_total']:,.0f}")
print(f"  Rentabilidad: {total['rentabilidad_porcentaje']:.1f}%")

# 4. Detallado
cursor.execute('SELECT COUNT(*) as total FROM vw_olap_detallado')
detallado = cursor.fetchone()
print(f'\n4. Vista Detallada: {detallado["total"]} registros')

cursor.close()
conn.close()

print('\n' + '=' * 60)
print('✅ Todas las vistas funcionan correctamente')
