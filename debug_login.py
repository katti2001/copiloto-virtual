"""Script para debuggear el problema de login"""
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
    print("Conectado a la base de datos\n")
    
    # 1. Ver qué hay en la tabla usuarios
    print("=== USUARIOS EN LA BASE DE DATOS ===")
    query = "SELECT id, nombre_usuario, nombre_completo, activo FROM usuarios"
    usuarios = db.fetch_all(query)
    
    for user in usuarios:
        print(f"ID: {user[0]}, Usuario: {user[1]}, Nombre: {user[2]}, Activo: {user[3]}")
    
    # 2. Obtener el hash almacenado del usuario admin
    print("\n=== VERIFICANDO HASH DE CONTRASEÑA ===")
    query = "SELECT id, hash_contrasena FROM usuarios WHERE nombre_usuario = %s"
    result = db.fetch_one(query, ("admin",))
    
    if result:
        user_id, stored_hash = result
        print(f"Usuario ID: {user_id}")
        print(f"Hash almacenado: {stored_hash[:60]}...")
        print(f"Tipo del hash: {type(stored_hash)}")
        
        # 3. Intentar verificar la contraseña
        print("\n=== INTENTANDO VERIFICAR CONTRASEÑA ===")
        password = "admin123"
        print(f"Contraseña a verificar: {password}")
        
        try:
            # Convertir el hash a bytes si es necesario
            if isinstance(stored_hash, str):
                stored_hash_bytes = stored_hash.encode('utf-8')
            else:
                stored_hash_bytes = stored_hash
            
            password_bytes = password.encode('utf-8')
            
            match = bcrypt.checkpw(password_bytes, stored_hash_bytes)
            print(f"Resultado de verificación: {match}")
            
            if match:
                print("[OK] La contraseña es correcta!")
            else:
                print("[FALLO] La contraseña NO coincide")
                
                # Crear un nuevo hash para admin123 y mostrarlo
                print("\n=== CREANDO NUEVO HASH ===")
                new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
                print(f"Nuevo hash: {new_hash}")
                
        except Exception as e:
            print(f"[ERROR] al verificar: {e}")
    
    else:
        print("No se encontró el usuario admin")
    
    db.disconnect()
else:
    print("[ERROR] No se pudo conectar a la base de datos")
