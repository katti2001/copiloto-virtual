import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import bcrypt


class DatabaseManager:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self) -> bool:
        """Conectar a la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"[DB ERROR] Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Ejecutar query sin retorno de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"[DB ERROR] Error en query: {e}")
            return False
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Obtener un solo resultado"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"[DB ERROR] Error en fetch: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[tuple]:
        """Obtener todos los resultados"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"[DB ERROR] Error en fetch: {e}")
            return []
    
    # ==================== USUARIOS ====================
    
    def create_user(self, username: str, password: str, full_name: str = None) -> bool:
        """Crear un nuevo usuario"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = "INSERT INTO usuarios (nombre_usuario, hash_contrasena, nombre_completo) VALUES (%s, %s, %s)"
        return self.execute_query(query, (username, password_hash, full_name))
    
    def verify_user(self, username: str, password: str) -> Optional[int]:
        """Verificar credenciales y retornar user_id si es correcto"""
        query = "SELECT id, hash_contrasena FROM usuarios WHERE nombre_usuario = %s AND activo = TRUE"
        result = self.fetch_one(query, (username,))
        
        if result:
            user_id, stored_hash = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                self._update_last_login(user_id)
                return user_id
        return None
    
    def _update_last_login(self, user_id: int):
        """Actualizar último login"""
        query = "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s"
        self.execute_query(query, (user_id,))
    
    # ==================== SESIONES ====================
    
    def create_session(self, user_id: int, auth_method: str) -> Optional[int]:
        """Crear una nueva sesión"""
        query = "INSERT INTO sesiones (usuario_id, metodo_autenticacion) VALUES (%s, %s)"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id, auth_method))
            self.connection.commit()
            session_id = cursor.lastrowid
            cursor.close()
            return session_id
        except Error as e:
            print(f"[DB ERROR] Error creando sesión: {e}")
            return None
    
    def end_session(self, session_id: int):
        """Finalizar una sesión"""
        query = """
            UPDATE sesiones 
            SET fin_sesion = NOW(), 
                duracion_segundos = TIMESTAMPDIFF(SECOND, inicio_sesion, NOW())
            WHERE id = %s
        """
        self.execute_query(query, (session_id,))
    
    # ==================== EVENTOS DE FATIGA ====================
    
    def log_fatigue_event(self, session_id: int, event_type: str, 
                          severity: str = 'baja', details: Dict[str, Any] = None):
        """Registrar evento de fatiga"""
        query = """
            INSERT INTO eventos_fatiga (sesion_id, tipo_evento, severidad, detalles)
            VALUES (%s, %s, %s, %s)
        """
        details_json = json.dumps(details) if details else None
        self.execute_query(query, (session_id, event_type, severity, details_json))
    
    # ==================== QUIZ ====================
    
    def log_quiz_response(self, session_id: int, question: str, expected_answer: str,
                          user_response: str, is_correct: bool, response_time_ms: int):
        """Registrar respuesta de quiz"""
        query = """
            INSERT INTO respuestas_quiz 
            (sesion_id, pregunta, respuesta_esperada, respuesta_usuario, es_correcta, tiempo_respuesta_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute_query(query, (session_id, question, expected_answer, 
                                   user_response, is_correct, response_time_ms))
    
    # ==================== LOGS DEL SISTEMA ====================
    
    def log_system(self, level: str, message: str, module: str = None, 
                   function_name: str = None, session_id: int = None, 
                   details: Dict[str, Any] = None):
        """Registrar log del sistema"""
        query = """
            INSERT INTO logs_sistema 
            (nivel_log, mensaje, modulo, nombre_funcion, sesion_id, detalles)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        details_json = json.dumps(details) if details else None
        self.execute_query(query, (level, message, module, function_name, 
                                   session_id, details_json))
    
    # ==================== VALIDACIONES ====================
    
    def log_validation(self, camera: bool, microphone: bool, speaker: bool,
                       config_valid: bool, ml_model: bool, details: Dict[str, Any] = None):
        """Registrar validación del sistema"""
        query = """
            INSERT INTO validaciones_sistema 
            (camara_disponible, microfono_disponible, altavoz_disponible, 
             configuracion_valida, modelo_ia_cargado, detalles_validacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        details_json = json.dumps(details) if details else None
        self.execute_query(query, (camera, microphone, speaker, config_valid, 
                                   ml_model, details_json))
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Obtener estadísticas de una sesión"""
        query = """
            SELECT 
                COUNT(*) as total_eventos,
                SUM(CASE WHEN tipo_evento = 'ojos_cerrados' THEN 1 ELSE 0 END) as conteo_ojos_cerrados,
                SUM(CASE WHEN tipo_evento = 'bostezo' THEN 1 ELSE 0 END) as conteo_bostezos,
                SUM(CASE WHEN tipo_evento = 'cabeza_abajo' THEN 1 ELSE 0 END) as conteo_cabeza_abajo,
                SUM(CASE WHEN tipo_evento = 'alerta_activada' THEN 1 ELSE 0 END) as conteo_alertas
            FROM eventos_fatiga
            WHERE sesion_id = %s
        """
        result = self.fetch_one(query, (session_id,))
        
        if result:
            return {
                'total_eventos': result[0],
                'ojos_cerrados': result[1],
                'bostezos': result[2],
                'cabeza_abajo': result[3],
                'alertas': result[4]
            }
        return {}
