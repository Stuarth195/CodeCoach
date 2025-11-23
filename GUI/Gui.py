# Gui.py - REEMPLAZAR el contenido completo con:
import sys
import os
import subprocess
import threading
import time
import requests

# Configurar paths ANTES de cualquier import
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


# Gui.py - REEMPLAZAR completamente la función start_ai_server()

# Gui.py - REEMPLAZAR la función start_ai_server() completa:

def start_ai_server():
    """Inicia el servidor de IA con manejo de puertos ocupados"""

    def check_port(port):
        """Verifica si un puerto está disponible"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False

    def find_available_port(start_port=8000, max_attempts=10):
        """Encuentra un puerto disponible"""
        for port in range(start_port, start_port + max_attempts):
            if check_port(port):
                return port
        return None

    def run_server(port):
        try:
            print(f"🚀 Iniciando servidor de IA en puerto {port}...")
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "analizador_api:app",
                "--host", "127.0.0.1",
                "--port", str(port)
            ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            def read_stdout():
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        print(f"[AI Server] {line}")

            def read_stderr():
                for line in process.stderr:
                    line = line.strip()
                    if line:
                        print(f"[AI Server ERROR] {line}")

            threading.Thread(target=read_stdout, daemon=True).start()
            threading.Thread(target=read_stderr, daemon=True).start()

            return process, port

        except Exception as e:
            print(f"❌ Error iniciando servidor IA: {e}")
            return None, None

    # Verificar si ya hay un servidor IA corriendo
    print("🔍 Buscando servidor de IA existente...")
    for port in range(8000, 8010):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Servidor IA ya ejecutándose en puerto {port}")
                # Guardar el puerto para uso futuro
                with open("ai_port.txt", "w") as f:
                    f.write(str(port))
                return True
        except:
            continue

    # Si no hay servidor, iniciar uno nuevo
    available_port = find_available_port()
    if available_port is None:
        print("❌ No se pudo encontrar puerto disponible para IA")
        return False

    process, port = run_server(available_port)
    if process is None:
        return False

    # Guardar el puerto para uso futuro
    with open("ai_port.txt", "w") as f:
        f.write(str(port))

    # Esperar a que esté listo (más rápido)
    print(f"⏳ Esperando servidor IA (puerto {port})...")
    for i in range(10):  # 20 segundos máximo
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Servidor de IA listo en puerto {port}!")
                return True
        except:
            pass
        time.sleep(2)

    print("⚠️  Servidor IA iniciado pero no respondió inmediatamente")
    return True
def main():
    """Módulo principal de ejecución"""
    try:
        from PyQt5.QtWidgets import QApplication
        from LoginWindow import LoginWindow

        app = QApplication(sys.argv)

        # Configurar estilo de la aplicación
        app.setStyle('Fusion')
        app.setApplicationName("leetAI")
        app.setApplicationVersion("1.0.0")

        print("🚀 Iniciando leetAI...")

        # ✅ INICIAR SERVIDOR DE IA SIN BLOQUEAR LA UI
        start_ai_server()

        login_window = LoginWindow()
        login_window.show()
        print("✅ Ventana de login mostrada")

        # Ejecutar loop de la aplicación
        return app.exec_()

    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())