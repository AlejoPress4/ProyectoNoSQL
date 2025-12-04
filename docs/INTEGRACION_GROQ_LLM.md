# 🤖 Integración Groq LLM con RAG Multimodal

## Descripción General

Se ha integrado Groq LLM (modelo `llama-3.1-8b-instant`) en el sistema RAG para generar respuestas inteligentes basadas en el contexto recuperado de productos, imágenes y reseñas.

## 🆕 Funcionalidades Implementadas

### 1. Cliente Groq (OpenAI Compatible)

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),  # Configura esto en .env
    base_url="https://api.groq.com/openai/v1"
)
```

**Configuración:**
- Variable de entorno: `GROQ_API_KEY` (opcional)
- Fallback: API key hardcodeada en el código
- Modelo por defecto: `llama-3.1-8b-instant`

### 2. Generación de Respuestas con LLM

**Función:** `generate_answer_with_llm(context, question, model="llama-3.1-8b-instant")`

**Características:**
- ✅ Prompt engineering optimizado para e-commerce tecnológico
- ✅ Temperature: 0.4 (balanceo creatividad/precisión)
- ✅ Max tokens: 800
- ✅ Manejo de errores con fallback a respuesta básica
- ✅ Sistema prompt especializado en productos tech

**Ejemplo de uso:**
```python
context = build_context_for_llm_from_products(productos, max_items=6)
respuesta = generate_answer_with_llm(context, "¿Cuál es la mejor laptop para gaming?")
```

### 3. Construcción de Contexto Enriquecido

**Función:** `build_context_for_llm_from_products(productos, max_items=6)`

**Incluye:**
- 📝 Nombre, marca, precio, categoría, descripción
- 🔧 Especificaciones técnicas
- ⭐ Scores de similitud (text, image, hybrid)
- 👍 Ventajas de reseñas de usuarios
- 👎 Desventajas de reseñas de usuarios

**Formato del contexto:**
```
[PRODUCTO 1]
Nombre: Laptop Dell XPS 15
Marca: Dell
Precio: $1299.99 USD
Categoría: Laptops
Descripción: Potente laptop con procesador Intel i7...
Especificaciones: RAM: 16GB, SSD: 512GB, GPU: RTX 3050
Relevancia: Text=85.3%, Image=78.2%, Hybrid=82.3%
    + Alto rendimiento
    + Excelente pantalla
    + Buena duración de batería
    - Precio elevado
    - Ventiladores ruidosos
```

### 4. Visualización de Resultados (show_results)

**Función:** `show_results(docs, fs)`

**Características:**
- 🔎 Muestra scores formateados
- 📷 Renderiza imágenes desde GridFS usando PIL
- 🏷️ Extrae metadatos (categoría, tags, caption)
- ⚠️ Manejo robusto de errores en imágenes

**Ejemplo de salida:**
```
🔎 Dell XPS 15 | score=0.8523 | cat=Laptops | tags=['gaming', 'profesional']
  📷 Imagen cargada: (1920, 1080) px
```

### 5. Utilidades de Gestión de Metadatos

#### a) Actualizar Caption/Descripción

**Función:** `update_caption_by_title(db, title, new_caption)`

**Endpoint:** `POST /api/utils/update-caption`

```bash
curl -X POST http://localhost:5000/api/utils/update-caption \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dell XPS 15",
    "new_caption": "Laptop premium para profesionales creativos con pantalla 4K"
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Caption actualizado para: Dell XPS 15"
}
```

#### b) Eliminar Imagen y Metadatos

**Función:** `delete_by_title(db, fs, title)`

**Endpoint:** `DELETE /api/utils/delete-image`

```bash
curl -X DELETE http://localhost:5000/api/utils/delete-image \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Producto obsoleto"
  }'
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Documento e imagen eliminados: Producto obsoleto"
}
```

#### c) Visualizar Resultados con Debugging

**Endpoint:** `POST /api/utils/show-results`

```bash
curl -X POST http://localhost:5000/api/utils/show-results \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptops gaming",
    "limit": 5
  }'
