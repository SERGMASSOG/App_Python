from PySide6.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from main_window import MainWindow

main_window = None

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(1200, 900)
        self.setWindowIcon(QIcon("logo.ico"))
        self.setStyleSheet('''
            QDialog {
                background: #FFFFFF;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin: 5px;
                padding: 5px;
                border: 1px solid #FFFFFF;
            }
            QLabel {
                font-size: 20px;
                color: #111;
                font-weight: bold;
            }
            QLineEdit {
                font-size: 20px;
                padding: 8px;
                border: 1px solid #FFFFFF;
                border-radius: 6px;
                margin-bottom: 8px;
                background: #FFFFFF;
                color: #222;
            }
            QPushButton {
                background: #DB6EA8;
                color: #fff;
                font-size: 20px;
                border: none;
                border-radius: 6px;
                padding: 10px 0;
                margin-top: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #DB6EA8;
                color: #fff;
            }
            QPushButton:pressed {
                background: #D36EDB;
                color: #D36EDB;
            }
            QFrame {
                background: #FFFFFF;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin: 5px;
                padding: 5px;
                border: 1px solid #FFFFFF;
            }
        ''')
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Panel izquierdo
        left_panel = QLabel()
        left_panel.setFixedSize(720, 900)
        left_panel.setStyleSheet('''
            QLabel {
                border-radius: 5px;
            }
            QFrame {
                background: #DB6EA8;
                border-radius:  5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
        ''')
        left_panel.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap('inicio.png')
        pixmap = pixmap.scaled(720, 900, Qt.KeepAspectRatio)
        left_panel.setPixmap(pixmap)
        layout.addWidget(left_panel)

        # Panel derecho
        right_panel = QFrame()
        right_panel.setMinimumSize(380, 600)
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setContentsMargins(20, 20, 20, 20)
        right_panel_layout.setSpacing(10)

        # Título
        self.title = QLabel("Angel Boutique")
        self.title.setStyleSheet('font-size: 40px; font-weight: bold; color: #111; margin-bottom: 18px; font-family:"Franklin Gothic Medium"; sans-serif;')
        self.title.setAlignment(Qt.AlignCenter)
        right_panel_layout.addWidget(self.title)
        # Subtítulo
        self.subtitle = QLabel("Iniciar Sesión")
        self.subtitle.setStyleSheet('font-size: 30px; font-weight: bold; color:#DB6EA8; margin-bottom: 12px; font-family:"Franklin Gothic Medium"; sans-serif;')
        self.subtitle.setAlignment(Qt.AlignCenter)
        right_panel_layout.addWidget(self.subtitle)

        # Campos de usuario y contraseña
        self.label = QLabel("Usuario:")
        self.label.setStyleSheet('font-size: 20px; font-weight: bold; color: #111; margin-bottom: 12px; font-family: "Arial";')
        self.username = QLineEdit()
        self.username.setMinimumHeight(36)
        self.label2 = QLabel("Contraseña:")
        self.label2.setStyleSheet('font-size: 20px; font-weight: bold; color: #111; margin-bottom: 12px; font-family: "Arial";')
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(36)
        self.button = QPushButton("Iniciar sesión")
        self.button.setStyleSheet('''
            font-size: 20px; 
            font-weight: bold; 
            margin-bottom: 12px; 
            margin-top: 12px; 
            padding: 12px; 
            border-radius: 5px;
            background: #DB6EA8;
            border: none;
            cursor: pointer;
            transition: background 0.3s ease;
            color: #fff;
            font-family: "Arial";
        ''')
        self.button.setMinimumHeight(40)
        self.button.clicked.connect(self.check_login)
        right_panel_layout.addWidget(self.label)
        right_panel_layout.addWidget(self.username)
        right_panel_layout.addWidget(self.label2)
        right_panel_layout.addWidget(self.password)
        right_panel_layout.addWidget(self.button)
        right_panel_layout.addStretch()
        right_panel.setLayout(right_panel_layout)
        layout.addWidget(right_panel)
        self.setLayout(layout)

    def check_login(self):
        global main_window
        user = self.username.text()
        pwd = self.password.text()
        if user == "admin" and pwd == "admin":
            main_window = MainWindow()
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            self.hide()  # Oculta la ventana de login, no la destruye
            QMessageBox.information(main_window, "Correcto", "Inicio de sesión exitoso")
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")
