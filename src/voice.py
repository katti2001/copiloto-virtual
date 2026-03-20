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
        self.recognizer = sr.Recognizer() if stt_enabled else None
        self._tts_lock = threading.Lock()
        self._is_listening = False

        # Detectar voz en español disponible una sola vez al inicio
        self._spanish_voice_id = None
        if tts_enabled:
            try:
                _tmp = pyttsx3.init()
                voices = _tmp.getProperty('voices')
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                        self._spanish_voice_id = voice.id
                        _log(f"Voz española encontrada: {voice.name}")
                        break
                _tmp.stop()
            except Exception as e:
                _log(f"Error detectando voces: {e}")

        if self.recognizer:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 3000
            self.recognizer.pause_threshold = 0.8

    def _make_engine(self):
        """Crea una nueva instancia del motor TTS. Debe llamarse desde el hilo que lo va a usar."""
        engine = pyttsx3.init()
        if self._spanish_voice_id:
            engine.setProperty('voice', self._spanish_voice_id)
        engine.setProperty('rate', 145)
        engine.setProperty('volume', 1.0)
        return engine

    def speak(self, text: str):
        if not self.tts_enabled:
            print(f"TTS: {text}")
            return
        _log(f"HABLA: {text}")
        try:
            with self._tts_lock:
                engine = self._make_engine()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
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
        pass  # No hay motor persistente que cerrar
