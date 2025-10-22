# 📁 Índice de Archivos del Proyecto

## 📚 Documentación Principal

### 1. **Entregable1_Analisis_Diseño.md** ⭐

**Ubicación:** `docs/Entregable1_Analisis_Diseño.md`

**Contenido completo para el Entregable 1:**

- ✅ Universo del discurso y análisis de requerimientos
- ✅ Justificación de decisiones de modelado NoSQL
- ✅ Comparación embedding vs. referencing (tabla detallada)
- ✅ Diseño de esquema NoSQL (3 colecciones)
- ✅ Ejemplos de documentos JSON
- ✅ Estrategias de indexing planificadas
- ✅ Schema validation rules completas
- ✅ Configuración de entorno

**Este es el documento principal para entregar.**

---

### 2. **README.md**

**Ubicación:** `README.md`

**Documentación general del proyecto:**

- Descripción del sistema RAG
- Arquitectura del proyecto
- Instrucciones de instalación
- Estructura de carpetas
- Tecnologías utilizadas
- Troubleshooting

---

### 3. **INICIO_RAPIDO.md**

**Ubicación:** `INICIO_RAPIDO.md`

**Guía rápida en 5 pasos:**

- Configurar MongoDB Atlas
- Instalar dependencias
- Configurar variables de entorno
- Ejecutar scripts de setup
- Verificar instalación

**Perfecto para comenzar rápidamente.**

---

### 4. **Guia_Configuracion_Atlas.md**

**Ubicación:** `docs/Guia_Configuracion_Atlas.md`

**Tutorial detallado de MongoDB Atlas:**

- Crear cuenta y cluster
- Configurar seguridad (usuarios, IPs)
- Obtener connection string
- Crear índices vectoriales en la UI
- Troubleshooting de conexión

---

### 5. **Diagramas_UML.md**

**Ubicación:** `docs/Diagramas_UML.md`

**Diagramas visuales del sistema:**

- Diagrama de colecciones (estructura)
- Diagrama de relaciones
- Flujo del sistema RAG
- Arquitectura de componentes
- Diagrama de secuencia
- Modelo ER simplificado
- Estrategia de indexing visual
- Comparación embedding vs referencing visual
- Pipeline de agregación ejemplo

---

### 6. **Ejemplos_Consultas.md**

**Ubicación:** `docs/Ejemplos_Consultas.md`

**Guía práctica de consultas:**

- Consultas básicas MongoDB
- Búsqueda de texto completo
- Aggregation pipelines
- Búsqueda vectorial (Atlas Search)
- Búsqueda híbrida (filtros + vectores)
- Pipeline RAG completo en código
- Casos de uso avanzados
- Ejemplos para el Entregable 2

---

## 🔧 Configuración

### 7. **.env.example**

**Ubicación:** `.env.example`

**Template de variables de entorno:**

```env
MONGODB_URI=...
MONGODB_DB_NAME=tech_rag_db
GROQ_API_KEY=...
```

**Copiar a `.env` y completar con tus credenciales.**

---

### 8. **requirements.txt**

**Ubicación:** `requirements.txt`

**Dependencias Python:**

- pymongo
- sentence-transformers
- torch, transformers
- pandas, numpy
- fastapi, uvicorn
- groq, openai

**Instalar con:** `pip install -r requirements.txt`

---

## 🐍 Scripts Python

### 9. **db_config.py**

**Ubicación:** `config/db_config.py`

**Configuración de MongoDB:**

- Clase `MongoDBConfig`
- Gestión de conexión
- Test de conectividad
- Constantes de colecciones

---

### 10. **01_setup_database.py** ⭐

**Ubicación:** `scripts/01_setup_database.py`

**Script 1: Configuración inicial**

- Crear colecciones con schema validation
- Aplicar reglas de validación para:
  - `articles`
  - `images`
  - `query_history`

**Ejecutar:** `python scripts/01_setup_database.py`

---

### 11. **02_create_indexes.py** ⭐

**Ubicación:** `scripts/02_create_indexes.py`

**Script 2: Crear índices**

- Índices compuestos
- Índices de texto
- Índices multikey
- Instrucciones para índices vectoriales (Atlas UI)

