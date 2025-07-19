from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QMessageBox, QPushButton, 
    QHBoxLayout, QVBoxLayout, QHeaderView, QLineEdit, QLabel, QWidget
)
from PySide6.QtCore import Qt
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

        # Tabla
        self.table_widget = QTableWidget()
        self.setup_clientes_table()

        # Añadir a layout
        layout.addLayout(search_layout)
        layout.addWidget(self.table_widget)
        self.load_clientes()

    def setup_clientes_table(self):
        headers = [
            'ID Documento', 'Tipo', 'Nombre', 'Segundo Nombre', 'Apellido',
            'Segundo Apellido', 'Email', 'Teléfono', 'Segundo Teléfono', 'Sexo'
        ]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
            for row, cliente in enumerate(clientes):
                for col, key in enumerate([
                    'id_documento', 'tipo_persona', 'nombre', 'segundo_nombre', 'apellido',
                    'segundo_apellido', 'email', 'telefono', 'segundo_telefono', 'sexo'
                ]):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(cliente.get(key, ''))))
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
