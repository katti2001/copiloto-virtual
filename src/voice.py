import re
import threading
import time
from typing import Optional, Tuple

import pyttsx3
import speech_recognition as sr

DEBUG = True

def _log(msg: str):
    print(f"[VOZ] {msg}")


NUMBERS_ES: dict = {
    'cero': '0', 'uno': '1', 'una': '1', 'un': '1', 'dos': '2', 'tres': '3',
    'cuatro': '4', 'cinco': '5', 'seis': '6', 'siete': '7', 'ocho': '8',
    'nueve': '9', 'diez': '10', 'once': '11', 'doce': '12',
}


class VoiceIO:
    def __init__(self, tts_enabled: bool = True, stt_enabled: bool = True):
        self.tts_enabled = tts_enabled
        self.stt_enabled = stt_enabled
        self.engine = pyttsx3.init() if tts_enabled else None
        self.recognizer = sr.Recognizer() if stt_enabled else None
        self._tts_lock = threading.Lock()
        self._is_listening = False

        if self.engine:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            self.engine.setProperty('rate', 145)
            self.engine.setProperty('volume', 1.0)

        if self.recognizer:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 3000
            self.recognizer.pause_threshold = 0.8

    def speak(self, text: str):
        if not self.tts_enabled or not self.engine:
            print(f"TTS: {text}")
            return
        _log(f"HABLA: {text}")
        try:
            with self._tts_lock:
                self.engine.stop()
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            _log(f"Error TTS: {e}")

    def play_alarm(self):
        try:
            import winsound
            for _ in range(3):
                winsound.Beep(1000, 200)
                time.sleep(0.15)
                winsound.Beep(1000, 200)
                time.sleep(0.15)
        except:
            pass

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        for word, num in NUMBERS_ES.items():
            text = re.sub(rf'\b{word}\b', num, text)
        
        return text.strip()

    def _extract_number(self, text: str) -> Optional[str]:
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
        return text if text else None

    def listen(self, timeout: float = 8) -> Tuple[Optional[str], str]:
        if not self.stt_enabled or not self.recognizer:
            return None, "disabled"
        
        self._is_listening = True
        
        try:
            with sr.Microphone() as source:
                _log("Calibrando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                _log(f"Threshold: {self.recognizer.energy_threshold:.0f}")
                _log("Habla ahora!")
                
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
                
                _log("Procesando...")
                text = self.recognizer.recognize_google(audio, language="es-ES")
                _log(f"ENTENDI: '{text}'")
                
                normalized = self._normalize(text)
                result = self._extract_number(normalized)
                _log(f"Numero: {result}")
                
                return result, "ok"
                
        except sr.WaitTimeoutError:
            _log("TIMEOUT - No hablaste")
            return None, "timeout"
        except sr.UnknownValueError:
            _log("NO ENTENDI")
            return None, "unknown"
        except sr.RequestError as e:
            _log(f"Error: {e}")
            return None, "error"
        except Exception as e:
            _log(f"Error: {e}")
            return None, "error"
        finally:
            self._is_listening = False
        
        return None, "error"

    def ask(self, question: str) -> Tuple[Optional[str], bool, str]:
        self.speak(question)
        time.sleep(0.5)
        
        resp, status = self.listen(timeout=8)
        
        if status == "ok" and resp:
            return resp, True, status
        
        return resp, False, status

    def is_listening(self) -> bool:
        return self._is_listening

    def close(self):
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
