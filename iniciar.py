"""
Script de inicio del Sistema de Detección de Fatiga
Ejecuta este archivo para iniciar el sistema con interfaz web
"""
import subprocess
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("  SISTEMA DE DETECCIÓN DE FATIGA - COPILOTO VIRTUAL")
    print("=" * 60)
    print()
    print("Iniciando servidor web...")
    print()
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\nSistema detenido por el usuario")
    except Exception as e:
        print(f"\n\nError al iniciar: {e}")
