from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QDateEdit)
from PySide6.QtCore import Qt, QDate
from db.mongo_connection import get_db_connection

class VentaDialog(QDialog):
    def __init__(self, parent=None, venta_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta" if not venta_data else "Editar Venta")
        self.setMinimumWidth(700)
        self.venta_data = venta_data or {}
        self.db = get_db_connection()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario de la venta
        form_layout = QFormLayout()
        
        # Selección de cliente
        self.cliente_combo = QComboBox()
        self.cargar_clientes()
        form_layout.addRow("Cliente*:", self.cliente_combo)
        
        # Fecha de la venta
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QDate.currentDate())
        form_layout.addRow("Fecha:", self.fecha_edit)
        
        # Método de pago
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(["Efectivo", "Tarjeta Crédito", "Tarjeta Débito", "Transferencia"])
        form_layout.addRow("Método de pago*:", self.metodo_pago_combo)
        
        # Tabla de productos
        self.productos_label = QLabel("Productos:")
        self.productos_table = QTableWidget()
        self.productos_table.setColumnCount(5)
        self.productos_table.setHorizontalHeaderLabels(["Producto", "Precio", "Cantidad", "Subtotal", ""])
        header = self.productos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Botones para productos
        btn_agregar = QPushButton("Agregar Producto")
        btn_agregar.clicked.connect(self.agregar_producto)
        
        # Total
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Botones del diálogo
        btn_box = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar.clicked.connect(self.validar_formulario)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(btn_guardar)
        btn_box.addWidget(btn_cancelar)
        
        # Agregar widgets al layout
        layout.addLayout(form_layout)
        layout.addWidget(self.productos_label)
        layout.addWidget(self.productos_table)
        layout.addWidget(btn_agregar)
        layout.addWidget(self.total_label, alignment=Qt.AlignRight)
        layout.addLayout(btn_box)
        
        # Si estamos editando, cargar los datos
        if self.venta_data:
            self.cargar_datos_venta()
    
    def cargar_clientes(self):
        """Carga la lista de clientes en el combo box"""
        try:
            clientes = self.db.clientes.find({}, {'_id': 0, 'id_documento': 1, 'nombre': 1, 'apellido': 1})
            self.cliente_combo.clear()
            for cliente in clientes:
                nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')} ({cliente.get('id_documento', '')})"
                self.cliente_combo.addItem(nombre_completo, cliente.get('id_documento'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")
    
    def cargar_datos_venta(self):
        """Carga los datos de la venta en el formulario"""
        try:
            # Configurar cliente
            cliente_idx = self.cliente_combo.findData(self.venta_data.get('cliente_id'))
            if cliente_idx >= 0:
                self.cliente_combo.setCurrentIndex(cliente_idx)
            
            # Configurar fecha
            if 'fecha' in self.venta_data:
                self.fecha_edit.setDate(QDate.fromString(self.venta_data['fecha'], 'yyyy-MM-dd'))
            
            # Configurar método de pago
            metodo_pago = self.venta_data.get('metodo_pago', 'Efectivo')
            idx = self.metodo_pago_combo.findText(metodo_pago)
            if idx >= 0:
                self.metodo_pago_combo.setCurrentIndex(idx)
            
            # Cargar productos
            for producto in self.venta_data.get('productos', []):
                self.agregar_fila_producto(producto)
            
            self.actualizar_total()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos de la venta: {str(e)}")
    
    def agregar_producto(self):
        """Abre un diálogo para seleccionar un producto y cantidad"""
        dialog = SeleccionProductoDialog(self)
        if dialog.exec() == QDialog.Accepted:
            producto_data = dialog.obtener_datos()
            if producto_data:
                self.agregar_fila_producto(producto_data)
                self.actualizar_total()
    
    def agregar_fila_producto(self, producto_data):
        """Agrega una fila con los datos del producto a la tabla"""
        row = self.productos_table.rowCount()
        self.productos_table.insertRow(row)
        
        # Producto
        nombre_item = QTableWidgetItem(producto_data.get('nombre', ''))
        nombre_item.setData(Qt.UserRole, producto_data.get('id_producto'))
        
        # Precio
        precio = float(producto_data.get('precio', 0))
        precio_item = QTableWidgetItem(f"${precio:.2f}")
        precio_item.setData(Qt.UserRole, precio)
        
        # Cantidad
        cantidad = int(producto_data.get('cantidad', 1))
        spin_cantidad = QSpinBox()
        spin_cantidad.setMinimum(1)
        spin_cantidad.setMaximum(9999)
        spin_cantidad.setValue(cantidad)
        spin_cantidad.valueChanged.connect(self.actualizar_totales_fila)
        
        # Subtotal
        subtotal = precio * cantidad
        subtotal_item = QTableWidgetItem(f"${subtotal:.2f}")
        
        # Botón eliminar
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_fila)
        
        # Agregar widgets a la tabla
        self.productos_table.setItem(row, 0, nombre_item)
        self.productos_table.setItem(row, 1, precio_item)
        self.productos_table.setCellWidget(row, 2, spin_cantidad)
        self.productos_table.setItem(row, 3, subtotal_item)
        self.productos_table.setCellWidget(row, 4, btn_eliminar)
    
    def actualizar_totales_fila(self, _=None):
        """Actualiza el subtotal de una fila cuando cambia la cantidad"""
        for row in range(self.productos_table.rowCount()):
            precio = self.productos_table.item(row, 1).data(Qt.UserRole)
            cantidad = self.productos_table.cellWidget(row, 2).value()
            subtotal = precio * cantidad
            self.productos_table.item(row, 3).setText(f"${subtotal:.2f}")
        self.actualizar_total()
    
    def eliminar_fila(self):
        """Elimina la fila seleccionada de la tabla"""
        button = self.sender()
        if button:
            row = self.productos_table.indexAt(button.pos()).row()
            self.productos_table.removeRow(row)
            self.actualizar_total()
    
    def actualizar_total(self):
        """Calcula y actualiza el total de la venta"""
        total = 0.0
        for row in range(self.productos_table.rowCount()):
            subtotal_text = self.productos_table.item(row, 3).text().replace('$', '').strip()
            try:
                subtotal = float(subtotal_text)
                total += subtotal
            except ValueError:
                pass
        self.total_label.setText(f"Total: ${total:.2f}")
    
    def validar_formulario(self):
        """Valida los datos del formulario antes de guardar"""
        if self.cliente_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un cliente")
            return
            
        if self.productos_table.rowCount() == 0:
            QMessageBox.warning(self, "Validación", "Debe agregar al menos un producto")
            return
            
        if not self.metodo_pago_combo.currentText():
            QMessageBox.warning(self, "Validación", "Debe seleccionar un método de pago")
            return
            
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos del formulario como un diccionario"""
        # Obtener ID del cliente
        cliente_id = self.cliente_combo.currentData()
        
        # Obtener productos
        productos = []
        for row in range(self.productos_table.rowCount()):
            producto_id = self.productos_table.item(row, 0).data(Qt.UserRole)
            nombre = self.productos_table.item(row, 0).text()
            precio = self.productos_table.item(row, 1).data(Qt.UserRole)
            cantidad = self.productos_table.cellWidget(row, 2).value()
            
            productos.append({
                'id_producto': producto_id,
                'nombre': nombre,
                'precio': precio,
                'cantidad': cantidad
            })
        
        # Calcular total
        total = 0.0
        for p in productos:
            total += p['precio'] * p['cantidad']
        
        return {
            'cliente_id': cliente_id,
            'fecha': self.fecha_edit.date().toString('yyyy-MM-dd'),
            'metodo_pago': self.metodo_pago_combo.currentText(),
            'productos': productos,
            'total': total,
            'estado': 'Completada'
        }


class SeleccionProductoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Producto")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Combo de productos
        self.producto_combo = QComboBox()
        self.cargar_productos()
        form_layout.addRow("Producto*:", self.producto_combo)
        
        # Cantidad
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(9999)
        self.cantidad_spin.setValue(1)
        form_layout.addRow("Cantidad*:", self.cantidad_spin)
        
        # Botones
        btn_box = QHBoxLayout()
        btn_aceptar = QPushButton("Aceptar")
        btn_cancelar = QPushButton("Cancelar")
        btn_aceptar.clicked.connect(self.validar_formulario)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(btn_aceptar)
        btn_box.addWidget(btn_cancelar)
        
        # Agregar widgets al layout
        layout.addLayout(form_layout)
        layout.addLayout(btn_box)
    
    def cargar_productos(self):
        """Carga la lista de productos disponibles"""
        try:
            db = get_db_connection()
            productos = db.inventario.find({'stock': {'$gt': 0}}, {'_id': 0, 'id': 1, 'nombre': 1, 'precio': 1, 'stock': 1})
            
            self.producto_combo.clear()
            for producto in productos:
                texto = f"{producto.get('nombre', '')} - ${producto.get('precio', 0):.2f} (Stock: {producto.get('stock', 0)})"
                self.producto_combo.addItem(texto, producto)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos: {str(e)}")
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        if self.producto_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un producto")
            return
            
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos del formulario"""
        producto = self.producto_combo.currentData()
        return {
            'id_producto': producto.get('id'),
            'nombre': producto.get('nombre'),
            'precio': float(producto.get('precio', 0)),
            'cantidad': self.cantidad_spin.value()
        }
