import cv2
import numpy as np
import time
from pathlib import Path
from typing import Optional, Tuple, Dict
import urllib.request
from mediapipe import Image, ImageFormat
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision


MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "face_landmarker.task"


def ensure_model():
    """Asegurar que el modelo esté descargado"""
    if MODEL_PATH.exists():
        return MODEL_PATH
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("[AUTH] Descargando modelo de detección facial...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def eye_aspect_ratio(landmarks: np.ndarray, eye_indices: list) -> float:
    """Calcular Eye Aspect Ratio"""
    if len(eye_indices) < 6:
        return 0.0
    
    p = landmarks[eye_indices]
    
    try:
        vertical_1 = np.linalg.norm(p[1] - p[5])
        vertical_2 = np.linalg.norm(p[2] - p[4])
        horizontal = np.linalg.norm(p[0] - p[3])
        
        if horizontal < 1e-6:
            return 0.0
        
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return float(ear)
    except:
        return 0.0


def landmarks_to_np(landmarks, image_shape):
    """Convertir landmarks a numpy array"""
    h, w, _ = image_shape
    pts = []
    for lm in landmarks:
        pts.append([lm.x * w, lm.y * h, lm.z * w])
    return np.array(pts)


class GestureAuthenticator:
    """Autenticación por gestos faciales"""
    
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [263, 387, 385, 362, 380, 373]
    
    def __init__(self):
        self.landmarker = self._init_model()
        self.cap = None
    
    def _init_model(self):
        """Inicializar modelo de MediaPipe"""
        model_path = ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
        )
        return vision.FaceLandmarker.create_from_options(options)
    
    def _open_camera(self) -> bool:
        """Abrir cámara"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return True
    
    def _close_camera(self):
        """Cerrar cámara"""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def _detect_blink(self, landmarks: np.ndarray) -> bool:
        """Detectar parpadeo (ambos ojos cerrados)"""
        left_ear = eye_aspect_ratio(landmarks, self.LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, self.RIGHT_EYE)
        
        avg_ear = (left_ear + right_ear) / 2.0
        return avg_ear < 0.20
    
    def _detect_wink_left(self, landmarks: np.ndarray) -> bool:
        """Detectar guiño ojo izquierdo"""
        left_ear = eye_aspect_ratio(landmarks, self.LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, self.RIGHT_EYE)
        
        return left_ear < 0.20 and right_ear > 0.25
    
    def _detect_wink_right(self, landmarks: np.ndarray) -> bool:
        """Detectar guiño ojo derecho"""
        left_ear = eye_aspect_ratio(landmarks, self.LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, self.RIGHT_EYE)
        
        return right_ear < 0.20 and left_ear > 0.25
    
    def _detect_head_movement(self, landmarks: np.ndarray) -> Optional[str]:
        """Detectar movimiento de cabeza (arriba/abajo)"""
        nose = landmarks[1]
        chin = landmarks[152]
        forehead = landmarks[10]
        
        face_height = abs(forehead[1] - chin[1])
        nose_position = (nose[1] - forehead[1]) / face_height if face_height > 0 else 0.5
        
        if nose_position < 0.4:
            return "up"
        elif nose_position > 0.6:
            return "down"
        return None
    
    def _draw_instructions(self, frame: np.ndarray, gesture: str, count: int, total: int):
        """Dibujar instrucciones en pantalla"""
        h, w = frame.shape[:2]
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        instructions = {
            "blink": f"Parpadea 3 veces ({count}/3)",
            "wink_left": f"Guiña el ojo izquierdo 1 vez ({count}/1)",
            "head_down": f"Baja la cabeza 1 vez ({count}/1)"
        }
        
        text = instructions.get(gesture, gesture)
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        progress = f"Paso {total}/3"
        cv2.putText(frame, progress, (20, 75), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.putText(frame, "ESC para cancelar", (w - 200, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
    def authenticate(self) -> bool:
        """
        Autenticar usuario mediante gestos faciales
        Secuencia: 3 parpadeos -> 1 guiño izquierdo -> 1 bajada de cabeza
        """
        if not self._open_camera():
            print("[AUTH] Error: No se pudo abrir la cámara")
            return False
        
        gestures = [
            ("blink", 3),
            ("wink_left", 1),
            ("head_down", 1)
        ]
        
        current_gesture_idx = 0
        gesture_count = 0
        last_state = False
        cooldown = 0
        step_completed = 0
        
        print("\n" + "=" * 50)
        print("  AUTENTICACIÓN POR GESTOS FACIALES")
        print("=" * 50)
        print("Realiza los siguientes gestos:")
        print("1. Parpadea 3 veces")
        print("2. Guiña el ojo izquierdo 1 vez")
        print("3. Baja la cabeza 1 vez")
        print("=" * 50 + "\n")
        
        start_time = time.time()
        timeout = 60
        
        while current_gesture_idx < len(gestures):
            if time.time() - start_time > timeout:
                print("[AUTH] Tiempo agotado")
                self._close_camera()
                return False
            
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)
            result = self.landmarker.detect(mp_image)
            
            current_gesture, required_count = gestures[current_gesture_idx]
            
            detected = False
            if result.face_landmarks:
                landmarks = landmarks_to_np(result.face_landmarks[0], frame.shape)
                
                if current_gesture == "blink":
                    detected = self._detect_blink(landmarks)
                elif current_gesture == "wink_left":
                    detected = self._detect_wink_left(landmarks)
                elif current_gesture == "head_down":
                    head_move = self._detect_head_movement(landmarks)
                    detected = head_move == "down"
                
                for i, lm in enumerate(result.face_landmarks[0]):
                    if i in [10, 152, 1, 33, 263]:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
            
            if cooldown > 0:
                cooldown -= 1
            
            if detected and not last_state and cooldown == 0:
                gesture_count += 1
                cooldown = 15
                print(f"[AUTH] Gesto {current_gesture} detectado ({gesture_count}/{required_count})")
                
                if gesture_count >= required_count:
                    step_completed += 1
                    print(f"[AUTH] [OK] Paso {step_completed}/3 completado")
                    current_gesture_idx += 1
                    gesture_count = 0
                    time.sleep(0.5)
            
            last_state = detected
            
            self._draw_instructions(frame, current_gesture, gesture_count, step_completed + 1)
            
            if detected and cooldown > 0:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 15, (0, 255, 0), -1)
            
            cv2.imshow("Autenticacion por Gestos", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("[AUTH] Autenticación cancelada")
                self._close_camera()
                return False
        
        print("[AUTH] [OK] Autenticacion por gestos exitosa")
        self._close_camera()
        return True


def test_gesture_auth():
    """Función de prueba"""
    auth = GestureAuthenticator()
    result = auth.authenticate()
    print(f"Resultado: {'ÉXITO' if result else 'FALLO'}")


if __name__ == "__main__":
    test_gesture_auth()
