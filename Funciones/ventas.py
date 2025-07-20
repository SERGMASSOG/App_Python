from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QFrame, QHeaderView, QGridLayout
)
from PySide6.QtCore import Qt, QDate
from pymongo import MongoClient
from datetime import datetime
import csv
import os

class VentasManager(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Gestión de Ventas")
        self.setMinimumSize(1000, 700)

        self.setup_ui()
        self.aplicar_estilos()
        self.load_ventas()

    def setup_ui(self):
        """Construye la interfaz: filtros de fecha, cuadrícula de botones de acción y tarjetas métricas al tope, tabla de ventas debajo."""
        # --- Layout raíz
        main_layout = QVBoxLayout(self)

        # ================= Sección superior =================
        top_layout = QHBoxLayout()
        # -------- Filtros de fecha (izquierda) --------
        filtros_layout = QVBoxLayout()
        lbl_desde = QLabel("Desde:")
        self.fecha_desde = QDateEdit(calendarPopup=True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(lbl_desde)
        filtros_layout.addWidget(self.fecha_desde)

        lbl_hasta = QLabel("Hasta:")
        self.fecha_hasta = QDateEdit(calendarPopup=True)
        self.fecha_hasta.setDate(QDate.currentDate())
        filtros_layout.addWidget(lbl_hasta)
        filtros_layout.addWidget(self.fecha_hasta)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.load_ventas)
        filtros_layout.addWidget(self.btn_buscar)
        filtros_layout.addStretch()
        top_layout.addLayout(filtros_layout)

        # -------- Botones de acción (centro) --------
        grid_buttons = QGridLayout()
        self.btn_nueva_venta = QPushButton("Nueva Venta")
        self.btn_anular_venta = QPushButton("Anular Venta")
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_exportar = QPushButton("Exportar")

        grid_buttons.addWidget(self.btn_nueva_venta, 0, 0)
        grid_buttons.addWidget(self.btn_anular_venta, 0, 1)
        grid_buttons.addWidget(self.btn_imprimir, 1, 0)
        grid_buttons.addWidget(self.btn_exportar, 1, 1)

        # Conectar señales
        self.btn_nueva_venta.clicked.connect(self.nueva_venta)
        self.btn_anular_venta.clicked.connect(self.anular_venta)
        self.btn_imprimir.clicked.connect(self.imprimir_ticket)

        botones_widget = QWidget()
        botones_widget.setLayout(grid_buttons)
        top_layout.addWidget(botones_widget, alignment=Qt.AlignTop)

        # -------- Tarjetas métricas (derecha) --------
        self.metrics = {}
        metrics_widget = QWidget()
        metrics_grid = QGridLayout(metrics_widget)
        metrics_grid.setSpacing(10)
        metrics_grid.setContentsMargins(0, 10, 0, 10)

        # Crear tarjetas (2 filas x 2 columnas)
        metric_keys_order = [
            ("total_ventas", "Total Ventas", "0", "#4CAF50"),
            ("total_vendido", "Total Vendido", "$0", "#2196F3"),
            ("ventas_anuladas", "Ventas Anuladas", "0", "#FF9800"),
            ("ticket_promedio", "Ticket Promedio", "$0", "#9C27B0"),
        ]
        for idx, (k, titulo, val, color) in enumerate(metric_keys_order):
            self.metrics[k] = self.create_metric_card(titulo, val, color)
            row, col = divmod(idx, 2)
            metrics_grid.addWidget(self.metrics[k], row, col)

        top_layout.addWidget(metrics_widget, alignment=Qt.AlignTop)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # ================= Tabla de ventas =================
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(6)
        self.ventas_table.setHorizontalHeaderLabels([
            "Código", "Cliente", "Fecha", "Total", "Estado", "Método Pago"
        ])
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.ventas_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        main_layout.addWidget(self.ventas_table)
        main_layout.setStretchFactor(self.ventas_table, 1)

        # Compatibilidad con referencias heredadas
        self.tabla_reportes = None

        # Exportar
        self.btn_exportar.clicked.connect(self.exportar_excel)

        # Finalizar construcción de UI y evitar ejecutar código duplicado heredado
        return
        layout_principal = QVBoxLayout(self)

        # ======= Top section with filters and action buttons =======
        top_layout = QHBoxLayout()

        # Left: date filters stacked vertically + Buscar
        date_layout = QVBoxLayout()
        lbl_desde = QLabel("Desde:")
        self.fecha_desde = QDateEdit(calendarPopup=True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(lbl_desde)
        date_layout.addWidget(self.fecha_desde)

        lbl_hasta = QLabel("Hasta:")
        self.fecha_hasta = QDateEdit(calendarPopup=True)
        self.fecha_hasta.setDate(QDate.currentDate())
        date_layout.addWidget(lbl_hasta)
        date_layout.addWidget(self.fecha_hasta)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.load_ventas)
        date_layout.addWidget(self.btn_buscar)

        date_layout.addStretch()
        top_layout.addLayout(date_layout)

        # Right: action buttons in 2x2 grid
        grid_buttons = QGridLayout()
        self.btn_nueva_venta = QPushButton("Nueva Venta")
        self.btn_anular_venta = QPushButton("Anular Venta")
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_exportar = QPushButton("Exportar")

        grid_buttons.addWidget(self.btn_nueva_venta, 0, 0)
        grid_buttons.addWidget(self.btn_anular_venta, 0, 1)
        grid_buttons.addWidget(self.btn_imprimir, 1, 0)
        grid_buttons.addWidget(self.btn_exportar, 1, 1)

        # Conectar señales
        self.btn_nueva_venta.clicked.connect(self.nueva_venta)
        self.btn_anular_venta.clicked.connect(self.anular_venta)
        self.btn_imprimir.clicked.connect(self.imprimir_ticket)

        # Contenedor para los botones para poder alinear fácilmente al tope
        botones_widget = QWidget()
        botones_widget.setLayout(grid_buttons)
        top_layout.addWidget(botones_widget)
        top_layout.setAlignment(botones_widget, Qt.AlignTop)
        top_layout.addStretch()

        layout_principal.addLayout(top_layout)

        # ======= Metric cards (added previously, keep existing container) =======
        # metric container built below in code section already present

        layout_principal = QVBoxLayout(self)

        # --- Filtros de fecha ---
        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = QDateEdit(calendarPopup=True)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(self.fecha_desde)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = QDateEdit(calendarPopup=True)
        self.fecha_hasta.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.fecha_hasta)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.load_ventas)
        filtros_layout.addWidget(self.btn_buscar)

        layout_principal.addLayout(filtros_layout)

        # ----- Métricas -----
        self.metrics = {}
        metrics_container = QWidget()
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 10, 0, 10)
        metrics_layout.setSpacing(15)

        self.metrics["total_ventas"] = self.create_metric_card("Total Ventas", "0", "#4CAF50")
        self.metrics["total_vendido"] = self.create_metric_card("Total Vendido", "$0", "#2196F3")
        self.metrics["ventas_anuladas"] = self.create_metric_card("Ventas Anuladas", "0", "#FF9800")
        self.metrics["ticket_promedio"] = self.create_metric_card("Ticket Promedio", "$0", "#9C27B0")

        metrics_layout.addStretch()
        for key in [
            "total_ventas",
            "total_vendido",
            "ventas_anuladas",
            "ticket_promedio"
        ]:
            metrics_layout.addWidget(self.metrics[key])
        metrics_layout.addStretch()

        layout_principal.addWidget(metrics_container)

        # Dummy attribute to maintain compatibility with legacy references
        self.tabla_reportes = None

        # ======= Tabla de ventas =======
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(6)
        self.ventas_table.setHorizontalHeaderLabels([
            "Código", "Cliente", "Fecha", "Total", "Estado", "Método Pago"
        ])
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self.ventas_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        layout_principal.addWidget(self.ventas_table)
        # Hacer que la tabla use el espacio restante
        layout_principal.setStretchFactor(self.ventas_table, 1)

        # (Tabla resumen eliminada — información ahora en tarjetas)

        # self.tabla_reportes.setHorizontalHeaderLabels(["Cantidad de Ventas", "Total Vendido", "Ventas Anuladas"])

        # layout_principal.addWidget(self.tabla_reportes)





        self.btn_exportar.clicked.connect(self.exportar_excel)

    def create_metric_card(self, title, initial_value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                min-width: 150px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        label_title = QLabel(title)
        label_title.setStyleSheet("color: #718096; font-size: 14px;")
        label_value = QLabel(initial_value)
        label_value.setObjectName("value")
        label_value.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        card_layout.addWidget(label_title)
        card_layout.addWidget(label_value)
        return card

    def update_metric_cards(self, total, vendido, anuladas):
        self.metrics["total_ventas"].findChild(QLabel, "value").setText(str(total))
        self.metrics["total_vendido"].findChild(QLabel, "value").setText(f"${vendido:,.2f}")
        self.metrics["ventas_anuladas"].findChild(QLabel, "value").setText(str(anuladas))
        ticket = vendido / (total - anuladas) if (total - anuladas) else 0
        self.metrics["ticket_promedio"].findChild(QLabel, "value").setText(f"${ticket:,.2f}")

    def nueva_venta(self):
        """Abre diálogo para registrar nueva venta"""
        try:
            from dialogs.venta_dialog import VentaDialog
        except ImportError:
            QMessageBox.critical(self, "Error", "No se encontró el diálogo de venta (venta_dialog.py)")
            return
        dialog = VentaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:  # Correct
            datos = dialog.obtener_datos()
            try:
                self.db["Ventas"].insert_one(datos)
                QMessageBox.information(self, "Éxito", "Venta registrada correctamente")
                self.load_ventas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo registrar la venta: {str(e)}")

    def anular_venta(self):
        selected = self.ventas_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione una venta para anular")
            return
        row = selected[0].row()
        codigo = self.ventas_table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Anular la venta {codigo}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.db["Ventas"].update_one({"codigo": codigo}, {"$set": {"estado": "Anulada"}})
                QMessageBox.information(self, "Éxito", "Venta anulada")
                self.load_ventas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo anular la venta: {str(e)}")

    def imprimir_ticket(self):
        QMessageBox.information(self, "Imprimir", "Función de impresión aún no implementada")

    def aplicar_estilos(self):
        estilo_boton = """
        QPushButton {
            background-color: #FF6B00;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #E05E00;
        }
        QPushButton:pressed {
            background-color: #C35000;
        }
        """
        estilo_fecha = """
        QDateEdit {
            background-color: white;
            border: 1px solid #CCC;
            padding: 4px;
            border-radius: 4px;
        }
        """
        estilo_tabla = """
        QTableWidget {
            background-color: #F9F9F9;
            border: 1px solid #DDD;
            font-size: 13px;
        }
        QHeaderView::section {
            background-color: #FF6B00;
            color: white;
            font-weight: bold;
            padding: 6px;
            border: none;
        }
        QTableWidget::item:selected {
            background-color: #FFE0CC;
        }
        """

        for btn in [self.btn_buscar, self.btn_nueva_venta, self.btn_anular_venta, self.btn_imprimir, self.btn_exportar]:
            btn.setStyleSheet(estilo_boton)

        self.fecha_desde.setStyleSheet(estilo_fecha)
        self.fecha_hasta.setStyleSheet(estilo_fecha)
        self.ventas_table.setStyleSheet(estilo_tabla)
    

    def load_ventas(self):
        """Carga las ventas y actualiza tabla + resumen"""
        fecha_ini = self.fecha_desde.date().toPython()
        fecha_fin = self.fecha_hasta.date().toPython()
        fecha_ini = datetime(fecha_ini.year, fecha_ini.month, fecha_ini.day, 0, 0, 0)
        fecha_fin = datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day, 23, 59, 59)

        ventas = list(self.db["Ventas"].find({
            "fecha": {"$gte": fecha_ini, "$lte": fecha_fin}
        }).sort("fecha", 1))

        self.ventas_table.setRowCount(0)
        total_vendido = 0
        anuladas = 0

        for venta in ventas:
            row = self.ventas_table.rowCount()
            self.ventas_table.insertRow(row)
            def make_item(text):
                item = QTableWidgetItem(text)
                item.setForeground(Qt.black)
                return item

            self.ventas_table.setItem(row, 0, make_item(venta.get("codigo", "")))
            self.ventas_table.setItem(row, 1, make_item(venta.get("cliente", "")))
            self.ventas_table.setItem(row, 2, make_item(str(venta.get("fecha", ""))))
            self.ventas_table.setItem(row, 3, make_item(f"${venta.get('total', 0):,.2f}"))
            self.ventas_table.setItem(row, 4, make_item(venta.get("estado", "")))
            self.ventas_table.setItem(row, 5, make_item(venta.get("metodo_pago", "")))

            if venta.get("estado", "").lower() != "anulada":
                total_vendido += float(venta.get("total", 0))
            else:
                anuladas += 1

        # Ajustar columnas
        self.ventas_table.resizeColumnsToContents()

        # Ajustar columnas
        #
        #
        #

        # Actualizar tarjetas
        self.update_metric_cards(len(ventas), total_vendido, anuladas)

    def exportar_excel(self):
        """Exporta la tabla de ventas a un archivo CSV"""
        try:
            path = "reporte_ventas.csv"
            with open(path, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                headers = ["Código", "Cliente", "Fecha", "Total", "Estado", "Método Pago"]
                writer.writerow(headers)
                for row in range(self.ventas_table.rowCount()):
                    fila = []
                    for col in range(self.ventas_table.columnCount()):
                        item = self.ventas_table.item(row, col)
                        fila.append(item.text() if item else "")
                    writer.writerow(fila)
            QMessageBox.information(self, "Exportación Exitosa", f"Archivo exportado como {path}")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {str(e)}")
