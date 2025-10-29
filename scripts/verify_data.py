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
        "descripcion_embedding": {"$exists": True, "$ne": None}
    })
    
    print(f"  Productos totales: {total_productos}")
    print(f"  Productos con embedding: {productos_con_embedding}")
    
    if productos_con_embedding > 0:
        # Verificar dimensión del embedding
        producto_sample = productos_col.find_one({"descripcion_embedding": {"$exists": True}})
        if producto_sample and "descripcion_embedding" in producto_sample:
            dim = len(producto_sample["descripcion_embedding"])
            print(f"  Dimensión de embeddings: {dim}")
            print(f"  ✓ Embeddings de productos OK")
        else:
            print(f"  ⚠ No se pudo verificar la dimensión")
    else:
        print(f"  ✗ No hay productos con embeddings")
    
    print()
    
    # Verificar embeddings de reseñas
    resenas_col = db[COLLECTIONS['RESENAS']]
    total_resenas = resenas_col.count_documents({})
    resenas_con_embedding = resenas_col.count_documents({
        "contenido_embedding": {"$exists": True, "$ne": None}
    })
    
    print(f"  Reseñas totales: {total_resenas}")
    print(f"  Reseñas con embedding: {resenas_con_embedding}")
    
    if resenas_con_embedding > 0:
        # Verificar dimensión del embedding
        resena_sample = resenas_col.find_one({"contenido_embedding": {"$exists": True}})
        if resena_sample and "contenido_embedding" in resena_sample:
            dim = len(resena_sample["contenido_embedding"])
            print(f"  Dimensión de embeddings: {dim}")
            print(f"  ✓ Embeddings de reseñas OK")
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
    pipeline = [
        {"$group": {
            "_id": "$categoria.nombre",
            "cantidad": {"$sum": 1},
            "precio_promedio": {"$avg": "$metadata.precio_usd"}
        }},
        {"$sort": {"cantidad": -1}}
    ]
    
    for result in productos_col.aggregate(pipeline):
        categoria = result['_id']
        cantidad = result['cantidad']
        precio_prom = result['precio_promedio']
        print(f"    {categoria:20s}: {cantidad:3d} productos (Precio prom: ${precio_prom:.2f})")
    
    # Productos por marca
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
    
    # Estadísticas de reseñas
    print("\n  Estadísticas de reseñas:")
    resenas_col = db[COLLECTIONS['RESENAS']]
    
    total_resenas = resenas_col.count_documents({})
    print(f"    Total de reseñas: {total_resenas}")
    
    # Promedio de reseñas por producto
    productos_con_resenas = resenas_col.distinct("id_producto")
    if productos_con_resenas:
        promedio = total_resenas / len(productos_con_resenas)
        print(f"    Productos con reseñas: {len(productos_con_resenas)}")
        print(f"    Promedio de reseñas por producto: {promedio:.2f}")
    
    # Distribución de calificaciones
    print("\n  Distribución de calificaciones:")
    pipeline = [
        {"$group": {
            "_id": "$calificacion",
            "cantidad": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    for result in resenas_col.aggregate(pipeline):
        estrellas = result['_id']
        cantidad = result['cantidad']
        porcentaje = (cantidad / total_resenas * 100) if total_resenas > 0 else 0
        barra = "█" * int(porcentaje / 2)
        print(f"    {estrellas} ⭐: {cantidad:4d} ({porcentaje:5.1f}%) {barra}")
    
    # Reseñas por idioma
    print("\n  Reseñas por idioma:")
    pipeline = [
        {"$group": {
            "_id": "$idioma",
            "cantidad": {"$sum": 1}
        }},
        {"$sort": {"cantidad": -1}}
    ]
    
    for result in resenas_col.aggregate(pipeline):
        idioma = result['_id']
        cantidad = result['cantidad']
        porcentaje = (cantidad / total_resenas * 100) if total_resenas > 0 else 0
        print(f"    {idioma:5s}: {cantidad:4d} ({porcentaje:5.1f}%)")
    
    # Compras verificadas
    compras_verificadas = resenas_col.count_documents({"compra_verificada": True})
    porcentaje_verificado = (compras_verificadas / total_resenas * 100) if total_resenas > 0 else 0
    print(f"\n  Compras verificadas: {compras_verificadas} ({porcentaje_verificado:.1f}%)")
    
    # Estadísticas de imágenes
    print("\n  Estadísticas de imágenes:")
    imagenes_col = db[COLLECTIONS['IMAGENES']]
    
    total_imagenes = imagenes_col.count_documents({})
    print(f"    Total de imágenes: {total_imagenes}")
    
    if total_imagenes > 0:
        productos_con_imagenes = imagenes_col.distinct("id_producto")
        promedio_imgs = total_imagenes / len(productos_con_imagenes) if productos_con_imagenes else 0
        print(f"    Productos con imágenes: {len(productos_con_imagenes)}")
        print(f"    Promedio de imágenes por producto: {promedio_imgs:.2f}")
        
        # Imágenes por tipo
        print("\n    Imágenes por tipo:")
        pipeline = [
            {"$group": {
                "_id": "$tipo_imagen",
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
        print(f"    Código: {producto.get('codigo_producto')}")
        print(f"    Nombre: {producto.get('nombre')}")
        print(f"    Marca: {producto.get('marca', {}).get('nombre')}")
        print(f"    Categoría: {producto.get('categoria', {}).get('nombre')}")
        print(f"    Precio: ${producto.get('metadata', {}).get('precio_usd')}")
        print(f"    Embedding: {'✓ Presente' if producto.get('descripcion_embedding') else '✗ Ausente'}")
    
    # Mostrar una reseña de ejemplo
    print("\n  Ejemplo de Reseña:")
    resena = db[COLLECTIONS['RESENAS']].find_one()
    if resena:
        print(f"    Usuario: {resena.get('usuario', {}).get('nombre_usuario')}")
        print(f"    Calificación: {resena.get('calificacion')} ⭐")
        print(f"    Título: {resena.get('titulo')}")
        print(f"    Idioma: {resena.get('idioma')}")
        print(f"    Compra verificada: {'Sí' if resena.get('compra_verificada') else 'No'}")
        print(f"    Embedding: {'✓ Presente' if resena.get('contenido_embedding') else '✗ Ausente'}")
    
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
