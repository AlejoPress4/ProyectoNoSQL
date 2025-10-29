"""
Script para crear colecciones con validación de esquema en MongoDB.
"""

from pymongo.errors import CollectionInvalid
from config import get_database, COLLECTIONS, DISPONIBILIDAD_ENUM, IDIOMAS_ENUM, TIPO_IMAGEN_ENUM


def create_productos_collection(db):
    """Crea la colección de productos con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["codigo_producto", "nombre", "descripcion", "marca", "categoria", "metadata"],
            "properties": {
                "codigo_producto": {
                    "bsonType": "string",
                    "pattern": "^PROD-[0-9]{3,}$",
                    "description": "Código único del producto (formato: PROD-XXX)"
                },
                "nombre": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 200,
                    "description": "Nombre del producto"
                },
                "descripcion": {
                    "bsonType": "string",
                    "minLength": 50,
                    "description": "Descripción detallada del producto"
                },
                "marca": {
                    "bsonType": "object",
                    "required": ["id", "nombre"],
                    "properties": {
                        "id": {"bsonType": "objectId"},
                        "nombre": {"bsonType": "string"}
                    }
                },
                "categoria": {
                    "bsonType": "object",
                    "required": ["id", "nombre", "slug"],
                    "properties": {
                        "id": {"bsonType": "objectId"},
                        "nombre": {"bsonType": "string"},
                        "slug": {"bsonType": "string"}
                    }
                },
                "especificaciones": {
                    "bsonType": "object",
                    "description": "Especificaciones técnicas del producto"
                },
                "metadata": {
                    "bsonType": "object",
                    "required": ["precio_usd", "disponibilidad"],
                    "properties": {
                        "precio_usd": {
                            "bsonType": "number",
                            "minimum": 0,
                            "description": "Precio en dólares estadounidenses"
                        },
                        "fecha_lanzamiento": {
                            "bsonType": "date",
                            "description": "Fecha de lanzamiento del producto"
                        },
                        "disponibilidad": {
                            "enum": DISPONIBILIDAD_ENUM,
                            "description": "Estado de disponibilidad del producto"
                        },
                        "calificacion_promedio": {
                            "bsonType": ["double", "int"],
                            "minimum": 0,
                            "maximum": 5
                        },
                        "cantidad_resenas": {
                            "bsonType": "int",
                            "minimum": 0
                        }
                    }
                },
                "descripcion_embedding": {
                    "bsonType": "array",
                    "description": "Vector de embedding de la descripción (384 dimensiones)"
                },
                "imagen_principal": {
                    "bsonType": "string"
                },
                "fecha_creacion": {
                    "bsonType": "date"
                },
                "fecha_actualizacion": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['PRODUCTOS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['PRODUCTOS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['PRODUCTOS']}' ya existe")


def create_marcas_collection(db):
    """Crea la colección de marcas con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre", "pais"],
            "properties": {
                "nombre": {
                    "bsonType": "string",
                    "minLength": 2,
                    "maxLength": 100,
                    "description": "Nombre de la marca"
                },
                "pais": {
                    "bsonType": "string",
                    "description": "País de origen de la marca"
                },
                "sitio_web": {
                    "bsonType": "string",
                    "pattern": "^https?://",
                    "description": "Sitio web oficial de la marca"
                },
                "descripcion": {
                    "bsonType": "string",
                    "description": "Descripción de la marca"
                },
                "fecha_creacion": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['MARCAS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['MARCAS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['MARCAS']}' ya existe")


def create_categorias_collection(db):
    """Crea la colección de categorías con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre", "slug"],
            "properties": {
                "nombre": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 100,
                    "description": "Nombre de la categoría"
                },
                "slug": {
                    "bsonType": "string",
                    "pattern": "^[a-z0-9-]+$",
                    "description": "Slug único para URLs"
                },
                "descripcion": {
                    "bsonType": "string"
                },
                "id_categoria_padre": {
                    "bsonType": ["objectId", "null"],
                    "description": "ID de categoría padre para jerarquía"
                },
                "fecha_creacion": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['CATEGORIAS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['CATEGORIAS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['CATEGORIAS']}' ya existe")


def create_usuarios_collection(db):
    """Crea la colección de usuarios con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre_usuario", "correo"],
            "properties": {
                "nombre_usuario": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 50,
                    "pattern": "^[a-zA-Z0-9_]+$",
                    "description": "Nombre de usuario único"
                },
                "correo": {
                    "bsonType": "string",
                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                    "description": "Correo electrónico válido"
                },
                "nombre_completo": {
                    "bsonType": "string"
                },
                "comprador_verificado": {
                    "bsonType": "bool",
                    "description": "Indica si el usuario ha realizado compras verificadas"
                },
                "fecha_creacion": {
                    "bsonType": "date"
                },
                "ultimo_acceso": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['USUARIOS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['USUARIOS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['USUARIOS']}' ya existe")


def create_resenas_collection(db):
    """Crea la colección de reseñas con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id_producto", "id_usuario", "calificacion", "titulo", "contenido"],
            "properties": {
                "id_producto": {
                    "bsonType": "objectId",
                    "description": "ID del producto reseñado"
                },
                "id_usuario": {
                    "bsonType": "objectId",
                    "description": "ID del usuario que escribe la reseña"
                },
                "usuario": {
                    "bsonType": "object",
                    "required": ["nombre_usuario"],
                    "properties": {
                        "nombre_usuario": {"bsonType": "string"},
                        "comprador_verificado": {"bsonType": "bool"}
                    }
                },
                "calificacion": {
                    "bsonType": "int",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Calificación de 1 a 5 estrellas"
                },
                "titulo": {
                    "bsonType": "string",
                    "minLength": 5,
                    "maxLength": 150,
                    "description": "Título de la reseña"
                },
                "contenido": {
                    "bsonType": "string",
                    "minLength": 20,
                    "description": "Contenido detallado de la reseña"
                },
                "ventajas": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "desventajas": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "idioma": {
                    "enum": IDIOMAS_ENUM,
                    "description": "Idioma de la reseña"
                },
                "votos_utiles": {
                    "bsonType": "int",
                    "minimum": 0
                },
                "compra_verificada": {
                    "bsonType": "bool"
                },
                "contenido_embedding": {
                    "bsonType": "array",
                    "description": "Vector de embedding del contenido (384 dimensiones)"
                },
                "fecha_creacion": {
                    "bsonType": "date"
                },
                "fecha_actualizacion": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['RESENAS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['RESENAS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['RESENAS']}' ya existe")


def create_imagenes_collection(db):
    """Crea la colección de imágenes con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id_producto", "url_imagen", "tipo_imagen"],
            "properties": {
                "id_producto": {
                    "bsonType": "objectId",
                    "description": "ID del producto"
                },
                "url_imagen": {
                    "bsonType": "string",
                    "description": "URL o ruta de la imagen"
                },
                "tipo_imagen": {
                    "enum": TIPO_IMAGEN_ENUM,
                    "description": "Tipo de imagen"
                },
                "angulo_vista": {
                    "bsonType": "string",
                    "description": "Ángulo o vista de la fotografía"
                },
                "metadata": {
                    "bsonType": "object",
                    "properties": {
                        "ancho": {"bsonType": "int", "minimum": 1},
                        "alto": {"bsonType": "int", "minimum": 1},
                        "formato": {"bsonType": "string"},
                        "tamano_kb": {"bsonType": ["int", "double"], "minimum": 0}
                    }
                },
                "imagen_embedding": {
                    "bsonType": "array",
                    "description": "Vector de embedding de la imagen (512 dimensiones)"
                },
                "texto_alternativo": {
                    "bsonType": "string"
                },
                "es_principal": {
                    "bsonType": "bool"
                },
                "orden_visualizacion": {
                    "bsonType": "int",
                    "minimum": 1
                },
                "fecha_subida": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['IMAGENES'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['IMAGENES']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['IMAGENES']}' ya existe")


def create_all_collections():
    """
    Crea todas las colecciones del sistema con sus respectivas validaciones.
    
    Returns:
        bool: True si todas las colecciones se crearon exitosamente
    """
    try:
        print("\n" + "="*60)
        print("CREANDO COLECCIONES CON VALIDACIÓN DE ESQUEMA")
        print("="*60 + "\n")
        
        db = get_database()
        
        # Crear cada colección
        create_marcas_collection(db)
        create_categorias_collection(db)
        create_usuarios_collection(db)
        create_productos_collection(db)
        create_resenas_collection(db)
        create_imagenes_collection(db)
        
        print("\n" + "="*60)
        print("✓ TODAS LAS COLECCIONES CREADAS EXITOSAMENTE")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error al crear colecciones: {str(e)}")
        return False


if __name__ == "__main__":
    create_all_collections()
