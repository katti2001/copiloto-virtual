# Sistema de detección de fatiga con voz

App local en Python que usa la cámara y el micrófono para detectar somnolencia (ojos cerrados, bostezos, cabeza inclinada). Al detectar riesgo lanza preguntas sencillas (trivia/matemática) por voz; espera respuesta por voz y avisa si no es correcta.

## Requisitos
- Python 3.10+
- Webcam y micrófono funcionando.
- En Windows, PyAudio requiere `pip install pipwin` y luego `pipwin install pyaudio` si la instalación directa falla.

## Instalación
```bash
pip install -r requirements.txt
```

Si PyAudio falla en Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

## Ejecución
```bash
python -m src.main
```
Presiona `ESC` para salir.

## Configuración
Umbrales y opciones en `config.yaml`:
- `thresholds.ear_closed`: EAR para ojo cerrado.
- `thresholds.ear_frames`: frames consecutivos con ojo cerrado.
- `thresholds.mar_yawn`: MAR para bostezo.
- `thresholds.mar_frames`: frames consecutivos de bostezo.
- `thresholds.head_pitch_deg`: grados de inclinación hacia abajo.
- `alerts.quiz_timeout_sec`: segundos para responder.
- `alerts.cooldown_sec`: enfriamiento entre alertas.
- `alerts.tts_voice_enabled` y `alerts.stt_enabled`: activar/desactivar voz.
- `video.camera_index`: índice de cámara.

## Notas
- Funciona mejor con buena iluminación y rostro frontal.
- Gafas oscuras reducen precisión en EAR.
- El reconocimiento de voz usa Google (requiere conexión). Si hay ruido, aumentar `recognizer.adjust_for_ambient_noise`.
# copiloto-virtual
