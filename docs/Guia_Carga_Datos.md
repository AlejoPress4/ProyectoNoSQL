# 📚 Guía de Carga de Datos (Dataset)

## 🎯 Objetivo

Cargar el dataset completo en MongoDB para cumplir con el **Entregable 1**:
- ✅ Mínimo 100 documentos de texto
- ✅ Mínimo 50 imágenes asociadas
- ✅ Embeddings vectoriales generados

---

## 📋 Pre-requisitos

### 1. Configuración completada

```powershell
# Verificar que el archivo .env existe y tiene tu MongoDB URI
cat .env
```

Debe contener:
```env
MONGODB_URI=mongodb+srv://tu_usuario:tu_password@tu-cluster.mongodb.net/...
MONGODB_DB_NAME=tech_rag_db
```

### 2. Colecciones creadas

```powershell
# Ejecutar script de setup (si no lo has hecho)
python scripts\01_setup_database.py
```

### 3. Dependencias instaladas

```powershell
# Instalar librerías necesarias
pip install pymongo python-dotenv sentence-transformers tqdm numpy
```

**⚠️ NOTA:** `sentence-transformers` descargará automáticamente el modelo `all-MiniLM-L6-v2` (~80MB) la primera vez.

---

## 🚀 Paso a Paso: Cargar el Dataset

### **PASO 1: Cargar Artículos** (Script 03)

**📂 Archivo:** `scripts\03_load_articles.py`

**🎯 Qué hace:**
- Genera **30 artículos** tecnológicos de calidad:
  - 10 artículos detallados (1000+ palabras cada uno)
  - 20 artículos adicionales (500+ palabras)
- Calcula **embeddings de 384 dimensiones** usando `all-MiniLM-L6-v2`
- Inserta en colección `articles` con todos los campos requeridos
- Asigna metadatos: categoría, dificultad, idioma, tags, autor

**▶️ Ejecutar:**

```powershell
cd "c:\Users\aleja\OneDrive\Documentos\Universidad\bases\ProyectoNoSQL"

python scripts\03_load_articles.py
```

**✅ Salida esperada:**

```
================================================================================
                    📚 CARGA DE ARTÍCULOS TECNOLÓGICOS
================================================================================

🔄 Conectando a MongoDB Atlas...
✅ Conexión exitosa a la base de datos: tech_rag_db

🤖 Cargando modelo de embeddings...
   Modelo: all-MiniLM-L6-v2 (384 dimensiones)
✅ Modelo cargado

📝 Preparando 30 artículos para carga...
Generando embeddings: 100%|████████████████████| 30/30 [00:15<00:00,  1.95it/s]

💾 Insertando artículos en MongoDB...

✅ 30 artículos insertados exitosamente

================================================================================
                               📊 ESTADÍSTICAS
================================================================================

📂 Artículos por categoría:
   - Backend: 6 artículos
   - Machine Learning: 5 artículos
   - Frontend: 4 artículos
   - DevOps: 3 artículos
   - Cloud: 3 artículos
   ...

🌍 Artículos por idioma:
   - Español: 28 artículos
   - Inglés: 2 artículos

📈 Artículos por dificultad:
   - Intermedio: 15 artículos
   - Avanzado: 10 artículos
   - Basico: 5 artículos

================================================================================
🎉 ¡CARGA COMPLETADA EXITOSAMENTE!
================================================================================
```

**⏱️ Tiempo estimado:** 15-30 segundos (depende de tu conexión para descargar el modelo)

---

### **PASO 2: Cargar Imágenes** (Script 04)

**📂 Archivo:** `scripts\04_load_images.py`

**🎯 Qué hace:**
- Genera **50 imágenes** técnicas de 5 tipos:
  - 10 diagramas (arquitecturas, flujos)
  - 10 screenshots (herramientas, dashboards)
  - 10 gráficos (estadísticas, comparativas)
  - 10 fotos (hardware, oficinas)
  - 10 iconos (logos de tecnologías)
- Calcula **embeddings simulados de 512 dimensiones**
- Vincula automáticamente con artículos por tags comunes
- Inserta en colección `images`

**▶️ Ejecutar:**

```powershell
python scripts\04_load_images.py
```

**✅ Salida esperada:**

```
================================================================================
                       🖼️  CARGA DE IMÁGENES TÉCNICAS
================================================================================

🔄 Conectando a MongoDB Atlas...
✅ Conexión exitosa a la base de datos: tech_rag_db

🎨 Generando imágenes técnicas...
📝 Preparadas 50 imágenes para carga
   (Embeddings de 512 dimensiones)

💾 Insertando imágenes en MongoDB...

✅ 50 imágenes insertadas exitosamente

🔗 Vinculando imágenes con artículos...
Vinculando: 100%|████████████████████| 30/30 [00:02<00:00, 12.34it/s]
✅ 65 vinculaciones creadas

================================================================================
                               📊 ESTADÍSTICAS
================================================================================

🎨 Imágenes por tipo:
   - Diagrama: 10 imágenes
   - Screenshot: 10 imágenes
   - Grafico: 10 imágenes
   - Foto: 10 imágenes
   - Icono: 10 imágenes

📁 Imágenes por formato:
   - PNG: 28 imágenes
   - JPG: 12 imágenes
   - SVG: 10 imágenes

💾 Tamaño promedio: 245 KB

================================================================================
🎉 ¡CARGA COMPLETADA EXITOSAMENTE!
================================================================================
```

