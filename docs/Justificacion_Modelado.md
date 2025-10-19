# 📐 Justificación del Modelado NoSQL
## ¿Por qué Embebimos o Referenciamos cada dato?

---

## 1. ¿EL DATASET TIENE FORMATO JSON VÁLIDO? ✅

Sí. Los scripts generan documentos JSON que se insertan directamente en MongoDB con `insert_many()`.

---

## 2. DECISIONES DE MODELADO

### 📊 Resumen:

| Entidad/Campo | Estrategia | ¿Por qué? |
|--------------|-----------|-----------|
| **Metadatos** (fecha, idioma, categoría) | 🔹 **EMBEBIDO** | Son pequeños y siempre se consultan con el artículo |
| **Autor** (nombre, perfil) | 🔹 **EMBEBIDO** | Son solo 2 datos simples que forman parte del artículo |
| **Tags** (array de palabras clave) | 🔹 **EMBEBIDO** | Lista corta que se usa para buscar artículos |
| **Embeddings** (vectores 384D/512D) | 🔹 **EMBEBIDO** | MongoDB requiere que estén en el mismo documento para búsqueda vectorial |
| **Imágenes** | 🔷 **REFERENCIADO** | Son grandes y se reutilizan en múltiples artículos |

---

## 3. JUSTIFICACIÓN DETALLADA

### 📝 Metadatos del Artículo

**Estrategia: EMBEBIDO** 🔹

```json
{
  "titulo": "GraphQL vs REST",
  "metadata": {
    "fecha_publicacion": "2024-09-20",
    "idioma": "es",
    "categoria": "Backend"
  }
}
```

**¿Por qué embebidos?**
- Los metadatos son información básica del artículo (fecha, idioma, categoría)
- Son datos pequeños que siempre necesitamos cuando leemos un artículo
- No tiene sentido consultarlos por separado
- Cada artículo tiene sus propios metadatos únicos (no se comparten)

---

### 👤 Autor del Artículo

**Estrategia: EMBEBIDO** 🔹

```json
{
  "titulo": "React Hooks",
  "autor": {
    "nombre": "Pedro Martínez",
    "perfil": "https://github.com/pedro"
  }
}
```

**¿Por qué embebido?**
- Solo guardamos 2 datos simples: nombre y enlace al perfil
- Siempre mostramos el autor junto con el artículo
- No necesitamos gestionar información compleja del autor (biografía, contacto, etc.)
- Es parte natural del artículo

---

### 🏷️ Tags (Etiquetas)

**Estrategia: EMBEBIDO** 🔹

```json
{
  "titulo": "Docker y Kubernetes",
  "tags": ["docker", "kubernetes", "devops", "contenedores"]
}
```

**¿Por qué embebidos?**
- Son una lista corta de palabras clave (5-10 tags)
- Se usan constantemente para buscar y filtrar artículos
- Son específicos de cada artículo
- Fáciles de agregar o quitar cuando sea necesario

---

### 🎯 Embeddings (Vectores de Búsqueda)

**Estrategia: EMBEBIDO** 🔹

```json
{
  "titulo": "Introducción a CNNs",
  "texto_embedding": [0.023, -0.451, 0.889, ...]  // 384 números
}
```

**¿Por qué embebidos?**
- MongoDB necesita que los vectores estén en el mismo documento para poder hacer búsqueda vectorial
- Los vectores representan el contenido del artículo (no tienen sentido separados)
- Es un requisito técnico de la base de datos

---

### 🖼️ Imágenes

**Estrategia: REFERENCIADO** 🔷

```json
// Colección: articles
{
  "_id": ObjectId("art1"),
  "titulo": "Microservicios",
  "imagenes": [ObjectId("img1"), ObjectId("img2")]  // Solo guardamos IDs
}

// Colección: images
{
  "_id": ObjectId("img1"),
  "nombre": "Diagrama de arquitectura microservicios",
  "url": "https://...",
  "image_embedding": [...512 números...],
  "metadata": {...},
  "articulos_relacionados": [ObjectId("art1"), ObjectId("art2"), ObjectId("art3")]
}
```

