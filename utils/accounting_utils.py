from datetime import datetime
from db.mongo_connection import get_db_connection

class AccountingUtils:
    @staticmethod
    def record_sale_transaction(sale_data):
        """Registra una transacción de venta en contabilidad con validaciones mejoradas"""
        from bson.objectid import ObjectId
        
        # Validación básica de datos de entrada
        required_fields = ['total', 'id_venta', 'cliente', 'productos']
        if not all(field in sale_data for field in required_fields):
            print("Error: Faltan campos requeridos en sale_data")
            return False
        
        try:
            total = float(sale_data['total'])
            if total <= 0:
                print("Error: El total debe ser un valor positivo")
                return False
                
        except (ValueError, TypeError):
            print("Error: El total debe ser un número válido")
            return False

        session = None
        try:
            db = get_db_connection()
            
            # Configurar opciones de transacción
            transaction_options = {
                'maxCommitTimeMS': 5000,  # Timeout de 5 segundos
                'readConcern': {'level': 'snapshot'},
                'writeConcern': {'w': 'majority'}
            }
            
            with db.client.start_session() as session:
                session.start_transaction(**transaction_options)
                
                # Obtener o crear cuenta de ingresos
                cuenta_ventas = db.cuentas_contables.find_one(
                    {"codigo": "4.1.1"},
                    session=session
                )
                
                if not cuenta_ventas:
                    cuenta_data = {
                        "_id": str(ObjectId()),
                        "codigo": "4.1.1",
                        "nombre": "Ingresos por Ventas",
                        "tipo": "ingreso",
                        "nivel": 3,
                        "saldo": 0,
                        "fecha_creacion": datetime.now(),
                        "estado": "activa"
                    }
                    insert_result = db.cuentas_contables.insert_one(cuenta_data, session=session)
                    cuenta_ventas = db.cuentas_contables.find_one(
                        {"_id": insert_result.inserted_id},
                        session=session
                    )
                    print("Nueva cuenta de ingresos creada")
                
                # Crear transacción
                transaccion = {
                    "_id": str(ObjectId()),
                    "fecha": datetime.now(),
                    "tipo": "ingreso",
                    "descripcion": f"Venta a {sale_data['cliente']}",
                    "monto": total,
                    "cuenta": cuenta_ventas['_id'],
                    "cuenta_nombre": cuenta_ventas['nombre'],
                    "referencia": f"Venta-{sale_data['id_venta']}",
                    "detalle": [{
                        "producto": p.get('nombre', ''),
                        "cantidad": p.get('cantidad', 0),
                        "precio": p.get('precio_unitario', 0)
                    } for p in sale_data['productos']],
                    "estado": "completada",
                    "fecha_creacion": datetime.now(),
                    "usuario": sale_data.get('usuario', 'Sistema')
                }
                
                # Insertar transacción
                trans_result = db.transacciones.insert_one(transaccion, session=session)
                if not trans_result.inserted_id:
                    raise Exception("No se pudo insertar la transacción")
                
                # Actualizar saldo de cuenta
                update_result = db.cuentas_contables.update_one(
                    {"_id": cuenta_ventas['_id']},
                    {"$inc": {"saldo": total}},
                    session=session
                )
                if update_result.modified_count == 0:
                    raise Exception("No se pudo actualizar el saldo de la cuenta")
                
                session.commit_transaction()
                print(f"Transacción registrada exitosamente. ID: {trans_result.inserted_id}")
                return True
                
        except Exception as e:
            if session and session.in_transaction:
                session.abort_transaction()
            print(f"Error en record_sale_transaction: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def record_inventory_purchase(purchase_data):
        """Registra compra de inventario con manejo de transacciones"""
        from bson.objectid import ObjectId
        
        # Validación de datos
        required_fields = ['total', 'id_compra', 'proveedor', 'productos']
        if not all(field in purchase_data for field in required_fields):
            print("Error: Faltan campos requeridos en purchase_data")
            return False
        
        try:
            total = float(purchase_data['total'])
            if total <= 0:
                print("Error: El total debe ser positivo")
                return False
        except (ValueError, TypeError):
            print("Error: Total debe ser número válido")
            return False

        session = None
        try:
            db = get_db_connection()
            
            with db.client.start_session() as session:
                session.start_transaction()
                
                # Obtener cuenta de inventario
                cuenta_inventario = db.cuentas_contables.find_one(
                    {"codigo": "1.1.3"},
                    session=session
                )
                
                if not cuenta_inventario:
                    raise Exception("Cuenta de inventario no encontrada")
                
                # Crear transacción
                transaccion = {
                    "_id": str(ObjectId()),
                    "fecha": datetime.now(),
                    "tipo": "egreso",
                    "descripcion": f"Compra a {purchase_data['proveedor']}",
                    "monto": total,
                    "cuenta": cuenta_inventario['_id'],
                    "cuenta_nombre": cuenta_inventario['nombre'],
                    "referencia": f"Compra-{purchase_data['id_compra']}",
                    "detalle": [{
                        "producto": p.get('nombre', ''),
                        "cantidad": p.get('cantidad', 0),
                        "precio": p.get('precio_unitario', 0)
                    } for p in purchase_data['productos']],
                    "estado": "completada",
                    "fecha_creacion": datetime.now(),
                    "usuario": purchase_data.get('usuario', 'Sistema')
                }
                
                # Insertar transacción
                trans_result = db.transacciones.insert_one(transaccion, session=session)
                if not trans_result.inserted_id:
                    raise Exception("No se pudo insertar transacción")
                
                # Actualizar saldo
                update_result = db.cuentas_contables.update_one(
                    {"_id": cuenta_inventario['_id']},
                    {"$inc": {"saldo": total}},
                    session=session
                )
                if update_result.modified_count == 0:
                    raise Exception("No se pudo actualizar saldo")
                
                session.commit_transaction()
                print(f"Transacción de compra registrada. ID: {trans_result.inserted_id}")
                return True
                
        except Exception as e:
            if session and session.in_transaction:
                session.abort_transaction()
            print(f"Error en record_inventory_purchase: {str(e)}")
            import traceback
            traceback.print_exc()
            return False