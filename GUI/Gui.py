    # Gui.py
import sys
from PyQt5.QtWidgets import QApplication
from LoginWindow import LoginWindow

def main():
    """Módulo principal de ejecución"""
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    app.setApplicationName("leetAI")
    app.setApplicationVersion("1.0.0")

    # Importar y mostrar ventana de login
    try:
        login_window = LoginWindow()
        login_window.show()
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo iniciar la aplicación: {e}")
        return 1

    # Ejecutar loop de la aplicación
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()