**¿Por qué referenciadas?**

**1. Se reutilizan en múltiples artículos**
- Una misma imagen puede ilustrar varios artículos diferentes
- Ejemplo: El "Diagrama de arquitectura microservicios" puede aparecer en:
  - Artículo sobre Microservicios
  - Artículo sobre Docker
  - Artículo sobre API Gateway

**2. Evita duplicación de datos**
- Si embebemos: la imagen se copia completa en cada artículo (desperdicio de espacio)
- Si referenciamos: la imagen se guarda una sola vez

**3. Son datos grandes**
- Cada imagen incluye: URL, embedding de 512 números, metadata
- Esto suma ~2 KB por imagen
- Multiplicado por varios artículos = mucho espacio desperdiciado

**4. Facilita las actualizaciones**
- Si necesito cambiar la URL de una imagen, solo actualizo 1 lugar
- Si estuviera embebida, tendría que actualizar todos los artículos que la usan

**5. Permiten búsqueda independiente**
- Puedo buscar imágenes por tipo (diagramas, screenshots, gráficos)
- Puedo hacer búsqueda visual (encontrar imágenes similares)
- No necesito consultar artículos para buscar imágenes

---

## 4. COMPARACIÓN VISUAL

### ¿Qué pasa si embebemos las imágenes?

```
❌ EMBEBIDO (desperdicia espacio):

Artículo 1: "Microservicios"
└── Imagen completa "Diagrama X" [2 KB]

Artículo 2: "Docker"  
└── Imagen completa "Diagrama X" [2 KB]  ← ¡DUPLICADO!

Artículo 3: "Kubernetes"
└── Imagen completa "Diagrama X" [2 KB]  ← ¡DUPLICADO!

Total: 6 KB (4 KB desperdiciados)
```

### ¿Qué pasa si referenciamos las imágenes?

```
✅ REFERENCIADO (sin desperdicio):

Artículo 1: "Microservicios"
└── Referencia → ObjectId("img1")

Artículo 2: "Docker"
└── Referencia → ObjectId("img1")  ← Apunta a la misma

Artículo 3: "Kubernetes"  
└── Referencia → ObjectId("img1")  ← Apunta a la misma

Colección Images:
└── img1: "Diagrama X" [2 KB]  ← Solo 1 copia

Total: 2 KB + referencias
Ahorro: 67% de espacio
```

---

## 5. REGLA SIMPLE

### Usamos EMBEBIDO cuando:
- ✅ Los datos son pequeños
- ✅ Siempre se consultan junto al documento principal
- ✅ No se reutilizan en otros lugares
- ✅ Son parte natural del documento

### Usamos REFERENCIADO cuando:
- ✅ Los datos son grandes
- ✅ Se reutilizan en múltiples documentos
- ✅ Necesitamos consultarlos independientemente
- ✅ Se actualizan frecuentemente

---

## 6. RESUMEN FINAL

| Entidad | Decisión | Razón en 1 frase |
|---------|----------|------------------|
| **Metadatos** | 🔹 EMBEBIDO | Son pequeños y siempre se leen con el artículo |
| **Autor** | 🔹 EMBEBIDO | Solo 2 datos simples que forman parte del artículo |
| **Tags** | 🔹 EMBEBIDO | Lista corta para buscar artículos |
| **Embeddings** | 🔹 EMBEBIDO | MongoDB lo requiere para búsqueda vectorial |
| **Imágenes** | 🔷 REFERENCIADO | Son grandes, se reutilizan, y se buscan independientemente |

---

**Conclusión:** Usamos embebido para datos pequeños que forman parte del artículo, y referenciado para imágenes que son grandes y se comparten entre artículos.

---

**Fecha:** 19 de Octubre de 2025
