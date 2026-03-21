from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sys
import threading
import webbrowser
from pathlib import Path

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import DatabaseManager
from auth import GestureAuthenticator
from validator import SystemValidator
from main import FatigueMonitor, load_config

app = Flask(__name__)
app.secret_key = "fatigue_detection_secret_key_2024"  # Cambiar en producción

# Base de datos global
db = None

@app.route("/", methods=["GET", "POST"])
def login():
    """Página de login"""
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        
        if not usuario or not password:
            return render_template("login.html", error="Por favor completa todos los campos")
        
        # Conectar a base de datos
        global db
        if not db:
            db = DatabaseManager(
                host="localhost",
                user="root",
                password="",
                database="detector_fatiga"
            )
            if not db.connect():
                return render_template("login.html", error="Error de conexión a base de datos")
        
        # Verificar credenciales
        user_id = db.verify_user(usuario, password)
        
        if user_id:
            # Guardar en sesión
            session['user_id'] = user_id
            session['username'] = usuario
            return redirect(url_for('gestos'))
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    
    return render_template("login.html")

@app.route("/gestos")
def gestos():
    """Página de gestos faciales"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template("gestos.html", username=session.get('username'))

@app.route("/iniciar_gestos", methods=["POST"])
def iniciar_gestos():
    """API para iniciar autenticación por gestos"""
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "No autenticado"})
    
    try:
        # Ejecutar autenticación por gestos en segundo plano
        gesture_auth = GestureAuthenticator()
        success = gesture_auth.authenticate()
        
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Autenticación fallida"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/monitor")
def monitor():
    """Página que inicia el monitor de fatiga"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Crear sesión en BD
    global db
    user_id = session.get('user_id')
    session_id = db.create_session(user_id, "ambos")
    
    if not session_id:
        return render_template("error.html", error="No se pudo crear la sesión")
    
    session['session_id'] = session_id
    
    # Iniciar monitor en un thread separado
    def run_monitor():
        try:
            config_path = Path(__file__).parent / "config.yaml"
            monitor = FatigueMonitor(db, session_id, str(config_path))
            monitor.run()
        except Exception as e:
            print(f"Error en monitor: {e}")
    
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    
    return render_template("monitor.html", username=session.get('username'))

@app.route("/logout")
def logout():
    """Cerrar sesión"""
    if 'session_id' in session:
        global db
        db.end_session(session['session_id'])
    
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Validar sistema antes de iniciar
    print("=" * 50)
    print("  SISTEMA DE DETECCIÓN DE FATIGA")
    print("=" * 50)
    
    validator = SystemValidator()
    config_path = Path(__file__).parent / "config.yaml"
    all_valid, validation_details = validator.validate_all(str(config_path))
    
    if not all_valid:
        print("\n[ERROR] El sistema no pasó todas las validaciones.")
        print("Por favor, corrige los errores antes de continuar.")
        sys.exit(1)
    
    print("\n[OK] Todas las validaciones pasaron")
    print("\n[INFO] Iniciando servidor web en http://localhost:5000")
    print("[INFO] Abre tu navegador en esa dirección para acceder al sistema")
    
    # Abrir navegador automáticamente
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000')).start()
    
    app.run(debug=True, use_reloader=False)