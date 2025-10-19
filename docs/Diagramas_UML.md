# 📊 Diagramas UML del Sistema RAG

## 1. Diagrama de Colecciones (Estructura de Datos)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COLECCIÓN: articles                          │
├─────────────────────────────────────────────────────────────────────┤
│ PK  _id                    : ObjectId                                │
│     titulo                 : String(5-200)                           │
│     contenido              : String(min:100)                         │
│     resumen                : String(max:500)                         │
│     texto_embedding        : Array[Float](384)                       │
│                                                                      │
│     metadata {                                                       │
│         fecha_publicacion  : Date                                    │
│         idioma            : Enum[es, en]                            │
│         categoria         : Enum[ML, Backend, Frontend, ...]        │
│         dificultad        : Enum[basico, intermedio, avanzado]      │
│         tiempo_lectura_min: Integer(1-120)                          │
│         fuente            : String(URL)                              │
│     }                                                                │
│                                                                      │
│     autor {                                                          │
│         nombre            : String(2-100)                            │
│         perfil            : String(URL)                              │
│     }                                                                │
│                                                                      │
│     tags                   : Array[String](max:10)                   │
│ FK  imagenes               : Array[ObjectId] ───────────┐            │
│                                                         │            │
│     estadisticas {                                      │            │
│         vistas            : Integer(>=0)                │            │
│         valoracion        : Float(0.0-5.0)              │            │
│     }                                                   │            │
│                                                         │            │
│     fecha_creacion         : Date                       │            │
│     fecha_actualizacion    : Date                       │            │
└─────────────────────────────────────────────────────────┼────────────┘
                                                          │
                                                          │  1:N
                                                          │
┌─────────────────────────────────────────────────────────▼────────────┐
│                         COLECCIÓN: images                             │
├──────────────────────────────────────────────────────────────────────┤
│ PK  _id                    : ObjectId                                 │
│     nombre                 : String(3-100)                            │
│     descripcion            : String(max:500)                          │
│     url                    : String(URL)                              │
│     image_embedding        : Array[Float](512)                        │
│                                                                       │
│     metadata {                                                        │
│         formato           : Enum[png, jpg, svg, gif, webp]           │
│         tamaño_kb         : Integer(1-5120)                          │
│         dimensiones {                                                 │
│             ancho         : Integer                                   │
│             alto          : Integer                                   │
│         }                                                             │
│         tipo              : Enum[diagrama, screenshot, grafico, ...]  │
│     }                                                                 │
│                                                                       │
│     tags                   : Array[String](max:15)                    │
│     fecha_creacion         : Date                                     │
└──────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────┐
│                    COLECCIÓN: query_history                           │
├──────────────────────────────────────────────────────────────────────┤
│ PK  _id                    : ObjectId                                 │
│     query_text             : String(3-500)                            │
│     query_type             : Enum[semantic, hybrid, image, text]      │
│     query_embedding        : Array[Float]                             │
│                                                                       │
│     filtros_aplicados {                                               │
│         idioma            : Enum[es, en]                             │
│         categoria         : String                                    │
│         fecha_desde       : Date                                      │
│         fecha_hasta       : Date                                      │
│     }                                                                 │
│                                                                       │
│     resultados {                                                      │
│         count             : Integer(>=0)                              │
│ FK      top_docs          : Array[ObjectId]                          │
│         scores            : Array[Float](0.0-1.0)                    │
│     }                                                                 │
│                                                                       │
│     metricas {                                                        │
│         tiempo_busqueda_ms: Integer(>=0)                             │
│         tiempo_llm_ms     : Integer(>=0)                             │
│         tiempo_total_ms   : Integer(>=0)                             │
│     }                                                                 │
│                                                                       │
│     respuesta_generada     : String(max:5000)                         │
│     timestamp              : Date                                     │
│                                                                       │
│     user_feedback {                                                   │
│         util              : Boolean                                   │
│         comentario        : String(max:500)                           │
│     }                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de Relaciones

