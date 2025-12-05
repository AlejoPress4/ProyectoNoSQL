#!/usr/bin/env python3
"""
Sistema RAG Multimodal v2.0 con Groq LLM
Aplicación principal con menú interactivo

Proyecto: ProyectoNoSQL - Bases de Datos No Relacionales
Autor: Tu nombre
Fecha: Diciembre 2024
"""

import sys
import os
import platform
from typing import Optional

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports del proyecto
from config import verify_connection
from scripts import (
    create_all_collections,
    create_all_indexes,
    load_all_data,
    verify_all_data
)
from search.vector_search import search_productos, search_resenas, search_by_image, hybrid_search
from rag.groq_rag import rag_query_productos, rag_query_resenas, chat_interactive


def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def print_header():
    """Imprime el encabezado de la aplicación."""
    print("\n" + "="*70)
    print(" "*8 + "🚀 SISTEMA RAG MULTIMODAL - PRODUCTOS TECNOLÓGICOS")
    print(" "*10 + "MongoDB Atlas + Groq LLM + Embeddings Vectoriales")
    print(" "*15 + "Búsqueda por Texto 📝 + Imágenes 🖼️ + Chat IA 🤖")
    print("="*70 + "\n")


def print_menu():
    """Imprime el menú principal."""
    print("\n" + "-"*70)
    print("MENÚ PRINCIPAL")
    print("-"*70)
    print("  [1] Crear colecciones con validación de esquema")
    print("  [2] Crear índices")
    print("  [3] Cargar datos completos")
    print("  [4] Verificar datos cargados")
    print("  [5] Ejecutar setup completo")
    print("  [6] Verificar conexión a MongoDB")
    print("")
    print("  🔍 BÚSQUEDA VECTORIAL:")
    print("  [7] 🔍 Búsqueda vectorial de productos")
    print("  [8] 📝 Búsqueda de reseñas")
    print("  [9] 🖼️ Búsqueda por imagen")
    print("  [10] 🔄 Búsqueda híbrida (texto + imagen)")
    print("")
    print("  🤖 SISTEMA RAG:")
    print("  [11] 🤖 Consulta RAG con Groq")
    print("  [12] 💬 Chat interactivo RAG")
    print("  [13] 📊 Análisis de reseñas con IA")
    print("")
    print("  [0] Salir")
    print("-"*70)


# ==================== OPCIONES DE SETUP ====================

def option_1_create_collections():
    """Opción 1: Crear colecciones."""
    print("\n🏗️ CREAR COLECCIONES CON VALIDACIÓN")
    print("\nEsto creará las colecciones con esquemas de validación JSON:")
    print("  • categorias")
    print("  • productos (con marcas embebidas)")
    print("  • usuarios (con reseñas embebidas)")
    print("  • imagenesProducto")
    
    confirm = input("\n¿Continuar? (s/n): ").strip().lower()
    if confirm in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            create_all_collections()
            print("\n✅ Colecciones creadas exitosamente")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_2_create_indexes():
    """Opción 2: Crear índices."""
    print("\n📇 CREAR ÍNDICES OPTIMIZADOS")
    print("\nEsto creará índices para:")
    print("  • Búsquedas por ID y códigos")
    print("  • Índices compuestos")
    print("  • Índices de texto completo")
    print("  • Índices vectoriales (si Atlas Search está disponible)")
    
    confirm = input("\n¿Continuar? (s/n): ").strip().lower()
    if confirm in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            create_all_indexes()
            print("\n✅ Índices creados exitosamente")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_3_load_data():
    """Opción 3: Cargar datos."""
    print("\n📦 CARGAR DATOS COMPLETOS")
    print("\nEsto cargará:")
    print("  • Categorías y marcas")
    print("  • 100+ productos tecnológicos con embeddings")
    print("  • 50 usuarios con 300+ reseñas")
    print("  • Metadatos de imágenes con embeddings CLIP")
    print("\n⚠️  ADVERTENCIA: Puede tomar 10-15 minutos")
    
    confirm = input("\n¿Continuar? (s/n): ").strip().lower()
    if confirm in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            load_all_data()
            print("\n✅ Datos cargados exitosamente")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_4_verify_data():
    """Opción 4: Verificar datos."""
    print("\n🔍 VERIFICAR DATOS CARGADOS")
    try:
        verify_all_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_5_full_setup():
    """Opción 5: Setup completo."""
    print("\n🚀 SETUP COMPLETO DEL SISTEMA")
    print("\nEste proceso ejecutará:")
    print("  1. Crear colecciones con validación")
    print("  2. Crear índices")
    print("  3. Cargar todos los datos con embeddings")
    
    print("\n⚠️  ADVERTENCIA: Este proceso puede tomar 10-15 minutos")
    print("    y eliminará todos los datos existentes en las colecciones")
    
    confirm = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    
    if confirm in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            print("\n" + "="*70)
            print("INICIANDO SETUP COMPLETO")
            print("="*70)
            
            # Paso 1: Crear colecciones
            print("\n🔹 PASO 1/3: Creando colecciones...")
            create_all_collections()
            print("✓ Colecciones creadas")
            
            # Paso 2: Crear índices
            print("\n🔹 PASO 2/3: Creando índices...")
            create_all_indexes()
            print("✓ Índices creados")
            
            # Paso 3: Cargar datos
            print("\n🔹 PASO 3/3: Cargando datos...")
            load_all_data()
            print("✓ Datos cargados")
            
            print("\n" + "="*70)
            print("✅ SETUP COMPLETO FINALIZADO")
            print("✅ El sistema está listo para usar")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ Error en setup completo: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_6_verify_connection():
    """Opción 6: Verificar conexión."""
    print("\n🔌 VERIFICAR CONEXIÓN A MONGODB")
    try:
        if verify_connection():
            print("✅ Conexión exitosa a MongoDB Atlas")
        else:
            print("❌ Error de conexión")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


