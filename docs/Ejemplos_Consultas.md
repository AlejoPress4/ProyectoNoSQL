# 🔍 Ejemplos de Consultas y Casos de Uso

## 1. Consultas Básicas (MongoDB)

### 1.1 Buscar todos los artículos de Machine Learning

```python
from pymongo import MongoClient

# Consulta simple con filtro
result = db.articles.find({
    "metadata.categoria": "Machine Learning"
})

for doc in result:
    print(f"- {doc['titulo']}")
```

**SQL Equivalente:**
```sql
SELECT titulo FROM articles 
WHERE metadata.categoria = 'Machine Learning';
```

---

### 1.2 Buscar artículos recientes en español

```python
from datetime import datetime, timedelta

# Artículos de los últimos 30 días en español
fecha_limite = datetime.now() - timedelta(days=30)

result = db.articles.find({
    "metadata.idioma": "es",
    "metadata.fecha_publicacion": {"$gte": fecha_limite}
}).sort("metadata.fecha_publicacion", -1).limit(10)
```

---

### 1.3 Buscar por tags

```python
# Artículos con el tag "python"
result = db.articles.find({
    "tags": "python"
})

# Artículos con múltiples tags (AND)
result = db.articles.find({
    "tags": {"$all": ["python", "machine-learning"]}
})

# Artículos con al menos uno de los tags (OR)
result = db.articles.find({
    "tags": {"$in": ["python", "javascript", "typescript"]}
})
```

---

## 2. Búsqueda de Texto Completo

### 2.1 Buscar por palabras clave

```python
# Buscar artículos que contengan "neural networks"
result = db.articles.find(
    {"$text": {"$search": "neural networks"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])

for doc in result:
    print(f"{doc['titulo']} - Score: {doc['score']:.2f}")
```

---

### 2.2 Buscar con operadores booleanos

```python
# Buscar "python" Y "api" (ambas palabras)
result = db.articles.find({
    "$text": {"$search": "python api"}
})

# Buscar "python" pero NO "django"
result = db.articles.find({
    "$text": {"$search": "python -django"}
})

# Buscar frase exacta
result = db.articles.find({
    "$text": {"$search": "\"machine learning\""}
})
```

---

## 3. Aggregation Pipeline

### 3.1 Contar artículos por categoría

```python
pipeline = [
    {
        "$group": {
            "_id": "$metadata.categoria",
            "count": {"$sum": 1},
            "promedio_tiempo_lectura": {"$avg": "$metadata.tiempo_lectura_min"}
        }
    },
    {
        "$sort": {"count": -1}
    }
]

result = db.articles.aggregate(pipeline)

# Output:
# Machine Learning: 35 artículos (promedio: 12 min)
# Backend: 28 artículos (promedio: 10 min)
# Frontend: 20 artículos (promedio: 8 min)
```

---

### 3.2 Join con imágenes ($lookup)

```python
pipeline = [
    {
        "$match": {
            "metadata.categoria": "Machine Learning"
        }
    },
    {
        "$lookup": {
            "from": "images",
            "localField": "imagenes",
            "foreignField": "_id",
            "as": "imagenes_data"
        }
    },
    {
        "$project": {
            "titulo": 1,
            "num_imagenes": {"$size": "$imagenes_data"},
            "urls_imagenes": "$imagenes_data.url"
        }
    },
    {
        "$match": {
            "num_imagenes": {"$gt": 0}
        }
    }
]

result = db.articles.aggregate(pipeline)
```

---

### 3.3 Estadísticas por idioma y dificultad

```python
pipeline = [
    {
        "$group": {
            "_id": {
                "idioma": "$metadata.idioma",
                "dificultad": "$metadata.dificultad"
            },
            "total": {"$sum": 1},
            "promedio_valoracion": {"$avg": "$estadisticas.valoracion"}
        }
    },
    {
        "$sort": {"_id.idioma": 1, "_id.dificultad": 1}
    }
]

result = db.articles.aggregate(pipeline)

# Output:
# es, basico: 15 artículos (valoración: 4.2)
# es, intermedio: 25 artículos (valoración: 4.5)
# es, avanzado: 10 artículos (valoración: 4.7)
```

---

### 3.4 Top 10 tags más usados

```python
pipeline = [
    # Descomponer el array de tags
    {"$unwind": "$tags"},
    
    # Agrupar por tag y contar
    {
        "$group": {
            "_id": "$tags",
            "count": {"$sum": 1}
        }
    },
    
    # Ordenar por frecuencia
    {"$sort": {"count": -1}},
    
    # Top 10
    {"$limit": 10},
    
    # Renombrar campos
    {
        "$project": {
            "tag": "$_id",
            "frecuencia": "$count",
            "_id": 0
        }
    }
]

result = db.articles.aggregate(pipeline)

# Output:
# 1. python: 45 veces
# 2. javascript: 38 veces
# 3. machine-learning: 35 veces
```

