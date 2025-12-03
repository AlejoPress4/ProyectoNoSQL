# 🤖 Sistema RAG Multimodal + Groq LLM

**Sistema de búsqueda inteligente de productos tecnológicos** que combina búsqueda por texto e imágenes con inteligencia artificial para generar respuestas naturales y personalizadas.

## 🎬 ¿Qué Hace Este Programa?

Este sistema te permite hacer preguntas en lenguaje natural como:
- *"Necesito una laptop para gaming con buena refrigeración bajo $1500"*
- *"¿Qué smartphone tiene mejor cámara para fotos nocturnas?"*
- *"Compara laptops Dell vs Asus para gaming"*

Y te responde con:
- ✅ **Análisis inteligente** generado por IA (Groq LLM)
- ✅ **Productos recomendados** con precios y especificaciones
- ✅ **Ventajas y desventajas** según reseñas de usuarios
- ✅ **Comparaciones automáticas** entre productos
- ✅ **Búsqueda por imágenes** usando CLIP (texto-a-imagen)

## 🎯 Características Principales

### 🔍 Búsqueda Inteligente
- **Multimodal:** Busca por texto O por descripción de imágenes
- **Semántica:** Entiende el significado, no solo palabras clave
- **Contextual:** Analiza productos, imágenes y reseñas de usuarios

### 🤖 Inteligencia Artificial
- **Groq LLM:** Modelo `llama-3.1-8b-instant` para respuestas naturales
- **CLIP:** Búsqueda de imágenes basada en texto (512 dimensiones)
- **Sentence Transformers:** Embeddings de texto (384 dimensiones)

### 📊 Base de Datos
- **MongoDB Atlas:** Base de datos NoSQL en la nube
- **Vector Search:** Búsqueda por similitud de embeddings
- **100+ Productos:** Laptops, smartphones, tablets, audio, wearables
- **300+ Reseñas:** Con ventajas y desventajas reales

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso | Versión |
|------------|-----|---------|
| **Python** | Lenguaje principal | 3.8+ |
| **Flask** | Servidor web | 3.0.0 |
| **MongoDB Atlas** | Base de datos NoSQL | Cloud |
| **Groq API** | LLM (llama-3.1) | API |
| **CLIP** | Búsqueda de imágenes | openai/clip-vit-base-patch32 |
| **Sentence Transformers** | Embeddings de texto | all-MiniLM-L6-v2 |
| **PyTorch** | Deep Learning | 2.1.0+ |
| **scikit-learn** | Similitud coseno | 1.3.0+ |

## 📋 Requisitos del Sistema

### Necesario
- ✅ Python 3.8 o superior
- ✅ 4 GB RAM mínimo (8 GB recomendado)
- ✅ 2 GB espacio en disco
- ✅ Conexión a internet
- ✅ Cuenta MongoDB Atlas (gratuita)
- ✅ API Key de Groq (gratuita)

### Opcional
- GPU NVIDIA (para CLIP más rápido)
- CUDA 11.8+ (si tienes GPU)

## 🚀 Instalación Rápida (5 Pasos)

## 🚀 Instalación Rápida (5 Pasos)

### 1️⃣ Instalar Python
```bash
# Verificar que tienes Python 3.8+
python --version
# o
py --version
```

### 2️⃣ Instalar Dependencias
```bash
cd ProyectoNoSQL
pip install -r requirements.txt
```
⏳ *Esto tarda 5-10 minutos la primera vez (descarga modelos de IA)*

### 3️⃣ Configurar MongoDB Atlas

**Opción A: Usar mi base de datos (recomendado para probar)**
```env
# Ya está configurado en .env, solo úsalo
MONGODB_URI=mongodb+srv://Alejandro:Alexia2002@cluster0.sqrqo.mongodb.net/
DATABASE_NAME=ragtech
```

**Opción B: Crear tu propia base de datos**
1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea cuenta gratis
3. Crea un cluster M0 (gratis)
4. Configura Network Access (añade tu IP: `0.0.0.0/0`)
5. Crea usuario de base de datos
6. Copia tu connection string al `.env`

### 4️⃣ Configurar Groq API (Opcional)

La API key ya está incluida en el código, pero puedes usar la tuya:

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea cuenta gratis
3. Genera API Key
4. Agrégala al `.env`:
```env
GROQ_API_KEY=gsk_tu_api_key_aqui
```

### 5️⃣ Iniciar el Servidor

```bash
py web_app.py
```

✅ Abre tu navegador en: **http://localhost:5000**

## 🧪 Cómo Probar el Sistema

### Opción 1: Interfaz Web (Más Fácil)

1. Inicia el servidor:
   ```bash
   py web_app.py
   ```

2. Abre **http://localhost:5000** en tu navegador

