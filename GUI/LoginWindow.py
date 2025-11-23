# LoginWindow.py
import sys
import os

# Configurar path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor

# LoginWindow.py - AGREGAR al inicio después de los imports:
import sys
import os

# Configurar path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


try:
    from logic.auth_logic import AuthManager
    from logic.user_models import User
    print("✅ Módulos de lógica importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos de lógica: {e}")
    # Fallback para desarrollo - MÁS ROBUSTO
    class AuthManager:
        def create_user(self, username, password):
            print(f"DUMMY: Creando usuario {username}")
            return True, "Usuario creado (modo dummy)", User(username)
        def validate_login(self, username, password):
            print(f"DUMMY: Validando {username}")
            return True, "Login exitoso (modo dummy)", User(username)
        def get_user_data(self, username):
            return User(username)

    class User:
        def __init__(self, username=""):
            self.username = username
            self.puntaje_total = 0
            self.problemas_resueltos = 0
            self.ejercicios_completados = []
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.auth_manager = AuthManager()
        self.initUI()

    def initUI(self):
        """Inicializa la interfaz de login"""
        self.setWindowTitle('leetAI - Iniciar Sesión')
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Configurar paleta de colores oscura
        self.setup_dark_palette()

        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("loginContainer")
        central_widget.setStyleSheet("""
            #loginContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 15px;
                border: 1px solid #555;
            }
        """)
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 40, 30, 30)
        main_layout.setSpacing(0)

        # Logo/Header
        header = QLabel("🚀 leetAI")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ecf0f1;
                margin-bottom: 30px;
            }
        """)
        main_layout.addWidget(header)

        # Subtítulo
        subtitle = QLabel("Plataforma de Entrenamiento")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #bdc3c7;
                margin-bottom: 40px;
            }
        """)
        main_layout.addWidget(subtitle)

        # Formulario
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)

        # Campo de usuario
        user_label = QLabel("Usuario:")
        user_label.setStyleSheet("color: #ecf0f1; font-size: 12px;")
        form_layout.addWidget(user_label)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingresa tu usuario")
        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.user_input)

        # Campo de contraseña
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("color: #ecf0f1; font-size: 12px;")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingresa tu contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.password_input)

        main_layout.addWidget(form_widget)
        main_layout.addSpacing(30)

        # Botones
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(12)

        # Botón de iniciar sesión
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        buttons_layout.addWidget(self.login_btn)

        # Botón de crear usuario
        self.create_btn = QPushButton("New User")
        self.create_btn.setFixedHeight(45)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)
        buttons_layout.addWidget(self.create_btn)

        main_layout.addLayout(buttons_layout)

        # Conectar botones
        self.login_btn.clicked.connect(self.handle_signin)
        self.create_btn.clicked.connect(self.handle_new_user)

        # Efecto de aparición
        self.fade_in()

    def setup_dark_palette(self):
        """Configura paleta de colores oscura"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 35))
        dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        self.setPalette(dark_palette)

    def fade_in(self):
        """Animación de aparición suave"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def handle_signin(self):
        """Maneja el evento de iniciar sesión"""
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_message("Error", "Por favor completa todos los campos")
            return

        if len(username) < 3:
            self.show_message("Error", "El usuario debe tener al menos 3 caracteres")
            return

        try:
            success, message, user = self.auth_manager.validate_login(username, password)

            if success:
                self.open_main_window(user)
            else:
                self.show_message("Error", message)

        except Exception as e:
            self.show_message("Error", f"Error de conexión: {str(e)}")

    def handle_new_user(self):
        """Maneja el evento de crear usuario"""
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_message("Error", "Por favor completa todos los campos")
            return

        if len(username) < 3:
            self.show_message("Error", "El usuario debe tener al menos 3 caracteres")
            return

        if len(password) < 4:
            self.show_message("Error", "La contraseña debe tener al menos 4 caracteres")
            return

        try:
            success, message, user = self.auth_manager.create_user(username, password)

            if success:
                self.open_main_window(user)
            else:
                self.show_message("Error", message)

        except Exception as e:
            self.show_message("Error", f"Error de conexión: {str(e)}")

    def show_message(self, title, message):
        """Muestra un mensaje emergente"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)

        if title == "Error":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QMessageBox QLabel {
                color: #ecf0f1;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        msg.exec_()

    def mousePressEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Maneja el movimiento para arrastrar"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def open_main_window(self, user):
        """Abre la ventana principal y cierra el login"""
        try:
            from AuxCreator import ModernMainWindow

            self.main_window = ModernMainWindow()
            self.main_window.logged_in_user = user

            print(f"🎮 Iniciando sesión como: {user.username}")
            print(f"📊 Stats iniciales: {user.puntaje_total} puntos, {user.problemas_resueltos} problemas")

            self.main_window.show()
            self.close()

        except ImportError as e:
            print(f"ERROR: No se pudo importar dependencias: {e}")
            self.show_message("Error Crítico", f"No se pudo cargar la aplicación: {str(e)}")
        except Exception as e:
            print(f"ERROR inesperado: {e}")
            import traceback
            traceback.print_exc()
            self.show_message("Error", f"Error al abrir la aplicación: {str(e)}")