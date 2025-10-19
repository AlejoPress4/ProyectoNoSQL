# 🚀 Sistema RAG de Tecnología con MongoDB

Sistema de Recuperación y Generación Aumentada (RAG) enfocado en contenido tecnológico, utilizando MongoDB Atlas con búsqueda vectorial.

## 📋 Descripción

Este proyecto implementa un sistema RAG completo que:
- 🤖 Almacena y procesa artículos técnicos sobre tecnología
- 🔍 Realiza búsqueda semántica mediante embeddings vectoriales
- 🖼️ Procesa imágenes técnicas (diagramas, arquitecturas)
- 💬 Genera respuestas contextualizadas usando LLMs
- 🎯 Soporta consultas híbridas (filtros + similaridad vectorial)

## 🏗️ Arquitectura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Artículos  │────▶│   MongoDB    │────▶│  Vector      │
│   Imágenes   │     │   Atlas      │     │  Search      │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  RAG Engine  │
                     │   + LLM      │
                     └──────────────┘
```

## 📦 Estructura del Proyecto

```
ProyectoNoSQL/
├── config/
│   ├── db_config.py          # Configuración MongoDB
│   └── .env.example          # Template de variables de entorno
├── scripts/
│   ├── 01_setup_database.py  # Crear colecciones
│   ├── 02_create_indexes.py  # Crear índices
│   ├── 03_load_articles.py   # Cargar artículos
│   ├── 04_load_images.py     # Cargar imágenes
│   └── 05_test_connection.py # Verificar setup
├── data/
│   ├── raw/                  # Datos originales
│   ├── processed/            # Datos procesados
│   └── images/               # Imágenes
├── docs/
│   └── Entregable1_Analisis_Diseño.md  # Documentación completa
├── requirements.txt
└── README.md
```

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/AlejoPress4/ProyectoNoSQL.git
cd ProyectoNoSQL
```

### 2. Crear Entorno Virtual

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```powershell
# Copiar el template
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

**Contenido del archivo `.env`:**

```env
MONGODB_URI=mongodb+srv://tu_usuario:tu_password@cluster.xxxxx.mongodb.net/
MONGODB_DB_NAME=tech_rag_db
GROQ_API_KEY=tu_api_key_de_groq
```

### 5. Configurar MongoDB Atlas

1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Crear cluster gratuito M0
3. Configurar acceso de red (0.0.0.0/0 para desarrollo)
4. Crear usuario de base de datos
5. Obtener connection string

### 6. Ejecutar Scripts de Configuración

```powershell
# Script 1: Crear colecciones con validación
python scripts/01_setup_database.py

# Script 2: Crear índices
python scripts/02_create_indexes.py

# Script 3: Verificar conexión y setup
python scripts/05_test_connection.py
```

## 🗄️ Colecciones de MongoDB

### 1. `articles` - Artículos Tecnológicos

```json
{
  "_id": ObjectId,
  "titulo": "String",
  "contenido": "String",
  "texto_embedding": [Float...],  // 384 dims
  "metadata": {
    "fecha_publicacion": Date,
    "idioma": "es|en",
    "categoria": "Machine Learning|Backend|...",
    "dificultad": "basico|intermedio|avanzado"
  },
  "tags": ["tag1", "tag2"],
  "imagenes": [ObjectId...]
}
```

### 2. `images` - Imágenes Técnicas

```json
{
  "_id": ObjectId,
  "nombre": "String",
  "url": "String",
  "image_embedding": [Float...],  // 512 dims
  "metadata": {
    "formato": "png|jpg|svg",
    "tipo": "diagrama|screenshot|grafico"
  },
  "tags": ["tag1", "tag2"]
}
```

### 3. `query_history` - Historial de Consultas

```json
{
  "_id": ObjectId,
  "query_text": "String",
  "query_type": "semantic|hybrid|image",
  "resultados": {...},
  "metricas": {...},
  "timestamp": Date
}
```

## 🔍 Índices Configurados

### Índices Tradicionales (MongoDB)

- **articles**:
  - Compuesto: `{fecha: -1, idioma: 1}`
  - Texto: `{titulo: text, contenido: text}`
  - Multikey: `tags`
  - Simple: `categoria`, `fecha`

- **images**:
  - Simple: `tipo`
  - Multikey: `tags`

### Índices Vectoriales (Atlas Search)

**IMPORTANTE:** Crear manualmente en la UI de Atlas:

1. Ir a "Search" → "Create Search Index"
2. Usar configuración JSON para:
   - `vector_index_articles` (384 dims, cosine)
   - `vector_index_images` (512 dims, cosine)

Ver detalles en `Entregable1_Analisis_Diseño.md` sección 5.2

## 🧪 Verificar Instalación

```powershell
# Test completo de conexión
python scripts/05_test_connection.py
```

**Output esperado:**
```
✅ Conexión establecida correctamente
✅ 'articles' existe (0 documentos)
✅ 'images' existe (0 documentos)
✅ 'query_history' existe (0 documentos)
✅ Schema validation está funcionando correctamente
🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!
```

## 📊 Próximos Pasos (Entregable 2)

1. **Recolectar Dataset**:
   - 100+ artículos técnicos (DEV.to, Medium, ArXiv)
   - 50+ imágenes (Unsplash, Wikipedia Commons)

2. **Implementar Pipeline RAG**:
   - Generación de embeddings (sentence-transformers)
   - Búsqueda vectorial ($vectorSearch)
   - Integración con LLM (Groq/Llama 3.1)

3. **Desarrollar API REST**:
   - `POST /search` - Búsqueda híbrida
   - `POST /rag` - Generación de respuestas
   - `GET /stats` - Estadísticas

## 🛠️ Tecnologías

- **Base de Datos**: MongoDB Atlas (M0 Free Tier)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Image Embeddings**: CLIP (clip-vit-base-patch32)
- **LLM**: Groq API (Llama 3.1)
- **Backend**: Python 3.10+
- **Framework**: FastAPI (próximamente)

## 📚 Documentación

- **Análisis Completo**: Ver `docs/Entregable1_Analisis_Diseño.md`
- **Lineamientos**: Ver `LineamientoProyecto.md`

## 👤 Autor

**Alejandro**  
Proyecto Final - Bases de Datos No Relacionales  
Universidad - 2025

## 📝 Licencia

Proyecto académico de uso educativo.

---

## ⚠️ Troubleshooting

### Error: "No module named 'pymongo'"
```powershell
pip install pymongo
```

### Error: "ServerSelectionTimeoutError"
- Verificar connection string en `.env`
- Verificar acceso a internet
- Verificar whitelist de IP en Atlas (usar 0.0.0.0/0)

### Error: "Authentication failed"
- Verificar usuario y contraseña en `.env`
- Verificar que el usuario tenga permisos de "Atlas Admin"

---

**Estado del Proyecto**: ✅ Entregable 1 Completado  
**Última Actualización**: Octubre 2025