---

## 4. Búsqueda Vectorial (Atlas Search)

### 4.1 Búsqueda semántica básica

```python
from sentence_transformers import SentenceTransformer

# Cargar modelo de embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Query del usuario
query = "¿Cómo implementar autenticación JWT en APIs?"

# Generar embedding del query
query_embedding = model.encode(query).tolist()

# Búsqueda vectorial
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_articles",
            "path": "texto_embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 5
        }
    },
    {
        "$project": {
            "titulo": 1,
            "resumen": 1,
            "metadata.categoria": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]

results = db.articles.aggregate(pipeline)

for doc in results:
    print(f"Score: {doc['score']:.3f} - {doc['titulo']}")
```

---

### 4.2 Búsqueda híbrida (vectorial + filtros)

```python
# Buscar artículos similares SOLO en español y de categoría Backend
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_articles",
            "path": "texto_embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 10,
            "filter": {
                "$and": [
                    {"metadata.idioma": {"$eq": "es"}},
                    {"metadata.categoria": {"$eq": "Backend"}}
                ]
            }
        }
    },
    {
        "$project": {
            "titulo": 1,
            "metadata": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]

results = db.articles.aggregate(pipeline)
```

---

### 4.3 Búsqueda multimodal (texto → imagen)

```python
from transformers import CLIPModel, CLIPProcessor

# Cargar modelo CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Query de texto
query = "diagrama de arquitectura de microservicios"

# Generar embedding de texto con CLIP
inputs = processor(text=[query], return_tensors="pt", padding=True)
text_embedding = model.get_text_features(**inputs).detach().numpy()[0].tolist()

# Buscar imágenes similares
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_images",
            "path": "image_embedding",
            "queryVector": text_embedding,
            "numCandidates": 50,
            "limit": 5,
            "filter": {
                "metadata.tipo": {"$eq": "diagrama"}
            }
        }
    },
    {
        "$project": {
            "nombre": 1,
            "url": 1,
            "descripcion": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]

results = db.images.aggregate(pipeline)
```

---

### 4.4 Búsqueda por rango de fechas + similaridad

```python
from datetime import datetime

fecha_inicio = datetime(2024, 1, 1)
fecha_fin = datetime(2024, 12, 31)

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_articles",
            "path": "texto_embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 10,
            "filter": {
                "$and": [
                    {"metadata.fecha_publicacion": {"$gte": fecha_inicio}},
                    {"metadata.fecha_publicacion": {"$lte": fecha_fin}}
                ]
            }
        }
    }
]

results = db.articles.aggregate(pipeline)
```

---

## 5. Pipeline RAG Completo

### 5.1 Función RAG básica

```python
import os
from groq import Groq

def rag_query(user_query: str, db, model):
    """
    Pipeline RAG completo:
    1. Generar embedding del query
    2. Buscar documentos relevantes
    3. Construir contexto
    4. Generar respuesta con LLM
    """
    
    # 1. Generar embedding
    query_embedding = model.encode(user_query).tolist()
    
    # 2. Búsqueda vectorial
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index_articles",
                "path": "texto_embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": 5
            }
        },
        {
            "$project": {
                "titulo": 1,
                "contenido": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    results = list(db.articles.aggregate(pipeline))
    
    # 3. Construir contexto
    context = "\n\n".join([
        f"[Documento {i+1}]\nTítulo: {doc['titulo']}\nContenido: {doc['contenido'][:500]}..."
        for i, doc in enumerate(results)
    ])
    
    # 4. Generar respuesta con LLM
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""Eres un asistente experto en tecnología. Responde la pregunta del usuario basándote ÚNICAMENTE en el contexto proporcionado.

Contexto:
{context}

Pregunta del usuario: {user_query}

Respuesta:"""
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un asistente técnico que responde basándose solo en el contexto dado."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=500
    )
    
    respuesta = chat_completion.choices[0].message.content
    
    # 5. Guardar en historial
    db.query_history.insert_one({
        "query_text": user_query,
        "query_type": "semantic",
        "query_embedding": query_embedding,
        "resultados": {
            "count": len(results),
            "top_docs": [doc["_id"] for doc in results],
            "scores": [doc["score"] for doc in results]
        },
        "respuesta_generada": respuesta,
        "timestamp": datetime.now()
    })
    
    return respuesta, results


# Uso:
respuesta, docs = rag_query(
    "¿Cuáles son las mejores prácticas para diseñar APIs RESTful?",
    db,
    model
)

print("Respuesta:", respuesta)
print("\nDocumentos consultados:")
for doc in docs:
    print(f"- {doc['titulo']} (score: {doc['score']:.3f})")
```

