# logic/database_handler.py
import pymongo
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from datetime import datetime
import hashlib


class DatabaseHandler:
    """
    Maneja TODAS las operaciones de base de datos - USUARIOS Y PROBLEMAS
    """

    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.problems_collection = None
        self.user_stats_collection = None
        self.admins_collection = None  # Nueva colección para administradores

        self.connect()

    def connect(self):
        """Establece conexión con MongoDB"""
        MONGO_URI = "mongodb://localhost:27017/"
        TIMEOUT_MS = 5000

        try:
            self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=TIMEOUT_MS)
            self.client.admin.command('ping')  # Test de conexión

            # Usar codecoach_db para todo
            self.db = self.client["codecoach_db"]

            # Inicializar todas las colecciones
            self.users_collection = self.db["users"]
            self.problems_collection = self.db["problems"]
            self.user_stats_collection = self.db["user_stats"]
            self.admins_collection = self.db["admins"]  # Nueva colección

            # ✅ CORRECCIÓN: Inicializar como None si no existen las colecciones
            existing_collections = self.db.list_collection_names()

            if "users" not in existing_collections:
                self.users_collection = None
                print("⚠️  Colección 'users' no encontrada")
            if "user_stats" not in existing_collections:
                self.user_stats_collection = None
                print("⚠️  Colección 'user_stats' no encontrada")
            if "problems" not in existing_collections:
                self.problems_collection = None
                print("⚠️  Colección 'problems' no encontrada")
            if "admins" not in existing_collections:
                self.admins_collection = None
                print("⚠️  Colección 'admins' no encontrada - Los usuarios no tendrán privilegios de admin")

            print("✅ MongoDB conectado - Base de datos: codecoach_db")
            print(f"   - Colecciones disponibles: {existing_collections}")

        except ServerSelectionTimeoutError:
            print("❌ ERROR: No se pudo conectar a MongoDB - Verifica que esté ejecutándose")
            self.client = None
            self.users_collection = None
            self.user_stats_collection = None
            self.problems_collection = None
            self.admins_collection = None
        except Exception as e:
            print(f"❌ ERROR DB: {e}")
            self.client = None
            self.users_collection = None
            self.user_stats_collection = None
            self.problems_collection = None
            self.admins_collection = None

    # =============================================
    # MÉTODOS PARA USUARIOS
    # =============================================

    def user_exists(self, username):
        """Verifica si un usuario ya existe"""
        if self.users_collection is None:
            return False
        try:
            return self.users_collection.find_one({"username": username}) is not None
        except Exception as e:
            print(f"❌ Error verificando usuario: {e}")
            return False

    def create_user(self, username, password):
        """Crea un nuevo usuario en la base de datos"""
        if self.users_collection is None:
            return False

        try:
            # Hash simple de la contraseña (en producción usar bcrypt)
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            user_data = {
                "username": username,
                "password_hash": password_hash,
                "email": f"{username}@codecoach.com",  # Email temporal
                "fecha_registro": datetime.now(),
                "ultimo_acceso": datetime.now(),
                "activo": True
            }

            # Insertar usuario
            result = self.users_collection.insert_one(user_data)

            if result.inserted_id:
                # Crear estadísticas iniciales del usuario
                stats_data = {
                    "username": username,
                    "puntaje_total": 0,
                    "problemas_resueltos": 0,
                    "ejercicios_completados": [],
                    "facil_resueltos": 0,
                    "medio_resueltos": 0,
                    "dificil_resueltos": 0,
                    "racha_actual": 0,
                    "mejor_racha": 0,
                    "tiempo_total_practica": 0,
                    "ultima_actualizacion": datetime.now()
                }

                self.user_stats_collection.insert_one(stats_data)
                print(f"✅ Usuario '{username}' creado exitosamente en MongoDB")
                return True
            else:
                return False

        except DuplicateKeyError:
            print(f"❌ Usuario '{username}' ya existe")
            return False
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            return False

    def validate_login(self, username, password):
        """Valida las credenciales de login"""
        if self.users_collection is None:
            return False

        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user = self.users_collection.find_one({
                "username": username,
                "password_hash": password_hash
            })

            if user:
                # Actualizar último acceso
                self.users_collection.update_one(
                    {"username": username},
                    {"$set": {"ultimo_acceso": datetime.now()}}
                )
                print(f"✅ Login válido para: {username}")
                return True
            else:
                print(f"❌ Credenciales inválidas para: {username}")
                return False

        except Exception as e:
            print(f"❌ Error validando login: {e}")
            return False

    def get_user_stats(self, username):
        """Obtiene estadísticas completas del usuario"""
        if self.users_collection is None:
            return False

        try:
            stats = self.user_stats_collection.find_one({"username": username})
            if stats:
                # Convertir ObjectId a string y limpiar
                if '_id' in stats:
                    stats['_id'] = str(stats['_id'])
                return stats
            else:
                print(f"⚠️  No se encontraron stats para: {username}")
                return None
        except Exception as e:
            print(f"❌ Error obteniendo stats: {e}")
            return None

    def update_user_score(self, username, problem_title, difficulty, points_earned=10):
        """Actualiza el puntaje del usuario después de resolver un problema"""
        if self.users_collection is None:
            return False

        try:
            # Primero verificar si el usuario ya resolvió este problema
            user_stats = self.user_stats_collection.find_one({"username": username})
            if user_stats and problem_title in user_stats.get('ejercicios_completados', []):
                print(f"⚠️  Usuario {username} ya resolvió {problem_title}")
                return True  # Ya está resuelto, no sumar puntos otra vez

            # Preparar campos de actualización
            update_fields = {
                "$inc": {
                    "puntaje_total": points_earned,
                    "problemas_resueltos": 1,
                    "racha_actual": 1
                },
                "$addToSet": {"ejercicios_completados": problem_title},
                "$set": {"ultima_actualizacion": datetime.now()}
            }

            # Incrementar contador por dificultad
            if difficulty == "Fácil":
                update_fields["$inc"]["facil_resueltos"] = 1
            elif difficulty == "Medio":  # ✅ CORREGIDO: era "Media"
                update_fields["$inc"]["medio_resueltos"] = 1
            elif difficulty == "Difícil":
                update_fields["$inc"]["dificil_resueltos"] = 1

            # Actualizar mejor racha si es necesario
            if user_stats:
                nueva_racha = user_stats.get('racha_actual', 0) + 1
                mejor_racha = user_stats.get('mejor_racha', 0)
                if nueva_racha > mejor_racha:
                    update_fields["$set"]["mejor_racha"] = nueva_racha

            result = self.user_stats_collection.update_one(
                {"username": username},
                update_fields
            )

            success = result.modified_count > 0

            if success:
                print(f"✅ Progreso actualizado: {username} +{points_earned}p - {problem_title}")
            else:
                print(f"⚠️  No se pudo actualizar progreso para: {username}")

            return success

        except Exception as e:
            print(f"❌ Error actualizando puntaje: {e}")
            return False

    def get_global_ranking(self, limit=10):
        """Obtiene el ranking global de usuarios"""
        if self.user_stats_collection is None:
            return []

        try:
            ranking = self.user_stats_collection.find(
                {"puntaje_total": {"$gt": 0}}
            ).sort("puntaje_total", -1).limit(limit)

            ranking_list = []
            for i, user in enumerate(ranking, 1):
                user_data = {
                    "posicion": i,
                    "username": user.get("username", "Unknown"),
                    "puntaje": user.get("puntaje_total", 0),
                    "problemas": user.get("problemas_resueltos", 0)
                }
                ranking_list.append(user_data)

            return ranking_list
        except Exception as e:
            print(f"❌ Error obteniendo ranking: {e}")
            return []

    # =============================================
    # MÉTODOS PARA PROBLEMAS
    # =============================================

    def get_all_problem_titles(self):
        """Obtiene todos los títulos de problemas"""
        if self.problems_collection is None:
            return []
        try:
            problems_cursor = self.problems_collection.find({})
            problems_list = list(problems_cursor)

            formatted_list = []
            for problem in problems_list:
                title = problem.get('title', 'Sin título')
                difficulty = problem.get('difficulty', 'Desconocida')

                if difficulty == "Fácil":
                    icon = "🟢"
                elif difficulty == "Medio":  # ✅ CORREGIDO: era "Media"
                    icon = "🟡"
                elif difficulty == "Difícil":
                    icon = "🔴"
                else:
                    icon = "⚪"

                formatted_list.append(f"{icon} {title} - {difficulty}")

            return formatted_list

        except Exception as e:
            print(f"❌ Error al obtener problemas: {e}")
            return []

    def get_problem_details(self, title):
        """Obtiene detalles de un problema específico"""
        if self.problems_collection is None:
            return None
        try:
            # Limpiar el título (remover iconos y dificultad si existen)
            clean_title = title
            if ' - ' in title:
                clean_title = title.split(' - ')[0].split(' ', 1)[1]

            problem_data = self.problems_collection.find_one({"title": clean_title})

            if problem_data and '_id' in problem_data:
                problem_data['_id'] = str(problem_data['_id'])

            return problem_data

        except Exception as e:
            print(f"❌ Error al obtener detalles: {e}")
            return None

    def insert_problem(self, problem_data):
        """Inserta un nuevo problema en la colección 'problems'"""
        if self.problems_collection is None:
            print("❌ Colección 'problems' no disponible")
            return False

        try:
            # Verificar si ya existe un problema con el mismo título
            existing_problem = self.problems_collection.find_one({"title": problem_data["title"]})
            if existing_problem:
                print(f"❌ Ya existe un problema con el título: {problem_data['title']}")
                return False

            # Preparar el documento completo del problema
            problem_document = {
                "title": problem_data["title"],
                "category": problem_data["category"],
                "difficulty": problem_data["difficulty"],
                "statement": problem_data["statement"],
                "big_o_expected": problem_data["big_o_expected"],
                "examples": problem_data["examples"],
                "fecha_creacion": datetime.now(),
                "activo": True
            }

            # Insertar el nuevo problema
            result = self.problems_collection.insert_one(problem_document)

            success = result.inserted_id is not None

            if success:
                print(f"✅ Problema '{problem_data['title']}' insertado correctamente en MongoDB")
                print(f"   - ID: {result.inserted_id}")
                print(f"   - Categoría: {problem_data['category']}")
                print(f"   - Dificultad: {problem_data['difficulty']}")
                print(f"   - Ejemplos: {len(problem_data['examples'])}")
            else:
                print(f"❌ Error al insertar problema '{problem_data['title']}'")

            return success

        except Exception as e:
            print(f"❌ Error insertando problema: {e}")
            return False

    # =============================================
    # MÉTODOS PARA ADMINISTRADORES
    # =============================================

    def is_user_admin(self, username):
        """Verifica si un usuario es administrador"""
        if self.admins_collection is None:
            print("⚠️  Colección 'admins' no disponible")
            return False

        try:
            admin_user = self.admins_collection.find_one({"username": username})
            is_admin = admin_user is not None

            if is_admin:
                print(f"👑 Usuario '{username}' es administrador")
            else:
                print(f"👤 Usuario '{username}' NO es administrador")

            return is_admin

        except Exception as e:
            print(f"❌ Error verificando admin: {e}")
            return False

    def create_admin_user(self, username, email=None):
        """Crea un nuevo usuario administrador"""
        if self.admins_collection is None:
            return False

        try:
            admin_data = {
                "username": username,
                "email": email or f"{username}@codecoach.com",
                "fecha_creacion": datetime.now(),
                "activo": True
            }

            result = self.admins_collection.insert_one(admin_data)

            if result.inserted_id:
                print(f"✅ Administrador '{username}' creado exitosamente")
                return True
            else:
                return False

        except DuplicateKeyError:
            print(f"❌ Administrador '{username}' ya existe")
            return False
        except Exception as e:
            print(f"❌ Error creando administrador: {e}")
            return False

    def get_all_admins(self):
        """Obtiene todos los usuarios administradores"""
        if self.admins_collection is None:
            return []

        try:
            admins = list(self.admins_collection.find({}))
            return admins
        except Exception as e:
            print(f"❌ Error obteniendo administradores: {e}")
            return []

    # =============================================
    # MÉTODOS DE UTILIDAD
    # =============================================

    def initialize_default_data(self):
        """Inicializa datos por defecto en la base de datos"""
        try:
            # Crear un usuario administrador por defecto si no existe
            if self.admins_collection is not None:
                default_admin = self.admins_collection.find_one({"username": "admin"})
                if not default_admin:
                    self.create_admin_user("admin", "admin@codecoach.com")
                    print("✅ Usuario administrador 'admin' creado por defecto")

            # Verificar si hay problemas en la base de datos
            if self.problems_collection is not None:
                problem_count = self.problems_collection.count_documents({})
                print(f"📊 Número de problemas en la base de datos: {problem_count}")

            return True

        except Exception as e:
            print(f"❌ Error inicializando datos por defecto: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Conexión MongoDB cerrada")

    def get_database_status(self):
        """Obtiene el estado de la base de datos"""
        status = {
            "connected": self.client is not None,
            "collections": {}
        }

        if self.client:
            try:
                collections = self.db.list_collection_names()
                for collection_name in ["users", "problems", "user_stats", "admins"]:
                    status["collections"][collection_name] = collection_name in collections

                    # Contar documentos si la colección existe
                    if collection_name in collections:
                        collection = self.db[collection_name]
                        count = collection.count_documents({})
                        status["collections"][f"{collection_name}_count"] = count
            except Exception as e:
                status["error"] = str(e)

        return status