"""
Script para generar embeddings de imágenes usando CLIP (OpenAI)
y cargarlos a MongoDB Atlas para búsqueda vectorial.

Requisitos:
    pip install torch torchvision transformers pillow pymongo python-dotenv

Uso:
    python scripts/generate_image_embeddings_clip.py
"""

import os
import json
from pathlib import Path
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import numpy as np
from pymongo import MongoClient
from tqdm import tqdm
from datetime import datetime

# ==================== CONFIGURACIÓN ====================

# Modelo CLIP (512 dimensiones)
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"

# Directorio de imágenes
IMAGE_DIR = Path("data/images")

# MongoDB
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://baironvasquez16:duvier16042005@basenosql.r9oaz2u.mongodb.net/?retryWrites=true&w=majority&appName=BaseNoSQL"
)
DB_NAME = "ragtech_db"
COLLECTION_IMAGENES = "imagenesProducto"

# ==================== INICIALIZACIÓN ====================

print("🚀 Iniciando generación de embeddings con CLIP...")

# Device (GPU si está disponible)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"📱 Dispositivo: {device}")

# Cargar modelo CLIP
print(f"⏳ Cargando modelo CLIP: {CLIP_MODEL_NAME}...")
clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME).to(device)
clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
print("✅ Modelo CLIP cargado correctamente")

# Conectar a MongoDB
print(f"🔌 Conectando a MongoDB Atlas...")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
imagenes_collection = db[COLLECTION_IMAGENES]
print(f"✅ Conectado a BD: {DB_NAME}")

# ==================== FUNCIONES ====================

def embed_image_clip(pil_image):
    """
    Genera embedding de imagen usando CLIP (512 dimensiones).
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        numpy array de shape (512,) con el embedding normalizado
    """
    inputs = clip_processor(images=pil_image, return_tensors="pt")
    pixel_values = inputs["pixel_values"].to(device)
    
    with torch.no_grad():
        image_features = clip_model.get_image_features(pixel_values=pixel_values)
    
    # Normalizar (cosine similarity)
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
    
    return image_features.cpu().numpy()[0].astype("float32")


def embed_text_clip(text):
    """
    Genera embedding de texto usando CLIP (512 dimensiones).
    Útil para búsqueda multimodal imagen-texto.
    
    Args:
        text: string de texto
        
    Returns:
        numpy array de shape (512,) con el embedding normalizado
    """
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    
    with torch.no_grad():
        text_features = clip_model.get_text_features(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
    
    # Normalizar
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
    
    return text_features.cpu().numpy()[0].astype("float32")


def process_and_update_image(doc, image_path):
    """
    Procesa una imagen, genera embeddings (imagen + texto) y actualiza MongoDB.
    
    Args:
        doc: documento de MongoDB con metadata de imagen
        image_path: Path al archivo de imagen
        
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        # Cargar imagen
        pil_image = Image.open(image_path).convert("RGB")
        
        # Generar embedding de imagen
        image_embedding = embed_image_clip(pil_image)
        
        # Generar embedding de texto alternativo (para búsqueda híbrida)
        texto_alt = doc.get("texto_alternativo", "")
        text_embedding = None
        if texto_alt:
            text_embedding = embed_text_clip(texto_alt)
        
        # Actualizar documento en MongoDB
        update_data = {
            "imagen_embedding_clip": image_embedding.tolist(),
            "imagen_embedding_dimensions": 512,
            "embedding_model": CLIP_MODEL_NAME,
            "embedding_generated_at": datetime.utcnow(),
        }
        
        if text_embedding is not None:
            update_data["texto_embedding_clip"] = text_embedding.tolist()
        
        imagenes_collection.update_one(
            {"_id": doc["_id"]},
            {"$set": update_data}
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando {image_path.name}: {e}")
        return False


# ==================== PROCESAMIENTO PRINCIPAL ====================

def main():
    print("\n" + "="*60)
    print("GENERACIÓN DE EMBEDDINGS CLIP PARA IMÁGENES")
    print("="*60 + "\n")
    
    # Verificar directorio de imágenes
    if not IMAGE_DIR.exists():
        print(f"❌ Error: No existe el directorio {IMAGE_DIR}")
        return
    
    # Obtener todos los documentos de imágenes
    print("📊 Obteniendo metadatos de imágenes desde MongoDB...")
    total_docs = imagenes_collection.count_documents({})
    print(f"   Total de imágenes en BD: {total_docs}")
    
    # Contar cuántas ya tienen embeddings
    with_embeddings = imagenes_collection.count_documents(
        {"imagen_embedding_clip": {"$exists": True}}
    )
    print(f"   Con embeddings CLIP: {with_embeddings}")
    print(f"   Sin embeddings: {total_docs - with_embeddings}")
    
    # Preguntar si regenerar todos o solo los faltantes
    regenerar = input("\n¿Regenerar TODOS los embeddings? (s/N): ").strip().lower()
    
    if regenerar == 's':
        docs = list(imagenes_collection.find({}))
        print(f"\n🔄 Regenerando embeddings para {len(docs)} imágenes...")
    else:
        docs = list(imagenes_collection.find(
            {"imagen_embedding_clip": {"$exists": False}}
        ))
        print(f"\n🔄 Generando embeddings para {len(docs)} imágenes nuevas...")
    
    if not docs:
        print("✅ Todas las imágenes ya tienen embeddings CLIP!")
        return
    
    # Procesar cada imagen
    success_count = 0
    error_count = 0
    
    for doc in tqdm(docs, desc="Procesando imágenes"):
        url_imagen = doc.get("url_imagen", "")
        
        # Extraer nombre de archivo de la URL
        if url_imagen.startswith("/images/"):
            filename = url_imagen.replace("/images/", "")
        else:
            filename = Path(url_imagen).name
        
        image_path = IMAGE_DIR / filename
        
        if not image_path.exists():
            print(f"⚠️ Imagen no encontrada: {image_path}")
            error_count += 1
            continue
        
        if process_and_update_image(doc, image_path):
            success_count += 1
        else:
            error_count += 1
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE GENERACIÓN DE EMBEDDINGS")
    print("="*60)
    print(f"✅ Procesadas exitosamente: {success_count}")
    print(f"❌ Errores: {error_count}")
    print(f"📊 Total procesadas: {success_count + error_count}")
    
    # Verificar embeddings finales
    final_count = imagenes_collection.count_documents(
        {"imagen_embedding_clip": {"$exists": True}}
    )
    print(f"\n🎯 Imágenes con embeddings CLIP en BD: {final_count}/{total_docs}")
    
    print("\n" + "="*60)
    print("PRÓXIMOS PASOS:")
    print("="*60)
    print("1. Ve a MongoDB Atlas → Database → Browse Collections")
    print("2. Selecciona la colección 'imagenesProducto'")
    print("3. Ve a 'Search Indexes' → Create Search Index")
    print("4. Selecciona 'JSON Editor' y pega el contenido de:")
    print("   atlas_search_indexes/idx_imagen_vector_clip.json")
    print("5. Espera 5-10 minutos a que se construya el índice")
    print("6. Prueba la búsqueda por imágenes en la interfaz web!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
