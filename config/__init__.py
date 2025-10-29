"""
Módulo de configuración para el sistema RAG de productos tecnológicos.
"""

from .mongodb_config import get_database, verify_connection
from .settings import (
    TEXT_EMBEDDING_DIM,
    IMAGE_EMBEDDING_DIM,
    EMBEDDING_MODEL_NAME,
    COLLECTIONS,
    DISPONIBILIDAD_ENUM,
    IDIOMAS_ENUM,
    TIPO_IMAGEN_ENUM,
    ANGULO_VISTA_ENUM,
    DATA_FILES
)

__all__ = [
    'get_database',
    'verify_connection',
    'TEXT_EMBEDDING_DIM',
    'IMAGE_EMBEDDING_DIM',
    'EMBEDDING_MODEL_NAME',
    'COLLECTIONS',
    'DISPONIBILIDAD_ENUM',
    'IDIOMAS_ENUM',
    'TIPO_IMAGEN_ENUM',
    'ANGULO_VISTA_ENUM',
    'DATA_FILES'
]
