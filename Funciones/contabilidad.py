from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QDateEdit, QLabel, 
                             QComboBox, QHeaderView, QFormLayout, QLineEdit, QDialog, 
                             QDialogButtonBox, QWidget, QFileDialog)
from PySide6.QtCore import Qt, QDate
from db.mongo_connection import get_db_connection
import csv

class ContabilidadManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db = get_db_connection()
        self.transacciones_collection = self.db['transacciones']
        self.cuentas_collection = self.db['cuentas_contables']
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Rango de fechas:"))

        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(QLabel("Desde:"))
        filter_layout.addWidget(self.fecha_desde)

        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("Hasta:"))
        filter_layout.addWidget(self.fecha_hasta)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.filtrar_transacciones)

        btn_nueva_transaccion = QPushButton("Nueva Transacción")
        btn_nueva_transaccion.clicked.connect(self.nueva_transaccion)

        top_layout.addLayout(filter_layout)
        top_layout.addStretch()
        top_layout.addWidget(btn_buscar)
        top_layout.addWidget(btn_nueva_transaccion)

        self.tabs = QTabWidget()
        self.tab_transacciones = QWidget()
        self.setup_tab_transacciones()
        self.tab_resumen = QWidget()
        self.setup_tab_resumen()

        self.tabs.addTab(self.tab_transacciones, "Transacciones")
        self.tabs.addTab(self.tab_resumen, "Resumen")

        layout.addLayout(top_layout)
        layout.addWidget(self.tabs)

        self.cargar_transacciones()
        self.actualizar_resumen()

    def setup_tab_transacciones(self):
        layout = QVBoxLayout(self.tab_transacciones)
        self.tabla_transacciones = QTableWidget()
        self.configurar_tabla_transacciones()
        layout.addWidget(self.tabla_transacciones)

    def setup_tab_resumen(self):
        layout = QVBoxLayout(self.tab_resumen)

        self.tabla_reportes = QTableWidget()
        self.tabla_reportes.setColumnCount(2)
        self.tabla_reportes.setHorizontalHeaderLabels(["Cuenta", "Saldo"])
        self.tabla_reportes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        btn_exportar = QPushButton("Exportar Resumen CSV")
        btn_exportar.clicked.connect(self.exportar_resumen_csv)

        layout.addWidget(QLabel("Resumen de contabilidad"))
        layout.addWidget(self.tabla_reportes)
        layout.addWidget(btn_exportar)

    def configurar_tabla_transacciones(self):
        headers = ["ID", "Fecha", "Tipo", "Descripción", "Monto", "Cuenta", "Estado"]
        self.tabla_transacciones.setColumnCount(len(headers))
        self.tabla_transacciones.setHorizontalHeaderLabels(headers)
        self.tabla_transacciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_transacciones.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_transacciones.setEditTriggers(QTableWidget.NoEditTriggers)

    def cargar_transacciones(self):
        try:
            fecha_desde = self.fecha_desde.date().toString('yyyy-MM-dd')
            fecha_hasta = self.fecha_hasta.date().toString('yyyy-MM-dd')
            self.load_transacciones(self.tabla_transacciones, fecha_desde, fecha_hasta)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar transacciones: {str(e)}")

    def filtrar_transacciones(self):
        self.cargar_transacciones()
        self.actualizar_resumen()

    def nueva_transaccion(self):
        self.mostrar_dialogo_transaccion()

    def load_transacciones(self, table_widget, fecha_inicio=None, fecha_fin=None):
        try:
            query = {}
            if fecha_inicio and fecha_fin:
                query['fecha'] = {'$gte': fecha_inicio, '$lte': fecha_fin}

            transacciones = list(self.transacciones_collection.find(query, {'_id': 0}))
            table_widget.setRowCount(len(transacciones))

            for row, trans in enumerate(transacciones):
                for col, key in enumerate(['id', 'fecha', 'tipo', 'descripcion', 'monto', 'cuenta', 'estado']):
                    table_widget.setItem(row, col, QTableWidgetItem(str(trans.get(key, ''))))
        except Exception as e:
            QMessageBox.critical(self.parent, 'Error', f'Error al cargar transacciones: {str(e)}')

    def add_transaccion(self, data):
        try:
            data['fecha'] = QDate.currentDate().toString('yyyy-MM-dd')
            self.transacciones_collection.insert_one(data)
            self.actualizar_saldo_cuenta(data['cuenta'], data['monto'], data['tipo'])
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, 'Error', f'Error al agregar transacción: {str(e)}')
            return False

    def actualizar_saldo_cuenta(self, cuenta_id, monto, tipo_transaccion):
        try:
            cuenta = self.cuentas_collection.find_one({'id': cuenta_id})
            if not cuenta:
                raise Exception("Cuenta no encontrada")

            nuevo_saldo = float(cuenta.get('saldo', 0))
            if tipo_transaccion.lower() == 'ingreso':
                nuevo_saldo += float(monto)
            else:
                nuevo_saldo -= float(monto)

            self.cuentas_collection.update_one({'id': cuenta_id}, {'$set': {'saldo': nuevo_saldo}})
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, 'Error', f'Error al actualizar saldo: {str(e)}')
            return False

    def mostrar_dialogo_transaccion(self, transaccion=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Transacción" if not transaccion else "Editar Transacción")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()
        form = QFormLayout()

        cmb_tipo = QComboBox()
        cmb_tipo.addItems(['Ingreso', 'Egreso'])
        txt_descripcion = QLineEdit()
        txt_monto = QLineEdit()
        txt_monto.setPlaceholderText("0.00")
        cmb_cuenta = QComboBox()

        cuentas = self.cuentas_collection.find({}, {'_id': 0, 'nombre': 1, 'id': 1})
        for cuenta in cuentas:
            cmb_cuenta.addItem(cuenta['nombre'], cuenta['id'])

        form.addRow("Tipo:", cmb_tipo)
        form.addRow("Descripción:", txt_descripcion)
        form.addRow("Monto:", txt_monto)
        form.addRow("Cuenta:", cmb_cuenta)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            if not all([txt_descripcion.text().strip(), txt_monto.text().strip()]):
                QMessageBox.warning(self, 'Validación', 'Todos los campos son obligatorios')
                return

            try:
                monto = float(txt_monto.text())
                if monto <= 0:
                    raise ValueError("El monto debe ser mayor a cero")

                transaccion_data = {
                    'tipo': cmb_tipo.currentText(),
                    'descripcion': txt_descripcion.text().strip(),
                    'monto': monto,
                    'cuenta': cmb_cuenta.currentData(),
                    'estado': 'Pendiente'
                }

                if not transaccion:
                    if self.add_transaccion(transaccion_data):
                        QMessageBox.information(self, 'Éxito', 'Transacción agregada correctamente')
                        self.cargar_transacciones()
                        self.actualizar_resumen()
                else:
                    if self.actualizar_transaccion(transaccion['id'], transaccion_data):
                        QMessageBox.information(self, 'Éxito', 'Transacción actualizada correctamente')
                        self.cargar_transacciones()
                        self.actualizar_resumen()
            except ValueError as e:
                QMessageBox.critical(self, 'Error', f'Error en los datos: {str(e)}')

    def actualizar_transaccion(self, transaccion_id, data):
        try:
            self.transacciones_collection.update_one({'id': transaccion_id}, {'$set': data})
            self.actualizar_saldo_cuenta(data['cuenta'], data['monto'], data['tipo'])
            return True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al actualizar transacción: {str(e)}')
            return False

    def actualizar_resumen(self):
        cuentas = list(self.cuentas_collection.find({}, {'_id': 0, 'nombre': 1, 'saldo': 1}))
        self.tabla_reportes.setRowCount(len(cuentas))

        for i, cuenta in enumerate(cuentas):
            self.tabla_reportes.setItem(i, 0, QTableWidgetItem(str(cuenta.get('nombre', ''))))
            self.tabla_reportes.setItem(i, 1, QTableWidgetItem(str(cuenta.get('saldo', 0))))

    def exportar_resumen_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "resumen.csv", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Cuenta", "Saldo"])
                    for row in range(self.tabla_reportes.rowCount()):
                        cuenta = self.tabla_reportes.item(row, 0).text()
                        saldo = self.tabla_reportes.item(row, 1).text()
                        writer.writerow([cuenta, saldo])
                QMessageBox.information(self, "Éxito", "Resumen exportado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo: {str(e)}")
