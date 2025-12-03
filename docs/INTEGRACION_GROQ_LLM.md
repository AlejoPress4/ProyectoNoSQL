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
