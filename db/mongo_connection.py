from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

# Configuración de la conexión
MONGO_URI = ""
DB_NAME = "Despliegue"

# Inicialización del cliente y la base de datos
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Forzar la conexión para verificar
    db = client[DB_NAME]
    
    # Colecciones
    usuarios_col = db["usuarios"]
    inventario_col = db["inventario"]
    ventas_col = db["ventas"]
    crm_col = db["clientes"]
    contabilidad_col = db["contabilidad"]
    transacciones_col = db["transacciones"]
    
    # Crear índices para mejorar el rendimiento
    try:
        # Primero, asegurarse de que no hay códigos nulos
        inventario_col.update_many(
            {"codigo": None},
            [{"$set": {"codigo": {"$toString": "$_id"}}}]  # Usar el _id como código temporal
        )
        
        # Luego crear el índice único
        inventario_col.create_index("codigo", unique=True, name="codigo_unico")
        
        # Índices para otras colecciones
        usuarios_col.create_index("usuario", unique=True, name="usuario_unico")
        crm_col.create_index("email", unique=True, name="email_unico")
        
    except Exception as e:
        print(f"Advertencia al crear índices: {e}")
        print("Continuando sin índices únicos...")
    
except Exception as e:
    print(f"Error al conectar con MongoDB: {e}")
    raise

def get_db_connection():
    """Retorna la conexión a la base de datos"""
    return db

# ===== MÉTODOS PARA CLIENTES (CRM) =====

