"""
Módulo de búsqueda vectorial para el sistema RAG.
"""

from .vector_search import search_productos, search_resenas, search_by_image

__all__ = [
    'search_productos',
    'search_resenas', 
    'search_by_image'
]