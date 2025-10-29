"""
Script para crear índices en las colecciones de MongoDB.
"""

from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure
from config import get_database, COLLECTIONS


def create_productos_indexes(db):
    """Crea los índices para la colección de productos."""
    collection = db[COLLECTIONS['PRODUCTOS']]
    
    try:
        # Índice único para codigo_producto
        collection.create_index(
            [("codigo_producto", ASCENDING)],
            unique=True,
            name="idx_codigo_producto_unique"
        )
        print(f"  ✓ Índice único: codigo_producto")
        
        # Índice de texto para búsquedas en nombre y descripción
        collection.create_index(
            [("nombre", TEXT), ("descripcion", TEXT)],
            default_language="spanish",
            name="idx_text_nombre_descripcion"
        )
        print(f"  ✓ Índice de texto: nombre + descripcion (español)")
        
        # Índice compuesto para filtros por categoría, precio y calificación
        collection.create_index(
            [
                ("categoria.id", ASCENDING),
                ("metadata.precio_usd", ASCENDING),
                ("metadata.calificacion_promedio", DESCENDING)
            ],
            name="idx_categoria_precio_calificacion"
        )
        print(f"  ✓ Índice compuesto: categoria.id + precio + calificacion")
        
        # Índice simple para marca
        collection.create_index(
            [("marca.id", ASCENDING)],
            name="idx_marca_id"
        )
        print(f"  ✓ Índice simple: marca.id")
        
        # Índice para disponibilidad
        collection.create_index(
            [("metadata.disponibilidad", ASCENDING)],
            name="idx_disponibilidad"
        )
        print(f"  ✓ Índice simple: disponibilidad")
        
        # Índice para búsqueda por calificación
        collection.create_index(
            [("metadata.calificacion_promedio", DESCENDING)],
            name="idx_calificacion_promedio"
        )
        print(f"  ✓ Índice simple: calificacion_promedio")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de productos: {str(e)}")


def create_resenas_indexes(db):
    """Crea los índices para la colección de reseñas."""
    collection = db[COLLECTIONS['RESENAS']]
    
    try:
        # Índice compuesto para obtener reseñas de un producto ordenadas por fecha
        collection.create_index(
            [
                ("id_producto", ASCENDING),
                ("fecha_creacion", DESCENDING)
            ],
            name="idx_producto_fecha"
        )
        print(f"  ✓ Índice compuesto: id_producto + fecha_creacion")
        
        # Índice para búsquedas por usuario
        collection.create_index(
            [("id_usuario", ASCENDING)],
            name="idx_usuario"
        )
        print(f"  ✓ Índice simple: id_usuario")
        
        # Índice compuesto para filtros por idioma y calificación
        collection.create_index(
            [
                ("idioma", ASCENDING),
                ("calificacion", DESCENDING)
            ],
            name="idx_idioma_calificacion"
        )
        print(f"  ✓ Índice compuesto: idioma + calificacion")
        
        # Índice de texto para búsquedas en contenido y título
        collection.create_index(
            [("contenido", TEXT), ("titulo", TEXT)],
            default_language="spanish",
            name="idx_text_contenido_titulo"
        )
        print(f"  ✓ Índice de texto: contenido + titulo (español)")
        
        # Índice para reseñas con compra verificada
        collection.create_index(
            [("compra_verificada", ASCENDING)],
            name="idx_compra_verificada"
        )
        print(f"  ✓ Índice simple: compra_verificada")
        
        # Índice para ordenar por votos útiles
        collection.create_index(
            [("votos_utiles", DESCENDING)],
            name="idx_votos_utiles"
        )
        print(f"  ✓ Índice simple: votos_utiles")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de reseñas: {str(e)}")


