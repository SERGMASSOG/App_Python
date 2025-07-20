from datetime import datetime
from db.mongo_connection import get_db_connection

class AccountingUtils:
    @staticmethod
    def record_sale_transaction(sale_data):
        """
        Registra una transacción de venta en contabilidad
        
        Args:
            sale_data (dict): Datos de la venta con la siguiente estructura:
                - total (float): Monto total de la venta
                - id_venta (str): ID de la venta
                - cliente (str): Nombre del cliente
                - productos (list): Lista de productos vendidos
        """
        try:
            db = get_db_connection()
            
            # Obtener la cuenta de ingresos por ventas (debería existir en la base de datos)
            cuenta_ventas = db.cuentas_contables.find_one({"codigo": "4.1.1"})  # Código de cuenta de ingresos por ventas
            if not cuenta_ventas:
                print("Error: No se encontró la cuenta de ingresos por ventas")
                return False
                
            # Crear transacción de ingreso por venta
            transaccion = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "ingreso",
                "descripcion": f"Venta a {sale_data.get('cliente', 'Cliente')}",
                "monto": float(sale_data['total']),
                "cuenta": cuenta_ventas['id'],
                "cuenta_nombre": cuenta_ventas['nombre'],
                "referencia": f"Venta-{sale_data.get('id_venta', '')}",
                "estado": "completada",
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": sale_data.get('usuario', 'Sistema')
            }
            
            # Registrar la transacción
            result = db.transacciones.insert_one(transaccion)
            
            # Actualizar saldo de la cuenta
            if result.inserted_id:
                db.cuentas_contables.update_one(
                    {"id": cuenta_ventas['id']},
                    {"$inc": {"saldo": float(sale_data['total'])}}
                )
                return True
            return False
            
        except Exception as e:
            print(f"Error al registrar transacción de venta: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

    @staticmethod
    def record_inventory_purchase(purchase_data):
        """
        Registra una transacción de compra de inventario en contabilidad
        
        Args:
            purchase_data (dict): Datos de la compra con la siguiente estructura:
                - total (float): Monto total de la compra
                - id_compra (str): ID de la compra
                - proveedor (str): Nombre del proveedor
                - productos (list): Lista de productos comprados
        """
        try:
            db = get_db_connection()
            
            # Obtener la cuenta de inventario (activo corriente)
            cuenta_inventario = db.cuentas_contables.find_one({"codigo": "1.1.3"})  # Código de cuenta de inventario
            if not cuenta_inventario:
                print("Error: No se encontró la cuenta de inventario")
                return False
                
            # Crear transacción de egreso por compra de inventario
            transaccion = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "tipo": "egreso",
                "descripcion": f"Compra de inventario a {purchase_data.get('proveedor', 'Proveedor')}",
                "monto": float(purchase_data['total']),
                "cuenta": cuenta_inventario['id'],
                "cuenta_nombre": cuenta_inventario['nombre'],
                "referencia": f"Compra-{purchase_data.get('id_compra', '')}",
                "estado": "completada",
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": purchase_data.get('usuario', 'Sistema')
            }
            
            # Registrar la transacción
            result = db.transacciones.insert_one(transaccion)
            
            # Actualizar saldo de la cuenta de inventario
            if result.inserted_id:
                db.cuentas_contables.update_one(
                    {"id": cuenta_inventario['id']},
                    {"$inc": {"saldo": float(purchase_data['total'])}}
                )
                return True
            return False
            
        except Exception as e:
            print(f"Error al registrar transacción de compra de inventario: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
