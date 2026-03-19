import cv2
import numpy as np
from typing import Dict


def draw_overlay(frame, conf: Dict[str, float], signs: Dict[str, bool]):
    h, w, _ = frame.shape
    cv2.rectangle(frame, (10, 10), (260, 150), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (260, 150), (0, 255, 255), 1)

    text = [
        f"EAR: {conf.get('ear', 0):.2f}",
        f"MAR: {conf.get('mar', 0):.2f}",
        f"Pitch: {conf.get('pitch', 0):.1f}",
        f"Ojos cerrados: {signs.get('eyes_closed', False)}",
        f"Bostezo: {signs.get('yawn', False)}",
        f"Cabeza baja: {signs.get('head_down', False)}",
    ]
    y = 35
    for t in text:
        cv2.putText(frame, t, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        y += 20

    return frame
