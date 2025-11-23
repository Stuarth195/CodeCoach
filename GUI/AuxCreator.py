# AuxCreator.py - VENTANA PRINCIPAL COMPLETA
import sys
import os
import threading
# Añadir después de las importaciones existentes
import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal
# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
                             QListWidget, QLabel, QPushButton, QSplitter,
                             QFrame, QProgressBar, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QFontDatabase

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
import subprocess
import time
import threading
from PyQt5.QtCore import QProcess


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
        self.ai_server_started = False  # No iniciar automáticamente

        # REMOVER esta línea: self.start_ai_server()

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
        """Crea el QStackedWidget para manejar las diferentes secciones"""
        self.stacked_widget = QStackedWidget()

        # Crear todas las secciones
        self.editor_section = self.create_coding_environment()
        self.problems_section = self.create_problems_section()
        self.progress_section = self.create_progress_section()
        self.ranking_section = self.create_ranking_section()
        self.settings_section = self.create_settings_section()

        # Agregar secciones al stacked widget
        self.stacked_widget.addWidget(self.editor_section)  # Índice 0
        self.stacked_widget.addWidget(self.problems_section)  # Índice 1
        self.stacked_widget.addWidget(self.progress_section)  # Índice 2
        self.stacked_widget.addWidget(self.ranking_section)  # Índice 3
        self.stacked_widget.addWidget(self.settings_section)  # Índice 4

        return self.stacked_widget

    def show_section(self, section_name):
        """Muestra una sección específica con animación"""
        section_map = {
            "Editor": 0,
            "Problemas": 1,
            "Mi Progreso": 2,
            "Ranking": 3,
            "Ajustes": 4
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
            ("Ajustes", "⚙️")
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
        """Crea el entorno de programación con editor, terminal y análisis de IA"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Barra de herramientas del editor
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background-color: #252530; border-radius: 4px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)

        self.run_btn = QPushButton("▶️ Ejecutar")
        self.run_btn.setFixedHeight(35)
        self.run_btn.setStyleSheet(self._button_style("#27ae60"))
        toolbar_layout.addWidget(self.run_btn)

        self.send_btn = QPushButton("📤 Enviar")
        self.send_btn.setFixedHeight(35)
        self.send_btn.setStyleSheet(self._button_style("#2980b9"))
        toolbar_layout.addWidget(self.send_btn)

        self.reset_btn = QPushButton("🔄 Reiniciar")
        self.reset_btn.setFixedHeight(35)
        self.reset_btn.setStyleSheet(self._button_style("#e74c3c"))
        toolbar_layout.addWidget(self.reset_btn)

        self.save_btn = QPushButton("💾 Guardar")
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet(self._button_style("#f39c12"))
        toolbar_layout.addWidget(self.save_btn)

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
        """Pone un código C++ de ejemplo en el editor"""
        default_code = """#include <iostream>
#include <vector>
#include <string>
using namespace std;

// Función que quieres probar
int suma(int a, int b) {
    return a + b;
}

// Función para procesar strings
string procesarTexto(string texto) {
    return "Procesado: " + texto;
}

int main() {
    // Ejemplo de uso
    int resultado = suma(5, 3);
    cout << "5 + 3 = " << resultado << endl;

    string texto = procesarTexto("Hola Mundo");
    cout << texto << endl;

    return 0;
}"""

        if hasattr(self, 'code_editor'):
            self.code_editor.setPlainText(default_code)
            self.code_base_loaded = True
            print("✅ Código base cargado en el editor")

    def setup_actions(self):
        """CONECTA LOS BOTONES A SUS MÉTODOS CORRESPONDIENTES"""
        print("🔗 Conectando botones...")

        # Conectar botones de ejecución
        if hasattr(self, 'run_btn'):
            self.run_btn.clicked.connect(self.submit_code_for_evaluation)
        if hasattr(self, 'send_btn'):
            self.send_btn.clicked.connect(self.submit_code_for_evaluation)

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

    # =============================================
    # MÉTODOS NUEVOS PARA INTEGRACIÓN CON IA
    # =============================================

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación - detiene el servidor de IA"""
        print("🔴 Cerrando aplicación...")
        self.stop_ai_server()
        super().closeEvent(event)

    def send_to_ai_feedback(self, detailed_result, user_code):
        """Envía código a IA con validación de longitud"""
        try:
            # Verificar longitud del código
            current_code = self.get_current_code()
            if len(current_code) > 2000:
                self.ai_feedback.setPlainText(
                    "📝 Código demasiado largo\n\n"
                    "Tu código excede el límite recomendado para análisis.\n\n"
                    "Sugerencias:\n"
                    "• Divide el código en funciones más pequeñas\n"
                    "• Envía solo la parte problemática\n"
                    "• El análisis funciona mejor con código conciso\n\n"
                    "Longitud actual: " + str(len(current_code)) + " caracteres\n"
                                                                   "Límite recomendado: 2000 caracteres"
                )
                return

            # Verificar si el servidor de IA está disponible
            if not self.ai_server_started:
                self.ai_feedback.setPlainText("🔧 Iniciando servidor de IA...")
                if not self.start_ai_server():
                    self.ai_feedback.setPlainText("❌ No se pudo iniciar el servidor de IA")
                    return

            # Mensaje de carga con información de tiempo
            self.ai_feedback.setPlainText(
                "🔄 Analizando código...\n\n"
                "Esto puede tomar hasta 45 segundos si es la primera vez.\n"
                "Los modelos de IA necesitan tiempo para cargar.\n\n"
                "⏳ Por favor espera..."
            )

            # Obtener datos
            problem_statement = ""
            if hasattr(self, 'current_problem_data') and self.current_problem_data:
                problem_statement = self.current_problem_data.get('statement', '')

            # Formatear resultados
            eval_results = self._format_eval_results_for_ai(detailed_result)

            # Preparar datos para IA
            ai_data = self._create_enhanced_ai_prompt(current_code, problem_statement, eval_results)

            print(f"🤖 Solicitando análisis de IA (código: {len(current_code)} caracteres)...")

            # Verificar servidor
            if not self.check_ai_server_running():
                self.ai_feedback.setPlainText("❌ Servidor de IA no disponible")
                return

            # Enviar a IA
            self.ai_thread = AIAnalysisThread(self.ai_api_url, ai_data)
            self.ai_thread.analysis_complete.connect(self.handle_ai_response)
            self.ai_thread.start()

        except Exception as e:
            self.ai_feedback.setPlainText(f"❌ Error: {str(e)}")

    def _format_eval_results_for_ai(self, detailed_result):
        """Formatea los resultados de evaluación para la API de IA, enfocado en análisis de código"""
        status = detailed_result.get('status', 'unknown')
        summary = detailed_result.get('summary', 'No summary')
        passed_count = detailed_result.get('passed_count', 0)
        total_tests = detailed_result.get('total_tests', 0)
        score = detailed_result.get('score', 0)
        execution_time = detailed_result.get('execution_time', 0)
        problem_solved = detailed_result.get('problem_solved', False)

        formatted_results = f"""
    INFORMACIÓN DE EJECUCIÓN:
    - Estado: {status.upper()}
    - Problema resuelto: {'SÍ' if problem_solved else 'NO'}
    - Pruebas pasadas: {passed_count}/{total_tests}
    - Tiempo de ejecución: {execution_time}ms
    """

        # Solo agregar detalles de pruebas si hay errores
        if status != "success" and status != "compile_error":
            tests = detailed_result.get('tests', [])
            if tests:
                formatted_results += "\nDETALLES DE PRUEBAS FALLIDAS:\n"
                failed_tests = [test for test in tests if not test.get('passed', False)]
                for i, test in enumerate(failed_tests[:3], 1):  # Máximo 3 tests fallidos
                    test_id = test.get('test_id', f'Test_{i}')
                    input_val = test.get('input', 'N/A')
                    obtained = test.get('obtained', 'N/A')
                    expected = test.get('expected', 'N/A')
                    formatted_results += f"  ❌ {test_id}:\n"
                    formatted_results += f"     Input: {input_val}\n"
                    formatted_results += f"     Obtenido: {obtained}\n"
                    formatted_results += f"     Esperado: {expected}\n\n"

        # Información de compilación si hay error
        if status == "compile_error":
            compilation_output = detailed_result.get('compilation_output', '')
            # Limitar la salida de compilación a las primeras líneas
            compilation_lines = compilation_output.split('\n')[:10]
            short_compilation = '\n'.join(compilation_lines)
            formatted_results += f"\nERRORES DE COMPILACIÓN (primeras 10 líneas):\n{short_compilation}"

            if len(compilation_output.split('\n')) > 10:
                # ✅ Corregido para Python 3.11
                num_lines = len(compilation_output.split('\n'))
                remaining_lines = num_lines - 10
                formatted_results += f"\n... y {remaining_lines} líneas más"

        return formatted_results

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

    def _format_general_feedback(self, feedback):
        """Formatea feedback general cuando no se detecta análisis de complejidad"""
        return f"""🤖 ANÁLISIS GENERAL DEL CÓDIGO
    ==================================================
    {feedback}

    ⚠️  Nota: No se detectó análisis específico de complejidad algorítmica.
    El análisis se centra en la funcionalidad general del código."""

    def _format_ai_feedback(self, feedback):
        """Formatea el feedback de IA en mensajes simples y directos"""
        if not feedback:
            return "No se recibió feedback de la IA."

        # Convertir a minúsculas para búsqueda más fácil
        feedback_lower = feedback.lower()

        # Buscar indicadores de código correcto
        correct_indicators = [
            'correcto', 'correcta', 'bien', 'éxito', 'success',
            'funciona', 'adecuado', 'apropiado', 'cumple'
        ]

        # Buscar complejidad algorítmica
        complexity_found = False
        complexity_lines = []

        lines = feedback.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detectar líneas de complejidad
            if any(keyword in line.lower() for keyword in ['o(', 'complejidad', 'big o', 'o(n)', 'o(1)', 'o(log']):
                complexity_found = True
                complexity_lines.append(line)

        # Determinar si el código es correcto
        is_correct = any(indicator in feedback_lower for indicator in correct_indicators) or complexity_found

        if is_correct and complexity_found:
            # Código correcto - mostrar complejidad
            complexity_display = "\n".join(complexity_lines[:3])  # Mostrar máximo 3 líneas de complejidad
            return f"🎉 ¡Muy bien! Tu algoritmo es de complejidad:\n\n{complexity_display}"

        elif is_correct:
            # Código correcto pero no se encontró complejidad específica
            return "✅ ¡Buen trabajo! Tu código parece correcto.\n\n🤖 La IA no detectó problemas mayores, pero revisa la complejidad manualmente."

        else:
            # Código con errores - buscar pistas
            hint_lines = []
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in
                       ['error', 'problema', 'pista', 'sugerencia', 'recomendación', 'debería', 'podría']):
                    if len(line.strip()) > 10:  # Solo líneas con contenido sustancial
                        hint_lines.append(line.strip())

            if hint_lines:
                # Tomar las 2-3 pistas más relevantes
                relevant_hints = hint_lines[:3]
                hints_text = "\n• ".join(relevant_hints)
                return f"🔧 Hay algunos errores. Te recomiendo pensar en:\n\n• {hints_text}"
            else:
                # Si no se encuentran pistas específicas, mostrar feedback general
                short_feedback = feedback[:300] + "..." if len(feedback) > 300 else feedback
                return f"📝 El código necesita ajustes:\n\n{short_feedback}"

    def create_payload_with_real_data(self, codigo_cpp: str, user_name: str):
        """Crea el payload usando los datos REALES del problema actual desde MongoDB"""
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            error_msg = "❌ No hay problema seleccionado para crear el payload"
            print(error_msg)
            return None  # ✅ Retornar None en lugar de datos dummy

        problem_data = self.current_problem_data
        examples = problem_data.get('examples', [])

        print(f"🔍 Extrayendo datos REALES del problema: {problem_data.get('title', 'N/A')}")
        print(f"   - Número de ejemplos encontrados: {len(examples)}")

        # Construir payload con TODOS los datos reales
        payload = {
            "nombre": user_name,
            "codigo": codigo_cpp,
            "problem_title": problem_data.get('title', 'Problema sin título'),
            "difficulty": problem_data.get('difficulty', 'Desconocida'),
            "category": problem_data.get('category', 'Sin categoría'),
            "statement": problem_data.get('statement', 'Sin descripción'),
            "big_o_expected": problem_data.get('big_o_expected', 'O(n)')
        }

        # Agregar todos los ejemplos disponibles (no limitar a 3)
        for i, example in enumerate(examples, 1):
            input_key = f"input{i}"
            output_key = f"output_esperado{i}"

            input_val = example.get('input_raw', '')
            output_val = example.get('output_raw', '')

            payload[input_key] = input_val
            payload[output_key] = output_val

            print(f"   - Ejemplo {i}: Input='{input_val}', Output='{output_val}'")

        return payload

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
        """Crea el payload CORRECTO para la API de DialoGPT"""

        ai_data = {
            "codigo_usuario": current_code,
            "resultados_evaluacion": eval_results,
            "problema_enunciado": problem_statement,
            "lenguaje": "C++",
            "instrucciones_especificas": """
            Analiza este código C++ y proporciona:
            1. COMPLEJIDAD: Si el código es correcto, da la complejidad algorítmica en notación Big O
            2. PISTAS: Si hay errores, da 1-2 pistas específicas para corregirlos
            3. SÉ BREVE: Máximo 3-4 líneas de respuesta
            """
        }

        return ai_data


