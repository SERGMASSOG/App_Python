from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QSizePolicy, QScrollArea,
    QPushButton, QComboBox, QMessageBox, QFileDialog, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, QDate, QSize
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QSizePolicy, QScrollArea,
    QPushButton, QComboBox, QMessageBox, QFileDialog, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, QDate, QSize
from datetime import datetime, timedelta
from bson.decimal128 import Decimal128
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QPixmap, QIcon, QColor, QFont
from dateutil.relativedelta import relativedelta
import numpy as np
import traceback
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

class DashboardManager(QScrollArea):
    """
    Panel principal de dashboard para métricas y gráficos de negocio.
    Incluye auto-refresh, feedback visual, controles interactivos y manejo robusto de errores.
    """
    def __init__(self, db, parent=None, username=None):
            super().__init__(parent)
            self.db = db
            self.username = username or "Usuario"
            self.refresh_interval_ms = 300000  # 5 minutos por default
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_all)
            self.is_loading = False
            self.error_message = ""
            self.date_range = "mes"  # Opciones: "dia", "semana", "mes", "año"
            self.metrics = {}  # Inicializar el diccionario de métricas
            self.setup_ui()
            self.refresh_all()
            
            # Actualizar nombre de usuario si está disponible
            if hasattr(self, 'username_label') and self.username:
                self.username_label.setText(self.username)

    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard"""
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)

        # Widget principal que contendrá ambos paneles
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========== PANEL IZQUIERDO (Contenido principal) ==========
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: #FFFFFF; border: none; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)  # Eliminar espaciado entre widgets principales

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)  # Reducir márgenes verticales
        content_layout.setSpacing(12)  # Reducir espaciado entre elementos

        # ========== BIENVENIDA ==========
        welcome_container = QFrame()
        welcome_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #E0E0E0;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_container)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(8)  # Reducir espaciado entre título y fecha

        welcome_title = QLabel(f"¡Bienvenido/a {self.username}!")
        welcome_title.setFont(QFont("Arial", 16, QFont.Bold))
        welcome_title.setStyleSheet("color: #333333; margin-bottom: 5px;")
        welcome_title.setAlignment(Qt.AlignLeft)

        date_label = QLabel(QDate.currentDate().toString("dddd, d 'de' MMMM 'de' yyyy"))
        date_label.setFont(QFont("Arial", 14))
        date_label.setStyleSheet("color: #555555;")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(date_label)
        content_layout.addWidget(welcome_container)

        # ========== MÉTRICAS ==========
        metrics_container = QWidget()
        metrics_layout = QGridLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)
        metrics_layout.setVerticalSpacing(10)

        self.metric_cards = {}
        metrics = [
            ("Ventas Totales", "$0", "#FF6B00", "dollar-sign"),
            ("Productos Vendidos", "0", "#FF6B00", "shopping-cart"),
            ("Productos en Stock", "0", "#FF6B00", "box"),
            ("Productos Agotados", "0", "#FF6B00", "x-circle")
        ]

        # Definición de métricas con colores consistentes
        self.metric_cards = {
            "ventas_totales": self.create_metric_card("Ventas Totales", "$0", "#4CAF50", "dollar-sign"),
            "productos_vendidos": self.create_metric_card("Productos Vendidos", "0", "#2196F3", "shopping-cart"),
            "productos_stock": self.create_metric_card("Productos en Stock", "0", "#9C27B0", "box"),
            "productos_agotados": self.create_metric_card("Productos Agotados", "0", "#FF9800", "x-circle")
        }

        # Añadir tarjetas al grid
        for i, (key, card) in enumerate(self.metric_cards.items()):
            card.setFixedHeight(120)
            metrics_layout.addWidget(card, i // 2, i % 2)

        content_layout.addWidget(metrics_container)
        content_layout.addStretch()
        
            # Reducir tamaño de las tarjetas
        for i, (title, value, color, icon) in enumerate(metrics):
            card = self.create_metric_card(title, value, color, icon)
            card.setFixedHeight(120)  # Altura reducida
            metrics_layout.addWidget(card, i // 2, i % 2)
            self.metric_cards[title.lower().replace(" ", "_")] = card

        content_layout.addWidget(metrics_container)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        left_layout.addWidget(scroll_area)

        # ========== PANEL DERECHO (Barra lateral) ==========
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-left: 1px solid #E0E0E0;
            }
        """)
        right_panel.setMinimumWidth(280)  # Ancho mínimo reducido
        right_panel.setMaximumWidth(320)  # Ancho máximo reducido
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)  # Márgenes reducidos
        right_layout.setSpacing(15)  # Espaciado reducido

        # Logo más pequeño
        logo_container = QLabel()
        logo_pixmap = QPixmap("assets/app_icon.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_container.setPixmap(logo_pixmap)
        logo_container.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(logo_container)

        # Título más pequeño
        title_label = QLabel("SISTEMA DE GESTIÓN")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333333; margin: 10px 0;")
        right_layout.addWidget(title_label)

        # Sección de usuario más compacta
        user_section = QFrame()
        user_section.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        user_layout = QVBoxLayout(user_section)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)

        user_icon = QLabel()
        user_pixmap = QPixmap("assets/icons/users.png")
        if not user_pixmap.isNull():
            user_icon.setPixmap(user_pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        user_icon.setAlignment(Qt.AlignCenter)

        self.username_label = QLabel(self.username)
        self.username_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.username_label.setStyleSheet("color: #333333; margin-top: 5px;")
        self.username_label.setAlignment(Qt.AlignCenter)

        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.username_label)
        right_layout.addWidget(user_section)

        # Sección redes sociales más compacta
        social_section = QFrame()
        social_section.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        social_layout = QVBoxLayout(social_section)
        social_layout.setContentsMargins(0, 0, 0, 0)
        social_layout.setSpacing(10)

        social_title = QLabel("Redes Sociales")
        social_title.setFont(QFont("Arial", 14, QFont.Bold))
        social_title.setStyleSheet("color: #333333;")
        social_title.setAlignment(Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)

        def social_button(icon_path, border_color, hover_color, url):
            btn = QPushButton()
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(30, 30))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    border: 2px solid {border_color};
                    border-radius: 20px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
            btn.clicked.connect(lambda: self.open_url(url))
            return btn

        buttons_layout.addWidget(social_button("assets/icons/instagram.png", "#E1306C", "rgba(225,48,108,0.1)", "https://www.instagram.com/"))
        buttons_layout.addWidget(social_button("assets/icons/whatsapp.png", "#25D366", "rgba(37,211,102,0.1)", "https://web.whatsapp.com/"))
        buttons_layout.addWidget(social_button("assets/icons/dian.png", "#0033A0", "rgba(0,51,160,0.1)", "https://www.dian.gov.co/transaccional/paginas/transaccional.aspx"))

        social_layout.addWidget(social_title)
        social_layout.addLayout(buttons_layout)
        right_layout.addWidget(social_section)

        right_layout.addStretch()

        # ========== ENSAMBLAR LAYOUT PRINCIPAL ==========
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        container_layout.addWidget(left_panel, 1)
        container_layout.addWidget(right_panel, 0)
        
        self.setWidget(container)
        self.setWidgetResizable(True)

        # Estilos para la barra de desplazamiento
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def create_metric_card(self, title, value, color, icon_name):
        """Crea una tarjeta de métrica con íconos pero con estilo uniforme"""
        icon_map = {
            "dollar-sign": "assets/icons/dashboard/dollar-sign.png",
            "shopping-cart": "assets/icons/dashboard/shopping-cart.png",
            "box": "assets/icons/dashboard/box.png",
            "x-circle": "assets/icons/dashboard/alert-triangle.png"
        }
        
        icon_path = icon_map.get(icon_name, "assets/icons/dashboard/bar-chart.png")    
        
        card = QFrame()
        card.setObjectName("metricCard")
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                min-width: 180px;
            }}
            QLabel#metricTitle {{
                color: #718096;
                font-size: 14px;
            }}
            QLabel#metricValue {{
                color: {color};
                font-size: 22px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Fila superior con ícono y título
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        # Contenedor del ícono
        icon_container = QLabel()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QLabel {
                background-color: #F8F9FA;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        
        # Ícono
        icon_label = QLabel(icon_container)
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        
        top_row.addWidget(icon_container)
        top_row.addWidget(title_label)
        top_row.addStretch()
        
        # Valor
        value_label = QLabel(str(value))
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        layout.addLayout(top_row)
        layout.addWidget(value_label)
        
        # Almacenar referencia al label de valor
        card.value_label = value_label
        
        return card

    def actualizar_metricas(self):
        """Actualiza las métricas con datos reales de la base de datos"""
        try:
            # Obtener datos de ventas
            ventas_data = self.db.ventas.aggregate([
                {"$group": {
                    "_id": None,
                    "total_ventas": {"$sum": "$total"},
                    "total_productos": {"$sum": {"$size": "$productos"}}
                }}
            ])
            ventas_data = list(ventas_data)
            
            total_ventas = ventas_data[0]['total_ventas'] if ventas_data else 0
            total_productos_vendidos = ventas_data[0]['total_productos'] if ventas_data else 0
            
            # Obtener datos de inventario
            inventario_data = self.db.inventario.aggregate([
                {"$group": {
                    "_id": None,
                    "total_stock": {"$sum": "$stock_actual"},
                    "productos_stock": {"$sum": {"$cond": [{"$gt": ["$stock_actual", 0]}, 1, 0]}},
                    "productos_agotados": {"$sum": {"$cond": [{"$lte": ["$stock_actual", 0]}, 1, 0]}}
                }}
            ])
            inventario_data = list(inventario_data)
            
            productos_stock = inventario_data[0]['productos_stock'] if inventario_data else 0
            productos_agotados = inventario_data[0]['productos_agotados'] if inventario_data else 0
            
            # Actualizar las tarjetas
            self.metric_cards["ventas_totales"].value_label.setText(f"${total_ventas:,.2f}")
            self.metric_cards["productos_vendidos"].value_label.setText(f"{total_productos_vendidos}")
            self.metric_cards["productos_stock"].value_label.setText(f"{productos_stock}")
            self.metric_cards["productos_agotados"].value_label.setText(f"{productos_agotados}")
            
        except Exception as e:
            print(f"Error al actualizar métricas: {str(e)}")
            traceback.print_exc()

    def get_inventario_por_categoria(self):
        """Obtiene el inventario agrupado por categoría"""
        try:
            pipeline = [
                {"$match": {"stock": {"$gt": 0}}},  # Solo productos con stock > 0
                {"$group": {
                    "_id": "$categoria", 
                    "stock_total": {"$sum": "$stock"},
                    "cantidad_productos": {"$sum": 1}
                }},
                {"$sort": {"stock_total": -1}},
                {"$limit": 8}  # Limitar a las 8 categorías principales
            ]
                
            # Obtener datos de la base de datos
            categorias = list(self.db.productos.aggregate(pipeline))
                
            # Si no hay categorías, devolver una lista vacía
            if not categorias:
                return []
                
            # Procesar los resultados
            resultado = []
            for cat in categorias:
                resultado.append({
                    'categoria': cat['_id'] or 'Sin categoría',
                    'total_stock': cat['stock_total'],
                    'cantidad_productos': cat['cantidad_productos']
                })
                
            return resultado
            
        except Exception as e:
            print(f"Error al obtener inventario por categoría: {str(e)}")
            traceback.print_exc()
            return []

    def open_url(self, url):
        """Abre una URL en el navegador predeterminado"""
        if not url.startswith("http"):
            url = "https://" + url
        QDesktopServices.openUrl(QUrl(url))

    def replace_chart_content(self, frame, new_widget):
        """Reemplaza el contenido de un frame con un nuevo widget"""
        # Limpiar el frame existente
        layout = frame.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Configurar el nuevo widget
        new_widget.setParent(frame)
        if layout:
            layout.addWidget(new_widget)
        else:
            new_layout = QVBoxLayout(frame)
            new_layout.setContentsMargins(0, 0, 0, 0)
            new_layout.addWidget(new_widget)
        
        # Asegurar que el fondo sea blanco
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
            }
        """)
        new_widget.setStyleSheet("background-color: #FFFFFF;")

    def refresh_all(self):
        """Actualiza todos los datos del dashboard"""
        try:
            self.is_loading = True
            self.error_message = ""
                
            # Actualizar métricas
            self.actualizar_metricas()
                                
        except Exception as e:
            self.error_message = f"Error al actualizar el dashboard: {str(e)}"
            print(self.error_message)
            traceback.print_exc()
        finally:
            self.is_loading = False