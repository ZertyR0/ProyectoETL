#!/bin/bash

# 🚀 Script de Configuración Rápida para Ambiente Distribuido
# Este script configura automáticamente las variables de ambiente necesarias

echo "🚀 Configurando Sistema ETL Distribuido"
echo "========================================"

# Función para preguntar al usuario
preguntar() {
    local pregunta="$1"
    local default="$2"
    local variable="$3"
    
    echo -n "$pregunta [$default]: "
    read respuesta
    
    if [ -z "$respuesta" ]; then
        respuesta="$default"
    fi
    
    export $variable="$respuesta"
}

# Función para configurar ambiente
configurar_ambiente() {
    echo ""
    echo "📋 Configuración de IPs y Credenciales"
    echo "--------------------------------------"
    
    # Configuración de máquinas
    preguntar "IP de la Máquina 1 (BD Origen)" "172.26.163.200" "ETL_HOST_ORIGEN"
    preguntar "IP de la Máquina 3 (Datawarehouse)" "172.26.164.100" "ETL_HOST_DESTINO"
    
    echo ""
    echo "🔐 Configuración de Credenciales"
    echo "--------------------------------"
    
    preguntar "Usuario de BD Origen" "etl_user" "ETL_USER_ORIGEN"
    preguntar "Password de BD Origen" "etl_password_123" "ETL_PASSWORD_ORIGEN"
    preguntar "Usuario de BD Destino" "etl_user" "ETL_USER_DESTINO"
    preguntar "Password de BD Destino" "etl_password_123" "ETL_PASSWORD_DESTINO"
    
    echo ""
    echo "🗄️ Configuración de Bases de Datos"
    echo "----------------------------------"
    
    preguntar "Nombre de BD Origen" "gestionproyectos_hist" "ETL_DB_ORIGEN"
    preguntar "Nombre de BD Destino" "dw_proyectos_hist" "ETL_DB_DESTINO"
    
    # Configuraciones adicionales
    export ETL_AMBIENTE="distribuido"
    export ETL_PORT_ORIGEN="3306"
    export ETL_PORT_DESTINO="3306"
}

# Función para generar archivo de configuración
generar_archivo_config() {
    echo ""
    echo "📄 Generando archivo de configuración..."
    
    cat > config_distribuido.env << EOF
# Configuración ETL Distribuido
# Generado automáticamente: $(date)

# Tipo de ambiente
export ETL_AMBIENTE=distribuido

# Base de datos origen (Máquina 1)
export ETL_HOST_ORIGEN=$ETL_HOST_ORIGEN
export ETL_PORT_ORIGEN=$ETL_PORT_ORIGEN
export ETL_USER_ORIGEN=$ETL_USER_ORIGEN
export ETL_PASSWORD_ORIGEN=$ETL_PASSWORD_ORIGEN
export ETL_DB_ORIGEN=$ETL_DB_ORIGEN

# Datawarehouse (Máquina 3)
export ETL_HOST_DESTINO=$ETL_HOST_DESTINO
export ETL_PORT_DESTINO=$ETL_PORT_DESTINO
export ETL_USER_DESTINO=$ETL_USER_DESTINO
export ETL_PASSWORD_DESTINO=$ETL_PASSWORD_DESTINO
export ETL_DB_DESTINO=$ETL_DB_DESTINO
EOF

    echo "✅ Archivo config_distribuido.env creado"
}

# Función para actualizar bashrc
actualizar_bashrc() {
    echo ""
    echo "📝 ¿Desea agregar la configuración a ~/.bashrc? (y/n)"
    read -n 1 respuesta
    echo ""
    
    if [ "$respuesta" = "y" ] || [ "$respuesta" = "Y" ]; then
        echo "" >> ~/.bashrc
        echo "# Configuración ETL Distribuido - $(date)" >> ~/.bashrc
        cat config_distribuido.env >> ~/.bashrc
        echo "✅ Configuración agregada a ~/.bashrc"
        echo "💡 Ejecute 'source ~/.bashrc' para aplicar los cambios"
    fi
}

