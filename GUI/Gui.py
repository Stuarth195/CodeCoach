# Gui.py
import sys
import os
import subprocess
import threading
import time
import requests
from PyQt5.QtWidgets import QApplication
from LoginWindow import LoginWindow

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def kill_process_on_port(port):
    """Mata cualquier proceso que esté ocupando el puerto especificado"""
    print(f"🧹 Limpiando puerto {port}...")
    try:
        if sys.platform == "win32":
            # Encontrar el PID
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True).decode()
            lines = output.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    # Matar el proceso
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    print(f"💀 Proceso {pid} eliminado del puerto {port}")
    except:
        pass  # Si falla o no hay proceso, continuamos


def start_ai_server():
    """Inicia el servidor de IA asegurando que usa el código nuevo"""
    port = 8000

    # 1. Matar zombies
    kill_process_on_port(port)
    time.sleep(1)  # Dar tiempo al sistema

    # 2. Iniciar el servidor correcto (analizador_api)
    try:
        print(f"🚀 Iniciando servidor Gemini en puerto {port}...")

        # Ocultar ventana de consola en Windows
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "analizador_api:app",  # <--- ESTO ES CLAVE: Usa el archivo de Gemini
            "--host", "127.0.0.1",
            "--port", str(port)
        ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            startupinfo=startupinfo
        )

        # Hilos para leer la salida sin bloquear
        def read_stream(stream, prefix):
            for line in stream:
                if line.strip():
                    print(f"[{prefix}] {line.strip()}")

        threading.Thread(target=read_stream, args=(process.stdout, "IA"), daemon=True).start()
        threading.Thread(target=read_stream, args=(process.stderr, "IA Error"), daemon=True).start()

        # Guardar puerto
        with open("ai_port.txt", "w") as f:
            f.write(str(port))

        # Esperar confirmación de salud
        print("⏳ Esperando respuesta del cerebro IA...")
        for _ in range(15):
            try:
                if requests.get(f"http://127.0.0.1:{port}/health", timeout=1).status_code == 200:
                    print("✅ Servidor IA (Gemini) listo y respondiendo.")
                    return True
            except:
                time.sleep(1)

        print("⚠️ El servidor IA arrancó pero no responde al health check.")
        return True  # Retornamos True para no bloquear la app

    except Exception as e:
        print(f"❌ Error fatal iniciando IA: {e}")
        return False


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        app.setApplicationName("leetAI")

        print("🚀 Arrancando sistema...")

        # Iniciar IA antes de la ventana
        start_ai_server()

        login_window = LoginWindow()
        login_window.show()

        return app.exec_()

    except Exception as e:
        print(f"🔥 Error crítico: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())