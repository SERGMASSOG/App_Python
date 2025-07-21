from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QDateEdit, QLabel, 
    QComboBox, QHeaderView, QFormLayout, QLineEdit, QDialog, 
    QDialogButtonBox, QWidget, QFileDialog, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QDoubleValidator
from db.mongo_connection import get_db_connection
import csv
from datetime import datetime
from fpdf import FPDF
import webbrowser
import os

class ContabilidadManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db = get_db_connection()
        self.transacciones_collection = self.db['transacciones']
        self.cuentas_collection = self.db['cuentas_contables']
        self.setup_ui()
        self.setup_estilos()
        self.cargar_datos_iniciales()

    def setup_estilos(self):
        """Configura los estilos visuales del módulo"""
        self.setStyleSheet("""
            /* Estilos generales */
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                color: #333333;
            }
            
            /* Pestañas */
            QTabWidget::pane {
                border-top: 1px solid #E0E0E0;
                background: #FFFFFF;
            }
            
            QTabBar::tab {
                background: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            
            QTabBar::tab:selected {
                background: #FFFFFF;
                border-bottom: 3px solid #FF6B00;
                font-weight: bold;
                color: #FF6B00;
            }
            
            /* Botones principales */
            QPushButton {
                background-color: #FF6B00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 120px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #E05E00;
            }
            
            QPushButton:pressed {
                background-color: #C35000;
            }
            
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
            
            /* Tablas */
            QTableWidget {
                background-color: white;
                alternate-background-color: #FAFAFA;
                gridline-color: #E0E0E0;
                border: none;
                selection-background-color: #FFE0B2;
                selection-color: #333333;
            }
            
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            
            /* Controles de formulario */
            QDateEdit, QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QDateEdit::drop-down, QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #E0E0E0;
            }
            
            /* Etiquetas */
            QLabel {
                color: #333333;
            }
            
            /* Marcos */
            QFrame {
                background-color: #FFFFFF;
            }
            
            /* Diálogos */
            QDialog {
                background-color: #FFFFFF;
            }
        """)

    def setup_ui(self):
        """Configura la interfaz principal de contabilidad"""
        self.setWindowTitle("Gestión Contable")
        self.setMinimumSize(1000, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # Configurar barra superior con filtros
        self.setup_barra_superior()
        
        # Configurar pestañas principales
        self.setup_tabs_principales()
        
        main_layout.addLayout(self.barra_superior)
        main_layout.addWidget(self.tabs_principales)

    def setup_barra_superior(self):
        """Configura la barra superior con filtros y acciones"""
        self.barra_superior = QHBoxLayout()
        self.barra_superior.setSpacing(12)
        
        # Grupo de filtros por fecha
        fecha_group = QFrame()
        fecha_group.setObjectName("fechaGroup")
        fecha_group.setStyleSheet("""
            QFrame#fechaGroup {
                background: #F5F5F5;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        fecha_layout = QHBoxLayout(fecha_group)
        fecha_layout.setContentsMargins(8, 8, 8, 8)
        
        lbl_filtro = QLabel("Filtrar por fecha:")
        lbl_filtro.setStyleSheet("font-weight: bold;")
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setDisplayFormat("dd/MM/yyyy")
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setDisplayFormat("dd/MM/yyyy")
        
        btn_buscar = QPushButton("🔍 Aplicar Filtros")
        btn_buscar.setToolTip("Buscar transacciones en el rango de fechas")
        btn_buscar.clicked.connect(self.filtrar_transacciones)
        
        fecha_layout.addWidget(lbl_filtro)
        fecha_layout.addWidget(QLabel("Desde:"))
        fecha_layout.addWidget(self.fecha_desde)
        fecha_layout.addWidget(QLabel("Hasta:"))
        fecha_layout.addWidget(self.fecha_hasta)
        fecha_layout.addWidget(btn_buscar)
        fecha_layout.addSpacing(20)
        
        # Grupo de acciones rápidas
        acciones_group = QFrame()
        acciones_layout = QHBoxLayout(acciones_group)
        acciones_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_nueva = QPushButton("➕ Nueva Transacción")
        btn_nueva.setToolTip("Registrar una nueva transacción contable")
        btn_nueva.clicked.connect(self.nueva_transaccion)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setToolTip("Actualizar todos los datos")
        btn_actualizar.clicked.connect(self.actualizar_todo)
        
        acciones_layout.addWidget(btn_nueva)
        acciones_layout.addWidget(btn_actualizar)
        
        # Agregar al layout principal
        self.barra_superior.addWidget(fecha_group)
        self.barra_superior.addStretch()
        self.barra_superior.addWidget(acciones_group)

    def setup_tabs_principales(self):
        """Configura las pestañas principales del módulo"""
        self.tabs_principales = QTabWidget()
        
        # Pestaña de transacciones
        self.tab_transacciones = QWidget()
        self.setup_tab_transacciones()
        
        # Pestaña de resumen contable
        self.tab_resumen = QWidget()
        self.setup_tab_resumen()
        
        # Pestaña de reportes
        self.tab_reportes = QWidget()
        self.setup_tab_reportes()
        
        # Pestaña de configuración
        self.tab_config = QWidget()
        self.setup_tab_config()
        
        self.tabs_principales.addTab(self.tab_transacciones, "📋 Transacciones")
        self.tabs_principales.addTab(self.tab_resumen, "📊 Resumen Contable")
        self.tabs_principales.addTab(self.tab_reportes, "📈 Reportes")
        self.tabs_principales.addTab(self.tab_config, "⚙️ Configuración")

    def setup_tab_transacciones(self):
        """Configura la pestaña de gestión de transacciones"""
        layout = QVBoxLayout(self.tab_transacciones)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        
        # Configurar tabla de transacciones
        self.tabla_transacciones = QTableWidget()
        self.tabla_transacciones.setObjectName("tablaTransacciones")
        self.tabla_transacciones.setColumnCount(8)
        self.tabla_transacciones.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Descripción", "Monto", "Cuenta", "Categoría", "Estado"
        ])
        
        # Configurar comportamiento de la tabla
        self.tabla_transacciones.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_transacciones.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_transacciones.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_transacciones.setAlternatingRowColors(True)
        self.tabla_transacciones.setSortingEnabled(True)
        
        # Configurar anchos de columnas
        header = self.tabla_transacciones.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Descripción ocupa espacio restante
        
        self.tabla_transacciones.setColumnWidth(0, 80)   # ID
        self.tabla_transacciones.setColumnWidth(1, 100)  # Fecha
        self.tabla_transacciones.setColumnWidth(2, 90)   # Tipo
        self.tabla_transacciones.setColumnWidth(4, 120)  # Monto
        self.tabla_transacciones.setColumnWidth(5, 150)  # Cuenta
        self.tabla_transacciones.setColumnWidth(6, 150)  # Categoría
        self.tabla_transacciones.setColumnWidth(7, 100)  # Estado
        
        # Configurar menú contextual
        self.tabla_transacciones.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_transacciones.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        # Barra de herramientas
        tool_bar = QFrame()
        tool_bar.setObjectName("toolBar")
        tool_bar.setStyleSheet("""
            QFrame#toolBar {
                background: #F5F5F5;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        tool_layout = QHBoxLayout(tool_bar)
        tool_layout.setContentsMargins(8, 4, 8, 4)
        
        btn_exportar = QPushButton("📤 Exportar CSV")
        btn_exportar.clicked.connect(self.exportar_transacciones_csv)
        
        btn_imprimir = QPushButton("🖨️ Generar PDF")
        btn_imprimir.clicked.connect(self.generar_pdf_transacciones)
        
        tool_layout.addWidget(btn_exportar)
        tool_layout.addWidget(btn_imprimir)
        tool_layout.addStretch()
        
        # Contador de resultados
        self.lbl_contador = QLabel("0 transacciones encontradas")
        self.lbl_contador.setStyleSheet("font-weight: bold; color: #666666;")
        tool_layout.addWidget(self.lbl_contador)
        
        # Agregar a layout
        layout.addWidget(self.tabla_transacciones)
        layout.addWidget(tool_bar)

    def setup_tab_resumen(self):
        """Configura la pestaña de resumen contable"""
        layout = QVBoxLayout(self.tab_resumen)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        
        # Tarjetas de resumen rápido
        resumen_frame = QFrame()
        resumen_frame.setObjectName("resumenFrame")
        resumen_frame.setStyleSheet("""
            QFrame#resumenFrame {
                background: #F5F5F5;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        resumen_layout = QHBoxLayout(resumen_frame)
        resumen_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tarjeta de Ingresos
        self.card_ingresos = self.crear_tarjeta_resumen("Ingresos", "$0.00", "#4CAF50")
        # Tarjeta de Egresos
        self.card_egresos = self.crear_tarjeta_resumen("Egresos", "$0.00", "#F44336")
        # Tarjeta de Balance
        self.card_balance = self.crear_tarjeta_resumen("Balance", "$0.00", "#2196F3")
        
        resumen_layout.addWidget(self.card_ingresos)
        resumen_layout.addWidget(self.card_egresos)
        resumen_layout.addWidget(self.card_balance)
        resumen_layout.addStretch()
        
        # Tabla de resumen por cuenta
        self.tabla_resumen = QTableWidget()
        self.tabla_resumen.setObjectName("tablaResumen")
        self.tabla_resumen.setColumnCount(5)
        self.tabla_resumen.setHorizontalHeaderLabels([
            "Cuenta", "Ingresos", "Egresos", "Saldo", "Tendencia"
        ])
        
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.setSortingEnabled(True)
        
        # Barra de herramientas
        tool_bar = QFrame()
        tool_layout = QHBoxLayout(tool_bar)
        tool_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_exportar = QPushButton("📤 Exportar Resumen")
        btn_exportar.clicked.connect(self.exportar_resumen_csv)
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self.actualizar_resumen)
        
        tool_layout.addStretch()
        tool_layout.addWidget(btn_actualizar)
        tool_layout.addWidget(btn_exportar)
        
        # Agregar a layout
        layout.addWidget(resumen_frame)
        layout.addWidget(self.tabla_resumen)
        layout.addWidget(tool_bar)

    def setup_tab_reportes(self):
        """Configura la pestaña de reportes financieros"""
        layout = QVBoxLayout(self.tab_reportes)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Título
        lbl_titulo = QLabel("Reportes Financieros")
        lbl_titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2C3E50;
                padding-bottom: 10px;
                border-bottom: 2px solid #FF6B00;
            }
        """)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        # Contenedor de botones
        btn_container = QFrame()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(15)
        
        # Estilo para botones de reportes
        btn_style = """
            QPushButton {
                padding: 20px;
                font-size: 14px;
                font-weight: bold;
                min-height: 80px;
                border-radius: 8px;
                text-align: left;
                padding-left: 50px;
            }
            QPushButton:hover {
                padding-left: 45px;
                border-left: 5px solid #FF6B00;
            }
        """
        
        # Botón de Balance General
        btn_balance = QPushButton("📄 Balance General")
        btn_balance.setStyleSheet(btn_style + "background-color: #9C27B0; color: white;")
        btn_balance.clicked.connect(self.generar_balance)
        
        # Botón de Estado de Resultados
        btn_resultados = QPushButton("📈 Estado de Resultados")
        btn_resultados.setStyleSheet(btn_style + "background-color: #3F51B5; color: white;")
        btn_resultados.clicked.connect(self.generar_estado_resultados)
        
        # Botón de Flujo de Efectivo
        btn_efectivo = QPushButton("💵 Flujo de Efectivo")
        btn_efectivo.setStyleSheet(btn_style + "background-color: #009688; color: white;")
        btn_efectivo.clicked.connect(self.generar_flujo_efectivo)
        
        # Agregar botones al layout
        btn_layout.addWidget(btn_balance)
        btn_layout.addWidget(btn_resultados)
        btn_layout.addWidget(btn_efectivo)
        btn_layout.addStretch()
        
        # Agregar al layout principal
        layout.addWidget(lbl_titulo)
        layout.addWidget(btn_container)
        layout.addStretch()

    def setup_tab_config(self):
        """Configura la pestaña de configuración"""
        layout = QVBoxLayout(self.tab_config)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Grupo de configuración de cuentas
        group_cuentas = QFrame()
        group_cuentas.setObjectName("groupCuentas")
        group_cuentas.setStyleSheet("""
            QFrame#groupCuentas {
                background: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        group_layout = QVBoxLayout(group_cuentas)
        
        lbl_titulo = QLabel("Configuración de Cuentas Contables")
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50;")
        
        # Tabla de cuentas
        self.tabla_cuentas = QTableWidget()
        self.tabla_cuentas.setColumnCount(4)
        self.tabla_cuentas.setHorizontalHeaderLabels(["Código", "Nombre", "Tipo", "Saldo Inicial"])
        self.tabla_cuentas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Botones de gestión de cuentas
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_nueva_cuenta = QPushButton("➕ Nueva Cuenta")
        btn_nueva_cuenta.clicked.connect(self.nueva_cuenta)
        
        btn_editar_cuenta = QPushButton("✏️ Editar")
        btn_editar_cuenta.clicked.connect(self.editar_cuenta)
        
        btn_eliminar_cuenta = QPushButton("🗑️ Eliminar")
        btn_eliminar_cuenta.clicked.connect(self.eliminar_cuenta)
        
        btn_layout.addWidget(btn_nueva_cuenta)
        btn_layout.addWidget(btn_editar_cuenta)
        btn_layout.addWidget(btn_eliminar_cuenta)
        btn_layout.addStretch()
        
        # Agregar al grupo
        group_layout.addWidget(lbl_titulo)
        group_layout.addWidget(self.tabla_cuentas)
        group_layout.addWidget(btn_frame)
        
        # Grupo de configuración del sistema
        group_sistema = QFrame()
        group_sistema.setObjectName("groupSistema")
        group_sistema.setStyleSheet("""
            QFrame#groupSistema {
                background: #F5F5F5;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        system_layout = QFormLayout(group_sistema)
        
        lbl_sistema = QLabel("Configuración del Sistema")
        lbl_sistema.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50;")
        
        self.chk_backup = QCheckBox("Realizar copias de seguridad automáticas")
        self.cmb_frecuencia = QComboBox()
        self.cmb_frecuencia.addItems(["Diaria", "Semanal", "Mensual"])
        
        system_layout.addRow(lbl_sistema)
        system_layout.addRow("Frecuencia de backup:", self.cmb_frecuencia)
        system_layout.addRow(self.chk_backup)
        
        # Agregar al layout principal
        layout.addWidget(group_cuentas)
        layout.addWidget(group_sistema)
        layout.addStretch()

    def crear_tarjeta_resumen(self, titulo, valor, color):
        """Crea una tarjeta de resumen con estilo"""
        frame = QFrame()
        frame.setObjectName("resumenCard")
        frame.setStyleSheet(f"""
            QFrame#resumenCard {{
                background: white;
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 12px;
            }}
            QLabel#titulo {{
                color: #666666;
                font-size: 13px;
                font-weight: bold;
            }}
            QLabel#valor {{
                color: {color};
                font-size: 20px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("titulo")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("valor")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        
        # Guardar referencia al label de valor
        frame.valor_label = lbl_valor
        
        return frame

    # ======================================================================
    # MÉTODOS DE CARGA DE DATOS
    # ======================================================================
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales al iniciar el módulo"""
        self.cargar_transacciones()
        self.actualizar_resumen()
        self.cargar_cuentas_contables()

    def cargar_transacciones(self):
        """Carga las transacciones según los filtros aplicados"""
        try:
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            
            query = {'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta}}
            transacciones = list(self.transacciones_collection.find(query).sort('fecha', -1))
            
            self.tabla_transacciones.setRowCount(len(transacciones))
            
            for row, trans in enumerate(transacciones):
                # ID
                self.tabla_transacciones.setItem(row, 0, QTableWidgetItem(str(trans.get('id', ''))))
                
                # Fecha (formateada)
                fecha = QDate.fromString(trans.get('fecha', ''), 'yyyy-MM-dd')
                fecha_str = fecha.toString('dd/MM/yyyy') if fecha.isValid() else ''
                self.tabla_transacciones.setItem(row, 1, QTableWidgetItem(fecha_str))
                
                # Tipo
                tipo_item = QTableWidgetItem(trans.get('tipo', ''))
                if trans.get('tipo') == 'Ingreso':
                    tipo_item.setForeground(QColor('#4CAF50'))
                else:
                    tipo_item.setForeground(QColor('#F44336'))
                self.tabla_transacciones.setItem(row, 2, tipo_item)
                
                # Descripción
                self.tabla_transacciones.setItem(row, 3, QTableWidgetItem(trans.get('descripcion', '')))
                
                # Monto (formateado)
                monto = float(trans.get('monto', 0))
                monto_item = QTableWidgetItem(f"${monto:,.2f}")
                monto_item.setData(Qt.UserRole, monto)  # Guardar valor numérico para ordenar
                self.tabla_transacciones.setItem(row, 4, monto_item)
                
                # Cuenta
                cuenta = self.cuentas_collection.find_one({'id': trans.get('cuenta', '')})
                nombre_cuenta = cuenta.get('nombre', '') if cuenta else ''
                self.tabla_transacciones.setItem(row, 5, QTableWidgetItem(nombre_cuenta))
                
                # Categoría
                self.tabla_transacciones.setItem(row, 6, QTableWidgetItem(trans.get('categoria', 'Sin categoría')))
                
                # Estado
                estado = trans.get('estado', 'Pendiente')
                estado_item = QTableWidgetItem(estado)
                if estado == 'Aprobado':
                    estado_item.setForeground(QColor('#4CAF50'))
                elif estado == 'Rechazado':
                    estado_item.setForeground(QColor('#F44336'))
                else:
                    estado_item.setForeground(QColor('#FF9800'))
                self.tabla_transacciones.setItem(row, 7, estado_item)
            
            # Actualizar contador
            self.lbl_contador.setText(f"{len(transacciones)} transacciones encontradas")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar transacciones: {str(e)}")

    def cargar_cuentas_contables(self):
        """Carga las cuentas contables en la tabla de configuración"""
        try:
            cuentas = list(self.cuentas_collection.find().sort('codigo', 1))
            self.tabla_cuentas.setRowCount(len(cuentas))
            
            for row, cuenta in enumerate(cuentas):
                self.tabla_cuentas.setItem(row, 0, QTableWidgetItem(cuenta.get('codigo', '')))
                self.tabla_cuentas.setItem(row, 1, QTableWidgetItem(cuenta.get('nombre', '')))
                self.tabla_cuentas.setItem(row, 2, QTableWidgetItem(cuenta.get('tipo', '')))
                
                saldo = float(cuenta.get('saldo_inicial', 0))
                saldo_item = QTableWidgetItem(f"${saldo:,.2f}")
                saldo_item.setData(Qt.UserRole, saldo)
                self.tabla_cuentas.setItem(row, 3, saldo_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar cuentas contables: {str(e)}")

    # ======================================================================
    # MÉTODOS DE ACTUALIZACIÓN
    # ======================================================================
    
    def actualizar_todo(self):
        """Actualiza todos los datos del módulo"""
        self.cargar_transacciones()
        self.actualizar_resumen()
        self.cargar_cuentas_contables()
        
    def actualizar_resumen(self):
        """Actualiza el resumen contable con los datos más recientes"""
        try:
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            
            # Obtener totales generales
            pipeline_totales = [
                {'$match': {'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta}}},
                {'$group': {
                    '_id': '$tipo',
                    'total': {'$sum': '$monto'}
                }}
            ]
            
            resultados_totales = list(self.transacciones_collection.aggregate(pipeline_totales))
            total_ingresos = sum(r['total'] for r in resultados_totales if r['_id'] == 'Ingreso')
            total_egresos = sum(r['total'] for r in resultados_totales if r['_id'] == 'Egreso')
            balance = total_ingresos - total_egresos
            
            # Actualizar tarjetas
            self.card_ingresos.valor_label.setText(f"${total_ingresos:,.2f}")
            self.card_egresos.valor_label.setText(f"${total_egresos:,.2f}")
            self.card_balance.valor_label.setText(f"${balance:,.2f}")
            
            # Obtener resumen por cuenta
            pipeline_cuentas = [
                {'$match': {'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta}}},
                {'$group': {
                    '_id': '$cuenta',
                    'ingresos': {
                        '$sum': {'$cond': [{'$eq': ['$tipo', 'Ingreso']}, '$monto', 0]}
                    },
                    'egresos': {
                        '$sum': {'$cond': [{'$eq': ['$tipo', 'Egreso']}, '$monto', 0]}
                    }
                }},
                {'$sort': {'_id': 1}}
            ]
            
            resultados_cuentas = list(self.transacciones_collection.aggregate(pipeline_cuentas))
            
            # Obtener nombres de cuentas
            cuentas = {c['id']: c for c in self.cuentas_collection.find()}
            
            # Llenar tabla de resumen
            self.tabla_resumen.setRowCount(len(resultados_cuentas))
            
            for row, res in enumerate(resultados_cuentas):
                cuenta_id = res['_id']
                cuenta_nombre = cuentas.get(cuenta_id, {}).get('nombre', 'Cuenta no encontrada')
                saldo = float(cuentas.get(cuenta_id, {}).get('saldo', 0))
                
                ingresos = float(res.get('ingresos', 0))
                egresos = float(res.get('egresos', 0))
                saldo_actual = saldo + ingresos - egresos
                
                # Nombre de cuenta
                self.tabla_resumen.setItem(row, 0, QTableWidgetItem(cuenta_nombre))
                
                # Ingresos
                ingresos_item = QTableWidgetItem(f"${ingresos:,.2f}")
                ingresos_item.setData(Qt.UserRole, ingresos)
                self.tabla_resumen.setItem(row, 1, ingresos_item)
                
                # Egresos
                egresos_item = QTableWidgetItem(f"${egresos:,.2f}")
                egresos_item.setData(Qt.UserRole, egresos)
                self.tabla_resumen.setItem(row, 2, egresos_item)
                
                # Saldo
                saldo_item = QTableWidgetItem(f"${saldo_actual:,.2f}")
                saldo_item.setData(Qt.UserRole, saldo_actual)
                if saldo_actual >= 0:
                    saldo_item.setForeground(QColor('#4CAF50'))
                else:
                    saldo_item.setForeground(QColor('#F44336'))
                self.tabla_resumen.setItem(row, 3, saldo_item)
                
                # Tendencia (simplificado)
                tendencia = "↑" if ingresos > egresos else "↓" if ingresos < egresos else "→"
                tendencia_item = QTableWidgetItem(tendencia)
                tendencia_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_resumen.setItem(row, 4, tendencia_item)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar resumen: {str(e)}")

    # ======================================================================
    # MÉTODOS DE TRANSACCIONES
    # ======================================================================
    
    def nueva_transaccion(self):
        """Muestra el diálogo para crear una nueva transacción"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Transacción Contable")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        form.setSpacing(12)
        
        # Campos del formulario
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(['Ingreso', 'Egreso'])
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setPlaceholderText("Descripción de la transacción")
        
        self.txt_monto = QLineEdit()
        self.txt_monto.setPlaceholderText("0.00")
        self.txt_monto.setValidator(QDoubleValidator(0, 9999999, 2))
        
        self.cmb_cuenta = QComboBox()
        cuentas = self.cuentas_collection.find().sort('nombre', 1)
        for cuenta in cuentas:
            # Usar _id de MongoDB como valor de los items del combo
            self.cmb_cuenta.addItem(cuenta['nombre'], str(cuenta['_id']))
        
        self.cmb_categoria = QComboBox()
        categorias = ["Ventas", "Compras", "Gastos", "Honorarios", "Impuestos", "Otros"]
        self.cmb_categoria.addItems(categorias)
        
        self.txt_notas = QTextEdit()
        self.txt_notas.setPlaceholderText("Notas adicionales...")
        self.txt_notas.setMaximumHeight(80)
        
        # Agregar campos al formulario
        form.addRow("Tipo:", self.cmb_tipo)
        form.addRow("Descripción:", self.txt_descripcion)
        form.addRow("Monto:", self.txt_monto)
        form.addRow("Cuenta:", self.cmb_cuenta)
        form.addRow("Categoría:", self.cmb_categoria)
        form.addRow("Notas:", self.txt_notas)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.procesar_transaccion(dialog))
        buttons.rejected.connect(dialog.reject)
        
        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        
        dialog.exec()

    def procesar_transaccion(self, dialog):
        """Procesa y guarda una nueva transacción"""
        try:
            # Validar campos
            if not self.txt_descripcion.text().strip():
                raise ValueError("La descripción es obligatoria")
            
            if not self.txt_monto.text():
                raise ValueError("El monto es obligatorio")
            
            monto = float(self.txt_monto.text())
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a cero")
            
            if self.cmb_cuenta.currentIndex() == -1:
                raise ValueError("Debe seleccionar una cuenta")
            
            # Crear documento de transacción
            transaccion = {
                'id': str(datetime.now().timestamp()),
                'fecha': QDate.currentDate().toString('yyyy-MM-dd'),
                'tipo': self.cmb_tipo.currentText(),
                'descripcion': self.txt_descripcion.text().strip(),
                'monto': monto,
                'cuenta': self.cmb_cuenta.currentData(),
                'categoria': self.cmb_categoria.currentText(),
                'notas': self.txt_notas.toPlainText(),
                'estado': 'Pendiente',
                'creado_en': datetime.now(),
                'creado_por': getattr(self.parent, 'username', 'Sistema')
            }
            
            # Insertar en la base de datos
            result = self.transacciones_collection.insert_one(transaccion)
            
            if result.inserted_id:
                # Actualizar saldo de la cuenta
                self.actualizar_saldo_cuenta(
                    self.cmb_cuenta.currentData(),
                    monto,
                    self.cmb_tipo.currentText()
                )
                
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "Transacción registrada correctamente"
                )
                dialog.accept()
                self.actualizar_todo()
            else:
                raise Exception("No se pudo insertar la transacción")
            
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo registrar la transacción: {str(e)}"
            )

    def actualizar_saldo_cuenta(self, cuenta_id, monto, tipo):
        """Actualiza el saldo de una cuenta contable"""
        try:
            from bson import ObjectId
            
            # Convertir el ID de string a ObjectId
            try:
                cuenta_oid = ObjectId(cuenta_id)
            except:
                raise Exception("ID de cuenta no válido")
                
            cuenta = self.cuentas_collection.find_one({'_id': cuenta_oid})
            if not cuenta:
                raise Exception("Cuenta no encontrada")

            saldo_actual = float(cuenta.get('saldo', 0))
            nuevo_saldo = saldo_actual + monto if tipo == 'Ingreso' else saldo_actual - monto
            
            result = self.cuentas_collection.update_one(
                {'_id': cuenta_oid},
                {'$set': {'saldo': nuevo_saldo}}
            )
            
            if result.matched_count == 0:
                raise Exception("No se pudo actualizar el saldo de la cuenta")
                
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo actualizar el saldo de la cuenta: {str(e)}"
            )
            return False

    def mostrar_menu_contextual(self, position):
        """Muestra el menú contextual para las transacciones"""
        selected_row = self.tabla_transacciones.currentRow()
        if selected_row == -1:
            return
            
        transaccion_id = self.tabla_transacciones.item(selected_row, 0).text()
        
        menu = QMenu()
        
        # Acciones del menú
        action_editar = QAction("✏️ Editar Transacción", self)
        action_aprobar = QAction("✅ Aprobar", self)
        action_rechazar = QAction("❌ Rechazar", self)
        action_eliminar = QAction("🗑️ Eliminar", self)
        
        # Conectar acciones
        action_editar.triggered.connect(lambda: self.editar_transaccion(transaccion_id))
        action_aprobar.triggered.connect(lambda: self.cambiar_estado_transaccion(transaccion_id, "Aprobado"))
        action_rechazar.triggered.connect(lambda: self.cambiar_estado_transaccion(transaccion_id, "Rechazado"))
        action_eliminar.triggered.connect(lambda: self.eliminar_transaccion(transaccion_id))
        
        # Agregar acciones al menú
        menu.addAction(action_editar)
        menu.addSeparator()
        menu.addAction(action_aprobar)
        menu.addAction(action_rechazar)
        menu.addSeparator()
        menu.addAction(action_eliminar)
        
        # Mostrar menú
        menu.exec(self.tabla_transacciones.viewport().mapToGlobal(position))

    def editar_transaccion(self, transaccion_id):
        """Edita una transacción existente"""
        # Implementación similar a nueva_transaccion pero cargando datos existentes
        pass

    def cambiar_estado_transaccion(self, transaccion_id, nuevo_estado):
        """Cambia el estado de una transacción"""
        try:
            result = self.transacciones_collection.update_one(
                {'id': transaccion_id},
                {'$set': {'estado': nuevo_estado}}
            )
            
            if result.modified_count:
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Transacción {nuevo_estado.lower()} correctamente"
                )
                self.cargar_transacciones()
            else:
                raise Exception("No se pudo actualizar el estado")
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo cambiar el estado: {str(e)}"
            )

    def eliminar_transaccion(self, transaccion_id):
        """Elimina una transacción"""
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro que desea eliminar esta transacción?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Primero obtener la transacción para revertir el saldo
                transaccion = self.transacciones_collection.find_one({'id': transaccion_id})
                if not transaccion:
                    raise Exception("Transacción no encontrada")
                
                # Eliminar la transacción
                result = self.transacciones_collection.delete_one({'id': transaccion_id})
                
                if result.deleted_count:
                    # Revertir el saldo en la cuenta
                    monto = float(transaccion.get('monto', 0))
                    tipo = transaccion.get('tipo', '')
                    cuenta_id = transaccion.get('cuenta', '')
                    
                    # Invertir el efecto en el saldo
                    if tipo == 'Ingreso':
                        self.actualizar_saldo_cuenta(cuenta_id, -monto, 'Ingreso')
                    else:
                        self.actualizar_saldo_cuenta(cuenta_id, monto, 'Egreso')
                    
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        "Transacción eliminada correctamente"
                    )
                    self.actualizar_todo()
                else:
                    raise Exception("No se pudo eliminar la transacción")
                    
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"No se pudo eliminar la transacción: {str(e)}"
                )

    # ======================================================================
    # MÉTODOS DE CUENTAS CONTABLES
    # ======================================================================
    
    def nueva_cuenta(self):
        """Crea una nueva cuenta contable"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Cuenta Contable")
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Campos del formulario
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Ej: 1105")
        
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Ej: Caja General")
        
        self.cmb_tipo_cuenta = QComboBox()
        self.cmb_tipo_cuenta.addItems(["Activo", "Pasivo", "Patrimonio", "Ingreso", "Gasto"])
        
        self.txt_saldo_inicial = QLineEdit("0.00")
        self.txt_saldo_inicial.setValidator(QDoubleValidator(0, 9999999, 2))
        
        # Agregar campos al formulario
        form.addRow("Código:", self.txt_codigo)
        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("Tipo:", self.cmb_tipo_cuenta)
        form.addRow("Saldo Inicial:", self.txt_saldo_inicial)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.guardar_cuenta(dialog))
        buttons.rejected.connect(dialog.reject)
        
        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        
        dialog.exec()

    def guardar_cuenta(self, dialog):
        """Guarda una nueva cuenta contable"""
        try:
            # Validar campos
            if not self.txt_codigo.text().strip():
                raise ValueError("El código es obligatorio")
            
            if not self.txt_nombre.text().strip():
                raise ValueError("El nombre es obligatorio")
            
            saldo = float(self.txt_saldo_inicial.text())
            
            # Crear documento de cuenta
            cuenta = {
                'id': f"CTA{datetime.now().timestamp()}",
                'codigo': self.txt_codigo.text().strip(),
                'nombre': self.txt_nombre.text().strip(),
                'tipo': self.cmb_tipo_cuenta.currentText(),
                'saldo': saldo,
                'saldo_inicial': saldo,
                'creado_en': datetime.now()
            }
            
            # Insertar en la base de datos
            result = self.cuentas_collection.insert_one(cuenta)
            
            if result.inserted_id:
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "Cuenta creada correctamente"
                )
                dialog.accept()
                self.cargar_cuentas_contables()
                self.actualizar_resumen()
            else:
                raise Exception("No se pudo crear la cuenta")
                
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo crear la cuenta: {str(e)}"
            )

    def editar_cuenta(self):
        """Edita una cuenta contable existente"""
        selected_row = self.tabla_cuentas.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione una cuenta para editar")
            return
            
        cuenta_id = self.tabla_cuentas.item(selected_row, 0).text()
        # Implementar lógica de edición similar a nueva_cuenta

    def eliminar_cuenta(self):
        """Elimina una cuenta contable"""
        selected_row = self.tabla_cuentas.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione una cuenta para eliminar")
            return
            
        cuenta_id = self.tabla_cuentas.item(selected_row, 0).text()
        
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Está seguro que desea eliminar esta cuenta?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Verificar si la cuenta tiene transacciones
                count = self.transacciones_collection.count_documents({'cuenta': cuenta_id})
                if count > 0:
                    raise Exception("No se puede eliminar una cuenta con transacciones asociadas")
                
                # Eliminar la cuenta
                result = self.cuentas_collection.delete_one({'codigo': cuenta_id})
                
                if result.deleted_count:
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        "Cuenta eliminada correctamente"
                    )
                    self.cargar_cuentas_contables()
                else:
                    raise Exception("No se pudo eliminar la cuenta")
                    
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"No se pudo eliminar la cuenta: {str(e)}"
                )

    # ======================================================================
    # MÉTODOS DE REPORTES
    # ======================================================================
    
    def generar_balance(self):
        """Genera el balance general de la empresa"""
        try:
            # Obtener cuentas de activo, pasivo y patrimonio
            activos = list(self.cuentas_collection.find({'tipo': 'Activo'}).sort('codigo', 1))
            pasivos = list(self.cuentas_collection.find({'tipo': 'Pasivo'}).sort('codigo', 1))
            patrimonio = list(self.cuentas_collection.find({'tipo': 'Patrimonio'}).sort('codigo', 1))
            
            # Calcular totales
            total_activos = sum(c['saldo'] for c in activos)
            total_pasivos = sum(c['saldo'] for c in pasivos)
            total_patrimonio = sum(c['saldo'] for c in patrimonio)
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Título
            pdf.cell(0, 10, "Balance General", 0, 1, 'C')
            pdf.ln(10)
            
            # Fecha del reporte
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Fecha: {QDate.currentDate().toString('dd/MM/yyyy')}", 0, 1, 'R')
            pdf.ln(5)
            
            # Sección de Activos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "ACTIVOS", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for cuenta in activos:
                pdf.cell(100, 6, cuenta['nombre'])
                pdf.cell(40, 6, f"${cuenta['saldo']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(100, 8, "TOTAL ACTIVOS")
            pdf.cell(40, 8, f"${total_activos:,.2f}", 0, 1, 'R')
            pdf.ln(10)
            
            # Sección de Pasivos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "PASIVOS", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for cuenta in pasivos:
                pdf.cell(100, 6, cuenta['nombre'])
                pdf.cell(40, 6, f"${cuenta['saldo']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(100, 8, "TOTAL PASIVOS")
            pdf.cell(40, 8, f"${total_pasivos:,.2f}", 0, 1, 'R')
            pdf.ln(10)
            
            # Sección de Patrimonio
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "PATRIMONIO", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for cuenta in patrimonio:
                pdf.cell(100, 6, cuenta['nombre'])
                pdf.cell(40, 6, f"${cuenta['saldo']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(100, 8, "TOTAL PATRIMONIO")
            pdf.cell(40, 8, f"${total_patrimonio:,.2f}", 0, 1, 'R')
            pdf.ln(15)
            
            # Total general
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(100, 10, "TOTAL PASIVOS + PATRIMONIO")
            pdf.cell(40, 10, f"${(total_pasivos + total_patrimonio):,.2f}", 0, 1, 'R')
            
            # Guardar y abrir el PDF
            file_path = os.path.join(os.path.expanduser("~"), "balance_general.pdf")
            pdf.output(file_path)
            
            webbrowser.open(file_path)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo generar el balance general: {str(e)}"
            )

    def generar_estado_resultados(self):
        """Genera el estado de resultados"""
        try:
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            
            # Obtener ingresos y gastos
            pipeline = [
                {'$match': {
                    'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                    'estado': 'Aprobado'
                }},
                {'$group': {
                    '_id': '$tipo',
                    'total': {'$sum': '$monto'}
                }}
            ]
            
            resultados = list(self.transacciones_collection.aggregate(pipeline))
            total_ingresos = sum(r['total'] for r in resultados if r['_id'] == 'Ingreso')
            total_egresos = sum(r['total'] for r in resultados if r['_id'] == 'Egreso')
            utilidad = total_ingresos - total_egresos
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Título
            pdf.cell(0, 10, "Estado de Resultados", 0, 1, 'C')
            pdf.ln(5)
            
            # Período
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Período: {self.fecha_desde.date().toString('dd/MM/yyyy')} a {self.fecha_hasta.date().toString('dd/MM/yyyy')}", 0, 1, 'C')
            pdf.ln(10)
            
            # Ingresos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "INGRESOS", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            # Agrupar ingresos por categoría
            pipeline_ingresos = [
                {'$match': {
                    'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                    'tipo': 'Ingreso',
                    'estado': 'Aprobado'
                }},
                {'$group': {
                    '_id': '$categoria',
                    'total': {'$sum': '$monto'}
                }},
                {'$sort': {'total': -1}}
            ]
            
            ingresos_cat = list(self.transacciones_collection.aggregate(pipeline_ingresos))
            
            for ingreso in ingresos_cat:
                pdf.cell(120, 6, ingreso['_id'])
                pdf.cell(40, 6, f"${ingreso['total']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "TOTAL INGRESOS")
            pdf.cell(40, 8, f"${total_ingresos:,.2f}", 0, 1, 'R')
            pdf.ln(10)
            
            # Gastos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "GASTOS", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            # Agrupar gastos por categoría
            pipeline_gastos = [
                {'$match': {
                    'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                    'tipo': 'Egreso',
                    'estado': 'Aprobado'
                }},
                {'$group': {
                    '_id': '$categoria',
                    'total': {'$sum': '$monto'}
                }},
                {'$sort': {'total': -1}}
            ]
            
            gastos_cat = list(self.transacciones_collection.aggregate(pipeline_gastos))
            
            for gasto in gastos_cat:
                pdf.cell(120, 6, gasto['_id'])
                pdf.cell(40, 6, f"${gasto['total']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "TOTAL GASTOS")
            pdf.cell(40, 8, f"${total_egresos:,.2f}", 0, 1, 'R')
            pdf.ln(15)
            
            # Utilidad
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(120, 10, "UTILIDAD NETA")
            pdf.cell(40, 10, f"${utilidad:,.2f}", 0, 1, 'R')
            
            # Guardar y abrir el PDF
            file_path = os.path.join(os.path.expanduser("~"), "estado_resultados.pdf")
            pdf.output(file_path)
            
            webbrowser.open(file_path)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo generar el estado de resultados: {str(e)}"
            )

    def generar_flujo_efectivo(self):
        """Genera el flujo de efectivo"""
        try:
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            
            # Obtener cuentas de efectivo
            cuentas_efectivo = list(self.cuentas_collection.find({
                'tipo': 'Activo',
                'nombre': {'$regex': 'caja|efectivo|banco', '$options': 'i'}
            }))
            
            if not cuentas_efectivo:
                raise Exception("No se encontraron cuentas de efectivo configuradas")
            
            # Obtener transacciones de efectivo
            transacciones = list(self.transacciones_collection.find({
                'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                'cuenta': {'$in': [c['id'] for c in cuentas_efectivo]},
                'estado': 'Aprobado'
            }))
            
            # Calcular saldos
            saldo_inicial = sum(c['saldo_inicial'] for c in cuentas_efectivo)
            ingresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'Ingreso')
            egresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'Egreso')
            saldo_final = saldo_inicial + ingresos - egresos
            
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Título
            pdf.cell(0, 10, "Flujo de Efectivo", 0, 1, 'C')
            pdf.ln(5)
            
            # Período
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Período: {self.fecha_desde.date().toString('dd/MM/yyyy')} a {self.fecha_hasta.date().toString('dd/MM/yyyy')}", 0, 1, 'C')
            pdf.ln(10)
            
            # Saldo inicial
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "SALDO INICIAL", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            for cuenta in cuentas_efectivo:
                pdf.cell(120, 6, cuenta['nombre'])
                pdf.cell(40, 6, f"${cuenta['saldo_inicial']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "TOTAL SALDO INICIAL")
            pdf.cell(40, 8, f"${saldo_inicial:,.2f}", 0, 1, 'R')
            pdf.ln(10)
            
            # Ingresos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "INGRESOS DE EFECTIVO", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            # Agrupar ingresos por categoría
            pipeline_ingresos = [
                {'$match': {
                    'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                    'tipo': 'Ingreso',
                    'estado': 'Aprobado',
                    'cuenta': {'$in': [c['id'] for c in cuentas_efectivo]}
                }},
                {'$group': {
                    '_id': '$categoria',
                    'total': {'$sum': '$monto'}
                }},
                {'$sort': {'total': -1}}
            ]
            
            ingresos_cat = list(self.transacciones_collection.aggregate(pipeline_ingresos))
            
            for ingreso in ingresos_cat:
                pdf.cell(120, 6, ingreso['_id'])
                pdf.cell(40, 6, f"${ingreso['total']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "TOTAL INGRESOS")
            pdf.cell(40, 8, f"${ingresos:,.2f}", 0, 1, 'R')
            pdf.ln(10)
            
            # Egresos
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, "EGRESOS DE EFECTIVO", 0, 1)
            pdf.set_font("Arial", '', 10)
            
            # Agrupar egresos por categoría
            pipeline_egresos = [
                {'$match': {
                    'fecha': {'$gte': fecha_desde, '$lte': fecha_hasta},
                    'tipo': 'Egreso',
                    'estado': 'Aprobado',
                    'cuenta': {'$in': [c['id'] for c in cuentas_efectivo]}
                }},
                {'$group': {
                    '_id': '$categoria',
                    'total': {'$sum': '$monto'}
                }},
                {'$sort': {'total': -1}}
            ]
            
            egresos_cat = list(self.transacciones_collection.aggregate(pipeline_egresos))
            
            for egreso in egresos_cat:
                pdf.cell(120, 6, egreso['_id'])
                pdf.cell(40, 6, f"${egreso['total']:,.2f}", 0, 1, 'R')
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(120, 8, "TOTAL EGRESOS")
            pdf.cell(40, 8, f"${egresos:,.2f}", 0, 1, 'R')
            pdf.ln(15)
            
            # Saldo final
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(120, 10, "SALDO FINAL DE EFECTIVO")
            pdf.cell(40, 10, f"${saldo_final:,.2f}", 0, 1, 'R')
            
            # Guardar y abrir el PDF
            file_path = os.path.join(os.path.expanduser("~"), "flujo_efectivo.pdf")
            pdf.output(file_path)
            
            webbrowser.open(file_path)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo generar el flujo de efectivo: {str(e)}"
            )

    # ======================================================================
    # MÉTODOS DE EXPORTACIÓN
    # ======================================================================
    
    def exportar_transacciones_csv(self):
        """Exporta las transacciones a un archivo CSV"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Transacciones", 
            f"transacciones_{QDate.currentDate().toString('yyyyMMdd')}.csv", 
            "Archivos CSV (*.csv)"
        )
        
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=',')
                
                # Escribir encabezados
                headers = []
                for col in range(self.tabla_transacciones.columnCount()):
                    headers.append(self.tabla_transacciones.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Escribir datos
                for row in range(self.tabla_transacciones.rowCount()):
                    row_data = []
                    for col in range(self.tabla_transacciones.columnCount()):
                        item = self.tabla_transacciones.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
                
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Transacciones exportadas correctamente a:\n{path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo exportar las transacciones: {str(e)}"
            )

    def exportar_resumen_csv(self):
        """Exporta el resumen contable a un archivo CSV"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Resumen Contable", 
            f"resumen_contable_{QDate.currentDate().toString('yyyyMMdd')}.csv", 
            "Archivos CSV (*.csv)"
        )
        
        if not path:
            return
            
        try:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=',')
                
                # Escribir encabezados
                headers = []
                for col in range(self.tabla_resumen.columnCount()):
                    headers.append(self.tabla_resumen.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Escribir datos
                for row in range(self.tabla_resumen.rowCount()):
                    row_data = []
                    for col in range(self.tabla_resumen.columnCount()):
                        item = self.tabla_resumen.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
                
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Resumen contable exportado correctamente a:\n{path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo exportar el resumen: {str(e)}"
            )

    def generar_pdf_transacciones(self):
        """Genera un PDF con el listado de transacciones"""
        try:
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Título
            pdf.cell(0, 10, "Reporte de Transacciones", 0, 1, 'C')
            pdf.ln(5)
            
            # Período
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Período: {self.fecha_desde.date().toString('dd/MM/yyyy')} a {self.fecha_hasta.date().toString('dd/MM/yyyy')}", 0, 1, 'C')
            pdf.ln(10)
            
            # Encabezados de tabla
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(200, 200, 200)
            
            headers = []
            for col in range(self.tabla_transacciones.columnCount()):
                headers.append(self.tabla_transacciones.horizontalHeaderItem(col).text())
            
            # Ajustar anchos de columna
            widths = [20, 20, 20, 60, 20, 30, 20, 20]
            
            for i, header in enumerate(headers):
                pdf.cell(widths[i], 8, header, 1, 0, 'C', True)
            
            pdf.ln()
            
            # Datos de la tabla
            pdf.set_font("Arial", '', 9)
            pdf.set_fill_color(255, 255, 255)
            
            for row in range(self.tabla_transacciones.rowCount()):
                for col in range(self.tabla_transacciones.columnCount()):
                    item = self.tabla_transacciones.item(row, col)
                    text = item.text() if item else ''
                    
                    # Aplicar color según el tipo de dato
                    if col == 2:  # Columna de Tipo
                        if text == 'Ingreso':
                            pdf.set_text_color(0, 128, 0)  # Verde
                        else:
                            pdf.set_text_color(255, 0, 0)  # Rojo
                    elif col == 7:  # Columna de Estado
                        if text == 'Aprobado':
                            pdf.set_text_color(0, 128, 0)  # Verde
                        elif text == 'Rechazado':
                            pdf.set_text_color(255, 0, 0)  # Rojo
                        else:
                            pdf.set_text_color(255, 165, 0)  # Naranja
                    else:
                        pdf.set_text_color(0, 0, 0)  # Negro
                    
                    pdf.cell(widths[col], 6, text, 1, 0, 'L')
                
                pdf.ln()
                pdf.set_text_color(0, 0, 0)  # Restablecer color
            
            # Guardar y abrir el PDF
            file_path = os.path.join(os.path.expanduser("~"), "reporte_transacciones.pdf")
            pdf.output(file_path)
            
            webbrowser.open(file_path)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo generar el PDF: {str(e)}"
            )
    
    def filtrar_transacciones(self):
        try:
            # Obtener fechas desde los QDateEdit
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            
            # Construir query de filtrado
            query = {
                'fecha': {
                    '$gte': fecha_desde,
                    '$lte': fecha_hasta
                }
            }
            
            # Obtener transacciones filtradas
            transacciones = list(self.transacciones_collection.find(query).sort('fecha', -1))
            
            # Limpiar tabla
            self.tabla_transacciones.setRowCount(0)
            
            # Llenar tabla con transacciones filtradas
            for row, trans in enumerate(transacciones):
                self.tabla_transacciones.insertRow(row)
                
                # ID
                self.tabla_transacciones.setItem(row, 0, QTableWidgetItem(str(trans.get('id', ''))))
                
                # Fecha (formateada)
                fecha = QDate.fromString(trans.get('fecha', ''), 'yyyy-MM-dd')
                fecha_str = fecha.toString('dd/MM/yyyy') if fecha.isValid() else ''
                self.tabla_transacciones.setItem(row, 1, QTableWidgetItem(fecha_str))
                
                # Tipo
                tipo_item = QTableWidgetItem(trans.get('tipo', ''))
                if trans.get('tipo') == 'Ingreso':
                    tipo_item.setForeground(QColor('#4CAF50'))  # Verde
                else:
                    tipo_item.setForeground(QColor('#F44336'))  # Rojo
                self.tabla_transacciones.setItem(row, 2, tipo_item)
                
                # Descripción
                self.tabla_transacciones.setItem(row, 3, QTableWidgetItem(trans.get('descripcion', '')))
                
                # Monto (formateado)
                monto = float(trans.get('monto', 0))
                monto_item = QTableWidgetItem(f"${monto:,.2f}")
                monto_item.setData(Qt.UserRole, monto)  # Guardar valor numérico para ordenar
                self.tabla_transacciones.setItem(row, 4, monto_item)
                
                # Cuenta
                cuenta = self.cuentas_collection.find_one({'id': trans.get('cuenta', '')})
                nombre_cuenta = cuenta.get('nombre', '') if cuenta else ''
                self.tabla_transacciones.setItem(row, 5, QTableWidgetItem(nombre_cuenta))
                
                # Categoría
                self.tabla_transacciones.setItem(row, 6, QTableWidgetItem(trans.get('categoria', 'Sin categoría')))
                
                # Estado
                estado = trans.get('estado', 'Pendiente')
                estado_item = QTableWidgetItem(estado)
                if estado == 'Aprobado':
                    estado_item.setForeground(QColor('#4CAF50'))
                elif estado == 'Rechazado':
                    estado_item.setForeground(QColor('#F44336'))
                else:
                    estado_item.setForeground(QColor('#FF9800'))  # Amarillo/Naranja
                self.tabla_transacciones.setItem(row, 7, estado_item)
            
            # Actualizar contador
            self.lbl_contador.setText(f"{len(transacciones)} transacciones encontradas")
            
            # Actualizar resumen
            self.actualizar_resumen()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar transacciones: {str(e)}")