# Función para probar conectividad
probar_conectividad() {
    echo ""
    echo "🔍 ¿Desea probar la conectividad ahora? (y/n)"
    read -n 1 respuesta
    echo ""
    
    if [ "$respuesta" = "y" ] || [ "$respuesta" = "Y" ]; then
        # Cargar configuración
        source config_distribuido.env
        
        echo "🔍 Probando conectividad..."
        
        # Probar ping a máquinas
        echo -n "📡 Ping a BD Origen ($ETL_HOST_ORIGEN)... "
        if ping -c 1 -W 3 $ETL_HOST_ORIGEN > /dev/null 2>&1; then
            echo "✅ OK"
        else
            echo "❌ FALLO"
        fi
        
        echo -n "📡 Ping a Datawarehouse ($ETL_HOST_DESTINO)... "
        if ping -c 1 -W 3 $ETL_HOST_DESTINO > /dev/null 2>&1; then
            echo "✅ OK"
        else
            echo "❌ FALLO"
        fi
        
        # Probar conexiones MySQL si está disponible
        if command -v mysql &> /dev/null; then
            echo -n "🗄️ Conexión MySQL BD Origen... "
            if mysql -h $ETL_HOST_ORIGEN -u $ETL_USER_ORIGEN -p$ETL_PASSWORD_ORIGEN -e "SELECT 1" > /dev/null 2>&1; then
                echo "✅ OK"
            else
                echo "❌ FALLO"
            fi
            
            echo -n "🗄️ Conexión MySQL Datawarehouse... "
            if mysql -h $ETL_HOST_DESTINO -u $ETL_USER_DESTINO -p$ETL_PASSWORD_DESTINO -e "SELECT 1" > /dev/null 2>&1; then
                echo "✅ OK"
            else
                echo "❌ FALLO"
            fi
        else
            echo "⚠️ MySQL cliente no instalado, saltando pruebas de BD"
        fi
        
        # Ejecutar verificador completo si está disponible
        if [ -f "verificar_distribuido.py" ]; then
            echo ""
            echo "🔍 ¿Desea ejecutar verificación completa? (y/n)"
            read -n 1 respuesta
            echo ""
            
            if [ "$respuesta" = "y" ] || [ "$respuesta" = "Y" ]; then
                python3 verificar_distribuido.py
            fi
        fi
    fi
}

# Función para mostrar resumen
mostrar_resumen() {
    echo ""
    echo "📊 RESUMEN DE CONFIGURACIÓN"
    echo "=========================="
    echo "🌐 Ambiente: $ETL_AMBIENTE"
    echo "📍 BD Origen: $ETL_USER_ORIGEN@$ETL_HOST_ORIGEN:$ETL_PORT_ORIGEN/$ETL_DB_ORIGEN"
    echo "📍 Datawarehouse: $ETL_USER_DESTINO@$ETL_HOST_DESTINO:$ETL_PORT_DESTINO/$ETL_DB_DESTINO"
    echo ""
    echo "📁 Archivos generados:"
    echo "   • config_distribuido.env"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "   1. Cargar configuración: source config_distribuido.env"
    echo "   2. Probar conexiones: python3 verificar_distribuido.py"
    echo "   3. Ejecutar ETL: python3 02_ETL/scripts/etl_principal.py"
    echo "   4. Iniciar dashboard: python3 03_Dashboard/backend/app.py"
    echo ""
}

# Función principal
main() {
    # Verificar que estamos en el directorio correcto
    if [ ! -f "README_PRINCIPAL.md" ]; then
        echo "❌ Error: Este script debe ejecutarse desde el directorio raíz del proyecto ETL"
        exit 1
    fi
    
    # Ejecutar configuración
    configurar_ambiente
    generar_archivo_config
    actualizar_bashrc
    probar_conectividad
    mostrar_resumen
    
    echo "🎉 ¡Configuración completada!"
}

# Ejecutar función principal
main

# Función de ayuda
mostrar_ayuda() {
    echo "📖 AYUDA - Configurador ETL Distribuido"
    echo "======================================="
    echo ""
    echo "Este script configura automáticamente un sistema ETL distribuido en 3 máquinas:"
    echo ""
    echo "📍 Máquina 1 (BD Origen):"
    echo "   • IP por defecto: 172.26.163.200"
    echo "   • Función: Base de datos operacional"
    echo "   • Software: MySQL Server"
    echo ""
    echo "📍 Máquina 2 (ETL + Dashboard):"
    echo "   • IP: Esta máquina"
    echo "   • Función: Procesamiento ETL y dashboard web"
    echo "   • Software: Python, Flask, MySQL Client"
    echo ""
    echo "📍 Máquina 3 (Datawarehouse):"
    echo "   • IP por defecto: 172.26.164.100"
    echo "   • Función: Almacén de datos para análisis"
    echo "   • Software: MySQL Server"
    echo ""
    echo "🔧 Uso:"
    echo "   ./configurar_distribuido.sh        # Configuración interactiva"
    echo "   ./configurar_distribuido.sh help   # Mostrar esta ayuda"
    echo ""
    echo "📁 Archivos generados:"
    echo "   • config_distribuido.env - Variables de ambiente"
    echo "   • ~/.bashrc actualizado (opcional)"
    echo ""
    echo "🔍 Verificación:"
    echo "   python3 verificar_distribuido.py   # Verificar configuración completa"
    echo ""
}

# Verificar si se solicita ayuda
if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    mostrar_ayuda
    exit 0
fi