3. Ve a la sección **"Búsqueda RAG"**

4. Escribe una pregunta, por ejemplo:
   ```
   laptop gaming con buena refrigeración bajo $1500
   ```

5. Presiona **"Buscar con IA"**

6. ✨ **Magia:** El sistema busca productos, analiza reseñas y te da una respuesta inteligente

### Opción 2: API con curl

```bash
curl -X POST http://localhost:5000/rag \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"smartphone con mejor cámara\", \"max_products\": 3}"
```

### Opción 3: Python Script

```python
import requests

response = requests.post('http://localhost:5000/rag', json={
    "query": "auriculares con cancelación de ruido",
    "max_products": 5,
    "include_reviews": True,
    "include_images": True
})

data = response.json()
print(data['rag_response'])  # Respuesta de la IA
```

### Opción 4: Ejemplos Incluidos

```bash
py ejemplos_uso_groq.py
```

Este script ejecuta 7 ejemplos diferentes automáticamente.

## 📊 Ejemplos de Consultas

Copia y pega estos en la interfaz web:

### Búsquedas Simples
```
laptop para programación
smartphone económico con buena batería
auriculares inalámbricos deportivos
tablet para diseño gráfico
```

### Búsquedas Específicas
```
laptop gaming con RTX 3060 y buena refrigeración bajo $1500
smartphone con cámara de 108MP para fotografía nocturna
auriculares Sony con cancelación de ruido activa
tablet con stylus para ilustración digital
```

### Comparaciones
```
compara iPhone vs Samsung para fotografía
diferencias entre Dell XPS y MacBook Pro
mejor relación calidad-precio en laptops gaming
```

### Consultas Complejas
```
necesito una laptop ligera para viajar, que tenga buena batería, 
pantalla de al menos 13 pulgadas, y pueda editar videos en 1080p
```

## 🎯 ¿Qué Responde el Sistema?

Para cada consulta, la IA te da:

1. **Análisis Inteligente**
   - Recomendación principal con justificación
   - Alternativas relevantes
   - Comparaciones si aplica

2. **Productos Específicos**
   - Nombre y marca
   - Precio en USD
   - Especificaciones clave
   - Score de relevancia (%)

3. **Opiniones de Usuarios**
   - Ventajas destacadas
   - Desventajas a considerar
   - Calificaciones promedio

4. **Conclusión**
   - Mejor opción según tu necesidad
   - Relación calidad-precio
   - Casos de uso recomendados

## 🔧 Solución de Problemas Comunes

### ❌ Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### ❌ Error: "Connection refused MongoDB"
- Verifica tu IP en MongoDB Atlas Network Access
- Asegúrate de que el URI en `.env` es correcto
- Prueba con `0.0.0.0/0` en Network Access (permite todas las IPs)

### ❌ Error: "CLIP model not found"
```bash
pip install torch torchvision transformers
```

### ❌ Servidor muy lento la primera vez
- Es normal, está descargando modelos de IA (~1.5 GB)
- Solo pasa la primera vez
- Siguiente inicio será rápido (5 segundos)

### ❌ Error: "Groq API rate limit"
- Estás haciendo muchas consultas muy rápido
- Espera 1 minuto
- O usa tu propia API key (gratis en console.groq.com)

### ❌ Resultados no relevantes
- Asegúrate de que los datos estén cargados: `py app.py` → Opción 4
- Verifica que los índices vectoriales existan en MongoDB Atlas
- Prueba con consultas más específicas

## 📁 Estructura de Archivos (Simplificada)

```
ProyectoNoSQL/
├── web_app.py                 # 🚀 SERVIDOR PRINCIPAL - Ejecuta este
├── requirements.txt           # 📦 Dependencias
├── .env                       # 🔐 Configuración (MongoDB, Groq)
├── README.md                  # 📖 Esta guía
│
├── data/                      # 💾 Datos de productos y reseñas (JSON)
├── config/                    # ⚙️ Configuración de base de datos
├── scripts/                   # 🛠️ Scripts de setup y pruebas
└── docs/                      # 📚 Documentación adicional
```

## 🧠 ¿Cómo Funciona Internamente?

### Flujo de Búsqueda RAG

1. **Tu pregunta:** "laptop gaming con buena refrigeración"

2. **Embedding de texto:** 
   - Convierte tu texto en vector de 384 números
   - Modelo: sentence-transformers/all-MiniLM-L6-v2

3. **Embedding CLIP (opcional):**
   - Convierte tu descripción en vector de 512 números
   - Modelo: openai/clip-vit-base-patch32
   - Busca imágenes similares

4. **Búsqueda Vectorial (MongoDB):**
   - Compara tu vector con todos los productos
   - Usa similitud coseno (sklearn)
   - Encuentra los más parecidos

