# Mantén tus imports actuales...
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLineEdit, QLabel, QComboBox,
    QMenu, QAbstractItemView, QDialog, QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor
from db.mongo_connection import get_db_connection
from dialogs.inventario_dialog import InventarioDialog
import pandas as pd
from fpdf import FPDF

# Aquí comienza tu clase como ya la tenías...

class InventarioManager(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.inventario_collection = self.db['inventario']
        self.metrics = {}
        self.setup_ui()
        self.load_inventario()
        
    def setup_ui(self):
        """Configura la interfaz de usuario del administrador de inventario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        # Selector de categoría
        self.cmb_categoria = QComboBox()
        self.cmb_categoria.addItem("Todas las categorías", "")
        self.cmb_categoria.addItems([
            "Camisas", "Pantalones", "Zapatos", "Gafas", 
            "Relojes", "Ropa Deportiva", "Faldas", "Gorros", "Otros"
        ])
        self.cmb_categoria.currentIndexChanged.connect(self.filtrar_inventario)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.textChanged.connect(self.filtrar_inventario)
        self.search_input.setMinimumWidth(200)

        # Añadir widgets a la barra de búsqueda
        search_layout.addWidget(QLabel("Categoría:"))
        search_layout.addWidget(self.cmb_categoria)
        search_layout.addStretch()
        search_layout.addWidget(QLabel("Buscar:"))
        search_layout.addWidget(self.search_input)

        # Tarjetas de métricas
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(10)
        
        self.metrics = {
            "total_productos": self.create_metric_card("Total Productos", "0", "#4CAF50"),
            "total_stock": self.create_metric_card("Stock Total", "0", "#2196F3"),
            "suma_precios": self.create_metric_card("Valor Total", "$0.00", "#9C27B0"),
            "total_categorias": self.create_metric_card("Categorías", "0", "#FF9800")
        }
        
        for metric in self.metrics.values():
            metrics_layout.addWidget(metric)
        
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_layout)
        metrics_container.setMaximumHeight(100)

        # Botones de acción
        btn_agregar = QPushButton("➕ Agregar Producto")
        btn_editar = QPushButton("✏️ Editar")
        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_exportar_excel = QPushButton("📊 Excel")
        btn_exportar_pdf = QPushButton("📄 PDF")

        # Estilo de los botones
        button_style = """
            QPushButton {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """
        
        for btn in [btn_agregar, btn_editar, btn_eliminar, btn_exportar_excel, btn_exportar_pdf]:
            btn.setStyleSheet(button_style)

        # Conectar señales
        btn_agregar.clicked.connect(self.agregar_producto)
        btn_editar.clicked.connect(self.editar_producto)
        btn_eliminar.clicked.connect(self.eliminar_producto)
        btn_exportar_excel.clicked.connect(self.exportar_excel)
        btn_exportar_pdf.clicked.connect(self.exportar_pdf)

        # Layout de botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_exportar_excel)
        btn_layout.addWidget(btn_exportar_pdf)

        # Tabla de inventario
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Código", "Nombre", "Descripción", "Categoría",
            "Precio", "Stock", "Mínimo", "Estado"
        ])
        
        # Configuración de la tabla
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #FFF3E0;
                gridline-color: #FFB74D;
                border: 1px solid #FFB74D;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #FF9800;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #F57C00;
                border-bottom: 1px solid #F57C00;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #FFE0B2;
            }
            QTableWidget::item:selected {
                background-color: #FFB74D;
                color: white;
            }
        """)
        
        # Ajustar el tamaño de las columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 120)  # Código
        self.table.setColumnWidth(1, 200)  # Nombre
        self.table.setColumnWidth(2, 250)  # Descripción
        self.table.setColumnWidth(3, 120)  # Categoría
        self.table.setColumnWidth(4, 100)  # Precio
        self.table.setColumnWidth(5, 80)   # Stock
        self.table.setColumnWidth(6, 80)   # Mínimo
        
        # Configurar menú contextual
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.mostrar_menu_contextual)

        # Añadir todo al layout principal
        layout.addLayout(search_layout)
        layout.addWidget(metrics_container)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table, 1)  # El 1 hace que la tabla ocupe el espacio restante

    def filtrar_inventario(self):
        try:
            texto = self.search_input.text().strip().lower()
            categoria = self.cmb_categoria.currentText()
            
            filtro = {}
            if categoria and categoria != "Todas las categorías":
                filtro["categoria"] = categoria
            if texto:
                filtro["$or"] = [
                    {"codigo": {"$regex": texto, "$options": "i"}},
                    {"nombre": {"$regex": texto, "$options": "i"}},
                ]

            resultados = list(self.inventario_collection.find(filtro))
            self.table.setRowCount(0)

            for producto in resultados:
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)

                campos = [
                    "codigo", "nombre", "descripcion", "categoria",
                    "precio", "stock_actual", "stock_minimo", "estado"
                ]
                for col, key in enumerate(campos):
                    valor = str(producto.get(key, ""))
                    item = QTableWidgetItem(valor)
                    # Estado en verde, resto negro
                    if key == "estado":
                        item.setForeground(QColor("green"))
                    else:
                        item.setForeground(QColor("black"))
                    self.table.setItem(row_pos, col, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar el inventario: {str(e)}")

    def agregar_producto(self):
        """Abre el diálogo para agregar un nuevo producto"""
        dialog = InventarioDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_item_data()
            # Verificar si ya existe un producto con el mismo código
            if self.inventario_collection.find_one({"codigo": data.get("codigo_barras")}):
                QMessageBox.warning(self, "Error", f"Ya existe un producto con el código: {data.get('codigo_barras')}")
                return
                
            # Transformar campos al esquema de la colección
            nuevo_doc = {
                "codigo": data.get("codigo_barras"),
                "nombre": data.get("nombre"),
                "descripcion": data.get("descripcion"),
                "categoria": data.get("categoria"),
                "precio": float(data.get("precio", 0)),
                "stock_actual": int(data.get("cantidad", 0)),
                "stock_minimo": int(data.get("stock_minimo", 0)),
                "estado": "Disponible"
            }
            try:
                self.inventario_collection.insert_one(nuevo_doc)
                QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
                self.load_inventario()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar el producto: {str(e)}")

    def editar_producto(self):
        """Abre el diálogo para editar el producto seleccionado"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Selecciona un producto para editar.")
            return

        row = self.table.currentRow()
        codigo = self.table.item(row, 0).text()
        producto = self.inventario_collection.find_one({"codigo": codigo})

        if not producto:
            QMessageBox.critical(self, "Error", "Producto no encontrado en la base de datos.")
            return

        # Mapear documento a item_data esperado por el diálogo
        item_data = {
            "codigo_barras": producto.get("codigo", ""),
            "nombre": producto.get("nombre", ""),
            "descripcion": producto.get("descripcion", ""),
            "categoria": producto.get("categoria", ""),
            "precio": producto.get("precio", 0),
            "cantidad": producto.get("stock_actual", 0),
            "stock_minimo": producto.get("stock_minimo", 0)
        }
        dialog = InventarioDialog(parent=self, item_data=item_data)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_item_data()
            updated_doc = {
                "codigo": data.get("codigo_barras"),
                "nombre": data.get("nombre"),
                "descripcion": data.get("descripcion"),
                "categoria": data.get("categoria"),
                "precio": data.get("precio"),
                "stock_actual": data.get("cantidad"),
                "stock_minimo": data.get("stock_minimo")
            }
            try:
                self.inventario_collection.update_one({"_id": producto.get("_id")}, {"$set": updated_doc})
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {str(e)}")
            self.load_inventario()

    def eliminar_producto(self):
        """Elimina el producto seleccionado de la base de datos"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Advertencia", "Selecciona un producto para eliminar.")
            return

        row = self.table.currentRow()
        codigo = self.table.item(row, 0).text()

        confirm = QMessageBox.question(
            self, "Eliminar producto",
            f"¿Estás seguro de eliminar el producto con código '{codigo}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            result = self.inventario_collection.delete_one({"codigo": codigo})
            if result.deleted_count:
                QMessageBox.information(self, "Eliminado", "Producto eliminado exitosamente.")
                self.load_inventario()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")

    def update_metric_cards(self, inventario):
        """Actualiza las tarjetas de métricas con los datos actuales"""
        total_productos = len(inventario)
        total_stock = sum(int(p.get("stock_actual", 0)) for p in inventario)
        suma_precios = sum(float(p.get("precio", 0)) * int(p.get("stock_actual", 0)) for p in inventario)
        categorias = {p.get("categoria", "Otros") for p in inventario}

        self.metrics["total_productos"].findChild(QLabel, "value").setText(str(total_productos))
        self.metrics["total_stock"].findChild(QLabel, "value").setText(str(total_stock))
        self.metrics["suma_precios"].findChild(QLabel, "value").setText(f"${suma_precios:,.2f}")
        self.metrics["total_categorias"].findChild(QLabel, "value").setText(str(len(categorias)))

    def create_metric_card(self, title, initial_value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                min-width: 150px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        label_title = QLabel(title)
        label_title.setStyleSheet("color: #718096; font-size: 14px;")
        label_value = QLabel(initial_value)
        label_value.setObjectName("value")
        label_value.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        card_layout.addWidget(label_title)
        card_layout.addWidget(label_value)
        return card

    def load_inventario(self):
        """Carga los productos del inventario en la tabla"""
        try:
            self.table.setRowCount(0)  # Limpiar tabla
            inventario = list(self.inventario_collection.find())

            # Ajustar ancho de columnas
            self.table.resizeColumnsToContents()
            for producto in inventario:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                campos = [
                    "codigo", "nombre", "descripcion", "categoria",
                    "precio", "stock_actual", "stock_minimo", "estado"
                ]
                for col, key in enumerate(campos):
                    valor = str(producto.get(key, ""))
                    item = QTableWidgetItem(valor)
                    if key == "estado":
                        item.setForeground(QColor("green"))
                    else:
                        item.setForeground(QColor("black"))
                    self.table.setItem(row_position, col, item)

            # Actualizar métricas
            self.update_metric_cards(inventario)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el inventario: {str(e)}")

    def mostrar_menu_contextual(self, position):
        menu = QMenu()

        editar_action = QAction("Editar", self) 
        eliminar_action = QAction("Eliminar", self)

        editar_action.triggered.connect(self.editar_producto)
        eliminar_action.triggered.connect(self.eliminar_producto)

        menu.addAction(editar_action)
        menu.addAction(eliminar_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def exportar_excel(self):
        """Exporta la tabla a un archivo Excel"""
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar como Excel", "", "Excel (*.xlsx)")
            if path:
                data = []
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else '')
                    data.append(row_data)

                df = pd.DataFrame(data, columns=[
                    'Código', 'Nombre', 'Descripción', 'Categoría',
                    'Precio', 'Stock Actual', 'Stock Mínimo', 'Estado'
                ])
                df.to_excel(path, index=False)
                QMessageBox.information(self, "Éxito", f"Inventario exportado a Excel:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a Excel: {str(e)}")

    def exportar_pdf(self):
        """Exporta la tabla a un archivo PDF"""
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", "", "PDF Files (*.pdf)")
            if path:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                pdf.set_fill_color(240, 240, 240)

                headers = [
                    'Código', 'Nombre', 'Descripción', 'Categoría',
                    'Precio', 'Stock', 'Stock Mínimo', 'Estado'
                ]
                col_widths = [20, 30, 40, 25, 20, 15, 20, 20]

                # Encabezados
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
                pdf.ln()

                # Filas
                for row in range(self.table.rowCount()):
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        texto = item.text() if item else ''
                        pdf.cell(col_widths[col], 8, texto[:30], 1)
                    pdf.ln()

                pdf.output(path)
                QMessageBox.information(self, "Éxito", f"Inventario exportado a PDF:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a PDF: {str(e)}")
