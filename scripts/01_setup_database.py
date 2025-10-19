"""
Script 1: Configuración inicial de la base de datos
- Crear colecciones con schema validation
- Aplicar reglas de validación
"""

import sys
sys.path.append('..')

from config.db_config import get_db_config, COLLECTIONS
from pymongo.errors import CollectionInvalid


def create_articles_collection(db):
    """Crear colección 'articles' con validación de esquema"""
    
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["titulo", "contenido", "texto_embedding", "metadata", "fecha_creacion"],
            "properties": {
                "titulo": {
                    "bsonType": "string",
                    "minLength": 5,
                    "maxLength": 200,
                    "description": "Título del artículo (5-200 caracteres)"
                },
                "contenido": {
                    "bsonType": "string",
                    "minLength": 100,
                    "description": "Contenido completo del artículo (min 100 caracteres)"
                },
                "resumen": {
                    "bsonType": "string",
                    "maxLength": 500,
                    "description": "Resumen opcional del artículo"
                },
                "texto_embedding": {
                    "bsonType": "array",
                    "minItems": 384,
                    "maxItems": 384,
                    "items": {
                        "bsonType": "double"
                    },
                    "description": "Vector de embeddings (384 dimensiones)"
                },
                "metadata": {
                    "bsonType": "object",
                    "required": ["fecha_publicacion", "idioma", "categoria"],
                    "properties": {
                        "fecha_publicacion": {
                            "bsonType": "date",
                            "description": "Fecha de publicación del artículo"
                        },
                        "idioma": {
                            "bsonType": "string",
                            "enum": ["es", "en"],
                            "description": "Idioma del artículo (es o en)"
                        },
                        "categoria": {
                            "bsonType": "string",
                            "enum": [
                                "Machine Learning", "Backend", "Frontend", "DevOps", 
                                "Ciberseguridad", "Mobile", "Data Science", "Cloud", 
                                "IoT", "Blockchain"
                            ],
                            "description": "Categoría tecnológica del artículo"
                        },
                        "dificultad": {
                            "bsonType": "string",
                            "enum": ["basico", "intermedio", "avanzado"],
                            "description": "Nivel de dificultad"
                        },
                        "tiempo_lectura_min": {
                            "bsonType": "int",
                            "minimum": 1,
                            "maximum": 120,
                            "description": "Tiempo estimado de lectura en minutos"
                        },
                        "fuente": {
                            "bsonType": "string",
                            "description": "URL de la fuente original"
                        }
                    }
                },
                "autor": {
                    "bsonType": "object",
                    "properties": {
                        "nombre": {
                            "bsonType": "string",
                            "minLength": 2,
                            "maxLength": 100
                        },
                        "perfil": {
                            "bsonType": "string"
                        }
                    }
                },
                "tags": {
                    "bsonType": "array",
                    "maxItems": 10,
                    "items": {
                        "bsonType": "string",
                        "minLength": 2,
                        "maxLength": 30
                    },
                    "description": "Tags del artículo (máximo 10)"
                },
                "imagenes": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "objectId"
                    },
                    "description": "Referencias a imágenes asociadas"
                },
                "estadisticas": {
                    "bsonType": "object",
                    "properties": {
                        "vistas": {
                            "bsonType": "int",
                            "minimum": 0
                        },
                        "valoracion": {
                            "bsonType": "double",
                            "minimum": 0.0,
                            "maximum": 5.0
                        }
                    }
                },
                "fecha_creacion": {
                    "bsonType": "date",
                    "description": "Fecha de creación en el sistema"
                },
                "fecha_actualizacion": {
                    "bsonType": "date",
                    "description": "Última actualización"
                }
            }
        }
    }
    
    try:
        db.create_collection(
            COLLECTIONS['ARTICLES'],
            validator=validator,
            validationLevel="strict",
            validationAction="error"
        )
        print(f"✅ Colección '{COLLECTIONS['ARTICLES']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠️  Colección '{COLLECTIONS['ARTICLES']}' ya existe")


