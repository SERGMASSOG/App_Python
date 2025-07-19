from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor, QIcon
import hashlib
import os

class LoginManager(QWidget):
    login_successful = Signal(str)

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db #Conexión a la base de datos
        self.setWindowTitle("Inicio de Sesión")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        screen = self.screen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        #Configuración del panel izquierdo
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #FF6B00;
                border: none;
            }
        """)
        #Ancho del panel izquierdo
        left_panel.setFixedWidth(400)

        #Configuración del panel izquierdo
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setSpacing(20)
        left_layout.addStretch()

        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo_white.png")
        #Configuración del logo
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            title = QLabel("Sistema de Gestión")
            title.setFont(QFont("Arial", 24, QFont.Bold))
            title.setStyleSheet("color: white;")
            logo_label = title

        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        desc_label = QLabel("Sistema Integral \n Gestión de Inventario")
        desc_label.setFont(QFont("Arial", 24, QFont.Bold))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                margin-top: 20px;
            }
        """)
        left_layout.addWidget(desc_label)
        left_layout.addStretch()

        copyright_label = QLabel(" 2024 Todos los derechos reservados \n Ingeniero Sergio Masso Giraldo")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        left_layout.addWidget(copyright_label)

        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
            }
        """)

        #Configuración del panel derecho
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(80, 40, 80, 40)
        right_layout.setSpacing(20)

        title = QLabel("Bienvenido")
        title.setFont(QFont("Arial", 50, QFont.Bold))
        title.setStyleSheet("color: #333333;font-size: 50px;")
        title.setAlignment(Qt.AlignCenter)
        right_layout.addStretch()
        right_layout.addWidget(title)

        #Configuración del subtitulo
        subtitulo = QLabel("Inicia sesión para continuar")
        subtitulo.setFont(QFont("Arial", 24, QFont.Bold))
        subtitulo.setStyleSheet("color: #666666;font-size: 24px;") 
        subtitulo.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(subtitulo)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        #Configuración del formulario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                min-width: 250px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #FF6B00;
            }
        """)

        #Configuración del campo de contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                min-width: 250px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #FF6B00;
            }
        """)

        show_password_btn = QPushButton("Mostrar contraseña")
        show_password_btn.setCheckable(True)
        show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: none;
                padding: 5px 0;
                text-align: left;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #FF6B00;
                text-decoration: underline;
            }
        """)
        show_password_btn.toggled.connect(self.toggle_password_visibility)

        login_btn = QPushButton("Iniciar Sesión")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #E05E00;
            }
            QPushButton:pressed {
                background-color: #CC5200;
            }
        """)
        login_btn.clicked.connect(self.attempt_login)

        #Configuración del formulario
        form_layout.addWidget(QLabel("Usuario"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Contraseña"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(show_password_btn, alignment=Qt.AlignRight)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_btn)
        
        #Configuración del formulario
        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        self.username_input.returnPressed.connect(login_btn.click)
        self.password_input.returnPressed.connect(login_btn.click)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.sender().setText("Ocultar contraseña")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.sender().setText("Mostrar contraseña")

    #Conectando con la base de datos
    def attempt_login(self):
        from db.mongo_connection import verificar_credenciales
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return

        # Verificar credenciales
        usuario = verificar_credenciales(username, password)
        if usuario:  # Si se encontró un usuario válido
            try:
                self.login_successful.emit(username)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al iniciar sesión: {str(e)}")
        else:
            QMessageBox.critical(
                self, 
                "Error", 
                "Usuario o contraseña incorrectos. Verifique sus credenciales."
            )
            self.password_input.clear()
            self.password_input.setFocus()
