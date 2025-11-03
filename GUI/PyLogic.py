# PyLogic.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QTabWidget, QTextEdit,
                             QListWidget, QLabel, QPushButton, QSplitter,
                             QFrame, QProgressBar, QStackedWidget)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QFontDatabase

class User:
    """
    Clase que representa a un usuario de la plataforma leetAI.
    """
    
    def __init__(self, nombre, contrasena, puntaje=0, num_ejercicios=0, exercise_list=None):
        """
        Inicializa un nuevo usuario.
        
        Args:
            nombre (str): Nombre del usuario
            contrasena (str): Contraseña del usuario
            puntaje (int): Puntaje acumulado del usuario (por defecto 0)
            num_ejercicios (int): Número de ejercicios resueltos (por defecto 0)
            exercise_list (list): Lista de ejercicios completados (por defecto lista vacía)
        """
        self.nombre = nombre
        self.contrasena = contrasena
        self.puntaje = puntaje
        self.num_ejercicios = num_ejercicios
        self.exercise_list = exercise_list if exercise_list is not None else []
    
    def __str__(self):
        """Representación en string del usuario."""
        return (f"User(nombre='{self.nombre}', puntaje={self.puntaje}, "
                f"num_ejercicios={self.num_ejercicios}, "
                f"exercise_list={self.exercise_list})")
    
    def to_dict(self):
        """Convierte el objeto User a un diccionario (útil para JSON o base de datos)."""
        return {
            'nombre': self.nombre,
            'contrasena': self.contrasena,
            'puntaje': self.puntaje,
            'num_ejercicios': self.num_ejercicios,
            'exercise_list': self.exercise_list
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto User desde un diccionario."""
        return cls(
            nombre=data.get('nombre', ''),
            contrasena=data.get('contrasena', ''),
            puntaje=data.get('puntaje', 0),
            num_ejercicios=data.get('num_ejercicios', 0),
            exercise_list=data.get('exercise_list', [])
        )


class UIActions:
    """
    Clase que contiene los métodos que responderán a los botones de la UI.
    """
    def __init__(self, main_window):
        self.win = main_window

    def run_code(self):
        """Se ejecutará cuando el usuario presione 'Ejecutar'."""
        print(">>> Botón 'Ejecutar' presionado")

    def send_code(self):


        print(">>> Ranking y progreso actualizados con datos fijos")

    def reset_editor(self):
        """Reiniciar el editor a plantilla."""
        print(">>> Botón 'Reiniciar' presionado")

    def save_code(self):
        """Guardar el contenido del editor."""
        print(">>> Botón 'Guardar' presionado")

    def open_section(self, section_name):
        """Navegar a una sección según el texto del botón."""
        print(f">>> Navegar a: {section_name}")


class LogAccion:
    """
    Clase para manejar las acciones de login y registro de usuarios.
    """
    
    def __init__(self):
        # Por ahora usaremos un diccionario simple para almacenar usuarios
        # En el futuro esto se reemplazará por una base de datos
        self.users = {}  # nombre -> User object
    
    def new_user(self, username, password):
        """Método para crear un nuevo usuario - SOLO establece nombre y contraseña."""
        print(f"=== NUEVO USUARIO ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        
        # Verificar si el usuario ya existe
        if username in self.users:
            print(f"Error: El usuario '{username}' ya existe")
            return False
        
        # Crear nuevo usuario - SOLO con nombre y contraseña, el resto por defecto
        new_user = User(
            nombre=username,
            contrasena=password  # Los demás atributos se inicializan automáticamente:
            # puntaje=0 (por defecto)
            # num_ejercicios=0 (por defecto) 
            # exercise_list=[] (por defecto)
        )
        
        # Guardar usuario
        self.users[username] = new_user
        print(f"Usuario '{username}' creado exitosamente con la contraseña {new_user.contrasena}")
        print(f"Datos del usuario: {new_user}")
        
        return True

    def signin(self, username, password):
        """Método para iniciar sesión."""
        print(f"=== INICIAR SESIÓN ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        
        # Verificar si el usuario existe
        if username not in self.users:
            print(f"Error: El usuario '{username}' no existe")
            return False
        
        # Verificar contraseña
        user = self.users[username]
        if user.contrasena != password:
            print("Error: Contraseña incorrecta")
            return False
        
        print(f"Login exitoso para usuario: {username}")
        print(f"Datos del usuario: {user}")
        
        return True
    
    def get_user(self, username):
        """Obtiene un usuario por su nombre."""
        return self.users.get(username)
    
    def update_user_score(self, username, points_earned, exercise_name):
        """Actualiza el puntaje y lista de ejercicios de un usuario."""
        if username in self.users:
            user = self.users[username]
            user.puntaje += points_earned
            user.num_ejercicios += 1
            if exercise_name not in user.exercise_list:
                user.exercise_list.append(exercise_name)
            print(f"Puntaje actualizado para {username}: +{points_earned} puntos")
            return True
        return False


