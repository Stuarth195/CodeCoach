# PyLogic.py
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
        """Enviar solución para evaluación."""
        print(">>> Botón 'Enviar' presionado")

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
        pass

    def new_user(self, username, password):
        """Método para crear un nuevo usuario (por ahora solo imprime)."""
        print(f"=== NUEVO USUARIO ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print("(Lógica de creación de usuario pendiente)")

        # Aquí irá la lógica futura para:
        # - Validar formato de usuario/contraseña
        # - Verificar si el usuario ya existe
        # - Encriptar contraseña
        # - Guardar en base de datos
        # - Enviar confirmación, etc.

    def signin(self, username, password):
        """Método para iniciar sesión (por ahora solo imprime)."""
        print(f"=== INICIAR SESIÓN ===")
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print("(Lógica de autenticación pendiente)")

        # Aquí irá la lógica futura para:
        # - Verificar credenciales en base de datos
        # - Validar contraseña encriptada
        # - Crear sesión de usuario
        # - Cargar preferencias y datos del usuario
        # - Redirigir a la pantalla principal