import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from Funciones.login_manager import LoginManager
from main_window import MainWindow
from db.mongo_connection import get_db_connection

class Application:
    def __init__(self, app):
        self.app = app
        self.app.setStyle("Fusion")
        self.db = get_db_connection()
        self.login_window = LoginManager(db=self.db)
        self.login_window.login_successful.connect(self.on_login_successful)

        # Configuración de la aplicación
        self.app.setApplicationName("Sistema de Gestión")
        self.app.setApplicationVersion("1.0.0")

        # Mostrar la ventana de login
        self.show_login()

    def show_login(self):
        """Muestra la ventana de inicio de sesión"""
        print("[DEBUG] Mostrando ventana de login...")
        print("[DEBUG] Señal login_successful conectada")
        self.login_window.show()

    def on_login_successful(self, username):
        """Maneja el inicio de sesión exitoso"""
        print(f"[DEBUG] Inicio de sesión exitoso para: {username}")
        try:
            self.login_window.close()
            print("[DEBUG] Ventana de login cerrada")
            self.main_window = MainWindow(username=username, db=self.db)
            print("[DEBUG] Ventana principal creada")
            self.main_window.show() 
            print("[DEBUG] Ventana principal mostrada")
        except Exception as e:
            print(f"[ERROR] Error al abrir la ventana principal: {str(e)}")
            QMessageBox.critical(None, "Error", f"No se pudo abrir la aplicación: {str(e)}")

if __name__ == "__main__":
    print("[DEBUG] Iniciando aplicación...")

    app = QApplication(sys.argv)
    with open("material_theme.qss", "r") as file:
        app.setStyleSheet(file.read())

    app_instance = Application(app)
    sys.exit(app.exec())