```

**Respuesta:**
```json
{
  "query": "laptops gaming",
  "results": [
    {
      "title": "Dell XPS 15",
      "score": "0.8523",
      "category": "Laptops",
      "tags": ["gaming", "profesional"],
      "caption": "Potente laptop...",
      "has_image": true
    }
  ],
  "total": 5
}
```

## 📊 Endpoint RAG Actualizado

### POST /rag

**Flujo actualizado:**

1. **Generación de embeddings**
   - Texto (sentence-transformers, 384d)
   - CLIP (para imágenes, 512d)

2. **Búsqueda multimodal**
   - Productos (texto)
   - Imágenes (CLIP)
   - Reseñas (texto)

3. **Fusión híbrida**
   - `hybrid_score = text_score * 0.6 + image_score * 0.4`

4. **Construcción de contexto enriquecido**
   - Productos con especificaciones
   - Ventajas/desventajas de reseñas

5. **🆕 Generación de respuesta con Groq LLM**
   - Análisis inteligente del contexto
   - Recomendaciones personalizadas
   - Comparaciones entre productos
   - Relación calidad-precio

6. **Respuesta JSON**
   ```json
   {
     "query": "mejor laptop para gaming",
     "rag_response": "[RESPUESTA GENERADA POR LLM]",
     "productos": [...],
     "metadata": {
       "llm_used": true,
       "model_llm": "llama-3.1-8b-instant"
     }
   }
   ```

    ## 📦 Índices Vectoriales y Pipelines de Búsqueda (Atlas Vector Search)

    Esta sección describe los índices vectoriales necesarios y ejemplos de pipelines `$vectorSearch` que implementa la aplicación.

    Archivos de ejemplo con la definición de índices están en `atlas_search_indexes/`:

    - `idx_descripcion_vector.json` (productos, `descripcion_embedding`, 384 dims)
    - `idx_imagen_vector_clip.json` (imágenes, `imagen_embedding_clip`, 512 dims)
    - `idx_contenido_resena_vector.json` (reseñas, `contenido_embedding`, 384 dims)

    Recomendación: importa estos JSON en la sección "Search Indexes" de MongoDB Atlas para crear los índices. Asegúrate de que `numDimensions` coincida con el tamaño del vector (384 para text, 512 para CLIP).

    ### 1) Crear índices en Atlas (pasos rápidos)

    1. Abre tu cluster en MongoDB Atlas → Search → Create Search Index.
    2. Selecciona la colección (ej. `productos`, `imagenesProducto`, `resenas`).
    3. Usa la opción "Import JSON" y pega el contenido de los archivos en `atlas_search_indexes/`.
    4. Guarda y espera a que Atlas construya el índice (puede tardar unos minutos).

    ### 2) Pipeline de ejemplo — Productos (búsqueda por descripción)

    ```json
    [{
      "$vectorSearch": {
        "index": "idx_descripcion_vector",
        "path": "descripcion_embedding",
        "queryVector": /* aquí tu embedding de texto (lista) */,
        "numCandidates": 100,
        "limit": 10
      }
    }, {
      "$addFields": {"text_similarity": {"$meta": "vectorSearchScore"}}
    }, {
      "$project": {"nombre": 1, "marca_nombre": 1, "precio_usd": 1, "descripcion": 1, "text_similarity": 1}
    }]
    ```

    ### 3) Pipeline de ejemplo — Imágenes (CLIP)

    ```json
    [{
      "$vectorSearch": {
        "index": "idx_imagen_vector_clip",
        "path": "imagen_embedding_clip",
        "queryVector": /* embedding CLIP (512 dims) */,
        "numCandidates": 200,
        "limit": 20
      }
    }, {
      "$addFields": {"image_similarity": {"$meta": "vectorSearchScore"}}
    }, {
      "$project": {"codigo_producto": 1, "imagen_url": 1, "texto_alternativo": 1, "image_similarity": 1}
    }]
    ```

    ### 4) Pipeline de ejemplo — Reseñas

    ```json
    [{
      "$vectorSearch": {
        "index": "idx_contenido_resena_vector",
        "path": "contenido_embedding",
        "queryVector": /* embedding de texto (384 dims) */,
        "numCandidates": 200,
        "limit": 10
      }
    }, {
      "$addFields": {"review_similarity": {"$meta": "vectorSearchScore"}}
    }, {
      "$project": {"codigo_producto": 1, "titulo": 1, "contenido": 1, "calificacion": 1, "review_similarity": 1}
    }]
    ```

    ### 5) Fallback cuando Atlas Vector Search no está disponible

    Si no puedes usar `$vectorSearch` (por ejemplo en entornos locales o si los índices no existen), la aplicación ofrece un fallback que:

    - Calcula similitud coseno localmente usando `sklearn.metrics.pairwise.cosine_similarity` entre tu embedding y embeddings almacenados en la colección.
    - Aplica filtros (categoría, marca, precio) y ordena por similitud.

    Ejemplo (pseudo-code Python):

    ```python
    from sklearn.metrics.pairwise import cosine_similarity
    query_emb = generate_embedding(query_text)  # 384d
    docs = list(db['productos'].find({'descripcion_embedding': {'$exists': True}}))
    scores = []
    for d in docs:
        v = d['descripcion_embedding']
        s = float(cosine_similarity([query_emb], [v])[0][0])
        scores.append((s, d))
    top = sorted(scores, key=lambda x: x[0], reverse=True)[:10]
    ```

    ### 6) Verificar que los embeddings existen (comandos útiles)

    En una sesión Python (o en `scripts/`):

    ```python
    db = get_database()
    print('Productos con embedding:', db['productos'].count_documents({'descripcion_embedding': {'$exists': True}}))
    print('Imágenes con CLIP emb:', db['imagenesProducto'].count_documents({'imagen_embedding_clip': {'$exists': True}}))
    print('Reseñas con embedding:', db['resenas'].count_documents({'contenido_embedding': {'$exists': True}}))
    ```

    Si los conteos son 0 para imágenes, debes generar embeddings CLIP; hay un script en `scripts/generate_image_embeddings_clip.py`.

    ### 7) Generar embeddings (resumen rápido)

    - Embeddings de texto: `scripts/load_data.py` o `scripts/generate_text_embeddings.py` (según tu repo) — usa `sentence-transformers` (384d).
    - Embeddings de imágenes CLIP: `scripts/generate_image_embeddings_clip.py` — usa `openai/clip-vit-base-patch32` y guarda los vectores en `imagen_embedding_clip` (512d).

    Ejemplo para ejecutar el script de imágenes:

    ```powershell
    py scripts\generate_image_embeddings_clip.py
    ```

    ### 8) Validación de dimensionalidad

    Antes de crear índices, valida la dimensión de los vectores guardados:

    ```python
    sample = db['imagenesProducto'].find_one({'imagen_embedding_clip': {'$exists': True}})
    len(sample['imagen_embedding_clip'])  # debe ser 512
    ```

    ### 9) Logs y debugging

    - El servidor registra cuántas imágenes con embeddings encuentra al arrancar y cuando se ejecutan búsquedas.
    - Si ves `0` imágenes con embeddings, ejecuta el script de generación y vuelve a importar el índice en Atlas.

    ---

    Con esto, la aplicación podrá ejecutar correctamente las tres búsquedas vectoriales y fusionarlas para obtener resultados multimodales. Si quieres, implemento un script adicional que valide los índices en Atlas vía la API (o que intente crear los índices automáticamente con la Admin API). ¿Qué prefieres que haga ahora: (A) añadir un script para crear índices automáticamente, o (B) documentar el proceso paso a paso para importarlos manualmente en Atlas?

**Ejemplo de consulta:**
```bash
curl -X POST http://localhost:5000/rag \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop gaming con buena refrigeración bajo $1500",
    "max_products": 5,
    "include_reviews": true,
    "include_images": true
  }'