```
                    ┌──────────────┐
                    │   articles   │
                    ├──────────────┤
                    │ - _id        │
                    │ - titulo     │
                    │ - contenido  │
                    │ - embedding  │
                    │ - metadata   │
                    │ - imagenes[] │
                    └──────┬───────┘
                           │
                           │ 1:N
                           │ (Referenced)
                           │
                    ┌──────▼───────┐
                    │    images    │
                    ├──────────────┤
                    │ - _id        │
                    │ - nombre     │
                    │ - url        │
                    │ - embedding  │
                    │ - metadata   │
                    └──────────────┘


        ┌─────────────────────────────────────┐
        │         query_history                │
        ├─────────────────────────────────────┤
        │ - query_text                         │
        │ - query_type                         │
        │ - resultados.top_docs[] ────────┐   │
        └─────────────────────────────────┘   │
                                              │ N:N
                                              │ (Referencia débil)
                                              │
                                    ┌─────────▼────────┐
                                    │    articles      │
                                    └──────────────────┘
```

---

## 3. Diagrama de Flujo del Sistema RAG

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       │ 1. Query
       ▼
┌─────────────────────┐
│  Query Processor    │
│  - Validar input    │
│  - Generar embedding│
└──────┬──────────────┘
       │
       │ 2. Embedding Vector
       ▼
┌─────────────────────────────┐
│   MongoDB Atlas             │
│  ┌─────────────────────┐    │
│  │  Vector Search      │    │
│  │  ($vectorSearch)    │    │
│  └──────┬──────────────┘    │
│         │                   │
│         │ 3. Filtros        │
│  ┌──────▼──────────────┐    │
│  │  Hybrid Search      │    │
│  │  (filters + vector) │    │
│  └──────┬──────────────┘    │
└─────────┼───────────────────┘
          │
          │ 4. Top-K Documentos
          ▼
┌─────────────────────┐
│  Context Builder    │
│  - Concatenar docs  │
│  - Formatear prompt │
└──────┬──────────────┘
       │
       │ 5. Prompt + Context
       ▼
┌─────────────────────┐
│   LLM (Groq/Llama) │
│  - Generar respuesta│
└──────┬──────────────┘
       │
       │ 6. Respuesta generada
       ▼
┌─────────────────────┐
│   Query History     │
│  - Guardar query    │
│  - Guardar métricas │
└──────┬──────────────┘
       │
       │ 7. Respuesta final
       ▼
┌─────────────┐
│   Usuario   │
└─────────────┘
```

---

## 4. Diagrama de Arquitectura de Componentes

```
┌───────────────────────────────────────────────────────────────────┐
│                        FRONTEND / API CLIENT                       │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 │ HTTP/REST
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   /search    │  │    /rag      │  │   /stats     │            │
│  │   endpoint   │  │   endpoint   │  │   endpoint   │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                    │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────────────────┐
│                      SERVICES LAYER                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │
│  │  Embedding     │  │  Search        │  │  Analytics     │       │
│  │  Service       │  │  Service       │  │  Service       │       │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘       │
│           │                   │                   │                │
└───────────┼───────────────────┼───────────────────┼────────────────┘
            │                   │                   │
            │                   │                   │
┌───────────▼───────────────────▼───────────────────▼────────────────┐
│                      DATA ACCESS LAYER                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │              PyMongo Client                             │         │
│  └────────────────────┬───────────────────────────────────┘         │
└───────────────────────┼─────────────────────────────────────────────┘
                        │
                        │ MongoDB Protocol
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                      MONGODB ATLAS                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   articles   │  │    images    │  │query_history │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │           Atlas Vector Search Engine                 │         │
│  │  - kNN Search (cosine similarity)                    │         │
│  │  - Hybrid queries (filters + vectors)                │         │
│  └──────────────────────────────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────┘


