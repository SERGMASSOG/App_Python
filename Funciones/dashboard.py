from PySide6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QFrame, 
                             QPushButton, QWidget, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor, QFont, QPixmap
from db.mongo_connection import get_db_connection

class DashboardManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db = get_db_connection()
        self.ventas_collection = self.db['ventas']
        self.inventario_collection = self.db['inventario']
        self.clientes_collection = self.db['clientes']
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        ventas_hoy = self.get_ventas_hoy()
        clientes_nuevos = self.get_clientes_nuevos()
        inventario_bajo = self.get_inventario_bajo_stock()
        ventas_mes = self.get_ventas_mes()

        metrics_layout.addWidget(self.create_metric_card("Ventas de Hoy", f"${ventas_hoy:,.2f}", "#4CAF50", "dollar-sign"))
        metrics_layout.addWidget(self.create_metric_card("Ventas del Mes", f"${ventas_mes:,.2f}", "#2196F3", "chart-line"))
        metrics_layout.addWidget(self.create_metric_card("Clientes Nuevos", str(clientes_nuevos), "#9C27B0", "user-plus"))
        metrics_layout.addWidget(self.create_metric_card("Bajo Stock", str(inventario_bajo), "#FF9800", "alert-triangle"))

        layout.addLayout(metrics_layout)

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        sales_chart = self.create_chart_frame("Ventas Recientes")
        products_chart = self.create_chart_frame("Productos más Vendidos")

        charts_layout.addWidget(sales_chart, 1)
        charts_layout.addWidget(products_chart, 1)

        layout.addLayout(charts_layout, 1)

        recent_activity = self.create_recent_activity()
        layout.addWidget(recent_activity, 1)

    def create_metric_card(self, title, value, color, icon_name):
        card = QFrame()
        card.setMinimumWidth(200)
        card.setMaximumWidth(300)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
            }
        """)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(f"assets/icons/{icon_name}.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
            }}
        """)

        layout.addLayout(top_layout)
        layout.addWidget(value_label)

        return card

    # Crear un marco para el gráfico
    def create_chart_frame(self, title):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2D3748;
                font-size: 15px;
                font-weight: 600;
            }
        """)

        chart_placeholder = QLabel(f"Gráfico de {title}")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setMinimumHeight(200)
        chart_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #E2E8F0;
                border-radius: 6px;
                color: #94A3B8;
                font-style: italic;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(chart_placeholder, 1)

        return frame

    def create_recent_activity(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title_label = QLabel("Actividad Reciente")
        title_label.setStyleSheet("""
            QLabel {
                color: #2D3748;
                font-size: 15px;
                font-weight: 600;
            }
        """)

        activity_list = QWidget()
        activity_layout = QVBoxLayout(activity_list)
        activity_layout.setContentsMargins(5, 5, 5, 5)
        activity_layout.setSpacing(10)

        activities = [
            ("Nueva venta registrada", "Hace 5 min"),
            ("Producto actualizado en inventario", "Hace 1 hora"),
            ("Nuevo cliente registrado", "Hace 2 horas"),
            ("Pago recibido", "Ayer"),
            ("Producto agotado", "Ayer")
        ]

        for activity, time in activities:
            item = QLabel(f"• {activity}")
            item.setStyleSheet("""
                QLabel {
                    color: #4B5563;
                    padding: 8px 0;
                    border-bottom: 1px solid #F1F5F9;
                }
                QLabel:last-child {
                    border-bottom: none;
                }
            """)

            time_label = QLabel(time)
            time_label.setStyleSheet("color: #94A3B8; font-size: 12px;")

            item_layout = QHBoxLayout()
            item_layout.addWidget(item, 1)
            item_layout.addWidget(time_label)

            activity_layout.addLayout(item_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(activity_list)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F8FAFC;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #E2E8F0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(scroll_area, 1)

        return frame

    def get_ventas_hoy(self):
        try:
            hoy = QDateTime.currentDateTime()
            inicio = hoy.date().startOfDay().toPython()
            fin = hoy.date().endOfDay().toPython()

            pipeline = [
                {'$match': {
                    'fecha': {'$gte': inicio, '$lt': fin}
                }},
                {'$group': {
                    '_id': None,
                    'total': {'$sum': '$total'}
                }}
            ]

            result = list(self.ventas_collection.aggregate(pipeline))
            return result[0]['total'] if result else 0

        except Exception as e:
            print(f"Error al obtener ventas de hoy: {str(e)}")
            return 0

    def get_ventas_mes(self):
        try:
            hoy = QDateTime.currentDateTime()
            actual = hoy.toPython()
            primer_dia_mes = actual.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin = actual.replace(hour=23, minute=59, second=59, microsecond=999999)

            pipeline = [
                {'$match': {
                    'fecha': {'$gte': primer_dia_mes, '$lte': fin}
                }},
                {'$group': {
                    '_id': None,
                    'total': {'$sum': '$total'}
                }}
            ]

            result = list(self.ventas_collection.aggregate(pipeline))
            return result[0]['total'] if result else 0

        except Exception as e:
            print(f"Error al obtener ventas del mes: {str(e)}")
            return 0

    def get_clientes_nuevos(self):
        try:
            hoy = QDateTime.currentDateTime()
            actual = hoy.toPython()
            primer_dia_mes = actual.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin = actual.replace(hour=23, minute=59, second=59, microsecond=999999)

            return self.clientes_collection.count_documents({
                'fecha_registro': {'$gte': primer_dia_mes, '$lte': fin}
            })

        except Exception as e:
            print(f"Error al obtener clientes nuevos: {str(e)}")
            return 0

    def get_inventario_bajo_stock(self, min_stock=10):
        try:
            return self.inventario_collection.count_documents({
                'stock': {'$lte': min_stock}
            })
        except Exception as e:
            print(f"Error al obtener inventario bajo stock: {str(e)}")
            return 0