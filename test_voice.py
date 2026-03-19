"""
Script de prueba interactivo para verificar el sistema de voz.
Ejecuta este script y sigue las instrucciones en pantalla.
"""
from src.voice import VoiceIO
from src.quiz import next_question

def test_voice():
    print("=" * 50)
    print("  TEST INTERACTIVO DE VOZ")
    print("=" * 50)
    print()
    
    v = VoiceIO()
    
    # Test 1: TTS
    print("[1/4] TEST DE VOZ (TTS)")
    print("Debes escuchar: 'Alerta de somnolencia'")
    v.speak("Alerta de somnolencia")
    input("Presiona ENTER cuando hayas escuchado -> ")
    print()
    
    # Test 2: Quiz
    print("[2/4] TEST DE PREGUNTAS")
    questions = []
    for i in range(5):
        q, a = next_question()
        questions.append((q, a))
        print(f"  {i+1}. {q} (respuesta: {a})")
    print()
    
    # Test 3: Escuchar
    print("[3/4] TEST DE ESCUCHA")
    q, a = questions[0]
    print(f"Responde la pregunta: {q}")
    print(f"Respuesta correcta: {a}")
    print("HABLA AHORA...")
    resp = v._listen_once(timeout=10)
    print(f"Escuchado: '{resp}'")
    print(f"Match: {resp and a in resp}")
    print()
    
    # Test 4: Flujo completo
    print("[4/4] TEST COMPLETO DE ALERTA")
    v.speak("Alerta de somnolencia. Contesta la pregunta.")
    
    q, a = questions[1]
    resp = v.ask_and_listen(q, timeout=8, attempts=2)
    
    if resp:
        if a in resp:
            v.speak("Correcto!")
            print(f"CORRECTO! ({a} en {resp})")
        else:
            v.speak("Incorrecto")
            print(f"INCORRECTO - Dijiste '{resp}', era '{a}'")
    else:
        print("NO SE DETECTO RESPUESTA")
    
    print()
    print("=" * 50)
    print("  TEST TERMINADO")
    print("=" * 50)

if __name__ == "__main__":
    test_voice()
