import time
import os
from pathlib import Path
import urllib.request
import threading

import yaml
import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from .detectors import detect_signs
from .quiz import next_question
from .state_machine import FatigueStateMachine, State
from .ui import draw_overlay
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


def main():
    cfg = load_config()

    video_cfg = cfg.get("video", {})
    thresholds = cfg.get("thresholds", {})
    alerts_cfg = cfg.get("alerts", {})
    debug = cfg.get("logging", {}).get("debug", False)

    cap = cv2.VideoCapture(video_cfg.get("camera_index", 0))
    cap.set(cv2.CAP_PROP_FPS, video_cfg.get("target_fps", 15))

    model_path = ensure_model()
    base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(options)

    voice = VoiceIO(tts_enabled=alerts_cfg.get("tts_voice_enabled", True), stt_enabled=alerts_cfg.get("stt_enabled", True))
    fsm = FatigueStateMachine(cooldown_sec=alerts_cfg.get("cooldown_sec", 20))
    counters = {"ear": 0, "mar": 0, "pitch": 0}
    conf = {}

    alert_active = False
    alert_message = ""
    current_question = ""

    def launch_alert():
        nonlocal alert_active, alert_message, current_question
        alert_active = True
        question, answer = next_question()
        current_question = question
        print(f"[ALERTA] {question}")
        voice.speak("Alerta de somnolencia. Contesta la pregunta.")
        # Intentos por voz
        resp = voice.ask_and_listen(question, timeout=alerts_cfg.get("quiz_timeout_sec", 8), attempts=3, pause_after_tts=0.5)
        # Si no responde por voz, pedir por teclado
        if not resp:
            voice.speak("No escuché respuesta. Escribe la respuesta y presiona Enter.")
            try:
                resp = input(f"{question} ").strip().lower()
            except Exception:
                resp = None

        if resp and answer in resp:
            voice.speak("Respuesta correcta. Mantente alerta.")
            alert_message = "Respuesta correcta"
        else:
            voice.speak("No se detectó respuesta correcta. Detén el vehículo si es necesario.")
            alert_message = "Sin respuesta o incorrecta"
        fsm.reset_after_alert()
        time.sleep(0.1)
        alert_active = False
        current_question = ""

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)
            result = landmarker.detect(mp_image)

            signs = {"eyes_closed": False, "yawn": False, "head_down": False}
            if result.face_landmarks:
                landmarks = landmarks_to_np(result.face_landmarks[0], frame.shape)
                signs = detect_signs(landmarks, thresholds, counters, conf)

            state = fsm.update(signs)

            if fsm.pending_alert and not alert_active:
                threading.Thread(target=launch_alert, daemon=True).start()

            draw_overlay(frame, conf, signs)
            if alert_active:
                cv2.putText(frame, "ALERTA: Responde la pregunta", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                if current_question:
                    cv2.putText(frame, current_question[:42], (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
                if alert_message:
                    cv2.putText(frame, alert_message, (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("Fatiga", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        voice.close()


if __name__ == "__main__":
    main()
