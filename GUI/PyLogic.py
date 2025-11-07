# PyLogic.py
import sys
import requests
from pymongo.errors import ServerSelectionTimeoutError
import pymongo
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


# PyLogic.py - CORREGIR LA CLASE DatabaseHandler

class DatabaseHandler:
    def __init__(self):
        self.client = None
        self.db = None
        self.problems_collection = None

        MONGO_URI = "mongodb://localhost:27017/"
        TIMEOUT_MS = 3000

        try:
            self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=TIMEOUT_MS)
            self.client.admin.command('ping')  # Forzar la verificación

            # CAMBIAR: Usar codecoach_db en lugar de leetai_db
            self.db = self.client["codecoach_db"]  # ← ESTA ES LA CORRECCIÓN
            self.problems_collection = self.db["problems"]
            print("INFO: Conexión a MongoDB establecida exitosamente.")
            print(f"INFO: Base de datos: {self.db.name}, Colección: {self.problems_collection.name}")

        except ServerSelectionTimeoutError as err:
            print("ERROR DB: Fallo de conexión a MongoDB. La aplicación continuará.")
            self.client = None
        except Exception as e:
            print(f"ERROR DB: Fallo inesperado: {e}")
            self.client = None

    def get_all_problem_titles(self):
        """
        Obtiene una lista de todos los títulos de problemas y su dificultad.
        """
        # VERIFICACIÓN CRÍTICA: Si no hay conexión, retornar lista vacía
        if self.problems_collection is None:
            print("DEBUG: problems_collection es None - sin conexión a DB")
            return []

        try:
            print("DEBUG: Intentando obtener problemas de la colección...")

            # Obtener todos los documentos de la colección problems
            problems_cursor = self.problems_collection.find({})
            problems_list = list(problems_cursor)

            print(f"DEBUG: Se encontraron {len(problems_list)} problemas en la colección")

            formatted_list = []
            for problem in problems_list:
                title = problem.get('title', 'Sin título')
                difficulty = problem.get('difficulty', 'Desconocida')

                print(f"DEBUG: Procesando problema - Título: {title}, Dificultad: {difficulty}")

                # Asignar iconos según dificultad
                if difficulty == "Fácil":
                    icon = "🟢"
                elif difficulty == "Media":
                    icon = "🟡"
                elif difficulty == "Difícil":
                    icon = "🔴"
                else:
                    icon = "⚪"  # Para dificultades desconocidas

                formatted_list.append(f"{icon} {title} - {difficulty}")

            print(f"DEBUG: Lista formateada: {formatted_list}")
            return formatted_list

        except Exception as e:
            print(f"Error al obtener títulos de problemas: {e}")
            return []

    def get_problem_details(self, title):
        """
        Obtiene todos los detalles de un problema por su título.
        """
        # VERIFICACIÓN CRÍTICA: Si no hay conexión, retornar None
        if self.problems_collection is None:
            print("DEBUG: Sin conexión a DB en get_problem_details")
            return None

        try:
            print(f"DEBUG: Buscando problema con título: {title}")

            # Limpiar el título (remover iconos y dificultad si existen)
            clean_title = title
            if ' - ' in title:
                clean_title = title.split(' - ')[0].split(' ', 1)[1]  # Remover icono y dificultad

            print(f"DEBUG: Título limpio para búsqueda: '{clean_title}'")

            problem_data = self.problems_collection.find_one({"title": clean_title})

            if problem_data:
                print(f"DEBUG: Problema encontrado: {problem_data.get('title')}")
                # Convertir ObjectId a string para serialización
                if '_id' in problem_data:
                    problem_data['_id'] = str(problem_data['_id'])
            else:
                print(f"DEBUG: No se encontró problema con título: '{clean_title}'")

            return problem_data

        except Exception as e:
            print(f"Error al obtener detalles del problema {title}: {e}")
            return None

class UIActions:
    """
    Clase actualizada con mejor logging para debugging
    """
    
    def __init__(self, main_window):
        self.win = main_window

    def run_code(self):
        """
        Se ejecutará cuando el usuario presione 'Enviar'.
        Mejorado con logging detallado.
        """
        print("🚀 ===== INICIANDO EVALUACIÓN =====")
        
        # Obtener datos de envío
        submission_package = self.win.get_submission_data_for_evaluation()
        
        if submission_package is None:
            print("❌ No se pudo obtener el paquete de envío")
            return
            
        print(f"✅ Paquete obtenido:")
        print(f"   - Usuario: {submission_package.get('user_name', 'N/A')}")
        print(f"   - Problema: {submission_package.get('problem_details', {}).get('title', 'N/A')}")
        
        # Limpiar terminal y mostrar mensaje de progreso
        self.win.terminal_output.clear()
        self.win.terminal_output.setText("🔄 Enviando código al servidor C++...")
        
        try:
            # Enviar al servidor C++
            result = self.win.compiler_client.send_evaluation_package(submission_package)
            
            print(f"📨 Respuesta del servidor C++: {result.get('status', 'unknown')}")
            
            # Mostrar resultados en la interfaz
            self.win.show_output(result)
            
        except Exception as e:
            error_msg = f"💥 Error inesperado: {str(e)}"
            print(error_msg)
            self.win.show_output({
                "status": "client_error", 
                "message": error_msg
            })

    def send_code(self):
        """Se ejecutará cuando el usuario presione 'Ejecutar'."""
        print(">>> Botón 'enviar' presionado")


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
        self.users = {}  # nombre -> User object

    def new_user(self, username, password):
        """Método para crear un nuevo usuario - SOLO establece nombre y contraseña."""
        print(f"=== NUEVO USUARIO ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")

        if username in self.users:
            print(f"Error: El usuario '{username}' ya existe")
            return False

        new_user = User(
            nombre=username,
            contrasena=password
        )

        self.users[username] = new_user
        print(f"Usuario '{username}' creado exitosamente con la contraseña {new_user.contrasena}")
        print(f"Datos del usuario: {new_user}")

        return True

    def signin(self, username, password):
        """Método para iniciar sesión."""
        print(f"=== INICIAR SESIÓN ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")

        if username not in self.users:
            print(f"Error: El usuario '{username}' no existe")
            return False

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


