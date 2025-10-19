"""
Script 2: Crear índices en las colecciones
- Índices compuestos
- Índices de texto
- Índices multikey para arrays
- Preparación para índices vectoriales (se crean en Atlas UI)
"""

import sys
sys.path.append('..')

from config.db_config import get_db_config, COLLECTIONS
from pymongo import ASCENDING, DESCENDING, TEXT


def create_articles_indexes(db):
    """Crear índices para la colección 'articles'"""
    
    collection = db[COLLECTIONS['ARTICLES']]
    
    print(f"\n📊 Creando índices para '{COLLECTIONS['ARTICLES']}'...")
    
    # Índice compuesto: fecha + idioma (para queries híbridas)
    collection.create_index(
        [
            ("metadata.fecha_publicacion", DESCENDING),
            ("metadata.idioma", ASCENDING)
        ],
        name="idx_fecha_idioma"
    )
    print("  ✓ Índice compuesto: metadata.fecha_publicacion + metadata.idioma")
    
    # Índice simple: categoría
    collection.create_index(
        [("metadata.categoria", ASCENDING)],
        name="idx_categoria"
    )
    print("  ✓ Índice simple: metadata.categoria")
    
    # Índice multikey: tags
    collection.create_index(
        [("tags", ASCENDING)],
        name="idx_tags"
    )
    print("  ✓ Índice multikey: tags")
    
    # Índice de texto: título y contenido
    collection.create_index(
        [
            ("titulo", TEXT),
            ("contenido", TEXT)
        ],
        name="idx_text_search",
        default_language="spanish",
        weights={
            "titulo": 10,
            "contenido": 5
        }
    )
    print("  ✓ Índice de texto: titulo + contenido")
    
    # Índice simple: fecha de publicación (para ordenar)
    collection.create_index(
        [("metadata.fecha_publicacion", DESCENDING)],
        name="idx_fecha"
    )
    print("  ✓ Índice simple: metadata.fecha_publicacion")
    
    # Índice compuesto: categoría + dificultad
    collection.create_index(
        [
            ("metadata.categoria", ASCENDING),
            ("metadata.dificultad", ASCENDING)
        ],
        name="idx_categoria_dificultad"
    )
    print("  ✓ Índice compuesto: categoria + dificultad")


def create_images_indexes(db):
    """Crear índices para la colección 'images'"""
    
    collection = db[COLLECTIONS['IMAGES']]
    
    print(f"\n📊 Creando índices para '{COLLECTIONS['IMAGES']}'...")
    
    # Índice simple: tipo de imagen
    collection.create_index(
        [("metadata.tipo", ASCENDING)],
        name="idx_tipo"
    )
    print("  ✓ Índice simple: metadata.tipo")
    
    # Índice multikey: tags de imágenes
    collection.create_index(
        [("tags", ASCENDING)],
        name="idx_tags_img"
    )
    print("  ✓ Índice multikey: tags")
    
    # Índice simple: fecha de creación
    collection.create_index(
        [("fecha_creacion", DESCENDING)],
        name="idx_fecha_creacion"
    )
    print("  ✓ Índice simple: fecha_creacion")


def create_query_history_indexes(db):
    """Crear índices para la colección 'query_history'"""
    
    collection = db[COLLECTIONS['QUERY_HISTORY']]
    
    print(f"\n📊 Creando índices para '{COLLECTIONS['QUERY_HISTORY']}'...")
    
    # Índice simple: timestamp (para análisis temporal)
    collection.create_index(
        [("timestamp", DESCENDING)],
        name="idx_timestamp"
    )
    print("  ✓ Índice simple: timestamp")
    
    # Índice simple: tipo de query
    collection.create_index(
        [("query_type", ASCENDING)],
        name="idx_query_type"
    )
    print("  ✓ Índice simple: query_type")
    
    # Índice compuesto: timestamp + query_type
    collection.create_index(
        [
            ("timestamp", DESCENDING),
            ("query_type", ASCENDING)
        ],
        name="idx_timestamp_type"
    )
    print("  ✓ Índice compuesto: timestamp + query_type")


def list_all_indexes(db):
    """Listar todos los índices creados"""
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE ÍNDICES CREADOS")
    print("=" * 60)
    
    for collection_name in [COLLECTIONS['ARTICLES'], COLLECTIONS['IMAGES'], COLLECTIONS['QUERY_HISTORY']]:
        collection = db[collection_name]
        indexes = list(collection.list_indexes())
        
        print(f"\n📚 Colección: {collection_name}")
        print(f"   Total de índices: {len(indexes)}")
        
        for idx in indexes:
            name = idx.get('name', 'N/A')
            keys = idx.get('key', {})
            print(f"   - {name}: {keys}")


def print_vector_index_instructions():
    """Mostrar instrucciones para crear índices vectoriales en Atlas"""
    
    print("\n" + "=" * 60)
    print("🔍 ÍNDICES VECTORIALES (Crear manualmente en Atlas)")
    print("=" * 60)
    
    print("""
📌 IMPORTANTE: Los índices vectoriales deben crearse en la UI de MongoDB Atlas

Pasos para crear el índice vectorial de 'articles':
1. Ve a tu cluster en MongoDB Atlas
2. Haz clic en "Search" en el menú lateral
3. Click en "Create Search Index"
4. Selecciona "JSON Editor"
5. Pega la siguiente configuración:

{
  "name": "vector_index_articles",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "texto_embedding",
        "numDimensions": 384,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "metadata.idioma"
      },
      {
        "type": "filter",
        "path": "metadata.categoria"
      },
      {
        "type": "filter",
        "path": "metadata.fecha_publicacion"
      }
    ]
  }
}

---

Pasos para crear el índice vectorial de 'images':
Repite el proceso anterior con esta configuración:

{
  "name": "vector_index_images",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "image_embedding",
        "numDimensions": 512,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "metadata.tipo"
      }
    ]
  }
}

⏱️  Los índices vectoriales pueden tardar unos minutos en construirse.
""")


def main():
    """Ejecutar creación de índices"""
    print("=" * 60)
    print("🚀 CREACIÓN DE ÍNDICES")
    print("=" * 60)
    
    # Conectar a MongoDB
    config = get_db_config()
    db = config.connect()
    
    try:
        # Crear índices tradicionales
        create_articles_indexes(db)
        create_images_indexes(db)
        create_query_history_indexes(db)
        
        # Listar todos los índices
        list_all_indexes(db)
        
        # Mostrar instrucciones para índices vectoriales
        print_vector_index_instructions()
        
        print("\n" + "=" * 60)
        print("✅ ÍNDICES TRADICIONALES CREADOS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante la creación de índices: {e}")
    finally:
        config.close()


if __name__ == "__main__":
    main()