---

## 6. Casos de Uso Avanzados

### 6.1 Recomendación de artículos similares

```python
def recomendar_similares(article_id, db, limit=5):
    """
    Dado un artículo, recomienda otros similares
    """
    
    # Obtener el artículo original
    article = db.articles.find_one({"_id": article_id})
    
    if not article:
        return []
    
    # Usar su embedding para buscar similares
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index_articles",
                "path": "texto_embedding",
                "queryVector": article["texto_embedding"],
                "numCandidates": 50,
                "limit": limit + 1  # +1 porque incluirá el artículo original
            }
        },
        {
            "$match": {
                "_id": {"$ne": article_id}  # Excluir el artículo original
            }
        },
        {
            "$project": {
                "titulo": 1,
                "metadata.categoria": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    return list(db.articles.aggregate(pipeline))
```

---

### 6.2 Análisis de tendencias temporales

```python
def analizar_tendencias(db, categoria=None):
    """
    Analizar tendencias de publicación por mes
    """
    
    match_stage = {}
    if categoria:
        match_stage = {"metadata.categoria": categoria}
    
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {
            "$group": {
                "_id": {
                    "año": {"$year": "$metadata.fecha_publicacion"},
                    "mes": {"$month": "$metadata.fecha_publicacion"}
                },
                "count": {"$sum": 1},
                "categorias": {"$addToSet": "$metadata.categoria"}
            }
        },
        {
            "$sort": {"_id.año": -1, "_id.mes": -1}
        }
    ]
    
    return list(db.articles.aggregate(pipeline))
```

---

### 6.3 Métricas de rendimiento del sistema

```python
def obtener_metricas_sistema(db):
    """
    Obtener métricas del sistema RAG
    """
    
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_queries": {"$sum": 1},
                "avg_tiempo_busqueda": {"$avg": "$metricas.tiempo_busqueda_ms"},
                "avg_tiempo_llm": {"$avg": "$metricas.tiempo_llm_ms"},
                "avg_tiempo_total": {"$avg": "$metricas.tiempo_total_ms"},
                "queries_por_tipo": {
                    "$push": {
                        "tipo": "$query_type",
                        "timestamp": "$timestamp"
                    }
                }
            }
        }
    ]
    
    return list(db.query_history.aggregate(pipeline))
```

---

## 7. Ejemplos de Consultas para el Entregable 2

### Caso de Prueba 1: Búsqueda Semántica
```python
query = "¿Qué documentos hablan sobre sostenibilidad ambiental en tecnología?"
respuesta, docs = rag_query(query, db, model)
```

### Caso de Prueba 2: Filtros Híbridos
```python
query_embedding = model.encode("tecnología blockchain").tolist()

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_articles",
            "path": "texto_embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 10,
            "filter": {
                "$and": [
                    {"metadata.idioma": {"$eq": "en"}},
                    {"metadata.categoria": {"$eq": "Blockchain"}},
                    {"metadata.fecha_publicacion": {"$gte": datetime(2024, 1, 1)}}
                ]
            }
        }
    }
]
```

### Caso de Prueba 3: Búsqueda Multimodal
```python
# Buscar imágenes similares a una imagen dada
query_image_embedding = [...]  # Embedding de la imagen de entrada

pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index_images",
            "path": "image_embedding",
            "queryVector": query_image_embedding,
            "numCandidates": 50,
            "limit": 10,
            "filter": {"metadata.tipo": "diagrama"}
        }
    }
]
```

### Caso de Prueba 4: RAG Complejo
```python
query = "Explica las principales tendencias en computación en la nube según los documentos de 2024"
respuesta, docs = rag_query(query, db, model)
```

---

## 📊 Resumen de Operadores Usados

| Operador | Uso | Ejemplo |
|----------|-----|---------|
| `$match` | Filtrar documentos | `{"categoria": "ML"}` |
| `$project` | Seleccionar campos | `{"titulo": 1, "tags": 1}` |
| `$group` | Agrupar y agregar | Contar por categoría |
| `$lookup` | Join entre colecciones | Unir articles con images |
| `$unwind` | Descomponer arrays | Analizar tags individuales |
| `$sort` | Ordenar resultados | Por fecha descendente |
| `$limit` | Limitar resultados | Top 10 |
| `$text` | Búsqueda de texto | Palabras clave |
| `$vectorSearch` | Búsqueda semántica | Similaridad coseno |

---

**Nota:** Todos estos ejemplos requieren tener datos cargados en la base de datos. Para el Entregable 2, implementarás los scripts de carga y podrás probar estas consultas.
