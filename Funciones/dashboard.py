from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QSizePolicy, QScrollArea,
    QPushButton, QComboBox, QMessageBox, QFileDialog, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, QDate
from datetime import datetime, timedelta
from bson.decimal128 import Decimal128
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QPixmap, QIcon, QColor, QFont
from dateutil.relativedelta import relativedelta
import numpy as np
import csv
import traceback

class DashboardManager(QScrollArea):
    """
    Panel principal de dashboard para métricas y gráficos de negocio.
    Incluye auto-refresh, feedback visual, controles interactivos y manejo robusto de errores.
    """
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.refresh_interval_ms = 300000  # 5 minutos por default
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.is_loading = False
        self.error_message = ""
        self.date_range = "mes"  # Opciones: "dia", "semana", "mes", "año"
        self.metrics = {}  # Inicializar el diccionario de métricas
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard"""
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        
        # Widget principal con scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(15)
        
        # Contenedor principal
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)

        # Panel superior de controles
        self.setup_top_controls()

        # Sección de métricas
        self.setup_metrics_section()
        
        # Espaciador para separar las tarjetas de las gráficas
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(spacer)

        # Sección de gráficos
        self.setup_charts_container()
        
        # Asegurar que los gráficos se expandan
        self.main_layout.addStretch(1)

        # Mensaje de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #C62828; font-weight: bold;")
        self.main_layout.addWidget(self.status_label)
        
        # Añadir el contenido al scroll
        scroll_layout.addWidget(main_widget)
        
        # Configurar el scroll area
        self.setWidget(scroll_widget)
        self.setWidgetResizable(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setup_top_controls(self):
        """Panel superior con controles de usuario"""
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Botón actualizar ahora
        self.refresh_btn = QPushButton("Actualizar ahora")
        self.refresh_btn.setIcon(QIcon("assets/icons/dashboard/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_all)
        controls_layout.addWidget(self.refresh_btn)

        # Selector de rango de fechas
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Hoy", "Esta semana", "Este mes", "Este año"])
        self.range_combo.setCurrentIndex(2)
        self.range_combo.currentIndexChanged.connect(self.on_range_changed)
        controls_layout.addWidget(QLabel("Rango:"))
        controls_layout.addWidget(self.range_combo)

        # Botón exportar CSV
        self.export_btn = QPushButton("Exportar CSV")
        self.export_btn.setIcon(QIcon("assets/icons/dashboard/download.png"))
        self.export_btn.clicked.connect(self.export_csv)
        controls_layout.addWidget(self.export_btn)

        # Espaciador
        controls_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.main_layout.addLayout(controls_layout)

    def on_range_changed(self, idx):
        """Cambia el rango de fechas y refresca todo"""
        ranges = ["dia", "semana", "mes", "año"]
        self.date_range = ranges[idx]
        self.refresh_all()

    def export_csv(self):
        """Exporta las métricas principales a un archivo CSV"""
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Exportar métricas a CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Métrica", "Valor"])
                for key, card in self.metrics.items():
                    value = card.findChild(QLabel, "value").text()
                    writer.writerow([key, value])
            QMessageBox.information(self, "Exportación exitosa", "Métricas exportadas correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))

    def set_status(self, msg, error=False):
        """Muestra un mensaje de estado en el dashboard"""
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("color: #C62828;" if error else "color: #388E3C;")

    def refresh_all(self):
        """Refresca métricas y gráficos, con feedback visual y manejo de errores"""
        self.is_loading = True
        self.set_status("Cargando datos...", error=False)
        try:
            self.update_metrics()
            self.update_charts()
            self.set_status("Dashboard actualizado correctamente.", error=False)
        except Exception as e:
            self.error_message = str(e)
            self.set_status(f"Error: {self.error_message}", error=True)
            traceback.print_exc()
        self.is_loading = False

    def setup_metrics_section(self):
        """Configura la sección de métricas principales"""
        # Contenedor principal para las métricas
        metrics_container = QWidget()
        metrics_layout = QVBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 0, 0, 10)  # Added bottom margin
        metrics_layout.setSpacing(10)
        
        # Section title with improved style
        title_label = QLabel("Métricas Principales")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                padding: 8px 0 5px 5px;
                border-bottom: 2px solid #3498DB;
                margin-bottom: 5px;
            }
        """)
        metrics_layout.addWidget(title_label)
        
        # Scroll container for metric cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
                padding: 2px 0;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: #F0F0F0;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #B0BEC5;
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                height: 0px;
            }
            QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        
        # Create a grid layout for the metrics cards
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(10, 5, 10, 10)
        grid_layout.setSpacing(15)
        
        # Create only the specified metric cards
        self.metrics = {
            # First row
            "ventas_mes": self.create_metric_card("Ventas del Mes", "$0", "#4CAF50", "dollar-sign"),
            "total_ventas": self.create_metric_card("Total Ventas", "0", "#2196F3", "shopping-cart"),
            "ticket_promedio": self.create_metric_card("Ticket Promedio", "$0", "#FF9800", "shopping-bag"),
            
            # Second row
            "ventas_anuladas": self.create_metric_card("Ventas Anuladas", "0", "#F44336", "x-circle"),
            "stock_total": self.create_metric_card("Total Inventario", "0", "#9C27B0", "box"),
            "total_clientes": self.create_metric_card("Total Clientes", "0", "#3F51B5", "users")
        }
        
        # Add cards to grid layout (3 cards per row)
        for i, (key, card) in enumerate(self.metrics.items()):
            row = i // 3
            col = i % 3
            grid_layout.addWidget(card, row, col, 1, 1)
        
        # Create a container for the grid
        container = QWidget()
        container.setLayout(grid_layout)
        
        # Add the container to the scroll area
        scroll.setWidget(container)
        
        # Set fixed height for the scroll area to fit 2 rows of cards
        scroll.setMinimumHeight(300)
        scroll.setMaximumHeight(350)
        
        # Add the scroll area to the metrics layout
        metrics_layout.addWidget(scroll)
        
        # Add the metrics container to the main layout
        self.main_layout.addWidget(metrics_container)
        
        # Add a visual separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #E0E0E0; margin: 5px 0;")
        self.main_layout.addWidget(separator)
        
    def setup_charts_container(self):
        """Configura el contenedor de gráficos del dashboard"""
        # Contenedor principal de gráficos
        charts_container = QWidget()
        charts_container.setObjectName("chartsContainer")
        charts_layout = QVBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(15)
        
        # Título de la sección
        title_label = QLabel("Análisis Visual")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                padding: 8px 0 5px 5px;
                border-bottom: 2px solid #3498DB;
                margin-bottom: 5px;
            }
        """)
        charts_layout.addWidget(title_label)
        
        # Fila para los tres gráficos
        charts_row = QHBoxLayout()
        charts_row.setContentsMargins(0, 0, 0, 0)
        charts_row.setSpacing(15)
        
        # Gráfico de ventas mensuales (35% del ancho)
        self.sales_chart = self.create_chart_frame("Ventas Mensuales", "sales_chart")
        self.sales_chart.setMinimumHeight(350)
        charts_row.addWidget(self.sales_chart, 35)  # 35% del ancho
        
        # Gráfico de inventario (30% del ancho)
        self.inventory_chart = self.create_chart_frame("Inventario por Categoría", "inventory_chart")
        self.inventory_chart.setMinimumHeight(350)
        charts_row.addWidget(self.inventory_chart, 30)  # 30% del ancho
        
        # Gráfico de clientes (35% del ancho)
        self.clients_chart = self.create_chart_frame("Clientes Principales", "clients_chart")
        self.clients_chart.setMinimumHeight(350)
        charts_row.addWidget(self.clients_chart, 35)  # 35% del ancho
        
        charts_layout.addLayout(charts_row)
        
        # Añadir el contenedor de gráficos al layout principal
        self.main_layout.addWidget(charts_container)
        
    def create_chart_frame(self, title, object_name):
        """Crea un frame para contener un gráfico con título"""
        frame = QFrame()
        frame.setObjectName(object_name)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 600;
                color: #37474F;
                padding: 5px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Contenedor para el gráfico
        chart_container = QWidget()
        chart_container.setObjectName(f"{object_name}_container")
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        
        # Widget temporal con mensaje de carga
        loading = QLabel("Cargando datos...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet("color: #78909C; font-style: italic; font-size: 11px;")
        chart_layout.addWidget(loading)
        
        layout.addWidget(chart_container, 1)  # Estirar el contenedor del gráfico
        
        return frame

    def update_metric_card(self, card_id, value):
        """Actualiza el valor de una tarjeta de métrica existente"""
        card = getattr(self, f"{card_id}_card", None)
        if card and hasattr(card, 'value_label'):
            card.value_label.setText(str(value))
            
            # Actualizar el color basado en el valor (opcional)
            if card_id == "ventas_anuladas" and value != "N/A" and int(value.replace(',', '')) > 0:
                card.value_label.setStyleSheet("color: #e74c3c; font-size: 24px; font-weight: 600;")
            elif card_id in ["pct_hombres", "pct_mujeres"] and value != "N/A":
                card.value_label.setStyleSheet("color: #3498db; font-size: 20px; font-weight: 600;")
            else:
                card.value_label.setStyleSheet("color: #2ecc71; font-size: 24px; font-weight: 600;")

    def create_metric_card(self, title, value, color="#3498db", icon_name="info"):
        """Crea una tarjeta de métrica con título, valor e ícono"""
        # Mapeo de nombres de íconos a códigos de fuente
        icon_map = {
            "dollar-sign": "$",
            "shopping-cart": "🛒",
            "shopping-bag": "🛍️",
            "x-circle": "❌",
            "box": "📦",
            "alert-triangle": "⚠️",
            "users": "👥",
            "user": "👤",
            "info": "ℹ️"
        }
        
        # Crear el contenedor principal de la tarjeta
        card = QFrame()
        card.setObjectName("metricCard")
        card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                padding: 12px;
            }}
            QLabel#metricTitle {{
                color: #666666;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QLabel#metricValue {{
                color: {color};
                font-size: 24px;
                font-weight: 600;
                margin: 5px 0;
            }}
        """)
        
        # Layout principal
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Fila superior con título e ícono
        top_row = QHBoxLayout()
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        
        # Ícono
        icon_label = QLabel(icon_map.get(icon_name, "ℹ️"))
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                opacity: 0.8;
            }
        """)
        
        # Añadir a la fila superior con espaciado
        top_row.addWidget(title_label, 1)
        top_row.addWidget(icon_label, 0, Qt.AlignRight)
        
        # Valor
        value_label = QLabel(str(value))
        value_label.setObjectName("metricValue")
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Añadir al layout principal
        layout.addLayout(top_row)
        layout.addWidget(value_label)
        
        # Añadir un espaciador para empujar todo hacia arriba
        layout.addStretch()
        
        # Configurar tamaño fijo para la tarjeta
        card.setFixedWidth(200)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Almacenar referencia a la etiqueta de valor para actualizaciones posteriores
        card.value_label = value_label
        
        return card

    def update_metrics(self):
        """Actualiza todas las métricas del dashboard"""
        try:
            # Obtener métricas de ventas
            ventas_mes = self.get_ventas_mes()
            total_ventas = self.get_total_ventas()
            ticket_promedio = self.get_ticket_promedio()
            ventas_anuladas = self.db.ventas.count_documents({"estado": "anulada"})
            
            # Obtener métricas de inventario
            stock_total = self.get_stock_total()
            
            # Obtener métricas de clientes
            total_clientes = self.get_total_clientes()
            
            # Actualizar las tarjetas de métricas
            self.update_metric_card("ventas_mes", f"${ventas_mes:,.2f}")
            self.update_metric_card("total_ventas", f"{total_ventas:,}")
            self.update_metric_card("ticket_promedio", f"${ticket_promedio:,.2f}")
            self.update_metric_card("ventas_anuladas", f"{ventas_anuladas:,}")
            self.update_metric_card("stock_total", f"{stock_total:,}")
            self.update_metric_card("total_clientes", f"{total_clientes:,}")
            
            # Actualizar los gráficos
            self.load_ventas_mensuales_chart()
            self.load_inventario_por_categoria_chart()
            self.load_top_clientes_chart()
            
        except Exception as e:
            print(f"Error al actualizar métricas: {str(e)}")
            traceback.print_exc()
    
    def update_charts(self):
        """Actualiza los tres gráficos clave del dashboard"""
        try:
            self.load_ventas_mensuales_chart()   # Línea de ventas por mes
            self.load_inventario_por_categoria_chart()  # Pie % stock por categoría
            self.load_top_clientes_chart()  # Barras: Top-10 clientes por monto
        except Exception as e:
            print(f"Error al actualizar gráficos: {str(e)}")
            traceback.print_exc()

    def show_no_data_message(self, frame, message):
        """Muestra un mensaje cuando no hay datos disponibles"""
        try:
            # Limpiar el frame actual
            for i in reversed(range(frame.layout().count())):
                frame.layout().itemAt(i).widget().setParent(None)
            
            # Crear widget de mensaje
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Añadir icono de advertencia
            icon = QLabel()
            icon.setPixmap(QPixmap(":/icons/alert-triangle").scaled(32, 32, Qt.KeepAspectRatio))
            icon.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon)
            
            # Añadir mensaje
            label = QLabel(message)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #666666; font-size: 12px;")
            layout.addWidget(label)
            
            # Añadir al frame
            frame.layout().addWidget(widget)
            
        except Exception as e:
            print(f"Error al mostrar mensaje de sin datos: {str(e)}")
            traceback.print_exc()

    def get_clientes_stats(self):
        """Obtiene estadísticas de clientes (total, % hombres, % mujeres)"""
        try:
            # Obtener total de clientes
            total = self.get_total_clientes()
            if total == 0:
                return {
                    'total': 0,
                    'hombres': 0,
                    'mujeres': 0,
                    'sin_genero': 0,
                    'porcentaje_hombres': 0,
                    'porcentaje_mujeres': 0
                }
                
            # Obtener conteo por género
            pipeline = [
                {"$group": {
                    "_id": "$genero",
                    "count": {"$sum": 1}
                }}
            ]
            
            resultados = list(self.db.clientes.aggregate(pipeline))
            
            # Contar por género
            contadores = {'H': 0, 'M': 0, 'sin_genero': 0}
            
            for r in resultados:
                genero = r.get('_id', '').upper()
                if genero in ['H', 'M']:
                    contadores[genero] = r.get('count', 0)
                else:
                    contadores['sin_genero'] += r.get('count', 0)
            
            # Calcular porcentajes
            porcentaje_hombres = (contadores['H'] / total) * 100 if total > 0 else 0
            porcentaje_mujeres = (contadores['M'] / total) * 100 if total > 0 else 0
            
            return {
                'total': total,
                'hombres': contadores['H'],
                'mujeres': contadores['M'],
                'sin_genero': contadores['sin_genero'],
                'porcentaje_hombres': round(porcentaje_hombres, 1),
                'porcentaje_mujeres': round(porcentaje_mujeres, 1)
            }
        except Exception as e:
            print(f"Error en get_ventas_mes: {str(e)}")
            return 0

    def get_stock_total(self):
        """Obtiene la suma total de unidades en inventario (stock)"""
        try:
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$stock"}}}
            ]
            result = list(self.db.productos.aggregate(pipeline))
            return int(result[0]['total']) if result and result[0].get('total') is not None else 0
        except Exception as e:
            print(f"Error en get_stock_total: {str(e)}")
            return 0

    def get_total_clientes(self):
        """Obtiene el total de clientes"""
        try:
            return self.db.clientes.count_documents({})
        except Exception as e:
            print(f"Error en get_total_clientes: {str(e)}")
            return 0

    def get_inventario_bajo_stock(self):
        """Obtiene la cantidad de productos con stock bajo (<10)"""
        try:
            return self.db.productos.count_documents({"stock": {"$lt": 10}})
        except Exception as e:
            print(f"Error en get_inventario_bajo_stock: {str(e)}")
            return 0

    def get_total_productos_vendidos(self):
        """Obtiene el total de productos vendidos"""
        try:
            pipeline = [
                {"$unwind": "$productos"},
                {"$group": {"_id": None, "total": {"$sum": "$productos.cantidad"}}}
            ]
            result = list(self.db.ventas.aggregate(pipeline))
            return int(result[0]['total']) if result and result[0].get('total') is not None else 0
        except Exception as e:
            print(f"Error en get_total_productos_vendidos: {str(e)}")
            return 0

    def get_ticket_promedio(self):
        """Calcula el ticket promedio de las ventas"""
        pipeline = [
            {"$group": {"_id": None, "promedio": {"$avg": "$total"}}}
        ]
        result = list(self.db.ventas.aggregate(pipeline))
        return float(result[0]['promedio']) if result and result[0].get('promedio') else 0

    def get_ventas_mes(self):
        """Obtiene el total de ventas del mes actual"""
        try:
            # Obtener el primer y último día del mes actual
            hoy = datetime.now()
            primer_dia = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Crear pipeline de agregación
            pipeline = [
                {
                    "$match": {
                        "fecha_venta": {"$gte": primer_dia},
                        "estado": "completada"
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$total"}
                    }
                }
            ]
            
            result = list(self.db.ventas.aggregate(pipeline))
            return float(result[0]['total']) if result and result[0].get('total') is not None else 0.0
            
        except Exception as e:
            print(f"Error en get_ventas_mes: {str(e)}")
            traceback.print_exc()
            return 0.0
            
    def get_total_ventas(self):
        """Obtiene el total de ventas (cantidad de ventas)"""
        return self.db.ventas.count_documents({})

    def load_ventas_mensuales_chart(self):
        """Carga el gráfico de ventas mensuales"""
        try:
            frame = self.findChild(QFrame, "sales_chart")
            if not frame:
                print("No se encontró el frame para el gráfico de ventas mensuales")
                return
                
            # Limpiar el frame actual
            for i in reversed(range(frame.layout().count())): 
                widget = frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Obtener ventas de los últimos 6 meses
            hoy = datetime.now()
            meses = []
            ventas = []
            
            for i in range(6):
                # Calcular primer y último día del mes
                mes = hoy.replace(day=1) - timedelta(days=i*30)
                meses.insert(0, mes.strftime('%b %Y'))
                
                inicio = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if mes.month == 12:
                    fin = datetime(mes.year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    fin = datetime(mes.year, mes.month + 1, 1) - timedelta(seconds=1)
                
                # Obtener ventas del mes
                try:
                    ventas_mes = list(self.db.ventas.find({
                        "fecha": {"$gte": inicio, "$lte": fin},
                        "estado": {"$ne": "anulada"}  # Excluir ventas anuladas
                    }))
                    
                    total_mes = sum(float(v.get("total", 0)) for v in ventas_mes)
                    ventas.append(total_mes)
                except Exception as e:
                    print(f"Error al obtener ventas del mes {mes.strftime('%Y-%m')}: {str(e)}")
                    ventas.append(0)  # Añadir 0 si hay un error
            
            # Verificar si hay datos para mostrar
            if not any(ventas):
                self.show_no_data_message(frame, "No hay datos de ventas para mostrar")
                return
            
            # Crear gráfico
            try:
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                bars = ax.bar(meses, ventas, color='#4CAF50')
                
                # Añadir etiquetas con los valores
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:  # Solo mostrar etiqueta si el valor es mayor que 0
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'${height:,.2f}',
                                ha='center', va='bottom', fontsize=8)
                
                ax.set_title('Ventas Mensuales', fontsize=12, pad=10)
                ax.grid(True, linestyle='-', alpha=0.3)
                ax.set_facecolor('#FFFFFF')
                fig.patch.set_facecolor('#FFFFFF')
                
                # Rotar etiquetas del eje X para mejor legibilidad
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
                # Ajustar márgenes
                fig.tight_layout()
                
                # Mostrar el gráfico en el frame
                canvas = FigureCanvas(fig)
                
                # Limpiar el layout actual
                for i in reversed(range(frame.layout().count())): 
                    widget = frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Añadir el canvas al layout del frame
                frame.layout().addWidget(canvas)
                canvas.draw()
                
            except Exception as e:
                print(f"Error al crear el gráfico de ventas mensuales: {str(e)}")
                traceback.print_exc()
                self.show_no_data_message(frame, "Error al generar el gráfico")
            
        except Exception as e:
            print(f"Error en load_ventas_mensuales_chart: {str(e)}")
            traceback.print_exc()
            if frame:
                self.show_no_data_message(frame, "Error al cargar los datos")
                return

    def load_top_clientes_chart(self):
        """Carga el gráfico de barras de los 10 clientes con mayor volumen de compra"""
        try:
            frame = self.findChild(QFrame, "top_clientes_chart")
            if not frame:
                print("No se encontró el frame para el gráfico de clientes")
                return
                
            # Limpiar el frame actual
            for i in reversed(range(frame.layout().count())): 
                widget = frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Obtener los 10 clientes con mayor volumen de compra
            pipeline = [
                {"$match": {"estado": {"$ne": "anulada"}}},  # Excluir ventas anuladas
                {"$group": {
                    "_id": "$cliente",
                    "total": {"$sum": "$total"},
                    "cantidad_compras": {"$sum": 1},
                    "ultima_compra": {"$max": "$fecha"}
                }},
                {"$sort": {"total": -1}},
                {"$limit": 10}
            ]
            
            top_clientes = list(self.db.ventas.aggregate(pipeline))
            
            # Si no hay datos, mostrar mensaje
            if not top_clientes:
                self.show_no_data_message(frame, "No hay datos de clientes")
                return
            
            # Obtener información detallada de los clientes
            clientes_ids = [c["_id"] for c in top_clientes]
            clientes_info = {}
            
            for cliente in self.db.clientes.find({"_id": {"$in": clientes_ids}}):
                cliente_id = str(cliente["_id"])
                nombre = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
                if not nombre:
                    nombre = f"Cliente {cliente_id[:8]}..."
                clientes_info[cliente_id] = {
                    'nombre': nombre,
                    'email': cliente.get('email', 'Sin email')
                }
            
            # Preparar datos para el gráfico
            datos = []
            for cliente in top_clientes:
                cliente_id = str(cliente["_id"])
                info = clientes_info.get(cliente_id, {
                    'nombre': f"Cliente {cliente_id[:8]}...",
                    'email': 'No disponible'
                })
                
                # Formatear nombre para mostrar (nombre + inicial del apellido si existe)
                nombre_parts = info['nombre'].split()
                if len(nombre_parts) > 1:
                    nombre_mostrar = f"{nombre_parts[0]} {nombre_parts[-1][0]}."
                else:
                    nombre_mostrar = info['nombre']
                
                datos.append({
                    'nombre': nombre_mostrar,
                    'total': float(cliente['total']),
                    'compras': cliente['cantidad_compras'],
                    'ultima_compra': cliente['ultima_compra'].strftime('%d/%m/%Y') if 'ultima_compra' in cliente else 'N/A'
                })
            
            # Ordenar datos por total descendente
            datos_ordenados = sorted(datos, key=lambda x: x['total'], reverse=True)
            nombres = [d['nombre'] for d in datos_ordenados]
            montos = [d['total'] for d in datos_ordenados]
            
            # Crear el gráfico de barras
            try:
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                # Crear el gráfico de barras horizontales
                y_pos = range(len(nombres))
                bars = ax.barh(y_pos, montos, color='#2196F3')
                
                # Añadir etiquetas con los valores
                for i, (bar, monto) in enumerate(zip(bars, montos)):
                    ax.text(monto, i, f' ${monto:,.2f}', 
                           va='center', ha='left', fontsize=8)
                
                # Configurar el gráfico
                ax.set_yticks(y_pos)
                ax.set_yticklabels(nombres, fontsize=9)
                ax.set_title('Top 10 Clientes por Volumen de Compra', fontsize=12, pad=10)
                ax.grid(True, linestyle='-', alpha=0.3, axis='x')
                ax.set_facecolor('#FFFFFF')
                fig.patch.set_facecolor('#FFFFFF')
                
                # Ajustar márgenes
                fig.tight_layout()
                
                # Mostrar el gráfico en el frame
                canvas = FigureCanvas(fig)
                
                # Limpiar el layout actual
                for i in reversed(range(frame.layout().count())): 
                    widget = frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Añadir el canvas al layout del frame
                frame.layout().addWidget(canvas)
                canvas.draw()
                
            except Exception as e:
                print(f"Error al crear el gráfico de clientes: {str(e)}")
                traceback.print_exc()
                self.show_no_data_message(frame, "Error al generar el gráfico")
                
        except Exception as e:
            print(f"Error en load_top_clientes_chart: {str(e)}")
            traceback.print_exc()
            if frame:
                self.show_no_data_message(frame, "Error al cargar los datos")
                
    def load_inventario_por_categoria_chart(self):
        """Carga el gráfico de inventario por categoría"""
        try:
            frame = self.findChild(QFrame, "inventory_chart")
            if not frame:
                print("No se encontró el frame para el gráfico de inventario")
                return
                
            # Limpiar el frame actual
            for i in reversed(range(frame.layout().count())): 
                widget = frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Obtener datos de inventario por categoría
            pipeline = [
                {"$group": {
                    "_id": "$categoria",
                    "total": {"$sum": "$stock"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total": -1}}
            ]
            
            categorias_data = list(self.db.productos.aggregate(pipeline))
            
            # Si no hay datos, mostrar mensaje
            if not categorias_data:
                self.show_no_data_message(frame, "No hay datos de inventario")
                return
            
            # Preparar datos para el gráfico
            categorias = [d["_id"] or "Sin categoría" for d in categorias_data]
            cantidades = [d["total"] for d in categorias_data]
            
            # Crear el gráfico de torta
            try:
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                # Colores para las categorías
                colors = plt.cm.tab20c(range(len(categorias)))
                
                # Crear el gráfico de torta
                wedges, texts, autotexts = ax.pie(
                    cantidades,
                    labels=categorias,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    textprops={'fontsize': 8}
                )
                
                # Hacer el gráfico circular
                ax.axis('equal')
                ax.set_title('Inventario por Categoría', fontsize=12, pad=10)
                
                # Añadir leyenda
                ax.legend(
                    wedges,
                    [f"{cat} ({cant:,})" for cat, cant in zip(categorias, cantidades)],
                    title="Categorías",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize=8
                )
                
                # Ajustar diseño
                fig.tight_layout()
                
                # Mostrar el gráfico en el frame
                canvas = FigureCanvas(fig)
                
                # Limpiar el layout actual
                for i in reversed(range(frame.layout().count())): 
                    widget = frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Añadir el canvas al layout del frame
                frame.layout().addWidget(canvas)
                canvas.draw()
                
            except Exception as e:
                print(f"Error al crear el gráfico de inventario: {str(e)}")
                traceback.print_exc()
                self.show_no_data_message(frame, "Error al generar el gráfico")
                
        except Exception as e:
            print(f"Error al crear el gráfico de clientes: {str(e)}")
            traceback.print_exc()
            self.show_no_data_message(frame, "Error al generar el gráfico")
                
        except Exception as e:
            print(f"Error en load_top_clientes_chart: {str(e)}")
            traceback.print_exc()
            if frame:
                self.show_no_data_message(frame, "Error al cargar los datos")

    def load_inventario_por_categoria_chart(self):
        """Carga el gráfico de inventario por categoría"""
        try:
            frame = self.findChild(QFrame, "inventory_chart")
            if not frame:
                print("No se encontró el frame para el gráfico de inventario")
                return
                
            # Limpiar el frame actual
            for i in reversed(range(frame.layout().count())): 
                widget = frame.layout().itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # Obtener datos de inventario por categoría
            pipeline = [
                {"$group": {
                    "_id": "$categoria",
                    "total": {"$sum": "$stock"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total": -1}}
            ]
            
            categorias_data = list(self.db.productos.aggregate(pipeline))
            
            # Si no hay datos, mostrar mensaje
            if not categorias_data:
                self.show_no_data_message(frame, "No hay datos de inventario")
                return
            
            # Preparar datos para el gráfico
            categorias = [d["_id"] or "Sin categoría" for d in categorias_data]
            cantidades = [d["total"] for d in categorias_data]
            
            # Crear el gráfico de torta
            try:
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                # Colores para las categorías
                colors = plt.cm.tab20c(range(len(categorias)))
                
                # Crear el gráfico de torta
                wedges, texts, autotexts = ax.pie(
                    cantidades,
                    labels=categorias,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    textprops={'fontsize': 8}
                )
                
                # Hacer el gráfico circular
                ax.axis('equal')
                ax.set_title('Inventario por Categoría', fontsize=12, pad=10)
                
                # Añadir leyenda
                ax.legend(
                    wedges,
                    [f"{cat} ({cant:,})" for cat, cant in zip(categorias, cantidades)],
                    title="Categorías",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize=8
                )
                
                # Ajustar diseño
                fig.tight_layout()
                
                # Mostrar el gráfico en el frame
                canvas = FigureCanvas(fig)
                
                # Limpiar el layout actual
                for i in reversed(range(frame.layout().count())): 
                    widget = frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                
                # Añadir el canvas al layout del frame
                frame.layout().addWidget(canvas)
                canvas.draw()
                
            except Exception as e:
                print(f"Error al crear el gráfico de inventario: {str(e)}")
                traceback.print_exc()
                self.show_no_data_message(frame, "Error al generar el gráfico")
                
        except Exception as e:
            print(f"Error en load_inventario_por_categoria_chart: {str(e)}")
            traceback.print_exc()
            if frame:
                self.show_no_data_message(frame, "Error al cargar los datos")
                icon_label.setPixmap(QPixmap(":/icons/alert-circle").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                # Mensaje
                msg_label = QLabel("No hay datos de inventario disponibles")
                msg_label.setAlignment(Qt.AlignCenter)
                msg_label.setStyleSheet("""
                    QLabel {
                        color: #78909C;
                        font-size: 12px;
                        margin-top: 10px;
                    }
                """)
                
                layout.addStretch()
                layout.addWidget(icon_label)
                layout.addWidget(msg_label)
                layout.addStretch()
                
                # Reemplazar el contenido del frame
                self.replace_chart_content(frame, widget)
                return
                
            # Filtrar categorías con stock > 0 y ordenar
            categorias = [c for c in categorias if c['stock_total'] > 0]
            categorias.sort(key=lambda x: x['stock_total'], reverse=True)
            
            # Limitar a 5 categorías principales + "Otras"
            if len(categorias) > 5:
                otras = {
                    '_id': 'Otras',
                    'stock_total': sum(c['stock_total'] for c in categorias[5:]),
                    'cantidad_productos': sum(c.get('cantidad_productos', 0) for c in categorias[5:])
                }
                categorias = categorias[:5] + [otras]
            
            nombres = [str(c['_id']).capitalize() for c in categorias]
            stock = [int(c['stock_total']) for c in categorias]
            
            # Crear figura con tamaño adaptativo
            fig = Figure(figsize=(10, 6), dpi=100)  # Aumentado el tamaño
            ax = fig.add_subplot(111)
            
            # Esquema de colores profesional
            colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1']
            
            # Configuración del gráfico de pastel
            wedges, texts, autotexts = ax.pie(
                stock,
                labels=None,  # No mostrar etiquetas directamente en el gráfico
                autopct=lambda p: f'{p:.1f}%' if p >= 5 else '',  # Solo mostrar porcentajes >= 5%
                startangle=90,
                colors=colors[:len(stock)],
                wedgeprops=dict(width=0.6, edgecolor='white', linewidth=1.5),  # Anillo más grueso
                pctdistance=0.75,  # Porcentajes más cerca del centro
                textprops={'fontsize': 10, 'fontweight': 'bold', 'color': 'white'},
                shadow=True,  # Sombra para dar profundidad
                explode=[0.05] * len(stock)  # Separar ligeramente las secciones
            )
            
            # Ajustar el tamaño y posición de los porcentajes
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_bbox(dict(facecolor='#00000040', edgecolor='none', boxstyle='round,pad=0.2'))
            
            # Añadir título informativo
            total_stock = sum(stock)
            ax.set_title(f'Total Stock: {total_stock:,} unidades', 
                        pad=20, fontsize=12, color='#37474F')
            
            # Añadir leyenda con información detallada
            legend_labels = []
            for nombre, cantidad, pct in zip(nombres, stock, [f"{s/sum(stock)*100:.1f}%" for s in stock]):
                legend_labels.append(f"{nombre}: {cantidad:,} u. ({pct})")
            
            # Posición y estilo de la leyenda
            legend = ax.legend(
                wedges,
                legend_labels,
                title="Categorías",
                loc="center left",
                bbox_to_anchor=(1, 0.5),  # Alinear a la derecha
                fontsize=9,
                title_fontsize=10,
                frameon=False
            )
            
            # Ajustar diseño
            fig.patch.set_facecolor('#FFFFFF')
            fig.tight_layout(rect=[0, 0, 0.8, 0.95])  # Dejar espacio para la leyenda
            
            # Asegurar que el gráfico sea circular
            ax.axis('equal')
            
            # Mostrar el gráfico en el frame
            canvas = FigureCanvas(fig)
            self.replace_chart_content(frame, canvas)
            
        except Exception as e:
            print(f"Error en load_inventario_por_categoria_chart: {str(e)}")
            traceback.print_exc()

    def get_productos_mas_vendidos(self, limit=5):
        """Obtiene los productos más vendidos"""
        pipeline = [
            {"$unwind": "$productos"},
            {"$group": {"_id": "$productos.nombre", "cantidad": {"$sum": "$productos.cantidad"}}},
            {"$sort": {"cantidad": -1}},
            {"$limit": limit}
        ]
        return list(self.db.ventas.aggregate(pipeline))

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
                
            # Calcular el total para el porcentaje de "Otros"
            total_stock = sum(c['stock_total'] for c in categorias)
            
            # Si hay más de 5 categorías, agrupar las menores en "Otros"
            if len(categorias) > 5:
                # Tomar las 4 principales
                principales = categorias[:4]
                
                # Sumar el resto en "Otros"
                otros_stock = sum(c['stock_total'] for c in categorias[4:])
                otros_cantidad = sum(c['cantidad_productos'] for c in categorias[4:])
                
                # Crear la entrada "Otros" si hay stock
                if otros_stock > 0:
                    otros = {
                        "_id": "Otros",
                        "stock_total": otros_stock,
                        "cantidad_productos": otros_cantidad
                    }
                    # Reconstruir la lista con las principales + "Otros"
                    categorias = principales + [otros]
            
            # Asegurarse de que los nombres de categoría sean strings
            for cat in categorias:
                if not isinstance(cat['_id'], str):
                    cat['_id'] = str(cat['_id'])
            
            return categorias
            
        except Exception as e:
            print(f"Error en get_inventario_por_categoria: {str(e)}")
            traceback.print_exc()
            return []

    def replace_chart_content(self, frame, canvas):
        """Reemplaza el contenido de un frame con un nuevo gráfico"""
        try:
            # Obtener el contenedor del gráfico (segundo widget en el layout)
            chart_container = frame.findChild(QWidget)
            if not chart_container:
                return
                
            # Limpiar el contenedor actual
            layout = chart_container.layout()
            if not layout:
                layout = QVBoxLayout(chart_container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                chart_container.setLayout(layout)
            
            # Eliminar widgets existentes
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Configurar el canvas
            canvas.setParent(chart_container)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Añadir el canvas al layout
            layout.addWidget(canvas)
            
            # Asegurarse de que el canvas se redibuje
            canvas.draw()
            
            # Forzar actualización del layout
            chart_container.updateGeometry()
            frame.updateGeometry()
            
        except Exception as e:
            print(f"Error en replace_chart_content: {str(e)}")
            traceback.print_exc()