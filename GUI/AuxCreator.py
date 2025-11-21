# AuxCreator.py - VENTANA PRINCIPAL COMPLETA
import sys
import os
import threading

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

class ModernMainWindow(QMainWindow):
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
        """Crea el entorno de programación con editor y terminal"""
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

        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #444; }")

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
        splitter.addWidget(self.code_editor)

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
        self.terminal_output.setMaximumHeight(300)
        terminal_layout.addWidget(self.terminal_output)

        splitter.addWidget(terminal_container)
        splitter.setSizes([700, 200])
        layout.addWidget(splitter)

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

    def get_current_code(self):
        """Obtiene el código actual del editor"""
        if hasattr(self, 'code_editor'):
            return self.code_editor.toPlainText().strip()
        return ""

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

            if payload is None:
                error_msg = "❌ No se pudo crear el payload con datos reales"
                print(error_msg)
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

        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            self.show_output({
                "status": "error",
                "message": "Selecciona un problema de la lista antes de enviar"
            })
            return

        try:
            result = self.send_raw_cpp_code(codigo_cpp)
            detailed_result = self.show_output(result)  # Ahora retorna la estructura completa

            # Actualizar MongoDB si la solución es correcta
            if detailed_result.get('problem_solved'):
                if hasattr(self, 'current_problem_data') and self.current_problem_data:
                    success = self.update_user_progress_after_solution(self.current_problem_data)
                    if success:
                        print("🎉 ¡Progreso guardado en MongoDB!")
                        # Aquí puedes usar detailed_result para estadísticas adicionales
                        score = detailed_result.get('score', 0)
                        print(f"📊 Puntaje obtenido: {score}")
                    else:
                        print("⚠️  Solución correcta pero no se pudo guardar el progreso")

            # Enviar a API de IA para retroalimentación
            self.send_to_ai_feedback(detailed_result, codigo_cpp)

        except Exception as e:
            print(f"Error en submit_code_for_evaluation: {e}")

    def seto_ai_feedbacknd_(self, detailed_result, user_code):
        """Envía resultados a API de IA para retroalimentación"""
        try:
            # Preparar datos para IA
            ai_data = {
                'user_code': user_code,
                'test_results': detailed_result.get('tests', []),
                'score': detailed_result.get('score', 0),
                'passed_count': detailed_result.get('passed_count', 0),
                'total_tests': detailed_result.get('total_tests', 0),
                'execution_time': detailed_result.get('execution_time', 0),
                'problem_solved': detailed_result.get('problem_solved', False)
            }

            # Aquí iría la llamada a tu API de IA
            print("🤖 Enviando datos a API de IA para retroalimentación...")
            # requests.post('https://tu-api-ia.com/feedback', json=ai_data)

        except Exception as e:
            print(f"Error enviando a IA: {e}")

    def create_payload_with_real_data(self, codigo_cpp: str, user_name: str):
        """Crea el payload usando los datos REALES del problema actual desde MongoDB"""
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            print("⚠️  No hay problema seleccionado, usando datos de prueba")
            return self.create_dummy_payload(codigo_cpp, user_name)

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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())