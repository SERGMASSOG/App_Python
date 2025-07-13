from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from main_window import MainWindow
from db.mongo_connection import get_usuario_by_username

main_window = None

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setFixedSize(1000, 700)
        self.setWindowIcon(QIcon("Style_app/login.png"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Panel izquierdo
        left_panel = QFrame()
        left_panel.setFixedWidth(420)
        left_panel.setStyleSheet('''
            QFrame {
                background: #111;
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }
        ''')
        left_layout = QVBoxLayout(left_panel)
        logo = QLabel()
        pixmap = QPixmap("Style_app/login.png").scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addStretch()
        left_layout.addWidget(logo)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel)

        # Panel derecho
        right_panel = QFrame()
        right_panel.setStyleSheet('''
            QFrame {
                background: #F0460E;
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        ''')
        form_layout = QVBoxLayout(right_panel)
        form_layout.setContentsMargins(48, 48, 48, 48)
        form_layout.setSpacing(18)

        title = QLabel("Bienvenido")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #fff;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Ingresa a tu cuenta")
        subtitle.setStyleSheet("font-size: 22px; color: #fff; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignCenter)

        user_label = QLabel("Usuario")
        user_label.setStyleSheet("color: #fff; font-size: 17px; font-weight: bold;")
        self.username = QLineEdit()
        self.username.setStyleSheet("background: #fff; color: #111; font-size: 16px; border-radius: 8px; padding: 10px;")

        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet("color: #fff; font-size: 17px; font-weight: bold;")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet("background: #fff; color: #111; font-size: 16px; border-radius: 8px; padding: 10px;")

        login_button = QPushButton("Iniciar sesión")
        login_button.setStyleSheet('''
            QPushButton {
                background: #fff;
                color: #F0460E;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background: #111;
                color: #fff;
                border: 1.5px solid #fff;
            }
        ''')
        login_button.clicked.connect(self.check_login)

        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(10)
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.username)
        form_layout.addWidget(pass_label)
        form_layout.addWidget(self.password)
        form_layout.addWidget(login_button)
        form_layout.addStretch()
        right_panel.setLayout(form_layout)

        layout.addWidget(right_panel)

    def check_login(self):
        global main_window
        user = self.username.text().strip().lower()
        pwd = self.password.text().strip()

        usuario = get_usuario_by_username(user)
        print(f"[DEBUG] Usuario en BD: {usuario}")  # Debug

        if usuario:
            if usuario.get("contrasena") == pwd:
                main_window = MainWindow()
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
                self.hide()
                QMessageBox.information(main_window, "Correcto", "Inicio exitoso")
            else:
                QMessageBox.warning(self, "Error", "Contraseña incorrecta")
        else:
            QMessageBox.warning(self, "Error", "Usuario no encontrado")