# AuxCreator.py - AGREGAR estos métodos a la clase ModernMainWindow:

def check_ai_server_quick(self):
    """Verificación rápida del servidor IA"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def send_to_ai_feedback_fast(self, detailed_result, user_code):
    """Versión rápida para análisis de IA"""
    try:
        # Verificar servidor primero
        if not self.check_ai_server_quick():
            self.ai_feedback.setPlainText(
                "🤖 Servidor de IA no disponible\n\n"
                "Usando análisis rápido local...\n\n"
                "💡 Para análisis avanzado:\n"
                "1. Espera 1 minuto tras iniciar la app\n"
                "2. O reinicia la aplicación\n"
                "3. El servidor carga automáticamente"
            )
            return

        # Análisis rápido si el servidor está disponible
        current_code = self.get_current_code()

        if len(current_code) > 2000:
            self.ai_feedback.setPlainText("📝 Código muy largo para análisis rápido")
            return

        # Mostrar mensaje de carga
        self.ai_feedback.setPlainText("🔄 Analizando código (modo rápido)...")

        # Preparar datos
        problem_statement = ""
        if hasattr(self, 'current_problem_data') and self.current_problem_data:
            problem_statement = self.current_problem_data.get('statement', '')

        eval_results = self._format_eval_results_for_ai(detailed_result)

        ai_data = {
            "codigo_usuario": current_code,
            "resultados_evaluacion": eval_results,
            "problema_enunciado": problem_statement,
            "lenguaje": "C++"
        }

        # Enviar con timeout corto
        try:
            response = requests.post(
                "http://localhost:8000/analyze_solution",
                json=ai_data,
                timeout=10  # Timeout corto
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.ai_feedback.setPlainText(result.get('feedback_completo', 'Análisis completado'))
                else:
                    self.ai_feedback.setPlainText("❌ Error en análisis de IA")
            else:
                self.ai_feedback.setPlainText("🔌 Error conectando con IA")

        except requests.exceptions.Timeout:
            self.ai_feedback.setPlainText("⏰ Timeout - Servidor ocupado\n\nIntenta en 30 segundos")
        except Exception as e:
            self.ai_feedback.setPlainText(f"🔌 Error de conexión: {str(e)}")

    except Exception as e:
        self.ai_feedback.setPlainText(f"💥 Error: {str(e)}")


# Y MODIFICAR el método submit_code_for_evaluation:
def submit_code_for_evaluation(self):
    """Envía código para evaluación - CON IA RÁPIDA"""
    codigo_cpp = self.get_current_code()
    if not codigo_cpp:
        self.show_output({"status": "error", "message": "El editor está vacío"})
        return

    # Validar problema seleccionado
    if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
        self.show_output({
            "status": "error",
            "message": "❌ Selecciona un problema de la lista antes de enviar"
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

        # ✅ USAR LA VERSIÓN RÁPIDA DE IA
        self.send_to_ai_feedback_fast(detailed_result, codigo_cpp)

    except Exception as e:
        print(f"Error en submit_code_for_evaluation: {e}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())