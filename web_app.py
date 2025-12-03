"""
Aplicación web Flask para búsquedas semánticas de productos tecnológicos.
Endpoint: /ragtech para consultas en lenguaje natural.
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
from sentence_transformers import SentenceTransformer
from config import get_database, COLLECTIONS, EMBEDDING_MODEL_NAME
from pymongo import DESCENDING
import os

app = Flask(__name__)

# Variable global para el modelo de embeddings
_embedding_model = None


def get_embedding_model():
    """Carga el modelo de embeddings (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"📥 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"✓ Modelo cargado correctamente")
    return _embedding_model


def generate_embedding(text):
    """Genera embedding para un texto dado."""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def cosine_similarity(vec1, vec2):
    """Calcula la similitud coseno entre dos vectores."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    
    return dot_product / (norm_vec1 * norm_vec2)


def search_products(query, limit=10):
    """
    Busca productos usando búsqueda semántica con embeddings.
    
    Args:
        query (str): Consulta en lenguaje natural
        limit (int): Número máximo de resultados
        
    Returns:
        list: Lista de productos ordenados por relevancia
    """
    try:
        # Generar embedding de la consulta
        query_embedding = generate_embedding(query)
        
        # Conectar a la base de datos
        db = get_database()
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        # Obtener todos los productos con embeddings
        productos = list(productos_collection.find({
            "descripcionEmbedding": {"$exists": True, "$ne": []}
        }))
        
        # Normalizar consulta para coincidencias de palabras clave
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        # Calcular similitudes híbridas
        resultados = []
        for producto in productos:
            if "descripcionEmbedding" in producto and producto["descripcionEmbedding"]:
                # 1. Similitud semántica (embedding)
                semantic_similarity = cosine_similarity(query_embedding, producto["descripcionEmbedding"])
                
                # 2. Puntuación por coincidencia exacta de palabras clave
                keyword_score = 0
                text_fields = [
                    producto.get("nombre", "").lower(),
                    producto.get("descripcion", "").lower(),
                    str(producto.get("categoria", {}).get("nombre", "")).lower(),
                    str(producto.get("marca", {}).get("nombre", "")).lower()
                ]
                combined_text = " ".join(text_fields)
                
                # Puntuación por coincidencias exactas
                for word in query_words:
                    if word in combined_text:
                        keyword_score += 1
                
                # Normalizar keyword_score
                keyword_score = keyword_score / len(query_words) if query_words else 0
                
                # 3. Boost especial para coincidencias exactas en nombre o categoría
                exact_match_boost = 0
                if query_lower in producto.get("nombre", "").lower():
                    exact_match_boost = 0.3
                elif query_lower in str(producto.get("categoria", {}).get("nombre", "")).lower():
                    exact_match_boost = 0.25
                
                # 4. Combinar puntuaciones (pesos ajustados)
                # Semantic: 60%, Keywords: 30%, Exact Match: 10%
                hybrid_score = (
                    semantic_similarity * 0.6 + 
                    keyword_score * 0.3 + 
                    exact_match_boost
                )
                
                similarity = hybrid_score
                
                # Agregar información adicional
                producto_info = {
                    "id": str(producto.get("_id")),
                    "codigo_producto": producto.get("codigoProducto") or producto.get("codigo_producto", ""),
                    "nombre": producto.get("nombre", ""),
                    "descripcion": producto.get("descripcion", ""),
                    "marca": producto.get("marca", {}),
                    "categoria": producto.get("categoria", {}),
                    "precio_usd": (
                        producto.get("precioUsd") or 
                        producto.get("metadata", {}).get("precio_usd") or 
                        producto.get("precio_usd", 0)
                    ),
                    "calificacion": (
                        producto.get("calificacionPromedio") or 
                        producto.get("metadata", {}).get("calificacion_promedio") or 
                        producto.get("calificacion_promedio", 0)
                    ),
                    "disponibilidad": (
                        producto.get("disponibilidad") or 
                        producto.get("metadata", {}).get("disponibilidad", "")
                    ),
                    "imagen_principal": producto.get("imagen_principal", ""),
                    "similarity": round(similarity, 4),
                    "semantic_score": round(semantic_similarity, 4),
                    "keyword_score": round(keyword_score, 4),
                    "exact_match_boost": round(exact_match_boost, 4)
                }
                resultados.append(producto_info)
        
        # Ordenar por similitud descendente
        resultados.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Debug: mostrar top 5 resultados con puntuaciones
        print(f"🎯 Top 5 resultados para '{query}':")
        for i, producto in enumerate(resultados[:5]):
            print(f"{i+1}. {producto['nombre']} - Híbrido: {producto['similarity']:.3f} "
                  f"(Semántico: {producto['semantic_score']:.3f}, Keywords: {producto['keyword_score']:.3f}, "
                  f"Exacto: {producto['exact_match_boost']:.3f})")
        
        return resultados[:limit]
        
    except Exception as e:
        print(f"Error en búsqueda semántica: {str(e)}")
        return []


def search_reviews(query, limit=5):
    """
    Busca reseñas usando búsqueda semántica con embeddings.
    
    Args:
        query (str): Consulta en lenguaje natural
        limit (int): Número máximo de resultados
        
    Returns:
        list: Lista de reseñas ordenadas por relevancia
    """
    try:
        # Generar embedding de la consulta
        query_embedding = generate_embedding(query)
        
        # Conectar a la base de datos
        db = get_database()
        usuarios_collection = db[COLLECTIONS['USUARIOS']]
        
        # Obtener usuarios con reseñas que tengan embeddings
        usuarios = list(usuarios_collection.find({
            "resenas": {"$exists": True, "$ne": []}
        }))
        
        # Calcular similitudes para reseñas
        resultados = []
        for usuario in usuarios:
            if "resenas" in usuario:
                for resena in usuario["resenas"]:
                    if "contenidoEmbedding" in resena and resena["contenidoEmbedding"]:
                        similarity = cosine_similarity(query_embedding, resena["contenidoEmbedding"])
                        
                        resena_info = {
                            "usuario": usuario.get("nombreUsuario", ""),
                            "titulo": resena.get("titulo", ""),
                            "contenido": resena.get("contenido", ""),
                            "calificacion": resena.get("calificacion", 0),
                            "id_producto": str(resena.get("idProducto", resena.get("id_producto", ""))),
                            "compra_verificada": resena.get("compraVerificada", resena.get("compra_verificada", False)),
                            "similarity": round(similarity, 4)
                        }
                        resultados.append(resena_info)
        
        # Ordenar por similitud descendente
        resultados.sort(key=lambda x: x["similarity"], reverse=True)
        
        return resultados[:limit]
        
    except Exception as e:
        print(f"Error en búsqueda de reseñas: {str(e)}")
        return []


@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@app.route('/ragtech', methods=['GET', 'POST'])
def ragtech():
    """Endpoint principal para búsquedas semánticas."""
    if request.method == 'GET':
        return render_template('ragtech.html')
    
    elif request.method == 'POST':
        try:
            # Obtener consulta del request
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({"error": "Consulta requerida"}), 400
            
            query = data['query'].strip()
            if not query:
                return jsonify({"error": "Consulta vacía"}), 400
            
            limit = data.get('limit', 10)
            include_reviews = data.get('include_reviews', True)
            
            # Realizar búsqueda de productos
            productos = search_products(query, limit)
            
            # Realizar búsqueda de reseñas si se solicita
            resenas = []
            if include_reviews:
                resenas = search_reviews(query, 5)
            
            # Preparar respuesta
            response = {
                "query": query,
                "total_productos": len(productos),
                "total_resenas": len(resenas),
                "productos": productos,
                "resenas": resenas,
                "status": "success"
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({
                "error": f"Error interno del servidor: {str(e)}",
                "status": "error"
            }), 500


@app.route('/api/products')
def api_products():
    """API para obtener todos los productos."""
    try:
        db = get_database()
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        productos = list(productos_collection.find({}).limit(50))
        
        # Convertir ObjectId a string
        for producto in productos:
            producto["_id"] = str(producto["_id"])
        
        return jsonify({
            "productos": productos,
            "total": len(productos),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error al obtener productos: {str(e)}",
            "status": "error"
        }), 500


@app.route('/api/categories')
def api_categories():
    """API para obtener todas las categorías."""
    try:
        db = get_database()
        categorias_collection = db[COLLECTIONS['CATEGORIAS']]
        
        categorias = list(categorias_collection.find({}))
        
        # Convertir ObjectId a string
        for categoria in categorias:
            categoria["_id"] = str(categoria["_id"])
        
        return jsonify({
            "categorias": categorias,
            "total": len(categorias),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error al obtener categorías: {str(e)}",
            "status": "error"
        }), 500


@app.route('/api/stats')
def api_stats():
    """API para obtener estadísticas del sistema."""
    try:
        db = get_database()
        
        stats = {}
        for collection_name in COLLECTIONS.values():
            stats[collection_name] = db[collection_name].count_documents({})
        
        return jsonify({
            "estadisticas": stats,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error al obtener estadísticas: {str(e)}",
            "status": "error"
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 INICIANDO SERVIDOR WEB RAG TECH")
    print("="*60)
    print("📍 URL Principal: http://localhost:5000")
    print("🔍 Endpoint RAG: http://localhost:5000/ragtech")
    print("📊 API Productos: http://localhost:5000/api/products")
    print("📊 API Categorías: http://localhost:5000/api/categories")
    print("📊 API Stats: http://localhost:5000/api/stats")
    print("="*60 + "\n")
    
    # Crear directorio de templates si no existe
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Crear directorio static si no existe
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    app.run(debug=True, host='0.0.0.0', port=5000)