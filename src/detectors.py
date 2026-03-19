import math
from typing import Dict, Optional, Tuple

import numpy as np


# Índices de MediaPipe Face Mesh (468 puntos). Estos se usan para EAR y MAR.
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 380, 373]
MOUTH = [61, 81, 311, 291, 13, 14]
NOSE_TIP = 1
CHIN = 152


def _aspect_ratio(points: np.ndarray, idxs: Tuple[int, ...]) -> float:
    p = points[list(idxs)]
    return float(np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])) / (2.0 * np.linalg.norm(p[0] - p[3]))


def eye_aspect_ratio(landmarks: np.ndarray, left: bool = True) -> float:
    idxs = LEFT_EYE if left else RIGHT_EYE
    return _aspect_ratio(landmarks, tuple(idxs))


def mouth_aspect_ratio(landmarks: np.ndarray) -> float:
    # MAR clásico: (||61-81|| + ||311-291||) / (2 * ||13-14||)
    return _aspect_ratio(landmarks, (61, 81, 311, 291, 13, 14))


def head_pitch(landmarks: np.ndarray) -> float:
    # Aproximación simple: ángulo entre nariz y mentón con eje vertical
    nose = landmarks[NOSE_TIP]
    chin = landmarks[CHIN]
    v = chin - nose
    v_unit = v / (np.linalg.norm(v) + 1e-6)
    pitch_rad = math.asin(np.clip(v_unit[1], -1.0, 1.0))
    return math.degrees(pitch_rad)


def detect_signs(
    landmarks: np.ndarray,
    thresholds: Dict[str, float],
    counters: Dict[str, int],
    conf: Dict[str, int],
) -> Dict[str, bool]:
    left_ear = eye_aspect_ratio(landmarks, left=True)
    right_ear = eye_aspect_ratio(landmarks, left=False)
    ear = (left_ear + right_ear) / 2.0
    mar = mouth_aspect_ratio(landmarks)
    pitch = head_pitch(landmarks)

    # Counters
    if ear < thresholds["ear_closed"]:
        counters["ear"] += 1
    else:
        counters["ear"] = 0

    if mar > thresholds["mar_yawn"]:
        counters["mar"] += 1
    else:
        counters["mar"] = 0

    if pitch > thresholds["head_pitch_deg"]:
        counters["pitch"] += 1
    else:
        counters["pitch"] = 0

    signs = {
        "eyes_closed": counters["ear"] >= thresholds["ear_frames"],
        "yawn": counters["mar"] >= thresholds["mar_frames"],
        "head_down": counters["pitch"] >= conf.get("pitch_frames", 8),
    }

    conf.update({"ear": ear, "mar": mar, "pitch": pitch, "left_ear": left_ear, "right_ear": right_ear})
    return signs
