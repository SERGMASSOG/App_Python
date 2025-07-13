from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_URI = "mongodb+srv://sergiomasso:FD3jyrrJA5IQXozg@cluster0.ztucv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Despliegue"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Colecciones
usuarios_col = db["usuarios"]
inventario_col = db["inventario"] 
ventas_col = db["ventas"]
crm_col = db["crm"]

def get_cliente_by_id(cliente_id):
    return crm_col.find_one({"id": cliente_id})

def get_all_clientes():
    return list(crm_col.find())

def insert_cliente(cliente):
    return crm_col.insert_one(cliente)

def update_cliente(cliente_id, nuevos_datos):
    return crm_col.update_one({"id": cliente_id}, {"$set": nuevos_datos})

def delete_cliente(cliente_id):
    return crm_col.delete_one({"id": cliente_id})

def get_productos_by_id_fecha(producto_id=None, fecha=None):
    from bson.objectid import ObjectId
    filtro = {}
    if producto_id:
        try:
            filtro["_id"] = ObjectId(producto_id)
        except Exception:
            return []
    if fecha:
        filtro["fecha"] = fecha
    return list(inventario_col.find(filtro))

def get_usuario_by_username(username):
    username = username.lower().strip()
    return usuarios_col.find_one({"usuario": username})

def get_all_inventario():
    return list(inventario_col.find())

def insert_producto(producto):
    return inventario_col.insert_one(producto)

def update_producto(producto_id, nuevos_datos):
    from bson.objectid import ObjectId
    return inventario_col.update_one({'_id': ObjectId(producto_id)}, {'$set': nuevos_datos})

def delete_producto(producto_id):
    from bson.objectid import ObjectId
    return inventario_col.delete_one({'_id': ObjectId(producto_id)})

def get_ventas(filtro=None):
    if filtro is None:
        filtro = {}
    return list(ventas_col.find(filtro))

def insert_venta(venta):
    return ventas_col.insert_one(venta)

if __name__ == "__main__":
    usuarios = list(usuarios_col.find())
    for doc in usuarios:
        print(doc)

