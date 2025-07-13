from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QLineEdit, QTableWidget, QHeaderView, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QFrame, QTableWidgetItem, QMenu, QComboBox, QFormLayout, QDialog, QDateEdit, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, QPoint, QDate
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punto de Venta")
        self.setMinimumSize(1200, 900)
        self.setStyleSheet("background: #111;")
        self.setWindowIcon(QIcon("Style_app/Login.png"))

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
        logo = QLabel("<b style='color:#FFFFFF;font-size:28px'></b> <span style='color:#FFFFFF;font-size:18px;'>Punto de Venta</span>")
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
        self.user_btn = QPushButton("  👤 Usuario\nuser@email.com")
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
        self.pages.addWidget(self.page_dashboard())     # 0
        self.pages.addWidget(self.page_inventario())    # 1
        self.pages.addWidget(self.page_crm())           # 2
        self.pages.addWidget(self.page_contabilidad())  # 3
        self.pages.addWidget(self.page_ventas())        # 4
        self.pages.setStyleSheet("background: #FFFFFF;")

        # Añadir widgets al layout principal
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.pages)
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

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar_frame.setVisible(self.sidebar_visible)
        self.floating_toggle_btn.setVisible(not self.sidebar_visible)

    def display_page(self, index):
        """
        Cambia la página mostrada en el QStackedWidget según el índice recibido.
        """
        self.pages.setCurrentIndex(index)

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

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def page_inventario(self):
        from db.mongo_connection import get_all_inventario
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        widget.setStyleSheet("background: #F6F7FB; border-radius: 18px;")

        # Título
        title = QLabel("Inventario")
        title.setStyleSheet("font-size: 32px; color: #F0460E; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Filtros de búsqueda
        filter_layout = QHBoxLayout()
        self.inventario_id_input = QLineEdit()
        self.inventario_id_input.setPlaceholderText("Buscar por ID de producto")
        from PySide6.QtWidgets import QDateEdit
        self.inventario_fecha_input = QDateEdit()
        self.inventario_fecha_input.setCalendarPopup(True)
        self.inventario_fecha_input.setDisplayFormat("yyyy-MM-dd")
        btn_buscar_producto = QPushButton("Buscar")
        from db.mongo_connection import get_productos_by_id_fecha
        def buscar_producto():
            producto_id = self.inventario_id_input.text().strip()
            fecha = self.inventario_fecha_input.date().toString("yyyy-MM-dd") if self.inventario_fecha_input.date().isValid() else None
            if not producto_id and not fecha:
                productos = get_all_inventario()
            else:
                productos = get_productos_by_id_fecha(producto_id if producto_id else None, fecha if fecha else None)
            table.setRowCount(len(productos))
            for row, item in enumerate(productos):
                table.setItem(row, 0, QTableWidgetItem(str(item.get("referencia", ""))))
                table.setItem(row, 1, QTableWidgetItem(str(item.get("nombre", ""))))
                table.setItem(row, 2, QTableWidgetItem(str(item.get("cantidad", ""))))
                table.setItem(row, 3, QTableWidgetItem(str(item.get("precio_unitario", ""))))
                table.setItem(row, 4, QTableWidgetItem(str(item.get("precio_total", ""))))
                table.setItem(row, 5, QTableWidgetItem(str(item.get("valor_venta", ""))))
                table.setItem(row, 6, QTableWidgetItem(str(item.get("utilidad", ""))))
                table.setItem(row, 7, QTableWidgetItem(str(item.get("fecha", ""))))
        btn_buscar_producto.clicked.connect(buscar_producto)
        filter_layout.addWidget(self.inventario_id_input)
        filter_layout.addWidget(self.inventario_fecha_input)
        filter_layout.addWidget(btn_buscar_producto)
        layout.addLayout(filter_layout)

        # Botones de acción
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        from db.mongo_connection import insert_producto, update_producto, delete_producto, get_all_inventario
        action_layout = QHBoxLayout()

        # Tabla de inventario (debe estar antes de las funciones que la usan)
        data = get_all_inventario()
        headers = ["Referencia", "Nombre", "Cantidad", "Precio Unitario", "Precio Total", "Valor Venta", "Utilidad", "Fecha"]
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(str(item.get("referencia", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(item.get("nombre", ""))))
            table.setItem(row, 2, QTableWidgetItem(str(item.get("cantidad", ""))))
            table.setItem(row, 3, QTableWidgetItem(str(item.get("precio_unitario", ""))))
            table.setItem(row, 4, QTableWidgetItem(str(item.get("precio_total", ""))))
            table.setItem(row, 5, QTableWidgetItem(str(item.get("valor_venta", ""))))
            table.setItem(row, 6, QTableWidgetItem(str(item.get("utilidad", ""))))
            table.setItem(row, 7, QTableWidgetItem(str(item.get("fecha", ""))))
        # Estilo: texto negro sobre fondo blanco
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                color: #111;
                font-size: 17px;
            }
            QHeaderView::section {
                background: #F0460E;
                color: #fff;
                font-weight: bold;
                font-size: 17px;
                border: none;
            }
            QTableWidget QTableCornerButton::section {
                background: #F0460E;
                border: none;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        def cargar_tabla_inventario():
            data = get_all_inventario()
            table.setRowCount(len(data))
            for row, item in enumerate(data):
                table.setItem(row, 0, QTableWidgetItem(str(item.get("referencia", ""))))
                table.setItem(row, 1, QTableWidgetItem(str(item.get("nombre", ""))))
                table.setItem(row, 2, QTableWidgetItem(str(item.get("cantidad", ""))))
                table.setItem(row, 3, QTableWidgetItem(str(item.get("precio_unitario", ""))))
                table.setItem(row, 4, QTableWidgetItem(str(item.get("precio_total", ""))))
                table.setItem(row, 5, QTableWidgetItem(str(item.get("valor_venta", ""))))
                table.setItem(row, 6, QTableWidgetItem(str(item.get("utilidad", ""))))
                table.setItem(row, 7, QTableWidgetItem(str(item.get("fecha", ""))))
            return data

        def dialog_producto(producto=None):
            from PySide6.QtWidgets import QDateEdit
            from PySide6.QtCore import QDate
            dialog = QDialog()
            dialog.setWindowTitle("Agregar/Actualizar producto")
            form = QFormLayout()
            fecha_label = QLabel("Fecha")
            fecha_edit = QDateEdit()
            fecha_edit.setCalendarPopup(True)
            fecha_edit.setDisplayFormat("yyyy-MM-dd")
            if producto:
                fecha_edit.setDate(QDate.fromString(producto.get("fecha", ""), "yyyy-MM-dd"))
            else:
                fecha_edit.setDate(QDate.currentDate())
            referencia = QLineEdit()
            if producto:
                referencia.setText(producto.get("referencia", ""))
            nombre = QLineEdit()
            if producto:
                nombre.setText(producto.get("nombre", ""))
            cantidad = QLineEdit()
            if producto:
                cantidad.setText(str(producto.get("cantidad", "")))
            precio_unitario = QLineEdit()
            if producto:
                precio_unitario.setText(str(producto.get("precio_unitario", "")))
            precio_total = QLineEdit()
            if producto:
                precio_total.setText(str(producto.get("precio_total", "")))
            valor_venta = QLineEdit()
            if producto:
                valor_venta.setText(str(producto.get("valor_venta", "")))
            utilidad = QLineEdit()
            if producto:
                utilidad.setText(str(producto.get("utilidad", "")))
            form.setVerticalSpacing(10)
            form.addRow(fecha_label, fecha_edit)
            form.addRow("Referencia", referencia)
            form.addRow("Nombre", nombre)
            form.addRow("Cantidad", cantidad)
            form.addRow("Precio Unitario", precio_unitario)
            form.addRow("Precio Total", precio_total)
            form.addRow("Valor Venta", valor_venta)
            form.addRow("Utilidad", utilidad)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            form.addRow(buttons)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            dialog.setLayout(form)
            if dialog.exec() == QDialog.Accepted:
                if not fecha_edit.date().isValid():
                    QMessageBox.warning(dialog, "Error", "Debes seleccionar una fecha válida.")
                    return None
                if not referencia.text().strip():
                    QMessageBox.warning(dialog, "Error", "El campo Referencia es obligatorio.")
                    return None
                return {
                    "referencia": referencia.text().strip(),
                    "nombre": nombre.text().strip(),
                    "cantidad": int(cantidad.text().strip()) if cantidad.text().strip().isdigit() else 0,
                    "precio_unitario": float(precio_unitario.text().strip()) if precio_unitario.text().strip().replace('.', '', 1).isdigit() else 0.0,
                    "precio_total": float(precio_total.text().strip()) if precio_total.text().strip().replace('.', '', 1).isdigit() else 0.0,
                    "valor_venta": float(valor_venta.text().strip()) if valor_venta.text().strip().replace('.', '', 1).isdigit() else 0.0,
                    "utilidad": float(utilidad.text().strip()) if utilidad.text().strip().replace('.', '', 1).isdigit() else 0.0,
                    "fecha": fecha_edit.date().toString("yyyy-MM-dd")
                }
            return None

        def agregar_producto():
            prod = dialog_producto()
            if prod:
                insert_producto(prod)
                QMessageBox.information(table, "Éxito", "Producto agregado.")
                cargar_tabla_inventario()

        def actualizar_producto():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(table, "Error", "Selecciona un producto para actualizar.")
                return
            data = get_all_inventario()
            producto = data[row]
            prod_edit = dialog_producto(producto)
            if prod_edit:
                update_producto(str(producto["_id"]), prod_edit)
                QMessageBox.information(table, "Éxito", "Producto actualizado.")
                cargar_tabla_inventario()

        def borrar_producto():
            row = table.currentRow()
            if row < 0:
                QMessageBox.warning(table, "Error", "Selecciona un producto para borrar.")
                return
            data = get_all_inventario()
            producto = data[row]
            delete_producto(str(producto["_id"]))
            QMessageBox.information(table, "Éxito", "Producto eliminado.")
            cargar_tabla_inventario()

        btn_agregar_producto = QPushButton("Agregar producto")
        btn_agregar_producto.clicked.connect(agregar_producto)
        btn_actualizar_producto = QPushButton("Actualizar producto")
        btn_actualizar_producto.clicked.connect(actualizar_producto)
        btn_borrar_producto = QPushButton("Borrar producto")
        btn_borrar_producto.clicked.connect(borrar_producto)
        action_layout.addWidget(btn_agregar_producto)
        action_layout.addWidget(btn_actualizar_producto)
        action_layout.addWidget(btn_borrar_producto)
        layout.addLayout(action_layout)

        # Cargar productos al iniciar
        cargar_tabla_inventario()

        # Tabla de inventario
        data = get_all_inventario()
        headers = ["Nombre", "Categoría", "Cantidad", "Precio", "Descripción"]
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        for row, item in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(str(item.get("nombre", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(item.get("categoria", ""))))
            table.setItem(row, 2, QTableWidgetItem(str(item.get("cantidad", ""))))
            table.setItem(row, 3, QTableWidgetItem(str(item.get("precio", ""))))
            table.setItem(row, 4, QTableWidgetItem(str(item.get("descripcion", ""))))
        # Estilo: texto negro sobre fondo blanco
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                color: #111;
                font-size: 17px;
            }
            QHeaderView::section {
                background: #F0460E;
                color: #fff;
                font-weight: bold;
                font-size: 17px;
                border: none;
            }
            QTableWidget QTableCornerButton::section {
                background: #F0460E;
                border: none;
            }
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(table)

        widget.setLayout(layout)
        return widget

    def page_crm(self):
        from PySide6.QtWidgets import QMessageBox
        from db.mongo_connection import get_cliente_by_id, get_all_clientes, insert_cliente, update_cliente, delete_cliente
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        widget.setStyleSheet("background: #F6F7FB; border-radius: 18px;")

        # Título
        label = QLabel("CRM Clientes")
        label.setStyleSheet("font-size: 32px; color: #F0460E; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Buscar cliente por ID
        search_layout = QHBoxLayout()
        self.cliente_id_input = QLineEdit()
        self.cliente_id_input.setPlaceholderText("Buscar por ID de cliente")
        btn_buscar_cliente = QPushButton("Buscar")
        def buscar_cliente():
            cliente_id = self.cliente_id_input.text().strip()
            cliente = get_cliente_by_id(cliente_id)
            if cliente:
                self.cliente_id_form.setText(str(cliente.get("id", "")))
                self.cliente_nombre_form.setText(cliente.get("nombre", ""))
                self.cliente_segundo_nombre_form.setText(cliente.get("segundo_nombre", ""))
                self.cliente_apellido_form.setText(cliente.get("apellido", ""))
                self.cliente_segundo_apellido_form.setText(cliente.get("segundo_apellido", ""))
                self.cliente_email_form.setText(cliente.get("email", ""))
                self.cliente_tel_form.setText(cliente.get("telefono", ""))
                self.cliente_segundo_tel_form.setText(cliente.get("segundo_telefono", ""))
                self.cliente_sexo_form.setCurrentText(cliente.get("sexo", ""))
                self.cliente_id_documento_form.setText(cliente.get("id_documento", ""))
                QMessageBox.information(widget, "Cliente encontrado", f"Cliente {cliente_id} encontrado.")
            else:
                QMessageBox.warning(widget, "No encontrado", "No se encontró el cliente.")
        btn_buscar_cliente.clicked.connect(buscar_cliente)
        search_layout.addWidget(self.cliente_id_input)
        search_layout.addWidget(btn_buscar_cliente)
        layout.addLayout(search_layout)

        # Formulario de cliente
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Campos de cliente
        self.cliente_id_form = QLineEdit()
        self.cliente_id_form.setPlaceholderText("ID del cliente")
        self.cliente_id_form.setStyleSheet('''
            QLineEdit {
                background: #FFFFFF;
                border: 2px solid #E0E7EF;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #F0460E;
            }
        ''')
        form_layout.addRow("ID:", self.cliente_id_form)

        self.cliente_nombre_form = QLineEdit()
        self.cliente_nombre_form.setPlaceholderText("Nombre")
        self.cliente_nombre_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Nombre:", self.cliente_nombre_form)

        self.cliente_segundo_nombre_form = QLineEdit()
        self.cliente_segundo_nombre_form.setPlaceholderText("Segundo nombre")
        self.cliente_segundo_nombre_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Segundo nombre:", self.cliente_segundo_nombre_form)

        self.cliente_apellido_form = QLineEdit()
        self.cliente_apellido_form.setPlaceholderText("Apellido")
        self.cliente_apellido_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Apellido:", self.cliente_apellido_form)

        self.cliente_segundo_apellido_form = QLineEdit()
        self.cliente_segundo_apellido_form.setPlaceholderText("Segundo apellido")
        self.cliente_segundo_apellido_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Segundo apellido:", self.cliente_segundo_apellido_form)

        self.cliente_email_form = QLineEdit()
        self.cliente_email_form.setPlaceholderText("Correo electrónico")
        self.cliente_email_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Correo:", self.cliente_email_form)

        self.cliente_tel_form = QLineEdit()
        self.cliente_tel_form.setPlaceholderText("Teléfono")
        self.cliente_tel_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Teléfono:", self.cliente_tel_form)

        self.cliente_segundo_tel_form = QLineEdit()
        self.cliente_segundo_tel_form.setPlaceholderText("Segundo teléfono")
        self.cliente_segundo_tel_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("Segundo teléfono:", self.cliente_segundo_tel_form)

        self.cliente_sexo_form = QComboBox()
        self.cliente_sexo_form.addItems(["Masculino", "Femenino", "Otro"])
        self.cliente_sexo_form.setStyleSheet('''
            QComboBox {
                background: #FFFFFF;
                border: 2px solid #E0E7EF;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #F0460E;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url("Style_app/down_arrow.png");
                width: 12px;
                height: 12px;
            }
        ''')
        form_layout.addRow("Sexo:", self.cliente_sexo_form)

        self.cliente_id_documento_form = QLineEdit()
        self.cliente_id_documento_form.setPlaceholderText("ID documento")
        self.cliente_id_documento_form.setStyleSheet(self.cliente_id_form.styleSheet())
        form_layout.addRow("ID documento:", self.cliente_id_documento_form)

        # Botones de acción
        btn_agregar_cliente = QPushButton("Agregar cliente")
        btn_agregar_cliente.setStyleSheet('''
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2563EB;
            }
        ''')
        form_layout.addRow(btn_agregar_cliente)

        btn_actualizar_cliente = QPushButton("Actualizar cliente")
        btn_actualizar_cliente.setStyleSheet('''
            QPushButton {
                background: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
        ''')
        form_layout.addRow(btn_actualizar_cliente)

        btn_eliminar_cliente = QPushButton("Eliminar cliente")
        btn_eliminar_cliente.setStyleSheet('''
            QPushButton {
                background: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #DC2626;
            }
        ''')
        form_layout.addRow(btn_eliminar_cliente)

        layout.addLayout(form_layout)

        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(10)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "ID", "Nombre", "Segundo nombre", "Apellido", "Segundo apellido", 
            "Correo", "Teléfono", "Segundo teléfono", "Sexo", "ID documento"
        ])
        self.tabla_clientes.setStyleSheet('''
            QTableWidget {
                background: #FFFFFF;
                color: #111;
                font-size: 14px;
                alternate-background-color: #F5F5F5;
                gridline-color: #E0E7EF;
                selection-background-color: #F0460E;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #F0460E;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        ''')
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_clientes.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_clientes.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_clientes.setAlternatingRowColors(True)
        self.tabla_clientes.setSortingEnabled(True)
        layout.addWidget(self.tabla_clientes)

        # Funciones de cliente
        def cargar_clientes_tabla():
            clientes = get_all_clientes()
            self.tabla_clientes.setRowCount(len(clientes))
            for row, cliente in enumerate(clientes):
                self.tabla_clientes.setItem(row, 0, QTableWidgetItem(str(cliente.get("id", ""))))
                self.tabla_clientes.setItem(row, 1, QTableWidgetItem(cliente.get("nombre", "")))
                self.tabla_clientes.setItem(row, 2, QTableWidgetItem(cliente.get("segundo_nombre", "")))
                self.tabla_clientes.setItem(row, 3, QTableWidgetItem(cliente.get("apellido", "")))
                self.tabla_clientes.setItem(row, 4, QTableWidgetItem(cliente.get("segundo_apellido", "")))
                self.tabla_clientes.setItem(row, 5, QTableWidgetItem(cliente.get("email", "")))
                self.tabla_clientes.setItem(row, 6, QTableWidgetItem(cliente.get("telefono", "")))
                self.tabla_clientes.setItem(row, 7, QTableWidgetItem(cliente.get("segundo_telefono", "")))
                self.tabla_clientes.setItem(row, 8, QTableWidgetItem(cliente.get("sexo", "")))
                self.tabla_clientes.setItem(row, 9, QTableWidgetItem(cliente.get("id_documento", "")))

        def agregar_cliente():
            cliente = {
                "id": self.cliente_id_form.text().strip(),
                "nombre": self.cliente_nombre_form.text().strip(),
                "segundo_nombre": self.cliente_segundo_nombre_form.text().strip(),
                "apellido": self.cliente_apellido_form.text().strip(),
                "segundo_apellido": self.cliente_segundo_apellido_form.text().strip(),
                "email": self.cliente_email_form.text().strip(),
                "telefono": self.cliente_tel_form.text().strip(),
                "segundo_telefono": self.cliente_segundo_tel_form.text().strip(),
                "sexo": self.cliente_sexo_form.currentText(),
                "id_documento": self.cliente_id_documento_form.text().strip()
            }
            if not cliente["id"]:
                QMessageBox.warning(widget, "Error", "El campo ID es obligatorio.")
                return
            insert_cliente(cliente)
            QMessageBox.information(widget, "Éxito", "Cliente agregado.")
            cargar_clientes_tabla()

        def actualizar_cliente():
            cliente_id = self.cliente_id_form.text().strip()
            nuevos_datos = {
                "nombre": self.cliente_nombre_form.text().strip(),
                "segundo_nombre": self.cliente_segundo_nombre_form.text().strip(),
                "apellido": self.cliente_apellido_form.text().strip(),
                "segundo_apellido": self.cliente_segundo_apellido_form.text().strip(),
                "email": self.cliente_email_form.text().strip(),
                "telefono": self.cliente_tel_form.text().strip(),
                "segundo_telefono": self.cliente_segundo_tel_form.text().strip(),
                "sexo": self.cliente_sexo_form.currentText(),
                "id_documento": self.cliente_id_documento_form.text().strip()
            }
            if not cliente_id:
                QMessageBox.warning(widget, "Error", "El campo ID es obligatorio.")
                return
            update_cliente(cliente_id, nuevos_datos)
            QMessageBox.information(widget, "Éxito", "Cliente actualizado.")
            cargar_clientes_tabla()

        def eliminar_cliente():
            cliente_id = self.cliente_id_form.text().strip()
            if not cliente_id:
                QMessageBox.warning(widget, "Error", "El campo ID es obligatorio.")
                return
            result = delete_cliente(cliente_id)
            if result.deleted_count:
                QMessageBox.information(widget, "Éxito", "Cliente eliminado.")
                cargar_clientes_tabla()
                self.cliente_id_form.clear()
                self.cliente_nombre_form.clear()
                self.cliente_segundo_nombre_form.clear()
                self.cliente_apellido_form.clear()
                self.cliente_segundo_apellido_form.clear()
                self.cliente_email_form.clear()
                self.cliente_tel_form.clear()
                self.cliente_segundo_tel_form.clear()
                self.cliente_sexo_form.setCurrentIndex(0)
                self.cliente_id_documento_form.clear()
            else:
                QMessageBox.warning(widget, "Error", "No se encontró el cliente a eliminar.")

        def buscar_cliente():
            cliente_id = self.cliente_id_input.text().strip()
            cliente = get_cliente_by_id(cliente_id)
            if cliente:
                self.cliente_id_form.setText(str(cliente.get("id", "")))
                self.cliente_nombre_form.setText(cliente.get("nombre", ""))
                self.cliente_segundo_nombre_form.setText(cliente.get("segundo_nombre", ""))
                self.cliente_apellido_form.setText(cliente.get("apellido", ""))
                self.cliente_segundo_apellido_form.setText(cliente.get("segundo_apellido", ""))
                self.cliente_email_form.setText(cliente.get("email", ""))
                self.cliente_tel_form.setText(cliente.get("telefono", ""))
                self.cliente_segundo_tel_form.setText(cliente.get("segundo_telefono", ""))
                self.cliente_sexo_form.setCurrentText(cliente.get("sexo", ""))
                self.cliente_id_documento_form.setText(cliente.get("id_documento", ""))
                QMessageBox.information(widget, "Cliente encontrado", f"Cliente {cliente_id} encontrado.")
            else:
                QMessageBox.warning(widget, "No encontrado", "No se encontró el cliente.")

        # Conectar señales
        btn_agregar_cliente.clicked.connect(agregar_cliente)
        btn_actualizar_cliente.clicked.connect(actualizar_cliente)
        btn_eliminar_cliente.clicked.connect(eliminar_cliente)
        self.cliente_id_input.textChanged.connect(buscar_cliente)

        # Cargar datos iniciales
        cargar_clientes_tabla()

        widget.setLayout(layout)
        return widget

    def page_contabilidad(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        widget.setStyleSheet("background: #F6F7FB; border-radius: 18px;")
        label = QLabel("Contabilidad")
        label.setStyleSheet("font-size: 40px; color: #F0460E; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def page_ventas(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        widget.setStyleSheet("background: #F6F7FB; border-radius: 18px;")
        label = QLabel("Historial Ventas")
        label.setStyleSheet("font-size: 40px; color: #F0460E; font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
