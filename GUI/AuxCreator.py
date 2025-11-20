# AuxCreator.py - VENTANA PRINCIPAL COMPLETA
import sys
import os
import threading
import re

# Configurar paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
                             QListWidget, QLabel, QPushButton, QSplitter,
                             QFrame, QProgressBar, QStackedWidget, QMessageBox,
                             QLineEdit, QComboBox, QScrollArea, QFormLayout,
                             QGroupBox, QTextEdit, QCheckBox)
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

        def insert_problem(self, problem_data):
            print("Dummy: Insertando problema")
            return True


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


class ProblemValidator:
    """Clase para validar y formatear datos de problemas antes de insertar en MongoDB"""

    @staticmethod
    def validate_problem_data(problem_data):
        """Valida que los datos del problema sean correctos"""
        errors = []

        # Validar título
        title = problem_data.get('title', '').strip()
        if not title:
            errors.append("El título es obligatorio")
        elif len(title) < 3:
            errors.append("El título debe tener al menos 3 caracteres")
        elif not re.match(r'^[a-zA-Z0-9\s\-_]+$', title):
            errors.append("El título solo puede contener letras, números, espacios, guiones y guiones bajos")

        # Validar categoría
        category = problem_data.get('category', '').strip()
        if not category:
            errors.append("La categoría es obligatoria")

        # Validar dificultad
        difficulty = problem_data.get('difficulty', '').strip()
        if difficulty not in ['Fácil', 'Medio', 'Difícil']:
            errors.append("La dificultad debe ser: Fácil, Medio o Difícil")

        # Validar enunciado
        statement = problem_data.get('statement', '').strip()
        if not statement:
            errors.append("El enunciado es obligatorio")
        elif len(statement) < 10:
            errors.append("El enunciado debe tener al menos 10 caracteres")

        # Validar Big O
        big_o = problem_data.get('big_o_expected', '').strip()
        if not big_o:
            errors.append("El Big O esperado es obligatorio")

        # Validar ejemplos
        examples = problem_data.get('examples', [])
        if not examples:
            errors.append("Debe agregar al menos un ejemplo")
        else:
            for i, example in enumerate(examples, 1):
                if not example.get('input_raw', '').strip():
                    errors.append(f"El input del ejemplo {i} es obligatorio")
                if not example.get('output_raw', '').strip():
                    errors.append(f"El output del ejemplo {i} es obligatorio")

        return errors

    @staticmethod
    def format_problem_name(title):
        """Formatea el nombre del problema para usar en compilación"""
        # Reemplazar espacios con guiones bajos y eliminar caracteres especiales
        formatted = re.sub(r'[^\w\s-]', '', title)
        formatted = re.sub(r'[\s]+', '_', formatted)
        return formatted.lower()

    @staticmethod
    def create_problem_payload(form_data):
        """Crea el payload final para MongoDB"""
        formatted_title = ProblemValidator.format_problem_name(form_data['title'])

        payload = {
            'title': form_data['title'],
            'category': form_data['category'],
            'difficulty': form_data['difficulty'],
            'statement': form_data['statement'],
            'big_o_expected': form_data['big_o_expected'],
            'examples': form_data['examples'],
            'formatted_title': formatted_title  # Para uso en compilación
        }

        return payload


