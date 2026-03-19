import queue
import threading
import time
from typing import Optional

import pyttsx3
import sounddevice as sd
import speech_recognition as sr


class VoiceIO:
    def __init__(self, tts_enabled: bool = True, stt_enabled: bool = True):
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        self.engine = pyttsx3.init() if tts_enabled else None
        self.recognizer = sr.Recognizer() if stt_enabled else None
        self._audio_queue: "queue.Queue[bytes]" = queue.Queue()
        self._stop = threading.Event()

        if self.recognizer:
            # Habilita ajuste automatico y un umbral inicial razonable
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 250

    def speak(self, text: str):
        if not self.tts_enabled or not self.engine:
            return
        self.engine.say(text)
        self.engine.runAndWait()

    def _listen_once(self, timeout: float) -> Optional[str]:
        if not self.stt_enabled or not self.recognizer:
            return None
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                return self.recognizer.recognize_google(audio, language="es-ES").lower().strip()
            except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
                return None

    def ask_and_listen(self, question: str, timeout: float, attempts: int = 2, pause_after_tts: float = 0.4) -> Optional[str]:
        # Habla la pregunta y escucha; reintenta si no hubo respuesta
        for i in range(attempts):
            self.speak(question)
            if pause_after_tts:
                time.sleep(pause_after_tts)
            resp = self._listen_once(timeout)
            if resp:
                return resp
            if i < attempts - 1:
                self.speak("No escuché respuesta, repito.")
        return None

    def close(self):
        if self.engine:
            self.engine.stop()
