import math
from typing import Dict, Tuple

import numpy as np


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 380, 373]
MOUTH = [61, 81, 311, 291, 13, 14]
LEFT_EYEBROW = [70, 63, 105, 66, 107]
RIGHT_EYEBROW = [336, 296, 334, 293, 300]
NOSE_TIP = 1
CHIN = 152
FOREHEAD = 10


def _aspect_ratio(points: np.ndarray, idxs: Tuple[int, ...]) -> float:
    p = points[list(idxs)]
    try:
        numerator = np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])
        denominator = 2.0 * np.linalg.norm(p[0] - p[3])
        if denominator < 1e-6:
            return 0.0
        return float(numerator / denominator)
    except:
        return 0.0


def eye_aspect_ratio(landmarks: np.ndarray, left: bool = True) -> float:
    idxs = LEFT_EYE if left else RIGHT_EYE
    return _aspect_ratio(landmarks, tuple(idxs))


def mouth_aspect_ratio(landmarks: np.ndarray) -> float:
    return _aspect_ratio(landmarks, (61, 81, 311, 291, 13, 14))


def head_pitch(landmarks: np.ndarray) -> float:
    nose = landmarks[NOSE_TIP]
    chin = landmarks[CHIN]
    forehead = landmarks[FOREHEAD]
    
    face_vector = chin - forehead
    vertical = np.array([0, 1, 0])
    
    face_unit = face_vector / (np.linalg.norm(face_vector) + 1e-6)
    dot = np.dot(face_unit, vertical)
    dot = np.clip(dot, -1.0, 1.0)
    
    pitch = math.degrees(math.acos(dot))
    
    nose_y = nose[1]
    chin_y = chin[1]
    forehead_y = forehead[1]
    
    face_height = forehead_y - chin_y
    nose_to_chin = chin_y - nose_y
    
    if face_height > 0:
        ratio = nose_to_chin / face_height
        if ratio > 0.5:
            pitch += 15
    
    return pitch


def head_roll(landmarks: np.ndarray) -> float:
    left_ear = landmarks[234]
    right_ear = landmarks[454]
    
    dy = right_ear[1] - left_ear[1]
    dx = right_ear[0] - left_ear[0]
    
    angle = math.degrees(math.atan2(dy, dx))
    return angle


def head_yaw(landmarks: np.ndarray) -> float:
    nose = landmarks[NOSE_TIP]
    left_eye_center = np.mean([landmarks[i] for i in [33, 133]], axis=0)
    right_eye_center = np.mean([landmarks[i] for i in [362, 263]], axis=0)
    eye_center = (left_eye_center + right_eye_center) / 2
    
    nose_offset = nose[0] - eye_center[0]
    face_width = np.linalg.norm(right_eye_center - left_eye_center)
    
    if face_width > 0:
        yaw = (nose_offset / face_width) * 90
        return yaw
    return 0


class Smoother:
    def __init__(self, window: int = 5):
        self.window = window
        self.history = {}
    
    def update(self, key: str, value: float) -> float:
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(value)
        if len(self.history[key]) > self.window:
            self.history[key].pop(0)
        return np.mean(self.history[key])
    
    def reset(self):
        self.history = {}


smoother = Smoother(window=3)


def detect_signs(
    landmarks: np.ndarray,
    thresholds: Dict[str, float],
    counters: Dict[str, int],
    conf: Dict[str, float],
) -> Dict[str, bool]:
    left_ear = eye_aspect_ratio(landmarks, left=True)
    right_ear = eye_aspect_ratio(landmarks, left=False)
    ear = (left_ear + right_ear) / 2.0
    
    mar = mouth_aspect_ratio(landmarks)
    pitch = head_pitch(landmarks)
    roll = head_roll(landmarks)
    yaw = head_yaw(landmarks)
    
    ear = smoother.update("ear", ear)
    mar = smoother.update("mar", mar)
    pitch = smoother.update("pitch", pitch)
    
    ear_closed = thresholds.get("ear_closed", 0.21)
    mar_yawn = thresholds.get("mar_yawn", 0.5)
    head_pitch_deg = thresholds.get("head_pitch_deg", 20)
    
    ear_frames = thresholds.get("ear_frames", 5)
    mar_frames = thresholds.get("mar_frames", 5)
    pitch_frames = thresholds.get("pitch_frames", 6)
    
    if ear < ear_closed:
        counters["ear"] += 1
    else:
        counters["ear"] = max(0, counters["ear"] - 1)
    
    if mar > mar_yawn:
        counters["mar"] += 1
    else:
        counters["mar"] = max(0, counters["mar"] - 1)
    
    if pitch > head_pitch_deg:
        counters["pitch"] += 1
    else:
        counters["pitch"] = max(0, counters["pitch"] - 1)
    
    eyes_closed = counters["ear"] >= ear_frames
    yawn = counters["mar"] >= mar_frames
    head_down = counters["pitch"] >= pitch_frames
    
    signs = {
        "eyes_closed": eyes_closed,
        "yawn": yawn,
        "head_down": head_down,
        "ear_raw": ear,
        "mar_raw": mar,
        "pitch_raw": pitch,
        "roll": roll,
        "yaw": yaw,
    }
    
    conf.update({
        "ear": ear, 
        "mar": mar, 
        "pitch": pitch,
        "left_ear": left_ear, 
        "right_ear": right_ear,
        "roll": roll,
        "yaw": yaw,
        "ear_closed": eyes_closed,
        "yawn_active": yawn,
        "head_down_active": head_down,
    })
    
    return signs
