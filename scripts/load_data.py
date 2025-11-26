"""
Script para cargar datos en MongoDB con generación de embeddings.
Modelo actualizado: marcas embebidas en productos, reseñas embebidas en usuarios.
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


def load_categorias(db):
    """
    Carga las categorías en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        
    Returns:
        dict: Diccionario {slug_categoria: idCategoria}
    """
    print("\n📦 Cargando categorías...")
    
    collection = db[COLLECTIONS['CATEGORIAS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    categorias_data = load_json_file(DATA_FILES['CATEGORIAS'])
    
    # Preparar documentos para inserción con IDs secuenciales
    documentos = []
    categoria_map = {}
    
    for idx, categoria in enumerate(categorias_data, start=1):
        doc = {
            "idCategoria": idx,
            "nombre": categoria["nombre"],
            "slug": categoria["slug"],
            "descripcion": categoria.get("descripcion", ""),
            "idCategoriaPadre": categoria.get("id_categoria_padre"),
            "fechaCreacion": datetime.now()
        }
        documentos.append(doc)
        categoria_map[categoria["slug"]] = idx
    
    # Insertar documentos
    result = collection.insert_many(documentos)
    print(f"  ✓ {len(result.inserted_ids)} categorías insertadas")
    
    return categoria_map


def load_productos(db, categorias_map):
    """
    Carga los productos en la base de datos con embeddings y marcas embebidas.
    
    Args:
        db: Objeto de base de datos de MongoDB
        categorias_map (dict): Mapeo de slugs de categorías a idCategoria (int)
        
    Returns:
        dict: Diccionario {codigo_producto: idProducto (int)}
    """
    print("\n📦 Cargando productos con embeddings y marcas embebidas...")
    print("⏳ Este proceso puede tomar varios minutos...")
    
    collection = db[COLLECTIONS['PRODUCTOS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    productos_data = load_json_file(DATA_FILES['PRODUCTOS'])
    marcas_data = load_json_file(DATA_FILES['MARCAS'])
    
    # Crear mapa de marcas {nombre: datos_completos} y {nombre: idMarca}
    marcas_dict = {marca["nombre"]: marca for marca in marcas_data}
    marcas_id_map = {marca["nombre"]: idx for idx, marca in enumerate(marcas_data, start=1)}
    
    # Cargar modelo de embeddings
    get_embedding_model()
    
    # Preparar documentos para inserción
    documentos = []
    productos_map = {}
    
    for idx, producto in enumerate(tqdm(productos_data, desc="Generando embeddings de productos"), start=1):
        # Obtener datos de marca
        marca_nombre = producto.get("marca_nombre")
        if marca_nombre not in marcas_dict:
            print(f"⚠ Advertencia: Marca '{marca_nombre}' no encontrada. Omitiendo producto.")
            continue
        
        marca_info = marcas_dict[marca_nombre]
        id_marca = marcas_id_map[marca_nombre]
        
        # Validar que la categoría existe
        categoria_slug = producto.get("categoria_slug")
        if categoria_slug not in categorias_map:
            print(f"⚠ Advertencia: Categoría '{categoria_slug}' no encontrada. Omitiendo producto.")
            continue
        
        # Obtener ID de categoría
        categoria_id = categorias_map[categoria_slug]
        
        # Generar embedding de la descripción
        descripcion = producto["descripcion"]
        descripcion_embedding = generate_embedding(descripcion)
        
        # Parsear fecha de lanzamiento
        fecha_lanzamiento = producto.get("fecha_lanzamiento")
        if isinstance(fecha_lanzamiento, str):
            fecha_lanzamiento = datetime.fromisoformat(fecha_lanzamiento)
        
        # Construir documento completo con estructura plana (camelCase)
        doc = {
            "idProducto": idx,
            "codigoProducto": producto["codigo_producto"],
            "nombre": producto["nombre"],
            "idMarca": id_marca,  # ID secuencial para referencia
            "idCategoria": categoria_id,  # REFERENCIA a categorias
            "descripcion": descripcion,
            "precioUsd": float(producto["precio_usd"]),
            "fechaLanzamiento": fecha_lanzamiento,
            "disponibilidad": producto.get("disponibilidad", "en_stock"),
            "calificacionPromedio": float(producto.get("calificacion_promedio", 0.0)),
            "cantidadResenas": int(producto.get("cantidad_resenas", 0)),
            "fechaCreacion": datetime.now(),
            "fechaActualizacion": datetime.now(),
            "marca": {  # EMBEBIDO: Datos completos de la marca (desnormalización)
                "nombre": marca_info["nombre"],
                "pais": marca_info["pais"],
                "sitioWeb": marca_info.get("sitio_web", ""),
                "descripcion": marca_info.get("descripcion", "")
            },
            "descripcionEmbedding": descripcion_embedding
        }
        
        # Añadir campos de especificaciones PLANAS (no anidadas)
        if "especificaciones" in producto and isinstance(producto["especificaciones"], dict):
            specs = producto["especificaciones"]
            if specs:
                doc["idEspecificaciones"] = idx
                doc["procesador"] = specs.get("procesador", "")
                doc["memoriaRam"] = specs.get("memoria_ram", "")
                doc["almacenamiento"] = specs.get("almacenamiento", "")
                doc["pantalla"] = specs.get("pantalla", "")
                doc["bateria"] = specs.get("bateria", "")
                doc["sistemaOperativo"] = specs.get("sistema_operativo", "")
        
        documentos.append(doc)
        productos_map[producto["codigo_producto"]] = idx
    
    # Insertar documentos
    if documentos:
        result = collection.insert_many(documentos)
        print(f"✓ {len(result.inserted_ids)} productos cargados con embeddings y marcas embebidas")
    else:
        print("⚠ No se cargaron productos")
        return {}
    
    return productos_map


def load_usuarios_con_resenas(db, productos_map):
    """
    Carga usuarios con reseñas embebidas.
    
    Args:
        db: Objeto de base de datos de MongoDB
        productos_map (dict): Mapeo de códigos de productos a idProducto (int)
        
    Returns:
        dict: Diccionario {nombreUsuario: idUsuario}
    """
    print("\n📦 Cargando usuarios con reseñas embebidas...")
    print("⏳ Este proceso puede tomar varios minutos...")
    
    collection = db[COLLECTIONS['USUARIOS']]
    
    # Limpiar colección existente
    collection.delete_many({})
    
    # Cargar datos del JSON
    usuarios_data = load_json_file(DATA_FILES['USUARIOS'])
    resenas_data = load_json_file(DATA_FILES['RESENAS'])
    
    # Crear mapa de reseñas por usuario {nombre_usuario: [reseñas]}
    resenas_por_usuario = {}
    for resena in resenas_data:
        nombre_usuario = resena.get("nombre_usuario")
        if nombre_usuario not in resenas_por_usuario:
            resenas_por_usuario[nombre_usuario] = []
        resenas_por_usuario[nombre_usuario].append(resena)
    
    # Cargar modelo de embeddings
    get_embedding_model()
    
    # Preparar documentos para inserción
    documentos = []
    usuarios_map = {}
    
    for idx, usuario in enumerate(tqdm(usuarios_data, desc="Cargando usuarios con reseñas"), start=1):
        # Parsear fecha si está en formato string
        fecha_creacion = usuario.get("fecha_creacion")
        if isinstance(fecha_creacion, str):
            fecha_creacion = datetime.fromisoformat(fecha_creacion)
        else:
            fecha_creacion = datetime.now()
        
        nombre_usuario = usuario["nombre_usuario"]
        
        # Obtener reseñas del usuario
        resenas_usuario = resenas_por_usuario.get(nombre_usuario, [])
        resenas_embebidas = []
        
        for id_resena, resena in enumerate(resenas_usuario, 1):
            # Validar que el producto existe
            codigo_producto = resena.get("codigo_producto")
            if codigo_producto not in productos_map:
                print(f"⚠ Advertencia: Producto '{codigo_producto}' no encontrado. Omitiendo reseña.")
                continue
            
            # Generar embedding del contenido
            contenido = resena["contenido"]
            contenido_embedding = generate_embedding(contenido)
            
            # Parsear fecha si está en formato string
            fecha_resena = resena.get("fecha_creacion")
            if isinstance(fecha_resena, str):
                fecha_resena = datetime.fromisoformat(fecha_resena)
            else:
                fecha_resena = datetime.now()
            
            # Crear reseña embebida con camelCase
            resena_doc = {
                "idResena": id_resena,
                "idProducto": productos_map[codigo_producto],
                "calificacion": int(resena["calificacion"]),
                "titulo": resena["titulo"],
                "contenido": contenido,
                "ventajas": resena.get("ventajas", []),
                "desventajas": resena.get("desventajas", []),
                "idioma": resena.get("idioma", "es"),
                "votosUtiles": resena.get("votos_utiles", 0),
                "compraVerificada": resena.get("compra_verificada", False),
                "contenidoEmbedding": contenido_embedding,
                "fechaCreacion": fecha_resena,
                "fechaActualizacion": datetime.now()
            }
            resenas_embebidas.append(resena_doc)
        
        # Construir documento de usuario con reseñas embebidas (camelCase)
        doc = {
            "idUsuario": idx,
            "nombreUsuario": usuario["nombre_usuario"],
            "correo": usuario["correo"],
            "nombreCompleto": usuario.get("nombre_completo", ""),
            "compradorVerificado": usuario.get("comprador_verificado", False),
            "resenas": resenas_embebidas,  # Array de reseñas embebidas
            "fechaCreacion": fecha_creacion,
            "ultimoAcceso": datetime.now()
        }
        documentos.append(doc)
        usuarios_map[nombre_usuario] = idx
    
    # Insertar documentos
    if documentos:
        result = collection.insert_many(documentos)
        total_resenas = sum(len(doc["resenas"]) for doc in documentos)
        print(f"✓ {len(result.inserted_ids)} usuarios cargados")
        print(f"✓ {total_resenas} reseñas embebidas con embeddings")
    else:
        print("⚠ No se cargaron usuarios")
        return {}
    
    return usuarios_map


def load_imagenes(db, productos_map):
    """
    Carga los metadatos de imágenes en la base de datos.
    
    Args:
        db: Objeto de base de datos de MongoDB
        productos_map (dict): Mapeo de códigos de productos a idProducto (int)
        
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
    
    for idx, imagen in enumerate(imagenes_data, start=1):
        # Validar que el producto existe
        codigo_producto = imagen.get("codigo_producto")
        if codigo_producto not in productos_map:
            print(f"⚠ Advertencia: Producto '{codigo_producto}' no encontrado. Omitiendo imagen.")
            continue
        
        # Obtener metadata si existe
        metadata = imagen.get("metadata", {})
        
        # Construir documento completo con camelCase
        doc = {
            "idImagen": idx,
            "idProducto": productos_map[codigo_producto],
            "urlImagen": imagen["url_imagen"],
            "tipoImagen": imagen.get("tipo_imagen", "foto_producto"),
            "anguloVista": imagen.get("angulo_vista", "frontal"),
            "ancho": metadata.get("ancho", 800),
            "alto": metadata.get("alto", 600),
            "formato": metadata.get("formato", "jpg"),
            "tamanoKb": metadata.get("tamano_kb", 100),
            "textoAlternativo": imagen.get("texto_alternativo", ""),
            "esPrincipal": imagen.get("es_principal", False),
            "ordenVisualizacion": imagen.get("orden_visualizacion", 1),
            "fechaSubida": datetime.now()
        }
        
        # Nota: Los embeddings de imágenes se generarían con CLIP
        # pero requeriría procesamiento de imágenes reales
        
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
    Ahora las reseñas están embebidas en usuarios, por lo que hay que buscarlas allí.
    
    Args:
        db: Objeto de base de datos de MongoDB
    """
    print("\n📊 Actualizando estadísticas de productos...")
    
    productos_collection = db[COLLECTIONS['PRODUCTOS']]
    usuarios_collection = db[COLLECTIONS['USUARIOS']]
    
    # Para cada producto, calcular estadísticas de reseñas
    productos = productos_collection.find()
    
    actualizados = 0
    for producto in productos:
        # Buscar todas las reseñas del producto en los usuarios (ahora usa idProducto integer)
        usuarios_con_resenas = usuarios_collection.find({
            "resenas.idProducto": producto["idProducto"]
        })
        
        calificaciones = []
        for usuario in usuarios_con_resenas:
            for resena in usuario.get("resenas", []):
                if resena["idProducto"] == producto["idProducto"]:
                    calificaciones.append(resena["calificacion"])
        
        if calificaciones:
            # Calcular promedio de calificaciones
            promedio = sum(calificaciones) / len(calificaciones)
            
            # Actualizar producto con campos planos (camelCase)
            productos_collection.update_one(
                {"_id": producto["_id"]},
                {
                    "$set": {
                        "calificacionPromedio": round(promedio, 2),
                        "cantidadResenas": len(calificaciones)
                    }
                }
            )
            actualizados += 1
    
    print(f"✓ {actualizados} productos actualizados con estadísticas de reseñas")


def load_all_data():
    """
    Ejecuta la carga completa de datos en el orden correcto.
    Modelo: marcas EMBEBIDAS en productos (sin colección independiente),
    reseñas embebidas en usuarios.
    
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
        # 1. Categorías (colección independiente)
        categorias_map = load_categorias(db)
        
        # 2. Productos (referencia categorías, embebe marca completa)
        productos_map = load_productos(db, categorias_map)
        
        # 3. Usuarios con reseñas embebidas (reseñas referencian productos)
        usuarios_map = load_usuarios_con_resenas(db, productos_map)
        
        # 4. Imágenes (referencian productos)
        load_imagenes(db, productos_map)
        
        # 5. Actualizar estadísticas de productos
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
