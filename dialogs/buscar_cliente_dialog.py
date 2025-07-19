from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt
from db.mongo_connection import get_db_connection

class BuscarClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscar Cliente")
        self.setMinimumWidth(800)
        self.db = get_db_connection()
        self.ventas_collection = self.db['ventas']
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Sección de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingrese el ID del cliente...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_cliente)
        
        search_layout.addWidget(QLabel("ID del Cliente:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_buscar)
        
        # Tabla de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Tipo', 'Nombre', 'Segundo Nombre', 'Apellido', 
            'Segundo Apellido', 'Email', 'Teléfono', 'Segundo Teléfono', 
            'Sexo', 'Total Ventas'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #FF6B00;
                color: white;
            }
        """)
        
        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        
        # Agregar widgets al layout
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        layout.addWidget(button_box)
        
    def buscar_cliente(self):
        """Busca un cliente por ID y muestra su información"""
        id_cliente = self.search_input.text().strip()
        if not id_cliente:
            QMessageBox.warning(self, "Advertencia", "Por favor ingrese un ID de cliente")
            return
            
        try:
            # Buscar el cliente
            cliente = self.db['clientes'].find_one(
                {'id_documento': id_cliente},
                {'_id': 0}
            )
            
            if not cliente:
                QMessageBox.information(self, "Búsqueda", "No se encontró ningún cliente con ese ID")
                self.table.setRowCount(0)
                return
                
            # Contar ventas del cliente
            total_ventas = self.ventas_collection.count_documents(
                {'cliente.id_documento': id_cliente}
            )
            
            # Mostrar resultados en la tabla
            self.table.setRowCount(1)
            
            # Mapear los datos del cliente a las columnas
            columnas = [
                'id_documento', 'tipo_persona', 'nombre', 'segundo_nombre', 
                'apellido', 'segundo_apellido', 'email', 'telefono', 
                'segundo_telefono', 'sexo'
            ]
            
            for col, key in enumerate(columnas):
                self.table.setItem(0, col, QTableWidgetItem(str(cliente.get(key, ''))))
                
            # Agregar el total de ventas
            self.table.setItem(0, 10, QTableWidgetItem(str(total_ventas)))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar el cliente: {str(e)}")
            self.table.setRowCount(0)
