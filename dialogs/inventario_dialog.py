from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDialogButtonBox, QMessageBox, QLabel, QGroupBox
)
from PySide6.QtCore import Qt

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

        self.spn_precio = QDoubleSpinBox()
        self.spn_precio.setRange(0, 999999.99)
        self.spn_precio.setPrefix("$ ")
        self.spn_precio.setDecimals(2)

        self.spn_cantidad = QSpinBox()
        self.spn_cantidad.setRange(0, 999999)

        self.spn_stock_minimo = QSpinBox()
        self.spn_stock_minimo.setRange(0, 999999)

        # Agregar al formulario
        form.addRow("Código de Barras *", self.txt_codigo)
        form.addRow("Nombre *", self.txt_nombre)
        form.addRow("Descripción", self.txt_descripcion)
        form.addRow("Categoría *", self.cmb_categoria)
        form.addRow("Precio Unitario *", self.spn_precio)
        form.addRow("Cantidad en Stock *", self.spn_cantidad)
        form.addRow("Stock Mínimo", self.spn_stock_minimo)

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
            QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox, QSpinBox {
                padding: 8px;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background-color: #FAFAFA;
                color: #000;
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
                color: #fff;
            }
            QPushButton:hover {
                background-color: #E05E00;
                color: #fff;
            }
        """)

    def cargar_datos_item(self):
        self.txt_codigo.setText(self.item_data.get('codigo_barras', ''))
        self.txt_nombre.setText(self.item_data.get('nombre', ''))
        self.txt_descripcion.setPlainText(self.item_data.get('descripcion', ''))

        categoria_index = self.cmb_categoria.findText(self.item_data.get('categoria', ''))
        if categoria_index >= 0:
            self.cmb_categoria.setCurrentIndex(categoria_index)

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
        return {
            'codigo_barras': self.txt_codigo.text().strip(),
            'nombre': self.txt_nombre.text().strip(),
            'descripcion': self.txt_descripcion.toPlainText().strip(),
            'categoria': self.cmb_categoria.currentText(),
            'precio': self.spn_precio.value(),
            'cantidad': self.spn_cantidad.value(),
            'stock_minimo': self.spn_stock_minimo.value()
        }
