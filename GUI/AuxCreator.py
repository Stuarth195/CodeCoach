# AuxCreator.py (versión reorganizada y corregida)
import sys

try:
    import PyLogic as H
    # Importar la nueva clase
    from PyLogic import DatabaseHandler
except Exception as e:
    print(f"Error importing PyLogic: {e}")
    H = None
    DatabaseHandler = None  # Añade esta línea
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
                             QListWidget, QLabel, QPushButton, QSplitter,
                             QFrame, QProgressBar, QStackedWidget)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QFontDatabase

# =============================================
# MÓDULO DE LÓGICA - IMPORTAR HANDLERS
# =============================================
try:
    import PyLogic as H
except Exception as e:
    print(f"Error importing PyLogic: {e}")
    H = None


class ModernMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.current_section = None
        self.initUI()

        # --- Conexión a la Base de Datos ---

        # 1. Instanciar el manejador de la base de datos
        if DatabaseHandler:
            self.db_handler = DatabaseHandler()
        else:
            self.db_handler = None

        # 2. Cargar los problemas en la lista de la barra lateral
        self.load_problems_into_sidebar()

        # 3. Conectar la lista a una nueva función
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

        # =============================================
        # CONFIGURACIÓN DE ACCIONES - CONECTAR BOTONES
        # =============================================
        self.setup_actions()

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
        # Animación de desvanecimiento
        self.animation = QPropertyAnimation(self.stacked_widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self.complete_section_change(new_index))
        self.animation.start()

    def complete_section_change(self, new_index):
        """Completa el cambio de sección después de la animación"""
        self.stacked_widget.setCurrentIndex(new_index)

        # Animación de aparición
        self.animation = QPropertyAnimation(self.stacked_widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def setup_actions(self):
        """CONECTA LOS BOTONES A SUS MÉTODOS CORRESPONDIENTES"""

        # Instanciar handlers
        if H is not None and hasattr(H, 'UIActions'):
            try:
                self.actions = H.UIActions(self)
            except Exception as e:
                print(f'Error instanciando UIActions: {e}')
                self.actions = self.create_dummy_actions()
        else:
            self.actions = self.create_dummy_actions()

        # =============================================
        # CONEXIÓN DE BOTONES DEL EDITOR
        # =============================================
        # Botón Ejecutar
        if hasattr(self.actions, 'run_code'):
            self.run_btn.clicked.connect(self.actions.run_code)

        # Botón Enviar
        if hasattr(self.actions, 'send_code'):
            self.send_btn.clicked.connect(self.actions.send_code)

        # Botón Reiniciar
        if hasattr(self.actions, 'reset_editor'):
            self.reset_btn.clicked.connect(self.actions.reset_editor)

        # Botón Guardar
        if hasattr(self.actions, 'save_code'):
            self.save_btn.clicked.connect(self.actions.save_code)

        # =============================================
        # CONEXIÓN DE BOTONES DE NAVEGACIÓN
        # =============================================
        # Conectar botones de navegación para cambiar secciones
        if hasattr(self, 'nav_buttons'):
            for name, btn in self.nav_buttons.items():
                btn.clicked.connect(lambda checked=False, n=name: self.show_section(n))

    def create_dummy_actions(self):
        """Crea acciones placeholder si no hay módulo de lógica"""

        class _DummyActions:
            def __init__(self, win):
                self.win = win

            def run_code(self): print(">>> Botón 'Ejecutar' presionado")

            def send_code(self): print(">>> Botón 'Enviar' presionado")

            def reset_editor(self): print(">>> Botón 'Reiniciar' presionado")

            def save_code(self): print(">>> Botón 'Guardar' presionado")

            def open_section(self, name): print(f">>> Navegar a: {name}")

        return _DummyActions(self)

    def setup_fonts(self):
        """Configura fuentes personalizadas para la aplicación"""
        # (Asegúrate de tener esta ruta de recursos si la usas, de lo contrario coméntala)
        # QFontDatabase.addApplicationFont(":/fonts/JetBrainsMono-Regular.ttf")
        pass  # Puedes descomentar la línea de arriba si tienes un archivo de recursos .qrc

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

    # ... dentro de ModernMainWindow

    def load_problems_into_sidebar(self):
        """
        Obtiene los títulos de la base de datos y los pone en self.problems_list.
        """
        if not self.db_handler:
            print("No hay manejador de base de datos.")
            return

        # Obtener los títulos formateados desde PyLogic
        problem_titles = self.db_handler.get_all_problem_titles()

        # Limpiar la lista estática que tenías
        self.problems_list.clear()

        if problem_titles:
            # Añadir los nuevos ítems desde la BD
            self.problems_list.addItems(problem_titles)
        else:
            # Mostrar un error si no se pudo cargar
            self.problems_list.addItem("Error al cargar problemas")

    def display_problem_details(self, item):
        """
        Se activa al hacer clic en un ítem de self.problems_list.
        Busca el problema en la BD y actualiza la sección "Problemas".
        """
        if not self.db_handler:
            return

        # Extraer el título limpio
        # El texto es "🟢 Suma de dos números - Fácil"
        # Necesitamos "Suma de dos números"
        full_text = item.text()
        try:
            # Quitar el ícono y el espacio
            title_with_diff = full_text.split(" ", 1)[1]
            # Quitar la dificultad (ej: " - Fácil")
            problem_title = title_with_diff.split(" - ")[0].strip()
        except IndexError:
            print(f"Error al parsear el título: {full_text}")
            return

        print(f"Buscando detalles para: {problem_title}")

        # 2. Obtener datos completos de la BD
        problem_data = self.db_handler.get_problem_details(problem_title)

        if not problem_data:
            print("No se encontraron datos para este problema.")
            return

        # 3. Actualizar los widgets de la sección "Problemas"
        if hasattr(self, 'problem_section_title') and hasattr(self, 'problem_section_desc'):
            self.problem_section_title.setText(problem_data.get('title', 'Sin Título'))

            # Formatear la descripción y los ejemplos
            statement = problem_data.get('statement', 'Sin descripción.')
            examples_list = problem_data.get('examples', [])

            examples_text = "\n\n" + "=" * 20 + "\nEJEMPLOS\n" + "=" * 20
            for ex in examples_list:
                examples_text += f"\n\nInput: {ex.get('input', '')}"
                examples_text += f"\nOutput: {ex.get('output', '')}"
                if 'explanation' in ex and ex.get('explanation'):
                    examples_text += f"\nExplicación: {ex.get('explanation')}"

            self.problem_section_desc.setText(statement + examples_text)

            # Opcional: Cambiar a la sección de problemas automáticamente
            self.show_section("Problemas")

        else:
            print("Error: 'problem_section_title' o 'problem_section_desc' no existen.")
            print("Asegúrate de añadir 'self.' en el método create_problems_section.")

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

        # Sección de problemas (solo visible en la sección de problemas)
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
        # Dejamos que 'load_problems_into_sidebar' llene esta lista.
        # Ya no necesitamos los datos estáticos aquí.

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

        # =============================================
        # BOTONES PRINCIPALES DEL EDITOR
        # =============================================
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

        # Selector de lenguaje
        lang_label = QLabel("Lenguaje: C++")
        lang_label.setStyleSheet("color: #ccc; padding: 8px;")
        toolbar_layout.addWidget(lang_label)

        layout.addWidget(toolbar)

        # Splitter para editor y terminal
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #444; }")

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
        splitter.addWidget(self.code_editor)

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
        self.terminal_output.setReadOnly(False)
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

        # Título
        title = QLabel("📋 Problemas de Práctica")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Descripción
        desc = QLabel("Selecciona un problema de la lista en la barra lateral para comenzar a resolverlo.")
        desc.setStyleSheet("font-size: 16px; color: #ccc; margin-bottom: 30px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Contenedor de problema seleccionado
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

        # --- INICIO DE LA CORRECCIÓN ---
        # Convertimos 'problem_title' y 'problem_desc' en atributos de clase (self.)
        # para que 'display_problem_details' pueda acceder a ellos y modificar su texto.

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

        # --- FIN DE LA CORRECCIÓN ---

        layout.addWidget(problem_frame)
        layout.addStretch()

        return container

    def create_progress_section(self):
        """Crea la sección de Mi Progreso"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("📊 Mi Progreso")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Estadísticas
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

        stats_data = [
            ("120", "Problemas Resueltos", "#27ae60"),
            ("45", "Resueltos Hoy", "#f39c12"),
            ("15", "Racha Actual", "#2980b9"),
            ("350", "Puntos Totales", "#9b59b6"),
            ("85%", "Tasa de Éxito", "#e74c3c"),
            ("25", "Días Consecutivos", "#1abc9c")
        ]

        for i, (value, label, color) in enumerate(stats_data):
            stat_widget = QFrame()
            stat_widget.setStyleSheet("background-color: #1a1a1f; border-radius: 6px; padding: 15px;")
            stat_layout = QVBoxLayout(stat_widget)

            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignCenter)

            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 12px; color: #ccc;")
            label_label.setAlignment(Qt.AlignCenter)

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)

            stats_layout.addWidget(stat_widget, i // 3, i % 3)

        layout.addWidget(stats_frame)
        layout.addStretch()

        return container

    def create_ranking_section(self):
        """Crea la sección de Ranking"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("🏆 Ranking Global")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Tabla de ranking
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

        # Crear grid layout para alinear las columnas
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        # Encabezados
        headers = ["Posición", "Usuario", "Puntaje", "Problemas"]
        for col, header in enumerate(headers):
            header_label = QLabel(header)
            header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f1c40f; padding: 10px;")
            grid_layout.addWidget(header_label, 0, col)  # Fila 0 para encabezados

        # Datos de ranking (ejemplo)
        ranking_data = [
            ("🥇 1", "CodeMaster", "1250", "45"),
            ("🥈 2", "AlgoExpert", "1180", "42"),
            ("🥉 3", "PythonPro", "1120", "38"),
            ("4", "JavaWizard", "1050", "35"),
            ("5", "CppGuru", "980", "32"),
            ("6", "DataStruct", "920", "30"),
            ("7", "AlgorithmLover", "870", "28"),
            ("8", "LeetCodeFan", "810", "25"),
            ("9", "BinarySearch", "760", "22"),
            ("10", "QuickSort", "700", "20")
        ]

        # Agregar datos al grid
        for row, (position, user, score, problems) in enumerate(ranking_data, start=1):
            pos_label = QLabel(position)
            user_label = QLabel(user)
            score_label = QLabel(score)
            problems_label = QLabel(problems)

            # Estilo para los datos
            for label in [pos_label, user_label, score_label, problems_label]:
                label.setStyleSheet("font-size: 14px; color: #ddd; padding: 8px;")

            # Destacar los primeros 3 puestos
            if row <= 3:
                for label in [pos_label, user_label, score_label, problems_label]:
                    label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f1c40f; padding: 8px;")

            # Agregar al grid en la misma columna que los encabezados
            grid_layout.addWidget(pos_label, row, 0)  # Posición
            grid_layout.addWidget(user_label, row, 1)  # Usuario
            grid_layout.addWidget(score_label, row, 2)  # Puntaje
            grid_layout.addWidget(problems_label, row, 3)  # Problemas

        ranking_layout.addLayout(grid_layout)
        layout.addWidget(ranking_frame)
        layout.addStretch()

        return container

    def create_settings_section(self):
        """Crea la sección de Ajustes"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("⚙️ Ajustes")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff; margin-bottom: 20px;")
        layout.addWidget(title)

        # Configuraciones
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
        """Devuelve stylesheet para botones con color dado."""
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())