**Ejecutar:** `python scripts/02_create_indexes.py`

---

### 12. **05_test_connection.py** ⭐

**Ubicación:** `scripts/05_test_connection.py`

**Script 5: Suite de tests**

- Test de conectividad
- Verificar colecciones
- Verificar índices
- Test de inserción
- Test de schema validation
- Test de búsqueda de texto

**Ejecutar:** `python scripts/05_test_connection.py`

---

## 📂 Estructura de Carpetas

```
ProyectoNoSQL/
│
├── 📄 LineamientoProyecto.md        # Lineamientos originales
├── 📄 README.md                     # Documentación principal
├── 📄 INICIO_RAPIDO.md              # Guía rápida
├── 📄 requirements.txt              # Dependencias
├── 📄 .env.example                  # Template de variables
├── 📄 .env                          # Variables reales (NO subir a Git)
│
├── 📁 docs/
│   ├── 📄 Entregable1_Analisis_Diseño.md ⭐ # DOCUMENTO PRINCIPAL
│   ├── 📄 Guia_Configuracion_Atlas.md
│   ├── 📄 Diagramas_UML.md
│   └── 📄 Ejemplos_Consultas.md
│
├── 📁 config/
│   └── 📄 db_config.py              # Configuración MongoDB
│
├── 📁 scripts/
│   ├── 📄 01_setup_database.py ⭐   # Crear colecciones
│   ├── 📄 02_create_indexes.py ⭐   # Crear índices
│   └── 📄 05_test_connection.py ⭐  # Suite de tests
│
└── 📁 data/
    ├── 📁 raw/                      # Datos originales
    ├── 📁 processed/                # Datos procesados
    └── 📁 images/                   # Imágenes
```

---

## 🎯 Checklist del Entregable 1

### Documentación Requerida

- [x] **1. Documento de Análisis** ✅

  - Archivo: `docs/Entregable1_Analisis_Diseño.md`
  - ✅ Universo del discurso
  - ✅ Análisis de requerimientos (10 RF + 5 RNF + 5 CU)
  - ✅ Justificación de modelado NoSQL
  - ✅ Comparación embedding vs referencing

- [x] **2. Diseño de Esquema NoSQL** ✅

  - Archivo: `docs/Entregable1_Analisis_Diseño.md` (sección 4)
  - Diagrama: `docs/Diagramas_UML.md`
  - ✅ Definición de 3 colecciones
  - ✅ Ejemplos de documentos JSON
  - ✅ Estrategias de indexing
  - ✅ Schema validation rules

- [x] **3. Configuración de Entorno** ✅

  - Archivo: `docs/Guia_Configuracion_Atlas.md`
  - Scripts: `scripts/01_setup_database.py`, `02_create_indexes.py`
  - ✅ Instrucciones de cluster MongoDB Atlas
  - ✅ Scripts de inicialización
  - ✅ Script de verificación de conexión

- [x] **4. Dataset Preparado** ⏳
  - **Estado**: Pendiente para Entregable 2
  - **Fuentes identificadas**:
    - Texto: DEV.to, Medium, ArXiv, Wikipedia
    - Imágenes: Unsplash, Wikimedia Commons

---

## 🚀 Orden de Ejecución

### Para empezar el proyecto:

1. **Leer primero:**

   - `INICIO_RAPIDO.md` → 5 minutos
   - `docs/Guia_Configuracion_Atlas.md` → 15 minutos

2. **Configurar Atlas:**

   - Crear cuenta y cluster (10 minutos)
   - Obtener connection string

3. **Configurar proyecto:**

   ```powershell
   # Copiar template
   copy .env.example .env

   # Editar .env con tus credenciales
   notepad .env

   # Crear entorno virtual
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Instalar dependencias
   pip install -r requirements.txt
   ```

4. **Ejecutar scripts en orden:**

   ```powershell
   # Script 1: Crear colecciones
   python scripts/01_setup_database.py

   # Script 2: Crear índices
   python scripts/02_create_indexes.py

   # Script 5: Verificar todo
   python scripts/05_test_connection.py
   ```

5. **Crear índices vectoriales:**
   - Seguir instrucciones en `docs/Guia_Configuracion_Atlas.md` sección 8

---
