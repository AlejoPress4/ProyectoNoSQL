"""
Configuraciones generales del sistema RAG de productos tecnológicos.
"""

# Configuración de embeddings
TEXT_EMBEDDING_DIM = 384  # Dimensiones para embeddings de texto (sentence-transformers)
IMAGE_EMBEDDING_DIM = 512  # Dimensiones para embeddings de imágenes (CLIP)

# Modelo de embeddings de texto
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# Nombres de colecciones (ahora marcas embebidas en productos, reseñas embebidas en usuarios)
COLLECTIONS = {
    'PRODUCTOS': 'productos',
    'CATEGORIAS': 'categorias',
    'USUARIOS': 'usuarios',
    'IMAGENES': 'imagenesProducto'
}

# Rutas de archivos de datos
DATA_FILES = {
    'MARCAS': 'data/marcas.json',
    'CATEGORIAS': 'data/categorias.json',
    'PRODUCTOS': 'data/productos.json',
    'USUARIOS': 'data/usuarios.json',
    'RESENAS': 'data/resenas.json',
    'IMAGENES': 'data/imagenes_metadata.json'
}

# Configuración de validación
DISPONIBILIDAD_ENUM = ["en_stock", "agotado", "pre_orden", "descontinuado"]
IDIOMAS_ENUM = ["es", "en", "pt", "fr", "de"]
TIPO_IMAGEN_ENUM = ["foto_producto", "lifestyle", "detalle", "comparativa"]
ANGULO_VISTA_ENUM = ["frontal", "posterior", "lateral", "superior", "uso"]

# Rangos de validación
CALIFICACION_MIN = 1
CALIFICACION_MAX = 5
PRECIO_MIN = 0

# Configuración de batch processing
BATCH_SIZE = 100  # Número de documentos a insertar por lote
