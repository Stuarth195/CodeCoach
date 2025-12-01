import sys
import os
import threading
import subprocess
import time
import requests
import json
import re
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve,
    pyqtProperty, pyqtSignal, QThread, QProcess
)

from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QFontDatabase
)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
    QListWidget, QLabel, QPushButton, QSplitter,
    QFrame, QProgressBar, QStackedWidget, QMessageBox,
    QFormLayout, QLineEdit, QComboBox, QFileDialog
)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar desde módulos de lógica
try:
    from logic.database_handler import DatabaseHandler
    from logic.auth_logic import AuthManager
    from logic.user_models import User
    print("✅ Módulos de lógica importados en AuxCreator")
except ImportError as e:
    print(f"❌ Error importando módulos de lógica: {e}")
    # Clases dummy para desarrollo
    class DatabaseHandler:
        def get_all_problem_titles(self): return ["Problema Dummy 1", "Problema Dummy 2"]
        def get_problem_details(self, title): return None
        def get_global_ranking(self, limit=10): return []

    class AuthManager:
        def update_user_progress(self, *args): print("Dummy: Actualizando progreso"); return True, None

    class User:
        def __init__(self, username=""):
            self.username = username
            self.puntaje_total = 0
            self.problemas_resueltos = 0
            self.ejercicios_completados = []
            self.facil_resueltos = 0
            self.medio_resueltos = 0
            self.dificil_resueltos = 0
            self.racha_actual = 0
            self.mejor_racha = 0

        def refresh_stats(self): pass
        def get_stats_for_display(self):
            return {
                'Puntos Totales': str(self.puntaje_total),
                'Problemas Resueltos': str(self.problemas_resueltos),
                'Ejercicios Únicos': str(len(self.ejercicios_completados)),
                'Racha Actual': str(self.racha_actual),
                'Mejor Racha': str(self.mejor_racha),
                'Fácil Resueltos': str(self.facil_resueltos),
                'Medio Resueltos': str(self.medio_resueltos),
                'Difícil Resueltos': str(self.dificil_resueltos)
            }

# Importar PyLogic
try:
    from PyLogic import CodeCompilerWrapper, UIActions
    print("✅ PyLogic importado correctamente")
except ImportError as e:
    print(f"❌ Error importando PyLogic: {e}")
    # Dummy classes
    class CodeCompilerWrapper:
        def send_evaluation_package(self, payload):
            return {"status": "dummy", "message": "Modo dummy"}

    class UIActions:
        def __init__(self, win): self.win = win
        def run_code(self): print("Dummy run_code")
        def send_code(self): print("Dummy send_code")
        def reset_editor(self): print("Dummy reset_editor")
        def save_code(self): print("Dummy save_code")
        def open_section(self, name): print(f"Dummy open_section: {name}")


