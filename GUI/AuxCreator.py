# AuxCreator.py (versión mejor organizada)
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
                             QListWidget, QLabel, QPushButton, QSplitter,
                             QFrame, QProgressBar, QStackedWidget)
from PyQt5.QtCore import Qt, QSize
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
        self.initUI()

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
        central_area = self.create_central_area()
        right_sidebar = self.create_right_sidebar()

        # Agregar componentes al layout principal
        main_layout.addWidget(left_sidebar)
        main_layout.addWidget(central_area, 1)
        main_layout.addWidget(right_sidebar)

        # =============================================
        # CONFIGURACIÓN DE ACCIONES - CONECTAR BOTONES
        # =============================================
        self.setup_actions()

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
        if hasattr(self.actions, 'open_section'):
            for name, btn in self.nav_buttons.items():
                btn.clicked.connect(lambda checked=False, n=name: self.actions.open_section(n))

    def create_dummy_actions(self):
        """Crea acciones placeholder si no hay módulo de lógica"""

        class _DummyActions:
            def __init__(self, win):
                self.win = win

            def run_code(self): print(">>> run_code: handler no implementado")

            def send_code(self): print(">>> send_code: handler no implementado")

            def reset_editor(self): print(">>> reset_editor: handler no implementado")

            def save_code(self): print(">>> save_code: handler no implementado")

            def open_section(self, name): print(f">>> open_section: {name} (no implementado)")

        return _DummyActions(self)

    # ... (el resto de los métodos create_left_sidebar, create_central_area, etc. se mantienen igual)
    def setup_fonts(self):
        """Configura fuentes personalizadas para la aplicación"""
        QFontDatabase.addApplicationFont(":/fonts/JetBrainsMono-Regular.ttf")

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
        # ... (implementación existente)
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
                }
                QPushButton:hover {
                    background-color: #3a3a45;
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
        problems_label = QLabel("PROBLEMAS")
        problems_label.setStyleSheet("color: #ccc; font-weight: bold;")
        layout.addWidget(problems_label)

        self.problems_list = QListWidget()
        self.problems_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1f;
                color: #ddd;
                border: none;
                padding: 6px;
            }
        """)
        problems = [
            "🟢 Two Sum - Fácil",
            "🟢 Valid Parentheses - Fácil",
            "🟡 Reverse Linked List - Medio",
            "🟡 Binary Tree Inorder - Medio",
            "🔴 Median of Two Arrays - Difícil",
            "🔴 Trapping Rain Water - Difícil"
        ]
        self.problems_list.addItems(problems)
        layout.addWidget(self.problems_list)

        return sidebar

    def create_central_area(self):
        """Crea la parte central con pestañas y contenido principal"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

        # Pestaña de programación
        coding_tab = self.create_coding_environment()
        self.main_tabs.addTab(coding_tab, "💻 Editor de Código")

        # Pestaña de problemas
        problems_tab = QWidget()
        p_layout = QVBoxLayout(problems_tab)
        p_layout.setContentsMargins(12, 12, 12, 12)

        problem_title = QLabel("Two Sum")
        problem_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #eee;")
        p_layout.addWidget(problem_title)

        problem_desc = QLabel("Dada una lista de enteros, encuentra dos números que sumen un objetivo.")
        problem_desc.setWordWrap(True)
        problem_desc.setStyleSheet("color: #ddd;")
        p_layout.addWidget(problem_desc)

        self.main_tabs.addTab(problems_tab, "📋 Problema")
        layout.addWidget(self.main_tabs)
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

    def create_right_sidebar(self):
        """Crea la barra lateral derecha con estadísticas y ranking"""
        # ... (implementación existente)
        right = QWidget()
        right.setFixedWidth(320)
        right.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(right)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Tarjeta de estadísticas
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(12, 12, 12, 12)
        stats_layout.setSpacing(8)

        title = QLabel("Resumen")
        title.setStyleSheet("font-weight: bold; color: #fff;")
        stats_layout.addWidget(title)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(8)

        sample_stats = [
            ("120", "Problemas resueltos", "#27ae60"),
            ("45", "Hoy", "#f39c12"),
            ("12", "Racha", "#2980b9"),
            ("350", "Puntos", "#9b59b6")
        ]

        for i, (value, label, color) in enumerate(sample_stats):
            stat_widget = QFrame()
            stat_widget.setStyleSheet("background-color: #1a1a1f; border-radius: 6px;")
            stat_layout = QVBoxLayout(stat_widget)
            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 11px; color: #ccc;")
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            stats_grid.addWidget(stat_widget, i // 2, i % 2)

        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_card)

        # Tarjeta de ranking
        rank_card = QFrame()
        rank_card.setStyleSheet("""
            QFrame {
                background-color: #252530;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        rank_layout = QVBoxLayout(rank_card)
        rank_layout.setContentsMargins(12, 12, 12, 12)

        rtitle = QLabel("Ranking")
        rtitle.setStyleSheet("font-weight: bold; color: #fff;")
        rank_layout.addWidget(rtitle)

        rank_list = QListWidget()
        rank_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1f;
                color: #ddd;
                border: none;
                padding: 6px;
            }
        """)
        rank_list.addItems([
            "1. Alice - 1240",
            "2. Bob - 1190",
            "3. Carol - 1100"
        ])
        rank_layout.addWidget(rank_list)
        layout.addWidget(rank_card)

        return right


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernMainWindow()
    win.show()
    sys.exit(app.exec_())