def create_imagenes_indexes(db):
    """Crea los índices para la colección de imágenes."""
    collection = db[COLLECTIONS['IMAGENES']]
    
    try:
        # Índice compuesto para obtener imágenes de un producto ordenadas
        collection.create_index(
            [
                ("id_producto", ASCENDING),
                ("orden_visualizacion", ASCENDING)
            ],
            name="idx_producto_orden"
        )
        print(f"  ✓ Índice compuesto: id_producto + orden_visualizacion")
        
        # Índice para imagen principal por producto
        collection.create_index(
            [
                ("id_producto", ASCENDING),
                ("es_principal", ASCENDING)
            ],
            name="idx_producto_principal"
        )
        print(f"  ✓ Índice compuesto: id_producto + es_principal")
        
        # Índice por tipo de imagen
        collection.create_index(
            [("tipo_imagen", ASCENDING)],
            name="idx_tipo_imagen"
        )
        print(f"  ✓ Índice simple: tipo_imagen")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de imágenes: {str(e)}")


def create_marcas_indexes(db):
    """Crea los índices para la colección de marcas."""
    collection = db[COLLECTIONS['MARCAS']]
    
    try:
        # Índice único para nombre de marca
        collection.create_index(
            [("nombre", ASCENDING)],
            unique=True,
            name="idx_nombre_marca_unique"
        )
        print(f"  ✓ Índice único: nombre")
        
        # Índice de texto para búsqueda por nombre y descripción
        collection.create_index(
            [("nombre", TEXT), ("descripcion", TEXT)],
            name="idx_text_marca"
        )
        print(f"  ✓ Índice de texto: nombre + descripcion")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de marcas: {str(e)}")


def create_categorias_indexes(db):
    """Crea los índices para la colección de categorías."""
    collection = db[COLLECTIONS['CATEGORIAS']]
    
    try:
        # Índice único para slug
        collection.create_index(
            [("slug", ASCENDING)],
            unique=True,
            name="idx_slug_unique"
        )
        print(f"  ✓ Índice único: slug")
        
        # Índice para jerarquía de categorías
        collection.create_index(
            [("id_categoria_padre", ASCENDING)],
            name="idx_categoria_padre"
        )
        print(f"  ✓ Índice simple: id_categoria_padre")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de categorías: {str(e)}")


def create_usuarios_indexes(db):
    """Crea los índices para la colección de usuarios."""
    collection = db[COLLECTIONS['USUARIOS']]
    
    try:
        # Índice único para nombre_usuario
        collection.create_index(
            [("nombre_usuario", ASCENDING)],
            unique=True,
            name="idx_nombre_usuario_unique"
        )
        print(f"  ✓ Índice único: nombre_usuario")
        
        # Índice único para correo
        collection.create_index(
            [("correo", ASCENDING)],
            unique=True,
            name="idx_correo_unique"
        )
        print(f"  ✓ Índice único: correo")
        
        # Índice para compradores verificados
        collection.create_index(
            [("comprador_verificado", ASCENDING)],
            name="idx_comprador_verificado"
        )
        print(f"  ✓ Índice simple: comprador_verificado")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de usuarios: {str(e)}")


def create_all_indexes():
    """
    Crea todos los índices necesarios para el sistema.
    
    Returns:
        bool: True si todos los índices se crearon exitosamente
    """
    try:
        print("\n" + "="*60)
        print("CREANDO ÍNDICES EN COLECCIONES")
        print("="*60 + "\n")
        
        db = get_database()
        
        print(f"📁 Creando índices en '{COLLECTIONS['MARCAS']}':")
        create_marcas_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['CATEGORIAS']}':")
        create_categorias_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['USUARIOS']}':")
        create_usuarios_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['PRODUCTOS']}':")
        create_productos_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['RESENAS']}':")
        create_resenas_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['IMAGENES']}':")
        create_imagenes_indexes(db)
        print()
        
        print("="*60)
        print("✓ TODOS LOS ÍNDICES CREADOS EXITOSAMENTE")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error al crear índices: {str(e)}")
        return False


if __name__ == "__main__":
    create_all_indexes()