class AIAnalysisThread(QThread):
    """Hilo para manejar las solicitudes a la API de IA con reintentos"""
    analysis_complete = pyqtSignal(dict)

    def __init__(self, api_url, analysis_data):
        super().__init__()
        self.api_url = api_url
        self.analysis_data = analysis_data

    def run(self):
        max_retries = 2
        base_timeout = 30

        for attempt in range(max_retries):
            try:
                current_timeout = base_timeout * (attempt + 1)  # Timeout progresivo
                print(f"🤖 Intento {attempt + 1}/{max_retries} (timeout: {current_timeout}s)")

                response = requests.post(
                    self.api_url,
                    json=self.analysis_data,
                    timeout=current_timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    print("✅ Respuesta de IA recibida exitosamente")
                    self.analysis_complete.emit(result)
                    return
                else:
                    error_msg = f"Error HTTP {response.status_code}: {response.text}"
                    print(f"❌ {error_msg}")

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏰ Timeout en intento {attempt + 1}, reintentando...")
                    continue
                else:
                    error_msg = "Todos los intentos agotaron el tiempo de espera"
                    print(f"❌ {error_msg}")
                    self.analysis_complete.emit({
                        "status": "timeout_error",
                        "message": error_msg,
                        "feedback_completo": "El servidor de IA no responde. Puede estar cargando modelos grandes. Intenta en unos minutos."
                    })
                    return

            except requests.exceptions.ConnectionError:
                error_msg = "No se pudo conectar al servidor de IA"
                print(f"❌ {error_msg}")
                self.analysis_complete.emit({
                    "status": "connection_error",
                    "message": error_msg,
                    "feedback_completo": "El servidor de IA no está disponible en localhost:8000"
                })
                return

            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                print(f"❌ {error_msg}")
                self.analysis_complete.emit({
                    "status": "unexpected_error",
                    "message": error_msg,
                    "feedback_completo": f"Error inesperado: {str(e)}"
                })
                return

        # Si llegamos aquí, todos los reintentos fallaron por timeout
        self.analysis_complete.emit({
            "status": "max_retries_exceeded",
            "message": "Máximo número de reintentos alcanzado",
            "feedback_completo": "No se pudo obtener respuesta del servidor de IA después de múltiples intentos."
        })

class ModernMainWindow(QMainWindow):
    # AuxCreator.py - EN LA CLASE ModernMainWindow, MODIFICAR __init__:

    def __init__(self):
        super().__init__()
        self.current_section = None
        self.current_problem_data = None
        self.logged_in_user = None
        self.code_base_loaded = False

        print("🚀 INICIANDO MODERN MAIN WINDOW...")

        # Instanciación a prueba de fallos
        try:
            self.compiler_client = CodeCompilerWrapper()
            print("✅ CodeCompilerWrapper inicializado")
        except Exception as e:
            print(f"❌ Error en CodeCompilerWrapper: {e}")
            self.compiler_client = None

        try:
            self.db_handler = DatabaseHandler()
            print("✅ DatabaseHandler inicializado")
        except Exception as e:
            print(f"❌ Error en DatabaseHandler: {e}")
            self.db_handler = None

        self.ai_api_url = "http://localhost:8000/analyze_solution"
        self.ai_thread = None
        self.ai_server_process = None

        # --- CORRECCIÓN AQUÍ ---
        # Verificamos si Gui.py ya encendió el servidor
        if self.check_ai_server_running():
            print("✅ AuxCreator detectó que el servidor IA ya está online")
            self.ai_server_started = True
        else:
            print("⚠️ Servidor IA no detectado, se gestionará bajo demanda")
            self.ai_server_started = False



        self.diagnose_database()
        self.initUI()
        self.load_problems_into_sidebar()

        # Conectar la lista a una nueva función
        if hasattr(self, 'problems_list'):
            self.problems_list.itemClicked.connect(self.display_problem_details)

    def initUI(self):
        """Inicializa la interfaz de usuario con diseño moderno"""
        self.setWindowTitle('leetAI - Code Coaching Platform')
        self.setGeometry(100, 100, 1600, 1000)

        # Configuración básica
        self.setup_fonts()
        self.setup_dark_palette()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Crear componentes
        left_sidebar = self.create_left_sidebar()
        self.central_stacked = self.create_central_stacked()

        # Agregar componentes al layout principal
        main_layout.addWidget(left_sidebar)
        main_layout.addWidget(self.central_stacked, 1)

        # Configurar acciones
        self.setup_actions()

        # Configurar template por defecto
        self.setup_default_code_template()

        # Mostrar sección por defecto (Editor de Código)
        self.show_section("Editor")

    def start_ai_server(self):
        """Inicia el servidor de IA con mejor verificación"""
        try:
            print("🔧 Iniciando servidor de IA...")

            # Verificar si el servidor ya está corriendo
            if self.check_ai_server_running():
                print("✅ Servidor de IA ya está ejecutándose")
                self.ai_server_started = True
                return True

            # Verificar que el archivo de la API existe
            if not os.path.exists("analizador_api.py"):
                print("❌ Archivo analizador_api.py no encontrado")
                return False

            # Comando para iniciar el servidor FastAPI
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                "analizador_api:app",
                "--host", "127.0.0.1",  # Usar 127.0.0.1 en lugar de localhost
                "--port", "8000",
                "--reload"
            ]

            # Iniciar el proceso en segundo plano
            self.ai_server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Hilo para monitorear la salida del servidor
            monitor_thread = threading.Thread(target=self.monitor_ai_server_output)
            monitor_thread.daemon = True
            monitor_thread.start()

            # Esperar a que el servidor esté listo (más tiempo)
            print("⏳ Esperando a que el servidor de IA esté listo (hasta 60 segundos)...")
            if self.wait_for_ai_server(timeout=60):  # Aumentar timeout a 60 segundos
                print("✅ Servidor de IA iniciado exitosamente")
                self.ai_server_started = True
                return True
            else:
                print("❌ Timeout: Servidor de IA no respondió a tiempo")
                return False

        except Exception as e:
            print(f"❌ Error iniciando servidor de IA: {e}")
            return False

    def check_ai_server_running(self):
        """Verifica si el servidor de IA está corriendo"""
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            return response.status_code == 200
        except:
            return False

    def wait_for_ai_server(self, timeout=30):
        """Espera a que el servidor de IA esté listo"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_ai_server_running():
                return True
            time.sleep(2)  # Esperar 2 segundos entre intentos
        return False

    def monitor_ai_server_output(self):
        """Monitorea la salida del servidor de IA en un hilo separado"""
        try:
            print("📡 Monitoreando servidor de IA...")
            while self.ai_server_process and self.ai_server_process.poll() is None:
                # Leer stdout
                stdout_line = self.ai_server_process.stdout.readline()
                if stdout_line:
                    print(f"[AI Server] {stdout_line.strip()}")

                # Leer stderr
                stderr_line = self.ai_server_process.stderr.readline()
                if stderr_line:
                    print(f"[AI Server ERROR] {stderr_line.strip()}")

        except Exception as e:
            print(f"❌ Error monitoreando servidor IA: {e}")

    def stop_ai_server(self):
        """Detiene el servidor de IA cuando se cierra la aplicación"""
        if self.ai_server_process:
            print("🛑 Deteniendo servidor de IA...")
            self.ai_server_process.terminate()
            try:
                self.ai_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ai_server_process.kill()
            print("✅ Servidor de IA detenido")

    def show_ai_server_error(self, error_message):
        """Muestra errores del servidor de IA en el panel correspondiente"""
        error_display = f"""
    ❌ ERROR DEL SERVIDOR DE IA

    {error_message}

    Solución automática intentada:
    • Se intentó iniciar el servidor automáticamente
    • Verificando dependencias...

    Si el problema persiste:
    1. Verifica que tengas instaladas todas las dependencias
    2. Ejecuta manualmente: uvicorn analizador_api:app --reload --port 8000
    3. Reinicia la aplicación
    """
        if hasattr(self, 'ai_feedback'):
            self.ai_feedback.setPlainText(error_display)

    def create_central_stacked(self):
        """Crea el QStackedWidget para manejar las diferentes secciones - SIN AJUSTES"""
        self.stacked_widget = QStackedWidget()

        # Crear todas las secciones (SIN AJUSTES)
        self.editor_section = self.create_coding_environment()
        self.problems_section = self.create_problems_section()
        self.progress_section = self.create_progress_section()
        self.ranking_section = self.create_ranking_section()
        self.problem_management_section = self.create_problem_management_section()  # NUEVA SECCIÓN

        # Agregar secciones al stacked widget (SIN AJUSTES)
        self.stacked_widget.addWidget(self.editor_section)  # Índice 0
        self.stacked_widget.addWidget(self.problems_section)  # Índice 1
        self.stacked_widget.addWidget(self.progress_section)  # Índice 2
        self.stacked_widget.addWidget(self.ranking_section)  # Índice 3
        self.stacked_widget.addWidget(self.problem_management_section)  # Índice 4

        return self.stacked_widget

    def show_section(self, section_name):
        """Muestra una sección específica con animación - MAPA ACTUALIZADO"""
        section_map = {
            "Editor": 0,
            "Problemas": 1,
            "Mi Progreso": 2,
            "Ranking": 3,
            "Gestión Problemas": 4  # NUEVO ÍNDICE
        }

        if section_name in section_map:
            new_index = section_map[section_name]
            self.animate_section_change(new_index)
            self.current_section = section_name

    def animate_section_change(self, new_index):
        """Animación para cambiar entre secciones"""
        self.animation = QPropertyAnimation(self.stacked_widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self.complete_section_change(new_index))
        self.animation.start()

    def complete_section_change(self, new_index):
        """Completa el cambio de sección después de la animación"""
        self.stacked_widget.setCurrentIndex(new_index)
        self.animation = QPropertyAnimation(self.stacked_widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def setup_fonts(self):
        """Configura fuentes personalizadas para la aplicación"""
        pass

    def setup_dark_palette(self):
        """Configura paleta de colores oscura moderna"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 35))
        dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Base, QColor(20, 20, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 50))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 55))
        dark_palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        self.setPalette(dark_palette)

    def create_left_sidebar(self):
        """Crea la barra lateral izquierda con navegación"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)

        # Logo y título
        logo_label = QLabel("leetAI")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Navegación principal
        nav_buttons = [
            ("Editor", "💻"),
            ("Problemas", "📋"),
            ("Mi Progreso", "📊"),
            ("Ranking", "🏆"),
            ("Gestión Problemas", "🛠️"),
        ]

        self.nav_buttons = {}
        for text, icon in nav_buttons:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 15px;
                    font-size: 14px;
                    background-color: #2a2a35;
                    color: #ccc;
                }
                QPushButton:hover {
                    background-color: #3a3a45;
                }
                QPushButton:pressed {
                    background-color: #4a4a55;
                }
            """)
            layout.addWidget(btn)
            self.nav_buttons[text] = btn

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #444;")
        layout.addWidget(sep)

        # Sección de problemas
        self.problems_label = QLabel("PROBLEMAS")
        self.problems_label.setStyleSheet("color: #ccc; font-weight: bold;")
        layout.addWidget(self.problems_label)

        self.problems_list = QListWidget()
        self.problems_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1f;
                color: #ddd;
                border: none;
                padding: 6px;
            }
        """)
        layout.addWidget(self.problems_list)

        return sidebar

    def create_coding_environment(self):
        """Crea el entorno de programación - VERSIÓN CORREGIDA"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Barra de herramientas del editor - SOLO EJECUTAR Y REINICIAR
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #252530; border-radius: 4px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)

        self.run_btn = QPushButton("▶️ Ejecutar")
        self.run_btn.setFixedHeight(35)
        self.run_btn.setStyleSheet(self._button_style("#27ae60"))
        toolbar_layout.addWidget(self.run_btn)

        # ELIMINADO: Botón Enviar
        # ELIMINADO: Botón Guardar

        self.reset_btn = QPushButton("🔄 Reiniciar")
        self.reset_btn.setFixedHeight(35)
        self.reset_btn.setStyleSheet(self._button_style("#e74c3c"))
        toolbar_layout.addWidget(self.reset_btn)

        toolbar_layout.addStretch()

        lang_label = QLabel("Lenguaje: C++")
        lang_label.setStyleSheet("color: #ccc; padding: 8px;")
        toolbar_layout.addWidget(lang_label)

        layout.addWidget(toolbar)
        # Splitter principal vertical
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #444; }")

        # Editor de código
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText(
            "// Escribe tu solución en C++ aquí.\n"
            "#include <iostream>\n#include <vector>\n\nusing namespace std;\n\n"
            "class Solution {\npublic:\n    // Tu código aquí\n};"
        )
        self.code_editor.setStyleSheet("""
            QTextEdit {
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 13px;
                background-color: #1a1a1f;
                border: none;
                padding: 15px;
                color: #e0e0e0;
            }
        """)
        main_splitter.addWidget(self.code_editor)

        # Splitter horizontal para terminal y análisis de IA
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setStyleSheet("QSplitter::handle { background-color: #444; }")

        # Terminal de salida
        terminal_container = QWidget()
        terminal_layout = QVBoxLayout(terminal_container)
        terminal_layout.setContentsMargins(0, 0, 0, 0)

        terminal_header = QLabel("Terminal de Salida")
        terminal_header.setStyleSheet("""
            QLabel {
                background-color: #252530;
                color: #ccc;
                padding: 8px 15px;
                font-weight: bold;
                border-top: 1px solid #444;
            }
        """)
        terminal_layout.addWidget(terminal_header)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setPlaceholderText("Los resultados de ejecución aparecerán aquí.")
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                background-color: #1a1a1f;
                border: none;
                padding: 15px;
                color: #00ff00;
            }
        """)
        terminal_layout.addWidget(self.terminal_output)
        bottom_splitter.addWidget(terminal_container)

        # NUEVO: Panel de análisis de IA
        ai_container = QWidget()
        ai_layout = QVBoxLayout(ai_container)
        ai_layout.setContentsMargins(0, 0, 0, 0)

        ai_header = QLabel("🤖 Análisis de IA")
        ai_header.setStyleSheet("""
            QLabel {
                background-color: #252530;
                color: #ccc;
                padding: 8px 15px;
                font-weight: bold;
                border-top: 1px solid #444;
                border-left: 1px solid #444;
            }
        """)
        ai_layout.addWidget(ai_header)

        self.ai_feedback = QTextEdit()
        self.ai_feedback.setReadOnly(True)
        self.ai_feedback.setPlaceholderText("El análisis de IA aparecerá aquí después de ejecutar el código...")
        self.ai_feedback.setStyleSheet("""
            QTextEdit {
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                background-color: #1a1a1f;
                border: none;
                border-left: 1px solid #444;
                padding: 15px;
                color: #ffa500;
            }
        """)
        ai_layout.addWidget(self.ai_feedback)
        bottom_splitter.addWidget(ai_container)

        # Configurar tamaños del splitter horizontal
        bottom_splitter.setSizes([400, 400])

        # Agregar el splitter horizontal al vertical
        main_splitter.addWidget(bottom_splitter)

        # Configurar tamaños del splitter vertical
        main_splitter.setSizes([500, 200])
        layout.addWidget(main_splitter)

        return container

    def create_problems_section(self):
        """Crea la sección de problemas"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📋 Problemas de Práctica")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        desc = QLabel("Selecciona un problema de la lista en la barra lateral para comenzar a resolverlo.")
        desc.setStyleSheet("font-size: 16px; color: #ccc; margin-bottom: 30px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        problem_frame = QFrame()
        problem_frame.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
                padding: 20px;
            }
        """)
        problem_layout = QVBoxLayout(problem_frame)

        self.problem_section_title = QLabel("Selecciona un problema")
        self.problem_section_title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 15px;")
        problem_layout.addWidget(self.problem_section_title)

        self.problem_section_desc = QLabel(
            "Haz clic en un problema de la lista de la barra lateral "
            "para ver sus detalles completos aquí."
        )
        self.problem_section_desc.setStyleSheet("font-size: 14px; color: #ddd; line-height: 1.5;")
        self.problem_section_desc.setWordWrap(True)
        problem_layout.addWidget(self.problem_section_desc)

        layout.addWidget(problem_frame)
        layout.addStretch()

        return container

    def create_progress_section(self):
        """Crea la sección de Mi Progreso con datos REALES"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📊 Mi Progreso")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Botón para actualizar stats
        refresh_btn = QPushButton("🔄 Actualizar Estadísticas")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_user_stats)
        layout.addWidget(refresh_btn)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
                padding: 20px;
            }
        """)
        stats_layout = QGridLayout(stats_frame)

        # Cargar estadísticas
        self.progress_stats = self.load_user_progress_stats()

        # Mostrar estadísticas en una grid
        stats_data = [
            (self.progress_stats.get('Puntos Totales', '0'), "Puntos Totales", "#27ae60"),
            (self.progress_stats.get('Problemas Resueltos', '0'), "Problemas Resueltos", "#f39c12"),
            (self.progress_stats.get('Ejercicios Únicos', '0'), "Ejercicios Únicos", "#2980b9"),
            (self.progress_stats.get('Racha Actual', '0'), "Racha Actual", "#9b59b6"),
            (self.progress_stats.get('Mejor Racha', '0'), "Mejor Racha", "#e74c3c"),
            (self.progress_stats.get('Fácil Resueltos', '0'), "Fácil Resueltos", "#2ecc71"),
            (self.progress_stats.get('Medio Resueltos', '0'), "Medio Resueltos", "#f1c40f"),
            (self.progress_stats.get('Difícil Resueltos', '0'), "Difícil Resueltos", "#e74c3c")
        ]

        for i, (value, label, color) in enumerate(stats_data):
            stat_widget = QFrame()
            stat_widget.setStyleSheet("background-color: #1a1a1f; border-radius: 6px; padding: 15px;")
            stat_layout = QVBoxLayout(stat_widget)

            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setObjectName(f"stat_{label.replace(' ', '_')}")

            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 12px; color: #ccc;")
            label_label.setAlignment(Qt.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)

            stats_layout.addWidget(stat_widget, i // 4, i % 4)

        layout.addWidget(stats_frame)

        # Sección de ejercicios completados
        exercises_label = QLabel("📝 Ejercicios Completados")
        exercises_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff; margin-top: 20px;")
        layout.addWidget(exercises_label)

        self.completed_exercises_list = QListWidget()
        self.completed_exercises_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1f;
                color: #ddd;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.completed_exercises_list.setMaximumHeight(150)
        self.load_completed_exercises()
        layout.addWidget(self.completed_exercises_list)

        layout.addStretch()
        return container

    def create_ranking_section(self):
        """Crea la sección de Ranking"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🏆 Ranking Global")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        ranking_frame = QFrame()
        ranking_frame.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
                padding: 20px;
            }
        """)
        ranking_layout = QVBoxLayout(ranking_frame)

        # Obtener ranking real de la base de datos
        if self.db_handler:
            ranking_data = self.db_handler.get_global_ranking(limit=10)
        else:
            ranking_data = []

        if not ranking_data:
            # Datos de ejemplo si no hay conexión
            ranking_data = [
                {"posicion": 1, "username": "CodeMaster", "puntaje": 1250, "problemas": 45},
                {"posicion": 2, "username": "AlgoExpert", "puntaje": 1180, "problemas": 42},
                {"posicion": 3, "username": "PythonPro", "puntaje": 1120, "problemas": 38},
            ]

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        headers = ["Posición", "Usuario", "Puntaje", "Problemas"]
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1c40f; padding: 10px;")
            grid_layout.addWidget(header_label, 0, col)

        for row, user_data in enumerate(ranking_data, 1):
            position = user_data.get('posicion', row)
            username = user_data.get('username', 'N/A')
            score = user_data.get('puntaje', 0)
            problems = user_data.get('problemas', 0)

            # Emojis para las primeras posiciones
            if position == 1:
                position_str = "🥇 1"
            elif position == 2:
                position_str = "🥈 2"
            elif position == 3:
                position_str = "🥉 3"
            else:
                position_str = str(position)

            pos_label = QLabel(position_str)
            user_label = QLabel(username)
            score_label = QLabel(str(score))
            problems_label = QLabel(str(problems))

            for label in [pos_label, user_label, score_label, problems_label]:
                label.setStyleSheet("font-size: 14px; color: #ddd; padding: 8px;")

            if position <= 3:
                for label in [pos_label, user_label, score_label, problems_label]:
                    label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f1c40f; padding: 8px;")

            grid_layout.addWidget(pos_label, row, 0)
            grid_layout.addWidget(user_label, row, 1)
            grid_layout.addWidget(score_label, row, 2)
            grid_layout.addWidget(problems_label, row, 3)

        ranking_layout.addLayout(grid_layout)
        layout.addWidget(ranking_frame)
        layout.addStretch()

        return container

    def create_settings_section(self):
        """Crea la sección de Ajustes"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚙️ Ajustes")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
                padding: 20px;
            }
        """)
        settings_layout = QVBoxLayout(settings_frame)

        settings_options = [
            ("Tema", "Oscuro"),
            ("Lenguaje por defecto", "C++"),
            ("Tamaño de fuente", "Mediano"),
            ("Auto-guardado", "Activado"),
            ("Notificaciones", "Desactivadas")
        ]

        for setting, value in settings_options:
            setting_layout = QHBoxLayout()

            setting_label = QLabel(setting)
            setting_label.setStyleSheet("font-size: 16px; color: #fff;")

            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 16px; color: #ccc;")

            setting_layout.addWidget(setting_label)
            setting_layout.addStretch()
            setting_layout.addWidget(value_label)

            settings_layout.addLayout(setting_layout)

        layout.addWidget(settings_frame)
        layout.addStretch()

        return container

    def _button_style(self, color):
        """Devuelve stylesheet para botones con color dado"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """

    def diagnose_database(self):
        """Método temporal para diagnosticar la conexión a la base de datos"""
        print("\n=== DIAGNÓSTICO DE BASE DE DATOS ===")

        if not self.db_handler:
            print("❌ DatabaseHandler no está inicializado")
            return

        if not hasattr(self.db_handler, 'client') or not self.db_handler.client:
            print("❌ Cliente MongoDB no conectado")
            return

        print("✅ Cliente MongoDB conectado")

        try:
            databases = self.db_handler.client.list_database_names()
            print(f"📊 Bases de datos disponibles: {databases}")

            if 'codecoach_db' in databases:
                print("✅ codecoach_db encontrada")
                collections = self.db_handler.db.list_collection_names()
                print(f"📁 Colecciones en codecoach_db: {collections}")

                if 'problems' in collections:
                    count = self.db_handler.problems_collection.count_documents({})
                    print(f"📄 Número de problemas en la colección: {count}")

                    sample_problems = self.db_handler.problems_collection.find().limit(3)
                    print("🔍 Problemas de ejemplo:")
                    for problem in sample_problems:
                        print(f"   - {problem.get('title', 'Sin título')}")
                else:
                    print("❌ Colección 'problems' NO encontrada")
            else:
                print("❌ codecoach_db NO encontrada")

        except Exception as e:
            print(f"💥 Error durante diagnóstico: {e}")

        print("=== FIN DIAGNÓSTICO ===\n")

    def load_problems_into_sidebar(self):
        """Obtiene los títulos de la base de datos y los pone en self.problems_list"""
        if not self.db_handler:
            print("No hay manejador de base de datos.")
            self.problems_list.addItem("❌ No hay conexión a la base de datos")
            return

        problem_titles = self.db_handler.get_all_problem_titles()
        self.problems_list.clear()

        if problem_titles:
            self.problems_list.addItems(problem_titles)
            print(f"✅ {len(problem_titles)} problemas cargados en la barra lateral")
        else:
            self.problems_list.addItem("❌ No se pudieron cargar problemas")

    def display_problem_details(self, item):
        """Carga y muestra la descripción de un problema seleccionado"""
        problem_title = item.text()
        print(f"🎯 CARGANDO PROBLEMA: {problem_title}")

        if self.db_handler:
            problem_info = self.db_handler.get_problem_details(problem_title)
        else:
            problem_info = None

        if not problem_info:
            error_msg = f"Error: No se pudieron cargar los detalles del problema '{problem_title}'"
            print(f"❌ {error_msg}")
            self.show_output({"status": "error", "message": error_msg})
            return

        print(f"✅ Problema encontrado en MongoDB:")
        print(f"   - Título: {problem_info.get('title')}")
        print(f"   - Dificultad: {problem_info.get('difficulty')}")

        examples = problem_info.get('examples', [])
        print(f"   - Ejemplos para testing: {len(examples)}")

        self.current_problem_data = problem_info
        self.update_problem_display(problem_info)

        # ✅ NUEVO: Mostrar confirmación en terminal
        self.terminal_output.append(f"\n✅ Problema seleccionado: {problem_info.get('title')}")
        self.terminal_output.append(f"📊 Dificultad: {problem_info.get('difficulty')}")
        self.terminal_output.append("🎯 ¡Ahora puedes escribir y enviar tu solución!\n")

    def get_current_code(self):
        """Obtiene el código actual del editor"""
        if hasattr(self, 'code_editor'):
            return self.code_editor.toPlainText().strip()
        return ""

    def handle_ai_response(self, response):
        """Maneja la respuesta de la IA con mejor manejo de errores"""
        try:
            status = response.get('status')
            message = response.get('message', '')

            if status == 'success':
                feedback = response.get('feedback_completo', 'Sin feedback')
                formatted_feedback = self._format_ai_feedback(feedback)
                self.ai_feedback.setPlainText(formatted_feedback)

            elif status == 'timeout_error':
                self.ai_feedback.setPlainText(
                    "⏰ El servidor de IA está tardando demasiado\n\n"
                    "Esto puede pasar porque:\n"
                    "• El modelo de IA está cargando\n"
                    "• Tu código es muy largo\n"
                    "• El servidor está ocupado\n\n"
                    "Solución:\n"
                    "• Espera 1-2 minutos e intenta nuevamente\n"
                    "• Usa código más corto\n"
                    "• Reinicia el servidor de IA"
                )

            elif status == 'connection_error':
                self.ai_feedback.setPlainText(
                    "🔌 No se puede conectar al servidor de IA\n\n"
                    "Para solucionarlo:\n"
                    "1. Abre una terminal\n"
                    "2. Ejecuta: uvicorn analizador_api:app --reload --port 8000\n"
                    "3. Espera a que aparezca 'Application startup complete'\n"
                    "4. Vuelve a intentar\n\n"
                    "Si el problema persiste, reinicia la aplicación."
                )

            else:
                error_msg = response.get('message', 'Error desconocido')
                self.ai_feedback.setPlainText(
                    f"❌ Error en análisis de IA\n\n"
                    f"Detalles: {error_msg}\n\n"
                    f"Puedes intentar:\n"
                    f"• Reiniciar el servidor de IA\n"
                    f"• Verificar que analizador_api.py esté en la carpeta correcta\n"
                    f"• Revisar la consola para más detalles"
                )

        except Exception as e:
            self.ai_feedback.setPlainText(
                f"💥 Error crítico\n\n"
                f"No se pudo procesar la respuesta de IA:\n{str(e)}\n\n"
                f"Reinicia la aplicación y el servidor de IA."
            )

    def send_raw_cpp_code(self, codigo_cpp: str):
        """Envía el código C++ en bruto al servidor CON LOS DATOS REALES DE MONGODB"""
        try:
            print("🔄 Iniciando envío de código C++...")

            user_name = "Invitado"
            if hasattr(self, 'logged_in_user') and self.logged_in_user:
                user_name = getattr(self.logged_in_user, 'username', 'Invitado')

            print(f"👤 Usuario: {user_name}")
            print(f"📏 Longitud del código: {len(codigo_cpp)} caracteres")

            payload = self.create_payload_with_real_data(codigo_cpp, user_name)

            # ✅ NUEVA VALIDACIÓN: Si no hay payload, retornar error
            if payload is None:
                error_msg = "No se pudo crear el payload. Selecciona un problema de la lista."
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg
                }

            print(f"📦 Payload creado exitosamente:")
            print(f"   - Usuario: {payload.get('nombre', 'N/A')}")
            print(f"   - Problema: {payload.get('problem_title', 'N/A')}")

            if self.compiler_client:
                result = self.compiler_client.send_evaluation_package(payload)
                print(f"✅ Respuesta recibida: {result.get('status', 'unknown')}")
                return result
            else:
                return {
                    "status": "error",
                    "message": "Cliente de compilación no disponible"
                }

        except Exception as e:
            error_msg = f"💥 Error crítico en send_raw_cpp_code: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                "status": "critical_error",
                "message": error_msg
            }

    def show_output(self, result):
        """Muestra el resultado de la evaluación en la terminal y procesa para estadísticas"""

        # Extraer todos los campos de la nueva estructura
        status = result.get('status', 'unknown')
        summary = result.get('summary', 'No summary provided')
        passed_count = result.get('passed_count', 0)
        total_tests = result.get('total_tests', 0)
        score = result.get('score', 0)
        problem_solved = result.get('problem_solved', False)
        compilation_output = result.get('compilation_output', '')
        execution_output = result.get('execution_output', '')
        execution_time = result.get('execution_time_ms', 0)
        tests = result.get('tests', [])

        # Determinar color para la terminal
        if status == "success":
            color = "#00ff00"
        elif status in ["error", "compile_error", "runtime_error"]:
            color = "#ff0000"
        else:
            color = "#ffff00"

        # Construir display completo
        display_text = f"Estado: {status}\n"
        display_text += f"Resumen: {summary}\n"
        display_text += f"Puntaje: {score} puntos\n"
        display_text += f"Tiempo de ejecución: {execution_time}ms\n"
        display_text += f"Problema resuelto: {'Sí' if problem_solved else 'No'}\n\n"

        # Detalles de pruebas
        if tests:
            display_text += "Detalles de pruebas:\n"
            for test in tests:
                test_id = test.get('test_id', 'N/A')
                input_val = test.get('input', 'N/A')
                obtained = test.get('obtained', 'N/A')
                passed = test.get('passed', False)
                status_icon = "✅" if passed else "❌"
                display_text += f"  {status_icon} Prueba {test_id}: Input={input_val}, Obtenido={obtained}\n"

        # Información de compilación si hay error
        if compilation_output and status == "compile_error":
            display_text += f"\nSalida de compilación:\n{compilation_output}"

        # Actualizar interfaz
        self.terminal_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                background-color: #1a1a1f;
                border: none;
                padding: 15px;
                color: {color};
            }}
        """)

        self.terminal_output.setText(display_text)

        # Devolver estructura completa para uso externo
        return {
            'status': status,
            'summary': summary,
            'passed_count': passed_count,
            'total_tests': total_tests,
            'score': score,
            'problem_solved': problem_solved,
            'tests': tests,
            'execution_time': execution_time,
            'compilation_output': compilation_output,
            'execution_output': execution_output
        }

    def setup_default_code_template(self):
        """Pone un código C++ apropiado según el tipo de problema"""

        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            # Template genérico
            default_code = """#include <iostream>
    #include <vector>
    #include <string>
    using namespace std;

    // Escribe tu solución aquí

    int main() {
        // Ejemplo de uso
        cout << "Hello World" << endl;
        return 0;
    }"""
        else:
            problem_type = self.current_problem_data.get('function_type', 'string')

            if problem_type == "bool":
                default_code = """#include <iostream>
    #include <string>
    using namespace std;

    bool miFuncion(bool entrada) {
        // Tu lógica aquí
        // Retorna true (1) o false (0)
        return true; // ejemplo
    }

    int main() {
        // Ejemplo
        bool resultado = miFuncion(true);
        cout << (resultado ? "1" : "0") << endl;
        return 0;
    }"""
            elif problem_type == "int":
                default_code = """#include <iostream>
    using namespace std;

    int miFuncion(int entrada) {
        // Tu lógica aquí
        return entrada * 2; // ejemplo
    }

    int main() {
        // Ejemplo
        int resultado = miFuncion(5);
        cout << resultado << endl;
        return 0;
    }"""
            elif problem_type == "array":
                default_code = """#include <iostream>
    #include <vector>
    using namespace std;

    vector<int> miFuncion(vector<int> entrada) {
        // Tu lógica aquí
        return entrada; // ejemplo
    }

    int main() {
        // Ejemplo
        vector<int> input = {1, 2, 3};
        vector<int> resultado = miFuncion(input);

        // Mostrar resultado
        cout << "[";
        for (int i = 0; i < resultado.size(); i++) {
            cout << resultado[i];
            if (i < resultado.size() - 1) cout << ",";
        }
        cout << "]" << endl;

        return 0;
    }"""
            else:  # string
                default_code = """#include <iostream>
    #include <string>
    using namespace std;

    string miFuncion(string entrada) {
        // Tu lógica aquí
        return "Procesado: " + entrada; // ejemplo
    }

    int main() {
        // Ejemplo
        string resultado = miFuncion("Hola");
        cout << resultado << endl;
        return 0;
    }"""

        if hasattr(self, 'code_editor'):
            self.code_editor.setPlainText(default_code)
            self.code_base_loaded = True
            print("✅ Código template cargado según tipo de problema")

    def setup_actions(self):
        """CONECTA LOS BOTONES A SUS MÉTODOS CORRESPONDIENTES - VERSIÓN CORREGIDA"""
        print("🔗 Conectando botones...")

        # Conectar botones de ejecución (SOLO EJECUTAR)
        if hasattr(self, 'run_btn'):
            self.run_btn.clicked.connect(self.submit_code_for_evaluation)

        # ELIMINADO: Botón Enviar
        # ELIMINADO: Botón Guardar

        # Conectar botones de navegación
        if hasattr(self, 'nav_buttons'):
            for name, btn in self.nav_buttons.items():
                btn.clicked.connect(lambda checked=False, n=name: self.show_section(n))

        # Conectar botón de reinicio
        if hasattr(self, 'reset_btn'):
            self.reset_btn.clicked.connect(lambda: self.setup_default_code_template())

        print("✅ Todos los botones conectados correctamente")

    def load_user_progress_stats(self):
        """Carga las estadísticas REALES del usuario desde MongoDB"""
        if not hasattr(self, 'logged_in_user') or not self.logged_in_user:
            return {
                'Puntos Totales': '0',
                'Problemas Resueltos': '0',
                'Ejercicios Únicos': '0',
                'Racha Actual': '0',
                'Mejor Racha': '0',
                'Fácil Resueltos': '0',
                'Medio Resueltos': '0',
                'Difícil Resueltos': '0'
            }

        try:
            self.logged_in_user.refresh_stats()
            return self.logged_in_user.get_stats_for_display()
        except Exception as e:
            print(f"❌ Error cargando stats de usuario: {e}")
            return {
                'Puntos Totales': 'Error',
                'Problemas Resueltos': 'Error',
                'Ejercicios Únicos': 'Error',
                'Racha Actual': 'Error',
                'Mejor Racha': 'Error',
                'Fácil Resueltos': 'Error',
                'Medio Resueltos': 'Error',
                'Difícil Resueltos': 'Error'
            }

    def load_completed_exercises(self):
        """Carga la lista de ejercicios completados del usuario"""
        if not hasattr(self, 'logged_in_user') or not self.logged_in_user:
            self.completed_exercises_list.addItem("🔒 Inicia sesión para ver tu progreso")
            return

        try:
            self.completed_exercises_list.clear()
            exercises = getattr(self.logged_in_user, 'ejercicios_completados', [])

            if not exercises:
                self.completed_exercises_list.addItem("🎯 Aún no has completado ejercicios")
                return

            for exercise in exercises[:10]:
                self.completed_exercises_list.addItem(f"✅ {exercise}")

            if len(exercises) > 10:
                self.completed_exercises_list.addItem(f"... y {len(exercises) - 10} más")

        except Exception as e:
            print(f"❌ Error cargando ejercicios completados: {e}")
            self.completed_exercises_list.addItem("Error cargando ejercicios")

    def refresh_user_stats(self):
        """Actualiza las estadísticas en la GUI"""
        print("🔄 Actualizando estadísticas del usuario...")
        self.progress_stats = self.load_user_progress_stats()

        stats_mapping = {
            'Puntos_Totales': self.progress_stats.get('Puntos Totales', '0'),
            'Problemas_Resueltos': self.progress_stats.get('Problemas Resueltos', '0'),
            'Ejercicios_Únicos': self.progress_stats.get('Ejercicios Únicos', '0'),
            'Racha_Actual': self.progress_stats.get('Racha Actual', '0'),
            'Mejor_Racha': self.progress_stats.get('Mejor Racha', '0'),
            'Fácil_Resueltos': self.progress_stats.get('Fácil Resueltos', '0'),
            'Medio_Resueltos': self.progress_stats.get('Medio Resueltos', '0'),
            'Difícil_Resueltos': self.progress_stats.get('Difícil Resueltos', '0')
        }

        for stat_name, value in stats_mapping.items():
            label = self.findChild(QLabel, f"stat_{stat_name}")
            if label:
                label.setText(value)

        self.load_completed_exercises()
        print("✅ Estadísticas actualizadas en GUI")

    def update_user_progress_after_solution(self, problem_data):
        """Actualiza el progreso del usuario después de resolver un problema"""
        if not hasattr(self, 'logged_in_user') or not self.logged_in_user:
            print("❌ No hay usuario logueado para actualizar progreso")
            return False

        try:
            from logic.auth_logic import AuthManager
            auth_mgr = AuthManager()

            success, updated_user = auth_mgr.update_user_progress(
                self.logged_in_user.username,
                problem_data,
                points_earned=10
            )

            if success and updated_user:
                self.logged_in_user = updated_user
                print(f"✅ Progreso actualizado en MongoDB para {self.logged_in_user.username}")
                self.refresh_user_stats()
                return True
            else:
                print("❌ No se pudo actualizar el progreso en MongoDB")
                return False

        except Exception as e:
            print(f"❌ Error actualizando progreso: {e}")
            return False

    def submit_code_for_evaluation(self):
        """Envía código para evaluación y actualiza progreso si es exitoso"""
        codigo_cpp = self.get_current_code()
        if not codigo_cpp:
            self.show_output({"status": "error", "message": "El editor está vacío"})
            return

        # ✅ VALIDACIÓN MEJORADA: Verificar problema seleccionado
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            self.show_output({
                "status": "error",
                "message": "❌ Selecciona un problema de la lista antes de enviar\n\n" +
                           "📝 Pasos:\n" +
                           "1. Ve a la barra lateral izquierda\n" +
                           "2. Haz clic en un problema de la lista\n" +
                           "3. Espera a que carguen los detalles\n" +
                           "4. Vuelve a intentar enviar tu código"
            })
            return

        try:
            result = self.send_raw_cpp_code(codigo_cpp)
            detailed_result = self.show_output(result)

            # Actualizar MongoDB si la solución es correcta
            if detailed_result.get('problem_solved'):
                if hasattr(self, 'current_problem_data') and self.current_problem_data:
                    success = self.update_user_progress_after_solution(self.current_problem_data)
                    if success:
                        print("🎉 ¡Progreso guardado en MongoDB!")
                        score = detailed_result.get('score', 0)
                        print(f"📊 Puntaje obtenido: {score}")
                    else:
                        print("⚠️  Solución correcta pero no se pudo guardar el progreso")

            # Enviar a API de IA para retroalimentación
            self.send_to_ai_feedback(detailed_result, codigo_cpp)

        except Exception as e:
            print(f"Error en submit_code_for_evaluation: {e}")

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación - detiene el servidor de IA"""
        print("🔴 Cerrando aplicación...")
        self.stop_ai_server()
        super().closeEvent(event)

    def send_to_ai_feedback(self, detailed_result, user_code):
        """Envía código a IA integrando el formateo directamente"""
        try:
            # Verificar longitud del código
            current_code = self.get_current_code()
            if len(current_code) > 2000:
                self.ai_feedback.setPlainText("📝 Código demasiado largo para análisis.")
                return

            # Verificar si el servidor de IA está disponible
            if not self.ai_server_started:
                self.ai_feedback.setPlainText(" Iniciando servidor de IA...")
                if not self.start_ai_server():
                    self.ai_feedback.setPlainText(" No se pudo iniciar el servidor de IA")
                    return

            self.ai_feedback.setPlainText(" Analizando código con IA...")

            # Obtener enunciado
            problem_statement = ""
            if hasattr(self, 'current_problem_data') and self.current_problem_data:
                problem_statement = self.current_problem_data.get('statement', '')

            # --- CORRECCIÓN: FORMATEO INLINE (Sin llamar a la función vieja) ---
            # Convertimos el diccionario de resultados a un texto claro para la IA
            status = detailed_result.get('status', 'unknown')
            passed = detailed_result.get('passed_count', 0)
            total = detailed_result.get('total_tests', 0)

            eval_results_str = f"Estado: {status}\nPruebas: {passed}/{total}\n"

            if status == "compile_error":
                eval_results_str += f"\nERROR COMPILACIÓN:\n{detailed_result.get('compilation_output', '')}"
            elif status == "runtime_error":
                eval_results_str += f"\nERROR EJECUCIÓN:\n{detailed_result.get('execution_output', '')}"
            elif passed < total:
                # Agregar detalles de pruebas fallidas
                tests = detailed_result.get('tests', [])
                failed = [t for t in tests if not t.get('passed', False)]
                for f in failed[:2]:  # Solo las primeras 2 para no saturar
                    eval_results_str += f"\nFallo en Test: Input={f.get('input')} -> Obtenido={f.get('obtained')}"

            ai_data = self._create_enhanced_ai_prompt(current_code, problem_statement, eval_results_str)

            print(f" Solicitando análisis de IA...")

            # Enviar a IA
            self.ai_thread = AIAnalysisThread(self.ai_api_url, ai_data)
            self.ai_thread.analysis_complete.connect(self.handle_ai_response)
            self.ai_thread.start()

        except Exception as e:
            self.ai_feedback.setPlainText(f" Error preparando datos IA: {str(e)}")
            import traceback
            traceback.print_exc()

    def send_to_ai_feedback_fast(self, detailed_result, user_code):
        """Versión rápida para análisis de IA con formateo integrado"""
        try:
            if not self.check_ai_server_quick():
                self.ai_feedback.setPlainText("🤖 Servidor IA no disponible para análisis rápido.")
                return

            current_code = self.get_current_code()
            self.ai_feedback.setPlainText("🔄 Analizando código (modo rápido)...")

            # Preparar datos
            problem_statement = ""
            if hasattr(self, 'current_problem_data') and self.current_problem_data:
                problem_statement = self.current_problem_data.get('statement', '')

            # --- CORRECCIÓN: FORMATEO INLINE ---
            status = detailed_result.get('status', 'unknown')
            eval_results_str = f"Estado: {status}\n"
            if status == "compile_error":
                eval_results_str += f"Error: {detailed_result.get('compilation_output', '')}"
            elif status == "runtime_error":
                eval_results_str += f"Error: {detailed_result.get('execution_output', '')}"
            # -----------------------------------

            # Usamos la estructura nueva directamente
            ai_data = {
                "codigo_usuario": current_code,
                "resultados_evaluacion": eval_results_str,
                "problema_enunciado": problem_statement,
                "lenguaje": "C++",
                "instrucciones_especificas": "Análisis rápido: Identifica el error principal brevemente."
            }

            # Enviar con timeout corto
            try:
                response = requests.post(
                    "http://localhost:8000/analyze_solution",
                    json=ai_data,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        self.ai_feedback.setPlainText(result.get('feedback_completo', 'Análisis completado'))
                else:
                    self.ai_feedback.setPlainText("🔌 Error conectando con IA")

            except Exception:
                self.ai_feedback.setPlainText("⏰ Timeout o error de conexión")

        except Exception as e:
            self.ai_feedback.setPlainText(f"💥 Error: {str(e)}")

    def handle_ai_response(self, response):
        """Maneja la respuesta de la IA de manera simple"""
        try:
            if response.get('status') == 'success':
                feedback = response.get('feedback_completo', 'Sin feedback')
                formatted_feedback = self._format_ai_feedback(feedback)
                self.ai_feedback.setPlainText(formatted_feedback)
            else:
                error_msg = response.get('message', 'Error desconocido')
                self.ai_feedback.setPlainText(f"❌ Error de IA: {error_msg}")

        except Exception as e:
            self.ai_feedback.setPlainText(f"❌ Error procesando respuesta: {str(e)}")

    def _format_ai_feedback(self, feedback):
        """Formatea el feedback de IA para mejor legibilidad"""
        if not feedback:
            return "🤖 No se recibió análisis de IA."

        # Si ya está bien formateado, mantenerlo
        if any(emoji in feedback for emoji in ["✅", "🔧", "⚡", "🎯", "💡", "📊"]):
            return feedback

        # Convertir feedback simple en formato estructurado
        lines = [line.strip() for line in feedback.split('\n') if line.strip()]

        if len(lines) <= 2:
            return f"💡 **Análisis:**\n\n{feedback}"

        # Agrupar por categorías detectadas
        sections = []
        current_section = []

        for line in lines:
            if line.startswith(('•', '-', '*')) or any(
                    keyword in line.lower() for keyword in ['sugerencia', 'revisa', 'verifica', 'considera']):
                if current_section:
                    sections.append(current_section)
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append(current_section)

        # Formatear secciones
        formatted = []
        for section in sections:
            if section:
                header = section[0]
                if any(keyword in header.lower() for keyword in ['complejidad', 'eficiencia']):
                    formatted.append(f"📊 {header}")
                elif any(keyword in header.lower() for keyword in ['pista', 'sugerencia']):
                    formatted.append(f"💡 {header}")
                else:
                    formatted.append(f"🔍 {header}")

                for item in section[1:]:
                    formatted.append(f"   {item}")

        return "\n".join(formatted) if formatted else feedback


    def update_problem_display(self, problem_info):
        """Actualiza la visualización del problema en la GUI"""
        title = problem_info.get('title', 'Sin título')
        statement = problem_info.get('statement', 'Descripción no disponible.')
        difficulty = problem_info.get('difficulty', 'Desconocida')
        category = problem_info.get('category', 'Sin categoría')
        big_o = problem_info.get('big_o_expected', 'No especificado')

        description_html = f"""
        <div style="color: #ddd; line-height: 1.6;">
            <p><b>Dificultad:</b> {difficulty}</p>
            <p><b>Categoría:</b> {category}</p>
            <p><b>Complejidad Esperada:</b> {big_o}</p>
            <p><b>Enunciado:</b> {statement}</p>
        """

        examples = problem_info.get('examples', [])
        if examples:
            description_html += "<p><b>Ejemplos para testing:</b></p>"
            for i, example in enumerate(examples, 1):
                input_raw = example.get('input_raw', 'N/A')
                output_raw = example.get('output_raw', 'N/A')
                explanation = example.get('explanation', '')

                description_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: #1a1a1f; border-radius: 5px;">
                    <b>Ejemplo {i}:</b><br>
                    <b>Input:</b> {input_raw}<br>
                    <b>Output esperado:</b> {output_raw}<br>
                    <b>Explicación:</b> {explanation}
                </div>
                """

        description_html += "</div>"

        self.problem_section_title.setText(title)
        self.problem_section_desc.setText(description_html)

    def _create_enhanced_ai_prompt(self, current_code, problem_statement, eval_results):
        """Crea el payload para el análisis inteligente"""

        ai_data = {
            "codigo_usuario": current_code,
            "resultados_evaluacion": eval_results,
            "problema_enunciado": problem_statement,
            "lenguaje": "C++",
            "instrucciones_especificas": """
            Analiza este código C++ y proporciona:
            1. COMPLEJIDAD: Análisis de complejidad algorítmica en notación Big O
            2. PISTAS: Si hay errores, da pistas específicas para corregirlos (NO soluciones completas)
            3. RECOMENDACIONES: Sugerencias para mejorar la eficiencia o estilo
            4. SÉ PRÁCTICO: Enfócate en ayudar a entender, no en dar la respuesta
            """
        }

        return ai_data


    def check_ai_server_quick(self):
        """Verificación rápida del servidor IA"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def create_payload_with_real_data(self, codigo_cpp: str, user_name: str):
        """Crea el payload usando los datos REALES del problema actual desde MongoDB"""
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            error_msg = "❌ No hay problema seleccionado para crear el payload"
            print(error_msg)
            return None

        problem_data = self.current_problem_data
        examples = problem_data.get('examples', [])

        print(f"🔍 Extrayendo datos REALES del problema: {problem_data.get('title', 'N/A')}")
        print(f"   - Número de ejemplos encontrados: {len(examples)}")

        # ✅ CORREGIDO: Obtener function_type con valor por defecto
        function_type = problem_data.get('function_type', 'string')
        function_name = problem_data.get('function_name', problem_data.get('title', 'solution'))

        print(f"   - Function Type: {function_type}")
        print(f"   - Function Name: {function_name}")

        # Construir payload con TODOS los datos reales
        payload = {
            "nombre": user_name,
            "codigo": codigo_cpp,
            "problem_title": problem_data.get('title', 'Problema sin título'),
            "function_name": function_name,
            "function_type": function_type,  # ✅ SIEMPRE INCLUIR
            "difficulty": problem_data.get('difficulty', 'Desconocida'),
            "category": problem_data.get('category', 'Sin categoría'),
            "statement": problem_data.get('statement', 'Sin descripción'),
            "big_o_expected": problem_data.get('big_o_expected', 'O(n)')
        }

        # Agregar todos los ejemplos disponibles
        for i, example in enumerate(examples, 1):
            input_key = f"input{i}"
            output_key = f"output_esperado{i}"

            input_val = example.get('input_raw', '')
            output_val = example.get('output_raw', '')

            payload[input_key] = input_val
            payload[output_key] = output_val

            print(f"   - Ejemplo {i}: Input='{input_val}', Output='{output_val}'")

        return payload


    # Añadir después de create_settings_section() en AuxCreator.py


    def create_problem_management_section(self):
        """Crea la sección de gestión de problemas"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🛠️ Gestión de Problemas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Pestañas para diferentes modos
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #252530;
            }
            QTabBar::tab {
                background-color: #2a2a35;
                color: #ccc;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #fff;
            }
        """)

        # Pestaña de formulario
        form_tab = self.create_problem_form_tab()
        tab_widget.addTab(form_tab, "📝 Formulario")

        # Pestaña de JSON
        json_tab = self.create_json_upload_tab()
        tab_widget.addTab(json_tab, "📁 Cargar JSON")

        # Pestaña de documentación
        docs_tab = self.create_documentation_tab()
        tab_widget.addTab(docs_tab, "📚 Cómo Usar")

        layout.addWidget(tab_widget)
        return container




    def create_json_upload_tab(self):
        """Crea la pestaña para cargar JSON"""
        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("📁 Cargar Problema desde JSON")
        title.setStyleSheet("font-size: 18px; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Área para pegar JSON
        self.json_editor = QTextEdit()
        self.json_editor.setPlaceholderText("Pega aquí tu JSON o usa el botón para cargar archivo...")
        self.json_editor.setStyleSheet("""
            QTextEdit {
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                background-color: #1a1a1f;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 10px;
                color: #e0e0e0;
            }
        """)
        layout.addWidget(self.json_editor)

        # Botones
        buttons_layout = QHBoxLayout()

        load_file_btn = QPushButton("📂 Cargar Archivo JSON")
        load_file_btn.setStyleSheet(self._button_style("#f39c12"))
        load_file_btn.clicked.connect(self.load_json_file)

        validate_btn = QPushButton("🔍 Validar JSON")
        validate_btn.setStyleSheet(self._button_style("#3498db"))
        validate_btn.clicked.connect(self.validate_json)

        submit_json_btn = QPushButton("🚀 Subir JSON")
        submit_json_btn.setStyleSheet(self._button_style("#27ae60"))
        submit_json_btn.clicked.connect(self.submit_json_problem)

        buttons_layout.addWidget(load_file_btn)
        buttons_layout.addWidget(validate_btn)
        buttons_layout.addWidget(submit_json_btn)
        layout.addLayout(buttons_layout)

        # Estado
        self.json_status = QLabel("")
        self.json_status.setStyleSheet("color: #ccc; padding: 10px;")
        layout.addWidget(self.json_status)

        layout.addStretch()
        return container


    def create_documentation_tab(self):
        """Crea la pestaña de documentación"""
        container = QWidget()
        layout = QVBoxLayout(container)

        doc_text = QTextEdit()
        doc_text.setReadOnly(True)
        doc_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1f;
                color: #ddd;
                border: none;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        doc_text.setHtml(self.get_documentation_html())
        layout.addWidget(doc_text)

        return container


    def get_documentation_html(self):
        """Retorna el HTML formateado para la documentación"""
        return """
        <h1 style="color: #3498db;">📚 Guía de Uso - leetAI</h1>
    
        <h2 style="color: #f39c12;">🚀 Cómo Subir Problemas</h2>
    
        <h3 style="color: #2ecc71;">📝 Usando el Formulario</h3>
        <ul>
            <li><b>Título:</b> Nombre único del problema (ej: "suma_dos_numeros")</li>
            <li><b>Categoría:</b> Área del problema</li>
            <li><b>Dificultad:</b> Fácil, Medio o Difícil</li>
            <li><b>Tipos de Entrada/Salida:</b> Solo los tipos soportados (ver abajo)</li>
            <li><b>Enunciado:</b> Descripción clara del problema</li>
            <li><b>Ejemplos:</b> Mínimo 1 ejemplo de input/output</li>
        </ul>
    
        <h3 style="color: #2ecc71;">📁 Usando JSON</h3>
        <pre style="background: #252530; padding: 15px; border-radius: 5px; color: #e0e0e0;">
    {
      "title": "suma_basica",
      "category": "Matemáticas",
      "difficulty": "Fácil", 
      "statement": "Dado un número entero n, retorna n+1.",
      "input_type": "int",
      "output_type": "int",
      "examples": [
        {
          "input_raw": "5",
          "output_raw": "6"
        }
      ],
      "big_o_expected": "O(1)"
    }</pre>
    
        <h2 style="color: #f39c12;">✅ Tipos de Datos Soportados</h2>
        <ul>
            <li><code>bool</code> - Valores true/false</li>
            <li><code>int</code> - Números enteros</li>
            <li><code>double</code> - Números decimales</li>
            <li><code>string</code> - Cadenas de texto</li>
            <li><code>char</code> - Caracteres individuales</li>
            <li><code>vector&lt;int&gt;</code> - Arrays de enteros</li>
            <li><code>list&lt;int&gt;</code> - Listas enlazadas de enteros</li>
        </ul>
    
        <h2 style="color: #f39c12;">❌ Limitaciones del Runner</h2>
        <ul>
            <li><b>1 parámetro máximo</b> por función</li>
            <li><b>NO soportados:</b> struct, class, map, set, templates</li>
            <li><b>NO referencias:</b> Solo paso por valor</li>
            <li><b>Timeout:</b> 2 segundos máximo</li>
            <li><b>Sin recursión compleja</b> ni lambdas</li>
            <li><b>Bibliotecas prohibidas:</b> filesystem, network, concurrencia</li>
        </ul>
    
        <h2 style="color: #f39c12;">💡 Consejos para Soluciones</h2>
        <ul>
            <li><b>Nombre de función:</b> Usa EXACTAMENTE el nombre especificado en el problema</li>
            <li>Incluye <code>#include</code> necesarios</li>
            <li>Prueba con los ejemplos antes de enviar</li>
            <li>Considera casos edge (valores límite)</li>
            <li><b>Caracteres permitidos en nombres:</b> letras, números, _ (sin espacios)</li>
        </ul>
                <h2 style="color: #f39c12;">🤖 Análisis de IA</h2>
        <p>El sistema de IA te proporcionará <b>pistas prácticas</b> para mejorar tu código:</p>
        <ul>
            <li>🔧 <b>Errores de compilación:</b> Sugerencias de sintaxis y includes</li>
            <li>⚡ <b>Errores de ejecución:</b> Pistas sobre bucles y memoria</li>
            <li>🎯 <b>Pruebas fallidas:</b> Consejos de lógica y casos extremos</li>
            <li>💡 <b>Análisis general:</b> Mejoras de estilo y eficiencia</li>
        </ul>
        <p><i>La IA da pistas, no soluciones completas. ¡Aprende resolviendo!</i></p>
            """


    def load_json_file(self):
        """Carga un archivo JSON y lo muestra en el editor"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo JSON", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.json_editor.setPlainText(content)
                    self.json_status.setText("✅ Archivo cargado correctamente")
                    self.json_status.setStyleSheet("color: #27ae60;")
            except Exception as e:
                self.json_status.setText(f"❌ Error cargando archivo: {str(e)}")
                self.json_status.setStyleSheet("color: #e74c3c;")


    def validate_json(self):
        """Valida el JSON ingresado"""
        try:
            json_text = self.json_editor.toPlainText().strip()
            if not json_text:
                self.json_status.setText("❌ JSON vacío")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return False

            problem_data = json.loads(json_text)

            # Validar campos requeridos
            required_fields = ["title", "category", "difficulty", "statement",
                               "input_type", "output_type", "examples"]
            for field in required_fields:
                if field not in problem_data:
                    self.json_status.setText(f"❌ Campo requerido faltante: {field}")
                    self.json_status.setStyleSheet("color: #e74c3c;")
                    return False

            # Validar tipos soportados
            supported_types = ["bool", "int", "double", "string", "char", "vector<int>", "list<int>"]
            if problem_data["input_type"] not in supported_types:
                self.json_status.setText(f"❌ Tipo de entrada no soportado: {problem_data['input_type']}")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return False

            if problem_data["output_type"] not in supported_types:
                self.json_status.setText(f"❌ Tipo de salida no soportado: {problem_data['output_type']}")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return False
            # ✅ NUEVO: Validar nombre de función en JSON
            if "function_name" not in problem_data:
                self.json_status.setText("❌ Campo requerido faltante: function_name")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return False

            function_name = problem_data["function_name"]
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', function_name):
                self.json_status.setText("❌ Nombre de función inválido. Solo letras, números y _")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return False
            self.json_status.setText("✅ JSON válido - Listo para subir")
            self.json_status.setStyleSheet("color: #27ae60;")
            return True

        except json.JSONDecodeError as e:
            self.json_status.setText(f"❌ JSON inválido: {str(e)}")
            self.json_status.setStyleSheet("color: #e74c3c;")
            return False
        except Exception as e:
            self.json_status.setText(f"❌ Error validando JSON: {str(e)}")
            self.json_status.setStyleSheet("color: #e74c3c;")
            return False

    def create_problem_form_tab(self):
        """Crea el formulario para subir problemas - CON NOMBRE DE FUNCIÓN PERSONALIZABLE"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # PRIMERO crear form_status ANTES de cualquier uso
        self.form_status = QLabel("Complete todos los campos requeridos (*)")
        self.form_status.setStyleSheet("color: #ccc; padding: 10px; background-color: #2a2a35; border-radius: 4px;")
        self.form_status.setWordWrap(True)

        # Formulario con validación
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Campos del formulario
        self.form_title = QLineEdit()
        self.form_title.setPlaceholderText("ej: suma_dos_numeros")

        self.form_category = QComboBox()
        self.form_category.addItems(["Matemáticas", "Algoritmos", "Estructuras de Datos", "Cadenas", "Arrays", "Otros"])

        self.form_difficulty = QComboBox()
        self.form_difficulty.addItems(["Fácil", "Medio", "Difícil"])

        self.form_input_type = QComboBox()
        self.form_input_type.addItems(["bool", "int", "double", "string", "char", "vector<int>", "list<int>"])

        self.form_output_type = QComboBox()
        self.form_output_type.addItems(["bool", "int", "double", "string", "char", "vector<int>", "list<int>"])

        # ✅ NUEVO: Campo para nombre de función personalizado
        self.form_function_name = QLineEdit()
        self.form_function_name.setPlaceholderText("solution")
        self.form_function_name.setText("solution")  # Valor por defecto

        # Validador para solo letras, números y _
        validator = QRegExpValidator(QRegExp("[a-zA-Z_][a-zA-Z0-9_]*"))
        self.form_function_name.setValidator(validator)

        self.form_statement = QTextEdit()
        self.form_statement.setMaximumHeight(120)
        self.form_statement.setPlaceholderText("Describe el problema claramente...")

        # Big O como ComboBox
        self.form_big_o = QComboBox()
        self.form_big_o.addItems(["O(1)", "O(n)", "O(n^2)", "O(log n)", "O(n log n)", "O(2^n)"])
        self.form_big_o.setCurrentText("O(n)")

        # Ejemplos dinámicos - CON MÍNIMO 2 Y MÁXIMO 3
        examples_label = QLabel("Ejemplos (Mínimo 2, Máximo 3):")
        examples_label.setStyleSheet("color: #fff; font-weight: bold;")
        form_layout.addRow(examples_label)

        self.examples_widget = QWidget()
        self.examples_layout = QVBoxLayout(self.examples_widget)
        self.examples_list = []

        add_example_btn = QPushButton("➕ Agregar Ejemplo")
        add_example_btn.setStyleSheet(self._button_style("#27ae60"))
        add_example_btn.clicked.connect(self.add_example_field)

        # Añadir campos al formulario
        form_layout.addRow("Título*:", self.form_title)
        form_layout.addRow("Categoría*:", self.form_category)
        form_layout.addRow("Dificultad*:", self.form_difficulty)
        form_layout.addRow("Tipo de Entrada*:", self.form_input_type)
        form_layout.addRow("Tipo de Salida*:", self.form_output_type)
        form_layout.addRow("Nombre de Función*:", self.form_function_name)  # ✅ NUEVO CAMPO
        form_layout.addRow("Enunciado*:", self.form_statement)
        form_layout.addRow("Complejidad Esperada*:", self.form_big_o)
        form_layout.addRow(add_example_btn)
        form_layout.addRow(self.examples_widget)

        layout.addWidget(form_widget)

        # Añadir 2 ejemplos por defecto
        self.add_initial_examples()

        # Botón de enviar
        submit_btn = QPushButton("🚀 Subir Problema a MongoDB")
        submit_btn.setFixedHeight(45)
        submit_btn.setStyleSheet(self._button_style("#2980b9"))
        submit_btn.clicked.connect(self.submit_problem_form)
        layout.addWidget(submit_btn)

        # FINALMENTE añadir form_status al layout
        layout.addWidget(self.form_status)

        layout.addStretch()
        return container

    def remove_example_field(self, widget):
        """Elimina un campo de ejemplo - CON LÍMITE MÍNIMO"""
        if len(self.examples_list) <= 2:
            self.form_status.setText("❌ Mínimo 2 ejemplos requeridos")
            self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
            return

        for i, (input_edit, output_edit, remove_btn, example_widget) in enumerate(self.examples_list):
            if example_widget == widget:
                self.examples_list.pop(i)
                break

        widget.deleteLater()
        self.update_examples_count()


    def update_examples_count(self):
        """Actualiza el contador de ejemplos"""
        count = len(self.examples_list)
        if count < 2:
            self.form_status.setText(f"❌ Necesitas {2 - count} ejemplo(s) más (mínimo 2)")
            self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
        elif count == 2:
            self.form_status.setText("✅ Mínimo de ejemplos alcanzado. Puedes añadir 1 más si lo deseas.")
            self.form_status.setStyleSheet("color: #27ae60; background-color: #2a2a35;")
        else:
            self.form_status.setText("✅ Máximo de ejemplos alcanzado (3)")
            self.form_status.setStyleSheet("color: #27ae60; background-color: #2a2a35;")

    def submit_problem_form(self):
        """Envía el problema desde el formulario a MongoDB - VERSIÓN CORREGIDA"""
        try:
            print("🚀 INICIANDO SUBIDA DE PROBLEMA...")

            # Validar campos requeridos
            if not self.form_title.text().strip():
                self.form_status.setText("❌ El título es requerido")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            if not self.form_statement.toPlainText().strip():
                self.form_status.setText("❌ El enunciado es requerido")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            # Validar que haya exactamente 2 o 3 ejemplos VÁLIDOS
            valid_examples = []
            for input_edit, output_edit, _, _ in self.examples_list:
                input_val = input_edit.text().strip()
                output_val = output_edit.text().strip()
                if input_val and output_val:
                    valid_examples.append({
                        "input_raw": input_val,
                        "output_raw": output_val
                    })
            # ✅ NUEVO: Validar nombre de función
            function_name = self.form_function_name.text().strip()
            if not function_name:
                self.form_status.setText("❌ El nombre de la función es requerido")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            # Validar que solo contenga caracteres permitidos
            import re
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', function_name):
                self.form_status.setText("❌ Nombre de función inválido. Solo letras, números y _")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            if len(valid_examples) < 2:
                self.form_status.setText("❌ Se requieren al menos 2 ejemplos válidos")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            if len(valid_examples) > 3:
                self.form_status.setText("❌ Máximo 3 ejemplos permitidos")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
                return

            # ✅ CORREGIDO: Incluir nombre de función personalizado
            function_name = self.form_function_name.text().strip()
            statement_text = self.form_statement.toPlainText().strip()

            # Añadir instrucción sobre el nombre de función al statement
            full_statement = f"{statement_text}\n\nLa función debe llamarse: {function_name}"

            problem_data = {
                "title": self.form_title.text().strip(),
                "category": self.form_category.currentText(),
                "difficulty": self.form_difficulty.currentText(),
                "statement": full_statement,  # ✅ Statement con nombre de función
                "input_type": self.form_input_type.currentText(),
                "output_type": self.form_output_type.currentText(),
                "function_type": self.form_output_type.currentText(),
                "function_name": function_name,  # ✅ Nombre personalizado
                "examples": valid_examples,
                "big_o_expected": self.form_big_o.currentText(),
                "run_timeout_s": 2
            }

            print(f"📦 Problema construido:")
            print(f"   - Título: {problem_data['title']}")
            print(f"   - Ejemplos: {len(problem_data['examples'])}")
            print(f"   - Tipo función: {problem_data['function_type']}")

            # Insertar en MongoDB
            if self.db_handler and hasattr(self.db_handler, 'insert_problem'):
                self.form_status.setText("🔄 Conectando con MongoDB...")
                self.form_status.setStyleSheet("color: #f39c12; background-color: #2a2a35;")

                # Forzar actualización de la GUI
                QApplication.processEvents()

                success = self.db_handler.insert_problem(problem_data)
                if success:
                    self.form_status.setText("✅ Problema subido correctamente a MongoDB")
                    self.form_status.setStyleSheet("color: #27ae60; background-color: #2a2a35;")

                    # Limpiar formulario
                    self.form_title.clear()
                    self.form_function_name.setText("solution")
                    self.form_statement.clear()
                    self.form_big_o.setCurrentIndex(0)

                    # Limpiar ejemplos pero mantener 2 vacíos
                    for i in reversed(range(self.examples_layout.count())):
                        widget = self.examples_layout.itemAt(i).widget()
                        if widget:
                            widget.deleteLater()
                    self.examples_list = []

                    # Añadir 2 ejemplos vacíos por defecto
                    self.add_initial_examples()

                    # ✅ ACTUALIZAR LISTA EN SIDEBAR INMEDIATAMENTE
                    self.load_problems_into_sidebar()
                    print("🔄 Lista de problemas actualizada en sidebar")

                else:
                    self.form_status.setText("❌ Error insertando en la base de datos. Verifica la consola.")
                    self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
            else:
                self.form_status.setText("❌ No hay conexión a la base de datos")
                self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")

        except Exception as e:
            error_msg = f"❌ Error crítico subiendo problema: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.form_status.setText(error_msg)
            self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")

    def submit_json_problem(self):
        """Envía el problema desde JSON a MongoDB - VERSIÓN CORREGIDA"""
        if not self.validate_json():
            return

        try:
            json_text = self.json_editor.toPlainText().strip()
            problem_data = json.loads(json_text)

            # ✅ CORREGIDO: Asegurar estructura compatible
            required_fields = ["title", "category", "difficulty", "statement",
                               "input_type", "output_type", "examples"]

            for field in required_fields:
                if field not in problem_data:
                    self.json_status.setText(f"❌ Campo requerido faltante: {field}")
                    self.json_status.setStyleSheet("color: #e74c3c;")
                    return

            # Asegurar campos de compatibilidad con runner
            if "function_type" not in problem_data:
                problem_data["function_type"] = problem_data["output_type"]

            if "function_name" not in problem_data:
                problem_data["function_name"] = "solution"

            # Validar número de ejemplos
            if len(problem_data["examples"]) < 2 or len(problem_data["examples"]) > 3:
                self.json_status.setText("❌ Debe haber entre 2 y 3 ejemplos")
                self.json_status.setStyleSheet("color: #e74c3c;")
                return

            print(f"📦 JSON validado - Insertando en MongoDB...")
            print(f"   - Título: {problem_data['title']}")
            print(f"   - Ejemplos: {len(problem_data['examples'])}")

            # Insertar en MongoDB
            if self.db_handler and hasattr(self.db_handler, 'insert_problem'):
                self.json_status.setText("🔄 Insertando en MongoDB...")
                self.json_status.setStyleSheet("color: #f39c12;")

                QApplication.processEvents()  # Forzar actualización

                success = self.db_handler.insert_problem(problem_data)
                if success:
                    self.json_status.setText("✅ Problema subido correctamente a MongoDB")
                    self.json_status.setStyleSheet("color: #27ae60;")
                    self.json_editor.clear()

                    # ✅ ACTUALIZAR LISTA INMEDIATAMENTE
                    self.load_problems_into_sidebar()
                    print("✅ Lista de problemas actualizada")

                else:
                    self.json_status.setText("❌ Error insertando en MongoDB (ver consola)")
                    self.json_status.setStyleSheet("color: #e74c3c;")
            else:
                self.json_status.setText("❌ No hay conexión a la base de datos")
                self.json_status.setStyleSheet("color: #e74c3c;")

        except Exception as e:
            error_msg = f"❌ Error subiendo problema: {str(e)}"
            print(error_msg)
            self.json_status.setText(error_msg)
            self.json_status.setStyleSheet("color: #e74c3c;")

    def add_initial_examples(self):
        """Añade 2 ejemplos iniciales por defecto - SIN ACTUALIZAR ESTADO INICIAL"""
        for i in range(2):
            self.add_example_field_silent()

        # Solo actualizar el estado después de crear todos los ejemplos
        self.update_examples_count()

    def add_example_field_silent(self):
        """Versión silenciosa de add_example_field para inicialización"""
        if len(self.examples_list) >= 3:
            return

        example_widget = QWidget()
        example_layout = QHBoxLayout(example_widget)

        input_edit = QLineEdit()
        input_edit.setPlaceholderText("Input (ej: 5, 'hola', [1,2,3])")

        output_edit = QLineEdit()
        output_edit.setPlaceholderText("Output esperado")

        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(30, 30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        example_layout.addWidget(QLabel("Input:"))
        example_layout.addWidget(input_edit)
        example_layout.addWidget(QLabel("Output:"))
        example_layout.addWidget(output_edit)
        example_layout.addWidget(remove_btn)

        self.examples_layout.addWidget(example_widget)
        self.examples_list.append((input_edit, output_edit, remove_btn, example_widget))

        remove_btn.clicked.connect(lambda: self.remove_example_field(example_widget))

    def add_example_field(self):
        """Añade campos para un nuevo ejemplo - CON LÍMITE MÁXIMO"""
        if len(self.examples_list) >= 3:
            self.form_status.setText("❌ Máximo 3 ejemplos permitidos")
            self.form_status.setStyleSheet("color: #e74c3c; background-color: #2a2a35;")
            return

        example_widget = QWidget()
        example_layout = QHBoxLayout(example_widget)

        input_edit = QLineEdit()
        input_edit.setPlaceholderText("Input (ej: 5, 'hola', [1,2,3])")

        output_edit = QLineEdit()
        output_edit.setPlaceholderText("Output esperado")

        remove_btn = QPushButton("❌")
        remove_btn.setFixedSize(30, 30)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        example_layout.addWidget(QLabel("Input:"))
        example_layout.addWidget(input_edit)
        example_layout.addWidget(QLabel("Output:"))
        example_layout.addWidget(output_edit)
        example_layout.addWidget(remove_btn)

        self.examples_layout.addWidget(example_widget)
        self.examples_list.append((input_edit, output_edit, remove_btn, example_widget))

        remove_btn.clicked.connect(lambda: self.remove_example_field(example_widget))

        # Actualizar estado
        self.update_examples_count()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())