```

**Respuesta del LLM (ejemplo):**

> Basándome en el contexto recuperado, te recomiendo las siguientes opciones:
> 
> **1. Dell XPS 15 ($1299.99)**
> - Excelente sistema de refrigeración con ventiladores duales
> - GPU RTX 3050 ideal para gaming 1080p
> - Los usuarios destacan: "Alto rendimiento", "Buena duración de batería"
> - Contras: Ventiladores pueden ser ruidosos bajo carga extrema
> 
> **2. ASUS ROG Strix G15 ($1449.99)**
> - Sistema de refrigeración ROG con líquido y vapor chamber
> - GPU RTX 3060, mejor que la XPS para gaming intensivo
> - Ventajas según reseñas: "Excelente refrigeración", "Alto FPS en juegos"
> - Contras: Diseño gaming muy llamativo, no ideal para oficina
> 
> **Recomendación:** Si priorizas refrigeración, la ASUS ROG ofrece mejor sistema de cooling. Si buscas balance entre trabajo/gaming, la Dell XPS es más versátil.

## 🎯 Ventajas de la Integración LLM

1. **Respuestas naturales y conversacionales**
   - No más plantillas rígidas
   - Análisis contextual profundo

2. **Comparaciones inteligentes**
   - Detecta trade-offs automáticamente
   - Sugiere según necesidades del usuario

3. **Interpretación de reseñas**
   - Sintetiza ventajas/desventajas
   - Identifica patrones en opiniones

4. **Personalización**
   - Adapta lenguaje según consulta
   - Prioriza características relevantes

5. **Fallback robusto**
   - Si LLM falla, usa respuesta básica
   - No interrumpe la experiencia del usuario

## 🔒 Seguridad y Mejores Prácticas

1. **API Key Management**
   ```python
   # Usar variable de entorno en producción
   api_key = os.environ.get("GROQ_API_KEY", "fallback_key")
   ```

2. **Rate Limiting**
   - Groq: límite de requests/minuto
   - Implementar caché de respuestas frecuentes

3. **Validación de contexto**
   - Máximo 6 productos para no exceder tokens
   - Truncar descripciones muy largas

4. **Monitoreo**
   ```python
   print(f"✓ Respuesta LLM generada: {len(respuesta)} caracteres")
   ```

## 🚀 Próximos Pasos

- [ ] Implementar caché de respuestas LLM (Redis)
- [ ] Agregar modelo de fallback (GPT-3.5-turbo)
- [ ] A/B testing: respuestas LLM vs respuestas template
- [ ] Métricas: tiempo de respuesta, tasa de éxito
- [ ] Fine-tuning de prompts basado en feedback

## 📚 Referencias

- [Groq API Docs](https://console.groq.com/docs)
- [OpenAI Python Client](https://github.com/openai/openai-python)
- [LLama 3.1 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)

---

**Última actualización:** 3 de diciembre de 2025
**Versión:** 2.0 - RAG Multimodal + Groq LLM
