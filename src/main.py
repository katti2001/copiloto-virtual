import time
import cv2
import numpy as np
from pathlib import Path
import urllib.request
import threading

import yaml
from mediapipe import Image, ImageFormat
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from .detectors import detect_signs, smoother
from .quiz import get_question, check_answer
from .state_machine import FatigueStateMachine
from .ui import draw_overlay, draw_alert, draw_face_mesh
from .voice import VoiceIO

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "face_landmarker.task"


def load_config(path: str = "config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_model():
    if MODEL_PATH.exists():
        return MODEL_PATH
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def landmarks_to_np(landmarks, image_shape):
    h, w, _ = image_shape
    pts = []
    for lm in landmarks:
        pts.append([lm.x * w, lm.y * h, lm.z * w])
    return np.array(pts)


class FatigueMonitor:
    def __init__(self):
        self.cfg = load_config()
        self.running = True
        self.alert_active = False
        self.current_question = ""
        self.correct_answer = ""
        self.last_response = ""
        self.face_detected = False
        self.current_signs = {"eyes_closed": False, "yawn": False, "head_down": False}
        
        self.voice_state = "IDLE"
        self.answer_result = ""
        
        self._init_camera()
        self._init_model()
        self._init_voice()
        self._init_state()
    
    def _init_camera(self):
        video_cfg = self.cfg.get("video", {})
        self.cap = cv2.VideoCapture(video_cfg.get("camera_index", 0))
        self.cap.set(cv2.CAP_PROP_FPS, video_cfg.get("target_fps", 15))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    def _init_model(self):
        model_path = ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
    
    def _init_voice(self):
        alerts_cfg = self.cfg.get("alerts", {})
        self.voice = VoiceIO(
            tts_enabled=alerts_cfg.get("tts_voice_enabled", True),
            stt_enabled=alerts_cfg.get("stt_enabled", True)
        )
    
    def _init_state(self):
        self.fsm = FatigueStateMachine(cooldown_sec=self.cfg.get("alerts", {}).get("cooldown_sec", 0))
        self.counters = {"ear": 0, "mar": 0, "pitch": 0}
        self.conf = {}
        self.thresholds = self.cfg.get("thresholds", {})
        self.quiz_timeout = self.cfg.get("alerts", {}).get("quiz_timeout_sec", 10)
    
    def _play_beep(self):
        try:
            import winsound
            winsound.Beep(1000, 150)
            time.sleep(0.1)
            winsound.Beep(1000, 150)
        except:
            pass
    
    def _play_alarm(self):
        try:
            import winsound
            for _ in range(3):
                winsound.Beep(1200, 200)
                time.sleep(0.1)
                winsound.Beep(1200, 200)
                time.sleep(0.1)
        except:
            pass
    
    def _check_sensors_active(self) -> bool:
        return (self.current_signs.get("eyes_closed") or 
                self.current_signs.get("yawn") or 
                self.current_signs.get("head_down"))
    
    def _launch_alert(self):
        if self.alert_active:
            return
        
        self.alert_active = True
        smoother.reset()
        self.last_response = ""
        self.answer_result = ""
        
        self.voice_state = "SPEAKING"
        self.voice.speak("Alerta de somnolencia.")
        self._play_beep()
        time.sleep(0.3)
        
        question, answer = get_question()
        self.current_question = question
        self.correct_answer = answer
        
        self.voice.speak(question)
        
        while self.running:
            self.voice_state = "LISTENING"
            response, heard, status = self.voice.ask(question)
            
            if not heard or not response:
                self.voice_state = "NO_ESCUCHE"
                self.last_response = ""
                self.answer_result = "No te escuche"
                
                self._play_alarm()
                self.voice.play_alarm()
                
                self.voice.speak("No respondiste. Responder mal cuenta como incorrecto.")
                
                sensors_active = self._check_sensors_active()
                
                if sensors_active:
                    self.voice.speak("Sigue dormido. Responde la pregunta.")
                else:
                    self.voice.speak("Sigue alerta. Responde la pregunta.")
                
                time.sleep(0.5)
                self.voice_state = "SPEAKING"
                self.voice.speak(question)
                continue
            
            self.last_response = response
            correct = check_answer(response, answer)
            
            if correct:
                self.voice_state = "CORRECTO"
                self.answer_result = "Correcto"
                self.voice.speak("Correcto. Bien hecho.")
                break
            else:
                self.voice_state = "INCORRECTO"
                self.answer_result = f"Era {answer}"
                self.voice.speak(f"Incorrecto. Era {answer}.")
                
                self._play_alarm()
                self.voice.play_alarm()
                
                sensors_active = self._check_sensors_active()
                
                if sensors_active:
                    self.voice.speak("Todavia con fatiga. Responde la siguiente.")
                else:
                    self.voice.speak("Presta atencion. Responde la siguiente.")
                
                question, answer = get_question()
                self.current_question = question
                self.correct_answer = answer
                self.last_response = ""
                
                time.sleep(0.3)
                self.voice_state = "SPEAKING"
                self.voice.speak(question)
            
            time.sleep(0.3)
        
        time.sleep(1.5)
        
        self.fsm.reset_after_alert()
        self.alert_active = False
        self.current_question = ""
        self.correct_answer = ""
        self.voice_state = "IDLE"
    
    def run(self):
        fps_time = time.time()
        fps_count = 0
        fps = 0
        
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                break
            
            fps_count += 1
            if time.time() - fps_time >= 1.0:
                fps = fps_count
                fps_count = 0
                fps_time = time.time()
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)
            result = self.landmarker.detect(mp_image)
            
            self.face_detected = bool(result.face_landmarks)
            
            self.current_signs = {"eyes_closed": False, "yawn": False, "head_down": False}
            if result.face_landmarks:
                landmarks = landmarks_to_np(result.face_landmarks[0], frame.shape)
                self.current_signs = detect_signs(landmarks, self.thresholds, self.counters, self.conf)
                frame = draw_face_mesh(frame, landmarks, self.current_signs)
            
            state = self.fsm.update(self.current_signs)
            
            if self.fsm.pending_alert and not self.alert_active:
                threading.Thread(target=self._launch_alert, daemon=True).start()
            
            frame = draw_overlay(frame, self.conf, self.current_signs, fps)
            
            if self.alert_active:
                frame = draw_alert(frame, self.current_question, self.answer_result,
                                   voice_state=self.voice_state, last_response=self.last_response,
                                   correct_answer=self.correct_answer)
            
            state_colors = {
                "NORMAL": (0, 255, 0),
                "RISK": (0, 255, 255),
                "ALERT": (0, 0, 255)
            }
            cv2.putText(frame, f"Estado: {state.name}", (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_colors.get(state.name, (255, 255, 255)), 1, cv2.LINE_AA)
            
            if not self.face_detected:
                cv2.putText(frame, "! No se detecta cara !", (frame.shape[1] // 2 - 120, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
            
            cv2.imshow("Detector de Fatiga", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                self.running = False
        
        self.cleanup()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.voice.close()
        print("Sistema detenido.")


def main():
    print("=" * 50)
    print("  DETECTOR DE FATIGA")
    print("=" * 50)
    print("Presiona ESC para salir")
    print("=" * 50)
    
    monitor = FatigueMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
