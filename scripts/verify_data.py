"""
Script para verificar los datos cargados en MongoDB.
"""

from config import get_database, COLLECTIONS


def count_documents(db):
    """Cuenta los documentos en cada colección."""
    print("\n📊 CONTEO DE DOCUMENTOS POR COLECCIÓN")
    print("-" * 60)
    
    total = 0
    for collection_name in COLLECTIONS.values():
        count = db[collection_name].count_documents({})
        print(f"  {collection_name:25s}: {count:6d} documentos")
        total += count
    
    print("-" * 60)
    print(f"  {'TOTAL':25s}: {total:6d} documentos\n")
    
    return total


def verify_embeddings(db):
    """Verifica que los embeddings se hayan generado correctamente."""
    print("\n🔍 VERIFICACIÓN DE EMBEDDINGS")
    print("-" * 60)
    
    # Verificar embeddings de productos
    productos_col = db[COLLECTIONS['PRODUCTOS']]
    total_productos = productos_col.count_documents({})
    productos_con_embedding = productos_col.count_documents({
        "descripcionEmbedding": {"$exists": True, "$ne": None}
    })
    
    print(f"  Productos totales: {total_productos}")
    print(f"  Productos con embedding: {productos_con_embedding}")
    
    if productos_con_embedding > 0:
        # Verificar dimensión del embedding
        producto_sample = productos_col.find_one({"descripcionEmbedding": {"$exists": True}})
        if producto_sample and "descripcionEmbedding" in producto_sample:
            dim = len(producto_sample["descripcionEmbedding"])
            print(f"  Dimensión de embeddings: {dim}")
            print(f"  ✓ Embeddings de productos OK")
        else:
            print(f"  ⚠ No se pudo verificar la dimensión")
    else:
        print(f"  ✗ No hay productos con embeddings")
    
    print()
    
    # Verificar embeddings de reseñas (ahora embebidas en usuarios)
    usuarios_col = db[COLLECTIONS['USUARIOS']]
    total_usuarios = usuarios_col.count_documents({})
    usuarios_con_resenas = usuarios_col.count_documents({
        "resenas": {"$exists": True, "$ne": []}
    })
    
    # Contar total de reseñas embebidas
    pipeline = [
        {"$match": {"resenas": {"$exists": True}}},
        {"$project": {"num_resenas": {"$size": {"$ifNull": ["$resenas", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$num_resenas"}}}
    ]
    result = list(usuarios_col.aggregate(pipeline))
    total_resenas = result[0]["total"] if result else 0
    
    # Contar reseñas con embeddings
    usuarios_con_embeddings = usuarios_col.count_documents({
        "resenas.contenidoEmbedding": {"$exists": True}
    })
    
    print(f"  Usuarios totales: {total_usuarios}")
    print(f"  Usuarios con reseñas: {usuarios_con_resenas}")
    print(f"  Total de reseñas embebidas: {total_resenas}")
    print(f"  Usuarios con reseñas con embedding: {usuarios_con_embeddings}")
    
    if usuarios_con_embeddings > 0:
        # Verificar dimensión del embedding de una reseña
        usuario_sample = usuarios_col.find_one({
            "resenas.contenidoEmbedding": {"$exists": True}
        })
        if usuario_sample and "resenas" in usuario_sample and len(usuario_sample["resenas"]) > 0:
            if "contenidoEmbedding" in usuario_sample["resenas"][0]:
                dim = len(usuario_sample["resenas"][0]["contenidoEmbedding"])
                print(f"  Dimensión de embeddings: {dim}")
                print(f"  ✓ Embeddings de reseñas OK")
            else:
                print(f"  ⚠ No se pudo verificar la dimensión")
        else:
            print(f"  ⚠ No se pudo verificar la dimensión")
    else:
        print(f"  ✗ No hay reseñas con embeddings")
    
    print()


def list_indexes(db):
    """Lista todos los índices creados en cada colección."""
    print("\n📑 ÍNDICES CREADOS POR COLECCIÓN")
    print("-" * 60)
    
    for collection_name in COLLECTIONS.values():
        indexes = db[collection_name].list_indexes()
        index_list = list(indexes)
        
        print(f"\n  {collection_name} ({len(index_list)} índices):")
        for idx in index_list:
            name = idx.get('name', 'N/A')
            keys = idx.get('key', {})
            unique = " [UNIQUE]" if idx.get('unique', False) else ""
            text = " [TEXT]" if any(v == 'text' for v in keys.values()) else ""
            
            # Formatear las claves del índice
            keys_str = ", ".join([f"{k}:{v}" for k, v in keys.items()])
            
            print(f"    - {name}{unique}{text}")
            print(f"      {keys_str}")
    
    print()


def show_statistics(db):
    """Muestra estadísticas interesantes de los datos."""
    print("\n📈 ESTADÍSTICAS GENERALES")
    print("-" * 60)
    
    # Productos por categoría
    print("\n  Productos por categoría:")
    productos_col = db[COLLECTIONS['PRODUCTOS']]
    categorias_col = db[COLLECTIONS['CATEGORIAS']]
    
    # Obtener nombres de categorías
    categorias_map = {cat['idCategoria']: cat['nombre'] for cat in categorias_col.find()}
    
    pipeline = [
        {"$group": {
            "_id": "$idCategoria",
            "cantidad": {"$sum": 1},
            "precio_promedio": {"$avg": "$precioUsd"}
        }},
        {"$sort": {"cantidad": -1}}
    ]
    
    for result in productos_col.aggregate(pipeline):
        categoria_id = result['_id']
        categoria_nombre = categorias_map.get(categoria_id, f"ID {categoria_id}")
        cantidad = result['cantidad']
        precio_prom = result.get('precio_promedio', 0)
        print(f"    {categoria_nombre:20s}: {cantidad:3d} productos (Precio prom: ${precio_prom:.2f})")
    
    # Productos por marca (embebida)
    print("\n  Top 5 marcas con más productos:")
    pipeline = [
        {"$group": {
            "_id": "$marca.nombre",
            "cantidad": {"$sum": 1}
        }},
        {"$sort": {"cantidad": -1}},
        {"$limit": 5}
    ]
    
    for result in productos_col.aggregate(pipeline):
        marca = result['_id']
        cantidad = result['cantidad']
        print(f"    {marca:20s}: {cantidad:3d} productos")
    
    # Estadísticas de reseñas (EMBEBIDAS en usuarios)
    print("\n  Estadísticas de reseñas embebidas:")
    usuarios_col = db[COLLECTIONS['USUARIOS']]
    
    # Contar total de reseñas
    pipeline = [
        {"$match": {"resenas": {"$exists": True}}},
        {"$project": {"num_resenas": {"$size": {"$ifNull": ["$resenas", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$num_resenas"}}}
    ]
    result = list(usuarios_col.aggregate(pipeline))
    total_resenas = result[0]["total"] if result else 0
    
    print(f"    Total de reseñas: {total_resenas}")
    
    # Productos con reseñas
    if total_resenas > 0:
        productos_con_resenas_pipeline = [
            {"$match": {"resenas": {"$exists": True, "$ne": []}}},
            {"$unwind": "$resenas"},
            {"$group": {"_id": "$resenas.idProducto"}},
            {"$count": "total"}
        ]
        result = list(usuarios_col.aggregate(productos_con_resenas_pipeline))
        productos_con_resenas = result[0]["total"] if result else 0
        
        promedio = total_resenas / productos_con_resenas if productos_con_resenas > 0 else 0
        print(f"    Productos con reseñas: {productos_con_resenas}")
        print(f"    Promedio de reseñas por producto: {promedio:.2f}")
    
    # Distribución de calificaciones
    print("\n  Distribución de calificaciones:")
    pipeline = [
        {"$match": {"resenas": {"$exists": True, "$ne": []}}},
        {"$unwind": "$resenas"},
        {"$group": {
            "_id": "$resenas.calificacion",
            "cantidad": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    for result in usuarios_col.aggregate(pipeline):
        estrellas = result['_id']
        cantidad = result['cantidad']
        porcentaje = (cantidad / total_resenas * 100) if total_resenas > 0 else 0
        barra = "█" * int(porcentaje / 2)
        print(f"    {estrellas} ⭐: {cantidad:4d} ({porcentaje:5.1f}%) {barra}")
    
    # Reseñas por idioma
    print("\n  Reseñas por idioma:")
    pipeline = [
        {"$match": {"resenas": {"$exists": True, "$ne": []}}},
        {"$unwind": "$resenas"},
        {"$group": {
            "_id": "$resenas.idioma",
            "cantidad": {"$sum": 1}
        }},
        {"$sort": {"cantidad": -1}}
    ]
    
    for result in usuarios_col.aggregate(pipeline):
        idioma = result['_id']
        cantidad = result['cantidad']
        porcentaje = (cantidad / total_resenas * 100) if total_resenas > 0 else 0
        print(f"    {idioma:5s}: {cantidad:4d} ({porcentaje:5.1f}%)")
    
    # Compras verificadas
    pipeline = [
        {"$match": {"resenas": {"$exists": True, "$ne": []}}},
        {"$unwind": "$resenas"},
        {"$match": {"resenas.compraVerificada": True}},
        {"$count": "total"}
    ]
    result = list(usuarios_col.aggregate(pipeline))
    compras_verificadas = result[0]["total"] if result else 0
    porcentaje_verificado = (compras_verificadas / total_resenas * 100) if total_resenas > 0 else 0
    print(f"\n  Compras verificadas: {compras_verificadas} ({porcentaje_verificado:.1f}%)")
    
    # Estadísticas de imágenes
    print("\n  Estadísticas de imágenes:")
    imagenes_col = db[COLLECTIONS['IMAGENES']]
    
    total_imagenes = imagenes_col.count_documents({})
    print(f"    Total de imágenes: {total_imagenes}")
    
    if total_imagenes > 0:
        productos_con_imagenes_pipeline = [
            {"$group": {"_id": "$idProducto"}},
            {"$count": "total"}
        ]
        result = list(imagenes_col.aggregate(productos_con_imagenes_pipeline))
        productos_con_imagenes = result[0]["total"] if result else 0
        
        promedio_imgs = total_imagenes / productos_con_imagenes if productos_con_imagenes > 0 else 0
        print(f"    Productos con imágenes: {productos_con_imagenes}")
        print(f"    Promedio de imágenes por producto: {promedio_imgs:.2f}")
        
        # Imágenes por tipo
        print("\n    Imágenes por tipo:")
        pipeline = [
            {"$group": {
                "_id": "$tipoImagen",
                "cantidad": {"$sum": 1}
            }},
            {"$sort": {"cantidad": -1}}
        ]
        
        for result in imagenes_col.aggregate(pipeline):
            tipo = result['_id']
            cantidad = result['cantidad']
            print(f"      {tipo:20s}: {cantidad:3d}")
    
    print()


def show_sample_data(db):
    """Muestra ejemplos de datos para verificación manual."""
    print("\n📄 EJEMPLOS DE DATOS")
    print("-" * 60)
    
    # Mostrar un producto de ejemplo
    print("\n  Ejemplo de Producto:")
    producto = db[COLLECTIONS['PRODUCTOS']].find_one()
    if producto:
        print(f"    Código: {producto.get('codigoProducto')}")
        print(f"    Nombre: {producto.get('nombre')}")
        print(f"    Marca: {producto.get('marca', {}).get('nombre')}")
        print(f"    ID Categoría: {producto.get('idCategoria')}")
        print(f"    Precio: ${producto.get('precioUsd')}")
        print(f"    Embedding: {'✓ Presente' if producto.get('descripcionEmbedding') else '✗ Ausente'}")
        if producto.get('procesador'):
            print(f"    Especificaciones: procesador={producto.get('procesador')}, RAM={producto.get('memoriaRam')}")
    
    # Mostrar un usuario con reseñas de ejemplo
    print("\n  Ejemplo de Usuario con Reseñas:")
    usuario = db[COLLECTIONS['USUARIOS']].find_one({"resenas": {"$exists": True, "$ne": []}})
    if usuario:
        print(f"    Nombre de usuario: {usuario.get('nombreUsuario')}")
        print(f"    Correo: {usuario.get('correo')}")
        print(f"    Comprador verificado: {'Sí' if usuario.get('compradorVerificado') else 'No'}")
        resenas = usuario.get('resenas', [])
        if resenas:
            print(f"    Número de reseñas: {len(resenas)}")
            print(f"\n    Primera reseña:")
            resena = resenas[0]
            print(f"      Calificación: {resena.get('calificacion')} ⭐")
            print(f"      Título: {resena.get('titulo')}")
            print(f"      Idioma: {resena.get('idioma')}")
            print(f"      Compra verificada: {'Sí' if resena.get('compraVerificada') else 'No'}")
            print(f"      Embedding: {'✓ Presente' if resena.get('contenidoEmbedding') else '✗ Ausente'}")
    
    print()


def verify_all_data():
    """
    Ejecuta todas las verificaciones de datos.
    
    Returns:
        bool: True si la verificación fue exitosa
    """
    try:
        print("\n" + "="*60)
        print("VERIFICACIÓN DE DATOS CARGADOS")
        print("="*60)
        
        # Conectar a la base de datos
        db = get_database()
        
        # Ejecutar verificaciones
        count_documents(db)
        verify_embeddings(db)
        list_indexes(db)
        show_statistics(db)
        show_sample_data(db)
        
        print("="*60)
        print("✓ VERIFICACIÓN COMPLETADA")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    verify_all_data()
