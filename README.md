# Sistema RAG de Productos Tecnológicos con MongoDB Atlas

Sistema de Retrieval-Augmented Generation (RAG) para gestión de catálogo de productos tecnológicos con búsqueda semántica usando embeddings vectoriales.

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de gestión de productos tecnológicos (smartphones, laptops, tablets, audio, wearables, vaping) con reseñas de usuarios y capacidades de búsqueda semántica avanzada utilizando MongoDB Atlas y embeddings vectoriales generados con `sentence-transformers`.

**Características principales:**
- ✅ Base de datos NoSQL con MongoDB Atlas
- ✅ Validación de esquemas con JSON Schema
- ✅ Índices optimizados para búsquedas eficientes
- ✅ Embeddings vectoriales de 384 dimensiones para búsqueda semántica
- ✅ Más de 100 productos tecnológicos reales
- ✅ Sistema de reseñas con calificaciones y análisis de sentimiento
- ✅ Gestión de imágenes con metadatos
- ✅ Interfaz CLI interactiva

## 🎯 Entregable 1 - Bases de Datos No Relacionales

Este proyecto corresponde al Entregable 1 del curso de Bases de Datos No Relacionales, implementando:
- Diseño de esquema NoSQL para productos tecnológicos
- Colecciones relacionadas con referencias
- Índices compuestos y de texto completo
- Embeddings vectoriales para RAG
- Validación de datos con JSON Schema

## 🏗️ Estructura del Proyecto

```
proyecto-rag-productos/
├── .env                          # Variables de entorno (MongoDB URI)
├── requirements.txt              # Dependencias de Python
├── README.md                     # Documentación (este archivo)
├── app.py                        # Aplicación principal con menú interactivo
│
├── config/                       # Configuraciones del sistema
│   ├── __init__.py
│   ├── mongodb_config.py         # Conexión a MongoDB Atlas
│   └── settings.py               # Configuraciones generales
│
├── scripts/                      # Scripts de setup y carga
│   ├── __init__.py
│   ├── create_collections.py    # Crear colecciones con validación
│   ├── create_indexes.py        # Crear índices optimizados
│   ├── load_data.py             # Cargar datos con embeddings
│   └── verify_data.py           # Verificar datos cargados
│
├── models/                       # Esquemas de datos
│   ├── __init__.py
│   └── schemas.py               # Definición de esquemas
│
└── data/                         # Archivos JSON de datos
    ├── marcas.json              # 12 marcas tecnológicas
    ├── categorias.json          # 7 categorías de productos
    ├── productos.json           # 100+ productos detallados
    ├── usuarios.json            # 50 usuarios
    ├── resenas.json             # 300+ reseñas detalladas
    └── imagenes_metadata.json   # Metadatos de imágenes
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Python 3.8 o superior**
- **MongoDB Atlas** (cuenta gratuita o de pago)
- **Conexión a Internet** para descargar modelos de embeddings

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd ProyectoNoSQL
```

### Paso 2: Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar MongoDB Atlas

1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crear un cluster (tier gratuito M0 disponible)
3. Configurar acceso de red (agregar tu IP)
4. Crear usuario de base de datos
5. Obtener connection string

### Paso 5: Configurar Variables de Entorno

Editar el archivo `.env` con tus credenciales:

```env
MONGODB_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=productos_tecnologicos
```

**⚠️ IMPORTANTE:** Reemplazar con tus credenciales reales.

## 📖 Uso del Sistema

### Ejecución de la Aplicación CLI

```bash
python app.py
```

### Flujo Recomendado (Primera Vez)

1. **Opción 6:** Verificar conexión a MongoDB
2. **Opción 5:** Ejecutar setup completo (⏳ 10-15 minutos)
3. **Opción 4:** Verificar datos cargados

### 🌐 Interfaz Web RAG Tech

La aplicación incluye una interfaz web moderna para búsquedas semánticas:

```bash
python web_app.py
```

**URLs disponibles:**
- **Principal:** http://localhost:5000
- **Búsqueda RAG:** http://localhost:5000/ragtech
- **API Productos:** http://localhost:5000/api/products
- **API Categorías:** http://localhost:5000/api/categories
- **API Estadísticas:** http://localhost:5000/api/stats

### Características de la Interfaz Web

- ✅ **Búsqueda en lenguaje natural** con embeddings vectoriales
- ✅ **Interfaz responsive** con Bootstrap 5
- ✅ **Resultados ordenados por relevancia** semántica
- ✅ **Visualización de productos** con imágenes y metadatos
- ✅ **Análisis de reseñas** relacionadas
- ✅ **APIs RESTful** para integración
- ✅ **Consultas de ejemplo** predefinidas

### Ejemplos de Consultas

```
"Smartphone con buena cámara y batería duradera"
"Laptop para gaming con procesador potente"
"Auriculares con cancelación de ruido"
"Tablet para diseño gráfico y productividad"
```

## 🗄️ Esquema de Base de Datos

### Colecciones Principales

- **productos**: Catálogo de productos con embeddings
- **marcas**: Fabricantes de productos
- **categorias**: Clasificación de productos
- **usuarios**: Usuarios del sistema
- **resenas**: Reseñas con embeddings de contenido
- **imagenes_producto**: Metadatos de imágenes

Ver esquemas completos en `models/schemas.py`

## 🧠 Embeddings Vectoriales

**Modelo:** sentence-transformers/all-MiniLM-L6-v2
- **Dimensiones:** 384
- **Idioma:** Multilingüe
- **Uso:** Búsqueda semántica y recomendaciones

## 📝 Datos Incluidos

- **100+ Productos** distribuidos en 7 categorías
- **12 Marcas** tecnológicas reconocidas
- **50 Usuarios** con perfiles variados
- **300+ Reseñas** detalladas en múltiples idiomas

## 🛠️ Solución de Problemas

### Error de Conexión
- Verificar URI en `.env`
- Verificar IP autorizada en MongoDB Atlas
- Verificar conexión a internet

### Carga Lenta
- La primera vez descarga el modelo (~90MB)
- Generar embeddings toma 5-10 minutos
- Es normal, solo ocurre una vez

## 👥 Autor

Proyecto académico - Bases de Datos No Relacionales 2024

## 📄 Licencia

Uso académico

---

**Documentación completa:** Consulta [MongoDB Docs](https://docs.mongodb.com/) y [Sentence Transformers](https://www.sbert.net/)
