#!/usr/bin/env python3
"""
Test rápido del Pipeline RAG
Verifica que todos los componentes funcionen correctamente.
"""

import requests
import json
import time
import sys

def test_rag_endpoint():
    """Prueba el endpoint RAG completo"""
    print("🧪 Probando endpoint RAG...")
    
    url = "http://localhost:5000/rag"
    test_data = {
        "query": "¿Cuál es el mejor smartphone con buena cámara?",
        "max_products": 3,
        "max_reviews": 3,
        "include_reviews": True
    }
    
    try:
        print("📤 Enviando consulta:", test_data["query"])
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta recibida exitosamente")
            print(f"📊 Status: {data.get('status')}")
            print(f"🤖 Modelo usado: {data.get('metadata', {}).get('model_used', 'N/A')}")
            print(f"📱 Productos encontrados: {data.get('context', {}).get('total_productos', 0)}")
            print(f"💬 Reseñas encontradas: {data.get('context', {}).get('total_resenas', 0)}")
            
            # Mostrar respuesta generada
            rag_response = data.get('rag_response', '')
            if rag_response:
                print(f"\n🧠 Respuesta RAG generada:")
                print("-" * 50)
                print(rag_response[:300] + "..." if len(rag_response) > 300 else rag_response)
                print("-" * 50)
            
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en http://localhost:5000?")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El servidor tardó demasiado en responder")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_search_endpoints():
    """Prueba los endpoints de búsqueda básica"""
    print("\n🔍 Probando endpoints de búsqueda...")
    
    endpoints = {
        "/api/products/search": {"query": "smartphone"},
        "/api/reviews/search": {"query": "excelente"}
    }
    
    for endpoint, params in endpoints.items():
        try:
            url = f"http://localhost:5000{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', []))
                print(f"✅ {endpoint}: {count} resultados")
            else:
                print(f"❌ {endpoint}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

def test_interface_accessibility():
    """Verifica que la interfaz esté disponible"""
    print("\n🌐 Probando interfaz web...")
    
    interfaces = [
        "/rag-interface",
        "/ragtech",
        "/api/stats"
    ]
    
    for interface in interfaces:
        try:
            url = f"http://localhost:5000{interface}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {interface}: Disponible")
            else:
                print(f"❌ {interface}: Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {interface}: {str(e)}")

def main():
    print("🚀 PRUEBA RÁPIDA DEL PIPELINE RAG")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor web detectado en puerto 5000")
    except:
        print("❌ Servidor no disponible en puerto 5000")
        print("💡 Ejecuta: python web_app.py")
        sys.exit(1)
    
    # Ejecutar pruebas
    rag_success = test_rag_endpoint()
    test_search_endpoints()
    test_interface_accessibility()
    
    print("\n" + "=" * 50)
    if rag_success:
        print("🎉 ¡Pipeline RAG funcionando correctamente!")
        print("✅ El proyecto cumple con los requerimientos básicos")
    else:
        print("⚠️  Hay problemas con el Pipeline RAG")
        print("🔧 Revisa la configuración y los logs del servidor")
    
    print("\n📋 Para validación completa, ejecuta:")
    print("   python validate_project.py")

if __name__ == "__main__":
    main()