def get_cliente_by_id(cliente_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un cliente por su ID"""
    try:
        if not ObjectId.is_valid(cliente_id):
            raise ValueError("ID de cliente no válido")
        return crm_col.find_one({"_id": ObjectId(cliente_id)})
    except Exception as e:
        print(f"Error al obtener cliente: {e}")
        return None

def get_all_clientes(filtro: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Obtiene todos los clientes con un filtro opcional"""
    try:
        return list(crm_col.find(filtro or {}))
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        return []

def insert_cliente(cliente: Dict[str, Any]) -> Optional[str]:
    """Inserta un nuevo cliente"""
    try:
        # Validar campos requeridos
        required_fields = ["nombre", "email", "telefono"]
        if not all(field in cliente for field in required_fields):
            raise ValueError(f"Campos requeridos faltantes: {required_fields}")
            
        # Verificar si el email ya existe
        if crm_col.find_one({"email": cliente["email"]}):
            raise ValueError("Ya existe un cliente con este email")
            
        cliente["fecha_creacion"] = datetime.utcnow()
        result = crm_col.insert_one(cliente)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error al insertar cliente: {e}")
        return None

def update_cliente(cliente_id: str, nuevos_datos: Dict[str, Any]) -> bool:
    """Actualiza los datos de un cliente"""
    try:
        if not ObjectId.is_valid(cliente_id):
            raise ValueError("ID de cliente no válido")
            
        # No permitir actualizar el _id
        nuevos_datos.pop("_id", None)
        nuevos_datos["fecha_actualizacion"] = datetime.utcnow()
        
        result = crm_col.update_one(
            {"_id": ObjectId(cliente_id)},
            {"$set": nuevos_datos}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar cliente: {e}")
        return False

def delete_cliente(cliente_id: str) -> bool:
    """Elimina un cliente por su ID"""
    try:
        if not ObjectId.is_valid(cliente_id):
            raise ValueError("ID de cliente no válido")
            
        result = crm_col.delete_one({"_id": ObjectId(cliente_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        return False

# ===== MÉTODOS PARA INVENTARIO =====

def get_producto_by_id(producto_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un producto por su ID"""
    try:
        if not ObjectId.is_valid(producto_id):
            raise ValueError("ID de producto no válido")
        return inventario_col.find_one({"_id": ObjectId(producto_id)})
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return None

def get_productos(filtro: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Obtiene productos con un filtro opcional"""
    try:
        return list(inventario_col.find(filtro or {}))
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []

def get_productos_by_codigo(codigo: str) -> List[Dict[str, Any]]:
    """Busca productos por código (búsqueda por coincidencia parcial)"""
    try:
        return list(inventario_col.find({"codigo": {"$regex": f".*{codigo}.*", "$options": "i"}}))
    except Exception as e:
        print(f"Error al buscar productos: {e}")
        return []

def insert_producto(producto: Dict[str, Any]) -> Optional[str]:
    """Inserta un nuevo producto"""
    try:
        # Validar campos requeridos
        required_fields = ["nombre", "precio", "stock"]
        if not all(field in producto for field in required_fields):
            raise ValueError(f"Campos requeridos faltantes: {required_fields}")
            
        # Validar tipos de datos
        if not isinstance(producto["precio"], (int, float)) or producto["precio"] <= 0:
            raise ValueError("El precio debe ser un número positivo")
            
        if not isinstance(producto["stock"], int) or producto["stock"] < 0:
            raise ValueError("El stock debe ser un número entero no negativo")
            
        producto["fecha_creacion"] = datetime.utcnow()
        result = inventario_col.insert_one(producto)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error al insertar producto: {e}")
        return None

def update_producto(producto_id: str, nuevos_datos: Dict[str, Any]) -> bool:
    """Actualiza un producto existente"""
    try:
        if not ObjectId.is_valid(producto_id):
            raise ValueError("ID de producto no válido")
            
        # No permitir actualizar el _id
        nuevos_datos.pop("_id", None)
        nuevos_datos["fecha_actualizacion"] = datetime.utcnow()
        
        result = inventario_col.update_one(
            {"_id": ObjectId(producto_id)},
            {"$set": nuevos_datos}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return False

def delete_producto(producto_id: str) -> bool:
    """Elimina un producto por su ID"""
    try:
        if not ObjectId.is_valid(producto_id):
            raise ValueError("ID de producto no válido")
            
        result = inventario_col.delete_one({"_id": ObjectId(producto_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return False

# ===== MÉTODOS PARA VENTAS =====

def get_venta_by_id(venta_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene una venta por su ID"""
    try:
        if not ObjectId.is_valid(venta_id):
            raise ValueError("ID de venta no válido")
        return ventas_col.find_one({"_id": ObjectId(venta_id)})
    except Exception as e:
        print(f"Error al obtener venta: {e}")
        return None

def get_ventas(filtro: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Obtiene ventas con un filtro opcional"""
    try:
        return list(ventas_col.find(filtro or {}).sort("fecha", -1))
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        return []

def insert_venta(venta: Dict[str, Any]) -> Optional[str]:
    """Inserta una nueva venta"""
    from bson import Decimal128
    
    try:
        # Validar campos requeridos
        required_fields = ["cliente_id", "productos", "total"]
        if not all(field in venta for field in required_fields):
            raise ValueError(f"Campos requeridos faltantes: {required_fields}")
            
        # Validar productos
        if not isinstance(venta["productos"], list) or not venta["productos"]:
            raise ValueError("La venta debe incluir al menos un producto")
            
        # Convertir total a Decimal128 para precisión monetaria
        venta["total"] = Decimal128(str(venta["total"]))
        
        # Agregar fechas
        venta["fecha"] = datetime.utcnow()
        venta["estado"] = "completada"
        
        # Iniciar transacción
        with client.start_session() as session:
            with session.start_transaction():
                # Verificar stock y actualizar inventario
                for producto in venta["productos"]:
                    producto_id = producto.get("producto_id")
                    cantidad = producto.get("cantidad", 0)
                    
                    if not producto_id or cantidad <= 0:
                        raise ValueError("Producto inválido en la venta")
                        
                    # Actualizar stock (usando $inc atómico)
                    result = inventario_col.update_one(
                        {"_id": ObjectId(producto_id), "stock": {"$gte": cantidad}},
                        {"$inc": {"stock": -cantidad}},
                        session=session
                    )
                    
                    if result.matched_count == 0:
                        raise ValueError(f"Producto {producto_id} sin stock suficiente o no encontrado")
                
                # Insertar la venta
                result = ventas_col.insert_one(venta, session=session)
                return str(result.inserted_id)
                
    except Exception as e:
        print(f"Error al procesar venta: {e}")
        return None

# ===== MÉTODOS PARA USUARIOS =====

def get_usuario_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su nombre de usuario"""
    try:
        return usuarios_col.find_one({"usuario": username.lower().strip()})
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

def get_usuario_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su nombre de usuario"""
    try:
        return usuarios_col.find_one({"correo": email.lower().strip()})
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

def verificar_credenciales(username: str, password: str):
    """Verifica las credenciales de un usuario"""
    try:
        usuario = usuarios_col.find_one({
            "usuario": username.lower().strip()
        })
        
        if usuario and usuario.get("contrasena") == password:  # En producción, usar hash
            # No devolver la contraseña
            usuario.pop("contrasena", None)
            return usuario
        return None
    except Exception as e:
        print(f"Error al verificar credenciales: {e}")
        return None

# Exportar las funciones principales
__all__ = [
    # Clientes
    'get_cliente_by_id',
    'get_all_clientes',
    'insert_cliente',
    'update_cliente',
    'delete_cliente',
    
    # Productos
    'get_producto_by_id',
    'get_productos',
    'get_productos_by_codigo',
    'insert_producto',
    'update_producto',
    'delete_producto',
    
    # Ventas
    'get_venta_by_id',
    'get_ventas',
    'insert_venta',
    
    # Usuarios
    'get_usuario_by_username',
    'verificar_credenciales',
    
    # Conexión
    'get_db_connection',
    
    # Colecciones (solo para uso interno)
    'db',
    'client',
    'usuarios_col',
    'inventario_col',
    'ventas_col',
    'crm_col'
]

if __name__ == "__main__":
    usuarios = list(usuarios_col.find())
    for doc in usuarios:
        print(doc)
