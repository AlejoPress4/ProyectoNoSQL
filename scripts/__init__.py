"""
Scripts para configuración y carga de datos del sistema RAG.
"""

from .create_collections import create_all_collections
from .create_indexes import create_all_indexes
from .load_data import load_all_data
from .verify_data import verify_all_data

__all__ = [
    'create_all_collections',
    'create_all_indexes',
    'load_all_data',
    'verify_all_data'
]
