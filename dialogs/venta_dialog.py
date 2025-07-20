from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QDateEdit,
                             QFrame, QSizePolicy)
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
            stock_disponible = int(producto_data.get('stock_disponible', 0))
            cantidad = int(producto_data.get('cantidad', 1))
            
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
            nombre_widget = QLabel(nombre)
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
            
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos del formulario como un diccionario"""
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
                    
                    # Verificar stock actual
                    producto = db.productos.find_one({"_id": producto_id}, session=session)
                    if not producto:
                        QMessageBox.warning(self, "Error", f"Producto no encontrado en la base de datos")
                        session.abort_transaction()
                        return None
                        
                    stock_actual = int(producto.get('stock', 0))
                    if cantidad > stock_actual:
                        QMessageBox.warning(
                            self, 
                            "Stock insuficiente",
                            f"No hay suficiente stock para {producto.get('nombre', 'el producto')}. "
                            f"Stock actual: {stock_actual}"
                        )
                        session.abort_transaction()
                        return None
                    
                    # Agregar a la lista de productos
                    productos.append({
                        'id_producto': producto_id,
                        'nombre': producto.get('nombre', 'Producto desconocido'),
                        'cantidad': cantidad,
                        'precio_unitario': precio,
                        'subtotal': cantidad * precio
                    })
                
                # Si llegamos aquí, hay suficiente stock para todos los productos
                # Actualizar el stock de cada producto
                for producto in productos:
                    result = db.productos.update_one(
                        {"_id": producto['id_producto']},
                        {"$inc": {"stock": -producto['cantidad']}},
                        session=session
                    )
                    
                    if result.modified_count == 0:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"No se pudo actualizar el stock del producto {producto['nombre']}"
                        )
                        session.abort_transaction()
                        return None
                
                # Calcular total
                total = sum(p['subtotal'] for p in productos)
                
                # Crear registro de venta
                venta_data = {
                    'id_cliente': cliente_data['id_documento'],
                    'nombre_cliente': f"{cliente_data['nombre']} {cliente_data['apellido']}",
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
                    'cliente': f"{cliente_data['nombre']} {cliente_data['apellido']}",
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
        """Carga la lista de productos disponibles"""
        try:
            db = get_db_connection()
            
            # Primero, verificar la estructura de un producto para depuración
            sample_product = db.productos.find_one()
            if sample_product:
                print("Estructura del producto:", list(sample_product.keys()))
            
            # Obtener todos los productos activos
            productos = list(db.productos.find({"estado": {"$ne": "inactivo"}}))
            
            print(f"Total de productos encontrados: {len(productos)}")
            
            self.producto_combo.clear()
            
            if not productos:
                QMessageBox.information(self, "Sin productos", "No se encontraron productos en la base de datos.")
                self.reject()
                return
                
            # Ordenar productos por nombre
            productos_ordenados = sorted(productos, key=lambda x: str(x.get('nombre', '')).lower())
            
            for producto in productos_ordenados:
                try:
                    # Manejar diferentes estructuras de producto
                    stock = float(producto.get('stock', 0) or 0)
                    precio = float(producto.get('precio', 0) or producto.get('precio_venta', 0) or 0)
                    codigo = str(producto.get('codigo', producto.get('codigo_barras', 'SIN-COD')))
                    nombre = str(producto.get('nombre', 'Sin nombre')).strip()
                    
                    # Validar que el producto tenga los datos mínimos requeridos
                    if not nombre or nombre == 'Sin nombre':
                        print(f"Producto sin nombre válido: {producto}")
                        continue
                        
                    # Formatear el texto para mostrar en el combo
                    stock_text = f"Stock: {int(stock) if stock.is_integer() else stock}" if stock >= 0 else "Sin stock"
                    texto = f"{codigo} - {nombre} | Precio: ${precio:.2f} | {stock_text}"
                    
                    # Almacenar los datos del producto
                    producto_data = {
                        'id': str(producto.get('_id')),
                        'nombre': nombre,
                        'precio': precio,
                        'stock': stock,
                        'codigo': codigo
                    }
                    
                    # Agregar al combo
                    self.producto_combo.addItem(texto, producto_data)
                    
                    # Deshabilitar el ítem si no hay stock
                    index = self.producto_combo.count() - 1
                    model = self.producto_combo.model()
                    if stock <= 0:
                        model.setData(model.index(index, 0), self.palette().color(self.backgroundRole()), Qt.BackgroundRole)
                        model.setData(model.index(index, 0), self.palette().color(self.foregroundRole()).lighter(150), Qt.ForegroundRole)
                        
                except Exception as e:
                    print(f"Error al procesar producto {producto.get('_id')}: {str(e)}")
                    continue
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error al cargar productos: {error_details}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al cargar productos:\n{str(e)}\n\n"
                "Por favor verifique la conexión a la base de datos y la estructura de los productos."
            )
            self.reject()
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        if self.producto_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validación", "Debe seleccionar un producto")
            return
            
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos del formulario"""
        producto = self.producto_combo.currentData()
        if not producto:
            QMessageBox.warning(self, "Error", "No se ha seleccionado un producto válido")
            return None
            
        cantidad = self.cantidad_spin.value()
        stock_disponible = float(producto.get('stock', 0))
        
        # Validar stock solo si es un producto con stock controlado
        if stock_disponible >= 0 and cantidad > stock_disponible:
            QMessageBox.warning(
                self,
                "Stock insuficiente",
                f"No hay suficiente stock disponible. Stock actual: {stock_disponible}"
            )
            return None
            
        return {
            'id_producto': producto.get('id'),
            'nombre': producto.get('nombre'),
            'precio': float(producto.get('precio', 0)),
            'cantidad': cantidad,
            'stock_disponible': stock_disponible
        }
