# Gui.py - PUNTO DE ENTRADA PRINCIPAL
import sys
import os

# Configurar paths ANTES de cualquier import
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Módulo principal de ejecución"""
    from PyQt5.QtWidgets import QApplication
    from LoginWindow import LoginWindow
    
    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    app.setApplicationName("leetAI")
    app.setApplicationVersion("1.0.0")

    try:
        print("🚀 Iniciando leetAI...")
        login_window = LoginWindow()
        login_window.show()
        print("✅ Aplicación iniciada correctamente")
        
        # Ejecutar loop de la aplicación
        return app.exec_()
        
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())