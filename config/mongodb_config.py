"""
Configuración y conexión a MongoDB Atlas.
"""

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def get_database():
    """
    Establece conexión con MongoDB Atlas y retorna el objeto de base de datos.
    
    Returns:
        Database: Objeto de base de datos de MongoDB
        
    Raises:
        ConnectionFailure: Si no se puede conectar a MongoDB
        ValueError: Si faltan variables de entorno
    """
    # Obtener URI de MongoDB desde variables de entorno
    mongo_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME", "productos_tecnologicos")
    
    if not mongo_uri:
        raise ValueError(
            "MONGODB_URI no está configurada. "
            "Por favor, configura el archivo .env con tu URI de MongoDB Atlas."
        )
    
    try:
        # Crear cliente de MongoDB con ServerApi para compatibilidad
        client = MongoClient(
            mongo_uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000
        )
        
        # Verificar conexión con ping
        client.admin.command('ping')
        
        print(f"✓ Conexión exitosa a MongoDB Atlas")
        print(f"✓ Base de datos: {database_name}")
        
        # Retornar objeto de base de datos
        db = client[database_name]
        return db
        
    except ServerSelectionTimeoutError:
        raise ConnectionFailure(
            "No se pudo conectar a MongoDB Atlas. "
            "Verifica tu conexión a internet y la URI de MongoDB."
        )
    except ConnectionFailure as e:
        raise ConnectionFailure(f"Error de conexión a MongoDB: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado al conectar a MongoDB: {str(e)}")


def verify_connection():
    """
    Verifica que la conexión a MongoDB esté funcionando correctamente.
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        db = get_database()
        # Intentar listar colecciones como prueba adicional
        collections = db.list_collection_names()
        print(f"✓ Verificación exitosa. Colecciones encontradas: {len(collections)}")
        return True
    except Exception as e:
        print(f"✗ Error en verificación: {str(e)}")
        return False


def get_collection(collection_name):
    """
    Obtiene una colección específica de la base de datos.
    
    Args:
        collection_name (str): Nombre de la colección
        
    Returns:
        Collection: Objeto de colección de MongoDB
    """
    db = get_database()
    return db[collection_name]


if __name__ == "__main__":
    # Prueba de conexión
    print("Probando conexión a MongoDB Atlas...")
    if verify_connection():
        print("✓ Todo funcionando correctamente")
    else:
        print("✗ Hay problemas con la conexión")
