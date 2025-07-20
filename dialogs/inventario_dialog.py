from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDialogButtonBox, QMessageBox, QLabel, QGroupBox
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import QWidget 
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.accounting_utils import AccountingUtils
from db.mongo_connection import get_db_connection

class InventarioDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Producto" if not item_data else "Editar Producto")
        self.setMinimumWidth(550)
        self.item_data = item_data or {}
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Sección: Información del producto
        group_box = QGroupBox("Información del producto")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setSpacing(12)

        self.txt_codigo = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(70)

        self.cmb_categoria = QComboBox()
        self.cmb_categoria.addItems([
            "Camisas", "Pantalones", "Zapatos", "Gafas", 
            "Relojes", "Ropa Deportiva", "Faldas", "Gorros", "Otros"
        ])

        # Sección de precios
        precio_layout = QHBoxLayout()
        
        self.spn_costo = QDoubleSpinBox()
        self.spn_costo.setRange(0, 999999.99)
        self.spn_costo.setPrefix("$ ")
        self.spn_costo.setDecimals(2)
        self.spn_costo.setToolTip("Costo de compra del producto")
        
        self.spn_precio = QDoubleSpinBox()
        self.spn_precio.setRange(0, 999999.99)
        self.spn_precio.setPrefix("$ ")
        self.spn_precio.setDecimals(2)
        self.spn_precio.setToolTip("Precio de venta al público")
        
        precio_layout.addWidget(self.spn_costo)
        precio_layout.addWidget(QLabel("→"))
        precio_layout.addWidget(self.spn_precio)
        precio_layout.addStretch()

        # Sección de inventario
        inventario_layout = QHBoxLayout()
        
        self.spn_cantidad = QSpinBox()
        self.spn_cantidad.setRange(0, 999999)
        self.spn_cantidad.setToolTip("Cantidad actual en inventario")
        
        self.spn_stock_minimo = QSpinBox()
        self.spn_stock_minimo.setRange(0, 999999)
        self.spn_stock_minimo.setToolTip("Stock mínimo antes de reordenar")

        # Agregar al formulario
        form.addRow("Código de Barras *", self.txt_codigo)
        form.addRow("Nombre *", self.txt_nombre)
        form.addRow("Descripción", self.txt_descripcion)
        form.addRow("Categoría *", self.cmb_categoria)
        
        # Agregar fila de precios
        precio_widget = QWidget()
        precio_widget.setLayout(precio_layout)
        form.addRow("Costo → Precio Venta *", precio_widget)
        
        # Agregar fila de inventario
        inventario_widget = QWidget()
        inventario_layout.addWidget(QLabel("Stock Actual:"))
        inventario_layout.addWidget(self.spn_cantidad)
        inventario_layout.addSpacing(20)
        inventario_layout.addWidget(QLabel("Stock Mínimo:"))
        inventario_layout.addWidget(self.spn_stock_minimo)
        inventario_widget.setLayout(inventario_layout)
        form.addRow("Inventario", inventario_widget)

        group_box.setLayout(form)
        main_layout.addWidget(group_box)

        # Botonera
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validar_formulario)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        if self.item_data:
            self.cargar_datos_item()

        # Estilos modernizados con la letra color negro
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 15px;
                color: #000;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
            }
            QLabel {
                min-width: 130px;
                font-weight: 500;
                color: #333333; 
            }
            QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox {
                padding: 8px;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background-color: #FAFAFA;
                color: #000;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background-color: #FFFFFF;
                color: #000000;
                min-width: 150px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #FF6B00;
                selection-color: white;
                border: 1px solid #D0D0D0;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(none);
                width: 12px;
                height: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus, 
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #FF6B00;
                background-color: #FFFDF8;
                color: #000;
            }
            QPushButton {
                background-color: #FF6B00;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #E05E00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)

    def cargar_datos_item(self):
        self.txt_codigo.setText(self.item_data.get('codigo_barras', ''))
        self.txt_nombre.setText(self.item_data.get('nombre', ''))
        self.txt_descripcion.setPlainText(self.item_data.get('descripcion', ''))

        categoria_index = self.cmb_categoria.findText(self.item_data.get('categoria', ''))
        if categoria_index >= 0:
            self.cmb_categoria.setCurrentIndex(categoria_index)

        self.spn_costo.setValue(float(self.item_data.get('costo', 0)))
        self.spn_precio.setValue(float(self.item_data.get('precio', 0)))
        self.spn_cantidad.setValue(int(self.item_data.get('cantidad', 0)))
        self.spn_stock_minimo.setValue(int(self.item_data.get('stock_minimo', 0)))

    def validar_formulario(self):
        campos_requeridos = {
            'Código de Barras': self.txt_codigo.text().strip(),
            'Nombre': self.txt_nombre.text().strip(),
            'Categoría': self.cmb_categoria.currentText().strip(),
            'Precio': self.spn_precio.value(),
            'Cantidad': self.spn_cantidad.value()
        }

        faltantes = [campo for campo, valor in campos_requeridos.items() if not valor and valor != 0]
        if faltantes:
            QMessageBox.warning(
                self, 'Campos requeridos',
                'Por favor complete los siguientes campos:\n' +
                '\n'.join(f"• {campo}" for campo in faltantes)
            )
            return

        self.accept()

    def get_item_data(self):
        # Obtener los datos del formulario
        item_data = {
            'codigo_barras': self.txt_codigo.text().strip(),
            'nombre': self.txt_nombre.text().strip(),
            'descripcion': self.txt_descripcion.toPlainText().strip(),
            'categoria': self.cmb_categoria.currentText(),
            'costo': self.spn_costo.value(),
            'precio': self.spn_precio.value(),
            'cantidad': self.spn_cantidad.value(),
            'stock_minimo': self.spn_stock_minimo.value()
        }
        
        # Si es una edición, registrar la diferencia en inventario
        if self.item_data and 'cantidad' in self.item_data:
            cantidad_anterior = int(self.item_data.get('cantidad', 0))
            cantidad_nueva = item_data['cantidad']
            diferencia = cantidad_nueva - cantidad_anterior
            
            if diferencia > 0:  # Se agregó inventario
                costo_total = diferencia * item_data['costo']
                
                # Registrar la transacción contable
                AccountingUtils.record_inventory_purchase({
                    'total': costo_total,
                    'id_compra': f"INV-{self.item_data.get('_id', '')}",
                    'proveedor': 'Proveedor no especificado',  # Se podría agregar un campo para el proveedor
                    'productos': [{
                        'id_producto': self.item_data.get('_id', ''),
                        'nombre': item_data['nombre'],
                        'cantidad': diferencia,
                        'costo_unitario': item_data['costo'],
                        'total': costo_total
                    }],
                    'usuario': getattr(self, 'current_user', 'Sistema')
                })
        
        return item_data
