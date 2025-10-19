# 🎯 Pasos Rápidos para Ejecutar el Proyecto

## 📋 Pre-requisitos

- Python 3.10 o superior instalado
- Cuenta de MongoDB Atlas (gratuita)
- Conexión a internet

---

## ⚡ Inicio Rápido (5 pasos)

### 1️⃣ Configurar MongoDB Atlas

```
1. Crear cuenta en https://www.mongodb.com/cloud/atlas
2. Crear cluster gratuito M0
3. Crear usuario: tech_rag_admin
4. Whitelist IP: 0.0.0.0/0
5. Copiar connection string
```

**Ver guía detallada:** `docs/Guia_Configuracion_Atlas.md`

### 2️⃣ Configurar el Proyecto

```powershell
# Clonar repositorio
git clone https://github.com/AlejoPress4/ProyectoNoSQL.git
cd ProyectoNoSQL

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 3️⃣ Configurar Variables de Entorno

```powershell
# Copiar template
copy .env.example .env

# Editar .env (usar Notepad o VS Code)
notepad .env
```

Agregar tu connection string:
```env
MONGODB_URI=mongodb+srv://tech_rag_admin:TU_PASSWORD@tech-rag-cluster.xxxxx.mongodb.net/
MONGODB_DB_NAME=tech_rag_db
```

### 4️⃣ Ejecutar Scripts de Setup

```powershell
# Crear colecciones con validación
python scripts/01_setup_database.py

# Crear índices
python scripts/02_create_indexes.py
```

### 5️⃣ Verificar Instalación

```powershell
python scripts/05_test_connection.py
```

**✅ Si todo está bien, verás:**
```
🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!
```

---

## 📚 Estructura Creada

```
tech_rag_db/
├── articles          (0 documentos) ✅
├── images            (0 documentos) ✅
└── query_history     (0 documentos) ✅
```

---

## 🔍 Crear Índices Vectoriales (Paso Adicional)

**IMPORTANTE:** Los índices vectoriales se crean en la UI de Atlas:

1. Ir a tu cluster en Atlas → pestaña **"Search"**
2. Click **"Create Search Index"**
3. Usar **"JSON Editor"**
4. Para `articles`:
   - Collection: `articles`
   - Index Name: `vector_index_articles`
   - Configuración: Ver `docs/Guia_Configuracion_Atlas.md` sección 8

5. Repetir para `images`:
   - Collection: `images`
   - Index Name: `vector_index_images`

⏱️ **Los índices tardan ~5-10 minutos en estar activos**

---

## 🎓 Entregable 1 - Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `docs/Entregable1_Analisis_Diseño.md` | 📄 Documento completo del análisis |
| `LineamientoProyecto.md` | 📋 Lineamientos del proyecto |
| `README.md` | 📖 Documentación general |
| `docs/Guia_Configuracion_Atlas.md` | 🔧 Guía paso a paso de Atlas |

---

## 🚀 Próximos Pasos (Entregable 2)

1. **Conseguir Dataset:**
   - 100+ artículos técnicos
   - 50+ imágenes técnicas

2. **Implementar Scripts de Carga:**
   - `03_load_articles.py`
   - `04_load_images.py`

3. **Desarrollar Pipeline RAG:**
   - Generación de embeddings
   - Búsqueda vectorial
   - Integración con LLM

4. **Crear API REST:**
   - Endpoints `/search` y `/rag`
   - Documentación con FastAPI

---

## ❓ ¿Problemas?

Ver sección **Troubleshooting** en:
- `README.md`
- `docs/Guia_Configuracion_Atlas.md`

O revisar los errores comunes:

### "No module named 'pymongo'"
```powershell
pip install pymongo python-dotenv
```

### "Authentication failed"
- Verificar contraseña en `.env`
- Verificar usuario en Atlas

### "Connection timeout"
- Verificar IP whitelist (0.0.0.0/0)
- Verificar connection string

---

## 📊 Estado Actual del Proyecto

- ✅ Análisis y diseño completado
- ✅ Esquemas NoSQL definidos
- ✅ Colecciones creadas con validación
- ✅ Índices tradicionales configurados
- ⏳ Índices vectoriales (pendiente en Atlas UI)
- ⏳ Dataset (pendiente para Entregable 2)
- ⏳ Pipeline RAG (pendiente para Entregable 2)

---

**🎉 ¡Listo para empezar!**

Tu base de datos MongoDB está configurada y lista para recibir datos.
