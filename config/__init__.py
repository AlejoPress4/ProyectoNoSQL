"""
Módulo de configuración para el sistema RAG de productos tecnológicos.
"""

from .mongodb_config import get_database, verify_connection
from .settings import (
    TEXT_EMBEDDING_DIM,
    IMAGE_EMBEDDING_DIM,
    EMBEDDING_MODEL_NAME,
    COLLECTIONS
)

__all__ = [
    'get_database',
    'verify_connection',
    'TEXT_EMBEDDING_DIM',
    'IMAGE_EMBEDDING_DIM',
    'EMBEDDING_MODEL_NAME',
    'COLLECTIONS'
]
