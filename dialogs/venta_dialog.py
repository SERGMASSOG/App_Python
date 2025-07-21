from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QDateEdit,
                             QFrame, QSizePolicy, QGroupBox, QDateTimeEdit)
from PySide6.QtCore import Qt, QDate, Signal, QDateTime
from PySide6.QtGui import QFont, QPixmap, QIcon
from datetime import datetime
import sys
import os

# Agregar el directorio de utilidades al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.accounting_utils import AccountingUtils
from db.mongo_connection import get_db_connection

# Estilos globales
STYLE_SHEET = """
    QDialog {
        background-color: #f5f7fa;
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #000000;  /* Texto negro */
    }
    QLabel {
        color: #000000;  /* Texto negro */
        font-size: 13px;
    }
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 8px;
        min-height: 30px;
        font-size: 13px;
        color: #000000;  /* Texto negro */
    }
    QPushButton {
        background-color: #FF8C00;  /* Naranja */
        color: #000000;  /* Texto negro */
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #FFA500;  /* Naranja más claro al pasar el mouse */
    }
    QPushButton:disabled {
        background-color: #CCCCCC;  /* Gris para botones deshabilitados */
        color: #666666;
    }
    QTableWidget {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        gridline-color: #e5e7eb;
        color: #000000;  /* Texto negro */
    }
    QTableWidget::item {
        padding: 8px;
        color: #000000;  /* Texto negro */
    }
    QHeaderView::section {
        background-color: #f3f4f6;
        padding: 8px;
        border: none;
        font-weight: 600;
        color: #000000;  /* Texto negro */
    }
    QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 20px;
        border-left: 1px solid #d1d5db;
    }
    QComboBox QAbstractItemView {
        color: #000000;  /* Texto negro en los items del combo */
        background-color: white;  /* Fondo blanco para los items */
    }
"""

