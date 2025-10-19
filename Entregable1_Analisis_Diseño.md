# Entregable 1: Diseño y Configuración
# Sistema RAG de Tecnología e Innovación

**Proyecto:** Sistema RAG NoSQL con MongoDB  
**Dominio:** Tecnología, Innovación y Ciencia Computacional  
**Fecha:** Octubre 2025  
**Autor:** Alejandro

---

## 📖 Tabla de Contenidos

1. [Universo del Discurso y Análisis de Requerimientos](#1-universo-del-discurso-y-análisis-de-requerimientos)
2. [Justificación de Decisiones de Modelado NoSQL](#2-justificación-de-decisiones-de-modelado-nosql)
3. [Comparación Embedding vs. Referencing](#3-comparación-embedding-vs-referencing)
4. [Diseño de Esquema NoSQL](#4-diseño-de-esquema-nosql)
5. [Estrategias de Indexing](#5-estrategias-de-indexing)
6. [Schema Validation Rules](#6-schema-validation-rules)
7. [Configuración de Entorno](#7-configuración-de-entorno)

---

## 1. Universo del Discurso y Análisis de Requerimientos

### 1.1 Descripción del Dominio

El sistema RAG estará enfocado en el dominio de **Tecnología e Innovación**, abarcando:

- 🤖 **Inteligencia Artificial y Machine Learning**
- 💻 **Desarrollo de Software y Programación**
- 🌐 **Tecnologías Web y Cloud Computing**
- 🔐 **Ciberseguridad**
- 📱 **Desarrollo Mobile y IoT**
- 🧬 **Biotecnología y Ciencia de Datos**

### 1.2 Objetivos del Sistema

El sistema debe ser capaz de:

1. **Almacenar y organizar** artículos técnicos, tutoriales, y documentación sobre tecnología
2. **Procesar y vectorizar** contenido multimodal (texto + imágenes de diagramas, arquitecturas, código)
3. **Responder preguntas complejas** sobre tendencias tecnológicas, comparaciones de frameworks, mejores prácticas
4. **Realizar búsquedas híbridas** combinando filtros (fecha, idioma, categoría) con similaridad semántica
5. **Generar respuestas contextualizadas** usando documentos relevantes como base de conocimiento

### 1.3 Casos de Uso Principales

#### CU-1: Búsqueda Semántica de Artículos
**Actor:** Usuario técnico  
**Descripción:** Buscar artículos relacionados con un concepto tecnológico específico  
**Ejemplo:** *"¿Qué artículos hablan sobre arquitecturas de microservicios?"*

#### CU-2: Consultas Híbridas con Filtros
**Actor:** Desarrollador/Investigador  
**Descripción:** Buscar contenido específico con restricciones de metadatos  
**Ejemplo:** *"Tutoriales en español sobre React publicados en 2024"*

#### CU-3: Búsqueda de Imágenes Técnicas
**Actor:** Estudiante/Profesional  
**Descripción:** Encontrar diagramas, arquitecturas o visualizaciones similares  
**Ejemplo:** *"Diagramas de arquitectura similar a este patrón MVC"*

#### CU-4: Preguntas RAG Complejas
**Actor:** Usuario final  
**Descripción:** Obtener respuestas sintetizadas desde múltiples fuentes  
**Ejemplo:** *"Compara las ventajas de usar PostgreSQL vs MongoDB para aplicaciones de e-commerce"*

#### CU-5: Análisis de Tendencias
**Actor:** Analista técnico  
**Descripción:** Identificar tendencias tecnológicas emergentes  
**Ejemplo:** *"¿Cuáles son las tecnologías más mencionadas en artículos de 2024?"*

### 1.4 Requerimientos Funcionales

| ID | Requerimiento | Prioridad |
|----|--------------|-----------|
| RF-01 | Almacenar mínimo 100 documentos de texto sobre tecnología | Alta |
| RF-02 | Almacenar mínimo 50 imágenes técnicas (diagramas, arquitecturas) | Alta |
| RF-03 | Generar embeddings de texto usando `all-MiniLM-L6-v2` | Alta |
| RF-04 | Generar embeddings de imágenes usando `CLIP` | Alta |
| RF-05 | Realizar búsqueda vectorial con $vectorSearch | Alta |
| RF-06 | Aplicar filtros por fecha, idioma, categoría | Media |
| RF-07 | Integrar LLM (Groq/Llama 3.1) para generación de respuestas | Alta |
| RF-08 | Registrar historial de consultas para análisis | Media |
| RF-09 | Soportar búsqueda multimodal (texto → imagen, imagen → texto) | Media |
| RF-10 | Validar esquemas de documentos al insertar | Baja |

### 1.5 Requerimientos No Funcionales

| ID | Requerimiento | Métrica |
|----|--------------|---------|
| RNF-01 | Tiempo de respuesta de búsqueda vectorial | < 500ms |
| RNF-02 | Tiempo de respuesta del pipeline RAG completo | < 3s |
| RNF-03 | Precisión de recuperación (top-5) | > 80% |
| RNF-04 | Disponibilidad del sistema | 99% |
| RNF-05 | Escalabilidad | Soportar hasta 1000 documentos en M0 |

### 1.6 Fuentes de Datos

#### Texto (100+ documentos):
- **DEV.to API**: Artículos sobre desarrollo de software
- **Medium API**: Posts técnicos sobre tecnología
- **GitHub README**: Documentación de proyectos populares
- **ArXiv**: Papers sobre Computer Science
- **Stack Overflow**: Preguntas/respuestas técnicas bien valoradas

#### Imágenes (50+):
- **Unsplash**: Fotos de tecnología, oficinas, hardware
- **GitHub**: Diagramas de arquitectura de repositorios
- **Wikipedia Commons**: Imágenes técnicas con licencia libre
- **Wikimedia**: Diagramas de conceptos tecnológicos

---

## 2. Justificación de Decisiones de Modelado NoSQL

### 2.1 ¿Por qué MongoDB para este RAG?

#### Ventajas de MongoDB en este contexto:

1. **Esquema Flexible**
   - Los artículos técnicos tienen estructuras variables (algunos con código, otros con tablas, otros con listas)
   - No todos los documentos tienen los mismos campos (ej: algunos tienen autor, otros son anónimos)
   - Fácil evolución del esquema sin migraciones complejas

2. **Atlas Vector Search Nativo**
   - Búsqueda vectorial integrada sin necesidad de herramientas externas (como Pinecone o Weaviate)
   - Combinación de filtros tradicionales con búsqueda semántica en una sola query
   - Índices kNN optimizados para embeddings

3. **Aggregation Framework Potente**
   - Pipelines complejos para análisis de tendencias
   - Operador `$lookup` para joins entre documentos e imágenes
   - `$facet` para búsquedas multicriterio

4. **Escalabilidad Horizontal**
   - Sharding nativo para crecer según necesidades
   - Replicación automática en Atlas

5. **Almacenamiento de Datos Grandes**
   - GridFS para imágenes de alta resolución
   - Documentos de hasta 16MB (suficiente para artículos largos)

### 2.2 Diseño de Colecciones

#### Decisión: 3 Colecciones Principales

```
1. articles        → Documentos de texto con embeddings
2. images          → Imágenes técnicas con embeddings
3. query_history   → Registro de consultas
```

**Justificación:**

- **Separación de Responsabilidades**: Cada colección tiene un propósito claro
- **Optimización de Consultas**: Los índices vectoriales son más eficientes en colecciones separadas
- **Reutilización**: Una imagen puede estar vinculada a múltiples artículos
- **Escalabilidad**: Fácil agregar nuevas colecciones (ej: `videos`, `podcasts`)

### 2.3 Estrategia de Modelado por Campo

| Campo | Estrategia | Justificación |
|-------|-----------|---------------|
| `titulo`, `contenido` | **Embedded** | Pequeños, siempre se consultan juntos |
| `texto_embedding` (384 dims) | **Embedded** | Necesario en cada query vectorial |
| `metadata` (fecha, idioma, etc.) | **Embedded** | Usados en filtros híbridos |
| `imagenes` (array de IDs) | **Referenced** | Imágenes pesadas, reutilizables |
| `autor` | **Embedded** | Objeto pequeño, alta cohesión |
| `tags` | **Embedded** | Array pequeño, búsqueda frecuente |

---

## 3. Comparación Embedding vs. Referencing

### 3.1 Análisis Detallado

#### 📋 Tabla Comparativa

| Criterio | Embedding (Embebido) | Referencing (Referenciado) | Decisión en el Proyecto |
|----------|---------------------|---------------------------|------------------------|
| **Tamaño de datos** | < 1KB | > 10KB | Metadatos: Embedded / Imágenes: Referenced |
| **Frecuencia de acceso** | Siempre juntos | Acceso independiente | Título+contenido: Embedded |
| **Relación 1:1 vs 1:N** | 1:1 | 1:N o N:N | Metadatos (1:1): Embedded / Imágenes (N:N): Referenced |
| **Actualización** | Todo el documento | Solo el referenciado | Metadatos estáticos: Embedded |
| **Consistencia** | Automática | Requiere transacciones | - |
| **Performance** | 1 query | 2+ queries (con $lookup) | Equilibrio según caso |

### 3.2 Casos Específicos del Proyecto

#### ✅ EMBEDDED: Metadatos del Artículo

```json
{
  "_id": ObjectId("..."),
  "titulo": "Introducción a GraphQL",
  "metadata": {
    "fecha": ISODate("2024-03-15"),
    "idioma": "es",
    "categoria": "Backend",
    "dificultad": "intermedio",
    "tiempo_lectura": 10
  }
}
```

**Razón:** 
- Tamaño pequeño (~200 bytes)
- Siempre se consultan juntos
- No se comparten entre documentos
- Relación 1:1

#### ✅ EMBEDDED: Embeddings Vectoriales

```json
{
  "_id": ObjectId("..."),
  "texto_embedding": [0.023, -0.451, 0.889, ...] // 384 floats
}
```

**Razón:**
- Crítico para búsqueda vectorial (debe estar en el mismo documento)
- Tamaño fijo (~1.5KB)
- No tiene sentido consultarlo por separado

#### ✅ REFERENCED: Imágenes

```json
// Colección: articles
{
  "_id": ObjectId("doc1"),
  "titulo": "Patrones de Arquitectura",
  "imagenes": [
    ObjectId("img1"),
    ObjectId("img2")
  ]
}

// Colección: images
{
  "_id": ObjectId("img1"),
  "url": "https://...",
  "image_embedding": [...],
  "tamaño_kb": 450
}
```

**Razón:**
- Imágenes pesadas (50KB - 2MB)
- Reutilizables en múltiples artículos
- Relación N:N (un diagrama puede ilustrar varios conceptos)
- Se consultan independientemente en búsqueda visual

#### ✅ EMBEDDED: Autor del Artículo

```json
{
  "_id": ObjectId("..."),
  "autor": {
    "nombre": "Juan Pérez",
    "perfil": "https://github.com/juanperez"
  }
}
```

**Razón:**
- Datos pequeños
- No hay CRUD independiente del autor
- Para este proyecto, no necesitamos una colección `authors`

### 3.3 Ventajas y Desventajas por Estrategia

#### Embedding

**✅ Ventajas:**
- Una sola consulta para obtener todo
- Atomicidad garantizada
- Mejor rendimiento en lecturas
- Simplicidad en el código

**❌ Desventajas:**
- Duplicación de datos si se comparten
- Tamaño del documento crece
- Difícil actualizar datos compartidos

#### Referencing

**✅ Ventajas:**
- No hay duplicación
- Documentos más pequeños
- Escalabilidad para datos grandes
- Actualizaciones centralizadas

**❌ Desventajas:**
- Requiere múltiples consultas o $lookup
- Complejidad en el código
- Posible inconsistencia

### 3.4 Conclusión

Para el RAG de Tecnología:
- **80% Embedding**: Metadatos, embeddings, autor, tags
- **20% Referencing**: Imágenes grandes, documentos relacionados

---

## 4. Diseño de Esquema NoSQL

### 4.1 Diagrama de Colecciones

```
┌─────────────────────────────────────────────────────────────┐
│                      COLECCIÓN: articles                     │
├─────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                │
│ titulo: String                                               │
│ contenido: String (texto completo)                           │
│ resumen: String                                              │
│ texto_embedding: Array<Float> [384]                          │
│ metadata: {                                                  │
│   fecha_publicacion: ISODate                                 │
│   idioma: String (es|en)                                     │
│   categoria: String (AI|Backend|Frontend|DevOps|...)         │
│   dificultad: String (basico|intermedio|avanzado)            │
│   tiempo_lectura_min: Number                                 │
│   fuente: String (url original)                              │
│ }                                                            │
│ autor: {                                                     │
│   nombre: String                                             │
│   perfil: String (url)                                       │
│ }                                                            │
│ tags: Array<String>                                          │
│ imagenes: Array<ObjectId> ──────────┐                        │
│ estadisticas: {                     │                        │
│   vistas: Number                    │                        │
│   valoracion: Number                │                        │
│ }                                   │                        │
│ fecha_creacion: ISODate             │                        │
│ fecha_actualizacion: ISODate        │                        │
└─────────────────────────────────────┼───────────────────────┘
                                      │
                                      │ REFERENCIA (1:N)
                                      │
┌─────────────────────────────────────▼───────────────────────┐
│                      COLECCIÓN: images                       │
├─────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                │
│ nombre: String                                               │
│ descripcion: String                                          │
│ url: String (Cloudinary/S3/GridFS)                           │
│ image_embedding: Array<Float> [512]                          │
│ metadata: {                                                  │
│   formato: String (png|jpg|svg)                              │
│   tamaño_kb: Number                                          │
│   dimensiones: {                                             │
│     ancho: Number                                            │
│     alto: Number                                             │
│   }                                                          │
│   tipo: String (diagrama|screenshot|grafico|foto)            │
│ }                                                            │
│ tags: Array<String>                                          │
│ fecha_creacion: ISODate                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   COLECCIÓN: query_history                   │
├─────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                │
│ query_text: String                                           │
│ query_type: String (semantic|hybrid|image)                   │
│ query_embedding: Array<Float> [384]                          │
│ filtros_aplicados: {                                         │
│   idioma: String                                             │
│   categoria: String                                          │
│   fecha_desde: ISODate                                       │
│   fecha_hasta: ISODate                                       │
│ }                                                            │
│ resultados: {                                                │
│   count: Number                                              │
│   top_docs: Array<ObjectId>                                  │
│   scores: Array<Float>                                       │
│ }                                                            │
│ metricas: {                                                  │
│   tiempo_busqueda_ms: Number                                 │
│   tiempo_llm_ms: Number                                      │
│   tiempo_total_ms: Number                                    │
│ }                                                            │
│ respuesta_generada: String                                   │
│ timestamp: ISODate                                           │
│ user_feedback: {                                             │
│   util: Boolean                                              │
│   comentario: String                                         │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Ejemplos de Documentos

#### Ejemplo 1: Artículo sobre Machine Learning

```json
{
  "_id": ObjectId("67123abc45def67890123456"),
  "titulo": "Introducción a Redes Neuronales Convolucionales",
  "contenido": "Las Redes Neuronales Convolucionales (CNN) son un tipo de red neuronal profunda especialmente diseñada para procesar datos con estructura de grilla, como imágenes. A diferencia de las redes neuronales completamente conectadas, las CNN aprovechan la estructura espacial de los datos mediante capas de convolución que aplican filtros...",
  "resumen": "Explicación básica de CNNs, sus componentes principales y aplicaciones en visión por computadora.",
  "texto_embedding": [0.023, -0.451, 0.889, 0.234, -0.667, 0.123, ...], // 384 valores
  "metadata": {
    "fecha_publicacion": ISODate("2024-08-15T10:30:00Z"),
    "idioma": "es",
    "categoria": "Machine Learning",
    "dificultad": "intermedio",
    "tiempo_lectura_min": 12,
    "fuente": "https://dev.to/ejemplo-cnn"
  },
  "autor": {
    "nombre": "María García",
    "perfil": "https://github.com/mariagarcia"
  },
  "tags": ["deep-learning", "computer-vision", "python", "tensorflow", "cnn"],
  "imagenes": [
    ObjectId("67123abc45def67890111111"),
    ObjectId("67123abc45def67890222222")
  ],
  "estadisticas": {
    "vistas": 1523,
    "valoracion": 4.7
  },
  "fecha_creacion": ISODate("2024-10-01T08:00:00Z"),
  "fecha_actualizacion": ISODate("2024-10-01T08:00:00Z")
}
```

#### Ejemplo 2: Artículo sobre Backend

```json
{
  "_id": ObjectId("67123abc45def67890123457"),
  "titulo": "GraphQL vs REST: Comparativa completa 2024",
  "contenido": "GraphQL es un lenguaje de consulta para APIs desarrollado por Facebook en 2015. A diferencia de REST, que expone múltiples endpoints fijos, GraphQL permite a los clientes solicitar exactamente los datos que necesitan mediante una única consulta...",
  "resumen": "Análisis comparativo entre GraphQL y REST API, ventajas, desventajas y casos de uso recomendados.",
  "texto_embedding": [0.156, 0.234, -0.678, 0.445, 0.890, -0.123, ...],
  "metadata": {
    "fecha_publicacion": ISODate("2024-09-20T14:20:00Z"),
    "idioma": "es",
    "categoria": "Backend",
    "dificultad": "intermedio",
    "tiempo_lectura_min": 15,
    "fuente": "https://medium.com/ejemplo-graphql"
  },
  "autor": {
    "nombre": "Carlos Rodríguez",
    "perfil": "https://twitter.com/carlosdev"
  },
  "tags": ["graphql", "rest", "api", "backend", "nodejs"],
  "imagenes": [
    ObjectId("67123abc45def67890333333")
  ],
  "estadisticas": {
    "vistas": 2847,
    "valoracion": 4.9
  },
  "fecha_creacion": ISODate("2024-10-02T10:15:00Z"),
  "fecha_actualizacion": ISODate("2024-10-02T10:15:00Z")
}
```

#### Ejemplo 3: Imagen - Diagrama de Arquitectura

```json
{
  "_id": ObjectId("67123abc45def67890111111"),
  "nombre": "arquitectura_cnn.png",
  "descripcion": "Diagrama que muestra las capas de una red neuronal convolucional típica: entrada, convolución, pooling, flatten y capas densas",
  "url": "https://res.cloudinary.com/tech-rag/image/upload/v1234/arquitectura_cnn.png",
  "image_embedding": [0.789, -0.234, 0.456, 0.123, -0.890, ...], // 512 valores
  "metadata": {
    "formato": "png",
    "tamaño_kb": 235,
    "dimensiones": {
      "ancho": 1200,
      "alto": 600
    },
    "tipo": "diagrama"
  },
  "tags": ["cnn", "arquitectura", "deep-learning", "diagrama"],
  "fecha_creacion": ISODate("2024-10-01T08:00:00Z")
}
```

#### Ejemplo 4: Query History

```json
{
  "_id": ObjectId("67123abc45def67890555555"),
  "query_text": "¿Cuáles son las mejores prácticas para diseñar APIs RESTful?",
  "query_type": "semantic",
  "query_embedding": [0.234, 0.567, -0.123, 0.890, ...],
  "filtros_aplicados": {
    "idioma": "es",
    "categoria": "Backend",
    "fecha_desde": ISODate("2024-01-01T00:00:00Z"),
    "fecha_hasta": ISODate("2024-12-31T23:59:59Z")
  },
  "resultados": {
    "count": 5,
    "top_docs": [
      ObjectId("67123abc45def67890123457"),
      ObjectId("67123abc45def67890123458"),
      ObjectId("67123abc45def67890123459")
    ],
    "scores": [0.92, 0.87, 0.85]
  },
  "metricas": {
    "tiempo_busqueda_ms": 245,
    "tiempo_llm_ms": 1823,
    "tiempo_total_ms": 2068
  },
  "respuesta_generada": "Las mejores prácticas para diseñar APIs RESTful incluyen: 1) Usar sustantivos para recursos, no verbos...",
  "timestamp": ISODate("2024-10-15T16:45:30Z"),
  "user_feedback": {
    "util": true,
    "comentario": "Respuesta muy completa y bien estructurada"
  }
}
```

---

## 5. Estrategias de Indexing

### 5.1 Índices Planificados

#### 🔍 Colección: `articles`

| Índice | Tipo | Campos | Propósito | Prioridad |
|--------|------|--------|-----------|-----------|
| `idx_vector` | **Vector Search** | `texto_embedding` | Búsqueda semántica (kNN) | ⭐⭐⭐ |
| `idx_fecha_idioma` | **Compuesto** | `{metadata.fecha_publicacion: -1, metadata.idioma: 1}` | Queries híbridas filtradas | ⭐⭐⭐ |
| `idx_categoria` | **Simple** | `metadata.categoria` | Filtrado por categoría | ⭐⭐ |
| `idx_tags` | **Multikey** | `tags` | Búsqueda por tags | ⭐⭐ |
| `idx_texto` | **Text Search** | `{titulo: "text", contenido: "text"}` | Búsqueda de texto completo | ⭐⭐ |
| `idx_fecha` | **Simple** | `metadata.fecha_publicacion: -1` | Ordenar por recientes | ⭐ |

#### 🖼️ Colección: `images`

| Índice | Tipo | Campos | Propósito | Prioridad |
|--------|------|--------|-----------|-----------|
| `idx_image_vector` | **Vector Search** | `image_embedding` | Búsqueda visual por similaridad | ⭐⭐⭐ |
| `idx_tipo` | **Simple** | `metadata.tipo` | Filtrar por tipo de imagen | ⭐⭐ |
| `idx_tags_img` | **Multikey** | `tags` | Búsqueda por tags | ⭐⭐ |

#### 📊 Colección: `query_history`

| Índice | Tipo | Campos | Propósito | Prioridad |
|--------|------|--------|-----------|-----------|
| `idx_timestamp` | **Simple** | `timestamp: -1` | Análisis temporal | ⭐⭐ |
| `idx_query_type` | **Simple** | `query_type` | Agrupar por tipo | ⭐ |

### 5.2 Configuración de Índices Vectoriales (Atlas Search)

#### Índice Vectorial para Artículos

```json
{
  "name": "vector_index_articles",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "texto_embedding",
        "numDimensions": 384,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "metadata.idioma"
      },
      {
        "type": "filter",
        "path": "metadata.categoria"
      },
      {
        "type": "filter",
        "path": "metadata.fecha_publicacion"
      }
    ]
  }
}
```

#### Índice Vectorial para Imágenes

```json
{
  "name": "vector_index_images",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "image_embedding",
        "numDimensions": 512,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "metadata.tipo"
      }
    ]
  }
}
```

### 5.3 Justificación de Índices

#### ¿Por qué Cosine Similarity?
- Mide el ángulo entre vectores, no la magnitud
- Ideal para embeddings normalizados
- Mejor que Euclidean para espacios de alta dimensionalidad

#### ¿Por qué índices compuestos?
- `{fecha: -1, idioma: 1}` optimiza queries como: *"artículos recientes en español"*
- MongoDB puede usar un índice compuesto para múltiples filtros

#### ¿Por qué índice multikey en tags?
- Los tags son un array
- Permite búsquedas eficientes como: `{tags: "python"}`

---

## 6. Schema Validation Rules

### 6.1 Validación para `articles`

```javascript
db.createCollection("articles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["titulo", "contenido", "texto_embedding", "metadata", "fecha_creacion"],
      properties: {
        titulo: {
          bsonType: "string",
          minLength: 5,
          maxLength: 200,
          description: "Título del artículo (5-200 caracteres)"
        },
        contenido: {
          bsonType: "string",
          minLength: 100,
          description: "Contenido completo del artículo (min 100 caracteres)"
        },
        resumen: {
          bsonType: "string",
          maxLength: 500,
          description: "Resumen opcional del artículo"
        },
        texto_embedding: {
          bsonType: "array",
          minItems: 384,
          maxItems: 384,
          items: {
            bsonType: "double"
          },
          description: "Vector de embeddings (384 dimensiones)"
        },
        metadata: {
          bsonType: "object",
          required: ["fecha_publicacion", "idioma", "categoria"],
          properties: {
            fecha_publicacion: {
              bsonType: "date",
              description: "Fecha de publicación del artículo"
            },
            idioma: {
              bsonType: "string",
              enum: ["es", "en"],
              description: "Idioma del artículo (es o en)"
            },
            categoria: {
              bsonType: "string",
              enum: ["Machine Learning", "Backend", "Frontend", "DevOps", "Ciberseguridad", "Mobile", "Data Science", "Cloud", "IoT", "Blockchain"],
              description: "Categoría tecnológica del artículo"
            },
            dificultad: {
              bsonType: "string",
              enum: ["basico", "intermedio", "avanzado"],
              description: "Nivel de dificultad"
            },
            tiempo_lectura_min: {
              bsonType: "int",
              minimum: 1,
              maximum: 120,
              description: "Tiempo estimado de lectura en minutos"
            },
            fuente: {
              bsonType: "string",
              pattern: "^https?://",
              description: "URL de la fuente original"
            }
          }
        },
        autor: {
          bsonType: "object",
          properties: {
            nombre: {
              bsonType: "string",
              minLength: 2,
              maxLength: 100
            },
            perfil: {
              bsonType: "string",
              pattern: "^https?://"
            }
          }
        },
        tags: {
          bsonType: "array",
          maxItems: 10,
          items: {
            bsonType: "string",
            minLength: 2,
            maxLength: 30
          },
          description: "Tags del artículo (máximo 10)"
        },
        imagenes: {
          bsonType: "array",
          items: {
            bsonType: "objectId"
          },
          description: "Referencias a imágenes asociadas"
        },
        estadisticas: {
          bsonType: "object",
          properties: {
            vistas: {
              bsonType: "int",
              minimum: 0
            },
            valoracion: {
              bsonType: "double",
              minimum: 0.0,
              maximum: 5.0
            }
          }
        },
        fecha_creacion: {
          bsonType: "date",
          description: "Fecha de creación en el sistema"
        },
        fecha_actualizacion: {
          bsonType: "date",
          description: "Última actualización"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

### 6.2 Validación para `images`

```javascript
db.createCollection("images", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "url", "image_embedding", "metadata", "fecha_creacion"],
      properties: {
        nombre: {
          bsonType: "string",
          minLength: 3,
          maxLength: 100,
          description: "Nombre del archivo de imagen"
        },
        descripcion: {
          bsonType: "string",
          maxLength: 500,
          description: "Descripción de la imagen"
        },
        url: {
          bsonType: "string",
          pattern: "^https?://",
          description: "URL de la imagen"
        },
        image_embedding: {
          bsonType: "array",
          minItems: 512,
          maxItems: 512,
          items: {
            bsonType: "double"
          },
          description: "Vector de embeddings de imagen (512 dimensiones)"
        },
        metadata: {
          bsonType: "object",
          required: ["formato", "tamaño_kb", "tipo"],
          properties: {
            formato: {
              bsonType: "string",
              enum: ["png", "jpg", "jpeg", "svg", "gif", "webp"],
              description: "Formato de la imagen"
            },
            tamaño_kb: {
              bsonType: "int",
              minimum: 1,
              maximum: 5120,
              description: "Tamaño en KB (máx 5MB)"
            },
            dimensiones: {
              bsonType: "object",
              properties: {
                ancho: {
                  bsonType: "int",
                  minimum: 1
                },
                alto: {
                  bsonType: "int",
                  minimum: 1
                }
              }
            },
            tipo: {
              bsonType: "string",
              enum: ["diagrama", "screenshot", "grafico", "foto", "icono"],
              description: "Tipo de imagen"
            }
          }
        },
        tags: {
          bsonType: "array",
          maxItems: 15,
          items: {
            bsonType: "string",
            minLength: 2,
            maxLength: 30
          }
        },
        fecha_creacion: {
          bsonType: "date"
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})
```

### 6.3 Validación para `query_history`

```javascript
db.createCollection("query_history", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["query_text", "query_type", "timestamp"],
      properties: {
        query_text: {
          bsonType: "string",
          minLength: 3,
          maxLength: 500,
          description: "Texto de la consulta del usuario"
        },
        query_type: {
          bsonType: "string",
          enum: ["semantic", "hybrid", "image", "text"],
          description: "Tipo de búsqueda realizada"
        },
        query_embedding: {
          bsonType: "array",
          items: {
            bsonType: "double"
          }
        },
        filtros_aplicados: {
          bsonType: "object",
          properties: {
            idioma: {
              bsonType: "string",
              enum: ["es", "en"]
            },
            categoria: {
              bsonType: "string"
            },
            fecha_desde: {
              bsonType: "date"
            },
            fecha_hasta: {
              bsonType: "date"
            }
          }
        },
        resultados: {
          bsonType: "object",
          properties: {
            count: {
              bsonType: "int",
              minimum: 0
            },
            top_docs: {
              bsonType: "array",
              items: {
                bsonType: "objectId"
              }
            },
            scores: {
              bsonType: "array",
              items: {
                bsonType: "double",
                minimum: 0.0,
                maximum: 1.0
              }
            }
          }
        },
        metricas: {
          bsonType: "object",
          properties: {
            tiempo_busqueda_ms: {
              bsonType: "int",
              minimum: 0
            },
            tiempo_llm_ms: {
              bsonType: "int",
              minimum: 0
            },
            tiempo_total_ms: {
              bsonType: "int",
              minimum: 0
            }
          }
        },
        respuesta_generada: {
          bsonType: "string",
          maxLength: 5000
        },
        timestamp: {
          bsonType: "date",
          description: "Momento de la consulta"
        },
        user_feedback: {
          bsonType: "object",
          properties: {
            util: {
              bsonType: "bool"
            },
            comentario: {
              bsonType: "string",
              maxLength: 500
            }
          }
        }
      }
    }
  },
  validationLevel: "moderate",
  validationAction: "warn"
})
```

---

## 7. Configuración de Entorno

### 7.1 Configuración de MongoDB Atlas

#### Paso 1: Crear Cluster Gratuito (M0)

1. Ir a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Crear cuenta gratuita
3. Crear nuevo cluster:
   - **Tier:** M0 Sandbox (Free)
   - **Provider:** AWS/GCP/Azure (el más cercano a tu ubicación)
   - **Region:** Seleccionar la más cercana (ej: São Paulo, Virginia)
   - **Cluster Name:** `tech-rag-cluster`

#### Paso 2: Configurar Seguridad

**Network Access:**
```
IP Whitelist: 0.0.0.0/0 (permitir desde cualquier IP para desarrollo)
```

**Database User:**
```
Username: tech_rag_admin
Password: [Generar contraseña segura]
Role: Atlas Admin
```

#### Paso 3: Obtener Connection String

```
mongodb+srv://tech_rag_admin:<password>@tech-rag-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### 7.2 Estructura del Proyecto

```
ProyectoNoSQL/
│
├── config/
│   ├── db_config.py          # Configuración de MongoDB
│   └── .env.example          # Variables de entorno template
│
├── data/
│   ├── raw/                  # Datos crudos (JSON, CSV)
│   ├── processed/            # Datos procesados
│   └── images/               # Imágenes descargadas
│
├── scripts/
│   ├── 01_setup_database.py     # Crear colecciones y validaciones
│   ├── 02_create_indexes.py     # Crear índices
│   ├── 03_load_articles.py      # Cargar artículos
│   ├── 04_load_images.py        # Cargar imágenes
│   └── 05_test_connection.py   # Verificar conexión
│
├── notebooks/
│   └── exploratory_analysis.ipynb  # Análisis exploratorio
│
├── docs/
│   └── Entregable1_Analisis_Diseño.md  # Este documento
│
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno (NO subir a Git)
└── README.md                # Documentación del proyecto
```

### 7.3 Dependencias del Proyecto

#### `requirements.txt`

```txt
# MongoDB
pymongo==4.6.0
motor==3.3.2

# Machine Learning & Embeddings
sentence-transformers==2.2.2
torch==2.1.0
torchvision==0.16.0
pillow==10.1.0
transformers==4.35.0

# Data Processing
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0

# API & Web
requests==2.31.0
beautifulsoup4==4.12.2

# Utilities
tqdm==4.66.1
pydantic==2.5.0
```

### 7.4 Scripts de Inicialización

Voy a crear los scripts necesarios en archivos separados...

---

## 📊 Resumen del Entregable 1

### ✅ Checklist de Completitud

- [x] **Universo del discurso definido**: Tecnología e Innovación
- [x] **Análisis de requerimientos**: 10 RF + 5 RNF + 5 Casos de Uso
- [x] **Justificación de modelado NoSQL**: MongoDB Atlas con Vector Search
- [x] **Comparación Embedding vs Referencing**: Tabla detallada + ejemplos
- [x] **Diseño de 3 colecciones**: articles, images, query_history
- [x] **Ejemplos de documentos JSON**: 4 ejemplos completos
- [x] **Estrategia de índices**: 11 índices planificados
- [x] **Schema validation rules**: Validación estricta para las 3 colecciones
- [x] **Configuración de entorno**: Instrucciones de Atlas + estructura de proyecto

### 📈 Métricas Esperadas

| Métrica | Valor Objetivo |
|---------|---------------|
| Documentos de texto | 100+ artículos |
| Imágenes | 50+ diagramas/fotos |
| Dimensiones embeddings texto | 384 (all-MiniLM-L6-v2) |
| Dimensiones embeddings imagen | 512 (CLIP) |
| Tiempo de búsqueda | < 500ms |
| Tiempo RAG completo | < 3s |

---

**Próximos Pasos:**
1. Crear scripts de inicialización (ver archivos adjuntos)
2. Conseguir dataset de 100+ artículos técnicos
3. Descargar 50+ imágenes relacionadas
4. Ejecutar pipeline de carga de datos
5. Verificar funcionamiento de índices vectoriales

---

**Fecha de Entrega:** [Definir según calendario académico]  
**Autor:** Alejandro  
**Versión:** 1.0
