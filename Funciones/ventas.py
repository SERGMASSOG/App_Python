from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox
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

        # --- Tabla de ventas ---
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(6)
        self.ventas_table.setHorizontalHeaderLabels([
            "Código", "Cliente", "Fecha", "Total", "Estado", "Método Pago"
        ])
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ventas_table.horizontalHeader().setStretchLastSection(True)
        layout_principal.addWidget(self.ventas_table)

        # --- Tabla resumen ---
        self.tabla_reportes = QTableWidget(1, 3)
        self.tabla_reportes.setHorizontalHeaderLabels(["Cantidad de Ventas", "Total Vendido", "Ventas Anuladas"])
        self.tabla_reportes.verticalHeader().setVisible(False)
        self.tabla_reportes.setEditTriggers(QTableWidget.NoEditTriggers)
        layout_principal.addWidget(self.tabla_reportes)

        # --- Botones de acción ---
        botones_layout = QHBoxLayout()
        self.btn_nueva_venta = QPushButton("Nueva Venta")
        self.btn_anular_venta = QPushButton("Anular Venta")
        self.btn_imprimir = QPushButton("Imprimir")
        self.btn_exportar = QPushButton("Exportar Excel")

        botones_layout.addWidget(self.btn_nueva_venta)
        botones_layout.addWidget(self.btn_anular_venta)
        botones_layout.addWidget(self.btn_imprimir)
        botones_layout.addWidget(self.btn_exportar)

        self.btn_exportar.clicked.connect(self.exportar_excel)
        layout_principal.addLayout(botones_layout)

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
        self.tabla_reportes.setStyleSheet(estilo_tabla)

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
            self.ventas_table.setItem(row, 0, QTableWidgetItem(venta.get("codigo", "")))
            self.ventas_table.setItem(row, 1, QTableWidgetItem(venta.get("cliente", "")))
            self.ventas_table.setItem(row, 2, QTableWidgetItem(str(venta.get("fecha", ""))))
            self.ventas_table.setItem(row, 3, QTableWidgetItem(f"${venta.get('total', 0):,.2f}"))
            self.ventas_table.setItem(row, 4, QTableWidgetItem(venta.get("estado", "")))
            self.ventas_table.setItem(row, 5, QTableWidgetItem(venta.get("metodo_pago", "")))

            if venta.get("estado", "").lower() != "anulada":
                total_vendido += float(venta.get("total", 0))
            else:
                anuladas += 1

        # Actualizar tabla resumen
        self.tabla_reportes.setItem(0, 0, QTableWidgetItem(str(len(ventas))))
        self.tabla_reportes.setItem(0, 1, QTableWidgetItem(f"${total_vendido:,.2f}"))
        self.tabla_reportes.setItem(0, 2, QTableWidgetItem(str(anuladas)))

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