class VentaDialog(QDialog):
    def __init__(self, parent=None, venta_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta" if not venta_data else "Editar Venta")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.venta_data = venta_data or {}
        self.db = get_db_connection()
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario de la venta
        form_layout = QFormLayout()
        
        # Sección de información del cliente
        cliente_group = QGroupBox("Datos del Cliente")
        cliente_layout = QFormLayout()
        
        # Selección de cliente
        self.cliente_combo = QComboBox()
        self.cliente_combo.setEditable(True)
        self.cliente_combo.setInsertPolicy(QComboBox.NoInsert)
        self.cargar_clientes()
        cliente_layout.addRow("Cliente*:", self.cliente_combo)
        
        # Botón para agregar nuevo cliente
        btn_nuevo_cliente = QPushButton("Nuevo Cliente")
        btn_nuevo_cliente.clicked.connect(self.agregar_nuevo_cliente)
        cliente_layout.addRow("", btn_nuevo_cliente)
        
        cliente_group.setLayout(cliente_layout)
        
        # Sección de información de la venta
        venta_group = QGroupBox("Información de la Venta")
        venta_layout = QFormLayout()
        
        # Fecha de la venta
        self.fecha_edit = QDateTimeEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDateTime(QDateTime.currentDateTime())
        venta_layout.addRow("Fecha y Hora*:", self.fecha_edit)
        
        # Método de pago
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(["Efectivo", "Tarjeta Crédito", "Tarjeta Débito", "Transferencia"])
        venta_layout.addRow("Método de pago*:", self.metodo_pago_combo)
        
        # Aplicar IVA
        self.aplicar_iva = QCheckBox("Aplicar IVA (19%)")
        self.aplicar_iva.setChecked(True)
        venta_layout.addRow("Impuestos:", self.aplicar_iva)
        
        # Descuento
        self.descuento_spin = QDoubleSpinBox()
        self.descuento_spin.setRange(0, 100)
        self.descuento_spin.setSuffix("%")
        self.descuento_spin.setValue(0)
        venta_layout.addRow("Descuento:", self.descuento_spin)
        
        venta_group.setLayout(venta_layout)
        
        # Agregar grupos al layout principal
        layout.addWidget(cliente_group)
        layout.addWidget(venta_group)
        
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
        
        # Sección de totales
        totales_group = QGroupBox("Totales")
        totales_layout = QFormLayout()
        
        # Subtotal
        self.subtotal_label = QLabel("$0.00")
        totales_layout.addRow("Subtotal:", self.subtotal_label)
        
        # IVA
        self.iva_label = QLabel("$0.00")
        totales_layout.addRow("IVA (19%):", self.iva_label)
        
        # Descuento
        self.descuento_label = QLabel("$0.00 (0%)")
        totales_layout.addRow("Descuento:", self.descuento_label)
        
        # Total
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #FF6B00;")
        totales_layout.addRow("<b>Total a Pagar:</b>", self.total_label)
        
        totales_group.setLayout(totales_layout)
        
        # Conectar señales para actualización en tiempo real
        self.descuento_spin.valueChanged.connect(self.actualizar_totales)
        self.aplicar_iva.stateChanged.connect(self.actualizar_totales)
        
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
            clientes = self.db.clientes.find({}, {'_id': 0, 'id_documento': 1, 'nombre': 1, 'apellido': 1, 'correo': 1, 'telefono': 1})
            self.cliente_combo.clear()
            
            # Agregar opción por defecto
            self.cliente_combo.addItem("Seleccione un cliente...", None)
            
            for cliente in clientes:
                nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')} - {cliente.get('id_documento', '')}"
                self.cliente_combo.addItem(nombre_completo, cliente.get('id_documento'))
                
            # Si hay datos de venta, seleccionar el cliente correspondiente
            if self.venta_data and 'cliente_id' in self.venta_data:
                idx = self.cliente_combo.findData(self.venta_data['cliente_id'])
                if idx >= 0:
                    self.cliente_combo.setCurrentIndex(idx)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")
    
    def agregar_nuevo_cliente(self):
        """Abre el diálogo para agregar un nuevo cliente"""
        from dialogs.cliente_dialog import ClienteDialog
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.cargar_clientes()  # Recargar la lista de clientes
            
    def actualizar_totales(self):
        """Actualiza los totales de la factura"""
        try:
            # Calcular subtotal
            subtotal = 0.0
            for row in range(self.productos_table.rowCount()):
                precio_item = self.productos_table.item(row, 1)
                cantidad_item = self.productos_table.item(row, 2)
                if precio_item and cantidad_item:
                    subtotal += float(precio_item.data(Qt.UserRole)) * int(cantidad_item.text())
            
            # Calcular IVA
            iva = subtotal * 0.19 if self.aplicar_iva.isChecked() else 0
            
            # Calcular descuento
            descuento_porcentaje = self.descuento_spin.value()
            descuento = (subtotal + iva) * (descuento_porcentaje / 100)
            
            # Calcular total
            total = (subtotal + iva) - descuento
            
            # Actualizar etiquetas
            self.subtotal_label.setText(f"${subtotal:,.2f}")
            self.iva_label.setText(f"${iva:,.2f}")
            self.descuento_label.setText(f"${descuento:,.2f} ({descuento_porcentaje}%)")
            self.total_label.setText(f"${total:,.2f}")
            
        except Exception as e:
            print(f"Error al actualizar totales: {str(e)}")
    
    def obtener_datos_venta(self):
        """Retorna los datos del formulario de venta"""
        cliente_idx = self.cliente_combo.currentIndex()
        cliente_id = self.cliente_combo.itemData(cliente_idx)
        
        if not cliente_id:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un cliente")
            return None
            
        # Obtener información del cliente
        cliente = self.db.clientes.find_one({"id_documento": cliente_id})
        if not cliente:
            QMessageBox.warning(self, "Error", "No se encontró la información del cliente")
            return None
            
        # Obtener productos
        productos = []
        for row in range(self.productos_table.rowCount()):
            producto_id = self.productos_table.item(row, 0).data(Qt.UserRole)
            cantidad = int(self.productos_table.item(row, 2).text())
            precio = float(self.productos_table.item(row, 1).data(Qt.UserRole))
            
            productos.append({
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio_unitario": precio
            })
        
        # Calcular totales
        subtotal = float(self.subtotal_label.text().replace('$', '').replace(',', ''))
        iva = float(self.iva_label.text().replace('$', '').replace(',', ''))
        descuento = float(self.descuento_label.text().split('$')[1].split(' ')[0].replace(',', ''))
        total = float(self.total_label.text().replace('$', '').replace(',', ''))
        
        # Crear objeto de venta
        venta = {
            "cliente_id": cliente_id,
            "cliente_nombre": f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}",
            "fecha": self.fecha_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "metodo_pago": self.metodo_pago_combo.currentText(),
            "productos": productos,
            "subtotal": subtotal,
            "impuestos": iva,
            "descuento": descuento,
            "total": total,
            "estado": "Completada",
            "creado_por": getattr(self.parent(), 'username', 'Sistema'),
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return venta
    
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
        try:
            dialog = SeleccionProductoDialog(self)
            if dialog.exec() == QDialog.Accepted:
                producto_data = dialog.obtener_datos()
                if producto_data:  # Verificar que se obtuvieron datos válidos
                    # Verificar si el producto ya está en la tabla
                    for row in range(self.productos_table.rowCount()):
                        item = self.productos_table.cellWidget(row, 0)
                        if item and item.property('producto_id') == producto_data['id_producto']:
                            # Producto ya existe, actualizar cantidad si hay stock disponible
                            cantidad_spin = self.productos_table.cellWidget(row, 2)
                            stock_disponible = cantidad_spin.property('stock_disponible')
                            cantidad_actual = cantidad_spin.value()
                            nueva_cantidad = cantidad_actual + producto_data['cantidad']
                            
                            if nueva_cantidad <= stock_disponible:
                                cantidad_spin.setValue(nueva_cantidad)
                                self.actualizar_totales_fila()
                                self.actualizar_total()
                            else:
                                QMessageBox.warning(
                                    self,
                                    "Stock insuficiente",
                                    f"No hay suficiente stock para agregar {producto_data['cantidad']} unidades más.\n"
                                    f"Stock disponible: {stock_disponible - cantidad_actual} unidades"
                                )
                            return
                    
                    # Si el producto no está en la tabla, agregarlo
                    self.agregar_fila_producto(producto_data)
                    self.actualizar_total()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al agregar producto: {str(e)}"
            )
            import traceback
            print(traceback.format_exc())
    
    def agregar_fila_producto(self, producto_data):
        """Agrega una fila con los datos del producto a la tabla"""
        try:
            row_position = self.productos_table.rowCount()
            self.productos_table.insertRow(row_position)
            
            # Obtener los datos del producto
            producto_id = producto_data['id_producto']
            nombre = producto_data['nombre']
            precio = float(producto_data['precio'])
            stock_disponible = int(producto_data['stock_disponible'])
            cantidad = int(producto_data.get('cantidad', 1))
            codigo = producto_data.get('codigo', '')

            # Mostrar nombre con código
            nombre_completo = f"{codigo} - {nombre}" if codigo else nombre
            
            # Validar que haya stock disponible
            if stock_disponible <= 0:
                QMessageBox.warning(
                    self,
                    "Sin stock",
                    f"No hay stock disponible para el producto {nombre}"
                )
                self.productos_table.removeRow(row_position)
                return
            
            # Asegurarse de que la cantidad no exceda el stock disponible
            cantidad = min(cantidad, stock_disponible) if stock_disponible > 0 else 1
            
            # Crear widget para el nombre del producto con el ID como propiedad
            nombre_widget = QLabel(nombre_completo)
            nombre_widget.setProperty('producto_id', str(producto_id))
            
            # Configurar el precio
            precio_item = QTableWidgetItem(f"${precio:.2f}")
            
            # SpinBox para la cantidad con validación de stock
            cantidad_spin = QSpinBox()
            cantidad_spin.setMinimum(1)
            cantidad_spin.setMaximum(stock_disponible)  # No permitir más que el stock disponible
            cantidad_spin.setValue(cantidad)
            cantidad_spin.setProperty("precio", precio)
            cantidad_spin.setProperty("stock_disponible", stock_disponible)
            cantidad_spin.setProperty("producto_id", str(producto_id))
            cantidad_spin.setProperty("fila", row_position)
            cantidad_spin.valueChanged.connect(self.validar_cantidad)
            cantidad_spin.valueChanged.connect(self.actualizar_totales_fila)
            
            # Etiqueta para el subtotal
            subtotal_label = QLabel(f"${precio:.2f}")
            subtotal_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Botón para eliminar
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(QIcon(":/icons/trash"))
            btn_eliminar.setToolTip("Eliminar producto")
            btn_eliminar.setProperty("fila", row_position)
            btn_eliminar.clicked.connect(self.eliminar_fila)
            
            # Agregar widgets a la tabla
            self.productos_table.setCellWidget(row_position, 0, nombre_widget)
            self.productos_table.setItem(row_position, 1, precio_item)
            self.productos_table.setCellWidget(row_position, 2, cantidad_spin)
            self.productos_table.setCellWidget(row_position, 3, subtotal_label)
            self.productos_table.setCellWidget(row_position, 4, btn_eliminar)
            
            # Actualizar totales
            self.actualizar_total()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar producto: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def validar_cantidad(self):
        """Valida la cantidad de un producto en la tabla"""
        cantidad_spin = self.sender()
        fila = cantidad_spin.property("fila")
        stock_disponible = cantidad_spin.property("stock_disponible")
        cantidad = cantidad_spin.value()
        
        if cantidad > stock_disponible:
            QMessageBox.warning(
                self, 
                "Stock insuficiente",
                f"No hay suficiente stock para agregar más unidades de {self.productos_table.cellWidget(fila, 0).text()}"
            )
            cantidad_spin.setValue(stock_disponible)
    
    def actualizar_totales_fila(self):
        """Actualiza el subtotal de una fila cuando cambia la cantidad"""
        for row in range(self.productos_table.rowCount()):
            precio = self.productos_table.cellWidget(row, 2).property("precio")
            cantidad = self.productos_table.cellWidget(row, 2).value()
            subtotal = precio * cantidad
            self.productos_table.cellWidget(row, 3).setText(f"${subtotal:.2f}")
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
            subtotal_text = self.productos_table.cellWidget(row, 3).text().replace('$', '').strip()
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
    
    def obtener_datos_venta(self):
        """Retorna los datos de la venta como un diccionario"""
        try:
            # Validar cliente seleccionado
            if self.cliente_combo.currentIndex() < 0:
                QMessageBox.warning(self, "Validación", "Debe seleccionar un cliente")
                return None
                
            # Validar productos
            if self.productos_table.rowCount() == 0:
                QMessageBox.warning(self, "Validación", "Debe agregar al menos un producto")
                return None
            
            # Iniciar transacción en la base de datos
            db = get_db_connection()
            session = db.client.start_session()
            
            with session.start_transaction():
                # Obtener datos del cliente
                cliente_data = self.cliente_combo.currentData()
                
                # Obtener productos y validar stock
                productos = []
                for row in range(self.productos_table.rowCount()):
                    cantidad_spin = self.productos_table.cellWidget(row, 2)
                    producto_id = cantidad_spin.property("producto_id")
                    cantidad = cantidad_spin.value()
                    precio = cantidad_spin.property("precio")
                    
                    # Verificar stock actual - manejar diferentes formatos de ID y campos de stock
                    from bson import ObjectId
                    
                    # Intentar buscar el producto de diferentes maneras
                    query = {
                        "$or": [
                            {"_id": ObjectId(producto_id) if isinstance(producto_id, str) else producto_id},
                            {"codigo": str(producto_id)},
                            {"id": str(producto_id)}
                        ]
                    }
                    
                    print(f"Buscando producto con query: {query}")
                    producto = db.inventario.find_one(query, session=session)
                    
                    if not producto:
                        QMessageBox.warning(
                            self, 
                            "Error", 
                            f"Producto con ID {producto_id} no encontrado en la base de datos. "
                            f"Colecciones disponibles: {db.list_collection_names()}"
                        )
                        session.abort_transaction()
                        return None
                    
                    # Obtener el stock disponible (manejar diferentes nombres de campo)
                    stock_actual = int(
                        producto.get('stock_actual') or 
                        producto.get('stock') or 
                        producto.get('cantidad') or 
                        0
                    )
                    
                    print(f"Producto encontrado: {producto.get('nombre')}, Stock: {stock_actual}")
                    
                    if cantidad > stock_actual:
                        QMessageBox.warning(
                            self, 
                            "Stock insuficiente",
                            f"No hay suficiente stock para {producto.get('nombre', 'el producto')}.\n"
                            f"Stock actual: {stock_actual}\n"
                            f"Solicitado: {cantidad}"
                        )
                        session.abort_transaction()
                        return None
                    
                    # Agregar a la lista de productos
                    productos.append({
                        'id_producto': producto['_id'],  # Usar el _id real del documento
                        'nombre': producto.get('nombre', 'Producto desconocido'),
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'subtotal': cantidad * precio,
                        'codigo': str(producto['_id'])  # Guardar el _id como código
                    })
                
                # Si llegamos aquí, hay suficiente stock para todos los productos
                # Actualizar el stock de cada producto
                for producto in productos:
                    # Buscar el producto nuevamente para asegurarnos de tener los datos actualizados
                    from bson import ObjectId
                    
                    # Intentar convertir el ID a ObjectId si es necesario
                    product_id = producto['id_producto']
                    try:
                        if isinstance(product_id, str):
                            product_id = ObjectId(product_id)
                    except:
                        pass  # No es un ObjectId válido, usar como está
                    
                    # Usar solo _id para buscar el producto
                    prod_query = {
                        "_id": product_id
                    }
                    
                    print(f"Buscando producto para actualizar stock con query: {prod_query}")
                    print(f"Datos completos del producto: {producto}")
                    
                    # Actualizar todos los posibles campos de stock
                    update_fields = {}
                    for field in ['stock', 'stock_actual', 'cantidad']:
                        update_fields[field] = -producto['cantidad']
                    
                    print(f"Actualizando stock para producto {producto.get('nombre')} con campos: {update_fields}")
                    
                    # Intentar actualizar el stock
                    result = db.inventario.update_one(
                        prod_query,
                        {"$inc": update_fields},
                        session=session
                    )
                    
                    if result.matched_count == 0:
                        # Intentar encontrar el producto manualmente para diagnóstico
                        print("\n--- DIAGNÓSTICO DE ERROR DE PRODUCTO ---")
                        print(f"Buscando producto con ID: {producto['id_producto']} (tipo: {type(producto['id_producto'])})")
                        
                        # Buscar por _id
                        found = db.inventario.find_one({"_id": product_id})
                        print(f"Búsqueda por _id: {'Encontrado' if found else 'No encontrado'}")
                        
                        # Buscar por código
                        if 'codigo' in producto:
                            found = db.inventario.find_one({"codigo": str(producto['codigo'])})
                            print(f"Búsqueda por código {producto['codigo']}: {'Encontrado' if found else 'No encontrado'}")
                        
                        # Buscar por nombre
                        if 'nombre' in producto:
                            found = db.inventario.find_one({"nombre": producto['nombre']})
                            print(f"Búsqueda por nombre '{producto['nombre']}': {'Encontrado' if found else 'No encontrado'}")
                        
                        # Listar algunos productos existentes para referencia
                        print("\nPrimeros 5 productos en la colección:")
                        for p in db.inventario.find().limit(5):
                            print(f"- {p.get('nombre', 'Sin nombre')} (ID: {p.get('_id')}, Código: {p.get('codigo')}, Stock: {p.get('stock')})")
                        
                        print("--- FIN DE DIAGNÓSTICO ---\n")
                        
                        error_msg = (
                            "Error al actualizar el inventario.\n\n"
                            f"Producto: {producto.get('nombre', 'Desconocido')}\n"
                            f"ID: {producto.get('id_producto')}\n"
                            f"Código: {producto.get('codigo', 'No especificado')}\n\n"
                            "Verifique la consola para más detalles de diagnóstico."
                        )
                        QMessageBox.critical(self, "Error de Inventario", error_msg)
                        session.abort_transaction()
                        return None
                        
                    if result.modified_count == 0:
                        print(f"Advertencia: No se modificó ningún documento para el producto {producto.get('nombre')}")
                        # No abortamos la transacción por esto, solo mostramos advertencia
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            f"No se pudo actualizar el stock del producto {producto.get('nombre', 'desconocido')}. "
                            "El stock podría no haberse actualizado correctamente."
                        )
                
                # Calcular total
                total = sum(p['subtotal'] for p in productos)
                
                # Obtener el ID del cliente seleccionado
                cliente_id = self.cliente_combo.currentData()
                
                # Obtener los datos completos del cliente desde la base de datos
                cliente = self.db.clientes.find_one({"id_documento": cliente_id})
                
                if not cliente:
                    QMessageBox.warning(self, "Error", "No se encontró el cliente seleccionado")
                    return None
                
                # Crear registro de venta
                venta_data = {
                    'id_cliente': cliente.get('id_documento', ''),
                    'nombre_cliente': f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip(),
                    'fecha': self.fecha_edit.date().toString("yyyy-MM-dd"),
                    'metodo_pago': self.metodo_pago_combo.currentText(),
                    'productos': productos,
                    'total': total,
                    'estado': 'completada',
                    'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'usuario': getattr(self, 'current_user', 'Sistema')
                }
                
                # Insertar la venta
                result = db.ventas.insert_one(venta_data, session=session)
                
                if not result.inserted_id:
                    QMessageBox.warning(self, "Error", "No se pudo registrar la venta")
                    session.abort_transaction()
                    return None
                
                # Registrar la transacción contable
                if not AccountingUtils.record_sale_transaction({
                    'total': total,
                    'id_venta': str(result.inserted_id),
                    'cliente': venta_data['nombre_cliente'],
                    'productos': productos,
                    'usuario': getattr(self, 'current_user', 'Sistema')
                }):
                    QMessageBox.warning(
                        self, 
                        "Advertencia", 
                        "La venta se registró pero hubo un error al registrar la transacción contable. "
                        "Por favor, verifique el registro manualmente."
                    )
                
                # Confirmar la transacción
                session.commit_transaction()
                return venta_data
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al procesar la venta: {str(e)}"
            )
            import traceback
            print(traceback.format_exc())
            
            try:
                if session.in_transaction:
                    session.abort_transaction()
            except:
                pass
                
            return None


class SeleccionProductoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Producto")
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Frame para el formulario
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e5e7eb;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        
        # Título
        title = QLabel("Seleccionar Producto")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        
        # Combo de productos
        self.producto_combo = QComboBox()
        self.producto_combo.setMinimumHeight(36)
        
        # Cantidad
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setMinimum(1)
        self.cantidad_spin.setMaximum(9999)
        self.cantidad_spin.setValue(1)
        self.cantidad_spin.setMinimumHeight(36)
        
        # Estilos específicos para los campos
        self.producto_combo.setStyleSheet("""
            QComboBox {
                padding-right: 15px;
                color: #000000;  /* Texto negro */
                background-color: white;  /* Fondo blanco */
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                color: #000000;  /* Texto negro en los items */
                background-color: white;  /* Fondo blanco para los items */
                selection-background-color: #FFA500;  /* Naranja para la selección */
                selection-color: #000000;  /* Texto negro para la selección */
            }
        """)
        
        # Agregar campos al formulario
        form_layout.addRow("<b>Producto</b>:", self.producto_combo)
        form_layout.addRow("<b>Cantidad</b>:", self.cantidad_spin)
        
        # Botones
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setIcon(QIcon(":/icons/check"))
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setIcon(QIcon(":/icons/close"))
        
        btn_aceptar.clicked.connect(self.validar_formulario)
        btn_cancelar.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(btn_aceptar)
        btn_box.addWidget(btn_cancelar)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(title, alignment=Qt.AlignLeft)
        main_layout.addWidget(form_frame)
        main_layout.addLayout(btn_box)
        
        # Cargar productos después de configurar la UI
        self.cargar_productos()
    
    def cargar_productos(self):
        """Carga la lista de productos disponibles del inventario"""
        try:
            db = get_db_connection()
            
            # Primero, verificar la conexión y la colección
            print("Colecciones disponibles:", db.list_collection_names())
            
            # Buscar productos con stock disponible y estado 'Disponible'
            query = {
                "$and": [
                    {
                        "$or": [
                            {"stock": {"$gt": 0}},
                            {"stock_actual": {"$gt": 0}},
                            {"cantidad": {"$gt": 0}}
                        ]
                    },
                    {
                        "estado": "Disponible"
                    }
                ]
            }
            
            print("Ejecutando consulta:", query)
            productos = list(db.inventario.find(query).limit(100))  # Limitar a 100 para depuración
            print(f"Se encontraron {len(productos)} productos")
            
            self.producto_combo.clear()
            
            if not productos:
                QMessageBox.information(
                    self, 
                    "Sin productos", 
                    "No se encontraron productos disponibles en el inventario."
                )
                return
                
            # Ordenar productos por nombre
            productos_ordenados = sorted(
                productos, 
                key=lambda x: x.get('nombre', '').lower()
            )
            
            # Agregar productos al combo
            for producto in productos_ordenados:
                try:
                    # Obtener datos del producto con valores por defecto
                    stock = int(producto.get('stock') or producto.get('stock_actual') or producto.get('cantidad') or 0)
                    precio = float(producto.get('precio') or producto.get('precio_venta') or 0)
                    nombre = str(producto.get('nombre') or producto.get('descripcion') or 'Producto sin nombre').strip()
                    producto_id = str(producto.get('_id', ''))
                    codigo = producto.get('codigo', producto_id[:8])  # Usar parte del ID si no hay código
                    
                    # Formatear el texto para mostrar
                    display_text = f"{nombre} - ${precio:,.2f} (Stock: {stock})"
                    if codigo and codigo != producto_id[:8]:  # Mostrar código solo si es diferente del ID
                        display_text = f"{codigo} - {display_text}"
                    self.producto_combo.addItem(display_text, {
                        'id': producto_id,
                        'nombre': nombre,
                        'precio': precio,
                        'stock': stock,
                        'codigo': codigo
                    })
                    
                except Exception as e:
                    print(f"Error procesando producto {producto.get('_id', '')}: {str(e)}")
                    continue
                    
            if self.producto_combo.count() == 0:
                QMessageBox.information(
                    self,
                    "Sin stock",
                    "No hay productos con stock disponible en el inventario."
                )
                self.reject()
                
        except Exception as e:
            import traceback
            error_msg = (
                f"Error al cargar productos:\n{str(e)}\n\n"
                "Por favor verifique la conexión a la base de datos."
            )
            print(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Error",
                error_msg
            )
            self.reject()

    def obtener_datos(self):
        """Retorna los datos del formulario"""
        try:
            index = self.producto_combo.currentIndex()
            if index < 0:
                QMessageBox.warning(self, "Error", "No se ha seleccionado un producto")
                return None
                
            producto_data = self.producto_combo.itemData(index)
            if not producto_data:
                QMessageBox.warning(self, "Error", "No se pudo obtener los datos del producto")
                return None
                
            cantidad = self.cantidad_spin.value()
            
            # Validar stock (manejar diferentes nombres de campo)
            stock_disponible = producto_data.get('stock') or producto_data.get('stock_actual') or producto_data.get('cantidad', 0)
            if cantidad > stock_disponible:
                QMessageBox.warning(
                    self,
                    "Stock insuficiente",
                    f"No hay suficiente stock disponible. Stock actual: {stock_disponible}"
                )
                return None
                
            return {
                'id_producto': producto_data['id'],
                'nombre': producto_data['nombre'],
                'precio': producto_data['precio'],
                'cantidad': cantidad,
                'stock_disponible': producto_data['stock'],
                'codigo': producto_data['codigo']
            }
                
        except Exception as e:
            print(f"Error en obtener_datos: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al obtener los datos del producto: {str(e)}"
            )
            return None

    def validar_formulario(self):
        """Valida los datos del formulario"""
        if self.producto_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un producto")
            return
            
        self.accept()
    
