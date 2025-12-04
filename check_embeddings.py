from config.mongodb_config import get_database

db = get_database()

print("=== VERIFICACIÓN DE EMBEDDINGS ===\n")

# Productos
count_all = db.productos.count_documents({})
count_emb = db.productos.count_documents({'descripcion_embedding': {'$exists': True}})
print(f"📦 Productos:")
print(f"   Total: {count_all}")
print(f"   Con descripcion_embedding: {count_emb}")

if count_emb > 0:
    sample = db.productos.find_one({'descripcion_embedding': {'$exists': True}})
    print(f"\n✓ Sample product:")
    print(f"   - nombre: {sample.get('nombre', 'N/A')}")
    print(f"   - descripcion: {sample.get('descripcion', 'N/A')[:80]}...")
    print(f"   - embedding_dimensions: {len(sample.get('descripcion_embedding', []))}")
    print(f"   - embedding_model: {sample.get('embedding_model', 'N/A')}")

# Imágenes
count_img = db.imagenesProducto.count_documents({})
count_clip = db.imagenesProducto.count_documents({'imagen_embedding_clip': {'$exists': True}})
print(f"\n🖼️ Imágenes:")
print(f"   Total: {count_img}")
print(f"   Con imagen_embedding_clip: {count_clip}")

print("\n" + "="*50)
