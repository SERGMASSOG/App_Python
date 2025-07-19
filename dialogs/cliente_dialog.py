from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QComboBox)
from PySide6.QtCore import Qt
import re

class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_data=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Cliente" if not cliente_data else "Editar Cliente")
        self.setMinimumWidth(500)
        self.cliente_data = cliente_data or {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulario
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setSpacing(15)
        
        # Campos del formulario
        self.txt_identificacion = QLineEdit()
        self.cmb_tipo_persona = QComboBox()
        self.cmb_tipo_persona.addItems(["Natural", "Jurídica"])
        self.txt_nombre = QLineEdit()
        self.txt_segundo_nombre = QLineEdit()
        self.txt_apellido = QLineEdit()
        self.txt_segundo_apellido = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_segundo_telefono = QLineEdit()
        self.cmb_sexo = QComboBox()
        self.cmb_sexo.addItems(["Femenino", "Masculino", "Otro"])
        
        # Agregar campos al formulario
        form.addRow("Identificación*:", self.txt_identificacion)
        form.addRow("Tipo de Persona*:", self.cmb_tipo_persona)
        form.addRow("Nombre*:", self.txt_nombre)
        form.addRow("Segundo Nombre:", self.txt_segundo_nombre)
        form.addRow("Apellido*:", self.txt_apellido)
        form.addRow("Segundo Apellido:", self.txt_segundo_apellido)
        form.addRow("Email:", self.txt_email)
        form.addRow("Teléfono*:", self.txt_telefono)
        form.addRow("Segundo Teléfono:", self.txt_segundo_telefono)
        form.addRow("Sexo*:", self.cmb_sexo)
        
        # Botones del diálogo
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        button_box.accepted.connect(self.validar_formulario)
        button_box.rejected.connect(self.reject)
        
        # Cargar datos si es una edición
        if self.cliente_data:
            self.cargar_datos_cliente()
        
        # Agregar widgets al layout
        layout.addLayout(form)
        layout.addWidget(button_box)
        
        # Aplicar estilos
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                color: #333333;
                font-size: 13px;
            }
            QLabel {
                font-weight: 500;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 250px;
                color: #333333;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QLineEdit:hover, QComboBox:hover {
                border: 1px solid #FF6B00;
            }
            QPushButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #E05E00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
            QComboBox::drop-down {
                border: 0px;
                padding-right: 5px;
            }
        """)
    
    def cargar_datos_cliente(self):
        """Carga los datos del cliente en el formulario"""
        self.txt_identificacion.setText(self.cliente_data.get('id_documento', ''))
        
        tipo_persona = self.cliente_data.get('tipo_persona', 'Natural')
        tipo_index = self.cmb_tipo_persona.findText(tipo_persona)
        if tipo_index >= 0:
            self.cmb_tipo_persona.setCurrentIndex(tipo_index)
            
        self.txt_nombre.setText(self.cliente_data.get('nombre', ''))
        self.txt_segundo_nombre.setText(self.cliente_data.get('segundo_nombre', ''))
        self.txt_apellido.setText(self.cliente_data.get('apellido', ''))
        self.txt_segundo_apellido.setText(self.cliente_data.get('segundo_apellido', ''))
        self.txt_email.setText(self.cliente_data.get('email', ''))
        self.txt_telefono.setText(self.cliente_data.get('telefono', ''))
        self.txt_segundo_telefono.setText(self.cliente_data.get('segundo_telefono', ''))
        
        sexo_index = self.cmb_sexo.findText(self.cliente_data.get('sexo', 'Femenino'))
        if sexo_index >= 0:
            self.cmb_sexo.setCurrentIndex(sexo_index)
    
    def validar_formulario(self):
        """Valida los campos del formulario"""
        # Validar campos requeridos
        campos_requeridos = {
            'Identificación': self.txt_identificacion.text().strip(),
            'Tipo de Persona': self.cmb_tipo_persona.currentText(),
            'Nombre': self.txt_nombre.text().strip(),
            'Apellido': self.txt_apellido.text().strip(),
            'Teléfono': self.txt_telefono.text().strip(),
            'Sexo': self.cmb_sexo.currentText()
        }
        
        faltantes = [campo for campo, valor in campos_requeridos.items() if not valor]
        if faltantes:
            QMessageBox.warning(
                self,
                'Campos requeridos',
                f'Por favor complete los siguientes campos requeridos:\n' + 
                '\n'.join(f'• {campo}' for campo in faltantes)
            )
            return
            
        # Validar formato de email si se proporciona
        email = self.txt_email.text().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            QMessageBox.warning(self, 'Error', 'El formato del correo electrónico no es válido')
            return
            
        # Si todo está bien, aceptar el diálogo
        self.accept()
    
    def get_cliente_data(self):
        """Devuelve los datos del formulario como un diccionario"""
        return {
            'id_documento': self.txt_identificacion.text().strip(),
            'tipo_persona': self.cmb_tipo_persona.currentText(),
            'nombre': self.txt_nombre.text().strip(),
            'segundo_nombre': self.txt_segundo_nombre.text().strip(),
            'apellido': self.txt_apellido.text().strip(),
            'segundo_apellido': self.txt_segundo_apellido.text().strip(),
            'email': self.txt_email.text().strip(),
            'telefono': self.txt_telefono.text().strip(),
            'segundo_telefono': self.txt_segundo_telefono.text().strip(),
            'sexo': self.cmb_sexo.currentText()
        }
