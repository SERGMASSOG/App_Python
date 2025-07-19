# Mantén tus imports actuales...
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QLineEdit, QLabel, QComboBox,
    QMenu, QAbstractItemView, QDialog, QFileDialog
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
        self.setup_ui()
        self.load_inventario()

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

                self.table.setItem(row_pos, 0, QTableWidgetItem(str(producto.get("codigo", ""))))
                self.table.setItem(row_pos, 1, QTableWidgetItem(str(producto.get("nombre", ""))))
                self.table.setItem(row_pos, 2, QTableWidgetItem(str(producto.get("descripcion", ""))))
                self.table.setItem(row_pos, 3, QTableWidgetItem(str(producto.get("categoria", ""))))
                self.table.setItem(row_pos, 4, QTableWidgetItem(str(producto.get("precio", ""))))
                self.table.setItem(row_pos, 5, QTableWidgetItem(str(producto.get("stock_actual", ""))))
                self.table.setItem(row_pos, 6, QTableWidgetItem(str(producto.get("stock_minimo", ""))))
                self.table.setItem(row_pos, 7, QTableWidgetItem(str(producto.get("estado", ""))))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar el inventario: {str(e)}")

    def agregar_producto(self):
        """Abre el diálogo para agregar un nuevo producto"""
        dialog = InventarioDialog(self.db)
        if dialog.exec() == QDialog.Accepted:
            self.load_inventario()

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

        dialog = InventarioDialog(self.db, producto)
        if dialog.exec() == QDialog.Accepted:
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

    def load_inventario(self):
        """Carga los productos del inventario en la tabla"""
        try:
            self.table.setRowCount(0)  # Limpiar tabla
            inventario = list(self.inventario_collection.find())

            for producto in inventario:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(producto.get("codigo", "")))
                self.table.setItem(row_position, 1, QTableWidgetItem(producto.get("nombre", "")))
                self.table.setItem(row_position, 2, QTableWidgetItem(producto.get("descripcion", "")))
                self.table.setItem(row_position, 3, QTableWidgetItem(producto.get("categoria", "")))
                self.table.setItem(row_position, 4, QTableWidgetItem(str(producto.get("precio", ""))))
                self.table.setItem(row_position, 5, QTableWidgetItem(str(producto.get("stock_actual", ""))))
                self.table.setItem(row_position, 6, QTableWidgetItem(str(producto.get("stock_minimo", ""))))
                self.table.setItem(row_position, 7, QTableWidgetItem(producto.get("estado", "")))

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

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        search_layout = QHBoxLayout()

        self.cmb_categoria = QComboBox()
        self.cmb_categoria.addItem("Todas las categorías", "")
        self.cmb_categoria.addItems([
            "Camisas", "Pantalones", "Zapatos", "Gafas", 
            "Relojes", "Ropa Deportiva", "Faldas", "Gorros", "Otros"
        ])
        self.cmb_categoria.currentIndexChanged.connect(self.filtrar_inventario)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.textChanged.connect(self.filtrar_inventario)

        btn_agregar = QPushButton("Nuevo Producto")
        btn_agregar.clicked.connect(self.agregar_producto)

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.clicked.connect(self.load_inventario)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_producto)

        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self.editar_producto)

        btn_export_pdf = QPushButton("Exportar PDF")
        btn_export_pdf.clicked.connect(self.exportar_pdf)

        btn_export_excel = QPushButton("Exportar Excel")
        btn_export_excel.clicked.connect(self.exportar_excel)

        # Estilo
        button_style = """
            QPushButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
            QPushButton:disabled {
                background-color: #FFCCBC;
            }
        """
        for btn in [btn_agregar, btn_actualizar, btn_eliminar, btn_editar, btn_export_pdf, btn_export_excel]:
            btn.setStyleSheet(button_style)

        search_layout.addWidget(QLabel("Categoría:"))
        search_layout.addWidget(self.cmb_categoria)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        search_layout.addWidget(btn_agregar)
        search_layout.addWidget(btn_actualizar)
        search_layout.addWidget(btn_eliminar)
        search_layout.addWidget(btn_editar)
        search_layout.addWidget(btn_export_pdf)
        search_layout.addWidget(btn_export_excel)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Código', 'Nombre', 'Descripción', 'Categoría',
            'Precio', 'Stock Actual', 'Stock Mínimo', 'Estado'
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""QTableWidget {background: white;}""")

        layout.addLayout(search_layout)
        layout.addWidget(self.table)

    # ... tus funciones load_inventario(), filtrar_inventario(), etc. siguen iguales ...

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
