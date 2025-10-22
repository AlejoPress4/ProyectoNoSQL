"""
Script 5: Verificar conexión y estado de la base de datos
- Test de conectividad
- Verificar colecciones
- Verificar índices
- Insertar y consultar documento de prueba
"""

import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from config.db_config import get_db_config, COLLECTIONS
from datetime import datetime
import numpy as np


def test_basic_connection():
    """Test 1: Conectividad básica"""
    print("\n" + "=" * 60)
    print("TEST 1: Conectividad Básica")
    print("=" * 60)
    
    config = get_db_config()
    
    try:
        db = config.connect()
        print(" Conexión establecida correctamente")
        return db, config
    except Exception as e:
        print(f" Fallo en la conexión: {e}")
        return None, None


def test_collections_exist(db):
    """Test 2: Verificar existencia de colecciones"""
    print("\n" + "=" * 60)
    print("TEST 2: Verificación de Colecciones")
    print("=" * 60)
    
    expected_collections = [
        COLLECTIONS['ARTICLES'],
        COLLECTIONS['IMAGES'],
        COLLECTIONS['QUERY_HISTORY']
    ]
    
    existing_collections = db.list_collection_names()
    
    all_exist = True
    for col in expected_collections:
        if col in existing_collections:
            count = db[col].estimated_document_count()
            print(f" '{col}' existe ({count} documentos)")
        else:
            print(f" '{col}' NO existe")
            all_exist = False
    
    return all_exist


def test_indexes(db):
    """Test 3: Verificar índices"""
    print("\n" + "=" * 60)
    print("TEST 3: Verificación de Índices")
    print("=" * 60)
    
    for collection_name in [COLLECTIONS['ARTICLES'], COLLECTIONS['IMAGES'], COLLECTIONS['QUERY_HISTORY']]:
        collection = db[collection_name]
        indexes = list(collection.list_indexes())
        
        print(f"\n {collection_name}:")
        print(f"   Total de índices: {len(indexes)}")
        
        for idx in indexes:
            name = idx.get('name', 'N/A')
            print(f"   ✓ {name}")


def test_insert_sample_document(db):
    """Test 4: Insertar documento de prueba"""
    print("\n" + "=" * 60)
    print("TEST 4: Inserción de Documento de Prueba")
    print("=" * 60)
    
    collection = db[COLLECTIONS['ARTICLES']]
    
    # Generar embedding fake (384 dimensiones)
    fake_embedding = np.random.rand(384).tolist()
    
    sample_doc = {
        "titulo": "Documento de Prueba - Conexión Verificada",
        "contenido": "Este es un documento de prueba para verificar que la conexión a MongoDB funciona correctamente. " * 5,
        "resumen": "Documento de prueba para validar la conexión y schema validation",
        "texto_embedding": fake_embedding,
        "metadata": {
            "fecha_publicacion": datetime(2024, 10, 18),
            "idioma": "es",
            "categoria": "Backend",
            "dificultad": "basico",
            "tiempo_lectura_min": 5,
            "fuente": "https://test.com/prueba"
        },
        "autor": {
            "nombre": "Sistema de Pruebas",
            "perfil": "https://github.com/test"
        },
        "tags": ["test", "prueba", "conexion"],
        "imagenes": [],
        "estadisticas": {
            "vistas": 0,
            "valoracion": 5.0
        },
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now()
    }
    
    try:
        result = collection.insert_one(sample_doc)
        print(f" Documento insertado con ID: {result.inserted_id}")
        
        # Consultar el documento insertado
        retrieved_doc = collection.find_one({"_id": result.inserted_id})
        print(f" Documento consultado exitosamente")
        print(f"   Título: {retrieved_doc['titulo']}")
        print(f"   Categoría: {retrieved_doc['metadata']['categoria']}")
        
        # Eliminar documento de prueba
        collection.delete_one({"_id": result.inserted_id})
        print(f" Documento de prueba eliminado")
        
        return True
        
    except Exception as e:
        print(f" Error al insertar documento: {e}")
        return False


def test_schema_validation(db):
    """Test 5: Verificar schema validation"""
    print("\n" + "=" * 60)
    print("TEST 5: Verificación de Schema Validation")
    print("=" * 60)
    
    collection = db[COLLECTIONS['ARTICLES']]
    
    # Intentar insertar documento inválido (sin campos requeridos)
    invalid_doc = {
        "titulo": "Test",  # Muy corto (min 5 caracteres)
        "contenido": "Muy corto"  # Muy corto (min 100 caracteres)
    }
    
    try:
        collection.insert_one(invalid_doc)
        print(" Schema validation NO está funcionando (documento inválido fue insertado)")
        collection.delete_one({"titulo": "Test"})
        return False
    except Exception as e:
        print(" Schema validation está funcionando correctamente")
        print(f"   Error esperado: {str(e)[:100]}...")
        return True


def test_text_search(db):
    """Test 6: Buscar usando índice de texto (si hay documentos)"""
    print("\n" + "=" * 60)
    print("TEST 6: Búsqueda de Texto")
    print("=" * 60)
    
    collection = db[COLLECTIONS['ARTICLES']]
    count = collection.estimated_document_count()
    
    if count == 0:
        print("  No hay documentos en la colección aún")
        print("   Este test se ejecutará cuando haya datos cargados")
        return True
    
    try:
        # Buscar documentos con la palabra "python"
        results = collection.find(
            {"$text": {"$search": "python"}},
            {"titulo": 1, "score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(5)
        
        result_list = list(results)
        print(f" Búsqueda de texto ejecutada: {len(result_list)} resultados")
        
        for i, doc in enumerate(result_list, 1):
            print(f"   {i}. {doc['titulo']} (score: {doc.get('score', 0):.2f})")
        
        return True
    except Exception as e:
        print(f" Error en búsqueda de texto: {e}")
        return False


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 80)
    print(" " * 20 + " SUITE DE TESTS DE CONEXIÓN")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Conectividad
    db, config = test_basic_connection()
    results['Conectividad'] = db is not None
    
    if db is None:
        print("\n No se puede continuar sin conexión a la base de datos")
        return
    
    try:
        # Test 2: Colecciones
        results['Colecciones'] = test_collections_exist(db)
        
        # Test 3: Índices
        test_indexes(db)
        results['Índices'] = True
        
        # Test 4: Inserción
        results['Inserción'] = test_insert_sample_document(db)
        
        # Test 5: Validación
        results['Schema Validation'] = test_schema_validation(db)
        
        # Test 6: Búsqueda de texto
        results['Búsqueda de Texto'] = test_text_search(db)
        
        # Resumen final
        print("\n" + "=" * 80)
        print(" " * 30 + " RESUMEN DE TESTS")
        print("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for v in results.values() if v)
        
        for test_name, passed in results.items():
            status = " PASS" if passed else " FAIL"
            print(f"   {status} - {test_name}")
        
        print("\n" + "-" * 80)
        print(f"   Total: {passed_tests}/{total_tests} tests pasados")
        
        if passed_tests == total_tests:
            print("\n    ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        else:
            print(f"\n     {total_tests - passed_tests} test(s) fallaron")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\n Error durante los tests: {e}")
    finally:
        if config:
            config.close()


if __name__ == "__main__":
    run_all_tests()
