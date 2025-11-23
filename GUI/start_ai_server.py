# start_ai_server.py - Crear este archivo nuevo
import subprocess
import time
import requests


def start_ai_server_detached():
    """Inicia el servidor IA de forma independiente"""
    print("🚀 INICIANDO SERVIDOR IA EN SEGUNDO PLANO...")

    try:
        process = subprocess.Popen([
            "python", "-m", "uvicorn",
            "analizador_api:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "warning"
        ])

        print("✅ Servidor IA iniciado. PID:", process.pid)

        # Esperar a que esté listo
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("🎯 Servidor IA listo y respondiendo!")
                    return True
            except:
                print(f"⏳ Esperando servidor IA... ({i + 1}/30)")
                time.sleep(2)

        print("⚠️  Servidor IA iniciado pero no respondió aún")
        return True

    except Exception as e:
        print(f"❌ Error iniciando servidor IA: {e}")
        return False


if __name__ == "__main__":
    start_ai_server_detached()