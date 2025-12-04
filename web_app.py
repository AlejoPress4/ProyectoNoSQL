"""
Aplicación web Flask para búsquedas semánticas de productos tecnológicos.
Endpoint: /ragtech para consultas en lenguaje natural.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from config import get_database, COLLECTIONS, EMBEDDING_MODEL_NAME
from pymongo import DESCENDING
import os
import io
from PIL import Image
from openai import OpenAI
import gridfs
from bson import ObjectId

app = Flask(__name__)
CORS(app)

@app.route('/images/<filename>')
def serve_image(filename):
    """Servir imágenes estáticas desde el directorio data/images."""
    images_dir = os.path.join(os.path.dirname(__file__), 'data', 'images')
    return send_from_directory(images_dir, filename)

# Variables globales para modelos de embeddings
_embedding_model = None
_clip_model = None
_clip_processor = None

# Cliente Groq (OpenAI API compatible)
_groq_client = None

def get_groq_client():
    """Obtiene el cliente de Groq (singleton)."""
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY no configurada. Agrega tu API key en el archivo .env")
        _groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        print("✓ Cliente Groq configurado")
    return _groq_client


def get_embedding_model():
    """Carga el modelo de embeddings de texto (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"📥 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"✓ Modelo cargado correctamente")
    return _embedding_model


def get_clip_model():
    """
    Carga el modelo CLIP para embeddings multimodales (singleton).
    Retorna (modelo, procesador, device).
    """
    global _clip_model, _clip_processor
    
    if _clip_model is None:
        try:
            print("📥 Cargando modelo CLIP para búsqueda de imágenes...")
            import torch
            from transformers import CLIPModel, CLIPProcessor
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_name = "openai/clip-vit-base-patch32"
            
            _clip_model = CLIPModel.from_pretrained(model_name).to(device)
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            
            print(f"✓ Modelo CLIP cargado correctamente (device: {device})")
            return _clip_model, _clip_processor, device
            
        except ImportError:
            print("⚠️ CLIP no disponible. Instala: pip install torch transformers")
            return None, None, None
    
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return _clip_model, _clip_processor, device


def generate_embedding(text):
    """Genera embedding de texto para búsqueda semántica (384 dims)."""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def generate_clip_text_embedding(text):
    """
    Genera embedding de texto usando CLIP (512 dims).
    Compatible con embeddings de imágenes CLIP.
    """
    clip_model, clip_processor, device = get_clip_model()
    
    if clip_model is None:
        print("⚠️ CLIP no disponible, usando modelo de texto estándar")
        return generate_embedding(text)
    
    import torch
    
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    
    with torch.no_grad():
        text_features = clip_model.get_text_features(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
    
    # Normalizar para cosine similarity
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
    
    return text_features.cpu().numpy()[0].astype("float32").tolist()


def generate_clip_image_embedding(pil_image):
    """
    Genera embedding de imagen usando CLIP (512 dims).
    Args:
        pil_image: PIL.Image object
    Returns:
        list: embedding de 512 dimensiones
    """
    clip_model, clip_processor, device = get_clip_model()
    
    if clip_model is None:
        raise ValueError("CLIP no está disponible. Instala: pip install torch transformers")
    
    import torch
    
    inputs = clip_processor(images=pil_image, return_tensors="pt")
    pixel_values = inputs["pixel_values"].to(device)
    
    with torch.no_grad():
        image_features = clip_model.get_image_features(pixel_values=pixel_values)
    
    # Normalizar para cosine similarity
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
    
    return image_features.cpu().numpy()[0].astype("float32").tolist()


def cosine_similarity(vec1, vec2):
    """
    Calcula la similitud coseno entre dos vectores.
    Usa sklearn para mayor eficiencia (como en el colab).
    """
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    
    # Usar sklearn (más rápido y preciso)
    similarity = sklearn_cosine_similarity(vec1, vec2)[0][0]
    return float(similarity)


def show_results(docs, fs):
    """
    Muestra resultados de búsqueda con scores y metadatos.
    Renderiza imágenes desde GridFS usando PIL.
    
    Args:
        docs: Lista de documentos con metadatos y referencias a imágenes
        fs: Instancia de GridFS para recuperar binarios de imágenes
    """
    results = []
    for d in docs:
        sc = d.get("score") or d.get("text_similarity") or d.get("hybrid_score")
        sc_str = f"{sc:.4f}" if isinstance(sc, (float, int)) else "N/A"
        
        result_info = {
            'title': d.get('nombre') or d.get('title'),
            'score': sc_str,
            'category': d.get('categoria_nombre') or d.get('category'),
            'tags': d.get('tags'),
            'caption': d.get('descripcion') or d.get('caption')
        }
        
        print(f"🔎 {result_info['title']} | score={sc_str} | cat={result_info['category']} | tags={result_info['tags']}")
        
        # Intentar mostrar imagen desde GridFS
        fid = d.get("image_file_id") or d.get("archivo_id")
        if fid and fs:
            try:
                if isinstance(fid, str):
                    fid = ObjectId(fid)
                data = fs.get(fid).read()
                img = Image.open(io.BytesIO(data))
                result_info['image'] = img
                print(f"  📷 Imagen cargada: {img.size} px")
            except Exception as e:
                print(f"  ⚠️ No se pudo mostrar imagen: {e}")
                result_info['image'] = None
        
        results.append(result_info)
    
    return results


def update_caption_by_title(db, title, new_caption):
    """
    Actualiza el caption/descripción de un documento por título.
    
    Args:
        db: Base de datos MongoDB
        title: Título del documento a actualizar
        new_caption: Nuevo caption/descripción
    """
    result = db[COLLECTIONS['imagenes']].update_one(
        {"nombre": title},
        {"$set": {"descripcion": new_caption}}
    )
    if result.modified_count > 0:
        print(f"✏️ Caption actualizado para: {title}")
        return True
    else:
        print(f"⚠️ No se encontró documento con título: {title}")
        return False


def delete_by_title(db, fs, title):
    """
    Elimina un documento y su imagen asociada en GridFS por título.
    
    Args:
        db: Base de datos MongoDB
        fs: Instancia de GridFS
        title: Título del documento a eliminar
    """
    doc = db[COLLECTIONS['imagenes']].find_one({"nombre": title})
    if not doc:
        print(f"⚠️ No existe documento con título: {title}")
        return False
    
    fid = doc.get("archivo_id")
    if fid:
        try:
            if isinstance(fid, str):
                fid = ObjectId(fid)
            fs.delete(fid)
            print(f"🗑️ Archivo GridFS eliminado: {fid}")
        except Exception as e:
            print(f"⚠️ Advertencia al eliminar binario: {e}")
    
    db[COLLECTIONS['imagenes']].delete_one({"_id": doc["_id"]})
    print(f"🗑️ Documento eliminado: {title}")
    return True


def generate_answer_with_llm(context, question, model="llama-3.1-8b-instant"):
    """
    Genera respuesta usando Groq LLM basándose en contexto recuperado.
    
    Args:
        context: Contexto textual con información recuperada
        question: Pregunta del usuario
        model: Modelo de Groq a utilizar
    
    Returns:
        str: Respuesta generada por el LLM
    """
    try:
        client = get_groq_client()
        
        system_prompt = (
            "Eres un asistente experto en búsqueda semántica y recuperación de información multimodal. "
            "Respondes de forma clara, directa y con base solo en el contexto entregado. "
            "Eres especialista en productos tecnológicos y ayudas a los usuarios a encontrar el mejor producto para sus necesidades."
        )
        
        full_prompt = f"""[Contexto recuperado]
{context}

[PREGUNTA]
{question}

[INSTRUCCIONES]
Con base únicamente en el contexto anterior, responde de manera clara y completa.
Incluye:
- Recomendaciones específicas de productos con sus características clave
- Ventajas y desventajas relevantes
- Comparaciones si hay múltiples opciones
- Precio y relación calidad-precio

Si el contexto no contiene información suficiente, dilo explícitamente.
Responde en español de manera profesional pero amigable.
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"⚠️ Error al invocar Groq LLM: {e}")
        return f"[Error al generar respuesta con LLM: {e}]"


def build_context_for_llm_from_products(productos, max_items=6):
    """
    Construye contexto textual a partir de productos recuperados.
    
    Args:
        productos: Lista de productos con metadatos
        max_items: Número máximo de productos a incluir
    
    Returns:
        str: Contexto formateado para el LLM
    """
    lines = []
    for i, p in enumerate(productos[:max_items], 1):
        nombre = p.get('nombre', 'Sin nombre')
        marca = p.get('marca_nombre', 'N/A')
        precio = p.get('precio_usd', 0)
        categoria = p.get('categoria_nombre', 'N/A')
        descripcion = p.get('descripcion', 'N/A')
        
        # Scores de similitud
        text_score = p.get('text_similarity', 0)
        image_score = p.get('image_similarity', 0)
        hybrid_score = p.get('hybrid_score', 0)
        
        # Especificaciones
        specs = p.get('especificaciones', {})
        specs_str = ', '.join([f"{k}: {v}" for k, v in specs.items()]) if specs else 'N/A'
        
        # Reseñas (ventajas/desventajas)
        ventajas = p.get('ventajas', [])
        desventajas = p.get('desventajas', [])
        ventajas_str = '\n    + ' + '\n    + '.join(ventajas[:3]) if ventajas else ''
        desventajas_str = '\n    - ' + '\n    - '.join(desventajas[:3]) if desventajas else ''
        
        lines.append(f"""[PRODUCTO {i}]
Nombre: {nombre}
Marca: {marca}
Precio: ${precio:.2f} USD
Categoría: {categoria}
Descripción: {descripcion}
Especificaciones: {specs_str}
Relevancia: Text={text_score:.1f}%, Image={image_score:.1f}%, Hybrid={hybrid_score:.1f}%{ventajas_str}{desventajas_str}
""")
    
    return "\n".join(lines)


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
    return render_template('ragtech.html')


@app.route('/academic')
def academic():
    """Página de pruebas académicas."""
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


@app.route('/api/products/search', methods=['GET'])
def api_products_search():
    """
    API para búsqueda semántica de productos usando Atlas Vector Search.
    Combina búsqueda vectorial con filtros tradicionales (híbrido).
    """
    try:
        query = request.args.get('query', '').strip()
        category = request.args.get('category', '').strip()
        max_price = request.args.get('max_price', type=float)
        brand = request.args.get('brand', '').strip()
        limit = request.args.get('limit', default=10, type=int)
        
        if not query:
            return jsonify({
                'error': 'El parámetro query es requerido',
                'results': []
            }), 400
        
        print(f"🔍 VECTOR SEARCH: '{query}' | Cat: {category or 'todas'} | $max: {max_price or '∞'} | Marca: {brand or 'todas'}")
        
        # Generar embedding de la consulta
        query_embedding = generate_embedding(query)
        
        # Obtener base de datos
        db = get_database()
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        # Construir pipeline de agregación con $vectorSearch
        pipeline = [
            {
                '$vectorSearch': {
                    'index': 'idx_descripcion_vector',  # Índice vectorial en MongoDB Atlas
                    'path': 'descripcion_embedding',
                    'queryVector': query_embedding,
                    'numCandidates': limit * 10,  # Candidatos a evaluar
                    'limit': limit * 3  # Obtener más para aplicar filtros
                }
            },
            {
                '$addFields': {
                    'similarity_score': {'$meta': 'vectorSearchScore'}
                }
            }
        ]
        
        # Agregar filtros tradicionales (búsqueda híbrida)
        filtros = []
        if category:
            filtros.append({'categoria.slug': category})
        if max_price:
            filtros.append({'metadata.precio_usd': {'$lte': max_price}})
        if brand:
            filtros.append({'marca.nombre': {'$regex': brand, '$options': 'i'}})
        
        if filtros:
            pipeline.append({
                '$match': {'$and': filtros}
            })
        
        # Proyección de campos necesarios
        pipeline.append({
            '$project': {
                '_id': 0,
                'codigo_producto': 1,
                'nombre': 1,
                'descripcion': 1,
                'marca.nombre': 1,
                'categoria.nombre': 1,
                'metadata.precio_usd': 1,
                'metadata.calificacion_promedio': 1,
                'imagen_principal': 1,
                'similarity_score': 1
            }
        })
        
        # Limitar resultados finales
        pipeline.append({'$limit': limit})
        
        try:
            # Intentar usar Atlas Vector Search
            resultados = list(productos_collection.aggregate(pipeline))
            print(f"   ✓ Atlas Vector Search: {len(resultados)} resultados")
            
            # Formatear resultados
            productos_formateados = []
            for p in resultados:
                productos_formateados.append({
                    'codigo': p.get('codigo_producto', ''),
                    'nombre': p.get('nombre', ''),
                    'descripcion': p.get('descripcion', ''),
                    'marca': p.get('marca', {}).get('nombre', ''),
                    'categoria': p.get('categoria', {}).get('nombre', ''),
                    'precio_usd': p.get('metadata', {}).get('precio_usd', 0),
                    'calificacion': p.get('metadata', {}).get('calificacion_promedio', 0),
                    'imagen': p.get('imagen_principal', ''),
                    'similarity': round(p.get('similarity_score', 0) * 100, 2)
                })
            
        except Exception as ve:
            # Fallback si Vector Search no está disponible
            print(f"   ⚠️ Vector Search no disponible: {ve}")
            print(f"   → Usando búsqueda manual con embeddings")
            
            # Construir filtros para búsqueda manual
            filtros_mongo = {}
            if category:
                filtros_mongo['categoria.slug'] = category
            if max_price:
                filtros_mongo['metadata.precio_usd'] = {'$lte': max_price}
            if brand:
                filtros_mongo['marca.nombre'] = {'$regex': brand, '$options': 'i'}
            
            # Obtener productos y calcular similitud manualmente
            productos = list(productos_collection.find(filtros_mongo).limit(200))
            
            productos_con_similitud = []
            for producto in productos:
                if 'descripcion_embedding' in producto and producto['descripcion_embedding']:
                    similitud = cosine_similarity(query_embedding, producto['descripcion_embedding'])
                    
                    productos_con_similitud.append({
                        'producto': producto,
                        'similarity_score': similitud
                    })
            
            # Ordenar por similitud
            productos_con_similitud.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Formatear top resultados
            productos_formateados = []
            for item in productos_con_similitud[:limit]:
                p = item['producto']
                productos_formateados.append({
                    'codigo': p.get('codigo_producto', ''),
                    'nombre': p.get('nombre', ''),
                    'descripcion': p.get('descripcion', ''),
                    'marca': p.get('marca', {}).get('nombre', ''),
                    'categoria': p.get('categoria', {}).get('nombre', ''),
                    'precio_usd': p.get('metadata', {}).get('precio_usd', 0),
                    'calificacion': p.get('metadata', {}).get('calificacion_promedio', 0),
                    'imagen': p.get('imagen_principal', ''),
                    'similarity': round(item['similarity_score'] * 100, 2)
                })
        
        print(f"✓ Devolviendo {len(productos_formateados)} productos vectoriales")
        
        return jsonify({
            'query': query,
            'total_results': len(productos_formateados),
            'results': productos_formateados
        })
        
    except Exception as e:
        print(f"❌ Error en búsqueda vectorial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error en búsqueda: {str(e)}',
            'results': []
        }), 500


@app.route('/api/products/search-by-image', methods=['GET', 'POST'])
def api_products_search_by_image():
    """
    Búsqueda MULTIMODAL usando CLIP embeddings (512 dims).
    
    Modos soportados:
    1. GET con ?description= → busca por descripción de texto
    2. POST con archivo de imagen → busca por imagen real subida
    
    Requiere índice 'foto_index' en MongoDB Atlas.
    """
    try:
        query_embedding = None
        query_type = "texto"
        query_display = ""
        
        # MODO 1: POST con imagen subida
        if request.method == 'POST' and 'image' in request.files:
            file = request.files['image']
            if file.filename:
                try:
                    # Leer imagen y generar embedding CLIP
                    image_bytes = file.read()
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    
                    query_embedding = generate_clip_image_embedding(pil_image)
                    query_type = "imagen"
                    query_display = f"Imagen subida: {file.filename}"
                    
                    print(f"🖼️ Búsqueda por IMAGEN REAL: {file.filename}")
                    
                except Exception as e:
                    print(f"❌ Error procesando imagen: {e}")
                    return jsonify({
                        'error': f'Error al procesar imagen: {str(e)}',
                        'results': []
                    }), 400
        
        # MODO 2: GET/POST con descripción de texto
        if query_embedding is None:
            description = request.args.get('description') or request.form.get('description', '')
            description = description.strip()
            
            if not description:
                return jsonify({
                    'error': 'Debes proporcionar una descripción o subir una imagen',
                    'results': [],
                    'hint': 'Escribe una descripción del producto que buscas (ej: "smartphone con buena cámara") o sube una imagen'
                }), 400
            
            try:
                query_embedding = generate_clip_text_embedding(description)
                query_type = "texto"
                query_display = description
                print(f"🔍 Búsqueda por DESCRIPCIÓN (CLIP): '{description}'")
            except Exception as clip_error:
                print(f"⚠️ Error generando embedding CLIP: {clip_error}")
                return jsonify({
                    'error': 'Error al generar embedding CLIP. Verifica que el modelo esté cargado.',
                    'details': str(clip_error),
                    'results': []
                }), 500
        
        limit = request.args.get('limit', default=10, type=int)
        
        db = get_database()
        imagenes_collection = db[COLLECTIONS['IMAGENES']]
        
        # Pipeline de búsqueda vectorial con MongoDB Atlas Vector Search
        pipeline = [
            {
                '$vectorSearch': {
                    'index': 'foto_index',  # Índice CLIP (512 dims)
                    'path': 'imagen_embedding_clip',
                    'queryVector': query_embedding,
                    'numCandidates': limit * 10,
                    'limit': limit * 3
                }
            },
            {
                '$addFields': {
                    'similarity_score': {'$meta': 'vectorSearchScore'}
                }
            },
            {
                '$match': {
                    'esPrincipal': True  # Solo imágenes principales (camelCase)
                }
            },
            {
                '$lookup': {
                    'from': 'productos',
                    'localField': 'idProducto',  # camelCase en imagenesProducto
                    'foreignField': 'idProducto',  # camelCase en productos
                    'as': 'producto_info'
                }
            },
            {
                '$unwind': '$producto_info'
            },
            {
                '$project': {
                    'producto_info.codigoProducto': 1,
                    'producto_info.nombre': 1,
                    'producto_info.descripcion': 1,
                    'producto_info.marcaNombre': 1,
                    'producto_info.categoriaSlug': 1,
                    'producto_info.precioUsd': 1,
                    'producto_info.imagenPrincipal': 1,
                    'similarity_score': 1,
                    'textoAlternativo': 1,
                    'urlImagen': 1
                }
            },
            {
                '$limit': limit
            }
        ]
        
        try:
            # Primero verificar cuántas imágenes tienen embeddings
            total_con_embedding = imagenes_collection.count_documents({
                'imagen_embedding_clip': {'$exists': True}
            })
            total_principales = imagenes_collection.count_documents({
                'esPrincipal': True
            })
            print(f"   📊 Debug: {total_con_embedding} imágenes con embedding, {total_principales} principales")
            
            # Intentar búsqueda vectorial con Atlas
            resultados = list(imagenes_collection.aggregate(pipeline))
            print(f"   ✓ Vector Search CLIP encontró {len(resultados)} resultados")
            
            # Si no hay resultados, dar feedback al usuario
            if len(resultados) == 0:
                print(f"   ⚠️ No se encontraron productos con embeddings CLIP")
                print(f"   💡 Intentando búsqueda SIN filtro esPrincipal...")
                
                # Pipeline sin filtro esPrincipal
                pipeline_sin_filtro = [
                    {
                        '$vectorSearch': {
                            'index': 'foto_index',
                            'path': 'imagen_embedding_clip',
                            'queryVector': query_embedding,
                            'numCandidates': limit * 10,
                            'limit': limit * 3
                        }
                    },
                    {
                        '$addFields': {
                            'similarity_score': {'$meta': 'vectorSearchScore'}
                        }
                    },
                    {
                        '$lookup': {
                            'from': 'productos',
                            'localField': 'idProducto',
                            'foreignField': 'idProducto',
                            'as': 'producto_info'
                        }
                    },
                    {
                        '$unwind': '$producto_info'
                    },
                    {
                        '$project': {
                            'producto_info.codigoProducto': 1,
                            'producto_info.nombre': 1,
                            'producto_info.descripcion': 1,
                            'producto_info.marcaNombre': 1,
                            'producto_info.categoriaSlug': 1,
                            'producto_info.precioUsd': 1,
                            'producto_info.imagenPrincipal': 1,
                            'similarity_score': 1,
                            'textoAlternativo': 1,
                            'urlImagen': 1,
                            'esPrincipal': 1
                        }
                    },
                    {
                        '$limit': limit
                    }
                ]
                
                resultados = list(imagenes_collection.aggregate(pipeline_sin_filtro))
                print(f"   ✓ Búsqueda SIN filtro encontró {len(resultados)} resultados")
            
        except Exception as ve:
            # Fallback: búsqueda manual con cosine similarity
            print(f"   ⚠️ Vector Search no disponible: {ve}")
            print(f"   → Usando búsqueda manual con embeddings CLIP")
            
            # Contar cuántas imágenes tienen embeddings CLIP
            total_con_embedding = imagenes_collection.count_documents({
                'imagen_embedding_clip': {'$exists': True, '$ne': [], '$ne': None}
            })
            print(f"   📊 Imágenes con embedding CLIP en BD: {total_con_embedding}")
            
            if total_con_embedding == 0:
                # No hay embeddings CLIP, usar búsqueda de texto normal como fallback
                print(f"   ⚠️ No hay embeddings CLIP. Fallback: búsqueda de texto normal")
                productos_collection = db[COLLECTIONS['PRODUCTOS']]
                
                # Buscar por nombre/descripción
                search_regex = {'$regex': query_display, '$options': 'i'}
                productos = list(productos_collection.find({
                    '$or': [
                        {'nombre': search_regex},
                        {'descripcion': search_regex},
                        {'marca_nombre': search_regex}
                    ]
                }).limit(limit))
                
                resultados = []
                for p in productos:
                    resultados.append({
                        'producto_info': p,
                        'similarity_score': 0.5,  # Score arbitrario para fallback
                        'texto_alternativo': '',
                        'url_imagen': p.get('imagen_principal', '')
                    })
                
                print(f"   ✓ Fallback texto encontró {len(resultados)} productos")
            else:
                # Hay embeddings, hacer búsqueda manual
                imagenes = list(imagenes_collection.find({
                    'imagen_embedding_clip': {'$exists': True, '$ne': [], '$ne': None},
                    'es_principal': True
                }).limit(200))
                
                imagenes_con_similitud = []
                for img in imagenes:
                    embedding = img.get('imagen_embedding_clip')
                    if embedding and len(embedding) == 512:  # Verificar dimensionalidad
                        try:
                            similitud = cosine_similarity(query_embedding, embedding)
                            img['similarity_score'] = similitud
                            imagenes_con_similitud.append(img)
                        except Exception as sim_error:
                            print(f"   ⚠️ Error calculando similitud: {sim_error}")
                            continue
                
                imagenes_con_similitud.sort(key=lambda x: x['similarity_score'], reverse=True)
                
                # Lookup manual de productos
                productos_collection = db[COLLECTIONS['PRODUCTOS']]
                resultados = []
                for img in imagenes_con_similitud[:limit]:
                    producto = productos_collection.find_one({
                        'codigo_producto': img['codigo_producto']
                    })
                    if producto:
                        resultados.append({
                            'producto_info': producto,
                            'similarity_score': img['similarity_score'],
                            'texto_alternativo': img.get('texto_alternativo', ''),
                            'url_imagen': img.get('url_imagen', '')
                        })
                
                print(f"   ✓ Búsqueda manual encontró {len(resultados)} productos")
        
        # Formatear resultados
        productos_formateados = []
        for r in resultados:
            p = r.get('producto_info', r)
            productos_formateados.append({
                'codigo': p.get('codigoProducto', p.get('codigo_producto', '')),
                'nombre': p.get('nombre', ''),
                'descripcion': p.get('descripcion', ''),
                'marca': p.get('marcaNombre', p.get('marca_nombre', '')),
                'categoria': p.get('categoriaSlug', p.get('categoria_slug', '')),
                'precio_usd': p.get('precioUsd', p.get('precio_usd', 0)),
                'imagen': r.get('urlImagen', r.get('url_imagen', p.get('imagenPrincipal', p.get('imagen_principal', '')))),
                'similarity': round(r.get('similarity_score', 0) * 100, 2)
            })
        
        print(f"✓ Devolviendo {len(productos_formateados)} productos (búsqueda por {query_type})")
        
        response = {
            'query': query_display,
            'query_type': query_type,
            'total_results': len(productos_formateados),
            'results': productos_formateados,
            'search_method': 'clip_multimodal_512d'
        }
        
        # Agregar mensaje si no hay resultados
        if len(productos_formateados) == 0:
            response['message'] = 'No se encontraron productos. Posibles razones:'
            response['suggestions'] = [
                '1. No hay embeddings CLIP en la base de datos. Ejecuta: py scripts/generate_image_embeddings_clip.py',
                '2. Intenta con una descripción más general (ej: "smartphone" en vez de "smartphone con cámara de 108MP")',
                '3. Verifica que los índices vectoriales estén creados en MongoDB Atlas'
            ]
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error en búsqueda por imagen: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Error en búsqueda: {str(e)}',
            'results': []
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


@app.route('/rag', methods=['POST'])
def rag_query():
    """
    Sistema RAG COMPLEJO con búsqueda multimodal.
    Combina: productos (texto), imágenes (CLIP), y reseñas.
    
    Capacidades:
    - Búsqueda vectorial en productos (descripción semántica)
    - Búsqueda vectorial en imágenes (CLIP multimodal)
    - Búsqueda vectorial en reseñas (opiniones de usuarios)
    - Análisis de tendencias y patrones
    - Generación de respuesta contextual inteligente
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_products = data.get('max_products', 5)
        max_reviews = data.get('max_reviews', 3)
        include_reviews = data.get('include_reviews', True)
        include_images = data.get('include_images', True)
        
        if not query:
            return jsonify({'error': 'El parámetro query es requerido'}), 400
        
        print(f"🤖 RAG COMPLEJO: '{query}'")
        print(f"   📦 Max productos: {max_products} | 💬 Reviews: {include_reviews} | 🖼️ Imágenes: {include_images}")
        
        # Generar embeddings para la consulta
        query_embedding_text = generate_embedding(query)  # 384 dims (sentence-transformers)
        
        # Si incluye imágenes, generar también embedding CLIP
        query_embedding_clip = None
        if include_images:
            try:
                query_embedding_clip = generate_clip_text_embedding(query)  # 512 dims (CLIP)
                print(f"   ✓ Embedding CLIP generado para búsqueda multimodal")
            except Exception as e:
                print(f"   ⚠️ CLIP no disponible: {e}")
        
        db = get_database()
        
        # ============================================================
        # 1. BÚSQUEDA VECTORIAL EN PRODUCTOS (Descripción)
        # ============================================================
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        pipeline_productos = [
            {
                '$vectorSearch': {
                    'index': 'idx_descripcion_vector',
                    'path': 'descripcion_embedding',
                    'queryVector': query_embedding_text,
                    'numCandidates': max_products * 10,
                    'limit': max_products * 2
                }
            },
            {
                '$addFields': {
                    'text_similarity': {'$meta': 'vectorSearchScore'}
                }
            },
            {
                '$project': {
                    'codigoProducto': 1,
                    'nombre': 1,
                    'descripcion': 1,
                    'marcaNombre': 1,
                    'categoriaSlug': 1,
                    'precioUsd': 1,
                    'imagenPrincipal': 1,
                    'especificaciones': 1,
                    'text_similarity': 1,
                    '_id': 1
                }
            }
        ]
        
        try:
            productos_texto = list(productos_collection.aggregate(pipeline_productos))
            print(f"   ✓ Productos (texto): {len(productos_texto)} encontrados")
        except Exception as ve:
            print(f"   ⚠️ Vector Search productos: {ve} | Fallback manual")
            productos = list(productos_collection.find({}).limit(100))
            productos_texto = []
            for p in productos:
                if p.get('descripcion_embedding'):
                    sim = cosine_similarity(query_embedding_text, p['descripcion_embedding'])
                    p['text_similarity'] = sim
                    productos_texto.append(p)
            productos_texto.sort(key=lambda x: x['text_similarity'], reverse=True)
            productos_texto = productos_texto[:max_products * 2]
        
        # ============================================================
        # 2. BÚSQUEDA VECTORIAL EN IMÁGENES (CLIP Multimodal)
        # ============================================================
        productos_imagen = []
        if include_images and query_embedding_clip:
            imagenes_collection = db[COLLECTIONS['IMAGENES']]
            
            pipeline_imagenes = [
                {
                    '$vectorSearch': {
                        'index': 'foto_index',
                        'path': 'imagen_embedding_clip',
                        'queryVector': query_embedding_clip,
                        'numCandidates': max_products * 5,
                        'limit': max_products
                    }
                },
                {
                    '$match': {'esPrincipal': True}
                },
                {
                    '$addFields': {
                        'image_similarity': {'$meta': 'vectorSearchScore'}
                    }
                },
                {
                    '$lookup': {
                        'from': 'productos',
                        'localField': 'idProducto',
                        'foreignField': 'codigoProducto',
                        'as': 'producto_info'
                    }
                },
                {
                    '$unwind': '$producto_info'
                },
                {
                    '$project': {
                        'codigo_producto': 1,
                        'producto_info': 1,
                        'image_similarity': 1,
                        'texto_alternativo': 1
                    }
                }
            ]
            
            try:
                productos_imagen = list(imagenes_collection.aggregate(pipeline_imagenes))
                print(f"   ✓ Productos (imagen/CLIP): {len(productos_imagen)} encontrados")
            except Exception as ve:
                print(f"   ⚠️ Vector Search imágenes: {ve}")
        
        # ============================================================
        # 3. FUSIÓN DE RESULTADOS (Híbrido: Texto + Imagen)
        # ============================================================
        productos_fusionados = {}
        
        # Agregar productos de búsqueda por texto
        for p in productos_texto:
            pid = str(p.get('_id', p.get('codigo_producto', '')))
            productos_fusionados[pid] = {
                'producto': p,
                'text_score': p.get('text_similarity', 0),
                'image_score': 0,
                'hybrid_score': p.get('text_similarity', 0) * 0.7  # Peso 70% texto
            }
        
        # Agregar/actualizar con productos de búsqueda por imagen
        for item in productos_imagen:
            p = item.get('producto_info', {})
            pid = str(p.get('_id', p.get('codigo_producto', '')))
            
            if pid in productos_fusionados:
                # Ya existe, actualizar con score de imagen
                productos_fusionados[pid]['image_score'] = item.get('image_similarity', 0)
                productos_fusionados[pid]['hybrid_score'] = (
                    productos_fusionados[pid]['text_score'] * 0.6 +  # Peso 60% texto
                    item.get('image_similarity', 0) * 0.4  # Peso 40% imagen
                )
            else:
                # Nuevo producto encontrado solo por imagen
                productos_fusionados[pid] = {
                    'producto': p,
                    'text_score': 0,
                    'image_score': item.get('image_similarity', 0),
                    'hybrid_score': item.get('image_similarity', 0) * 0.4
                }
        
        # Ordenar por score híbrido
        productos_ordenados = sorted(
            productos_fusionados.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )[:max_products]
        
        print(f"   ✓ Fusión híbrida: {len(productos_ordenados)} productos finales")
        
        # ============================================================
        # 4. BÚSQUEDA VECTORIAL EN RESEÑAS
        # ============================================================
        resenas_por_producto = {}
        total_resenas = 0
        
        if include_reviews:
            resenas_collection = db['resenas']
            
            for item in productos_ordenados:
                p = item['producto']
                pid = p.get('_id')
                
                pipeline_resenas = [
                    {
                        '$vectorSearch': {
                            'index': 'idx_contenido_resena_vector',
                            'path': 'contenido_embedding',
                            'queryVector': query_embedding_text,
                            'numCandidates': max_reviews * 5,
                            'limit': max_reviews * 3
                        }
                    },
                    {
                        '$match': {'codigoProducto': p.get('codigoProducto', p.get('codigo_producto'))}
                    },
                    {
                        '$addFields': {
                            'review_similarity': {'$meta': 'vectorSearchScore'}
                        }
                    },
                    {
                        '$limit': max_reviews
                    }
                ]
                
                try:
                    resenas = list(resenas_collection.aggregate(pipeline_resenas))
                except:
                    resenas = list(resenas_collection.find(
                        {'codigoProducto': p.get('codigoProducto', p.get('codigo_producto'))}
                    ).limit(max_reviews))
                
                resenas_por_producto[str(pid)] = resenas
                total_resenas += len(resenas)
        
        print(f"   ✓ Reseñas relevantes: {total_resenas} recuperadas")
        
        # ============================================================
        # 5. CONSTRUIR CONTEXTO ENRIQUECIDO
        # ============================================================
        contexto = f"CONSULTA: {query}\n\n"
        contexto += "="*80 + "\n"
        contexto += "ANÁLISIS MULTIMODAL (Texto + Imágenes + Reseñas)\n"
        contexto += "="*80 + "\n\n"
        
        for i, item in enumerate(productos_ordenados, 1):
            p = item['producto']
            contexto += f"\n{i}. {p.get('nombre', 'N/A')} - {p.get('marcaNombre', p.get('marca_nombre', 'N/A'))}\n"
            contexto += f"   {'─'*70}\n"
            contexto += f"   💰 Precio: ${p.get('precioUsd', p.get('precio_usd', 0)):.2f} USD\n"
            contexto += f"   📊 Score Híbrido: {item['hybrid_score']*100:.1f}%\n"
            contexto += f"      • Texto: {item['text_score']*100:.1f}%\n"
            contexto += f"      • Imagen: {item['image_score']*100:.1f}%\n"
            
            # Especificaciones técnicas
            if p.get('especificaciones'):
                contexto += f"\n   🔧 Especificaciones:\n"
                specs = p['especificaciones']
                for key, value in list(specs.items())[:4]:
                    contexto += f"      • {key}: {value}\n"
            
            # Reseñas
            pid = str(p.get('_id', ''))
            if pid in resenas_por_producto:
                resenas = resenas_por_producto[pid]
                if resenas:
                    contexto += f"\n   💬 Opiniones ({len(resenas)} reseñas relevantes):\n"
                    for j, r in enumerate(resenas, 1):
                        contexto += f"      {j}. ⭐ {r.get('calificacion', 0)}/5 - {r.get('titulo', 'Sin título')}\n"
                        if r.get('ventajas'):
                            contexto += f"         👍 {', '.join(r['ventajas'][:2])}\n"
                        if r.get('desventajas'):
                            contexto += f"         👎 {', '.join(r['desventajas'][:2])}\n"
            
            contexto += "\n"
        
        # ============================================================
        # 6. GENERAR RESPUESTA INTELIGENTE CON GROQ LLM
        # ============================================================
        # Construir contexto estructurado para el LLM
        llm_context = build_context_for_llm_from_products(
            [item['producto'] for item in productos_ordenados],
            max_items=min(6, len(productos_ordenados))
        )
        
        # Agregar información de reseñas al contexto
        for item in productos_ordenados[:6]:
            p = item['producto']
            pid = str(p.get('_id', ''))
            if pid in resenas_por_producto and resenas_por_producto[pid]:
                resenas = resenas_por_producto[pid]
                ventajas = []
                desventajas = []
                for r in resenas:
                    ventajas.extend(r.get('ventajas', []))
                    desventajas.extend(r.get('desventajas', []))
                
                # Agregar al producto para build_context
                p['ventajas'] = list(set(ventajas))[:5]
                p['desventajas'] = list(set(desventajas))[:5]
        
        # Reconstruir contexto con reseñas
        llm_context = build_context_for_llm_from_products(
            [item['producto'] for item in productos_ordenados],
            max_items=min(6, len(productos_ordenados))
        )
        
        print(f"   🧠 Generando respuesta con Groq LLM...")
        try:
            # Generar respuesta con LLM
            respuesta = generate_answer_with_llm(llm_context, query)
            print(f"   ✓ Respuesta LLM generada: {len(respuesta)} caracteres")
        except Exception as llm_error:
            print(f"   ⚠️ Error en LLM: {llm_error} | Usando respuesta básica")
            # Fallback: respuesta básica sin LLM
            respuesta = f"**Análisis RAG Multimodal para: '{query}'**\n\n"
            respuesta += f"He realizado una búsqueda avanzada combinando análisis de texto, imágenes y opiniones de usuarios. "
            respuesta += f"Encontré {len(productos_ordenados)} productos altamente relevantes:\n\n"
            
            for i, item in enumerate(productos_ordenados[:3], 1):
                p = item['producto']
                respuesta += f"**{i}. {p.get('nombre', 'N/A')}**\n"
                respuesta += f"   💰 ${p.get('precioUsd', p.get('precio_usd', 0)):.2f} | "
                respuesta += f"🎯 Relevancia: {item['hybrid_score']*100:.0f}%\n"
                
                # Análisis de reseñas
                pid = str(p.get('_id', ''))
                if pid in resenas_por_producto and resenas_por_producto[pid]:
                    resenas = resenas_por_producto[pid]
                    ventajas_todas = []
                    for r in resenas:
                        ventajas_todas.extend(r.get('ventajas', []))
                    if ventajas_todas:
                        respuesta += f"   ✨ Destacado por usuarios: {', '.join(set(ventajas_todas[:3]))}\n"
                
                respuesta += "\n"
            
            metodo = "Multimodal (CLIP + Texto)" if include_images else "Texto vectorial"
            respuesta += f"\n📊 **Método de búsqueda**: {metodo}\n"
            respuesta += f"🔍 **Precisión**: Alta relevancia semántica (>{productos_ordenados[0]['hybrid_score']*100:.0f}%)"
        
        # ============================================================
        # 7. FORMATEAR RESPUESTA JSON
        # ============================================================
        productos_formateados = []
        for item in productos_ordenados:
            p = item['producto']
            productos_formateados.append({
                'codigo': p.get('codigoProducto', p.get('codigo_producto', '')),
                'nombre': p.get('nombre', ''),
                'descripcion': p.get('descripcion', ''),
                'marca': p.get('marcaNombre', p.get('marca_nombre', '')),
                'categoria': p.get('categoriaSlug', p.get('categoria_slug', '')),
                'precio_usd': p.get('precioUsd', p.get('precio_usd', 0)),
                'imagen': p.get('imagenPrincipal', p.get('imagen_principal', '')),
                'similarity': round(item['hybrid_score'] * 100, 2),
                'text_similarity': round(item['text_score'] * 100, 2),
                'image_similarity': round(item['image_score'] * 100, 2),
                'hybrid_score': round(item['hybrid_score'] * 100, 2)
            })
        
        print(f"✅ RAG COMPLEJO completado exitosamente")
        
        return jsonify({
            'query': query,
            'rag_response': respuesta,
            'contexto': contexto,
            'productos': productos_formateados,
            'metadata': {
                'total_productos': len(productos_ordenados),
                'total_resenas': total_resenas,
                'search_modes': {
                    'text_search': True,
                    'image_search': include_images and query_embedding_clip is not None,
                    'review_search': include_reviews
                },
                'model_text': EMBEDDING_MODEL_NAME,
                'model_image': 'openai/clip-vit-base-patch32' if include_images else None,
                'model_used': 'Groq Llama 3.3 70B + CLIP + Sentence Transformers',
                'search_method': 'rag_multimodal_complex'
            },
            'context': {
                'total_productos': len(productos_ordenados),
                'total_resenas': total_resenas,
                'productos': productos_formateados
            }
        })
        
    except Exception as e:
        print(f"❌ Error en RAG complejo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error en RAG: {str(e)}'}), 500


@app.route('/api/utils/update-caption', methods=['POST'])
def api_update_caption():
    """
    Actualiza el caption/descripción de una imagen por título.
    
    Body JSON:
    {
        "title": "nombre_producto",
        "new_caption": "Nueva descripción"
    }
    """
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        new_caption = data.get('new_caption', '').strip()
        
        if not title or not new_caption:
            return jsonify({'error': 'Parámetros title y new_caption son requeridos'}), 400
        
        db = get_database()
        success = update_caption_by_title(db, title, new_caption)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Caption actualizado para: {title}'
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': f'No se encontró documento con título: {title}'
            }), 404
            
    except Exception as e:
        print(f"❌ Error al actualizar caption: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/utils/delete-image', methods=['DELETE'])
def api_delete_image():
    """
    Elimina una imagen y sus metadatos por título.
    
    Body JSON:
    {
        "title": "nombre_producto"
    }
    """
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({'error': 'Parámetro title es requerido'}), 400
        
        db = get_database()
        fs = gridfs.GridFS(db)
        
        success = delete_by_title(db, fs, title)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Documento e imagen eliminados: {title}'
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': f'No se encontró documento con título: {title}'
            }), 404
            
    except Exception as e:
        print(f"❌ Error al eliminar: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/utils/show-results', methods=['POST'])
def api_show_results_util():
    """
    Utilidad para visualizar resultados de búsqueda con imágenes.
    Útil para debugging y análisis.
    
    Body JSON:
    {
        "query": "texto de búsqueda",
        "limit": 5
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Parámetro query es requerido'}), 400
        
        db = get_database()
        fs = gridfs.GridFS(db)
        
        # Hacer búsqueda simple de productos
        query_embedding = generate_embedding(query)
        productos_collection = db[COLLECTIONS['PRODUCTOS']]
        
        productos = list(productos_collection.aggregate([
            {
                '$vectorSearch': {
                    'index': 'idx_descripcion_vector',
                    'path': 'descripcion_embedding',
                    'queryVector': query_embedding,
                    'numCandidates': limit * 10,
                    'limit': limit
                }
            },
            {
                '$addFields': {
                    'score': {'$meta': 'vectorSearchScore'}
                }
            }
        ]))
        
        # Usar función show_results
        results = show_results(productos, fs)
        
        # Formatear para JSON (sin imágenes binarias)
        results_json = []
        for r in results:
            results_json.append({
                'title': r['title'],
                'score': r['score'],
                'category': r['category'],
                'tags': r['tags'],
                'caption': r['caption'],
                'has_image': r.get('image') is not None
            })
        
        return jsonify({
            'query': query,
            'results': results_json,
            'total': len(results_json)
        })
        
    except Exception as e:
        print(f"❌ Error en show_results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500


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
