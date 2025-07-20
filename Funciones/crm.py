from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QMessageBox, QPushButton, 
    QHBoxLayout, QVBoxLayout, QHeaderView, QLineEdit, QLabel, QWidget,
    QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from db.mongo_connection import get_db_connection

class CRMManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db = get_db_connection()
        self.clientes_collection = self.db['clientes']
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID, nombre o apellido...")
        self.search_input.textChanged.connect(self.buscar_clientes)
        search_layout.addWidget(self.search_input)

        # Botones
        btn_agregar = QPushButton("Agregar Cliente")
        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")
        btn_agregar.setObjectName("btnAgregar")
        btn_editar.setObjectName("btnEditar")
        btn_eliminar.setObjectName("btnEliminar")

        # Conexiones
        btn_agregar.clicked.connect(self.agregar_cliente)
        btn_editar.clicked.connect(self.editar_cliente)
        btn_eliminar.clicked.connect(self.eliminar_cliente)

        # Layout botones
        search_layout.addWidget(btn_agregar)
        search_layout.addWidget(btn_editar)
        search_layout.addWidget(btn_eliminar)

        # ----- Métricas -----
        self.metrics = {}
        metrics_container = QWidget()
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 10, 0, 10)
        metrics_layout.setSpacing(15)

        self.metrics["total_clientes"] = self.create_metric_card("Total Clientes", "0", "#4CAF50")
        self.metrics["clientes_naturales"] = self.create_metric_card("Personas Naturales", "0", "#2196F3")
        self.metrics["clientes_juridicos"] = self.create_metric_card("Personas Jurídicas", "0", "#FF9800")
        self.metrics["pct_hombres"] = self.create_metric_card("% Hombres", "0%", "#03A9F4")
        self.metrics["pct_mujeres"] = self.create_metric_card("% Mujeres", "0%", "#E91E63")

        metrics_layout.addStretch()
        for key in [
            "total_clientes",
            "clientes_naturales",
            "clientes_juridicos",
            "pct_hombres",
            "pct_mujeres"
        ]:
            metrics_layout.addWidget(self.metrics[key])
        metrics_layout.addStretch()

        # Tabla
        self.table_widget = QTableWidget()
        self.setup_clientes_table()

        # Añadir a layout
        layout.addLayout(search_layout)
        layout.addWidget(metrics_container)
        layout.addWidget(self.table_widget)
        layout.setStretchFactor(self.table_widget, 1)
        self.load_clientes()

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

    def update_metric_cards(self):
        try:
            total_clientes = self.clientes_collection.count_documents({})
            naturales = self.clientes_collection.count_documents({"tipo_persona": "Natural"})
            juridicos = self.clientes_collection.count_documents({"tipo_persona": "Jurídica"})
            hombres = self.clientes_collection.count_documents({"sexo": {"$regex": "^m", "$options": "i"}})
            mujeres = self.clientes_collection.count_documents({"sexo": {"$regex": "^f", "$options": "i"}})
            pct_hombres = (hombres / total_clientes * 100) if total_clientes else 0
            pct_mujeres = (mujeres / total_clientes * 100) if total_clientes else 0

            self.metrics["total_clientes"].findChild(QLabel, "value").setText(str(total_clientes))
            self.metrics["clientes_naturales"].findChild(QLabel, "value").setText(str(naturales))
            self.metrics["clientes_juridicos"].findChild(QLabel, "value").setText(str(juridicos))
            self.metrics["pct_hombres"].findChild(QLabel, "value").setText(f"{pct_hombres:.1f}%")
            self.metrics["pct_mujeres"].findChild(QLabel, "value").setText(f"{pct_mujeres:.1f}%")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron calcular métricas: {str(e)}")

    def setup_clientes_table(self):
        headers = [
            'ID Documento', 'Tipo', 'Nombre', 'Segundo Nombre', 'Apellido',
            'Segundo Apellido', 'Email', 'Teléfono', 'Segundo Teléfono', 'Sexo'
        ]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        # Limitar ancho máximo de la columna "Sexo" para que no ocupe demasiado espacio
        header.resizeSection(9, 90)

    def load_clientes(self, filtro=None):
        query = {}
        if filtro:
            query = {
                '$or': [
                    {'id_documento': {'$regex': filtro, '$options': 'i'}},
                    {'nombre': {'$regex': filtro, '$options': 'i'}},
                    {'apellido': {'$regex': filtro, '$options': 'i'}}
                ]
            }
        try:
            clientes = list(self.clientes_collection.find(query, {'_id': 0}))
            self.table_widget.setRowCount(len(clientes))
            # Ajustar ancho según contenido
            self.table_widget.resizeColumnsToContents()
            # Actualizar métricas
            self.update_metric_cards()
            for row, cliente in enumerate(clientes):
                for col, key in enumerate([
                    'id_documento', 'tipo_persona', 'nombre', 'segundo_nombre', 'apellido',
                    'segundo_apellido', 'email', 'telefono', 'segundo_telefono', 'sexo'
                ]):
                    item = QTableWidgetItem(str(cliente.get(key, '')))
                    item.setForeground(QColor("black"))  # <-- Fuerza el texto a negro
                    self.table_widget.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al cargar clientes: {str(e)}')

    def buscar_clientes(self):
        filtro = self.search_input.text().strip()
        self.load_clientes(filtro)

    def agregar_cliente(self):
        from dialogs.cliente_dialog import ClienteDialog
        dialog = ClienteDialog(self)
        if dialog.exec():
            data = dialog.get_cliente_data()
            try:
                self.clientes_collection.insert_one(data)
                QMessageBox.information(self, "Éxito", "Cliente agregado correctamente")
                self.load_clientes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar cliente: {str(e)}")

    def editar_cliente(self):
        selected = self.table_widget.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente para editar")
            return
        row = selected[0].row()
        id_documento = self.table_widget.item(row, 0).text()
        cliente = self.get_cliente_by_id(id_documento)
        if not cliente:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información del cliente")
            return
        from dialogs.cliente_dialog import ClienteDialog
        dialog = ClienteDialog(self, cliente)
        if dialog.exec():
            nuevos_datos = dialog.get_cliente_data()
            try:
                self.clientes_collection.update_one(
                    {'id_documento': id_documento},
                    {'$set': nuevos_datos}
                )
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                self.load_clientes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar cliente: {str(e)}")

    def eliminar_cliente(self):
        selected = self.table_widget.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cliente para eliminar")
            return
        row = selected[0].row()
        id_documento = self.table_widget.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            'Confirmar Eliminación',
            f'¿Eliminar cliente con ID: {id_documento}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.clientes_collection.delete_one({'id_documento': id_documento})
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                self.load_clientes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar cliente: {str(e)}")

    def get_cliente_by_id(self, id_documento):
        try:
            return self.clientes_collection.find_one(
                {'id_documento': id_documento},
                {'_id': 0}
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al buscar cliente: {str(e)}')
            return None
