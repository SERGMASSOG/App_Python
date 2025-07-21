from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QFrame, QHeaderView, QGridLayout, QScrollArea, QSizePolicy, QStyle, QDialog
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Qt, QDate, QMargins, QRect, QSize, QDateTime
from PySide6.QtGui import QColor, QIcon, QFont, QPainter, QPixmap, QFontMetrics, QPdfWriter, QPageSize
from pymongo import MongoClient
from datetime import datetime
import csv
import os

class VentasManager(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Gestión de Ventas")
        self.setMinimumSize(1200, 800)
        
        # Paleta de colores basada en naranja
        self.COLOR_PRIMARIO = "#FF6B00"    # Naranja principal
        self.COLOR_SECUNDARIO = "#E05E00"  # Naranja oscuro
        self.COLOR_TERCIARIO = "#FF8C42"   # Naranja claro
        self.COLOR_EXITO = "#4CAF50"       # Verde para éxito
        self.COLOR_PELIGRO = "#F44336"     # Rojo para peligro
        self.COLOR_ADVERTENCIA = "#FF9800"  # Naranja para advertencia
        self.COLOR_TEXTO = "#2b2d42"       # Gris oscuro
        self.COLOR_FONDO = "#f8f9fa"       # Gris muy claro
        self.COLOR_BORDE = "#dee2e6"       # Gris claro
        
        self.setup_ui()
        self.aplicar_estilos()
        self.load_ventas()

    def setup_ui(self):
        """Interfaz moderna con mejor distribución visual"""
        self.setStyleSheet(f"background-color: {self.COLOR_FONDO};")
        
        # Layout principal con márgenes
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # =============== SECCIÓN SUPERIOR ===============
        top_section = QFrame()
        top_section.setObjectName("topSection")
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(30)
        
        # --- Panel de filtros ---
        filtros_panel = QFrame()
        filtros_panel.setObjectName("filtrosPanel")
        filtros_layout = QVBoxLayout(filtros_panel)
        filtros_layout.setContentsMargins(15, 15, 15, 15)
        filtros_layout.setSpacing(10)
        
        # Título del panel
        lbl_filtros = QLabel("Filtrar Ventas")
        lbl_filtros.setObjectName("panelTitle")
        filtros_layout.addWidget(lbl_filtros)
        
        # Filtros de fecha
        self.add_filtro_fecha(filtros_layout, "Desde:", QDate.currentDate().addMonths(-1))
        self.add_filtro_fecha(filtros_layout, "Hasta:", QDate.currentDate())
        
        # Botón de búsqueda con estilo naranja
        self.btn_buscar = QPushButton("Aplicar Filtros")
        self.btn_buscar.setObjectName("primaryButton")
        self.btn_buscar.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_buscar.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_PRIMARIO};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(self.COLOR_PRIMARIO, 15)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(self.COLOR_PRIMARIO, 25)};
            }}
        """)
        self.btn_buscar.clicked.connect(self.load_ventas)
        filtros_layout.addWidget(self.btn_buscar, alignment=Qt.AlignCenter)
        filtros_layout.addStretch()
        
        # --- Panel de acciones ---
        acciones_panel = QFrame()
        acciones_panel.setObjectName("accionesPanel")
        acciones_layout = QVBoxLayout(acciones_panel)
        acciones_layout.setContentsMargins(15, 15, 15, 15)
        acciones_layout.setSpacing(15)
        
        lbl_acciones = QLabel("Acciones")
        lbl_acciones.setObjectName("panelTitle")
        acciones_layout.addWidget(lbl_acciones)
        
        # Botones de acción en grid
        grid_buttons = QGridLayout()
        grid_buttons.setHorizontalSpacing(15)
        grid_buttons.setVerticalSpacing(10)
        
        # Usamos el naranja como color principal para los botones
        self.btn_nueva_venta = self.create_action_button("Nueva Venta", "list-add", self.COLOR_PRIMARIO)
        self.btn_anular_venta = self.create_action_button("Anular Venta", "edit-delete", self.COLOR_PELIGRO)
        self.btn_imprimir = self.create_action_button("Imprimir Ticket", "document-print", self.COLOR_ADVERTENCIA)
        self.btn_exportar = self.create_action_button("Exportar CSV", "document-save-as", self.COLOR_TERCIARIO)
        
        # Conectar botones a sus métodos
        self.btn_nueva_venta.clicked.connect(self.nueva_venta)
        self.btn_anular_venta.clicked.connect(self.anular_venta)
        self.btn_imprimir.clicked.connect(self.imprimir_ticket)
        self.btn_exportar.clicked.connect(self.exportar_excel)
        
        grid_buttons.addWidget(self.btn_nueva_venta, 0, 0)
        grid_buttons.addWidget(self.btn_anular_venta, 0, 1)
        grid_buttons.addWidget(self.btn_imprimir, 1, 0)
        grid_buttons.addWidget(self.btn_exportar, 1, 1)
        
        acciones_layout.addLayout(grid_buttons)
        acciones_layout.addStretch()
        
        # --- Panel de métricas ---
        metrics_panel = QFrame()
        metrics_panel.setObjectName("metricsPanel")
        metrics_layout = QVBoxLayout(metrics_panel)
        metrics_layout.setContentsMargins(15, 15, 15, 15)
        metrics_layout.setSpacing(15)
        
        lbl_metricas = QLabel("Resumen de Ventas")
        lbl_metricas.setObjectName("panelTitle")
        metrics_layout.addWidget(lbl_metricas)
        
        # Grid de métricas
        self.metrics = {}
        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(15)
        metrics_grid.setVerticalSpacing(15)
        
        # Usamos tonos de naranja para las métricas
        metricas = [
            ("total_ventas", "Total Ventas", self.COLOR_PRIMARIO),  # Naranja principal
            ("total_vendido", "Total Vendido", self.COLOR_TERCIARIO),  # Naranja claro
            ("ventas_anuladas", "Ventas Anuladas", self.COLOR_PELIGRO),  # Rojo
            ("ticket_promedio", "Ticket Promedio", self.COLOR_ADVERTENCIA),  # Naranja advertencia
        ]
        
        for idx, (key, titulo, color) in enumerate(metricas):
            self.metrics[key] = self.create_metric_card(titulo, "0", color)
            row, col = divmod(idx, 2)
            metrics_grid.addWidget(self.metrics[key], row, col)
        
        metrics_layout.addLayout(metrics_grid)
        metrics_layout.addStretch()
        
        # Organizar sección superior
        top_layout.addWidget(filtros_panel)
        top_layout.addWidget(acciones_panel)
        top_layout.addWidget(metrics_panel)
        
        # Asignar stretch factors para distribución proporcional
        top_layout.setStretch(0, 2)  # Filtros
        top_layout.setStretch(1, 2)  # Acciones
        top_layout.setStretch(2, 3)  # Métricas
        
        # =============== TABLA DE VENTAS ===============
        table_panel = QFrame()
        table_panel.setObjectName("tablePanel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_tabla = QLabel("Registro de Ventas")
        lbl_tabla.setObjectName("panelTitle")
        table_layout.addWidget(lbl_tabla)
        
        self.ventas_table = QTableWidget()
        self.ventas_table.setObjectName("ventasTable")
        self.ventas_table.setColumnCount(6)
        self.ventas_table.setHorizontalHeaderLabels([
            "Código", "Cliente", "Fecha", "Total", "Estado", "Método Pago"
        ])
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ventas_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Configurar header
        header = self.ventas_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignLeft)
        
        table_layout.addWidget(self.ventas_table)
        
        # Añadir todo al layout principal
        main_layout.addWidget(top_section)
        main_layout.addWidget(table_panel, stretch=1)

    def add_filtro_fecha(self, layout, label_text, default_date):
        """Añade un filtro de fecha al layout especificado"""
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(10)
        
        lbl = QLabel(label_text)
        lbl.setObjectName("filterLabel")
        date_edit = QDateEdit(calendarPopup=True)
        date_edit.setDate(default_date)
        date_edit.setObjectName("dateEdit")
        date_edit.setMinimumWidth(120)
        
        hbox.addWidget(lbl)
        hbox.addWidget(date_edit, stretch=1)
        
        layout.addLayout(hbox)
        
        # Guardar referencia
        if label_text == "Desde:":
            self.fecha_desde = date_edit
        else:
            self.fecha_hasta = date_edit

    def create_action_button(self, text, icon_name, color):
        """Crea un botón de acción con icono y color personalizado"""
        btn = QPushButton(text)
        btn.setObjectName("actionButton")
        
        # Usar iconos de tema o recursos incorporados
        if hasattr(QStyle, 'StandardPixmap'):
            # Para PySide6
            icon_mapping = {
                "list-add": QStyle.SP_FileIcon,
                "edit-delete": QStyle.SP_TrashIcon,
                "document-print": QStyle.SP_FileDialogContentsView,
                "document-save-as": QStyle.SP_DialogSaveButton,
                "view-refresh": QStyle.SP_BrowserReload
            }
            btn.setIcon(self.style().standardIcon(icon_mapping.get(icon_name, QStyle.SP_FileIcon)))
        else:
            # Fallback a iconos de tema
            btn.setIcon(QIcon.fromTheme(icon_name))
        
        # Usar el color naranja principal para todos los botones de acción
        btn_color = self.COLOR_PRIMARIO
        
        # Estilo dinámico basado en color
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 150px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 15)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 25)};
            }}
        """)
        
        return btn

    def create_metric_card(self, title, initial_value, color):
        card = QFrame()
        card.setObjectName("metricCard")
        card.setMinimumWidth(200)
        card.setMinimumHeight(100)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(5)
        
        # Título
        lbl_title = QLabel(title)
        lbl_title.setObjectName("metricTitle")
        
        # Valor - le asignamos un object name único
        lbl_value = QLabel(initial_value)
        lbl_value.setObjectName("metricValue")
        lbl_value.setStyleSheet(f"color: {color};")
        
        # Línea decorativa
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"border: 1px solid {self.COLOR_BORDE};")
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value, alignment=Qt.AlignCenter)
        card_layout.addWidget(line)
        
        # Guardamos referencia directa al label del valor
        card.value_label = lbl_value
        
        return card

    def darken_color(self, hex_color, percent):
        """Oscurece un color hexadecimal en un porcentaje dado"""
        color = QColor(hex_color)
        return color.darker(100 + percent).name()

    def aplicar_estilos(self):
        """Aplica estilos CSS modernos a todos los componentes"""
        self.setStyleSheet(f"""
            /* Estilos generales */
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
                color: {self.COLOR_TEXTO};
            }}
            
            /* Paneles */
            #topSection {{
                background-color: transparent;
            }}
            
            #filtrosPanel, #accionesPanel, #metricsPanel, #tablePanel {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid {self.COLOR_BORDE};
                padding: 5px;
            }}
            
            /* Títulos */
            #panelTitle {{
                font-size: 16px;
                font-weight: bold;
                color: {self.COLOR_SECUNDARIO};
                margin-bottom: 5px;
            }}
            
            /* Filtros */
            #filterLabel {{
                font-size: 14px;
                min-width: 50px;
            }}
            
            #dateEdit {{
                background-color: white;
                border: 1px solid {self.COLOR_BORDE};
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
            }}
            
            #dateEdit:hover {{
                border-color: {self.COLOR_PRIMARIO};
            }}
            
            /* Botón primario */
            #primaryButton {{
                background-color: {self.COLOR_PRIMARIO};
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            #primaryButton:hover {{
                background-color: {self.darken_color(self.COLOR_PRIMARIO, 15)};
            }}
            
            #primaryButton:pressed {{
                background-color: {self.darken_color(self.COLOR_PRIMARIO, 25)};
            }}
            
            /* Tarjetas de métricas */
            #metricCard {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid {self.COLOR_BORDE};
            }}
            
            #metricTitle {{
                font-size: 14px;
                color: {self.COLOR_TEXTO};
                font-weight: 500;
            }}
            
            #metricValue {{
                font-size: 24px;
                font-weight: bold;
                margin: 5px 0;
            }}
            
            /* Tabla */
            #ventasTable {{
                background-color: white;
                border: 1px solid {self.COLOR_BORDE};
                border-radius: 8px;
                font-size: 14px;
                gridline-color: {self.COLOR_BORDE};
                selection-background-color: {self.lighten_color(self.COLOR_PRIMARIO, 80)};
                selection-color: {self.COLOR_TEXTO};
            }}
            
            QHeaderView::section {{
                background-color: {self.COLOR_PRIMARIO};
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                font-size: 14px;
            }}
            
            QTableCornerButton::section {{
                background-color: {self.COLOR_PRIMARIO};
                border: none;
            }}
        """)

    def lighten_color(self, hex_color, percent):
        """Aclara un color hexadecimal en un porcentaje dado"""
        color = QColor(hex_color)
        return color.lighter(100 + percent).name()

    def update_metric_cards(self, total, vendido, anuladas):
        """Actualiza los valores de las tarjetas de métricas usando las referencias guardadas"""
        try:
            # Actualizamos usando las referencias directas
            self.metrics["total_ventas"].value_label.setText(str(total))
            self.metrics["total_vendido"].value_label.setText(f"${vendido:,.2f}")
            self.metrics["ventas_anuladas"].value_label.setText(str(anuladas))
            
            # Calcular ticket promedio
            ventas_validas = total - anuladas
            ticket = vendido / ventas_validas if ventas_validas > 0 else 0
            self.metrics["ticket_promedio"].value_label.setText(f"${ticket:,.2f}")
        except AttributeError as e:
            print(f"Error actualizando métricas: {e}")
            # Reconstruimos las tarjetas si hay error
            self.rebuild_metric_cards(total, vendido, anuladas)

    def nueva_venta(self):
        """Abre diálogo para registrar nueva venta"""
        try:
            from dialogs.venta_dialog import VentaDialog
            dialog = VentaDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos = dialog.obtener_datos()
                if not datos:
                    return
                    
                try:
                    # Formatear los datos de la venta
                    venta_data = {
                        'codigo': f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'cliente': datos.get('cliente', 'Cliente no especificado'),
                        'fecha': datetime.now(),
                        'total': float(datos.get('total', 0)),
                        'estado': 'Completada',
                        'metodo_pago': datos.get('metodo_pago', 'Efectivo'),
                        'productos': datos.get('productos', []),
                        'subtotal': float(datos.get('subtotal', 0)),
                        'impuestos': float(datos.get('impuestos', 0)),
                        'descuento': float(datos.get('descuento', 0))
                    }
                    
                    # Insertar en la base de datos
                    result = self.db["Ventas"].insert_one(venta_data)
                    
                    if result.inserted_id:
                        QMessageBox.information(self, "Éxito", "Venta registrada correctamente")
                        # Actualizar la tabla de ventas
                        self.load_ventas()
                        
                        # Actualizar el inventario
                        self.actualizar_inventario_venta(venta_data['productos'])
                    else:
                        QMessageBox.warning(self, "Advertencia", "No se pudo registrar la venta")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo registrar la venta: {str(e)}")
                    
        except ImportError as e:
            QMessageBox.critical(self, "Error", f"Error al importar el diálogo de venta: {str(e)}")
    
    def actualizar_inventario_venta(self, productos):
        """Actualiza el inventario después de una venta"""
        try:
            for producto in productos:
                self.db.inventario.update_one(
                    {'_id': producto['id_producto']},
                    {'$inc': {'stock_actual': -producto['cantidad']}}
                )
        except Exception as e:
            print(f"Error al actualizar inventario: {str(e)}")
            # No mostramos error al usuario para no interrumpir el flujo de venta

    def anular_venta(self):
        """Anula la venta seleccionada"""
        selected = self.ventas_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione una venta para anular")
            return
            
        row = selected[0].row()
        codigo = self.ventas_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Anular la venta {codigo}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db["Ventas"].update_one(
                    {"codigo": codigo}, 
                    {"$set": {"estado": "Anulada"}}
                )
                QMessageBox.information(self, "Éxito", "Venta anulada")
                self.load_ventas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo anular la venta: {str(e)}")

    def imprimir_ticket(self):
        """Muestra un diálogo para seleccionar y generar un ticket de venta"""
        try:
            # Obtener la venta seleccionada
            selected_rows = self.ventas_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "Advertencia", "Seleccione al menos una venta para generar el ticket")
                return

            # Si hay múltiples filas seleccionadas, pedir confirmación
            if len(selected_rows) > 1:
                reply = QMessageBox.question(
                    self, 
                    "Confirmar impresión múltiple", 
                    f"¿Desea generar {len(selected_rows)} tickets de venta?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply != QMessageBox.Yes:
                    return

            # Procesar cada venta seleccionada
            for row in selected_rows:
                row_index = row.row()
                self.generar_ticket_pdf(row_index)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el ticket: {str(e)}")

    def generar_ticket_pdf(self, row_index):
        """Genera un archivo PDF profesional para el ticket de la venta seleccionada"""
        try:
            # Obtener el código de la venta de la tabla
            codigo_venta = self.ventas_table.item(row_index, 0).text()
            
            # Obtener datos completos de la venta desde la base de datos
            venta = self.db.ventas.find_one({"codigo": codigo_venta})
            
            # Si no se encuentra por código, intentar por _id
            if not venta and len(codigo_venta) == 24:  # MongoDB _id tiene 24 caracteres
                try:
                    from bson import ObjectId
                    venta = self.db.ventas.find_one({"_id": ObjectId(codigo_venta)})
                except:
                    pass
            
            if not venta:
                QMessageBox.warning(self, "Error", f"No se encontraron los datos de la venta con código: {codigo_venta}")
                return
            
            # Obtener datos de la venta
            fecha_venta = venta.get('fecha', '')
            if isinstance(fecha_venta, str):
                try:
                    fecha_dt = datetime.fromisoformat(fecha_venta.replace('Z', '+00:00'))
                    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %H:%M")
                except:
                    fecha_formateada = "Fecha no disponible"
            else:
                fecha_formateada = fecha_venta.strftime("%d/%m/%Y %H:%M")
            
            # Obtener cliente
            cliente = venta.get('cliente', 'Cliente no especificado')
            if not cliente:
                cliente = 'Cliente no especificado'
            
            # Obtener método de pago
            metodo_pago = venta.get('metodo_pago', 'Efectivo')
            
            # Calcular totales
            subtotal = float(venta.get('subtotal', 0))
            impuestos = float(venta.get('impuestos', 0))
            descuento = float(venta.get('descuento', 0))
            total = float(venta.get('total', 0))
            
            # Obtener productos
            productos = venta.get('productos', [])
            
            # Verificar si la venta está anulada
            if venta.get('estado', '').lower() == 'anulada':
                QMessageBox.warning(self, "Venta Anulada", f"La venta {codigo_venta} está anulada y no se puede imprimir.")
                return

            # Configurar el PDF
            filename = f"factura_venta_{codigo_venta}.pdf".replace(" ", "_")
            pdf_writer = QPdfWriter(filename)
            pdf_writer.setPageSize(QPageSize(QPageSize.A4))
            pdf_writer.setTitle(f"Factura de Venta {codigo_venta}")
            
            painter = QPainter()
            if not painter.begin(pdf_writer):
                raise Exception("No se pudo iniciar el painter para el PDF")

            # Configuración de fuentes y colores
            font_titulo = QFont("Arial", 16, QFont.Bold)
            font_subtitulo = QFont("Arial", 10, QFont.Bold)
            font_normal = QFont("Arial", 9)
            font_negrita = QFont("Arial", 9, QFont.Bold)
            font_pie = QFont("Arial", 8)
            
            # Colores
            color_primario = QColor(255, 107, 0)  # Naranja
            color_secundario = QColor(64, 64, 64)  # Gris oscuro
            
            # Márgenes y dimensiones
            margin = 30
            width = pdf_writer.width() - 2 * margin
            y_pos = margin
            
            # Dibujar encabezado
            painter.setPen(color_primario)
            painter.setFont(font_titulo)
            
            # Logo de la empresa (si existe)
            logo_path = "assets/logo_empresa.png"  # Asegúrate de tener este archivo
            logo = QPixmap(logo_path)
            if not logo.isNull():
                logo = logo.scaled(120, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(margin, y_pos, logo)
                painter.drawText(QRect(margin + 140, y_pos, width - 140, 80), 
                              Qt.AlignLeft | Qt.AlignVCenter, 
                              "NOMBRE DE LA EMPRESA\nRUC: 12345678901\nDirección: Av. Principal 123\nTeléfono: (01) 123-4567")
            else:
                painter.drawText(QRect(margin, y_pos, width, 40), 
                              Qt.AlignLeft, 
                              "NOMBRE DE LA EMPRESA")
            
            y_pos += 100
            
            # Título del documento
            painter.setPen(color_secundario)
            painter.setFont(font_titulo)
            painter.drawText(QRect(margin, y_pos, width, 30), 
                          Qt.AlignCenter, "FACTURA DE VENTA")
            y_pos += 40
            
            # Información de la factura
            painter.setFont(font_negrita)
            painter.drawText(QRect(margin, y_pos, width/2, 20), 
                          Qt.AlignLeft, f"FACTURA N°: {codigo}")
            painter.drawText(QRect(width/2, y_pos, width/2, 20), 
                          Qt.AlignRight, f"FECHA: {venta.get('fecha', '')}")
            y_pos += 25
            
            # Datos del cliente
            painter.setPen(Qt.black)
            painter.setFont(font_negrita)
            painter.drawText(QRect(margin, y_pos, width, 20), 
                          Qt.AlignLeft, "DATOS DEL CLIENTE")
            y_pos += 20
            
            painter.setFont(font_normal)
            cliente_text = (
                f"Nombre: {venta.get('nombre_cliente', 'Cliente no especificado')}\n"
                f"Documento: {venta.get('id_cliente', 'No especificado')}\n"
                f"Método de pago: {venta.get('metodo_pago', 'No especificado')}"
            )
            
            # Crear un rectángulo con fondo gris claro para los datos del cliente
            rect_height = 60
            painter.fillRect(QRect(margin, y_pos, width, rect_height), QColor(245, 245, 245))
            painter.drawRect(QRect(margin, y_pos, width, rect_height))
            
            painter.drawText(QRect(margin + 10, y_pos + 10, width - 20, rect_height - 10), 
                          Qt.AlignLeft | Qt.TextWordWrap, cliente_text)
            y_pos += rect_height + 20
            
            # Tabla de productos
            painter.setFont(font_negrita)
            painter.drawText(QRect(margin, y_pos, width, 20), 
                          Qt.AlignLeft, "DETALLE DE PRODUCTOS")
            y_pos += 30
            
            # Encabezados de tabla
            headers = ["CÓDIGO", "DESCRIPCIÓN", "CANT.", "P. UNIT.", "IMPORTE"]
            col_widths = [width * 0.12, width * 0.38, width * 0.12, width * 0.18, width * 0.2]
            
            # Dibujar encabezado de la tabla
            painter.setPen(color_primario)
            painter.fillRect(QRect(margin, y_pos, width, 25), color_primario)
            painter.setPen(Qt.white)
            painter.setFont(font_subtitulo)
            
            for i, header in enumerate(headers):
                painter.drawText(QRectF(margin + sum(col_widths[:i]), y_pos, col_widths[i], 25), 
                              Qt.AlignCenter, header)
            
            y_pos += 25
            painter.setPen(Qt.black)
            
            # Obtener productos de la venta
            productos = venta.get('productos', [])
            subtotal = 0
            
            # Filas de productos
            for producto in productos:
                cantidad = float(producto.get('cantidad', 0))
                precio_unit = float(producto.get('precio', 0))
                importe = cantidad * precio_unit
                subtotal += importe
                
                # Alternar color de fondo para mejor legibilidad
                row_height = 25
                if y_pos % 50 < 25:  # Alternar cada dos filas
                    painter.fillRect(QRect(margin, y_pos, width, row_height), QColor(250, 250, 250))
                
                # Dibujar bordes de celda
                painter.setPen(QColor(200, 200, 200))
                for i in range(len(col_widths)):
                    x = margin + sum(col_widths[:i])
                    painter.drawRect(QRectF(x, y_pos, col_widths[i], row_height))
                
                # Dibujar contenido de la fila
                painter.setPen(Qt.black)
                painter.setFont(font_normal)
                
                # Código
                painter.drawText(QRectF(margin, y_pos, col_widths[0], row_height), 
                              Qt.AlignCenter | Qt.AlignVCenter, 
                              str(producto.get('codigo', '')))
                
                # Descripción
                painter.drawText(QRectF(margin + col_widths[0] + 5, y_pos + 2, 
                                     col_widths[1] - 10, row_height - 4), 
                              Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap, 
                              producto.get('descripcion', producto.get('nombre', 'Sin nombre')))
                
                # Cantidad
                painter.drawText(QRectF(margin + sum(col_widths[:2]), y_pos, 
                                     col_widths[2], row_height), 
                              Qt.AlignCenter | Qt.AlignVCenter, 
                              f"{cantidad:.2f}")
                
                # Precio Unitario
                painter.drawText(QRectF(margin + sum(col_widths[:3]), y_pos, 
                                     col_widths[3], row_height), 
                              Qt.AlignRight | Qt.AlignVCenter, 
                              f"S/ {precio_unit:.2f}")
                
                # Importe
                painter.setFont(font_negrita)
                painter.drawText(QRectF(margin + sum(col_widths[:4]), y_pos, 
                                     col_widths[4], row_height), 
                              Qt.AlignRight | Qt.AlignVCenter, 
                              f"S/ {importe:.2f}")
                
                y_pos += row_height
                
                # Verificar si necesitamos una nueva página
                if y_pos > pdf_writer.height() - 150:
                    self.agregar_pie_pagina(painter, margin, y_pos, width, font_pie)
                    pdf_writer.newPage()
                    y_pos = margin
                    
                    # Volver a dibujar el encabezado en la nueva página
                    painter.setFont(font_subtitulo)
                    painter.drawText(QRect(margin, y_pos, width, 20), 
                                  Qt.AlignLeft, "CONTINUACIÓN DE LA FACTURA")
                    y_pos += 30
                    
                    # Volver a dibujar los encabezados de la tabla
                    painter.setPen(color_primario)
                    painter.fillRect(QRect(margin, y_pos, width, 25), color_primario)
                    painter.setPen(Qt.white)
                    for i, header in enumerate(headers):
                        painter.drawText(QRectF(margin + sum(col_widths[:i]), y_pos, 
                                            col_widths[i], 25), 
                                      Qt.AlignCenter, header)
                    y_pos += 25
                    painter.setPen(Qt.black)
            
            # Línea divisoria
            painter.drawLine(margin, y_pos, margin + width, y_pos)
            y_pos += 10
            
            # Totales
            igv = subtotal * 0.18  # 18% de IGV
            total = subtotal + igv
            
            # Asegurar que haya suficiente espacio para los totales
            if y_pos > pdf_writer.height() - 100:
                self.agregar_pie_pagina(painter, margin, y_pos, width, font_pie)
                pdf_writer.newPage()
                y_pos = margin
            
            # Sección de totales alineada a la derecha
            total_width = width * 0.4
            start_x = margin + width - total_width
            
            # Fondo de la sección de totales
            painter.fillRect(QRectF(start_x - 10, y_pos, total_width + 10, 100), 
                          QColor(250, 250, 250))
            
            # Subtotal
            painter.setFont(font_negrita)
            painter.drawText(QRectF(start_x, y_pos, total_width - 20, 25), 
                          Qt.AlignRight, "Subtotal:")
            painter.drawText(QRectF(start_x, y_pos, total_width, 25), 
                          Qt.AlignRight, f"S/ {subtotal:.2f}")
            y_pos += 25
            
            # IGV (18%)
            painter.setFont(font_normal)
            painter.drawText(QRectF(start_x, y_pos, total_width - 20, 25), 
                          Qt.AlignRight, "IGV (18%):")
            painter.drawText(QRectF(start_x, y_pos, total_width, 25), 
                          Qt.AlignRight, f"S/ {igv:.2f}")
            y_pos += 25
            
            # Línea divisoria
            painter.drawLine(start_x, y_pos, start_x + total_width, y_pos)
            y_pos += 10
            
            # Total
            painter.setFont(font_titulo)
            painter.setPen(color_primario)
            painter.drawText(QRectF(start_x, y_pos, total_width - 20, 35), 
                          Qt.AlignRight, "TOTAL:")
            painter.drawText(QRectF(start_x, y_pos, total_width, 35), 
                          Qt.AlignRight, f"S/ {total:.2f}")
            painter.setPen(Qt.black)
            y_pos += 40
            
            # Método de pago
            painter.setFont(font_negrita)
            painter.drawText(QRectF(margin, y_pos, width, 20), 
                          Qt.AlignLeft, f"Método de pago: {venta.get('metodo_pago', 'No especificado').upper()}")
            y_pos += 30
            
            # Agregar pie de página
            self.agregar_pie_pagina(painter, margin, y_pos, width, font_pie)
            
            # Finalizar el documento
            painter.end()
            
            # Abrir el PDF generado
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el PDF: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def agregar_pie_pagina(self, painter, margin, y_pos, width, font):
        """Agrega un pie de página al documento"""
        painter.setFont(font)
        painter.setPen(Qt.gray)
        
        # Línea divisoria
        painter.drawLine(margin, y_pos, margin + width, y_pos)
        y_pos += 10
        
        # Texto del pie de página
        pie_texto = (
            "Gracias por su compra\n"
            "Este documento es una representación impresa de su factura electrónica.\n"
            "Para consultas o reclamos, comuníquese con nuestro servicio al cliente.\n"
            f"Documento generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        # Dibujar texto centrado
        painter.drawText(QRectF(margin, y_pos, width, 80), 
                       Qt.AlignCenter | Qt.TextWordWrap, pie_texto)
        
        # Agregar número de página si es necesario
        # (Puedes implementar la lógica de numeración de páginas si lo necesitas)
        return y_pos + 90
    
    def load_ventas(self):
        """Carga las ventas desde la base de datos y actualiza la interfaz"""
        try:
            # Obtener fechas del filtro
            fecha_ini = self.fecha_desde.date().toPython()
            fecha_fin = self.fecha_hasta.date().toPython()
            fecha_ini = datetime(fecha_ini.year, fecha_ini.month, fecha_ini.day, 0, 0, 0)
            fecha_fin = datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day, 23, 59, 59)

            # Consultar ventas en el rango de fechas
            ventas = list(self.db.ventas.find({
                "fecha": {
                    "$gte": fecha_ini.isoformat(),
                    "$lte": fecha_fin.isoformat()
                }
            }).sort("fecha", -1))

            self.ventas_table.setRowCount(0)
            total_vendido = 0
            anuladas = 0

            for venta in ventas:
                row = self.ventas_table.rowCount()
                self.ventas_table.insertRow(row)
                
                # Formatear la fecha
                fecha_venta = venta.get("fecha", venta.get("fecha_creacion", datetime.now()))
                if isinstance(fecha_venta, str):
                    try:
                        # Intentar parsear la fecha si es string
                        fecha_dt = datetime.fromisoformat(fecha_venta.replace('Z', '+00:00'))
                    except:
                        try:
                            fecha_dt = datetime.strptime(fecha_venta, "%Y-%m-%d %H:%M:%S")
                        except:
                            fecha_dt = datetime.now()
                else:
                    fecha_dt = fecha_venta
                
                fecha_formateada = fecha_dt.strftime("%Y-%m-%d %H:%M")
                
                # Obtener el estado de la venta
                estado = venta.get("estado", "completada").capitalize()
                
                # Obtener nombre del cliente (usar cadena vacía si es None o vacío)
                cliente = venta.get("cliente", "")
                if not cliente:
                    cliente = "Cliente no especificado"
                
                # Calcular el total de la venta
                total_venta = float(venta.get("total", 0))
                
                # Crear items para la tabla
                items = [
                    QTableWidgetItem(str(venta.get("codigo", ""))),
                    QTableWidgetItem(cliente),
                    QTableWidgetItem(fecha_formateada),
                    QTableWidgetItem(f"${total_venta:,.2f}"),
                    QTableWidgetItem(estado),
                    QTableWidgetItem(venta.get("metodo_pago", "Efectivo"))
                ]
                
                # Aplicar estilo si está anulada
                if estado.lower() == "anulada":
                    for item in items:
                        item.setForeground(QColor(self.COLOR_PELIGRO))
                    anuladas += 1
                else:
                    for item in items:
                        item.setForeground(QColor(self.COLOR_TEXTO))
                    total_vendido += total_venta
                
                # Añadir items a la tabla
                for col, item in enumerate(items):
                    self.ventas_table.setItem(row, col, item)

            # Actualizar métricas
            self.update_metric_cards(len(ventas), total_vendido, anuladas)
            
            # Ajustar columnas
            self.ventas_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error al cargar ventas: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al cargar las ventas: {str(e)}")

    def exportar_excel(self):
        """Exporta los datos a un archivo CSV"""
        try:
            path = "reporte_ventas.csv"
            with open(path, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo, delimiter=',')
                
                # Escribir encabezados
                headers = []
                for col in range(self.ventas_table.columnCount()):
                    headers.append(self.ventas_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Escribir datos
                for row in range(self.ventas_table.rowCount()):
                    fila = []
                    for col in range(self.ventas_table.columnCount()):
                        item = self.ventas_table.item(row, col)
                        fila.append(item.text() if item else "")
                    writer.writerow(fila)
                    
            QMessageBox.information(
                self, 
                "Exportación Exitosa", 
                f"Datos exportados correctamente a:\n{os.path.abspath(path)}"
            )
            
            # Abrir el archivo (solo en Windows)
            if os.name == 'nt':
                os.startfile(path)
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo exportar el archivo:\n{str(e)}"
            )

    def rebuild_metric_cards(self, total, vendido, anuladas):
        """Reconstruye las tarjetas de métricas si falla la actualización"""
        # Guardamos los valores actuales
        current_values = {
            "total_ventas": str(total),
            "total_vendido": f"${vendido:,.2f}",
            "ventas_anuladas": str(anuladas)
        }
        
        # Calculamos ticket promedio
        ventas_validas = total - anuladas
        ticket = vendido / ventas_validas if ventas_validas > 0 else 0
        current_values["ticket_promedio"] = f"${ticket:,.2f}"
        
        # Recreamos las tarjetas con la paleta de naranjas
        metricas = [
            ("total_ventas", "Total Ventas", self.COLOR_PRIMARIO),  # Naranja principal
            ("total_vendido", "Total Vendido", self.COLOR_TERCIARIO),  # Naranja claro
            ("ventas_anuladas", "Ventas Anuladas", self.COLOR_PELIGRO),  # Rojo
            ("ticket_promedio", "Ticket Promedio", self.COLOR_ADVERTENCIA),  # Naranja advertencia
        ]
        
        # Obtenemos el layout de métricas
        metrics_panel = self.metrics["total_ventas"].parent()
        metrics_layout = metrics_panel.layout()
        
        # Limpiamos el layout
        for i in reversed(range(metrics_layout.count())):
            metrics_layout.itemAt(i).widget().setParent(None)
        
        # Recreamos las tarjetas
        self.metrics = {}
        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(15)
        metrics_grid.setVerticalSpacing(15)
        
        for idx, (key, titulo, color) in enumerate(metricas):
            self.metrics[key] = self.create_metric_card(titulo, current_values[key], color)
            row, col = divmod(idx, 2)
            metrics_grid.addWidget(self.metrics[key], row, col)
        
        metrics_layout.addLayout(metrics_grid)