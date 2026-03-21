"""Script para verificar usuario en la base de datos"""
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
    
    # Verificar usuario admin
    print("\n=== Verificando usuario 'admin' ===")
    user_id = db.verify_user("admin", "admin123")
    
    if user_id:
        print(f"[OK] Usuario encontrado! ID: {user_id}")
    else:
        print("[FALLO] Usuario NO encontrado o contrasena incorrecta")
        
        # Intentar obtener info del usuario
        cursor = db.connection.cursor()
        cursor.execute("SELECT id, username, nombre_completo FROM usuarios WHERE username = %s", ("admin",))
        user = cursor.fetchone()
        
        if user:
            print(f"\nUsuario existe en DB: ID={user[0]}, username={user[1]}, nombre={user[2]}")
            print("El problema es la contraseña")
        else:
            print("\nUsuario 'admin' NO existe en la base de datos")
            print("Necesitas ejecutar el script database_setup.sql")
    
    db.disconnect()
else:
    print("No se pudo conectar a la base de datos")
