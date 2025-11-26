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
        # Índice único para codigoProducto
        collection.create_index(
            [("codigoProducto", ASCENDING)],
            unique=True,
            name="idx_codigoProducto_unique"
        )
        print(f"  ✓ Índice único: codigoProducto")
        
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
                ("idCategoria", ASCENDING),
                ("precioUsd", ASCENDING),
                ("calificacionPromedio", DESCENDING)
            ],
            name="idx_categoria_precio_calificacion"
        )
        print(f"  ✓ Índice compuesto: idCategoria + precioUsd + calificacionPromedio")
        
        # Índice simple para marca (nombre de marca embebida)
        collection.create_index(
            [("marca.nombre", ASCENDING)],
            name="idx_marca_nombre"
        )
        print(f"  ✓ Índice simple: marca.nombre")
        
        # Índice para disponibilidad
        collection.create_index(
            [("disponibilidad", ASCENDING)],
            name="idx_disponibilidad"
        )
        print(f"  ✓ Índice simple: disponibilidad")
        
        # Índice para búsqueda por calificación
        collection.create_index(
            [("calificacionPromedio", DESCENDING)],
            name="idx_calificacionPromedio"
        )
        print(f"  ✓ Índice simple: calificacionPromedio")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de productos: {str(e)}")


def create_imagenes_indexes(db):
    """Crea los índices para la colección de imágenes."""
    collection = db[COLLECTIONS['IMAGENES']]
    
    try:
        # Índice compuesto para obtener imágenes de un producto ordenadas
        collection.create_index(
            [
                ("idProducto", ASCENDING),
                ("ordenVisualizacion", ASCENDING)
            ],
            name="idx_producto_orden"
        )
        print(f"  ✓ Índice compuesto: idProducto + ordenVisualizacion")
        
        # Índice para imagen principal por producto
        collection.create_index(
            [
                ("idProducto", ASCENDING),
                ("esPrincipal", ASCENDING)
            ],
            name="idx_producto_principal"
        )
        print(f"  ✓ Índice compuesto: idProducto + esPrincipal")
        
        # Índice por tipo de imagen
        collection.create_index(
            [("tipoImagen", ASCENDING)],
            name="idx_tipoImagen"
        )
        print(f"  ✓ Índice simple: tipoImagen")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de imágenes: {str(e)}")


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
            [("idCategoriaPadre", ASCENDING)],
            name="idx_categoriaPadre"
        )
        print(f"  ✓ Índice simple: idCategoriaPadre")
        
    except OperationFailure as e:
        print(f"  ⚠ Error al crear índices de categorías: {str(e)}")


def create_usuarios_indexes(db):
    """Crea los índices para la colección de usuarios."""
    collection = db[COLLECTIONS['USUARIOS']]
    
    try:
        # Índice único para nombreUsuario
        collection.create_index(
            [("nombreUsuario", ASCENDING)],
            unique=True,
            name="idx_nombreUsuario_unique"
        )
        print(f"  ✓ Índice único: nombreUsuario")
        
        # Índice único para correo
        collection.create_index(
            [("correo", ASCENDING)],
            unique=True,
            name="idx_correo_unique"
        )
        print(f"  ✓ Índice único: correo")
        
        # Índice para compradores verificados
        collection.create_index(
            [("compradorVerificado", ASCENDING)],
            name="idx_compradorVerificado"
        )
        print(f"  ✓ Índice simple: compradorVerificado")
        
        # Índices para reseñas embebidas
        collection.create_index(
            [("resenas.idProducto", ASCENDING)],
            name="idx_resenas_producto"
        )
        print(f"  ✓ Índice simple: resenas.idProducto")
        
        collection.create_index(
            [("resenas.calificacion", DESCENDING)],
            name="idx_resenas_calificacion"
        )
        print(f"  ✓ Índice simple: resenas.calificacion")
        
        collection.create_index(
            [("resenas.compraVerificada", ASCENDING)],
            name="idx_resenas_compraVerificada"
        )
        print(f"  ✓ Índice simple: resenas.compraVerificada")
        
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
        
        print(f"📁 Creando índices en '{COLLECTIONS['CATEGORIAS']}':")
        create_categorias_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['USUARIOS']}':")
        create_usuarios_indexes(db)
        print()
        
        print(f"📁 Creando índices en '{COLLECTIONS['PRODUCTOS']}':")
        create_productos_indexes(db)
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
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    create_all_indexes()
