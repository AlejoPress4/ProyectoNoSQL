"""
Configuración de MongoDB para el proyecto RAG de Tecnología
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MongoDBConfig:
    """Clase para gestionar la configuración y conexión a MongoDB"""
    
    def __init__(self):
        # Verificar variables de entorno
        self.uri = os.getenv('MONGODB_URI')
        if not self.uri:
            print(" Error: MONGODB_URI no está configurado en el archivo .env")
            print(" Por favor, crea un archivo .env con la variable MONGODB_URI")
            print(" Ejemplo: MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/")
            sys.exit(1)
            
        self.db_name = os.getenv('MONGODB_DB_NAME', 'tech_rag_db')
        self.client = None
        self.db = None
        
    def connect(self, verbose=True):
        """Establecer conexión con MongoDB Atlas"""
        try:
            if verbose:
                print("\n Conectando a MongoDB Atlas...")
                print(f"   Base de datos: {self.db_name}")
                
            # Intentar conexión con timeout
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Verificar conexión con ping
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            
            if verbose:
                print(" Conexión exitosa a MongoDB Atlas")
            return self.db
            
        except ConnectionFailure as e:
            print(f"\n Error de conexión a MongoDB: {e}")
            print("\n Verifica:")
            print("   1. Tu conexión a internet")
            print("   2. El connection string en .env")
            print("   3. Usuario y contraseña correctos")
            print("   4. IP whitelisted en MongoDB Atlas")
            sys.exit(1)
            
        except ServerSelectionTimeoutError as e:
            print(f"\n Timeout al conectar con MongoDB: {e}")
            print("\n Posibles causas:")
            print("   1. Conexión a internet inestable")
            print("   2. Firewall bloqueando la conexión")
            print("   3. VPN interfiriendo")
            print("   4. MongoDB Atlas no responde")
            sys.exit(1)
            
        except Exception as e:
            print(f"\n Error inesperado: {e}")
            print("\n Verifica la configuración completa en .env")
            sys.exit(1)
    
    def get_collection(self, collection_name):
        """Obtener una colección específica"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            print(" Conexión cerrada")
    
    def test_connection(self):
        """Probar la conexión y mostrar diagnóstico completo"""
        try:
            print("\n🔍 DIAGNÓSTICO DE CONEXIÓN MONGODB")
            print("=" * 50)
            
            # 1. Probar conexión básica
            self.connect()
            
            # 2. Información del servidor
            server_info = self.client.server_info()
            print("\n Información del Servidor:")
            print(f"   • Versión MongoDB: {server_info.get('version', 'N/A')}")
            print(f"   • Tipo: MongoDB Atlas")
            
            # 3. Listar colecciones
            collections = self.db.list_collection_names()
            print(f"\n Colecciones en '{self.db_name}':")
            if collections:
                for col in collections:
                    count = self.db[col].estimated_document_count()
                    print(f"   • {col}: {count} documentos")
            else:
                print("   (No hay colecciones aún)")
                print("    Ejecuta: python scripts/01_setup_database.py")
            
            # 4. Estadísticas de la base de datos
            stats = self.db.command("dbStats")
            print(f"\n Estadísticas:")
            print(f"   • Tamaño total: {stats.get('dataSize', 0) / 1024:.2f} KB")
            print(f"   • Colecciones: {stats.get('collections', 0)}")
            print(f"   • Índices: {stats.get('indexes', 0)}")
            
            print("\n CONEXIÓN Y DIAGNÓSTICO EXITOSOS")
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"\n Error durante el diagnóstico: {e}")
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