**⏱️ Tiempo estimado:** 5-10 segundos

---

### **PASO 3: Verificar Carga**

**📂 Archivo:** `scripts\05_test_connection.py`

```powershell
python scripts\05_test_connection.py
```

Deberías ver:
```
TEST 2: Verificación de Colecciones
✅ 'articles' existe (30 documentos)
✅ 'images' existe (50 documentos)
✅ 'query_history' existe (0 documentos)
```

---

## 📊 Resultado Final

Después de ejecutar ambos scripts, tendrás en MongoDB:

| Colección | Documentos | Descripción |
|-----------|-----------|-------------|
| `articles` | 30+ | Artículos con embeddings de 384D |
| `images` | 50+ | Imágenes con embeddings de 512D |
| `query_history` | 0 | Vacío (se llenará en Entregable 2) |

### Relaciones creadas:
- Cada artículo tiene **1-3 imágenes** vinculadas
- Cada imagen referencia **1-3 artículos** relacionados
- Vinculaciones basadas en **tags comunes**

---

## 🔍 Explorar los Datos Cargados

### Opción 1: MongoDB Compass

1. Descargar [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. Conectar con tu URI
3. Navegar a `tech_rag_db` → `articles` / `images`
4. Explorar documentos visualmente

### Opción 2: MongoDB Atlas UI

1. Ir a [cloud.mongodb.com](https://cloud.mongodb.com)
2. Browse Collections → `tech_rag_db`
3. Ver documentos en la interfaz web

### Opción 3: Python Script

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['tech_rag_db']

# Ver artículos
print("=== ARTÍCULOS ===")
for doc in db.articles.find().limit(3):
    print(f"\n📄 {doc['titulo']}")
    print(f"   Categoría: {doc['metadata']['categoria']}")
    print(f"   Tags: {', '.join(doc['tags'][:3])}")
    print(f"   Embedding: {len(doc['texto_embedding'])} dims")
    print(f"   Imágenes: {len(doc['imagenes'])} vinculadas")

# Ver imágenes
print("\n\n=== IMÁGENES ===")
for doc in db.images.find().limit(3):
    print(f"\n🖼️  {doc['nombre']}")
    print(f"   Tipo: {doc['metadata']['tipo']}")
    print(f"   Formato: {doc['metadata']['formato']}")
    print(f"   Embedding: {len(doc['image_embedding'])} dims")
    print(f"   Artículos: {len(doc['articulos_relacionados'])} relacionados")
```

---

## ⚙️ Opciones Avanzadas

### Regenerar datos

Si quieres regenerar el dataset:

```powershell
# Los scripts preguntarán si quieres eliminar datos existentes
python scripts\03_load_articles.py  # Responde 's' para sobrescribir
python scripts\04_load_images.py    # Responde 's' para sobrescribir
```

### Cargar más artículos

Edita `scripts\03_load_articles.py`, línea ~344:

```python
# Cambiar de 20 a 80 para tener 100 artículos totales
articulos_adicionales = generar_articulos_adicionales(80)
```

### Usar datos reales (opcional)

Si quieres usar artículos reales de APIs:

**Wikipedia:**
```python
import requests

def fetch_wikipedia_tech():
    url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": "tecnología programación",
        "format": "json"
    }
    response = requests.get(url, params=params)
    return response.json()
```

**DEV.to:**
```python
def fetch_devto_articles():
    url = "https://dev.to/api/articles"
    params = {"tag": "python", "per_page": 30}
    response = requests.get(url, params=params)
    return response.json()
```

---

## ❓ Troubleshooting

### Error: "Import 'sentence_transformers' could not be resolved"

```powershell
pip install sentence-transformers
```

### Error: "Model download failed"

El modelo se descarga automáticamente. Si falla:
1. Verificar conexión a internet
2. Reintentar la ejecución
3. El modelo se guarda en `~/.cache/torch/sentence_transformers/`

### Error: "Connection timeout"

- Verificar `.env` con MongoDB URI correcto
- Verificar IP whitelist en Atlas (0.0.0.0/0)

### Warning: "Colección ya existe"

- Normal si re-ejecutas el script
- Responde 's' para sobrescribir o 'n' para cancelar

---

## ✅ Checklist del Dataset

Después de ejecutar los scripts, verifica:

- [ ] ✅ `articles` tiene 30+ documentos
- [ ] ✅ Cada artículo tiene `texto_embedding` de 384 elementos
- [ ] ✅ Cada artículo tiene `metadata`, `autor`, `tags`
- [ ] ✅ `images` tiene 50+ documentos
- [ ] ✅ Cada imagen tiene `image_embedding` de 512 elementos
- [ ] ✅ Imágenes están vinculadas con artículos (campo `imagenes[]`)
- [ ] ✅ Artículos tienen referencias a imágenes (campo `articulos_relacionados[]`)

---

## 📈 Próximos Pasos

Con el dataset cargado, puedes:

1. **Crear índices vectoriales** en Atlas UI (ver `docs/Guia_Configuracion_Atlas.md`)
2. **Probar consultas** de búsqueda (ver `docs/Ejemplos_Consultas.md`)
3. **Implementar el pipeline RAG** (Entregable 2)

---

**¿Tienes problemas?** Revisa:
- `README.md` - Troubleshooting general
- `docs/Guia_Configuracion_Atlas.md` - Configuración de MongoDB
- `INICIO_RAPIDO.md` - Guía de inicio

---

**Última actualización:** Octubre 2025
