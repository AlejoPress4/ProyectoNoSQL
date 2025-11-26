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
            "required": ["codigoProducto", "nombre", "descripcion", "marca", "idCategoria"],
            "properties": {
                "idProducto": {
                    "bsonType": "int",
                    "description": "ID secuencial del producto"
                },
                "codigoProducto": {
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
                "idMarca": {
                    "bsonType": "int",
                    "description": "ID de la marca"
                },
                "idCategoria": {
                    "bsonType": "int",
                    "description": "ID de la categoría"
                },
                "descripcion": {
                    "bsonType": "string",
                    "minLength": 50,
                    "description": "Descripción detallada del producto"
                },
                "precioUsd": {
                    "bsonType": ["double", "decimal"],
                    "minimum": 0,
                    "description": "Precio en dólares estadounidenses"
                },
                "fechaLanzamiento": {
                    "bsonType": "date",
                    "description": "Fecha de lanzamiento del producto"
                },
                "disponibilidad": {
                    "enum": DISPONIBILIDAD_ENUM,
                    "description": "Estado de disponibilidad del producto"
                },
                "calificacionPromedio": {
                    "bsonType": ["double", "decimal"],
                    "minimum": 0,
                    "maximum": 5
                },
                "cantidadResenas": {
                    "bsonType": "int",
                    "minimum": 0
                },
                "fechaCreacion": {
                    "bsonType": "date"
                },
                "fechaActualizacion": {
                    "bsonType": "date"
                },
                "idEspecificaciones": {
                    "bsonType": "int",
                    "description": "ID de las especificaciones (campo plano)"
                },
                "procesador": {
                    "bsonType": "string",
                    "description": "Especificación de procesador (campo plano)"
                },
                "memoriaRam": {
                    "bsonType": ["string", "array"],
                    "description": "Especificación de memoria RAM (campo plano)"
                },
                "almacenamiento": {
                    "bsonType": ["string", "array"],
                    "description": "Especificación de almacenamiento (campo plano, puede ser array de opciones)"
                },
                "pantalla": {
                    "bsonType": "string",
                    "description": "Especificación de pantalla (campo plano)"
                },
                "bateria": {
                    "bsonType": "string",
                    "description": "Especificación de batería (campo plano)"
                },
                "sistemaOperativo": {
                    "bsonType": "string",
                    "description": "Especificación de sistema operativo (campo plano)"
                },
                "marca": {
                    "bsonType": "object",
                    "required": ["nombre", "pais"],
                    "properties": {
                        "nombre": {"bsonType": "string"},
                        "pais": {"bsonType": "string"},
                        "sitioWeb": {"bsonType": "string"},
                        "descripcion": {"bsonType": "string"}
                    }
                },
                "descripcionEmbedding": {
                    "bsonType": "array",
                    "description": "Vector de embedding de la descripción (384 dimensiones)"
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['PRODUCTOS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['PRODUCTOS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['PRODUCTOS']}' ya existe")


def create_categorias_collection(db):
    """Crea la colección de categorías con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre", "slug"],
            "properties": {
                "idCategoria": {
                    "bsonType": "int",
                    "description": "ID secuencial de la categoría"
                },
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
                "idCategoriaPadre": {
                    "bsonType": ["int", "null"],
                    "description": "ID de categoría padre para jerarquía"
                },
                "fechaCreacion": {
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
            "required": ["nombreUsuario", "correo"],
            "properties": {
                "idUsuario": {
                    "bsonType": "int",
                    "description": "ID secuencial del usuario"
                },
                "nombreUsuario": {
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
                "nombreCompleto": {
                    "bsonType": "string"
                },
                "compradorVerificado": {
                    "bsonType": "bool",
                    "description": "Indica si el usuario ha realizado compras verificadas"
                },
                "fechaCreacion": {
                    "bsonType": "date"
                },
                "ultimoAcceso": {
                    "bsonType": "date"
                },
                "resenas": {
                    "bsonType": "array",
                    "description": "Array de reseñas embebidas del usuario",
                    "items": {
                        "bsonType": "object",
                        "required": ["idProducto", "calificacion", "titulo", "contenido"],
                        "properties": {
                            "idResena": {
                                "bsonType": "int",
                                "description": "ID de la reseña"
                            },
                            "idProducto": {
                                "bsonType": "int",
                                "description": "ID del producto"
                            },
                            "calificacion": {
                                "bsonType": "int",
                                "minimum": 1,
                                "maximum": 5
                            },
                            "titulo": {"bsonType": "string"},
                            "contenido": {"bsonType": "string"},
                            "ventajas": {
                                "bsonType": "array",
                                "items": {"bsonType": "string"}
                            },
                            "desventajas": {
                                "bsonType": "array",
                                "items": {"bsonType": "string"}
                            },
                            "idioma": {"bsonType": "string"},
                            "votosUtiles": {"bsonType": "int"},
                            "compraVerificada": {"bsonType": "bool"},
                            "fechaCreacion": {"bsonType": "date"},
                            "fechaActualizacion": {"bsonType": "date"},
                            "contenidoEmbedding": {
                                "bsonType": "array",
                                "description": "Vector embedding del contenido"
                            }
                        }
                    }
                }
            }
        }
    }
    
    try:
        db.create_collection(COLLECTIONS['USUARIOS'], validator=validator)
        print(f"✓ Colección '{COLLECTIONS['USUARIOS']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠ La colección '{COLLECTIONS['USUARIOS']}' ya existe")


def create_imagenes_collection(db):
    """Crea la colección de imágenes con validación de esquema."""
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["idProducto", "urlImagen", "tipoImagen"],
            "properties": {
                "idImagen": {
                    "bsonType": "int",
                    "description": "ID secuencial de la imagen"
                },
                "idProducto": {
                    "bsonType": "int",
                    "description": "ID del producto"
                },
                "urlImagen": {
                    "bsonType": "string",
                    "description": "URL o ruta de la imagen"
                },
                "tipoImagen": {
                    "enum": TIPO_IMAGEN_ENUM,
                    "description": "Tipo de imagen"
                },
                "anguloVista": {
                    "bsonType": "string",
                    "description": "Ángulo o vista de la fotografía"
                },
                "ancho": {
                    "bsonType": "int",
                    "minimum": 1
                },
                "alto": {
                    "bsonType": "int",
                    "minimum": 1
                },
                "formato": {
                    "bsonType": "string"
                },
                "tamanoKb": {
                    "bsonType": ["int", "double"],
                    "minimum": 0
                },
                "textoAlternativo": {
                    "bsonType": "string"
                },
                "esPrincipal": {
                    "bsonType": "bool"
                },
                "ordenVisualizacion": {
                    "bsonType": "int",
                    "minimum": 1
                },
                "fechaSubida": {
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
    Marcas: EMBEBIDAS en productos (no colección independiente)
    Reseñas: EMBEBIDAS en usuarios (no colección independiente)
    
    Returns:
        bool: True si todas las colecciones se crearon exitosamente
    """
    try:
        print("\n" + "="*60)
        print("CREANDO COLECCIONES CON VALIDACIÓN DE ESQUEMA")
        print("="*60 + "\n")
        
        db = get_database()
        
        # Crear colecciones (4 colecciones independientes)
        create_categorias_collection(db)
        create_usuarios_collection(db)
        create_productos_collection(db)
        create_imagenes_collection(db)
        
        print("\n" + "="*60)
        print("✓ TODAS LAS COLECCIONES CREADAS EXITOSAMENTE")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error al crear colecciones: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    create_all_collections()
