import cv2
import sounddevice as sd
import pyttsx3
import yaml
from pathlib import Path
from typing import Dict, Tuple, Any
import speech_recognition as sr


class SystemValidator:
    def __init__(self):
        self.results = {
            'camera': False,
            'microphone': False,
            'speaker': False,
            'config': False,
            'ml_model': False
        }
        self.details = {}
    
    def validate_all(self, config_path: str = "config.yaml") -> Tuple[bool, Dict[str, Any]]:
        """Validar todos los componentes del sistema"""
        print("\n" + "=" * 50)
        print("  VALIDACIÓN DEL SISTEMA")
        print("=" * 50)
        
        self.validate_config(config_path)
        self.validate_camera()
        self.validate_microphone()
        self.validate_speaker()
        self.validate_ml_model()
        
        all_valid = all(self.results.values())
        
        print("\n" + "=" * 50)
        if all_valid:
            print("[RESULTADO] TODAS LAS VALIDACIONES PASARON")
        else:
            print("[RESULTADO] ALGUNAS VALIDACIONES FALLARON")
        print("=" * 50 + "\n")
        
        return all_valid, {'results': self.results, 'details': self.details}
    
    def validate_config(self, config_path: str) -> bool:
        """Validar archivo de configuración"""
        print("[VALIDACIÓN] Verificando configuración...", end=" ")
        
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                print("[FALLO]")
                self.details['config'] = "Archivo config.yaml no encontrado"
                return False
            
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            required_sections = ['video', 'thresholds', 'alerts', 'database']
            missing = [s for s in required_sections if s not in config]
            
            if missing:
                print("[FALLO]")
                self.details['config'] = f"Secciones faltantes: {', '.join(missing)}"
                return False
            
            # Validar valores numéricos
            video = config.get('video', {})
            if not isinstance(video.get('camera_index'), int):
                print("[FALLO]")
                self.details['config'] = "camera_index debe ser un entero"
                return False
            
            thresholds = config.get('thresholds', {})
            required_thresholds = ['ear_closed', 'mar_yawn', 'head_pitch_deg']
            for th in required_thresholds:
                if th not in thresholds:
                    print("[FALLO]")
                    self.details['config'] = f"Threshold {th} faltante"
                    return False
            
            print("[OK]")
            self.results['config'] = True
            self.details['config'] = "Configuración válida"
            return True
            
        except Exception as e:
            print("[FALLO]")
            self.details['config'] = f"Error: {str(e)}"
            return False
    
    def validate_camera(self) -> bool:
        """Validar disponibilidad de cámara"""
        print("[VALIDACIÓN] Verificando cámara...", end=" ")
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[FALLO]")
                self.details['camera'] = "No se pudo abrir la cámara"
                return False
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                print("[FALLO]")
                self.details['camera'] = "No se pudo capturar frame"
                return False
            
            print("[OK]")
            self.results['camera'] = True
            self.details['camera'] = f"Cámara disponible - Resolución: {frame.shape[1]}x{frame.shape[0]}"
            return True
            
        except Exception as e:
            print("[FALLO]")
            self.details['camera'] = f"Error: {str(e)}"
            return False
    
    def validate_microphone(self) -> bool:
        """Validar disponibilidad de micrófono"""
        print("[VALIDACIÓN] Verificando micrófono...", end=" ")
        
        try:
            recognizer = sr.Recognizer()
            mic_list = sr.Microphone.list_microphone_names()
            
            if not mic_list:
                print("[FALLO]")
                self.details['microphone'] = "No se encontraron micrófonos"
                return False
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            print("[OK]")
            self.results['microphone'] = True
            self.details['microphone'] = f"Micrófono disponible - {len(mic_list)} dispositivo(s)"
            return True
            
        except Exception as e:
            print("[FALLO]")
            self.details['microphone'] = f"Error: {str(e)}"
            return False
    
    def validate_speaker(self) -> bool:
        """Validar disponibilidad de altavoces/TTS"""
        print("[VALIDACIÓN] Verificando altavoces...", end=" ")
        
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            if not voices:
                print("[FALLO]")
                self.details['speaker'] = "No se encontraron voces TTS"
                engine.stop()
                return False
            
            # Verificar dispositivos de audio
            devices = sd.query_devices()
            output_devices = [d for d in devices if d['max_output_channels'] > 0]
            
            if not output_devices:
                print("[FALLO]")
                self.details['speaker'] = "No se encontraron dispositivos de salida"
                engine.stop()
                return False
            
            engine.stop()
            print("[OK]")
            self.results['speaker'] = True
            self.details['speaker'] = f"Audio disponible - {len(output_devices)} dispositivo(s)"
            return True
            
        except Exception as e:
            print("[FALLO]")
            self.details['speaker'] = f"Error: {str(e)}"
            return False
    
    def validate_ml_model(self) -> bool:
        """Validar disponibilidad del modelo de ML"""
        print("[VALIDACIÓN] Verificando modelo de IA...", end=" ")
        
        try:
            model_path = Path(__file__).resolve().parent / "models" / "face_landmarker.task"
            
            if model_path.exists():
                size_mb = model_path.stat().st_size / (1024 * 1024)
                print("[OK]")
                self.results['ml_model'] = True
                self.details['ml_model'] = f"Modelo cargado - {size_mb:.1f} MB"
                return True
            else:
                print("[ADVERTENCIA - Se descargara]")
                self.details['ml_model'] = "Modelo no encontrado, se descargará al iniciar"
                # No marcamos como False porque se descargará automáticamente
                self.results['ml_model'] = True
                return True
                
        except Exception as e:
            print("[FALLO]")
            self.details['ml_model'] = f"Error: {str(e)}"
            return False
