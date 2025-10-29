"""
Script para cargar datos en MongoDB con generación de embeddings.
Este es el script principal para poblar la base de datos.
"""

import json
import os
from datetime import datetime
from bson import ObjectId
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config import get_database, COLLECTIONS, DATA_FILES, EMBEDDING_MODEL_NAME


# Variable global para el modelo de embeddings
_embedding_model = None


def get_embedding_model():
    """
    Carga el modelo de embeddings (singleton).
    
    Returns:
        SentenceTransformer: Modelo de embeddings
    """
    global _embedding_model
    if _embedding_model is None:
        print(f"📥 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"✓ Modelo cargado correctamente")
    return _embedding_model


def generate_embedding(text):
    """
    Genera embedding para un texto dado.
    
    Args:
        text (str): Texto a convertir en embedding
        
    Returns:
        list: Vector de embedding (384 dimensiones)
    """
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()  # Convertir numpy array a lista


def load_json_file(file_path):
    """
    Carga un archivo JSON.
    
    Args:
        file_path (str): Ruta del archivo JSON
        
    Returns:
        list/dict: Datos del archivo JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_marcas(db):
    """
    Carga las marcas en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        
    Returns:
        dict: Diccionario {nombre_marca: ObjectId}
    """
    print("\n📦 Cargando marcas...")
    
    collection = db[COLLECTIONS['MARCAS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    marcas_data = load_json_file(DATA_FILES['MARCAS'])
    
    # Preparar documentos para inserción
    documentos = []
    for marca in marcas_data:
        doc = {
            "nombre": marca["nombre"],
            "pais": marca["pais"],
            "sitio_web": marca.get("sitio_web", ""),
            "descripcion": marca.get("descripcion", ""),
            "fecha_creacion": datetime.now()
        }
        documentos.append(doc)
    
    # Insertar documentos
    result = collection.insert_many(documentos)
    
    # Crear diccionario de mapeo
    marcas_map = {}
    for marca in collection.find():
        marcas_map[marca["nombre"]] = marca["_id"]
    
    print(f"✓ {len(result.inserted_ids)} marcas cargadas")
    return marcas_map


def load_categorias(db):
    """
    Carga las categorías en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        
    Returns:
        dict: Diccionario {slug_categoria: ObjectId}
    """
    print("\n📦 Cargando categorías...")
    
    collection = db[COLLECTIONS['CATEGORIAS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    categorias_data = load_json_file(DATA_FILES['CATEGORIAS'])
    
    # Preparar documentos para inserción
    documentos = []
    for categoria in categorias_data:
        doc = {
            "nombre": categoria["nombre"],
            "slug": categoria["slug"],
            "descripcion": categoria.get("descripcion", ""),
            "id_categoria_padre": categoria.get("id_categoria_padre"),
            "fecha_creacion": datetime.now()
        }
        documentos.append(doc)
    
    # Insertar documentos
    result = collection.insert_many(documentos)
    
    # Crear diccionario de mapeo
    categorias_map = {}
    for categoria in collection.find():
        categorias_map[categoria["slug"]] = categoria["_id"]
    
    print(f"✓ {len(result.inserted_ids)} categorías cargadas")
    return categorias_map


def load_usuarios(db):
    """
    Carga los usuarios en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        
    Returns:
        dict: Diccionario {nombre_usuario: ObjectId}
    """
    print("\n📦 Cargando usuarios...")
    
    collection = db[COLLECTIONS['USUARIOS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    usuarios_data = load_json_file(DATA_FILES['USUARIOS'])
    
    # Preparar documentos para inserción
    documentos = []
    for usuario in usuarios_data:
        # Parsear fecha si está en formato string
        fecha_creacion = usuario.get("fecha_creacion")
        if isinstance(fecha_creacion, str):
            fecha_creacion = datetime.fromisoformat(fecha_creacion)
        else:
            fecha_creacion = datetime.now()
        
        doc = {
            "nombre_usuario": usuario["nombre_usuario"],
            "correo": usuario["correo"],
            "nombre_completo": usuario.get("nombre_completo", ""),
            "comprador_verificado": usuario.get("comprador_verificado", False),
            "fecha_creacion": fecha_creacion,
            "ultimo_acceso": datetime.now()
        }
        documentos.append(doc)
    
    # Insertar documentos
    result = collection.insert_many(documentos)
    
    # Crear diccionario de mapeo
    usuarios_map = {}
    for usuario in collection.find():
        usuarios_map[usuario["nombre_usuario"]] = usuario["_id"]
    
    print(f"✓ {len(result.inserted_ids)} usuarios cargados")
    return usuarios_map


def load_productos(db, marcas_map, categorias_map):
    """
    Carga los productos en la base de datos con embeddings.
    
    Args:
        db: Objeto de base de datos de MongoDB
        marcas_map (dict): Mapeo de nombres de marcas a ObjectIds
        categorias_map (dict): Mapeo de slugs de categorías a ObjectIds
        
    Returns:
        dict: Diccionario {codigo_producto: ObjectId}
    """
    print("\n📦 Cargando productos con embeddings...")
    print("⏳ Este proceso puede tomar varios minutos...")
    
    collection = db[COLLECTIONS['PRODUCTOS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    productos_data = load_json_file(DATA_FILES['PRODUCTOS'])
    
    # Cargar modelo de embeddings
    get_embedding_model()
    
    # Preparar documentos para inserción
    documentos = []
    
    for producto in tqdm(productos_data, desc="Generando embeddings de productos"):
        # Validar que la marca existe
        marca_nombre = producto.get("marca_nombre")
        if marca_nombre not in marcas_map:
            print(f"⚠ Advertencia: Marca '{marca_nombre}' no encontrada. Omitiendo producto.")
            continue
        
        # Validar que la categoría existe
        categoria_slug = producto.get("categoria_slug")
        if categoria_slug not in categorias_map:
            print(f"⚠ Advertencia: Categoría '{categoria_slug}' no encontrada. Omitiendo producto.")
            continue
        
        # Obtener nombre de categoría del slug
        categoria_doc = db[COLLECTIONS['CATEGORIAS']].find_one({"slug": categoria_slug})
        categoria_nombre = categoria_doc["nombre"] if categoria_doc else categoria_slug
        
        # Generar embedding de la descripción
        descripcion = producto["descripcion"]
        descripcion_embedding = generate_embedding(descripcion)
        
        # Parsear fecha de lanzamiento
        fecha_lanzamiento = producto.get("fecha_lanzamiento")
        if isinstance(fecha_lanzamiento, str):
            fecha_lanzamiento = datetime.fromisoformat(fecha_lanzamiento)
        
        # Construir documento completo
        doc = {
            "codigo_producto": producto["codigo_producto"],
            "nombre": producto["nombre"],
            "descripcion": descripcion,
            "marca": {
                "id": marcas_map[marca_nombre],
                "nombre": marca_nombre
            },
            "categoria": {
                "id": categorias_map[categoria_slug],
                "nombre": categoria_nombre,
                "slug": categoria_slug
            },
            "especificaciones": producto.get("especificaciones", {}),
            "metadata": {
                "precio_usd": float(producto["precio_usd"]),
                "fecha_lanzamiento": fecha_lanzamiento,
                "disponibilidad": producto.get("disponibilidad", "en_stock"),
                "calificacion_promedio": producto.get("calificacion_promedio", 0.0),
                "cantidad_resenas": producto.get("cantidad_resenas", 0)
            },
            "descripcion_embedding": descripcion_embedding,
            "imagen_principal": producto.get("imagen_principal", ""),
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": datetime.now()
        }
        documentos.append(doc)
    
    # Insertar documentos
    if documentos:
        result = collection.insert_many(documentos)
        print(f"✓ {len(result.inserted_ids)} productos cargados con embeddings")
    else:
        print("⚠ No se cargaron productos")
        return {}
    
    # Crear diccionario de mapeo
    productos_map = {}
    for producto in collection.find():
        productos_map[producto["codigo_producto"]] = producto["_id"]
    
    return productos_map


def load_resenas(db, productos_map, usuarios_map):
    """
    Carga las reseñas en la base de datos con embeddings.
    
    Args:
        db: Objeto de base de datos de MongoDB
        productos_map (dict): Mapeo de códigos de productos a ObjectIds
        usuarios_map (dict): Mapeo de nombres de usuario a ObjectIds
        
    Returns:
        int: Número de reseñas cargadas
    """
    print("\n📦 Cargando reseñas con embeddings...")
    print("⏳ Este proceso puede tomar varios minutos...")
    
    collection = db[COLLECTIONS['RESENAS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    resenas_data = load_json_file(DATA_FILES['RESENAS'])
    
    # Cargar modelo de embeddings
    get_embedding_model()
    
    # Preparar documentos para inserción
    documentos = []
    
    for resena in tqdm(resenas_data, desc="Generando embeddings de reseñas"):
        # Validar que el producto existe
        codigo_producto = resena.get("codigo_producto")
        if codigo_producto not in productos_map:
            print(f"⚠ Advertencia: Producto '{codigo_producto}' no encontrado. Omitiendo reseña.")
            continue
        
        # Validar que el usuario existe
        nombre_usuario = resena.get("nombre_usuario")
        if nombre_usuario not in usuarios_map:
            print(f"⚠ Advertencia: Usuario '{nombre_usuario}' no encontrado. Omitiendo reseña.")
            continue
        
        # Obtener información del usuario
        usuario_doc = db[COLLECTIONS['USUARIOS']].find_one({"_id": usuarios_map[nombre_usuario]})
        
        # Generar embedding del contenido
        contenido = resena["contenido"]
        contenido_embedding = generate_embedding(contenido)
        
        # Parsear fecha si está en formato string
        fecha_creacion = resena.get("fecha_creacion")
        if isinstance(fecha_creacion, str):
            fecha_creacion = datetime.fromisoformat(fecha_creacion)
        else:
            fecha_creacion = datetime.now()
        
        # Construir documento completo
        doc = {
            "id_producto": productos_map[codigo_producto],
            "id_usuario": usuarios_map[nombre_usuario],
            "usuario": {
                "nombre_usuario": nombre_usuario,
                "comprador_verificado": usuario_doc.get("comprador_verificado", False)
            },
            "calificacion": int(resena["calificacion"]),
            "titulo": resena["titulo"],
            "contenido": contenido,
            "ventajas": resena.get("ventajas", []),
            "desventajas": resena.get("desventajas", []),
            "idioma": resena.get("idioma", "es"),
            "votos_utiles": resena.get("votos_utiles", 0),
            "compra_verificada": resena.get("compra_verificada", False),
            "contenido_embedding": contenido_embedding,
            "fecha_creacion": fecha_creacion,
            "fecha_actualizacion": datetime.now()
        }
        documentos.append(doc)
    
    # Insertar documentos
    if documentos:
        result = collection.insert_many(documentos)
        print(f"✓ {len(result.inserted_ids)} reseñas cargadas con embeddings")
        return len(result.inserted_ids)
    else:
        print("⚠ No se cargaron reseñas")
        return 0


def load_imagenes(db, productos_map):
    """
    Carga los metadatos de imágenes en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        productos_map (dict): Mapeo de códigos de productos a ObjectIds
        
    Returns:
        int: Número de imágenes cargadas
    """
    print("\n📦 Cargando metadatos de imágenes...")
    
    collection = db[COLLECTIONS['IMAGENES']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Verificar si existe el archivo
    if not os.path.exists(DATA_FILES['IMAGENES']):
        print(f"⚠ Archivo {DATA_FILES['IMAGENES']} no encontrado. Omitiendo carga de imágenes.")
        return 0
    
    # Cargar datos del JSON
    imagenes_data = load_json_file(DATA_FILES['IMAGENES'])
    
    # Preparar documentos para inserción
    documentos = []
    
    for imagen in imagenes_data:
        # Validar que el producto existe
        codigo_producto = imagen.get("codigo_producto")
        if codigo_producto not in productos_map:
            print(f"⚠ Advertencia: Producto '{codigo_producto}' no encontrado. Omitiendo imagen.")
            continue
        
        # Construir documento completo
        doc = {
            "id_producto": productos_map[codigo_producto],
            "url_imagen": imagen["url_imagen"],
            "tipo_imagen": imagen.get("tipo_imagen", "foto_producto"),
            "angulo_vista": imagen.get("angulo_vista", "frontal"),
            "metadata": imagen.get("metadata", {}),
            "texto_alternativo": imagen.get("texto_alternativo", ""),
            "es_principal": imagen.get("es_principal", False),
            "orden_visualizacion": imagen.get("orden_visualizacion", 1),
            "fecha_subida": datetime.now()
        }
        
        # Nota: Los embeddings de imágenes se generarían con CLIP
        # pero requeriría procesamiento de imágenes reales
        # imagen_embedding se agregaría aquí si se tuvieran las imágenes
        
        documentos.append(doc)
    
    # Insertar documentos
    if documentos:
        result = collection.insert_many(documentos)
        print(f"✓ {len(result.inserted_ids)} metadatos de imágenes cargados")
        return len(result.inserted_ids)
    else:
        print("⚠ No se cargaron metadatos de imágenes")
        return 0


def update_productos_stats(db):
    """
    Actualiza las estadísticas de productos (calificación promedio y cantidad de reseñas).
    
    Args:
        db: Objeto de base de datos de MongoDB
    """
    print("\n📊 Actualizando estadísticas de productos...")
    
    productos_collection = db[COLLECTIONS['PRODUCTOS']]
    resenas_collection = db[COLLECTIONS['RESENAS']]
    
    # Para cada producto, calcular estadísticas de reseñas
    productos = productos_collection.find()
    
    actualizados = 0
    for producto in productos:
        # Obtener reseñas del producto
        resenas = list(resenas_collection.find({"id_producto": producto["_id"]}))
        
        if resenas:
            # Calcular promedio de calificaciones
            calificaciones = [r["calificacion"] for r in resenas]
            promedio = sum(calificaciones) / len(calificaciones)
            
            # Actualizar producto
            productos_collection.update_one(
                {"_id": producto["_id"]},
                {
                    "$set": {
                        "metadata.calificacion_promedio": round(promedio, 2),
                        "metadata.cantidad_resenas": len(resenas)
                    }
                }
            )
            actualizados += 1
    
    print(f"✓ {actualizados} productos actualizados con estadísticas de reseñas")


def load_all_data():
    """
    Ejecuta la carga completa de datos en el orden correcto.
    
    Returns:
        bool: True si la carga fue exitosa
    """
    try:
        print("\n" + "="*60)
        print("INICIANDO CARGA COMPLETA DE DATOS")
        print("="*60)
        
        # Conectar a la base de datos
        db = get_database()
        
        # Cargar datos en orden (respetando dependencias)
        marcas_map = load_marcas(db)
        categorias_map = load_categorias(db)
        usuarios_map = load_usuarios(db)
        productos_map = load_productos(db, marcas_map, categorias_map)
        load_resenas(db, productos_map, usuarios_map)
        load_imagenes(db, productos_map)
        
        # Actualizar estadísticas de productos
        update_productos_stats(db)
        
        print("\n" + "="*60)
        print("✓ CARGA DE DATOS COMPLETADA EXITOSAMENTE")
        print("="*60 + "\n")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {str(e)}")
        print("Asegúrate de que todos los archivos JSON existen en la carpeta 'data/'")
        return False
    except Exception as e:
        print(f"\n✗ Error durante la carga de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    load_all_data()
