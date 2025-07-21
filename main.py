import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from Funciones.login_manager import LoginManager
from main_window import MainWindow
from db.mongo_connection import get_db_connection, get_usuario_by_username

class Application:
    def __init__(self, app):
        self.app = app
        self.app.setStyle("Fusion")
        self.db = get_db_connection()
        self.setup_login()

        # Configuración de la aplicación
        self.app.setApplicationName("Sistema de Gestión")
        self.app.setApplicationVersion("1.0.0")

    def setup_login(self):
        """Configura y muestra la ventana de login"""
        # Asegurarse de que no haya una ventana de login previa
        if hasattr(self, 'login_window') and self.login_window:
            try:
                self.login_window.close()
                self.login_window.deleteLater()
            except:
                pass
                
        self.login_window = LoginManager(db=self.db)
        self.login_window.login_successful.connect(self.on_login_successful)
        self.login_window.show()

    def on_login_successful(self, username):
        """Maneja el inicio de sesión exitoso"""
        try:
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None
                
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.close()
                self.main_window.deleteLater()
                
            # Obtener los datos completos del usuario
            usuario = get_usuario_by_username(username)
        
            if not usuario:
                raise Exception("No se pudo obtener la información del usuario")
            
            self.main_window = MainWindow(
                username=username, 
                email=usuario.get('correo', 'No disponible'),
                db=self.db
            )
            self.main_window.show()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo iniciar la aplicación: {str(e)}")
            self.setup_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("material_theme.qss", "r") as file:
        app.setStyleSheet(file.read())

    app_instance = Application(app)
    sys.exit(app.exec())