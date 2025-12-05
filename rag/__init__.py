"""
Módulo RAG para el sistema de productos.
"""

from .groq_rag import rag_query_productos, rag_query_resenas, chat_interactive

__all__ = [
    'rag_query_productos',
    'rag_query_resenas',
    'chat_interactive'
]