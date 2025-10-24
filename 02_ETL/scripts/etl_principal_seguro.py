#!/usr/bin/env python3
"""
ETL PRINCIPAL SEGURO
- Solo usa procedimientos almacenados
- No hace SELECT/INSERT directos
- Previene filtración de datos
"""

import mysql.connector
from datetime import datetime
import sys

class ETLSeguro:
    """Clase para ETL usando solo stored procedures"""
    
    def __init__(self):
        self.conn_origen = None
        self.conn_destino = None
        self.stats = {
            'clientes': 0,
            'empleados': 0,
            'equipos': 0,
            'proyectos': 0,
            'hechos': 0
        }
    
    def conectar(self):
        """Conectar a ambas bases de datos"""
        try:
            # Conexión a BD Origen (usar etl_user en producción)
            self.conn_origen = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',  # En producción: 'etl_user'
                password='',
                database='gestionproyectos_hist',
                autocommit=False
            )
            print("✅ Conectado a BD Origen")
            
            # Conexión a BD Destino
            self.conn_destino = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',  # En producción: 'etl_user'
                password='',
                database='dw_proyectos_hist',
                autocommit=False
            )
            print("✅ Conectado a BD Destino")
            
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error conectando: {err}")
            return False
    
    def desconectar(self):
        """Cerrar conexiones"""
        if self.conn_origen:
            self.conn_origen.close()
        if self.conn_destino:
            self.conn_destino.close()
    
    def registrar_auditoria_inicio(self, operacion, tabla):
        """Registrar inicio en auditoría"""
        try:
            cursor = self.conn_origen.cursor()
            cursor.callproc('sp_etl_registrar_inicio', [operacion, tabla])
            
            # Obtener ID de auditoría
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    auditoria_id = row[0]
                    cursor.close()
                    return auditoria_id
            
            cursor.close()
            return None
            
        except mysql.connector.Error as err:
            print(f"⚠️  Error registrando auditoría: {err}")
            return None
    
    def registrar_auditoria_fin(self, auditoria_id, registros, estado, mensaje):
        """Registrar fin en auditoría"""
        try:
            cursor = self.conn_origen.cursor()
            cursor.callproc('sp_etl_registrar_fin', 
                          [auditoria_id, registros, estado, mensaje])
            cursor.close()
            self.conn_origen.commit()
        except mysql.connector.Error as err:
            print(f"⚠️  Error actualizando auditoría: {err}")
    
    def extraer_clientes(self):
        """Extraer clientes usando procedimiento"""
        try:
            cursor = self.conn_origen.cursor(dictionary=True)
            cursor.callproc('sp_etl_extraer_clientes')
            
            clientes = []
            for result in cursor.stored_results():
                clientes = result.fetchall()
            
            cursor.close()
            return clientes
            
        except mysql.connector.Error as err:
            print(f"❌ Error extrayendo clientes: {err}")
            return []
    
    def cargar_cliente(self, cliente):
        """Cargar cliente usando procedimiento"""
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_cargar_cliente', [
                cliente['ClienteID'],
                cliente['NombreCompleto'],
                cliente['Industria'],
                cliente['PaisOrigen'],
                cliente['hash_unico']
            ])
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error cargando cliente {cliente['ClienteID']}: {err}")
            return False
    
    def procesar_clientes(self):
        """Procesar dimensión clientes"""
        print("\n📦 Procesando Clientes...")
        auditoria_id = self.registrar_auditoria_inicio('EXTRAER', 'Cliente')
        
        clientes = self.extraer_clientes()
        
        if not clientes:
            print("⚠️  No hay clientes para procesar")
            if auditoria_id:
                self.registrar_auditoria_fin(auditoria_id, 0, 'VACIO', 
                                            'No hay datos')
            return
        
        print(f"   Extrayendo {len(clientes)} clientes...")
        
        exitosos = 0
        for cliente in clientes:
            if self.cargar_cliente(cliente):
                exitosos += 1
        
        self.conn_destino.commit()
        self.stats['clientes'] = exitosos
        
        if auditoria_id:
            self.registrar_auditoria_fin(auditoria_id, exitosos, 'EXITOSO',
                                        f'{exitosos} registros procesados')
        
        print(f"   ✅ {exitosos} clientes cargados")
    
    def extraer_empleados(self):
        """Extraer empleados usando procedimiento"""
        try:
            cursor = self.conn_origen.cursor(dictionary=True)
            cursor.callproc('sp_etl_extraer_empleados')
            
            empleados = []
            for result in cursor.stored_results():
                empleados = result.fetchall()
            
            cursor.close()
            return empleados
            
        except mysql.connector.Error as err:
            print(f"❌ Error extrayendo empleados: {err}")
            return []
    
    def cargar_empleado(self, empleado):
        """Cargar empleado usando procedimiento"""
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_cargar_empleado', [
                empleado['EmpleadoID'],
                empleado['NombreCompleto'],
                empleado['Especialidad'],
                empleado['NivelExperiencia'],
                empleado['hash_unico']
            ])
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error cargando empleado {empleado['EmpleadoID']}: {err}")
            return False
    
    def procesar_empleados(self):
        """Procesar dimensión empleados"""
        print("\n👥 Procesando Empleados...")
        auditoria_id = self.registrar_auditoria_inicio('EXTRAER', 'Empleado')
        
        empleados = self.extraer_empleados()
        
        if not empleados:
            print("⚠️  No hay empleados para procesar")
            if auditoria_id:
                self.registrar_auditoria_fin(auditoria_id, 0, 'VACIO', 
                                            'No hay datos')
            return
        
        print(f"   Extrayendo {len(empleados)} empleados...")
        
        exitosos = 0
        for empleado in empleados:
            if self.cargar_empleado(empleado):
                exitosos += 1
        
        self.conn_destino.commit()
        self.stats['empleados'] = exitosos
        
        if auditoria_id:
            self.registrar_auditoria_fin(auditoria_id, exitosos, 'EXITOSO',
                                        f'{exitosos} registros procesados')
        
        print(f"   ✅ {exitosos} empleados cargados")
    
    def extraer_equipos(self):
        """Extraer equipos usando procedimiento"""
        try:
            cursor = self.conn_origen.cursor(dictionary=True)
            cursor.callproc('sp_etl_extraer_equipos')
            
            equipos = []
            for result in cursor.stored_results():
                equipos = result.fetchall()
            
            cursor.close()
            return equipos
            
        except mysql.connector.Error as err:
            print(f"❌ Error extrayendo equipos: {err}")
            return []
    
    def cargar_equipo(self, equipo):
        """Cargar equipo usando procedimiento"""
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_cargar_equipo', [
                equipo['EquipoID'],
                equipo['NombreEquipo'],
                equipo['LiderID'],
                equipo['TipoProyecto'],
                equipo['Ubicacion'],
                equipo['hash_unico']
            ])
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error cargando equipo {equipo['EquipoID']}: {err}")
            return False
    
    def procesar_equipos(self):
        """Procesar dimensión equipos"""
        print("\n🔧 Procesando Equipos...")
        auditoria_id = self.registrar_auditoria_inicio('EXTRAER', 'Equipo')
        
        equipos = self.extraer_equipos()
        
        if not equipos:
            print("⚠️  No hay equipos para procesar")
            if auditoria_id:
                self.registrar_auditoria_fin(auditoria_id, 0, 'VACIO',
                                            'No hay datos')
            return
        
        print(f"   Extrayendo {len(equipos)} equipos...")
        
        exitosos = 0
        for equipo in equipos:
            if self.cargar_equipo(equipo):
                exitosos += 1
        
        self.conn_destino.commit()
        self.stats['equipos'] = exitosos
        
        if auditoria_id:
            self.registrar_auditoria_fin(auditoria_id, exitosos, 'EXITOSO',
                                        f'{exitosos} registros procesados')
        
        print(f"   ✅ {exitosos} equipos cargados")
    
    def extraer_proyectos(self):
        """Extraer proyectos usando procedimiento"""
        try:
            cursor = self.conn_origen.cursor(dictionary=True)
            cursor.callproc('sp_etl_extraer_proyectos')
            
            proyectos = []
            for result in cursor.stored_results():
                proyectos = result.fetchall()
            
            cursor.close()
            return proyectos
            
        except mysql.connector.Error as err:
            print(f"❌ Error extrayendo proyectos: {err}")
            return []
    
    def cargar_proyecto(self, proyecto):
        """Cargar proyecto usando procedimiento"""
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_cargar_proyecto', [
                proyecto['ProyectoID'],
                proyecto['NombreProyecto'],
                proyecto['ClienteID'],
                proyecto['EquipoID'],
                proyecto['FechaInicio'],
                proyecto['FechaFinReal'],
                proyecto['Complejidad'],
                proyecto['hash_unico']
            ])
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error cargando proyecto {proyecto['ProyectoID']}: {err}")
            return False
    
    def procesar_proyectos(self):
        """Procesar dimensión proyectos"""
        print("\n📊 Procesando Proyectos...")
        auditoria_id = self.registrar_auditoria_inicio('EXTRAER', 'Proyecto')
        
        proyectos = self.extraer_proyectos()
        
        if not proyectos:
            print("⚠️  No hay proyectos completados para procesar")
            if auditoria_id:
                self.registrar_auditoria_fin(auditoria_id, 0, 'VACIO',
                                            'No hay proyectos completados')
            return
        
        print(f"   Extrayendo {len(proyectos)} proyectos completados...")
        
        exitosos = 0
        for proyecto in proyectos:
            if self.cargar_proyecto(proyecto):
                exitosos += 1
        
        self.conn_destino.commit()
        self.stats['proyectos'] = exitosos
        
        if auditoria_id:
            self.registrar_auditoria_fin(auditoria_id, exitosos, 'EXITOSO',
                                        f'{exitosos} registros procesados')
        
        print(f"   ✅ {exitosos} proyectos cargados")
        
        return proyectos
    
    def extraer_proyecto_empleados(self):
        """Extraer relaciones proyecto-empleado usando procedimiento"""
        try:
            cursor = self.conn_origen.cursor(dictionary=True)
            cursor.callproc('sp_etl_extraer_proyecto_empleados')
            
            relaciones = []
            for result in cursor.stored_results():
                relaciones = result.fetchall()
            
            cursor.close()
            return relaciones
            
        except mysql.connector.Error as err:
            print(f"❌ Error extrayendo relaciones: {err}")
            return []
    
    def cargar_hecho_proyecto(self, proyecto, empleado_id):
        """Cargar hecho de proyecto usando procedimiento"""
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_cargar_hecho_proyecto', [
                proyecto['ProyectoID'],
                proyecto['ClienteID'],
                proyecto['EquipoID'],
                empleado_id,
                proyecto['FechaInicio'],
                proyecto['FechaFinReal'],
                proyecto['PresupuestoAsignado'],
                proyecto['CostoTotal']
            ])
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error cargando hecho: {err}")
            return False
    
    def procesar_hechos(self, proyectos):
        """Procesar tabla de hechos"""
        print("\n📈 Procesando Hechos de Proyectos...")
        auditoria_id = self.registrar_auditoria_inicio('CARGAR', 'HechoProyecto')
        
        relaciones = self.extraer_proyecto_empleados()
        
        if not relaciones:
            print("⚠️  No hay relaciones para procesar")
            if auditoria_id:
                self.registrar_auditoria_fin(auditoria_id, 0, 'VACIO',
                                            'No hay relaciones')
            return
        
        print(f"   Procesando {len(relaciones)} relaciones proyecto-empleado...")
        
        # Crear índice de proyectos por ID
        proyectos_map = {p['ProyectoID']: p for p in proyectos}
        
        exitosos = 0
        for rel in relaciones:
            proyecto = proyectos_map.get(rel['ProyectoID'])
            if proyecto:
                if self.cargar_hecho_proyecto(proyecto, rel['EmpleadoID']):
                    exitosos += 1
        
        self.conn_destino.commit()
        self.stats['hechos'] = exitosos
        
        if auditoria_id:
            self.registrar_auditoria_fin(auditoria_id, exitosos, 'EXITOSO',
                                        f'{exitosos} hechos procesados')
        
        print(f"   ✅ {exitosos} hechos cargados")
    
    def limpiar_datawarehouse(self):
        """Limpiar DataWarehouse usando procedimiento"""
        print("\n🗑️  Limpiando DataWarehouse...")
        try:
            cursor = self.conn_destino.cursor()
            cursor.callproc('sp_dw_limpiar')
            cursor.close()
            self.conn_destino.commit()
            print("   ✅ DataWarehouse limpiado")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error limpiando: {err}")
            return False
    
    def ejecutar_etl_completo(self, limpiar=False):
        """Ejecutar ETL completo"""
        print("="*70)
        print("🔒 ETL SEGURO - Inicio")
        print("="*70)
        print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.conectar():
            return False
        
        try:
            # Limpiar si se solicita
            if limpiar:
                if not self.limpiar_datawarehouse():
                    return False
            
            # Procesar dimensiones
            self.procesar_clientes()
            self.procesar_empleados()
            self.procesar_equipos()
            proyectos = self.procesar_proyectos()
            
            # Procesar hechos
            if proyectos:
                self.procesar_hechos(proyectos)
            
            # Resumen
            print("\n" + "="*70)
            print("📊 RESUMEN ETL SEGURO")
            print("="*70)
            print(f"   Clientes procesados:  {self.stats['clientes']:>6}")
            print(f"   Empleados procesados: {self.stats['empleados']:>6}")
            print(f"   Equipos procesados:   {self.stats['equipos']:>6}")
            print(f"   Proyectos procesados: {self.stats['proyectos']:>6}")
            print(f"   Hechos procesados:    {self.stats['hechos']:>6}")
            print("="*70)
            print("✅ ETL COMPLETADO EXITOSAMENTE")
            print("🔒 Sin acceso directo a datos sensibles")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error en ETL: {e}")
            return False
        
        finally:
            self.desconectar()

def main():
    """Función principal"""
    limpiar = '--limpiar' in sys.argv or '-l' in sys.argv
    
    etl = ETLSeguro()
    
    if limpiar:
        print("⚠️  Modo: Limpiar y recargar")
    else:
        print("ℹ️  Modo: Incremental")
    
    exito = etl.ejecutar_etl_completo(limpiar=limpiar)
    
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()
