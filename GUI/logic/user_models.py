# logic/user_models.py
from .database_handler import DatabaseHandler


class User:
    """
    Modelo de usuario que se sincroniza con la base de datos
    """

    def __init__(self, username, contrasena="", stats_data=None):
        self.username = username
        self.contrasena = contrasena
        self.db_handler = DatabaseHandler()

        # Inicializar estadísticas
        self.puntaje_total = 0
        self.problemas_resueltos = 0
        self.ejercicios_completados = []
        self.facil_resueltos = 0
        self.medio_resueltos = 0
        self.dificil_resueltos = 0
        self.racha_actual = 0
        self.mejor_racha = 0

        # Cargar datos desde MongoDB
        if stats_data:
            self.load_from_stats(stats_data)
        else:
            self.load_from_db()

    def load_from_db(self):
        """Carga los datos actualizados desde MongoDB"""
        if self.db_handler and self.username:
            stats_data = self.db_handler.get_user_stats(self.username)
            if stats_data:
                self.load_from_stats(stats_data)
                print(f"✅ Datos de {self.username} cargados desde DB")
            else:
                print(f"⚠️  No se encontraron datos en DB para {self.username}")

    def load_from_stats(self, stats_data):
        """Carga datos desde un diccionario de estadísticas"""
        self.puntaje_total = stats_data.get('puntaje_total', 0)
        self.problemas_resueltos = stats_data.get('problemas_resueltos', 0)
        self.ejercicios_completados = stats_data.get('ejercicios_completados', [])
        self.facil_resueltos = stats_data.get('facil_resueltos', 0)
        self.medio_resueltos = stats_data.get('medio_resueltos', 0)
        self.dificil_resueltos = stats_data.get('dificil_resueltos', 0)
        self.racha_actual = stats_data.get('racha_actual', 0)
        self.mejor_racha = stats_data.get('mejor_racha', 0)

    def refresh_stats(self):
        """Actualiza las estadísticas desde la base de datos"""
        self.load_from_db()

    def update_progress(self, problem_title, difficulty, points=10):
        """Actualiza el progreso del usuario en la base de datos"""
        if self.db_handler:
            success = self.db_handler.update_user_score(
                self.username, problem_title, difficulty, points
            )
            if success:
                self.refresh_stats()  # Recargar stats actualizados
            return success
        return False

    def to_dict(self):
        """Convierte a diccionario para JSON"""
        return {
            'username': self.username,
            'puntaje_total': self.puntaje_total,
            'problemas_resueltos': self.problemas_resueltos,
            'ejercicios_completados': self.ejercicios_completados,
            'facil_resueltos': self.facil_resueltos,
            'medio_resueltos': self.medio_resueltos,
            'dificil_resueltos': self.dificil_resueltos,
            'racha_actual': self.racha_actual,
            'mejor_racha': self.mejor_racha
        }

    def get_stats_for_display(self):
        """Devuelve estadísticas formateadas para mostrar en GUI"""
        return {
            'Puntos Totales': str(self.puntaje_total),
            'Problemas Resueltos': str(self.problemas_resueltos),
            'Ejercicios Únicos': str(len(self.ejercicios_completados)),
            'Racha Actual': str(self.racha_actual),
            'Mejor Racha': str(self.mejor_racha),
            'Fácil Resueltos': str(self.facil_resueltos),
            'Medio Resueltos': str(self.medio_resueltos),
            'Difícil Resueltos': str(self.dificil_resueltos)
        }

    def __str__(self):
        return (f"User(username='{self.username}', puntaje={self.puntaje_total}, "
                f"problemas={self.problemas_resueltos}, racha={self.racha_actual})")