┌───────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                               │
│  ┌────────────────┐                  ┌────────────────┐           │
│  │  Groq API      │                  │ HuggingFace    │           │
│  │  (LLM)         │                  │ (Embeddings)   │           │
│  └────────────────┘                  └────────────────┘           │
└───────────────────────────────────────────────────────────────────┘
```

---

## 5. Diagrama de Secuencia: Consulta RAG

```
Usuario    API      Embedder   MongoDB   VectorSearch   LLM      History
  │         │          │          │            │         │          │
  │──Query──▶│          │          │            │         │          │
  │         │          │          │            │         │          │
  │         │─Embed───▶│          │            │         │          │
  │         │          │          │            │         │          │
  │         │◀─Vector──│          │            │         │          │
  │         │          │          │            │         │          │
  │         │────$vectorSearch────▶            │         │          │
  │         │          │          │            │         │          │
  │         │          │          │◀───kNN─────│         │          │
  │         │          │          │            │         │          │
  │         │◀───Top-K Docs───────│            │         │          │
  │         │          │          │            │         │          │
  │         │─────Build Prompt────────────────────────▶  │          │
  │         │          │          │            │         │          │
  │         │◀──────Generated Response────────────────────│          │
  │         │          │          │            │         │          │
  │         │──────────────────Save Metrics───────────────────────▶ │
  │         │          │          │            │         │          │
  │◀Response│          │          │            │         │          │
  │         │          │          │            │         │          │
```

---

## 6. Modelo Entidad-Relación Simplificado

```
 ┌─────────────────────────┐
 │      ARTICLE            │
 ├─────────────────────────┤
 │ PK: _id                 │
 │ titulo                  │
 │ contenido               │
 │ texto_embedding [384]   │
 │ metadata.categoria      │
 │ metadata.idioma         │
 │ tags[]                  │
 └───────┬─────────────────┘
         │
         │ imagenes[]
         │ (Array de ObjectIds)
         │
         │ 1        N
         └─────────┐
                   │
         ┌─────────▼─────────────┐
         │      IMAGE            │
         ├───────────────────────┤
         │ PK: _id               │
         │ nombre                │
         │ url                   │
         │ image_embedding [512] │
         │ metadata.tipo         │
         │ tags[]                │
         └───────────────────────┘


 ┌─────────────────────────┐
 │   QUERY_HISTORY         │
 ├─────────────────────────┤
 │ PK: _id                 │
 │ query_text              │
 │ query_type              │
 │ query_embedding[]       │
 │ resultados.top_docs[]   │────┐
 │ metricas.tiempo_ms      │    │ (Referencias débiles)
 │ respuesta_generada      │    │
 │ timestamp               │    │
 └─────────────────────────┘    │
                                │
                    ┌───────────▼────────────┐
                    │    ARTICLE (ref)       │
                    └────────────────────────┘
```

---

## 7. Estrategia de Indexing Visual

```
COLECCIÓN: articles
═══════════════════════════════════════════════════════════

📊 ÍNDICES TRADICIONALES:
┌──────────────────────────────────────────────────┐
│  idx_fecha_idioma (Compuesto)                    │
│  {metadata.fecha_publicacion: -1, idioma: 1}     │
│  Uso: Queries filtradas por fecha e idioma       │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  idx_text_search (Text Index)                    │
│  {titulo: text, contenido: text}                 │
│  Uso: Búsqueda de texto completo                 │
│  Weights: titulo=10, contenido=5                 │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  idx_tags (Multikey)                             │
│  {tags: 1}                                       │
│  Uso: Filtrado por tags                          │
└──────────────────────────────────────────────────┘