def create_images_collection(db):
    """Crear colección 'images' con validación de esquema"""
    
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre", "url", "image_embedding", "metadata", "fecha_creacion"],
            "properties": {
                "nombre": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 100,
                    "description": "Nombre del archivo de imagen"
                },
                "descripcion": {
                    "bsonType": "string",
                    "maxLength": 500,
                    "description": "Descripción de la imagen"
                },
                "url": {
                    "bsonType": "string",
                    "description": "URL de la imagen"
                },
                "image_embedding": {
                    "bsonType": "array",
                    "minItems": 512,
                    "maxItems": 512,
                    "items": {
                        "bsonType": "double"
                    },
                    "description": "Vector de embeddings de imagen (512 dimensiones)"
                },
                "metadata": {
                    "bsonType": "object",
                    "required": ["formato", "tamaño_kb", "tipo"],
                    "properties": {
                        "formato": {
                            "bsonType": "string",
                            "enum": ["png", "jpg", "jpeg", "svg", "gif", "webp"],
                            "description": "Formato de la imagen"
                        },
                        "tamaño_kb": {
                            "bsonType": "int",
                            "minimum": 1,
                            "maximum": 5120,
                            "description": "Tamaño en KB (máx 5MB)"
                        },
                        "dimensiones": {
                            "bsonType": "object",
                            "properties": {
                                "ancho": {
                                    "bsonType": "int",
                                    "minimum": 1
                                },
                                "alto": {
                                    "bsonType": "int",
                                    "minimum": 1
                                }
                            }
                        },
                        "tipo": {
                            "bsonType": "string",
                            "enum": ["diagrama", "screenshot", "grafico", "foto", "icono"],
                            "description": "Tipo de imagen"
                        }
                    }
                },
                "tags": {
                    "bsonType": "array",
                    "maxItems": 15,
                    "items": {
                        "bsonType": "string",
                        "minLength": 2,
                        "maxLength": 30
                    }
                },
                "fecha_creacion": {
                    "bsonType": "date"
                }
            }
        }
    }
    
    try:
        db.create_collection(
            COLLECTIONS['IMAGES'],
            validator=validator,
            validationLevel="strict",
            validationAction="error"
        )
        print(f"✅ Colección '{COLLECTIONS['IMAGES']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠️  Colección '{COLLECTIONS['IMAGES']}' ya existe")


def create_query_history_collection(db):
    """Crear colección 'query_history' con validación de esquema"""
    
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["query_text", "query_type", "timestamp"],
            "properties": {
                "query_text": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 500,
                    "description": "Texto de la consulta del usuario"
                },
                "query_type": {
                    "bsonType": "string",
                    "enum": ["semantic", "hybrid", "image", "text"],
                    "description": "Tipo de búsqueda realizada"
                },
                "query_embedding": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "double"
                    }
                },
                "filtros_aplicados": {
                    "bsonType": "object",
                    "properties": {
                        "idioma": {
                            "bsonType": "string",
                            "enum": ["es", "en"]
                        },
                        "categoria": {
                            "bsonType": "string"
                        },
                        "fecha_desde": {
                            "bsonType": "date"
                        },
                        "fecha_hasta": {
                            "bsonType": "date"
                        }
                    }
                },
                "resultados": {
                    "bsonType": "object",
                    "properties": {
                        "count": {
                            "bsonType": "int",
                            "minimum": 0
                        },
                        "top_docs": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "objectId"
                            }
                        },
                        "scores": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "double",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        }
                    }
                },
                "metricas": {
                    "bsonType": "object",
                    "properties": {
                        "tiempo_busqueda_ms": {
                            "bsonType": "int",
                            "minimum": 0
                        },
                        "tiempo_llm_ms": {
                            "bsonType": "int",
                            "minimum": 0
                        },
                        "tiempo_total_ms": {
                            "bsonType": "int",
                            "minimum": 0
                        }
                    }
                },
                "respuesta_generada": {
                    "bsonType": "string",
                    "maxLength": 5000
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "Momento de la consulta"
                },
                "user_feedback": {
                    "bsonType": "object",
                    "properties": {
                        "util": {
                            "bsonType": "bool"
                        },
                        "comentario": {
                            "bsonType": "string",
                            "maxLength": 500
                        }
                    }
                }
            }
        }
    }
    
    try:
        db.create_collection(
            COLLECTIONS['QUERY_HISTORY'],
            validator=validator,
            validationLevel="moderate",
            validationAction="warn"
        )
        print(f"✅ Colección '{COLLECTIONS['QUERY_HISTORY']}' creada con validación")
    except CollectionInvalid:
        print(f"⚠️  Colección '{COLLECTIONS['QUERY_HISTORY']}' ya existe")


def main():
    """Ejecutar configuración inicial"""
    print("=" * 60)
    print("🚀 CONFIGURACIÓN INICIAL DE LA BASE DE DATOS")
    print("=" * 60)
    
    # Conectar a MongoDB
    config = get_db_config()
    db = config.connect()
    
    try:
        # Crear colecciones con validación
        print("\n📦 Creando colecciones con schema validation...\n")
        create_articles_collection(db)
        create_images_collection(db)
        create_query_history_collection(db)
        
        print("\n" + "=" * 60)
        print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        # Listar colecciones creadas
        collections = db.list_collection_names()
        print(f"\n📚 Colecciones disponibles: {', '.join(collections)}")
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
    finally:
        config.close()


if __name__ == "__main__":
    main()