class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_section = None
        self.current_problem_data = None
        self.logged_in_user = None
        self.code_base_loaded = False
        self.is_admin = False  # Por defecto no es admin
        self.validator = ProblemValidator()

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

        # Si es admin, agregar la sección de administración
        if self.is_admin:
            self.admin_section = self.create_admin_section()
            self.stacked_widget.addWidget(self.admin_section)  # Índice 5

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

        # Si es admin, agregar la sección de administración al mapa
        if self.is_admin:
            section_map["Admin"] = 5

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

        # Si es admin, agregar botón de administración
        if self.is_admin:
            nav_buttons.append(("Admin", "👑"))

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

    def create_admin_section(self):
        """Crea la sección de administración para agregar problemas"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("👑 Panel de Administración")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Scroll area para el formulario
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        # Widget contenedor del formulario
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        # Grupo de información básica
        basic_info_group = QGroupBox("Información Básica del Problema")
        basic_info_group.setStyleSheet("""
            QGroupBox {
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        basic_info_layout = QFormLayout(basic_info_group)

        # Campo de título
        self.admin_title_input = QLineEdit()
        self.admin_title_input.setPlaceholderText("Ej: Paréntesis Válidos")
        self.admin_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                margin: 5px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        basic_info_layout.addRow("Título*:", self.admin_title_input)

        # Campo de categoría
        self.admin_category_input = QLineEdit()
        self.admin_category_input.setPlaceholderText("Ej: Stacks, Arrays, Strings")
        self.admin_category_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                margin: 5px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        basic_info_layout.addRow("Categoría*:", self.admin_category_input)

        # Campo de dificultad
        self.admin_difficulty_combo = QComboBox()
        self.admin_difficulty_combo.addItems(["Fácil", "Medio", "Difícil"])
        self.admin_difficulty_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                margin: 5px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        basic_info_layout.addRow("Dificultad*:", self.admin_difficulty_combo)

        # Campo de Big O esperado
        self.admin_bigo_input = QLineEdit()
        self.admin_bigo_input.setPlaceholderText("Ej: O(n), O(n log n), O(1)")
        self.admin_bigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                margin: 5px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        basic_info_layout.addRow("Big O Esperado*:", self.admin_bigo_input)

        form_layout.addWidget(basic_info_group)

        # Grupo de enunciado
        statement_group = QGroupBox("Enunciado del Problema")
        statement_group.setStyleSheet("""
            QGroupBox {
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        statement_layout = QVBoxLayout(statement_group)

        self.admin_statement_input = QTextEdit()
        self.admin_statement_input.setPlaceholderText(
            "Describe el problema detalladamente...\n\n"
            "Ejemplo:\n"
            "Dada una cadena 's' que contiene solo los caracteres '(', ')', '{', '}', '[' y ']', "
            "determina si la cadena de entrada es válida.\n\n"
            "Una cadena de entrada es válida si:\n"
            "1. Los corchetes abiertos deben cerrarse con el mismo tipo de corchetes.\n"
            "2. Los corchetes abiertos deben cerrarse en el orden correcto."
        )
        self.admin_statement_input.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                min-height: 200px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        statement_layout.addWidget(self.admin_statement_input)

        form_layout.addWidget(statement_group)

        # Grupo de ejemplos
        examples_group = QGroupBox("Ejemplos de Entrada/Salida (Mínimo 1)")
        examples_group.setStyleSheet("""
            QGroupBox {
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        examples_layout = QVBoxLayout(examples_group)

        # Ejemplo 1
        example1_group = QGroupBox("Ejemplo 1")
        example1_group.setStyleSheet("""
            QGroupBox {
                color: #ccc;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 5px;
            }
        """)
        example1_layout = QFormLayout(example1_group)

        self.admin_example1_input = QLineEdit()
        self.admin_example1_input.setPlaceholderText("Input (ej: [1,2,3])")
        self.admin_example1_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example1_layout.addRow("Input*:", self.admin_example1_input)

        self.admin_example1_output = QLineEdit()
        self.admin_example1_output.setPlaceholderText("Output esperado (ej: 6)")
        self.admin_example1_output.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example1_layout.addRow("Output*:", self.admin_example1_output)

        examples_layout.addWidget(example1_group)

        # Ejemplo 2
        example2_group = QGroupBox("Ejemplo 2")
        example2_group.setStyleSheet("""
            QGroupBox {
                color: #ccc;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 5px;
            }
        """)
        example2_layout = QFormLayout(example2_group)

        self.admin_example2_input = QLineEdit()
        self.admin_example2_input.setPlaceholderText("Input (ej: hello)")
        self.admin_example2_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example2_layout.addRow("Input:", self.admin_example2_input)

        self.admin_example2_output = QLineEdit()
        self.admin_example2_output.setPlaceholderText("Output esperado (ej: olleh)")
        self.admin_example2_output.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example2_layout.addRow("Output:", self.admin_example2_output)

        examples_layout.addWidget(example2_group)

        # Ejemplo 3
        example3_group = QGroupBox("Ejemplo 3")
        example3_group.setStyleSheet("""
            QGroupBox {
                color: #ccc;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 5px;
            }
        """)
        example3_layout = QFormLayout(example3_group)

        self.admin_example3_input = QLineEdit()
        self.admin_example3_input.setPlaceholderText("Input (ej: 5)")
        self.admin_example3_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example3_layout.addRow("Input:", self.admin_example3_input)

        self.admin_example3_output = QLineEdit()
        self.admin_example3_output.setPlaceholderText("Output esperado (ej: 120)")
        self.admin_example3_output.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #ecf0f1;
            }
        """)
        example3_layout.addRow("Output:", self.admin_example3_output)

        examples_layout.addWidget(example3_group)

        form_layout.addWidget(examples_group)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        # Botón para limpiar formulario
        self.admin_clear_btn = QPushButton("🗑️ Limpiar Formulario")
        self.admin_clear_btn.setFixedHeight(45)
        self.admin_clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.admin_clear_btn.clicked.connect(self.clear_admin_form)

        # Botón para agregar problema
        self.admin_add_btn = QPushButton("➕ Agregar Problema")
        self.admin_add_btn.setFixedHeight(45)
        self.admin_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.admin_add_btn.clicked.connect(self.add_problem_to_database)

        buttons_layout.addWidget(self.admin_clear_btn)
        buttons_layout.addWidget(self.admin_add_btn)

        form_layout.addLayout(buttons_layout)
        form_layout.addStretch()

        scroll_area.setWidget(form_container)
        layout.addWidget(scroll_area)

        return container

    def add_problem_to_database(self):
        """Agrega un nuevo problema a la base de datos"""
        try:
            # Recolectar datos del formulario
            form_data = {
                'title': self.admin_title_input.text().strip(),
                'category': self.admin_category_input.text().strip(),
                'difficulty': self.admin_difficulty_combo.currentText(),
                'big_o_expected': self.admin_bigo_input.text().strip(),
                'statement': self.admin_statement_input.toPlainText().strip(),
                'examples': []
            }

            # Recolectar ejemplos
            examples = []

            # Ejemplo 1 (obligatorio)
            if self.admin_example1_input.text().strip() and self.admin_example1_output.text().strip():
                examples.append({
                    "input_raw": self.admin_example1_input.text().strip(),
                    "input_pretty": f"Input: {self.admin_example1_input.text().strip()}",
                    "output_raw": self.admin_example1_output.text().strip(),
                    "output_pretty": f"Output: {self.admin_example1_output.text().strip()}"
                })

            # Ejemplo 2 (opcional)
            if self.admin_example2_input.text().strip() and self.admin_example2_output.text().strip():
                examples.append({
                    "input_raw": self.admin_example2_input.text().strip(),
                    "input_pretty": f"Input: {self.admin_example2_input.text().strip()}",
                    "output_raw": self.admin_example2_output.text().strip(),
                    "output_pretty": f"Output: {self.admin_example2_output.text().strip()}"
                })

            # Ejemplo 3 (opcional)
            if self.admin_example3_input.text().strip() and self.admin_example3_output.text().strip():
                examples.append({
                    "input_raw": self.admin_example3_input.text().strip(),
                    "input_pretty": f"Input: {self.admin_example3_input.text().strip()}",
                    "output_raw": self.admin_example3_output.text().strip(),
                    "output_pretty": f"Output: {self.admin_example3_output.text().strip()}"
                })

            form_data['examples'] = examples

            # Validar datos usando ProblemValidator
            errors = self.validator.validate_problem_data(form_data)

            if errors:
                error_msg = "❌ Errores de validación:\n• " + "\n• ".join(errors)
                self.show_output({"status": "error", "message": error_msg})
                return

            # Crear payload final para MongoDB
            problem_data = self.validator.create_problem_payload(form_data)

            print(f"📦 Insertando problema en MongoDB:")
            print(f"   - Título: {problem_data['title']}")
            print(f"   - Categoría: {problem_data['category']}")
            print(f"   - Dificultad: {problem_data['difficulty']}")
            print(f"   - Big O: {problem_data['big_o_expected']}")
            print(f"   - Ejemplos: {len(problem_data['examples'])}")
            print(f"   - Nombre formateado: {problem_data.get('formatted_title', 'N/A')}")

            # Insertar en la base de datos
            if self.db_handler and hasattr(self.db_handler, 'insert_problem'):
                success = self.db_handler.insert_problem(problem_data)
                if success:
                    success_msg = f"✅ Problema '{problem_data['title']}' agregado correctamente\n"
                    success_msg += f"📝 Nombre para compilación: {problem_data.get('formatted_title', 'N/A')}"
                    self.show_output({"status": "success", "message": success_msg})
                    self.clear_admin_form()
                    # Recargar la lista de problemas en el sidebar
                    self.load_problems_into_sidebar()
                else:
                    self.show_output(
                        {"status": "error", "message": "❌ Error al agregar el problema a la base de datos"})
            else:
                self.show_output({"status": "error", "message": "❌ No se pudo acceder a la base de datos"})

        except Exception as e:
            error_msg = f"💥 Error inesperado: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.show_output({"status": "error", "message": error_msg})

    def clear_admin_form(self):
        """Limpia el formulario de administración"""
        self.admin_title_input.clear()
        self.admin_category_input.clear()
        self.admin_difficulty_combo.setCurrentIndex(0)
        self.admin_bigo_input.clear()
        self.admin_statement_input.clear()
        self.admin_example1_input.clear()
        self.admin_example1_output.clear()
        self.admin_example2_input.clear()
        self.admin_example2_output.clear()
        self.admin_example3_input.clear()
        self.admin_example3_output.clear()

    # ... (los métodos restantes se mantienen igual, solo muestro los que cambiaron)

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

    # ... (los métodos create_progress_section, create_ranking_section, create_settings_section
    # se mantienen igual que en la versión original)

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

    def update_problem_display(self, problem_info):
        """Actualiza la visualización del problema en la GUI"""
        title = problem_info.get('title', 'Sin título')
        statement = problem_info.get('statement', 'Descripción no disponible.')
        difficulty = problem_info.get('difficulty', 'Desconocida')
        category = problem_info.get('category', 'Sin categoría')

        description_html = f"""
        <div style="color: #ddd; line-height: 1.6;">
            <p><b>Dificultad:</b> {difficulty}</p>
            <p><b>Categoría:</b> {category}</p>
            <p><b>Enunciado:</b> {statement}</p>
        """

        examples = problem_info.get('examples', [])
        if examples:
            description_html += "<p><b>Ejemplos para testing:</b></p>"
            for i, example in enumerate(examples, 1):
                input_raw = example.get('input_raw', 'N/A')
                output_raw = example.get('output_raw', 'N/A')

                description_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: #1a1a1f; border-radius: 5px;">
                    <b>Ejemplo {i}:</b><br>
                    <b>Input:</b> {input_raw}<br>
                    <b>Output esperado:</b> {output_raw}
                </div>
                """

        description_html += "</div>"

        self.problem_section_title.setText(title)
        self.problem_section_desc.setText(description_html)

    def get_current_code(self):
        """Obtiene el código actual del editor"""
        if hasattr(self, 'code_editor'):
            return self.code_editor.toPlainText().strip()
        return ""

    def submit_code_for_evaluation(self):
        """Envía código para evaluación y actualiza progreso si es exitoso"""
        codigo_cpp = self.get_current_code()
        if not codigo_cpp:
            self.show_output({"status": "error", "message": "El editor está vacío"})
            return

        try:
            result = self.send_raw_cpp_code(codigo_cpp)
            self.show_output(result)

            # Actualizar MongoDB si la solución es correcta
            if result.get('status') == 'success':
                if hasattr(self, 'current_problem_data') and self.current_problem_data:
                    success = self.update_user_progress_after_solution(self.current_problem_data)
                    if success:
                        print("🎉 ¡Progreso guardado en MongoDB!")
                    else:
                        print("⚠️  Solución correcta pero no se pudo guardar el progreso")

        except Exception as e:
            print(f"Error en submit_code_for_evaluation: {e}")

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

    def create_payload_with_real_data(self, codigo_cpp: str, user_name: str):
        """Crea el payload usando los datos REALES del problema actual desde MongoDB"""
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            print("⚠️  No hay problema seleccionado, usando datos de prueba")
            return self.create_dummy_payload(codigo_cpp, user_name)

        problem_data = self.current_problem_data
        examples = problem_data.get('examples', [])

        print(f"🔍 Extrayendo datos REALES del problema: {problem_data.get('title', 'N/A')}")
        print(f"   - Número de ejemplos encontrados: {len(examples)}")

        payload = {
            "nombre": user_name,
            "codigo": codigo_cpp,
            "problem_title": problem_data.get('title', 'Problema sin título'),
            "difficulty": problem_data.get('difficulty', 'Desconocida')
        }

        for i, example in enumerate(examples[:3], 1):
            input_key = f"input{i}"
            output_key = f"output_esperado{i}"

            input_val = example.get('input_raw', '')
            output_val = example.get('output_raw', '')

            payload[input_key] = input_val
            payload[output_key] = output_val

            print(f"   - Ejemplo {i}: Input='{input_val}', Output='{output_val}'")

        for i in range(len(examples) + 1, 4):
            payload[f"input{i}"] = ""
            payload[f"output_esperado{i}"] = ""

        return payload

    def create_dummy_payload(self, codigo_cpp: str, user_name: str):
        """Crea payload con datos de prueba (fallback)"""
        return {
            "nombre": user_name,
            "codigo": codigo_cpp,
            "input1": "5",
            "input2": "10",
            "input3": "15",
            "output_esperado1": "25",
            "output_esperado2": "100",
            "output_esperado3": "225",
            "problem_title": "Problema de Prueba",
            "difficulty": "Fácil"
        }

    def show_output(self, result):
        """Muestra el resultado de la evaluación en la terminal"""
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message provided.')
        details = result.get('details', '')
        output = result.get('output', '')

        if status == "success":
            color = "#00ff00"
        elif status in ["error", "connection_error", "server_error", "runtime_error"]:
            color = "#ff0000"
        else:
            color = "#ffff00"

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

        display_text = f"Estado: {status}\nMensaje: {message}\n"
        if details:
            display_text += f"Detalles: {details}\n"
        if output:
            display_text += f"Salida:\n{output}"

        self.terminal_output.setText(display_text)

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

    def get_submission_data_for_evaluation(self):
        """Obtiene los datos para evaluación (método requerido por PyLogic)"""
        if not hasattr(self, 'current_problem_data') or not self.current_problem_data:
            return None

        codigo_cpp = self.get_current_code()
        if not codigo_cpp:
            return None

        user_name = "Invitado"
        if hasattr(self, 'logged_in_user') and self.logged_in_user:
            user_name = getattr(self.logged_in_user, 'username', 'Invitado')

        return self.create_payload_with_real_data(codigo_cpp, user_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())