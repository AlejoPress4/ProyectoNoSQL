"""
Ejemplos de uso de las nuevas funcionalidades de RAG con Groq LLM.
Puedes ejecutar este archivo directamente o copiar los ejemplos a tu código.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# ============================================================================
# EJEMPLO 1: Búsqueda RAG completa con LLM
# ============================================================================
print("="*80)
print("EJEMPLO 1: Búsqueda RAG Multimodal + LLM")
print("="*80)

query_1 = {
    "query": "laptop gaming con buena refrigeración y precio competitivo",
    "max_products": 5,
    "include_reviews": True,
    "include_images": True
}

response_1 = requests.post(f"{BASE_URL}/rag", json=query_1, timeout=30)
if response_1.status_code == 200:
    data = response_1.json()
    print(f"\n🤖 Respuesta del LLM:")
    print("-" * 80)
    print(data['rag_response'])
    print("-" * 80)
    print(f"\n📦 Top 3 Productos:")
    for i, p in enumerate(data['productos'][:3], 1):
        print(f"{i}. {p['nombre']} - ${p['precio_usd']}")
        print(f"   🎯 Hybrid Score: {p['hybrid_score']}%")
else:
    print(f"❌ Error: {response_1.text}")

# ============================================================================
# EJEMPLO 2: Búsqueda solo texto (sin imágenes)
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 2: RAG solo texto (más rápido)")
print("="*80)

query_2 = {
    "query": "smartphone con mejor cámara para fotografía nocturna",
    "max_products": 3,
    "include_reviews": True,
    "include_images": False  # Solo búsqueda de texto
}

response_2 = requests.post(f"{BASE_URL}/rag", json=query_2, timeout=20)
if response_2.status_code == 200:
    data = response_2.json()
    print(f"\n🤖 Respuesta del LLM:")
    print(data['rag_response'][:400] + "...")
    print(f"\n📊 Método: {data['metadata']['search_method']}")
else:
    print(f"❌ Error: {response_2.text}")

# ============================================================================
# EJEMPLO 3: Show Results (Debugging)
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 3: Visualización de Resultados (Debugging)")
print("="*80)

query_3 = {
    "query": "auriculares bluetooth con cancelación de ruido",
    "limit": 3
}

response_3 = requests.post(f"{BASE_URL}/api/utils/show-results", json=query_3, timeout=15)
if response_3.status_code == 200:
    data = response_3.json()
    print(f"\n🔍 Query: {data['query']}")
    print(f"📊 Total resultados: {data['total']}")
    
    for i, r in enumerate(data['results'], 1):
        print(f"\n{i}. {r['title']}")
        print(f"   Score: {r['score']}")
        print(f"   Categoría: {r['category']}")
        print(f"   Tiene imagen: {'✓' if r['has_image'] else '✗'}")
else:
    print(f"❌ Error: {response_3.text}")

# ============================================================================
# EJEMPLO 4: Actualizar Caption (Gestión de Metadatos)
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 4: Actualizar Descripción de Producto")
print("="*80)

# Nota: Este ejemplo puede fallar si el producto no existe
query_4 = {
    "title": "Dell XPS 15",
    "new_caption": "Laptop premium con pantalla 4K y sistema de refrigeración mejorado para gaming y trabajo profesional"
}

response_4 = requests.post(f"{BASE_URL}/api/utils/update-caption", json=query_4, timeout=10)
if response_4.status_code == 200:
    data = response_4.json()
    print(f"✅ {data['message']}")
elif response_4.status_code == 404:
    print(f"⚠️ Producto no encontrado en la base de datos")
else:
    print(f"❌ Error: {response_4.text}")

# ============================================================================
# EJEMPLO 5: Consulta especializada (e-commerce)
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 5: Consulta E-commerce Compleja")
print("="*80)

query_5 = {
    "query": "necesito una tablet para diseño gráfico con buen stylus, que no pese mucho y tenga batería de larga duración",
    "max_products": 4,
    "max_reviews": 5,
    "include_reviews": True,
    "include_images": True
}

response_5 = requests.post(f"{BASE_URL}/rag", json=query_5, timeout=30)
if response_5.status_code == 200:
    data = response_5.json()
    
    print(f"\n🎯 Query: {data['query']}")
    print(f"\n🤖 Análisis del LLM:")
    print("-" * 80)
    print(data['rag_response'])
    print("-" * 80)
    
    print(f"\n📊 Metadatos:")
    print(f"   • Productos encontrados: {data['metadata']['total_productos']}")
    print(f"   • Reseñas analizadas: {data['metadata']['total_resenas']}")
    print(f"   • Búsqueda de texto: {data['metadata']['search_modes']['text_search']}")
    print(f"   • Búsqueda de imágenes: {data['metadata']['search_modes']['image_search']}")
    print(f"   • Análisis de reseñas: {data['metadata']['search_modes']['review_search']}")
    
    print(f"\n💰 Rango de precios:")
    precios = [p['precio_usd'] for p in data['productos']]
    print(f"   • Min: ${min(precios):.2f}")
    print(f"   • Max: ${max(precios):.2f}")
    print(f"   • Promedio: ${sum(precios)/len(precios):.2f}")
else:
    print(f"❌ Error: {response_5.text}")

# ============================================================================
# EJEMPLO 6: Estadísticas del sistema
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 6: Estadísticas del Sistema")
print("="*80)

response_6 = requests.get(f"{BASE_URL}/api/stats", timeout=10)
if response_6.status_code == 200:
    data = response_6.json()
    print(f"\n📊 Estado de la base de datos:")
    for collection, count in data['estadisticas'].items():
        print(f"   • {collection}: {count:,} documentos")
else:
    print(f"❌ Error: {response_6.text}")

# ============================================================================
# EJEMPLO 7: Comparación de productos (uso avanzado)
# ============================================================================
print("\n\n" + "="*80)
print("EJEMPLO 7: Comparación de Productos (Avanzado)")
print("="*80)

query_7 = {
    "query": "compara laptops dell vs asus para gaming en el rango de $1000-$1500",
    "max_products": 6,
    "include_reviews": True,
    "include_images": True
}

response_7 = requests.post(f"{BASE_URL}/rag", json=query_7, timeout=30)
if response_7.status_code == 200:
    data = response_7.json()
    
    print(f"\n🤖 Análisis Comparativo del LLM:")
    print(data['rag_response'])
    
    # Agrupar por marca
    marcas = {}
    for p in data['productos']:
        marca = p['marca']
        if marca not in marcas:
            marcas[marca] = []
        marcas[marca].append(p)
    
    print(f"\n📊 Distribución por marca:")
    for marca, productos in marcas.items():
        print(f"   • {marca}: {len(productos)} productos")
        for prod in productos:
            print(f"      - {prod['nombre']} (${prod['precio_usd']})")
else:
    print(f"❌ Error: {response_7.text}")

print("\n" + "="*80)
print("✅ EJEMPLOS COMPLETADOS")
print("="*80)
print("\n💡 Tips:")
print("   • Ajusta 'max_products' para controlar resultados")
print("   • Usa 'include_images=False' para búsquedas más rápidas")
print("   • 'include_reviews=True' enriquece el contexto para el LLM")
print("   • Las respuestas del LLM varían ligeramente por temperature=0.4")
