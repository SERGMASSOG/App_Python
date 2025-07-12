from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QStackedWidget, QFrame, 
                              QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punto de Venta")
        self.setMinimumSize(1200, 900)
        self.setStyleSheet("background: #111;")
        self.setWindowIcon(QIcon("logo.ico"))

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
    
        # Barra lateral modernizada
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(210)
        self.sidebar_frame.setStyleSheet('''
            QFrame {
                background: #111;
                border-top-left-radius: 18px;
                border-bottom-left-radius: 18px;
            }
        ''')
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo y nombre app
        logo = QLabel("<b style='color:#FFFFFF;font-size:28px'></b> <span style='color:#FFFFFF;font-size:18px;'>🦋 Angel_Store 🦋</span>")
        logo.setFixedHeight(60)
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        sidebar_layout.addWidget(logo)

        # Botones de navegación
        nav_btns = [
            ("Dashboard", "🏠"),
            ("Inventario", "📦"),
            ("CRM Clientes", "👥"),
            ("Contabilidad", "💼"),
            ("Historial Ventas", "🧾")
        ]
        self.nav_buttons = []
        for idx, (text, icon) in enumerate(nav_btns):
            btn = QPushButton(f"  {icon}  {text}")
            btn.setFixedHeight(44)
            btn.setStyleSheet(f'''
                QPushButton {{
                    color: #fff;
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    text-align: left;
                    padding-left: 26px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: #2C3A4A;
                }}
            ''')
            btn.clicked.connect(lambda _, i=idx: self.display_page(i))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # Botón usuario parte inferior
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import QPoint
        self.user_btn = QPushButton("  👤 Angel_Store\nuser@email.com")
        self.user_btn.setStyleSheet('''
            QPushButton {
                color: #fff;
                background: #2C3A4A;
                border: none;
                font-size: 15px;
                text-align: left;
                padding: 12px 18px;
                border-radius: 12px;
                margin-bottom: 18px;
            }
            QPushButton:hover {
                background: #4ADE80;
                color: #222B36;
            }
        ''')
        self.user_btn.setFixedHeight(54)
        sidebar_layout.addWidget(self.user_btn)
        # Menú desplegable para el botón de usuario
        self.user_menu = QMenu()
        self.action_logout = self.user_menu.addAction("Cerrar Sesión")
        self.action_exit = self.user_menu.addAction("Salir")
        self.user_btn.clicked.connect(self.toggle_user_menu)
        self.action_logout.triggered.connect(self.logout)
        self.action_exit.triggered.connect(self.exit_app)

        self.sidebar_frame.setLayout(sidebar_layout)

        # Páginas principales
        self.pages = QStackedWidget()
        self.pages.addWidget(self.page_dashboard())      # 0
        self.pages.addWidget(self.page_inventario())    # 1
        self.pages.addWidget(self.page_crm())           # 2
        self.pages.addWidget(self.page_contabilidad())  # 3
        self.pages.addWidget(self.page_ventas())        # 4
        self.pages.setStyleSheet("background: #FFFFFF;")

        # Widget contenedor para el área principal (botón hamburguesa y páginas)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_widget.setLayout(self.content_layout)
        self.content_layout.addWidget(self.pages)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.content_widget)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

    def toggle_user_menu(self):
        from PySide6.QtCore import QPoint
        self.user_menu.exec_(self.user_btn.mapToGlobal(QPoint(0, self.user_btn.height())))

    def logout(self):
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def exit_app(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()


        self.sidebar_frame.setLayout(sidebar_layout)

        # Páginas principales
        self.pages = QStackedWidget()
        self.pages.addWidget(self.page_dashboard())      # 0
        self.pages.addWidget(self.page_inventario())    # 1
        self.pages.addWidget(self.page_crm())           # 2
        self.pages.addWidget(self.page_contabilidad())  # 3
        self.pages.addWidget(self.page_ventas())        # 4
        self.pages.setStyleSheet("background: #FFFFFF;")

        # Botón hamburguesa flotante para cuando la barra lateral esté oculta
        self.floating_toggle_btn = QPushButton()
        self.floating_toggle_btn.setIcon(QIcon.fromTheme("application-menu"))
        self.floating_toggle_btn.setText("≡ Opciones")
        self.floating_toggle_btn.setFixedHeight(40)
        self.floating_toggle_btn.setStyleSheet('''
            QPushButton {
                background: #FFFFFF;
                border: none;
                font-size: 18px;
                text-align: left;
                padding-left: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: black;
            }
        ''')
        self.floating_toggle_btn.clicked.connect(self.toggle_sidebar)
        self.floating_toggle_btn.hide()

        # Widget contenedor para el área principal (botón hamburguesa y páginas)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_widget.setLayout(self.content_layout)
        self.content_layout.addWidget(self.floating_toggle_btn, alignment=Qt.AlignLeft)
        self.content_layout.addWidget(self.pages)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.content_widget)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)
        self.sidebar_visible = True

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar_frame.setVisible(self.sidebar_visible)
        self.floating_toggle_btn.setVisible(not self.sidebar_visible)

    def page_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        widget.setStyleSheet("background: #F6F7FB; border-radius: 18px;")

        # Encabezado con botón y búsqueda
        header = QHBoxLayout()
        back_btn = QPushButton("←")
        back_btn.setFixedSize(38, 38)
        back_btn.setStyleSheet('''
            QPushButton {
                background: #fff;
                border: none;
                border-radius: 10px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: #E0E7EF;
            }
        ''')
        search = QPushButton("🔍     Search")
        search.setFixedHeight(38)
        search.setStyleSheet('''
            QPushButton {
                background: #fff;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                padding-left: 16px;
                color: #888;
                text-align: left;
            }
        ''')
        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(search)
        layout.addLayout(header)

        # Tarjetas resumen
        cards = QHBoxLayout()
        for color, value, label, percent in [
            ("#4ADE80", "51", "Lorem", "40%"),
            ("#F87171", "12", "Ipsum", "80%"),
            ("#FACC15", "87", "Dolor", "35%"),
            ("#818CF8", "32", "Sit", "35%"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: #fff;
                    border-radius: 14px;
                    min-width: 140px;
                    max-width: 160px;
                    min-height: 90px;
                    border: 1px solid #F1F1F1;
                }}
            """)
            v = QVBoxLayout()
            v.setAlignment(Qt.AlignTop)
            t = QLabel(f"<span style='font-size:26px;font-weight:bold;color:{color}'>{value}</span>")
            t2 = QLabel(f"<span style='color:#8A8A8A;font-size:15px;'>{label}</span>")
            bar = QFrame()
            bar.setFixedHeight(8)
            bar.setStyleSheet(f"background: #E5E7EB; border-radius: 4px;")
            progress = QFrame(bar)
            progress.setGeometry(0, 0, int(int(percent[:-1])*1.2), 8)
            progress.setStyleSheet(f"background: {color}; border-radius: 4px;")
            v.addWidget(t)
            v.addWidget(t2)
            v.addWidget(bar)
            card.setLayout(v)
            cards.addWidget(card)
        layout.addLayout(cards)

        # Gráfico de barras (dummy)
        graph = QFrame()
        graph.setStyleSheet('''
            QFrame {
                background: #fff;
                border-radius: 14px;
                border: 1px solid #F1F1F1;
            }
        ''')
        graph.setFixedHeight(140)
        graph_layout = QHBoxLayout()
        graph_layout.setContentsMargins(28, 16, 28, 16)
        for val in [30, 40, 47, 50, 55, 48, 49]:
            bar = QFrame()
            bar.setFixedWidth(18)
            bar.setFixedHeight(val+40)
            bar.setStyleSheet("background: #F87171; border-radius: 6px;")
            graph_layout.addWidget(bar, alignment=Qt.AlignBottom)
        graph.setLayout(graph_layout)
        layout.addWidget(graph)

        # Tabla resumen
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
        table = QTableWidget(4, 3)
        table.setHorizontalHeaderLabels(["Category name", "Value", "Change"])
        data = [
            ("Lorem Ipsum", "332", "+4.3%"),
            ("Dolor", "173", "+2.1%"),
            ("Sit amet", "96", "-2.5%"),
            ("Consectetuer", "63", "+5.3%"),
        ]
        for row, (cat, val, chg) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(cat))
            table.setItem(row, 1, QTableWidgetItem(val))
            table.setItem(row, 2, QTableWidgetItem(chg))
        table.setStyleSheet('''
            QTableWidget {
                background: #fff;
                border-radius: 14px;
                border: 1px solid #F1F1F1;
                font-size: 15px;
            }
            QHeaderView::section {
                background: #F6F7FB;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
        ''')
        table.setFixedHeight(140)
        layout.addWidget(table)

        # Tarjetas de objetos
        obj_cards = QHBoxLayout()
        for color, txt in [
            ("#222B36", "Object name"),
            ("#F87171", "Object name"),
            ("#4ADE80", "Object name"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {color};
                    border-radius: 14px;
                    min-width: 180px;
                    max-width: 220px;
                    min-height: 70px;
                }}
            """)
            v = QVBoxLayout()
            v.addWidget(QLabel(f"<span style='color:white;font-size:20px;'>📷</span>"))
            v.addWidget(QLabel(f"<span style='color:white;font-size:16px;'>{txt}</span>"))
            card.setLayout(v)
            obj_cards.addWidget(card)
        layout.addLayout(obj_cards)

        widget.setLayout(layout)
        return widget

    def page_inventario(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setStyleSheet("background: #F5F5F5;")
        layout.setContentsMargins(40, 20, 40, 20)  # Márgenes consistentes
        
        # Título de la página
        title_frame = QFrame()
        title_frame.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 20)
        
        title_label = QLabel("Gestión de Inventario")
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_frame.setLayout(title_layout)
        layout.addWidget(title_frame)
        
        # Contenedor de la tabla
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla de inventario (7 columnas)
        table = QTableWidget(4, 7)
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: none;
                font-size: 15px;
                alternate-background-color: #F9F9F9;
            }
            QHeaderView::section {
                background: #F6F7FB;
                border: none;
                font-weight: bold;
                font-size: 15px;
                padding: 12px;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #F1F1F1;
            }
        """)
        
        # Configuración de la tabla 
        table.setHorizontalHeaderLabels(["Referencia", "Nombre", "Cantidad", "Precio_unitario", "Precio_total", "Valor_Venta", "Utilidad"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacerla de solo lectura
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background: #000000;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 15px;
                padding: 12px;
            }
        """)
        # Datos de ejemplo
        data = [
            ("Lorem Ipsum", "332", "$123,456", "$456,789", "$123,456", "$456,789", "$123,456"),
            ("Dolor", "173", "$45,678", "$456,789", "$123,456", "$456,789", "$123,456"),
            ("Sit amet", "96", "$12,345", "$456,789", "$123,456", "$456,789", "$123,456"),
            ("Consectetuer", "63", "$8,901", "$456,789", "$123,456", "$456,789", "$123,456"),
        ]
        
        # Llenar la tabla
        for row, (referencia, nombre, cantidad, precio_unitario, precio_total, valor_venta, utilidad) in enumerate(data):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(referencia))
            table.setItem(row, 1, QTableWidgetItem(nombre))
            table.setItem(row, 2, QTableWidgetItem(cantidad))
            table.setItem(row, 3, QTableWidgetItem(precio_unitario))
            table.setItem(row, 4, QTableWidgetItem(precio_total))
            table.setItem(row, 5, QTableWidgetItem(valor_venta))
            table.setItem(row, 6, QTableWidgetItem(utilidad))
        
        # Ajustar tamaño de columnas
        table.resizeColumnsToContents()
        table.setColumnWidth(0, 200)  # Ancho fijo para la columna de nombre
        
        table_layout.addWidget(table)
        table_container.setLayout(table_layout)
        layout.addWidget(table_container)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def page_crm(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setStyleSheet("background: #FFFFFF;")
        label = QLabel("CRM de Clientes")
        label.setStyleSheet("color: black; font-size: 32px; font-weight: bold; margin-top: 80px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def page_contabilidad(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setStyleSheet("background: #FFFFFF;")
        label = QLabel("Módulo de Contabilidad")
        label.setStyleSheet("color: black; font-size: 32px; font-weight: bold; margin-top: 80px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def page_ventas(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setStyleSheet("background: #FFFFFF;")
        label = QLabel("Módulo de Ventas")
        label.setStyleSheet("color: black; font-size: 32px; font-weight: bold; margin-top: 80px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def display_page(self, index):
        self.pages.setCurrentIndex(index)
