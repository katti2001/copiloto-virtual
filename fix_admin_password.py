"""Script para actualizar la contraseña del usuario admin"""
import sys
sys.path.insert(0, 'src')

from database import DatabaseManager
import bcrypt

db = DatabaseManager(
    host="localhost",
    user="root",
    password="",
    database="detector_fatiga"
)

if db.connect():
    print("Conectado a la base de datos")
    
    # Crear nuevo hash para admin123
    password = "admin123"
    new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"\nActualizando contraseña del usuario 'admin'...")
    print(f"Nueva contraseña: {password}")
    print(f"Nuevo hash: {new_hash}")
    
    query = "UPDATE usuarios SET hash_contrasena = %s WHERE nombre_usuario = %s"
    success = db.execute_query(query, (new_hash, "admin"))
    
    if success:
        print("\n[OK] Contraseña actualizada exitosamente!")
        
        # Verificar que funciona
        print("\nVerificando login...")
        user_id = db.verify_user("admin", "admin123")
        
        if user_id:
            print(f"[OK] Login exitoso! User ID: {user_id}")
        else:
            print("[ERROR] Algo salió mal, el login no funciona")
    else:
        print("\n[ERROR] No se pudo actualizar la contraseña")
    
    db.disconnect()
else:
    print("[ERROR] No se pudo conectar a la base de datos")
