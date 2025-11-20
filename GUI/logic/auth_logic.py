# logic/auth_logic.py
import os
import sys
import hashlib
import secrets
from datetime import datetime

# Configurar paths para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from logic.database_handler import DatabaseHandler
    from logic.user_models import User

    print("✅ Módulos de lógica importados en auth_logic")
except ImportError as e:
    print(f"❌ Error importando módulos en auth_logic: {e}")


class AuthManager:
    """Manejador de autenticación y autorización de usuarios"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.admin_usernames = self._load_admin_usernames()

    def _load_admin_usernames(self):
        """Carga la lista de usuarios administradores desde la base de datos"""
        try:
            if hasattr(self.db_handler, 'admins_collection'):
                admins = list(self.db_handler.admins_collection.find({}))
                admin_usernames = [admin['username'] for admin in admins if 'username' in admin]
                print(f"👑 Administradores cargados: {admin_usernames}")
                return set(admin_usernames)
            else:
                print("⚠️  Colección de administradores no disponible, usando lista por defecto")
                return {'admin', 'root', 'administrator'}  # Fallback
        except Exception as e:
            print(f"❌ Error cargando administradores: {e}")
            return {'admin'}  # Fallback mínimo

    def _hash_password(self, password):
        """Hashea una contraseña usando SHA-256 con salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt

    def _verify_password(self, password, stored_hash, salt):
        """Verifica una contraseña contra el hash almacenado"""
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash

    def create_user(self, username, password, email=None):
        """Crea un nuevo usuario en el sistema"""
        try:
            # Validaciones básicas
            if not username or not password:
                return False, "Usuario y contraseña son obligatorios", None

            if len(username) < 3:
                return False, "El usuario debe tener al menos 3 caracteres", None

            if len(password) < 4:
                return False, "La contraseña debe tener al menos 4 caracteres", None

            # Verificar si el usuario ya existe
            existing_user = self.db_handler.users_collection.find_one({"username": username})
            if existing_user:
                return False, "El usuario ya existe", None

            # Hashear contraseña
            password_hash, salt = self._hash_password(password)

            # Crear documento de usuario
            user_data = {
                "username": username,
                "password_hash": password_hash,
                "salt": salt,
                "email": email or f"{username}@codecoach.com",
                "fecha_registro": datetime.now(),
                "ultimo_acceso": datetime.now(),
                "activo": True,
                "puntaje_total": 0,
                "problemas_resueltos": 0,
                "ejercicios_completados": [],
                "facil_resueltos": 0,
                "medio_resueltos": 0,
                "dificil_resueltos": 0,
                "racha_actual": 0,
                "mejor_racha": 0
            }

            # Insertar en la base de datos
            result = self.db_handler.users_collection.insert_one(user_data)

            if result.inserted_id:
                print(f"✅ Usuario creado: {username}")
                user_obj = User(username)
                user_obj.refresh_stats()  # Cargar stats desde la base de datos
                return True, "Usuario creado exitosamente", user_obj
            else:
                return False, "Error al crear usuario en la base de datos", None

        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            return False, f"Error del sistema: {str(e)}", None

    def validate_login(self, username, password):
        """Valida las credenciales de login"""
        try:
            if not username or not password:
                return False, "Usuario y contraseña son obligatorios", None

            # Buscar usuario en la base de datos
            user_data = self.db_handler.users_collection.find_one({"username": username})

            if not user_data:
                return False, "Usuario no encontrado", None

            if not user_data.get("activo", True):
                return False, "Usuario desactivado", None

            # Verificar contraseña
            stored_hash = user_data.get("password_hash")
            salt = user_data.get("salt")

            if not stored_hash or not salt:
                return False, "Error en los datos de autenticación", None

            if not self._verify_password(password, stored_hash, salt):
                return False, "Contraseña incorrecta", None

            # Actualizar último acceso
            self.db_handler.users_collection.update_one(
                {"username": username},
                {"$set": {"ultimo_acceso": datetime.now()}}
            )

            # Crear objeto User
            user_obj = User(username)
            user_obj.refresh_stats()  # Cargar stats actualizados

            print(f"✅ Login exitoso: {username}")
            return True, "Login exitoso", user_obj

        except Exception as e:
            print(f"❌ Error en validación de login: {e}")
            return False, f"Error del sistema: {str(e)}", None

    def is_user_admin(self, username):
        """Verifica si el usuario tiene privilegios de administrador"""
        try:
            # Primero verificar si el usuario existe
            user_data = self.db_handler.users_collection.find_one({"username": username})
            if not user_data:
                print(f"❌ Usuario no encontrado: {username}")
                return False

            # Verificar en la colección de administradores
            if hasattr(self.db_handler, 'admins_collection'):
                admin_user = self.db_handler.admins_collection.find_one({"username": username})
                is_admin = admin_user is not None

                if is_admin:
                    print(f"👑 Usuario {username} es administrador")
                else:
                    print(f"👤 Usuario {username} NO es administrador")

                return is_admin
            else:
                # Fallback: verificar en la lista cargada
                is_admin = username in self.admin_usernames
                print(f"⚠️  Usando lista local de admins: {username} -> {is_admin}")
                return is_admin

        except Exception as e:
            print(f"❌ Error verificando privilegios de admin: {e}")
            return False

    def update_user_progress(self, username, problem_data, points_earned=10):
        """Actualiza el progreso del usuario después de resolver un problema"""
        try:
            user_data = self.db_handler.users_collection.find_one({"username": username})
            if not user_data:
                return False, None

            problem_title = problem_data.get('title')
            difficulty = problem_data.get('difficulty', 'Desconocida')

            # Verificar si el usuario ya resolvió este problema
            ejercicios_completados = user_data.get('ejercicios_completados', [])
            if problem_title in ejercicios_completados:
                print(f"⚠️  Usuario {username} ya resolvió {problem_title}")
                return False, None

            # Actualizar estadísticas
            update_operations = {
                "$inc": {
                    "puntaje_total": points_earned,
                    "problemas_resueltos": 1,
                    "racha_actual": 1
                },
                "$push": {"ejercicios_completados": problem_title},
                "$set": {"ultimo_acceso": datetime.now()}
            }

            # Actualizar contadores por dificultad
            if difficulty == "Fácil":
                update_operations["$inc"]["facil_resueltos"] = 1
            elif difficulty == "Medio":
                update_operations["$inc"]["medio_resueltos"] = 1
            elif difficulty == "Difícil":
                update_operations["$inc"]["dificil_resueltos"] = 1

            # Actualizar mejor racha si es necesario
            current_streak = user_data.get('racha_actual', 0) + 1
            best_streak = user_data.get('mejor_racha', 0)
            if current_streak > best_streak:
                update_operations["$set"]["mejor_racha"] = current_streak

            # Aplicar actualizaciones
            result = self.db_handler.users_collection.update_one(
                {"username": username},
                update_operations
            )

            if result.modified_count > 0:
                print(f"✅ Progreso actualizado para {username}: +{points_earned} puntos")
                # Devolver usuario actualizado
                updated_user = User(username)
                updated_user.refresh_stats()
                return True, updated_user
            else:
                print(f"❌ No se pudo actualizar progreso para {username}")
                return False, None

        except Exception as e:
            print(f"❌ Error actualizando progreso: {e}")
            return False, None

    def get_user_stats(self, username):
        """Obtiene las estadísticas del usuario"""
        try:
            user_data = self.db_handler.users_collection.find_one(
                {"username": username},
                {
                    "puntaje_total": 1,
                    "problemas_resueltos": 1,
                    "ejercicios_completados": 1,
                    "facil_resueltos": 1,
                    "medio_resueltos": 1,
                    "dificil_resueltos": 1,
                    "racha_actual": 1,
                    "mejor_racha": 1
                }
            )

            if user_data:
                return {
                    'puntaje_total': user_data.get('puntaje_total', 0),
                    'problemas_resueltos': user_data.get('problemas_resueltos', 0),
                    'ejercicios_completados': user_data.get('ejercicios_completados', []),
                    'facil_resueltos': user_data.get('facil_resueltos', 0),
                    'medio_resueltos': user_data.get('medio_resueltos', 0),
                    'dificil_resueltos': user_data.get('dificil_resueltos', 0),
                    'racha_actual': user_data.get('racha_actual', 0),
                    'mejor_racha': user_data.get('mejor_racha', 0)
                }
            else:
                return None

        except Exception as e:
            print(f"❌ Error obteniendo stats de usuario: {e}")
            return None

    def reset_user_password(self, username, new_password):
        """Resetea la contraseña de un usuario"""
        try:
            password_hash, salt = self._hash_password(new_password)

            result = self.db_handler.users_collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "password_hash": password_hash,
                        "salt": salt
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            print(f"❌ Error reseteando contraseña: {e}")
            return False

    def deactivate_user(self, username):
        """Desactiva un usuario (solo administradores)"""
        try:
            result = self.db_handler.users_collection.update_one(
                {"username": username},
                {"$set": {"activo": False}}
            )

            return result.modified_count > 0

        except Exception as e:
            print(f"❌ Error desactivando usuario: {e}")
            return False

    def get_all_users(self):
        """Obtiene todos los usuarios (solo administradores)"""
        try:
            users = list(self.db_handler.users_collection.find(
                {},
                {
                    "username": 1,
                    "email": 1,
                    "fecha_registro": 1,
                    "ultimo_acceso": 1,
                    "puntaje_total": 1,
                    "problemas_resueltos": 1,
                    "activo": 1
                }
            ).sort("puntaje_total", -1))

            return users

        except Exception as e:
            print(f"❌ Error obteniendo usuarios: {e}")
            return []


# Clase de compatibilidad para manejo de errores
class LogAccion:
    """Clase de compatibilidad para el sistema legacy"""

    def __init__(self):
        self.auth_manager = AuthManager()

    def new_user(self, username, password):
        success, message, _ = self.auth_manager.create_user(username, password)
        return success

    def signin(self, username, password):
        success, message, _ = self.auth_manager.validate_login(username, password)
        return success


if __name__ == "__main__":
    # Pruebas básicas
    auth = AuthManager()

    # Test de creación de usuario
    success, message, user = auth.create_user("test_user", "test123")
    print(f"Crear usuario: {success} - {message}")

    # Test de login
    success, message, user = auth.validate_login("test_user", "test123")
    print(f"Login: {success} - {message}")

    # Test de verificación de admin
    is_admin = auth.is_user_admin("test_user")
    print(f"Es admin: {is_admin}")