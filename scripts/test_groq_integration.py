"""
Script de prueba para validar integración Groq LLM y nuevas funcionalidades.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def test_rag_with_llm():
    """Prueba el endpoint RAG con generación LLM."""
    print_section("TEST 1: RAG Multimodal con Groq LLM")
    
    url = f"{BASE_URL}/rag"
    payload = {
        "query": "laptops gaming con buena refrigeración",
        "max_products": 5,
        "include_reviews": True,
        "include_images": True
    }
    
    print(f"📤 Enviando query: {payload['query']}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Respuesta recibida exitosamente")
            print(f"📊 Total productos: {data['metadata']['total_productos']}")
            print(f"🔍 Search modes: {data['metadata']['search_modes']}")
            
            print(f"\n🤖 Respuesta LLM:")
            print("-" * 70)
            print(data['rag_response'][:500] + "..." if len(data['rag_response']) > 500 else data['rag_response'])
            print("-" * 70)
            
            print(f"\n📦 Top 3 productos:")
            for i, p in enumerate(data['productos'][:3], 1):
                print(f"{i}. {p['nombre']}")
                print(f"   💰 ${p['precio_usd']} | 🎯 Hybrid: {p['hybrid_score']}%")
                print(f"   📝 Text: {p['text_similarity']}% | 🖼️ Image: {p['image_similarity']}%")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en request: {e}")


def test_update_caption():
    """Prueba la actualización de caption."""
    print_section("TEST 2: Actualizar Caption")
    
    url = f"{BASE_URL}/api/utils/update-caption"
    payload = {
        "title": "Dell XPS 15",
        "new_caption": "Laptop premium renovada con mejor sistema de refrigeración"
    }
    
    print(f"📤 Actualizando caption para: {payload['title']}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        elif response.status_code == 404:
            print(f"⚠️ Producto no encontrado (normal si no existe en BD)")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en request: {e}")


def test_show_results():
    """Prueba la función de visualización de resultados."""
    print_section("TEST 3: Show Results (Debugging)")
    
    url = f"{BASE_URL}/api/utils/show-results"
    payload = {
        "query": "smartphones con buena cámara",
        "limit": 3
    }
    
    print(f"📤 Query: {payload['query']}")
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Resultados encontrados: {data['total']}")
            print(f"\n📋 Detalles:")
            
            for i, r in enumerate(data['results'], 1):
                print(f"\n{i}. {r['title']}")
                print(f"   🔎 Score: {r['score']}")
                print(f"   📁 Categoría: {r['category']}")
                print(f"   🏷️ Tags: {r['tags']}")
                print(f"   📷 Imagen: {'✓' if r['has_image'] else '✗'}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en request: {e}")


def test_stats():
    """Prueba el endpoint de estadísticas."""
    print_section("TEST 4: Estadísticas del Sistema")
    
    url = f"{BASE_URL}/api/stats"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Estadísticas obtenidas:")
            for collection, count in data['estadisticas'].items():
                print(f"   📊 {collection}: {count} documentos")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en request: {e}")


def test_health():
    """Verifica que el servidor esté activo."""
    print_section("TEST 0: Health Check")
    
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Servidor activo en {BASE_URL}")
        else:
            print(f"⚠️ Servidor responde con código {response.status_code}")
            
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        print(f"💡 Asegúrate de que web_app.py esté corriendo")
        return False
    
    return True


if __name__ == "__main__":
    print("\n" + "🚀 INICIANDO TESTS DE INTEGRACIÓN GROQ LLM" + "\n")
    
    # Health check primero
    if not test_health():
        print("\n❌ Tests abortados - servidor no disponible")
        exit(1)
    
    # Tests principales
    test_rag_with_llm()
    test_show_results()
    test_update_caption()
    test_stats()
    
    print("\n" + "="*70)
    print("✅ TESTS COMPLETADOS")
    print("="*70)
    print("\n💡 Nota: Algunos tests pueden fallar si:")
    print("   - No hay datos en MongoDB")
    print("   - Los índices vectoriales no están creados")
    print("   - La API key de Groq no es válida")
    print("   - No hay conexión a internet (para Groq API)")
