"""
Configuración de MongoDB para el proyecto RAG de Tecnología
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MongoDBConfig:
    """Clase para gestionar la configuración y conexión a MongoDB"""
    
    def __init__(self):
        self.uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'tech_rag_db')
        self.client = None
        self.db = None
        
    def connect(self):
        """Establecer conexión con MongoDB Atlas"""
        try:
            print("🔄 Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            
            print(f"✅ Conexión exitosa a la base de datos: {self.db_name}")
            return self.db
            
        except ConnectionFailure as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            print(f"❌ Timeout al conectar con MongoDB: {e}")
            print("Verifica tu connection string y acceso a internet")
            raise
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Obtener una colección específica"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            print("🔒 Conexión cerrada")
    
    def test_connection(self):
        """Probar la conexión y listar colecciones"""
        try:
            self.connect()
            
            # Información del servidor
            server_info = self.client.server_info()
            print(f"\n📊 Información del Servidor:")
            print(f"   Versión de MongoDB: {server_info.get('version', 'N/A')}")
            
            # Listar colecciones
            collections = self.db.list_collection_names()
            print(f"\n📚 Colecciones en '{self.db_name}':")
            if collections:
                for col in collections:
                    count = self.db[col].estimated_document_count()
                    print(f"   - {col}: {count} documentos")
            else:
                print("   (No hay colecciones aún)")
            
            # Estadísticas
            stats = self.db.command("dbStats")
            print(f"\n💾 Estadísticas de la Base de Datos:")
            print(f"   Tamaño de datos: {stats.get('dataSize', 0) / 1024:.2f} KB")
            print(f"   Número de colecciones: {stats.get('collections', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al probar la conexión: {e}")
            return False
        finally:
            self.close()


# Constantes de colecciones
COLLECTIONS = {
    'ARTICLES': 'articles',
    'IMAGES': 'images',
    'QUERY_HISTORY': 'query_history'
}

# Instancia global (singleton)
_db_config = None

def get_db_config():
    """Obtener instancia singleton de la configuración"""
    global _db_config
    if _db_config is None:
        _db_config = MongoDBConfig()
    return _db_config


if __name__ == "__main__":
    # Test de conexión
    config = MongoDBConfig()
    config.test_connection()