🔍 ÍNDICE VECTORIAL (Atlas Search):
┌──────────────────────────────────────────────────┐
│  vector_index_articles                           │
│  ┌────────────────────────────────────────────┐  │
│  │ texto_embedding [384 dims]                 │  │
│  │ similarity: cosine                         │  │
│  │                                            │  │
│  │ Filtros soportados:                        │  │
│  │  - metadata.idioma                         │  │
│  │  - metadata.categoria                      │  │
│  │  - metadata.fecha_publicacion              │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  Uso: Búsqueda semántica + filtros híbridos     │
└──────────────────────────────────────────────────┘
```

---

## 8. Comparación Embedding vs Referencing

```
┌─────────────────────────────────────────────────────────────────┐
│                     ESTRATEGIA: EMBEDDED                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  {                                                               │
│    "_id": ObjectId("..."),                                       │
│    "titulo": "Artículo",                                         │
│    "metadata": {              ◄── Embebido (Embedded)           │
│      "fecha": Date,                                              │
│      "idioma": "es",                                             │
│      "categoria": "Backend"                                      │
│    },                                                            │
│    "autor": {                 ◄── Embebido (Embedded)           │
│      "nombre": "Juan",                                           │
│      "perfil": "url"                                             │
│    }                                                             │
│  }                                                               │
│                                                                  │
│  ✅ Ventajas:                                                    │
│     - 1 sola query                                               │
│     - Atomicidad garantizada                                     │
│     - Mejor rendimiento en lecturas                              │
│                                                                  │
│  ❌ Desventajas:                                                 │
│     - Duplicación si se comparte                                 │
│     - Crece el documento                                         │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   ESTRATEGIA: REFERENCED                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  COLECCIÓN: articles                                             │
│  {                                                               │
│    "_id": ObjectId("doc1"),                                      │
│    "titulo": "Artículo",                                         │
│    "imagenes": [             ◄── Referencias (Referenced)       │
│      ObjectId("img1"),                                           │
│      ObjectId("img2")                                            │
│    ]                                                             │
│  }                                                               │
│                                                                  │
│  COLECCIÓN: images                                               │
│  {                                                               │
│    "_id": ObjectId("img1"),  ◄── Documento separado             │
│    "url": "https://...",                                         │
│    "image_embedding": [...]                                      │
│  }                                                               │
│                                                                  │
│  ✅ Ventajas:                                                    │
│     - No hay duplicación                                         │
│     - Reutilización (N:N)                                        │
│     - Documentos más pequeños                                    │
│                                                                  │
│  ❌ Desventajas:                                                 │
│     - Requiere múltiples queries o $lookup                       │
│     - Mayor complejidad                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Pipeline de Agregación Ejemplo

```
┌─────────────────────────────────────────────────────────┐
│  PIPELINE: Buscar artículos de ML en español con imgs   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  db.articles.aggregate([                                 │
│                                                          │
│    ┌────────────────────────────────────┐               │
│    │ $match                              │               │
│    │ {                                   │               │
│    │   "metadata.categoria": "ML",       │               │
│    │   "metadata.idioma": "es"           │               │
│    │ }                                   │               │
│    └────────────┬───────────────────────┘               │
│                 │                                        │
│                 ▼                                        │
│    ┌────────────────────────────────────┐               │
│    │ $lookup                             │               │
│    │ {                                   │               │
│    │   from: "images",                   │               │
│    │   localField: "imagenes",           │               │
│    │   foreignField: "_id",              │               │
│    │   as: "imagenes_data"               │               │
│    │ }                                   │               │
│    └────────────┬───────────────────────┘               │
│                 │                                        │
│                 ▼                                        │
│    ┌────────────────────────────────────┐               │
│    │ $project                            │               │
│    │ {                                   │               │
│    │   titulo: 1,                        │               │
│    │   resumen: 1,                       │               │
│    │   "imagenes_data.url": 1            │               │
│    │ }                                   │               │
│    └────────────┬───────────────────────┘               │
│                 │                                        │
│                 ▼                                        │
│    ┌────────────────────────────────────┐               │
│    │ $limit                              │               │
│    │ 10                                  │               │
│    └─────────────────────────────────────┘              │
│                                                          │
│  ])                                                      │
└─────────────────────────────────────────────────────────┘
```

---

**Leyenda:**
- `PK` = Primary Key (_id en MongoDB)
- `FK` = Foreign Key (referencia a otra colección)
- `→` = Relación Referenced
- `{}` = Documento embebido
- `[]` = Array