5. **Análisis de Reseñas:**
   - Busca reseñas relevantes
   - Extrae ventajas y desventajas
   - Calcula scores de sentimiento

6. **Fusión Híbrida:**
   ```python
   score_final = texto * 0.6 + imagen * 0.4
   ```

7. **Contexto para LLM:**
   - Top 6 productos
   - Especificaciones
   - Reseñas de usuarios
   - Scores de similitud

8. **Generación de Respuesta (Groq):**
   - Modelo: llama-3.1-8b-instant
   - Temperature: 0.4 (balance creatividad/precisión)
   - Max tokens: 800

9. **Tu respuesta:** Análisis inteligente en lenguaje natural 🎉

## 📊 Datos del Sistema

- **100+ Productos** distribuidos en 7 categorías
- **12 Marcas** tecnológicas reconocidas
- **50 Usuarios** con perfiles variados
- **300+ Reseñas** detalladas con ventajas/desventajas
- **Imágenes** con embeddings CLIP

## 🧪 Testing

```bash
# Ejecutar tests de integración
python scripts/test_groq_integration.py

# Ejecutar ejemplos de uso
python ejemplos_uso_groq.py
```

## 👥 Autor

Proyecto académico - Bases de Datos No Relacionales 2024/2025
**Versión 2.0** - RAG Multimodal + Groq LLM

## 📄 Licencia

Uso académico

---

## 📊 Datos del Sistema

| Colección | Cantidad | Descripción |
|-----------|----------|-------------|
| **Productos** | 100+ | Laptops, smartphones, tablets, audio, wearables |
| **Marcas** | 12 | Apple, Samsung, Dell, Asus, Sony, etc. |
| **Categorías** | 7 | Clasificación de productos |
| **Usuarios** | 50 | Perfiles variados |
| **Reseñas** | 300+ | Con ventajas, desventajas y calificaciones |

## 🎓 Proyecto Académico

**Curso:** Bases de Datos No Relacionales 2024/2025
**Entregable:** Sistema RAG con MongoDB Atlas + IA
**Versión:** 2.0 - RAG Multimodal + Groq LLM

### Objetivos Cumplidos
- ✅ Diseño de esquema NoSQL
- ✅ Índices optimizados (compuestos, texto, vectoriales)
- ✅ Embeddings vectoriales (384d + 512d)
- ✅ Validación con JSON Schema
- ✅ APIs RESTful
- ✅ Integración con IA (Groq LLM + CLIP)
- ✅ Búsqueda semántica multimodal
- ✅ Sistema de recomendaciones

## 📞 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Página principal |
| POST | `/rag` | **Búsqueda RAG con IA** ⭐ |
| GET | `/api/products` | Lista de productos |
| GET | `/api/categories` | Lista de categorías |
| GET | `/api/stats` | Estadísticas del sistema |
| POST | `/api/utils/update-caption` | Actualizar descripción |
| DELETE | `/api/utils/delete-image` | Eliminar producto |
| POST | `/api/utils/show-results` | Debug de búsquedas |

## 🔗 Enlaces Útiles

- 📚 [Documentación MongoDB](https://docs.mongodb.com/)
- 🤖 [Groq API Docs](https://console.groq.com/docs)
- 🧠 [Sentence Transformers](https://www.sbert.net/)
- 🖼️ [CLIP Model](https://huggingface.co/openai/clip-vit-base-patch32)
- 📖 [Flask Docs](https://flask.palletsprojects.com/)

## 💡 Tips para Mejor Experiencia

1. **Primera vez:** La carga de modelos tarda ~10 minutos
2. **Consultas específicas:** Mejor que consultas genéricas
3. **include_images=false:** Búsqueda más rápida (solo texto)
4. **max_products:** Limita a 3-5 para respuestas más rápidas
5. **include_reviews=true:** Contexto más rico para la IA

## 📄 Licencia

Uso académico - Universidad 2024/2025

---

**¿Necesitas ayuda?** Lee `RESUMEN_IMPLEMENTACION.md` o `docs/INTEGRACION_GROQ_LLM.md` para más detalles técnicos.

**¿Quieres probar rápido?** Ejecuta `py ejemplos_uso_groq.py` para ver 7 ejemplos automáticos.

**Documentación adicional:**
- [RESUMEN_IMPLEMENTACION.md](./RESUMEN_IMPLEMENTACION.md)
- [docs/INTEGRACION_GROQ_LLM.md](./docs/INTEGRACION_GROQ_LLM.md)
- [MongoDB Atlas Docs](https://docs.mongodb.com/)
- [Groq API Docs](https://console.groq.com/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [CLIP Model](https://huggingface.co/openai/clip-vit-base-patch32)

