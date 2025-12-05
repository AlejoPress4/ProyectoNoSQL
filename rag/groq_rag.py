"""
Sistema RAG usando Groq como LLM.
Adaptado del rag_llm.py existente.
"""

import os
from typing import List, Dict, Any
from search.vector_search import search_productos, search_resenas


def build_context_from_productos(productos: List[Dict]) -> str:
    """
    Construye contexto a partir de productos encontrados.
    
    Args:
        productos: Lista de productos
        
    Returns:
        Texto con información de productos
    """
    if not productos:
        return "No se encontraron productos relevantes."
    
    context_parts = []
    for i, prod in enumerate(productos, 1):
        marca = prod.get("marca", {}).get("nombre", "N/A")
        precio = prod.get("precioUsd", 0)
        rating = prod.get("calificacionPromedio", 0)
        num_reviews = prod.get("cantidadResenas", 0)
        
        context_parts.append(
            f"{i}. {prod['nombre']} (Marca: {marca})\n"
            f"   Precio: ${precio:.2f} USD\n"
            f"   Calificación: {rating:.1f}/5.0 ({num_reviews} reseñas)\n"
            f"   Descripción: {prod['descripcion']}\n"
        )
    
    return "\n".join(context_parts)


def build_context_from_resenas(resenas: List[Dict]) -> str:
    """
    Construye contexto a partir de reseñas.
    
    Args:
        resenas: Lista de reseñas
        
    Returns:
        Texto con reseñas
    """
    if not resenas:
        return "No se encontraron reseñas relevantes."
    
    context_parts = []
    for i, item in enumerate(resenas, 1):
        resena = item["resena"]
        usuario = item["nombreUsuario"]
        verificado = "✓ Comprador verificado" if item["compradorVerificado"] else ""
        
        context_parts.append(
            f"{i}. Reseña de {usuario} {verificado}\n"
            f"   Calificación: {resena['calificacion']}/5\n"
            f"   {resena['titulo']}\n"
            f"   {resena['contenido']}\n"
        )
    
    return "\n".join(context_parts)


def generate_rag_response(
    question: str,
    context: str
) -> str:
    """
    Genera respuesta usando Groq con contexto RAG.
    
    Args:
        question: Pregunta del usuario
        context: Contexto recuperado de la base de datos
        
    Returns:
        Respuesta generada por el LLM
    """
    try:
        from groq import Groq
        
        # Configurar cliente Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("tu_"):
            return "❌ API Key de Groq no configurada. Por favor, configura GROQ_API_KEY en tu archivo .env"
        
        client = Groq(api_key=api_key)
        
        # Construir prompt
        prompt = f"""Eres un asistente experto en productos tecnológicos. Tu trabajo es responder preguntas basándote ÚNICAMENTE en la información proporcionada.

CONTEXTO DE LA BASE DE DATOS:
{context}

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES:
- Responde SOLO con información del contexto proporcionado
- Si la información no está en el contexto, di "No tengo información suficiente"
- Sé específico y menciona nombres de productos, precios y características
- Sé conciso pero completo
- Responde en español

RESPUESTA:"""

        print("🤖 Groq está generando la respuesta...")
        
        # Llamada a Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1000
        )
        
        return chat_completion.choices[0].message.content
        
    except ImportError:
        return "❌ Librería 'groq' no instalada. Instala con: pip install groq"
    except Exception as e:
        return f"❌ Error al generar respuesta con Groq: {str(e)}\n¿Tu API Key es válida?"


def rag_query_productos(
    question: str,
    num_results: int = 5
) -> Dict[str, Any]:
    """
    Pipeline RAG completo para preguntas sobre productos.
    
    Args:
        question: Pregunta del usuario
        num_results: Número de productos a recuperar
        
    Returns:
        Diccionario con contexto, respuesta y fuentes
    """
    # Paso 1: Búsqueda vectorial (Retrieval)
    productos = search_productos(question, limit=num_results)
    
    if not productos:
        return {
            "pregunta": question,
            "contexto": "No se encontraron productos relevantes.",
            "respuesta": "Lo siento, no encontré productos que coincidan con tu consulta.",
            "fuentes": [],
            "num_fuentes": 0
        }
    
    # Paso 2: Construir contexto
    context = build_context_from_productos(productos)
    
    # Paso 3: Generar respuesta (Generation)
    respuesta = generate_rag_response(question, context)
    
    # Retornar todo
    return {
        "pregunta": question,
        "contexto": context,
        "respuesta": respuesta,
        "fuentes": [p["nombre"] for p in productos],
        "num_fuentes": len(productos)
    }


def rag_query_resenas(
    question: str,
    num_results: int = 5
) -> Dict[str, Any]:
    """
    Pipeline RAG para análisis de reseñas.
    
    Args:
        question: Pregunta del usuario
        num_results: Número de reseñas a recuperar
        
    Returns:
        Diccionario con análisis de reseñas
    """
    # Retrieval de reseñas
    resenas = search_resenas(question, limit=num_results)
    
    if not resenas:
        return {
            "pregunta": question,
            "contexto": "No se encontraron reseñas relevantes.",
            "respuesta": "No encontré reseñas relacionadas con tu consulta.",
            "fuentes": [],
            "num_resenas_analizadas": 0
        }
    
    # Construir contexto
    context = build_context_from_resenas(resenas)
    
    # Generar respuesta
    respuesta = generate_rag_response(question, context)
    
    return {
        "pregunta": question,
        "contexto": context,
        "respuesta": respuesta,
        "num_resenas_analizadas": len(resenas)
    }


def chat_interactive():
    """Modo chat interactivo con el sistema RAG."""
    print("\n" + "="*70)
    print(" "*15 + "🤖 CHAT RAG - Sistema de Productos")
    print("="*70)
    print("\nComandos:")
    print("  - Escribe tu pregunta y presiona Enter")
    print("  - '/exit' para salir")
    print("  - '/resenas <consulta>' para buscar en reseñas")
    print("  - '/productos <consulta>' para buscar productos")
    print("\n" + "-"*70)
    
    while True:
        try:
            question = input("\n🧑 Tú: ").strip()
            
            if not question:
                continue
            
            if question.lower() == '/exit':
                print("\n👋 ¡Hasta luego!")
                break
            
            if question.lower().startswith('/resenas '):
                query = question.split(' ', 1)[1]
                result = rag_query_resenas(query, num_results=5)
            elif question.lower().startswith('/productos '):
                query = question.split(' ', 1)[1]
                result = rag_query_productos(query, num_results=5)
            else:
                # Búsqueda por defecto en productos
                result = rag_query_productos(question, num_results=5)
            
            print(f"\n🤖 Asistente:")
            print(result["respuesta"])
            print(f"\n📚 Basado en {result['num_fuentes']} fuentes")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrumpido")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    # Pruebas básicas
    print("🧪 Pruebas del módulo RAG")
    
    # Test 1: RAG de productos
    print("\n1. RAG Query - Productos:")
    result = rag_query_productos("¿Qué smartphone tiene la mejor cámara y cuesta menos de $900?")
    print(f"Respuesta: {result['respuesta'][:100]}...")
    print(f"Fuentes: {result['num_fuentes']}")
    
    # Test 2: RAG de reseñas
    print("\n2. RAG Query - Reseñas:")
    result = rag_query_resenas("batería dura poco")
    print(f"Respuesta: {result['respuesta'][:100]}...")
    print(f"Reseñas analizadas: {result['num_resenas_analizadas']}")