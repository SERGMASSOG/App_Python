import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from ui_effects import UIEffects

# Importar gestores de funcionalidades
from Funciones.crm import CRMManager
from Funciones.ventas import VentasManager
from Funciones.contabilidad import ContabilidadManager
from Funciones.inventario_manager import InventarioManager
from Funciones.dashboard import DashboardManager

class MainWindow(QMainWindow):
    def __init__(self, username, email, db, parent=None):
        super().__init__(parent)
        self.username = username
        self.email = email
        self.db = db  # Primero asignar db
        self.setWindowTitle("Sistema de Gestión")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("assets/icons/logo.png"))
        
        # Inicializar manejadores después de tener self.db
        self.dashboard = DashboardManager(self.db, parent=self)
        self.crm_manager = CRMManager()
        self.ventas_manager = VentasManager(self.db, parent=self)
        self.contabilidad_manager = ContabilidadManager()
        self.inventario_manager = InventarioManager(self.db, parent=self)
        
        # Configurar la interfaz de usuario
        self.setup_ui()
        
        # Configurar el manejador de redimensionamiento
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        """Maneja el evento de redimensionamiento de la ventana"""
        width = self.width()
        height = self.height()

        # Evitar recalcular si el tamaño es muy similar
        if hasattr(self, '_last_size'):
            last_width, last_height = self._last_size
            if abs(width - last_width) < 100 and abs(height - last_height) < 100:
                return

        # Actualizar el tamaño de las tarjetas si están disponibles
        if hasattr(self, 'dashboard') and hasattr(self.dashboard, 'metrics'):
            for card in self.dashboard.metrics.values():
                if width < 1200:  # Si la ventana es pequeña
                    card.setMaximumWidth(250)
                else:
                    card.setMaximumWidth(350)

        # Guardar el tamaño actual para comparación
        self._last_size = (width, height)

    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra lateral
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Contenedor para el área de contenido y la barra superior
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_container.setStyleSheet("""
            QWidget#contentContainer {
                background-color: #f8fafc;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Barra superior
        self.top_bar = self.create_top_bar()
        content_layout.addWidget(self.top_bar)

        # Área de contenido
        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        self.content_area.setStyleSheet("""
            QWidget#contentArea {
                background-color: #ffffff;
                border-top-left-radius: 12px;
                border: 1px solid #e2e8f0;
                border-right: none;
                border-bottom: none;
            }
        """)

        # Layout del área de contenido
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Agregar los manejadores al área de contenido
        self.content_layout.addWidget(self.dashboard)
        self.content_layout.addWidget(self.crm_manager)
        self.content_layout.addWidget(self.inventario_manager)
        self.content_layout.addWidget(self.ventas_manager)
        self.content_layout.addWidget(self.contabilidad_manager)

        # Ocultar todos excepto el dashboard
        self.crm_manager.hide()
        self.inventario_manager.hide()
        self.ventas_manager.hide()
        self.contabilidad_manager.hide()

        content_layout.addWidget(self.content_area, 1)
        main_layout.addWidget(content_container, 1)

        self.show_tab("dashboard")

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(250)
        sidebar.setStyleSheet("""
        QFrame {
            background-color: #2c3e50;
        }
        QPushButton {
            text-align: left;
            padding: 12px 20px;
            border: none;
            color: #ecf0f1;
            background: transparent;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #34495e;
        }
        QPushButton:checked {
            background-color: #FF6B00;
            font-weight: bold;
        }
        QPushButton#logoBtn {
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            border-bottom: 1px solid #34495e;
        }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(10)

        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 30)

        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("assets/icons/logo.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.app_title = QLabel("Sistema de Gestión")
        self.app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-left: 10px;
            }
        """)

        header_layout.addWidget(self.logo)
        header_layout.addWidget(self.app_title)
        header_layout.addStretch()

        layout.addWidget(header)

        self.menu_buttons = {}
        menu_items = [
            ("dashboard", "Dashboard", "home"),
            ("crm", "Clientes", "users"),
            ("inventario", "Inventario", "package"),
            ("ventas", "Ventas", "dollar"),
            ("contabilidad", "Contabilidad", "bar-chart-2")
        ]

        for item_id, text, icon in menu_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setIcon(QIcon(f"assets/icons/{icon}.png"))
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(lambda checked, x=item_id: self.show_tab(x))
            self.menu_buttons[item_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        user_widget = QWidget()
        user_widget.setStyleSheet("""
            QWidget {
                background-color: #334155;
                border-radius: 6px;
                margin: 12px;
                padding: 12px;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QLabel#username {
                font-weight: bold;
                font-size: 14px;
            }
        """)

        user_layout = QVBoxLayout(user_widget)

        user_name = QLabel(self.username)
        user_name.setObjectName("username")
        user_email = QLabel(self.email)

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setIcon(QIcon("assets/icons/log-out.png"))
        btn_logout.setIconSize(QSize(16, 16))
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_logout.clicked.connect(self.logout)

        user_layout.addWidget(user_name)
        user_layout.addWidget(user_email)
        user_layout.addWidget(btn_logout)

        layout.addWidget(user_widget)

        return sidebar

    def create_top_bar(self):
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame#topBar {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
                padding: 0 20px;
            }
            QLabel#pageTitle {
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
            }
        """)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(0, 0, 20, 0)

        self.page_title = QLabel("Panel de Control")
        self.page_title.setObjectName("pageTitle")

        self.mobile_menu_btn = QPushButton()
        self.mobile_menu_btn.setIcon(QIcon("assets/icons/menu.png"))
        self.mobile_menu_btn.setIconSize(QSize(24, 24))
        self.mobile_menu_btn.setFixedSize(40, 40)
        self.mobile_menu_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        self.mobile_menu_btn.clicked.connect(self.toggle_sidebar)

        layout.addWidget(self.mobile_menu_btn)
        layout.addWidget(self.page_title)
        layout.addStretch()
        # Botón de notificaciones
        btn_notifications = QPushButton()
        btn_notifications.setIcon(QIcon("assets/icons/bell.png"))
        btn_notifications.setIconSize(QSize(24, 24))
        btn_notifications.setFixedSize(40, 40)
        btn_notifications.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)

        self.user_btn = QPushButton()
        self.user_btn.setIcon(QIcon("assets/icons/user.png"))
        self.user_btn.setIconSize(QSize(24, 24))
        self.user_btn.setFixedSize(40, 40)
        self.user_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #e2e8f0;
                border-radius: 20px;
                background: white;
            }
            QPushButton:hover {
                border-color: #cbd5e1;
            }
        """)

        layout.addWidget(btn_notifications)
        layout.addWidget(self.user_btn)

        return top_bar

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setText("☰")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("✕")

    def show_tab(self, tab_id):
        self.dashboard.hide()
        self.crm_manager.hide()
        self.inventario_manager.hide()
        self.ventas_manager.hide()
        self.contabilidad_manager.hide()

        if tab_id == "dashboard":
            self.dashboard.show()
            self.page_title.setText("Dashboard")
        elif tab_id == "crm":
            self.crm_manager.show()
            self.page_title.setText("Gestión de Clientes")
        elif tab_id == "inventario":
            self.inventario_manager.show()
            self.page_title.setText("Gestión de Inventario")
        elif tab_id == "ventas":
            self.ventas_manager.show()
            self.page_title.setText("Ventas")
        elif tab_id == "contabilidad":
            self.contabilidad_manager.show()
            self.page_title.setText("Contabilidad")

        for btn_id, btn in self.menu_buttons.items():
            btn.setChecked(btn_id == tab_id)

    def logout(self):
        """Cierra la sesión y cierra la aplicación"""
        self.close()
        import sys
        from main import main
        sys.exit(main())

    def show_message(self, title, message, is_error=False):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #d32f2f if is_error else #388e3c;
            }
        """)
        msg.exec_()

    def setup_ui_effects(self):
        """Configura los efectos de la interfaz de usuario"""
        # Configurar transiciones para el stacked widget principal
        UIEffects.setup_stack_transition(self.content_area)
        
        # Aplicar efectos hover a las tarjetas del dashboard
        if hasattr(self, 'dashboard'):
            self.setup_dashboard_effects()
            
        # Aplicar efectos a los botones del menú lateral
        for btn in self.menu_buttons.values():
            UIEffects.create_hover_button(btn, "#2D3748")
    
    def setup_dashboard_effects(self):
        """Configura efectos para los elementos del dashboard"""
        # Obtener todos los frames que son tarjetas en el dashboard
        for child in self.dashboard.findChildren(QFrame):
            if child.objectName().startswith('card_'):
                UIEffects.create_hover_card(child, "#2D3748")