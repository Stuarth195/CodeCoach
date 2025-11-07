# logic/auth_logic.py
from .database_handler import DatabaseHandler
from .user_models import User


class AuthManager:
    """
    Gestiona la autenticación y registro de usuarios
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()
        print("✅ AuthManager inicializado")

    def create_user(self, username, password):
        """
        Crea un nuevo usuario en la base de datos

        Returns:
            tuple: (success, message, user_object)
        """
        print(f"=== CREANDO NUEVO USUARIO ===")
        print(f"Usuario: {username}")

        # Validaciones del lado del servidor
        if not username or not password:
            return False, "Usuario y contraseña son requeridos", None

        if len(username) < 3:
            return False, "El usuario debe tener al menos 3 caracteres", None

        if len(password) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres", None

        # Verificar si el usuario ya existe
        if self.db_handler.user_exists(username):
            return False, f"El usuario '{username}' ya existe", None

        try:
            # Crear usuario en la base de datos
            success = self.db_handler.create_user(username, password)

            if success:
                print(f"✅ Usuario '{username}' creado exitosamente")
                # Crear objeto User con estadísticas iniciales
                user = User(username)
                return True, "Usuario creado exitosamente", user
            else:
                return False, "Error al crear usuario en la base de datos", None

        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            return False, f"Error de base de datos: {str(e)}", None

    def validate_login(self, username, password):
        """
        Valida las credenciales de login
        """
        print(f"=== VALIDANDO LOGIN ===")
        print(f"Usuario: {username}")

        if not username or not password:
            return False, "Usuario y contraseña son requeridos", None

        try:
            # ✅ CORRECCIÓN: Verificar si el handler está conectado
            if self.db_handler is None or self.db_handler.users_collection is None:
                return False, "Error de conexión a la base de datos", None

            # Validar contra la base de datos
            success = self.db_handler.validate_login(username, password)

            if success:
                print(f"✅ Login exitoso para: {username}")

                # Obtener estadísticas del usuario
                stats = self.db_handler.get_user_stats(username)
                if stats:
                    user = User(username, stats_data=stats)
                    print(f"📊 Stats cargadas: {user.puntaje_total} puntos, {user.problemas_resueltos} problemas")
                    return True, "Login exitoso", user
                else:
                    user = User(username)
                    return True, "Login exitoso", user
            else:
                return False, "Usuario o contraseña incorrectos", None

        except Exception as e:
            print(f"❌ Error validando login: {e}")
            return False, f"Error de conexión: {str(e)}", None

    def get_user_data(self, username):
        """Obtiene todos los datos del usuario"""
        stats = self.db_handler.get_user_stats(username)
        if stats:
            return User(username, stats_data=stats)
        return None

    def update_user_progress(self, username, problem_data, points_earned=10):
        """Actualiza el progreso del usuario después de resolver un problema"""
        try:
            problem_title = problem_data.get('title', 'Problema desconocido')
            difficulty = problem_data.get('difficulty', 'Desconocida')

            print(f"🎯 Actualizando progreso: {username} -> {problem_title} (+{points_earned}p)")

            # Obtener usuario y actualizar progreso
            user = self.get_user_data(username)
            if user:
                success = user.update_progress(problem_title, difficulty, points_earned)
                if success:
                    print(f"✅ Progreso actualizado para {username}")
                    return True, user
                else:
                    print(f"❌ Error actualizando progreso para {username}")
                    return False, user
            else:
                print(f"❌ Usuario {username} no encontrado")
                return False, None

        except Exception as e:
            print(f"❌ Error en update_user_progress: {e}")
            return False, None