class HttpClient:
    """
    Cliente HTTP actualizado para trabajar con Docker
    """
    
    def __init__(self, host=None, port=5000):
        # En Docker, usar el nombre del servicio; localmente, localhost
        docker_host = "cpp-server"  # Nombre del servicio en docker-compose
        local_host = "localhost"
        
        # Determinar automáticamente si estamos en Docker
        try:
            import socket
            # Intentar resolver el nombre del servicio Docker
            socket.gethostbyname(docker_host)
            self.BASE_URL = f"http://{docker_host}:{port}"
            print(f"✅ Conectando al servidor C++ en Docker: {self.BASE_URL}")
        except socket.gaierror:
            # Fallback a localhost
            self.BASE_URL = f"http://{local_host}:{port}"
            print(f"⚠️  Conectando al servidor C++ local: {self.BASE_URL}")

    def send(self, data: dict, endpoint: str):
        """
        Envía datos al servidor C++ con mejor manejo de errores
        """
        url = self.BASE_URL + endpoint
        print(f"📤 Enviando a {url}")

        try:
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"✅ Respuesta recibida del servidor C++")
                    return result
                except requests.exceptions.JSONDecodeError as e:
                    print(f"❌ Error decodificando JSON: {e}")
                    return {
                        "status": "json_error",
                        "message": f"Error decodificando respuesta: {str(e)}",
                        "response_text": response.text[:200]
                    }
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return {
                    "status": "http_error",
                    "message": f"Error HTTP {response.status_code}",
                    "details": response.text
                }

        except requests.exceptions.ConnectionError:
            error_msg = f"❌ No se pudo conectar al servidor C++ en {url}"
            print(error_msg)
            return {
                "status": "connection_error",
                "message": error_msg,
                "suggestion": "Asegúrate de que el servidor C++ esté ejecutándose en Docker"
            }
        except requests.exceptions.Timeout:
            error_msg = f"⏰ Timeout al conectar con el servidor C++"
            print(error_msg)
            return {
                "status": "timeout_error",
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"💥 Error inesperado: {str(e)}"
            print(error_msg)
            return {
                "status": "unexpected_error",
                "message": error_msg
            }


class CodeCompilerWrapper:
    """
    Capa de lógica de negocio actualizada para el nuevo formato
    """
    
    def __init__(self):
        self.http_client = HttpClient()  # Usa detección automática

    def send_evaluation_package(self, submission_package: dict):
        """
        Adapta el formato antiguo al nuevo formato esperado por C++
        """
        print("🔄 Adaptando formato para servidor C++...")
        
        # Extraer datos del paquete original
        user_code = submission_package.get("code", "")
        problem_details = submission_package.get("problem_details", {})
        user_name = submission_package.get("user_name", "Invitado")
        
        # Construir el nuevo formato para C++
        cpp_payload = {
            "problem_title": problem_details.get("title", "Problema sin título"),
            "user_code": user_code,
            "test_cases": self._extract_test_cases(problem_details)
        }
        
        print(f"📦 Payload para C++:")
        print(f"   - Problema: {cpp_payload['problem_title']}")
        print(f"   - Casos de prueba: {len(cpp_payload['test_cases'])}")
        print(f"   - Usuario: {user_name}")
        
        endpoint = "/submit_evaluation"
        return self.http_client.send(cpp_payload, endpoint)
    
    def _extract_test_cases(self, problem_details: dict) -> list:
        """
        Extrae y formatea los casos de prueba del formato MongoDB al formato C++
        """
        examples = problem_details.get('examples', [])
        test_cases = []
        
        for i, example in enumerate(examples, 1):
            test_case = {
                "input_raw": example.get('input_raw', ''),
                "expected_output_raw": example.get('output_raw', '')
            }
            test_cases.append(test_case)
            
            # Log para debugging
            print(f"   Caso {i}: Input='{test_case['input_raw']}', Expected='{test_case['expected_output_raw']}'")
        
        return test_cases

    def send_code_to_compile(self, user_code: str):
        """
        Para el botón 'Ejecutar' - compilación simple
        """
        # Para compatibilidad, podemos usar el mismo formato pero con un caso vacío
        payload = {
            "problem_title": "Ejecución Rápida",
            "user_code": user_code,
            "test_cases": [{
                "input_raw": "",
                "expected_output_raw": ""
            }]
        }
        endpoint = "/submit_evaluation"
        return self.http_client.send(payload, endpoint)

class CodeCompilerWrapper:
    """
    Capa de lógica de negocio que utiliza HttpClient para enviar código.
    """

    def __init__(self):
        self.http_client = HttpClient(host="http://127.0.0.1", port=5000)

    def send_code_to_compile(self, user_code: str):
        """Para el botón 'Ejecutar' (compilación simple)"""
        payload = {"code": user_code}
        endpoint = "/submit_code"
        return self.http_client.send(payload, endpoint)

    def send_evaluation_package(self, submission_package: dict):
        """Para el botón 'Enviar' (evaluación completa con test cases)"""
        endpoint = "/submit_evaluation"
        return self.http_client.send(submission_package, endpoint)