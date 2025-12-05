"""
Búsqueda vectorial completa para productos, reseñas e imágenes.
Extraído y adaptado del web_app.py existente.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from PIL import Image
import torch
import clip
import os
from config import get_database, COLLECTIONS, EMBEDDING_MODEL_NAME


# Singletons para modelos
_embedding_model = None
_clip_model = None
_clip_preprocess = None


def get_embedding_model():
    """Obtiene el modelo de embeddings de texto (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"📥 Cargando modelo de texto: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("✓ Modelo de texto cargado")
    return _embedding_model


def get_clip_model():
    """Obtiene el modelo CLIP para imágenes (singleton)."""
    global _clip_model, _clip_preprocess
    if _clip_model is None:
        print("📥 Cargando modelo CLIP para imágenes...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _clip_model, _clip_preprocess = clip.load("ViT-B/32", device=device)
        print("✓ Modelo CLIP cargado")
    return _clip_model, _clip_preprocess


def generate_text_embedding(text: str) -> List[float]:
    """
    Genera embedding para texto.
    
    Args:
        text: Texto de entrada
        
    Returns:
        Vector de embedding (384 dimensiones)
    """
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calcula similitud coseno entre dos vectores.
    
    Args:
        vec1: Primer vector
        vec2: Segundo vector
        
    Returns:
        Similitud entre 0 y 1
    """
    a = np.array(vec1)
    b = np.array(vec2)
    
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(np.dot(a, b) / (norm_a * norm_b))


def search_productos(
    query: str,
    limit: int = 10,
    min_score: float = 0.3,
    category_filter: Optional[str] = None,
    price_range: Optional[tuple] = None
) -> List[Dict[str, Any]]:
    """
    Búsqueda semántica de productos usando embeddings.
    
    Args:
        query: Consulta en lenguaje natural
        limit: Número máximo de resultados
        min_score: Score mínimo de similitud (0-1)
        category_filter: Filtro opcional por categoría
        price_range: Tupla (min_price, max_price) opcional
        
    Returns:
        Lista de productos ordenados por relevancia
    """
    db = get_database()
    collection = db[COLLECTIONS['PRODUCTOS']]
    
    print(f"\n🔍 Buscando productos: '{query}'")
    
    # Generar embedding de la consulta
    query_embedding = generate_text_embedding(query)
    
    # Construir filtros adicionales
    filters = {"descripcionEmbedding": {"$exists": True}}
    
    if category_filter:
        filters["idCategoria"] = category_filter
    
    if price_range:
        min_price, max_price = price_range
        filters["precioUsd"] = {}
        if min_price is not None:
            filters["precioUsd"]["$gte"] = min_price
        if max_price is not None:
            filters["precioUsd"]["$lte"] = max_price
    
    # Obtener productos
    productos = list(collection.find(
        filters,
        {
            "_id": 0,
            "idProducto": 1,
            "codigoProducto": 1,
            "nombre": 1,
            "descripcion": 1,
            "marca": 1,
            "precioUsd": 1,
            "calificacionPromedio": 1,
            "cantidadResenas": 1,
            "disponibilidad": 1,
            "descripcionEmbedding": 1
        }
    ))
    
    print(f"📊 Analizando {len(productos)} productos...")
    
    # Calcular similitud para cada producto
    resultados = []
    for prod in productos:
        if "descripcionEmbedding" in prod:
            similarity = cosine_similarity(query_embedding, prod["descripcionEmbedding"])
            
            if similarity >= min_score:
                # Eliminar embedding del resultado
                del prod["descripcionEmbedding"]
                prod["search_score"] = similarity
                resultados.append(prod)
    
    # Ordenar por similitud descendente
    resultados.sort(key=lambda x: x["search_score"], reverse=True)
    
    print(f"✓ Encontrados {len(resultados)} productos relevantes")
    
    return resultados[:limit]


def search_resenas(
    query: str,
    limit: int = 10,
    min_score: float = 0.3,
    verified_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Búsqueda semántica en reseñas.
    
    Args:
        query: Consulta en lenguaje natural
        limit: Número máximo de resultados
        min_score: Score mínimo de similitud
        verified_only: Solo compradores verificados
        
    Returns:
        Lista de reseñas ordenadas por relevancia
    """
    db = get_database()
    collection = db[COLLECTIONS['USUARIOS']]
    
    print(f"\n🔍 Buscando reseñas: '{query}'")
    query_embedding = generate_text_embedding(query)
    
    # Construir filtros
    filters = {"resenas": {"$exists": True, "$ne": []}}
    if verified_only:
        filters["compradorVerificado"] = True
    
    # Obtener usuarios con reseñas
    usuarios = list(collection.find(
        filters,
        {
            "_id": 0,
            "nombreUsuario": 1,
            "compradorVerificado": 1,
            "resenas": 1
        }
    ))
    
    # Procesar cada reseña
    resultados = []
    for usuario in usuarios:
        for resena in usuario.get("resenas", []):
            if "contenidoEmbedding" in resena:
                similarity = cosine_similarity(query_embedding, resena["contenidoEmbedding"])
                
                if similarity >= min_score:
                    # Eliminar embedding
                    del resena["contenidoEmbedding"]
                    
                    resultados.append({
                        "nombreUsuario": usuario["nombreUsuario"],
                        "compradorVerificado": usuario["compradorVerificado"],
                        "resena": resena,
                        "search_score": similarity
                    })
    
    # Ordenar por similitud
    resultados.sort(key=lambda x: x["search_score"], reverse=True)
    
    print(f"✓ Encontradas {len(resultados)} reseñas relevantes")
    
    return resultados[:limit]


def search_by_image(
    image_path: str,
    search_type: str = "productos",
    limit: int = 5,
    include_reviews: bool = True
) -> Dict[str, Any]:
    """
    Búsqueda por imagen usando CLIP.
    
    Args:
        image_path: Ruta a la imagen
        search_type: "productos" o "general"
        limit: Número de resultados
        include_reviews: Incluir reseñas relacionadas
        
    Returns:
        Diccionario con resultados y reseñas opcionales
    """
    try:
        # Cargar modelo CLIP
        clip_model, preprocess = get_clip_model()
        device = next(clip_model.parameters()).device
        
        # Procesar imagen
        if not os.path.exists(image_path):
            return {"error": f"Imagen no encontrada: {image_path}"}
        
        image = Image.open(image_path).convert('RGB')
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        
        # Generar embedding de imagen
        with torch.no_grad():
            image_embedding = clip_model.encode_image(image_tensor)
            image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)
            image_embedding = image_embedding.cpu().numpy().flatten().tolist()
        
        print(f"🖼️ Analizando imagen: {os.path.basename(image_path)}")
        
        # Buscar productos similares por imagen
        db = get_database()
        imagenes_col = db[COLLECTIONS['IMAGENES']]
        
        # Obtener todas las imágenes con embeddings
        imagenes = list(imagenes_col.find(
            {"clipEmbedding": {"$exists": True}},
            {
                "_id": 0,
                "idImagen": 1,
                "idProducto": 1,
                "rutaImagen": 1,
                "tipoImagen": 1,
                "clipEmbedding": 1
            }
        ))
        
        # Calcular similitudes
        resultados_imagenes = []
        for img in imagenes:
            if "clipEmbedding" in img:
                similarity = cosine_similarity(image_embedding, img["clipEmbedding"])
                if similarity > 0.1:  # Umbral bajo para imágenes
                    del img["clipEmbedding"]
                    img["similarity_score"] = similarity
                    resultados_imagenes.append(img)
        
        # Ordenar por similitud
        resultados_imagenes.sort(key=lambda x: x["similarity_score"], reverse=True)
        resultados_imagenes = resultados_imagenes[:limit]
        
        # Obtener información de productos
        productos_similares = []
        if resultados_imagenes:
            productos_ids = [img["idProducto"] for img in resultados_imagenes]
            productos_col = db[COLLECTIONS['PRODUCTOS']]
            
            productos = list(productos_col.find(
                {"idProducto": {"$in": productos_ids}},
                {
                    "_id": 0,
                    "idProducto": 1,
                    "nombre": 1,
                    "descripcion": 1,
                    "marca": 1,
                    "precioUsd": 1,
                    "calificacionPromedio": 1
                }
            ))
            
            # Combinar información
            productos_map = {p["idProducto"]: p for p in productos}
            for img in resultados_imagenes:
                if img["idProducto"] in productos_map:
                    producto_info = productos_map[img["idProducto"]].copy()
                    producto_info["imagen_similar"] = {
                        "rutaImagen": img["rutaImagen"],
                        "tipoImagen": img["tipoImagen"],
                        "similarity_score": img["similarity_score"]
                    }
                    productos_similares.append(producto_info)
        
        resultado = {
            "productos_similares": productos_similares,
            "total_encontrados": len(productos_similares)
        }
        
        # Incluir reseñas si se solicita
        if include_reviews and productos_similares:
            # Usar el primer producto para buscar reseñas relacionadas
            primer_producto = productos_similares[0]
            query_resenas = f"{primer_producto['nombre']} {primer_producto['marca']['nombre']}"
            reseñas_relacionadas = search_resenas(query_resenas, limit=3, min_score=0.2)
            resultado["resenas_relacionadas"] = reseñas_relacionadas
        
        print(f"✓ Encontrados {len(productos_similares)} productos similares por imagen")
        return resultado
        
    except Exception as e:
        print(f"❌ Error en búsqueda por imagen: {str(e)}")
        return {"error": str(e)}


def hybrid_search(
    text_query: Optional[str] = None,
    image_path: Optional[str] = None,
    filters: Optional[Dict] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Búsqueda híbrida combinando texto, imagen y filtros.
    
    Args:
        text_query: Consulta de texto opcional
        image_path: Ruta de imagen opcional  
        filters: Filtros adicionales
        limit: Número de resultados
        
    Returns:
        Resultados combinados
    """
    resultados = {
        "productos_texto": [],
        "productos_imagen": [],
        "productos_combinados": []
    }
    
    # Búsqueda por texto
    if text_query:
        resultados["productos_texto"] = search_productos(
            text_query, 
            limit=limit,
            category_filter=filters.get("category") if filters else None,
            price_range=filters.get("price_range") if filters else None
        )
    
    # Búsqueda por imagen
    if image_path:
        resultado_imagen = search_by_image(image_path, limit=limit)
        resultados["productos_imagen"] = resultado_imagen.get("productos_similares", [])
    
    # Combinar resultados si hay ambas búsquedas
    if text_query and image_path:
        ids_texto = {p["idProducto"] for p in resultados["productos_texto"]}
        ids_imagen = {p["idProducto"] for p in resultados["productos_imagen"]}
        
        # Productos que aparecen en ambas búsquedas (mayor relevancia)
        ids_comunes = ids_texto.intersection(ids_imagen)
        
        productos_combinados = []
        for producto in resultados["productos_texto"]:
            if producto["idProducto"] in ids_comunes:
                producto["relevancia"] = "alta"  # Aparece en texto e imagen
                productos_combinados.append(producto)
        
        # Agregar productos solo de texto
        for producto in resultados["productos_texto"]:
            if producto["idProducto"] not in ids_comunes:
                producto["relevancia"] = "texto"
                productos_combinados.append(producto)
        
        # Agregar productos solo de imagen
        for producto in resultados["productos_imagen"]:
            if producto["idProducto"] not in ids_texto:
                producto["relevancia"] = "imagen"
                productos_combinados.append(producto)
        
        resultados["productos_combinados"] = productos_combinados[:limit]
    
    return resultados


if __name__ == "__main__":
    # Pruebas básicas
    print("🧪 Pruebas del módulo de búsqueda")
    
    # Test 1: Búsqueda de productos
    print("\n1. Búsqueda de productos:")
    productos = search_productos("smartphone con buena cámara", limit=3)
    for i, p in enumerate(productos, 1):
        print(f"  {i}. {p['nombre']} - Score: {p['search_score']:.3f}")
    
    # Test 2: Búsqueda de reseñas  
    print("\n2. Búsqueda de reseñas:")
    resenas = search_resenas("batería dura mucho", limit=2)
    for i, r in enumerate(resenas, 1):
        print(f"  {i}. Usuario: {r['nombreUsuario']} - Score: {r['search_score']:.3f}")
        print(f"     {r['resena']['titulo'][:50]}...")