# start_ai_server.py - Versión optimizada
import subprocess
import time
import requests
import sys


def start_ai_server_detached():
    """Inicia el servidor IA de forma optimizada"""
    print("🚀 INICIANDO SERVIDOR IA MEJORADO...")

    try:
        # Usar configuración optimizada
        process = subprocess.Popen([
            "python", "-m", "uvicorn",
            "analizador_api:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "warning"
        ])

        print("✅ Servidor IA iniciado. PID:", process.pid)

        # Esperar a que esté listo con timeout extendido
        for i in range(15):  # 30 segundos máximo
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("🎯 Servidor IA listo y respondiendo!")
                    return True
            except:
                if i < 5:
                    print(f"⏳ Iniciando servidor IA... ({i + 1}/15)")
                time.sleep(2)

        print("⚠️  Servidor IA iniciado pero no respondió inmediatamente")
        return True

    except Exception as e:
        print(f"❌ Error iniciando servidor IA: {e}")
        return False


if __name__ == "__main__":
    start_ai_server_detached()