# ==================== OPCIONES DE BÚSQUEDA ====================

def option_7_vector_search():
    """Opción 7: Búsqueda vectorial."""
    print("\n🔍 BÚSQUEDA VECTORIAL DE PRODUCTOS")
    query = input("\nIngresa tu consulta: ").strip()
    
    if not query:
        print("❌ Consulta vacía")
        input("\nPresiona Enter para continuar...")
        return
    
    # Opciones adicionales
    print("\nOpciones de filtrado (opcional):")
    limit = input("Número de resultados (predeterminado: 10): ").strip()
    limit = int(limit) if limit.isdigit() else 10
    
    category = input("Filtrar por categoría (opcional): ").strip() or None
    min_price = input("Precio mínimo (opcional): ").strip()
    max_price = input("Precio máximo (opcional): ").strip()
    
    price_range = None
    if min_price or max_price:
        min_p = float(min_price) if min_price else None
        max_p = float(max_price) if max_price else None
        price_range = (min_p, max_p)
    
    try:
        resultados = search_productos(
            query, 
            limit=limit,
            category_filter=category,
            price_range=price_range
        )
        
        if resultados:
            print(f"\n✅ {len(resultados)} resultados encontrados:\n")
            for i, prod in enumerate(resultados, 1):
                print(f"{i}. {prod['nombre']}")
                print(f"   Marca: {prod['marca']['nombre']}")
                print(f"   Precio: ${prod['precioUsd']:.2f}")
                print(f"   Similitud: {prod['search_score']:.3f}")
                print(f"   Descripción: {prod['descripcion'][:100]}...")
                print()
        else:
            print("❌ No se encontraron resultados")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_8_search_reviews():
    """Opción 8: Búsqueda de reseñas."""
    print("\n📝 BÚSQUEDA DE RESEÑAS")
    query = input("\nIngresa tu consulta: ").strip()
    
    if not query:
        print("❌ Consulta vacía")
        input("\nPresiona Enter para continuar...")
        return
    
    limit = input("Número de reseñas (predeterminado: 5): ").strip()
    limit = int(limit) if limit.isdigit() else 5
    
    verified = input("¿Solo compradores verificados? (s/n): ").strip().lower()
    verified_only = verified in ['s', 'si', 'sí', 'y', 'yes']
    
    try:
        resenas = search_resenas(query, limit=limit, verified_only=verified_only)
        
        if resenas:
            print(f"\n✅ {len(resenas)} reseñas encontradas:\n")
            for i, r in enumerate(resenas, 1):
                usuario = r['nombreUsuario']
                verificado = "✓" if r['compradorVerificado'] else ""
                score = r['search_score']
                resena = r['resena']
                
                print(f"{i}. Usuario: {usuario} {verificado} (Score: {score:.3f})")
                print(f"   Calificación: {resena['calificacion']}/5")
                print(f"   Título: {resena['titulo']}")
                print(f"   Contenido: {resena['contenido'][:150]}...")
                print()
        else:
            print("❌ No se encontraron reseñas")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_9_search_by_image():
    """Opción 9: Búsqueda por imagen."""
    print("\n🖼️ BÚSQUEDA POR IMAGEN")
    print("\nFormatos soportados: JPG, PNG, JPEG")
    
    image_path = input("\nRuta de la imagen: ").strip()
    if not image_path:
        print("❌ Ruta vacía")
        input("\nPresiona Enter para continuar...")
        return
    
    # Verificar si la ruta es absoluta o relativa
    if not os.path.isabs(image_path):
        # Si es relativa, buscar en el directorio de imágenes del proyecto
        images_dir = os.path.join(os.path.dirname(__file__), "data", "images")
        image_path = os.path.join(images_dir, image_path)
    
    include_reviews = input("¿Incluir reseñas relacionadas? (s/n): ").strip().lower()
    include_reviews = include_reviews in ['s', 'si', 'sí', 'y', 'yes']
    
    try:
        resultado = search_by_image(
            image_path=image_path,
            search_type="productos",
            limit=5,
            include_reviews=include_reviews
        )
        
        if "error" in resultado:
            print(f"❌ Error: {resultado['error']}")
        else:
            productos = resultado.get("productos_similares", [])
            if productos:
                print(f"\n✅ {len(productos)} productos similares encontrados:\n")
                for i, prod in enumerate(productos, 1):
                    img_info = prod["imagen_similar"]
                    print(f"{i}. {prod['nombre']}")
                    print(f"   Marca: {prod['marca']['nombre']}")
                    print(f"   Precio: ${prod['precioUsd']:.2f}")
                    print(f"   Similitud visual: {img_info['similarity_score']:.3f}")
                    print(f"   Imagen: {img_info['rutaImagen']}")
                    print()
                
                # Mostrar reseñas si se incluyeron
                if include_reviews and "resenas_relacionadas" in resultado:
                    resenas = resultado["resenas_relacionadas"]
                    if resenas:
                        print(f"📝 Reseñas relacionadas ({len(resenas)}):")
                        for i, r in enumerate(resenas, 1):
                            resena = r['resena']
                            print(f"{i}. {r['nombreUsuario']}: {resena['titulo']}")
                            print(f"   {resena['contenido'][:100]}...")
            else:
                print("❌ No se encontraron productos similares")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_10_hybrid_search():
    """Opción 10: Búsqueda híbrida."""
    print("\n🔄 BÚSQUEDA HÍBRIDA (TEXTO + IMAGEN)")
    
    text_query = input("\nConsulta de texto (opcional): ").strip() or None
    image_path = input("Ruta de imagen (opcional): ").strip() or None
    
    if not text_query and not image_path:
        print("❌ Debes proporcionar al menos una consulta de texto o una imagen")
        input("\nPresiona Enter para continuar...")
        return
    
    # Procesar ruta de imagen si es relativa
    if image_path and not os.path.isabs(image_path):
        images_dir = os.path.join(os.path.dirname(__file__), "data", "images")
        image_path = os.path.join(images_dir, image_path)
    
    try:
        resultado = hybrid_search(
            text_query=text_query,
            image_path=image_path,
            limit=8
        )
        
        print(f"\n🔍 Resultados de búsqueda híbrida:")
        
        # Mostrar resultados combinados si hay ambos tipos de búsqueda
        if text_query and image_path:
            productos_combinados = resultado.get("productos_combinados", [])
            if productos_combinados:
                print(f"\n✅ {len(productos_combinados)} productos combinados:")
                for i, prod in enumerate(productos_combinados, 1):
                    relevancia = prod.get("relevancia", "combinada")
                    emoji = "🎯" if relevancia == "alta" else "📝" if relevancia == "texto" else "🖼️"
                    print(f"{i}. {emoji} {prod['nombre']} - ${prod['precioUsd']:.2f}")
                    if "search_score" in prod:
                        print(f"   Similitud texto: {prod['search_score']:.3f}")
            else:
                print("❌ No se encontraron productos combinados")
        else:
            # Mostrar resultados individuales
            if text_query:
                productos_texto = resultado.get("productos_texto", [])
                if productos_texto:
                    print(f"\n📝 Resultados por texto ({len(productos_texto)}):")
                    for i, prod in enumerate(productos_texto, 1):
                        print(f"{i}. {prod['nombre']} - Score: {prod['search_score']:.3f}")
            
            if image_path:
                productos_imagen = resultado.get("productos_imagen", [])
                if productos_imagen:
                    print(f"\n🖼️ Resultados por imagen ({len(productos_imagen)}):")
                    for i, prod in enumerate(productos_imagen, 1):
                        score = prod["imagen_similar"]["similarity_score"]
                        print(f"{i}. {prod['nombre']} - Score visual: {score:.3f}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


# ==================== OPCIONES RAG ====================

def option_11_rag_query():
    """Opción 11: Consulta RAG."""
    print("\n🤖 CONSULTA RAG CON GROQ")
    print("\nEl sistema buscará productos relevantes y generará una respuesta inteligente")
    question = input("\nTu pregunta: ").strip()
    
    if not question:
        print("❌ Pregunta vacía")
        input("\nPresiona Enter para continuar...")
        return
    
    num_results = input("Número de productos a consultar (predeterminado: 5): ").strip()
    num_results = int(num_results) if num_results.isdigit() else 5
    
    print("\n⏳ Procesando...")
    try:
        result = rag_query_productos(question, num_results=num_results)
        
        print("\n" + "="*70)
        print("RESPUESTA DEL ASISTENTE IA")
        print("="*70)
        print(f"\n{result['respuesta']}\n")
        print("-"*70)
        print(f"📚 Fuentes consultadas ({result['num_fuentes']} productos):")
        for i, fuente in enumerate(result['fuentes'], 1):
            print(f"  {i}. {fuente}")
        print("="*70)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_12_chat_interactive():
    """Opción 12: Chat interactivo."""
    print("\n💬 INICIANDO CHAT INTERACTIVO RAG")
    try:
        chat_interactive()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


def option_13_analyze_reviews():
    """Opción 13: Análisis de reseñas."""
    print("\n📊 ANÁLISIS DE RESEÑAS CON IA")
    question = input("\n¿Qué aspecto quieres analizar en las reseñas?: ").strip()
    
    if not question:
        print("❌ Consulta vacía")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n⏳ Analizando reseñas...")
    try:
        result = rag_query_resenas(question, num_results=8)
        
        print("\n" + "="*70)
        print("ANÁLISIS DE RESEÑAS")
        print("="*70)
        print(f"\n{result['respuesta']}\n")
        print("-"*70)
        print(f"📝 Reseñas analizadas: {result['num_resenas_analizadas']}")
        print("="*70)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPresiona Enter para continuar...")


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal de la aplicación."""
    while True:
        try:
            clear_screen()
            print_header()
            print_menu()
            
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == '1':
                option_1_create_collections()
            elif opcion == '2':
                option_2_create_indexes()
            elif opcion == '3':
                option_3_load_data()
            elif opcion == '4':
                option_4_verify_data()
            elif opcion == '5':
                option_5_full_setup()
            elif opcion == '6':
                option_6_verify_connection()
            elif opcion == '7':
                option_7_vector_search()
            elif opcion == '8':
                option_8_search_reviews()
            elif opcion == '9':
                option_9_search_by_image()
            elif opcion == '10':
                option_10_hybrid_search()
            elif opcion == '11':
                option_11_rag_query()
            elif opcion == '12':
                option_12_chat_interactive()
            elif opcion == '13':
                option_13_analyze_reviews()
            elif opcion == '0':
                print("\n👋 ¡Hasta luego!")
                print("="*70 + "\n")
                sys.exit(0)
            else:
                print("\n❌ Opción inválida")
                input("\nPresiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    print("🚀 Iniciando Sistema RAG Multimodal...")
    main()