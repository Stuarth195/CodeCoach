# PyLogic.py - CLIENTE HTTP Y COMPILADOR
import sys
import requests
import socket


class HttpClient:
    """
    Cliente HTTP para comunicación con servidor C++
    """

    def __init__(self, host=None, port=5000):
        docker_host = "cpp-server"
        local_host = "localhost"

        try:
            # Intentar conectar al servidor Docker
            socket.gethostbyname(docker_host)
            self.BASE_URL = f"http://{docker_host}:{port}"
            print(f"✅ Conectando al servidor C++ en Docker: {self.BASE_URL}")
        except socket.gaierror:
            # Fallback a localhost
            self.BASE_URL = f"http://{local_host}:{port}"
            print(f"⚠️  Conectando al servidor C++ local: {self.BASE_URL}")

    def send(self, data: dict, endpoint: str):
        """Envía datos al servidor C++ con manejo robusto de errores"""
        url = self.BASE_URL + endpoint
        print(f"📤 Enviando a {url}")

        try:
            response = requests.post(url, json=data, timeout=30)

            if response.status_code == 200:
                return response.json()
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
                "suggestion": "Asegúrate de que el servidor C++ esté ejecutándose"
            }

        except requests.exceptions.Timeout:
            error_msg = "⏰ Timeout al conectar con el servidor C++"
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
    Envía código C++ al servidor para evaluación
    """

    def __init__(self):
        self.http_client = HttpClient()

    def send_evaluation_package(self, payload: dict):
        """Envía payload completo al servidor C++ para evaluación"""
        print("🔄 Enviando payload al servidor C++...")

        # Validación mínima del payload
        if "codigo" not in payload:
            return {
                "status": "error",
                "message": "El payload debe contener al menos el campo 'codigo'"
            }

        print(f"📦 Payload preparado:")
        print(f"   - Usuario: {payload.get('nombre', 'N/A')}")
        print(f"   - Problema: {payload.get('problem_title', 'N/A')}")
        print(f"   - Longitud código: {len(payload.get('codigo', ''))} caracteres")

        endpoint = "/submit_evaluation"
        result = self.http_client.send(payload, endpoint)

        # Asegurar que siempre retorne un dict válido
        if result is None:
            return {
                "status": "error",
                "message": "No se recibió respuesta del servidor"
            }

        return result

    def send_code_to_compile(self, user_code: str):
        """
        Para el botón 'Ejecutar' - envía código simple para compilación rápida
        """
        payload = {
            "nombre": "Ejecución Rápida",
            "codigo": user_code,
            "input1": "test1",
            "input2": "test2",
            "input3": "test3",
            "output_esperado1": "result1",
            "output_esperado2": "result2",
            "output_esperado3": "result3"
        }
        endpoint = "/submit_evaluation"
        return self.http_client.send(payload, endpoint)


class UIActions:
    """
    Clase para manejar acciones de la interfaz de usuario
    """

    def __init__(self, main_window):
        self.win = main_window

    def run_code(self):
        """Se ejecuta cuando el usuario presiona 'Enviar'"""
        print("🚀 ===== INICIANDO EVALUACIÓN =====")

        # Obtener datos de envío desde la ventana principal
        submission_package = self.win.get_submission_data_for_evaluation()

        if submission_package is None:
            print("❌ No se pudo obtener el paquete de envío")
            self.win.show_output({
                "status": "error",
                "message": "No se pudo preparar el envío"
            })
            return

        print(f"✅ Paquete obtenido:")
        print(f"   - Usuario: {submission_package.get('nombre', 'N/A')}")
        print(f"   - Problema: {submission_package.get('problem_title', 'N/A')}")

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
        """Se ejecuta cuando el usuario presiona 'Ejecutar' (compilación rápida)"""
        print(">>> Botón 'Ejecutar' presionado - Compilación rápida")

        if hasattr(self.win, 'code_editor'):
            codigo = self.win.code_editor.toPlainText().strip()
            if not codigo:
                self.win.show_output({
                    "status": "error",
                    "message": "El editor está vacío"
                })
                return

            self.win.terminal_output.clear()
            self.win.terminal_output.setText("🔨 Compilando código...")

            try:
                result = self.win.compiler_client.send_code_to_compile(codigo)
                self.win.show_output(result)
            except Exception as e:
                self.win.show_output({
                    "status": "error",
                    "message": f"Error en compilación: {str(e)}"
                })

    def reset_editor(self):
        """Reiniciar el editor a plantilla"""
        print(">>> Botón 'Reiniciar' presionado")
        if hasattr(self.win, 'setup_default_code_template'):
            self.win.setup_default_code_template()
            self.win.show_output({
                "status": "success",
                "message": "Editor reiniciado a plantilla predeterminada"
            })

    def save_code(self):
        """Guardar el contenido del editor"""
        print(">>> Botón 'Guardar' presionado")
        if hasattr(self.win, 'code_editor'):
            codigo = self.win.code_editor.toPlainText()
            # Aquí podrías implementar la lógica de guardado en archivo
            self.win.show_output({
                "status": "success",
                "message": "Código guardado (función en desarrollo)"
            })

    def open_section(self, section_name):
        """Navegar a una sección específica"""
        print(f">>> Navegar a: {section_name}")
        if hasattr(self.win, 'show_section'):
            self.win.show_section(section_name)


# Clases de compatibilidad (para evitar errores de importación)
class User:
    """Clase User de compatibilidad - se usa la de user_models.py principalmente"""

    def __init__(self, nombre, contrasena="", puntaje=0, num_ejercicios=0, exercise_list=None):
        self.nombre = nombre
        self.contrasena = contrasena
        self.puntaje = puntaje
        self.num_ejercicios = num_ejercicios
        self.exercise_list = exercise_list or []


class LogAccion:
    """Clase de compatibilidad para login - se usa AuthManager principalmente"""

    def __init__(self):
        self.users = {}

    def new_user(self, username, password):
        print(f"DUMMY: Creando usuario {username}")
        return True

    def signin(self, username, password):
        print(f"DUMMY: Validando {username}")
        return True



if __name__ == "__main__":
    # Pruebas básicas del cliente
    print("🧪 Probando PyLogic...")

    client = HttpClient()
    compiler = CodeCompilerWrapper()

    test_payload = {
        "nombre": "test_user",
        "codigo": "#include <iostream>\nint main() { return 0; }",
        "input1": "test",
        "output_esperado1": "test"
    }

    result = compiler.send_evaluation_package(test_payload)
    print(f"Resultado prueba: {result.get('status', 'N/A')}")