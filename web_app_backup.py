"""
Aplicación web Flask para búsquedas semánticas de productos tecnológicos.
Endpoint: /ragtech para consultas en lenguaje natural.
"""

from flask import Flask, render_template, request, jsonify
import numpy as np
# Importación lazy de sentence_transformers para evitar cuelgues
# from sentence_transformers import SentenceTransformer
from config import get_database, COLLECTIONS, EMBEDDING_MODEL_NAME
from pymongo import DESCENDING
# Importación lazy del RAG LLM
# from rag_llm import RAGLLMIntegrator
import os

app = Flask(__name__)

# Variable global para el modelo de embeddings
_embedding_model = None

# Variable global para el integrador RAG LLM
_rag_integrator = None


def get_embedding_model():
    """Carga el modelo de embeddings (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        try:
            print(f"📥 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print(f"✓ Modelo cargado correctamente")
        except Exception as e:
            print(f"❌ Error cargando modelo: {str(e)}")
            _embedding_model = None
            raise
    return _embedding_model


def get_rag_integrator():
    """Carga el integrador RAG LLM (singleton)."""
    global _rag_integrator
    if _rag_integrator is None:
        try:
            print("🤖 Inicializando integrador RAG LLM...")
            from rag_llm import RAGLLMIntegrator
            _rag_integrator = RAGLLMIntegrator(provider="groq", model="llama-3.1-8b-instant")
            print("✓ Integrador RAG inicializado")
        except Exception as e:
            print(f"❌ Error inicializando RAG: {str(e)}")
            _rag_integrator = None
            raise
    return _rag_integrator


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
    Busca productos usando búsqueda híbrida: semántica con embeddings + coincidencias exactas.
    
    Args:
        query (str): Consulta en lenguaje natural
        limit (int): Número máximo de resultados
        
    Returns:
        list: Lista de productos ordenados por relevancia híbrida
    """
    try:
        # Generar embedding de la consulta
        query_embedding = generate_embedding(query)
        
        # Conectar a la base de datos
        db = get_database()
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        # Obtener todos los productos con embeddings
        productos = list(productos_collection.find({}))
        
        # Filtrar productos que tengan embeddings válidos
        productos_con_embeddings = []
        for producto in productos:
            if "descripcionEmbedding" in producto and isinstance(producto["descripcionEmbedding"], list) and len(producto["descripcionEmbedding"]) > 0:
                productos_con_embeddings.append(producto)
        
        print(f"🔍 Encontrados {len(productos_con_embeddings)} productos con embeddings de {len(productos)} productos totales")
        
        # Normalizar consulta para coincidencias de palabras clave
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        
        # Calcular similitudes híbridas
        resultados = []
        for producto in productos_con_embeddings:
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
                    "similarity": round(semantic_similarity, 4),
                    "keyword_score": round(keyword_score, 4),
                    "exact_match_boost": round(exact_match_boost, 4),
                    "hybrid_score": round(hybrid_score, 4)
                }
                resultados.append(producto_info)
        
        # Ordenar por puntuación híbrida descendente
        resultados.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        # Debug: mostrar top 5 resultados con puntuaciones
        print(f"🎯 Top 5 resultados para '{query}':")
        for i, producto in enumerate(resultados[:5]):
            print(f"{i+1}. {producto['nombre']} - Híbrido: {producto['hybrid_score']:.3f} "
                  f"(Semántico: {producto['similarity']:.3f}, Keywords: {producto['keyword_score']:.3f}, "
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


@app.route('/rag-interface')
def rag_interface():
    """Interfaz del Pipeline RAG - REQUERIMIENTO DEL PROYECTO."""
    return render_template('rag_interface.html')


@app.route('/checklist')
def project_checklist():
    """Checklist de validación del proyecto."""
    return render_template('project_checklist.html')


@app.route('/academic-tests')
def academic_tests():
    """Interfaz de pruebas académicas para validación completa del proyecto."""
    return render_template('academic_tests.html')


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


@app.route('/rag', methods=['POST'])
def rag_endpoint():
    """
    Endpoint RAG principal - REQUERIMIENTO OBLIGATORIO DEL PROYECTO
    Genera respuestas contextualizadas usando recuperación semántica + LLM.
    """
    try:
        print("🤖 Iniciando pipeline RAG completo...")
        
        # Obtener consulta del request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Consulta requerida"}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({"error": "Consulta vacía"}), 400
        
        print(f"🔍 Query RAG: '{query}'")
        
        # Parámetros opcionales
        max_products = data.get('max_products', 5)
        max_reviews = data.get('max_reviews', 3)
        include_reviews = data.get('include_reviews', True)
        
        # 1. RECUPERACIÓN - Buscar contexto relevante usando vectores
        print("📚 Fase de Recuperación...")
        productos_contexto = search_products(query, limit=max_products)
        
        resenas_contexto = []
        if include_reviews:
            resenas_contexto = search_reviews(query, limit=max_reviews)
        
        print(f"✅ Contexto recuperado: {len(productos_contexto)} productos, {len(resenas_contexto)} reseñas")
        
        # 2. GENERACIÓN - Usar LLM para generar respuesta con contexto
        print("🧠 Fase de Generación con LLM...")
        context_data = {
            'productos': productos_contexto,
            'resenas': resenas_contexto
        }
        rag_response = get_rag_integrator().generate_rag_response(
            query=query,
            context=context_data
        )
        
        # 3. Respuesta completa RAG
        response = {
            "query": query,
            "rag_response": rag_response["response"],
            "sources": rag_response["sources"],
            "context": {
                "productos": productos_contexto,
                "resenas": resenas_contexto,
                "total_productos": len(productos_contexto),
                "total_resenas": len(resenas_contexto)
            },
            "metadata": {
                "model_used": rag_response["model_used"],
                "pipeline_stage": "complete_rag",
                "retrieval_method": "vector_similarity"
            },
            "status": "success"
        }
        
        print("✅ Pipeline RAG completado exitosamente")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error en pipeline RAG: {str(e)}")
        return jsonify({
            "error": f"Error en pipeline RAG: {str(e)}",
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


@app.route('/api/products/search')
def api_products_search():
    """API para búsquedas avanzadas de productos (para pruebas académicas)."""
    try:
        import time
        start_time = time.time()
        
        db = get_database()
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        # Obtener parámetros de consulta
        query = request.args.get('query', '')
        category = request.args.get('category', '')
        max_price = request.args.get('max_price')
        min_rating = request.args.get('min_rating')
        in_stock = request.args.get('in_stock')
        
        # Construir filtros MongoDB
        filtros = {}
        
        if category:
            filtros['categoria'] = {'$regex': category, '$options': 'i'}
        
        if max_price:
            try:
                filtros['precio'] = {'$lte': float(max_price)}
            except:
                pass
        
        if min_rating:
            try:
                filtros['calificacion_promedio'] = {'$gte': float(min_rating)}
            except:
                pass
        
        if in_stock and in_stock.lower() in ['true', '1', 'yes']:
            filtros['stock'] = {'$gt': 0}
        
        # Búsqueda textual si hay query
        if query:
            filtros['$or'] = [
                {'nombre': {'$regex': query, '$options': 'i'}},
                {'descripcion': {'$regex': query, '$options': 'i'}},
                {'marca.nombre': {'$regex': query, '$options': 'i'}},
                {'categoria': {'$regex': query, '$options': 'i'}}
            ]
        
        # Ejecutar búsqueda
        productos = list(productos_collection.find(filtros).limit(20))
        
        # Convertir ObjectId a string
        for producto in productos:
            producto["_id"] = str(producto["_id"])
        
        processing_time = round(time.time() - start_time, 3)
        
        return jsonify({
            "results": productos,
            "total": len(productos),
            "filters_applied": {
                "query": query,
                "category": category,
                "max_price": max_price,
                "min_rating": min_rating,
                "in_stock": in_stock
            },
            "processing_time": f"{processing_time}s",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error en búsqueda: {str(e)}",
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
        
        # Contar documentos en cada colección
        productos_count = db[COLLECTIONS['PRODUCTOS']].count_documents({})
        categorias_count = db[COLLECTIONS['CATEGORIAS']].count_documents({})
        marcas_count = db[COLLECTIONS['MARCAS']].count_documents({})
        usuarios_count = db[COLLECTIONS['USUARIOS']].count_documents({})
        
        # Contar reseñas (están dentro de los usuarios)
        pipeline = [
            {"$unwind": "$resenas"},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        resenas_result = list(db[COLLECTIONS['USUARIOS']].aggregate(pipeline))
        resenas_count = resenas_result[0]['count'] if resenas_result else 0
        
        stats = {
            "productos": productos_count,
            "categorias": categorias_count,
            "marcas": marcas_count,
            "usuarios": usuarios_count,
            "resenas": resenas_count
        }
        
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
    print("🤖 Pipeline RAG: http://localhost:5000/rag")
    print("="*60)
    
    # Verificar estado del integrador RAG (lazy loading)
    # rag_status = get_rag_integrator().health_check()
    # print(f"🤖 Estado RAG LLM: {rag_status['status']}")
    # print(f"🔧 Proveedor: {rag_status['provider']} | Modelo: {rag_status['model']}")
    # print(f"🔑 API Key: {'✅ Configurada' if rag_status['api_key_configured'] else '⚠️  No configurada (modo demo)'}")
    print("🤖 RAG LLM: Se cargará cuando sea necesario (lazy loading)")
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
        
        print(f"\n🤖 EJECUTANDO PIPELINE RAG")
        print(f"📝 Query: {query}")
        print(f"🎯 Parámetros: productos={max_products}, reseñas={max_reviews}, incluir_reseñas={include_reviews}")
        
        # Paso 1: Generar embedding de la consulta
        print("🔍 Generando embedding de consulta...")
        query_embedding = generate_embedding(query)
        
        # Paso 2: Buscar productos relevantes
        print("📱 Buscando productos relevantes...")
        db = get_database()
        products_collection = db[COLLECTIONS['productos']]
        
        productos_pipeline = [
            {
                '$addFields': {
                    'similarity': {
                        '$divide': [
                            {
                                '$reduce': {
                                    'input': {'$range': [0, {'$size': '$embedding'}]},
                                    'initialValue': 0,
                                    'in': {
                                        '$add': [
                                            '$$value',
                                            {
                                                '$multiply': [
                                                    {'$arrayElemAt': ['$embedding', '$$this']},
                                                    {'$arrayElemAt': [query_embedding, '$$this']}
                                                ]
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                '$multiply': [
                                    {'$sqrt': {
                                        '$reduce': {
                                            'input': '$embedding',
                                            'initialValue': 0,
                                            'in': {'$add': ['$$value', {'$multiply': ['$$this', '$$this']}]}
                                        }
                                    }},
                                    {'$sqrt': {
                                        '$reduce': {
                                            'input': query_embedding,
                                            'initialValue': 0,
                                            'in': {'$add': ['$$value', {'$multiply': ['$$this', '$$this']}]}
                                        }
                                    }}
                                ]
                            }
                        ]
                    }
                }
            },
            {'$sort': {'similarity': -1}},
            {'$limit': max_products}
        ]
        
        productos_result = list(products_collection.aggregate(productos_pipeline))
        print(f"✅ Encontrados {len(productos_result)} productos")
        
        # Paso 3: Buscar reseñas relevantes (si está habilitado)
        resenas_result = []
        if include_reviews:
            print("💬 Buscando reseñas relevantes...")
            reviews_collection = db[COLLECTIONS['resenas']]
            
            resenas_pipeline = [
                {
                    '$addFields': {
                        'similarity': {
                            '$divide': [
                                {
                                    '$reduce': {
                                        'input': {'$range': [0, {'$size': '$embedding'}]},
                                        'initialValue': 0,
                                        'in': {
                                            '$add': [
                                                '$$value',
                                                {
                                                    '$multiply': [
                                                        {'$arrayElemAt': ['$embedding', '$$this']},
                                                        {'$arrayElemAt': [query_embedding, '$$this']}
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                },
                                {
                                    '$multiply': [
                                        {'$sqrt': {
                                            '$reduce': {
                                                'input': '$embedding',
                                                'initialValue': 0,
                                                'in': {'$add': ['$$value', {'$multiply': ['$$this', '$$this']}]}
                                            }
                                        }},
                                        {'$sqrt': {
                                            '$reduce': {
                                                'input': query_embedding,
                                                'initialValue': 0,
                                                'in': {'$add': ['$$value', {'$multiply': ['$$this', '$$this']}]}
                                            }
                                        }}
                                    ]
                                }
                            ]
                        }
                    }
                },
                {'$sort': {'similarity': -1}},
                {'$limit': max_reviews}
            ]
            
            resenas_result = list(reviews_collection.aggregate(resenas_pipeline))
            print(f"✅ Encontradas {len(resenas_result)} reseñas")
        
        # Paso 4: Preparar contexto para el LLM
        print("📋 Preparando contexto...")
        context = {
            "total_productos": len(productos_result),
            "total_resenas": len(resenas_result),
            "productos": productos_result,
            "resenas": resenas_result
        }
        
        # Paso 5: Generar respuesta con LLM
        print("🧠 Generando respuesta con LLM...")
        rag_response = get_rag_integrator().generate_rag_response(query, context)
        
        # Paso 6: Preparar fuentes
        sources = []
        
        # Añadir productos como fuentes
        for producto in productos_result[:3]:  # Top 3 más relevantes
            sources.append({
                "type": "product",
                "name": producto.get('nombre', 'Producto sin nombre'),
                "similarity": float(producto.get('similarity', 0))
            })
        
        # Añadir reseñas como fuentes
        for resena in resenas_result[:3]:  # Top 3 más relevantes
            sources.append({
                "type": "review", 
                "user": resena.get('usuario', 'Usuario anónimo'),
                "similarity": float(resena.get('similarity', 0))
            })
        
        # Paso 7: Preparar respuesta final
        response = {
            "status": "success",
            "query": query,
            "rag_response": rag_response["response"],
            "context": context,
            "sources": sources,
            "metadata": {
                "model_used": get_rag_integrator().model_name,
                "provider": get_rag_integrator().provider,
                "tokens_used": rag_response.get("tokens_used", 0),
                "processing_time": rag_response.get("processing_time", 0)
            }
        }
        
        print(f"✅ Pipeline RAG completado exitosamente")
        print(f"🔤 Tokens usados: {response['metadata']['tokens_used']}")
        print(f"⏱️  Tiempo de procesamiento: {response['metadata']['processing_time']:.2f}s")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error en pipeline RAG: {str(e)}")
        return jsonify({
            "status": "error",
            "error": f"Error en pipeline RAG: {str(e)}"
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
    print("🤖 Pipeline RAG: http://localhost:5000/rag")
    print("="*60)
    
    # Verificar estado del integrador RAG (lazy loading)
    # rag_status = get_rag_integrator().health_check()
    # print(f"🤖 Estado RAG LLM: {rag_status['status']}")
    # print(f"🔧 Proveedor: {rag_status['provider']} | Modelo: {rag_status['model']}")
    # print(f"🔑 API Key: {'✅ Configurada' if rag_status['api_key_configured'] else '⚠️  No configurada (modo demo)'}")
    print("🤖 RAG LLM: Se cargará cuando sea necesario (lazy loading)")
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