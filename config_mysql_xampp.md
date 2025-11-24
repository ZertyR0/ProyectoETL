# ===============================================
# CONFIGURACIÓN MYSQL PARA XAMPP
# ===============================================
# 
# Para usar MySQL con XAMPP en este proyecto,
# usa estos comandos con el socket correcto:

# Conexión a MySQL XAMPP
mysql -u root -S /Applications/XAMPP/xamppfiles/var/mysql/mysql.sock

# Crear bases de datos necesarias
mysql -u root -S /Applications/XAMPP/xamppfiles/var/mysql/mysql.sock -e "CREATE DATABASE IF NOT EXISTS gestionproyectos_hist;"
mysql -u root -S /Applications/XAMPP/xamppfiles/var/mysql/mysql.sock -e "CREATE DATABASE IF NOT EXISTS datawarehouse;"

# También puedes crear un alias en ~/.zshrc:
# alias mysql-xampp="mysql -u root -S /Applications/XAMPP/xamppfiles/var/mysql/mysql.sock"

# Para usar en Python (mysql-connector-python):
# {
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': '',  # Sin contraseña en XAMPP por defecto
#     'unix_socket': '/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
# }