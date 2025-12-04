"""
Script para generar embeddings de texto para productos y reseñas.
Usa sentence-transformers/all-MiniLM-L6-v2 (384 dimensiones).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Cargar variables de entorno
load_dotenv()

from sentence_transformers import SentenceTransformer
from config.mongodb_config import get_database

# Configuración
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
BATCH_SIZE = 32

def generate_text_embedding(text: str, model) -> list:
    """Genera embedding para un texto."""
    if not text or not text.strip():
        return None
    
    embedding = model.encode(text, show_progress_bar=False)
    return embedding.tolist()


def generate_product_embeddings():
    """Genera embeddings para descripciones de productos."""
    print("\n" + "="*80)
    print("🚀 GENERANDO EMBEDDINGS DE TEXTO PARA PRODUCTOS")
    print("="*80)
    
    # Cargar modelo
    print(f"\n📥 Cargando modelo: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✓ Modelo cargado correctamente")
    
    # Conectar a MongoDB
    db = get_database()
    productos_collection = db['productos']
    
    # Obtener productos sin embeddings o con descripciones actualizadas
    print("\n📊 Analizando productos...")
    productos = list(productos_collection.find({}))
    print(f"   Total de productos: {len(productos)}")
    
    # Filtrar productos que necesitan embeddings
    productos_sin_embedding = [
        p for p in productos 
        if not p.get('descripcion_embedding') and p.get('descripcion')
    ]
    
    print(f"   Productos sin embedding: {len(productos_sin_embedding)}")
    
    if not productos_sin_embedding:
        print("\n✅ Todos los productos ya tienen embeddings!")
        return
    
    # Generar embeddings
    print("\n🔄 Generando embeddings...")
    success_count = 0
    error_count = 0
    
    for producto in tqdm(productos_sin_embedding, desc="Procesando"):
        try:
            descripcion = producto.get('descripcion', '')
            
            if not descripcion:
                continue
            
            # Generar embedding
            embedding = generate_text_embedding(descripcion, model)
            
            if embedding:
                # Actualizar en BD
                productos_collection.update_one(
                    {'_id': producto['_id']},
                    {
                        '$set': {
                            'descripcion_embedding': embedding,
                            'embedding_model': EMBEDDING_MODEL_NAME,
                            'embedding_dimensions': len(embedding)
                        }
                    }
                )
                success_count += 1
            
        except Exception as e:
            print(f"\n   ⚠️ Error en producto {producto.get('codigoProducto', 'N/A')}: {e}")
            error_count += 1
    
    print(f"\n✅ Completado:")
    print(f"   ✓ Exitosos: {success_count}")
    print(f"   ✗ Errores: {error_count}")
    
    # Verificar
    total_con_embedding = productos_collection.count_documents({
        'descripcion_embedding': {'$exists': True}
    })
    print(f"\n🎯 Total de productos con embedding: {total_con_embedding}/{len(productos)}")


def generate_review_embeddings():
    """Genera embeddings para contenido de reseñas."""
    print("\n" + "="*80)
    print("🚀 GENERANDO EMBEDDINGS DE TEXTO PARA RESEÑAS")
    print("="*80)
    
    # Cargar modelo
    print(f"\n📥 Cargando modelo: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("✓ Modelo cargado correctamente")
    
    # Conectar a MongoDB
    db = get_database()
    resenas_collection = db['resenas']
    
    # Obtener reseñas sin embeddings
    print("\n📊 Analizando reseñas...")
    resenas = list(resenas_collection.find({}))
    print(f"   Total de reseñas: {len(resenas)}")
    
    # Filtrar reseñas que necesitan embeddings
    resenas_sin_embedding = [
        r for r in resenas 
        if not r.get('contenido_embedding') and r.get('contenido')
    ]
    
    print(f"   Reseñas sin embedding: {len(resenas_sin_embedding)}")
    
    if not resenas_sin_embedding:
        print("\n✅ Todas las reseñas ya tienen embeddings!")
        return
    
    # Generar embeddings
    print("\n🔄 Generando embeddings...")
    success_count = 0
    error_count = 0
    
    for resena in tqdm(resenas_sin_embedding, desc="Procesando"):
        try:
            contenido = resena.get('contenido', '')
            
            if not contenido:
                continue
            
            # Generar embedding
            embedding = generate_text_embedding(contenido, model)
            
            if embedding:
                # Actualizar en BD
                resenas_collection.update_one(
                    {'_id': resena['_id']},
                    {
                        '$set': {
                            'contenido_embedding': embedding,
                            'embedding_model': EMBEDDING_MODEL_NAME,
                            'embedding_dimensions': len(embedding)
                        }
                    }
                )
                success_count += 1
            
        except Exception as e:
            print(f"\n   ⚠️ Error en reseña: {e}")
            error_count += 1
    
    print(f"\n✅ Completado:")
    print(f"   ✓ Exitosos: {success_count}")
    print(f"   ✗ Errores: {error_count}")
    
    # Verificar
    total_con_embedding = resenas_collection.count_documents({
        'contenido_embedding': {'$exists': True}
    })
    print(f"\n🎯 Total de reseñas con embedding: {total_con_embedding}/{len(resenas)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 GENERADOR DE EMBEDDINGS DE TEXTO")
    print("   Modelo: sentence-transformers/all-MiniLM-L6-v2 (384 dims)")
    print("="*80)
    
    try:
        # Generar embeddings de productos
        generate_product_embeddings()
        
        # Generar embeddings de reseñas
        generate_review_embeddings()
        
        print("\n" + "="*80)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*80)
        print("\n💡 Ahora puedes ejecutar búsquedas RAG con análisis de texto!")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
