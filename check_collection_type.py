"""
Script para verificar el tipo de colección y convertir si es necesario
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def check_and_fix_collection():
    """Verificar tipo de colección y recrear si es time series"""
    try:
        # Conectar a MongoDB
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DATABASE_NAME', 'RAG')]
        
        print("\n🔍 VERIFICANDO COLECCIONES...")
        print("=" * 60)
        
        # Listar todas las colecciones con sus opciones
        collections = db.list_collections()
        
        for col_info in collections:
            col_name = col_info['name']
            col_type = col_info.get('type', 'collection')
            options = col_info.get('options', {})
            
            print(f"\n📦 Colección: {col_name}")
            print(f"   Tipo: {col_type}")
            
            if 'timeseries' in options:
                print(f"   ⚠️  ES TIME SERIES - NO PUEDE TENER VECTOR SEARCH")
                print(f"   Opciones: {options['timeseries']}")
                
                if col_name == 'productos':
                    print("\n" + "="*60)
                    print("⚠️  PROBLEMA ENCONTRADO")
                    print("="*60)
                    print("La colección 'productos' es de tipo Time Series.")
                    print("Los índices vectoriales NO son compatibles con Time Series.")
                    print("\n🔧 SOLUCIÓN:")
                    print("1. Necesitas recrear la colección como colección normal")
                    print("2. Migrar los datos de la colección actual a una nueva")
                    print("\n💡 ¿Quieres que te genere el script de migración? (y/n)")
            else:
                print(f"   ✅ Colección normal - compatible con Vector Search")
                
                # Contar documentos
                count = db[col_name].count_documents({})
                print(f"   Documentos: {count}")
                
                # Verificar embeddings si es productos o imagenesProducto
                if col_name == 'productos':
                    with_emb = db[col_name].count_documents({'descripcion_embedding': {'$exists': True}})
                    print(f"   Con descripcion_embedding: {with_emb}/{count}")
                elif col_name == 'imagenesProducto':
                    with_emb = db[col_name].count_documents({'imagen_embedding_clip': {'$exists': True}})
                    print(f"   Con imagen_embedding_clip: {with_emb}/{count}")
        
        print("\n" + "="*60)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_fix_collection()
