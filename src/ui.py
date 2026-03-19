import cv2
import numpy as np
import time
from typing import Dict


def draw_voice_status(frame, state: str, last_response: str = "", correct_answer: str = ""):
    h, w, _ = frame.shape
    center_x = w // 2
    
    if state == "LISTENING":
        pulse = int(abs(np.sin(time.time() * 5)) * 20 + 25)
        cv2.circle(frame, (center_x, 80), pulse, (0, 255, 0), -1)
        cv2.circle(frame, (center_x, 80), 35, (0, 255, 0), 3)
        
        for i in range(6):
            angle = time.time() * 4 + i * 1.0
            bx = int(center_x + np.cos(angle) * 60)
            by = int(80 + np.sin(angle) * 40)
            cv2.circle(frame, (bx, by), 5, (0, 255, 0), -1)
        
        cv2.putText(frame, "HABLA AHORA", (center_x - 80, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3, cv2.LINE_AA)
    
    elif state == "CORRECTO":
        cv2.circle(frame, (center_x, 80), 55, (0, 255, 0), -1)
        cv2.putText(frame, "OK", (center_x - 22, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, "CORRECTO", (center_x - 85, 155), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3, cv2.LINE_AA)
        if last_response:
            cv2.putText(frame, f"Tu respuesta: {last_response}", (center_x - 100, 185), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    elif state == "INCORRECTO":
        cv2.circle(frame, (center_x, 80), 55, (0, 0, 255), -1)
        cv2.putText(frame, "X", (center_x - 20, 102), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(frame, "INCORRECTO", (center_x - 95, 155), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3, cv2.LINE_AA)
        if last_response:
            cv2.putText(frame, f"Tu respuesta: {last_response}", (center_x - 100, 185), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 200, 200), 2, cv2.LINE_AA)
        if correct_answer:
            cv2.putText(frame, f"Correcta era: {correct_answer}", (center_x - 105, 210), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 100), 2, cv2.LINE_AA)
    
    elif state == "NO_ESCUCHE":
        cv2.circle(frame, (center_x, 80), 55, (100, 100, 100), -1)
        cv2.putText(frame, "?", (center_x - 17, 105), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, "NO ESCUCHE", (center_x - 90, 155), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, "Cuenta como incorrecto", (center_x - 110, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2, cv2.LINE_AA)
    
    elif state == "SPEAKING":
        cv2.circle(frame, (center_x, 80), 40, (0, 255, 255), 4)
        cv2.circle(frame, (center_x, 80), 25, (0, 255, 255), 2)
        bars = int(time.time() * 5) % 4
        for i in range(bars + 1):
            bh = 10 + i * 8
            cv2.rectangle(frame, (center_x - 60 + i * 18, 115 - bh), 
                         (center_x - 52 + i * 18, 115), (0, 255, 255), -1)
        cv2.putText(frame, "ESCUCHA", (center_x - 50, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    
    return frame


def draw_indicator(frame, x: int, y: int, label: str, active: bool, color_active=(0, 255, 0), color_inactive=(80, 80, 80)):
    color = color_active if active else color_inactive
    text_color = (255, 255, 255) if active else (150, 150, 150)
    
    cv2.rectangle(frame, (x, y), (x + 200, y + 35), color, -1)
    cv2.circle(frame, (x + 15, y + 17), 8, (255, 255, 255), -1)
    if active:
        cv2.circle(frame, (x + 15, y + 17), 8, color, -1)
    
    cv2.putText(frame, label, (x + 30, y + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1, cv2.LINE_AA)
    return y + 45


def draw_overlay(frame, conf: Dict[str, float], signs: Dict[str, bool], fps: float = 0):
    h, w, _ = frame.shape
    
    cv2.rectangle(frame, (w - 230, 10), (w - 10, 170), (20, 20, 20), -1)
    cv2.rectangle(frame, (w - 230, 10), (w - 10, 170), (0, 200, 255), 2)
    
    cv2.putText(frame, "FATIGA", (w - 220, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2, cv2.LINE_AA)
    
    y = 55
    
    eyes_active = conf.get("ear_closed", False)
    y = draw_indicator(frame, w - 220, y, "OJOS CERRADOS", eyes_active, (0, 0, 255), (60, 60, 60))
    
    yawn_active = conf.get("yawn_active", False)
    y = draw_indicator(frame, w - 220, y, "BOSTEZO", yawn_active, (0, 0, 255), (60, 60, 60))
    
    head_active = conf.get("head_down_active", False)
    y = draw_indicator(frame, w - 220, y, "CABEZA ABAJO", head_active, (0, 0, 255), (60, 60, 60))
    
    cv2.putText(frame, f"FPS: {fps:.0f}", (w - 100, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1, cv2.LINE_AA)
    
    return frame


def draw_alert(frame, question: str, result: str, voice_state: str = "IDLE", 
               last_response: str = "", correct_answer: str = ""):
    h, w, _ = frame.shape
    
    frame = draw_voice_status(frame, voice_state, last_response, correct_answer)
    
    if question:
        cv2.rectangle(frame, (50, h - 100), (w - 50, h - 20), (0, 0, 0), -1)
        cv2.rectangle(frame, (50, h - 100), (w - 50, h - 20), (0, 0, 255), 3)
        cv2.putText(frame, question[:70], (60, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
    
    return frame


def draw_face_mesh(frame, landmarks, signs: Dict[str, bool]):
    h, w, _ = frame.shape
    
    left_eye = [33, 160, 158, 133, 153, 144]
    right_eye = [263, 387, 385, 362, 380, 373]
    mouth = [61, 81, 311, 291, 13, 14]
    
    eye_color = (0, 0, 255) if signs.get("eyes_closed") else (0, 255, 0)
    mouth_color = (0, 0, 255) if signs.get("yawn") else (0, 255, 0)
    
    for idx in left_eye + right_eye:
        pt = landmarks[idx]
        x, y = int(pt[0]), int(pt[1])
        cv2.circle(frame, (x, y), 2, eye_color, -1)
    
    for idx in mouth:
        pt = landmarks[idx]
        x, y = int(pt[0]), int(pt[1])
        cv2.circle(frame, (x, y), 2, mouth_color, -1)
    
    nose = landmarks[1]
    chin = landmarks[152]
    cv2.circle(frame, (int(nose[0]), int(nose[1])), 3, (255, 255, 0), -1)
    cv2.circle(frame, (int(chin[0]), int(chin[1])), 3, (255, 255, 0), -1)
    
    return frame
