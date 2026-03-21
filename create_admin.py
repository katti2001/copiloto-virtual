"""Script para crear el usuario admin si no existe"""
import sys
sys.path.insert(0, 'src')

from database import DatabaseManager

db = DatabaseManager(
    host="localhost",
    user="root",
    password="",
    database="detector_fatiga"
)

if db.connect():
    print("Conectado a la base de datos")
    
    # Verificar si el usuario ya existe
    query = "SELECT id FROM usuarios WHERE nombre_usuario = %s"
    result = db.fetch_one(query, ("admin",))
    
    if result:
        print("El usuario 'admin' ya existe con ID:", result[0])
    else:
        print("Creando usuario 'admin'...")
        success = db.create_user("admin", "admin123", "Administrador del Sistema")
        
        if success:
            print("[OK] Usuario 'admin' creado exitosamente!")
            print("Credenciales: admin / admin123")
        else:
            print("[ERROR] No se pudo crear el usuario")
    
    db.disconnect()
else:
    print("[ERROR] No se pudo conectar a la base de datos")
    print("Asegúrate de que MySQL esté corriendo y que la base de datos 'detector_fatiga' exista")
