"""
Script 4: Cargar imágenes técnicas con embeddings a MongoDB
- Genera datos de imágenes técnicas de ejemplo
- Calcula embeddings simulados (512 dimensiones)
- Inserta en la colección 'images'
- Vincula con artículos existentes
"""

import sys
sys.path.append('..')

from config.db_config import get_db_config, COLLECTIONS
from datetime import datetime
import random
import numpy as np
from tqdm import tqdm

# Tipos de imágenes técnicas
TIPOS_IMAGENES = {
    "diagrama": [
        "Arquitectura de microservicios",
        "Diagrama de flujo de autenticación OAuth",
        "Modelo de red neuronal CNN",
        "Pipeline CI/CD completo",
        "Arquitectura hexagonal",
        "Diagrama UML de clases",
        "Arquitectura cliente-servidor",
        "Topología de red distribuida",
        "Flujo de datos en Apache Kafka",
        "Diagrama de componentes React"
    ],
    "screenshot": [
        "Interface de MongoDB Compass",
        "Dashboard de Kubernetes",
        "Terminal con comandos Docker",
        "VS Code con extensiones",
        "Panel de control AWS",
        "Github Actions workflow",
        "Grafana dashboard de métricas",
        "Postman API testing",
        "Chrome DevTools performance",
        "Terminal con Git commands"
    ],
    "grafico": [
        "Gráfico de performance benchmarks",
        "Comparativa de frameworks JavaScript",
        "Estadísticas de uso de lenguajes 2024",
        "Métricas de latencia API",
        "Gráfico de crecimiento de Docker",
        "Comparación de clouds (AWS vs Azure vs GCP)",
        "Evolución de React vs Vue",
        "Uso de bases de datos NoSQL",
        "Tendencias de Machine Learning",
        "Adopción de Kubernetes por año"
    ],
    "foto": [
        "Datacenter con servidores",
        "Equipo de desarrollo trabajando",
        "Conferencia de tecnología",
        "Hardware de computación en la nube",
        "Oficina con setup de programación",
        "Servidor rack en datacenter",
        "Cables de red y switches",
        "Monitor con código Python",
        "Teclado mecánico para programadores",
        "Setup de workstation dual monitor"
    ],
    "icono": [
        "Logo de MongoDB",
        "Icono de Docker",
        "Logo de React",
        "Símbolo de Python",
        "Logo de Kubernetes",
        "Icono de Git",
        "Logo de AWS",
        "Símbolo de JavaScript",
        "Logo de TensorFlow",
        "Icono de Node.js"
    ]
}

# URLs de ejemplo (Unsplash, Pixabay, etc.)
URL_BASE_UNSPLASH = "https://images.unsplash.com/photo-"
URL_BASE_PLACEHOLDER = "https://placehold.co/"

# Categorías para tags
CATEGORIAS_TAGS = {
    "diagrama": ["arquitectura", "diseño", "sistemas", "uml", "flujo"],
    "screenshot": ["interface", "ui", "dashboard", "herramientas", "desarrollo"],
    "grafico": ["estadisticas", "metricas", "comparativa", "datos", "visualizacion"],
    "foto": ["tecnologia", "hardware", "oficina", "equipo", "profesional"],
    "icono": ["logo", "marca", "tecnologia", "software", "framework"]
}


def generar_embedding_imagen_simulado():
    """
    Genera un embedding simulado de 512 dimensiones
    
    Nota: En producción, usarías un modelo real como CLIP:
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    """
    # Generar vector aleatorio normalizado (simulando CLIP)
    embedding = np.random.randn(512)
    # Normalizar para que tenga norma 1 (típico de embeddings)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


def generar_url_imagen(nombre, formato="png"):
    """Generar URL simulada para la imagen"""
    # Simular URL de Cloudinary o similar
    nombre_limpio = nombre.lower().replace(" ", "-").replace(",", "")[:50]
    return f"https://res.cloudinary.com/tech-rag/image/upload/v1/{nombre_limpio}.{formato}"


def generar_url_thumbnail(url_original):
    """Generar URL del thumbnail"""
    return url_original.replace("/upload/", "/upload/c_thumb,w_200,h_200/")


def preparar_imagen_para_mongo(nombre, tipo, descripcion, tags_adicionales=[]):
    """Preparar documento de imagen para MongoDB"""
    
    # Generar embedding simulado
    embedding = generar_embedding_imagen_simulado()
    
    # Formatos según tipo
    formatos = {
        "diagrama": ["svg", "png"],
        "screenshot": ["png", "jpg"],
        "grafico": ["png", "svg"],
        "foto": ["jpg", "webp"],
        "icono": ["svg", "png"]
    }
    
    formato = random.choice(formatos[tipo])
    
    # Dimensiones según tipo
    dimensiones_map = {
        "diagrama": [(1200, 800), (1600, 900), (1920, 1080)],
        "screenshot": [(1920, 1080), (1366, 768), (1440, 900)],
        "grafico": [(800, 600), (1024, 768), (1200, 800)],
        "foto": [(1920, 1280), (2048, 1365), (3840, 2160)],
        "icono": [(512, 512), (256, 256), (1024, 1024)]
    }
    
    ancho, alto = random.choice(dimensiones_map[tipo])
    
    # Calcular tamaño aproximado en KB
    tamaño_base = {
        "diagrama": (100, 300),
        "screenshot": (200, 800),
        "grafico": (80, 250),
        "foto": (300, 1500),
        "icono": (10, 50)
    }
    
    tamaño_kb = random.randint(*tamaño_base[tipo])
    
    # Combinar tags
    tags_base = CATEGORIAS_TAGS[tipo].copy()
    tags = list(set(tags_base + tags_adicionales))[:10]
    
    # URL de imagen
    url = generar_url_imagen(nombre, formato)
    
    documento = {
        "nombre": nombre,
        "descripcion": descripcion,
        "url": url,
        "url_thumbnail": generar_url_thumbnail(url),
        "image_embedding": embedding.tolist(),
        "metadata": {
            "formato": formato,
            "tamaño_kb": tamaño_kb,
            "dimensiones": {
                "ancho": ancho,
                "alto": alto
            },
            "tipo": tipo,
            "resolucion": f"{ancho}x{alto}"
        },
        "tags": tags,
        "fecha_creacion": datetime.now(),
        "articulos_relacionados": []  # Se llenará después
    }
    
    return documento


def generar_imagenes_completas():
    """Generar lista completa de imágenes para cargar"""
    imagenes = []
    
    for tipo, nombres in TIPOS_IMAGENES.items():
        for nombre in nombres:
            # Generar descripción
            descripcion = f"Imagen técnica de tipo {tipo} mostrando {nombre.lower()}. "
            
            if tipo == "diagrama":
                descripcion += "Representación visual de arquitectura y flujos de sistema."
            elif tipo == "screenshot":
                descripcion += "Captura de pantalla de herramienta o interface de desarrollo."
            elif tipo == "grafico":
                descripcion += "Gráfico con datos estadísticos y métricas comparativas."
            elif tipo == "foto":
                descripcion += "Fotografía relacionada con tecnología y desarrollo de software."
            elif tipo == "icono":
                descripcion += "Logo o icono representativo de tecnología o framework."
            
            # Tags adicionales según nombre
            tags_adicionales = []
            nombre_lower = nombre.lower()
            
            if "docker" in nombre_lower:
                tags_adicionales = ["docker", "contenedores", "devops"]
            elif "kubernetes" in nombre_lower or "k8s" in nombre_lower:
                tags_adicionales = ["kubernetes", "orquestacion", "cloud"]
            elif "react" in nombre_lower:
                tags_adicionales = ["react", "frontend", "javascript"]
            elif "python" in nombre_lower:
                tags_adicionales = ["python", "programacion", "backend"]
            elif "aws" in nombre_lower or "cloud" in nombre_lower:
                tags_adicionales = ["aws", "cloud", "infraestructura"]
            elif "neural" in nombre_lower or "ml" in nombre_lower:
                tags_adicionales = ["machine-learning", "ia", "deep-learning"]
            elif "api" in nombre_lower:
                tags_adicionales = ["api", "backend", "rest"]
            elif "git" in nombre_lower:
                tags_adicionales = ["git", "versionado", "github"]
            
            imagen = preparar_imagen_para_mongo(nombre, tipo, descripcion, tags_adicionales)
            imagenes.append(imagen)
    
    return imagenes


def vincular_imagenes_con_articulos(db):
    """Vincular imágenes con artículos basándose en tags comunes"""
    
    print("\n🔗 Vinculando imágenes con artículos...")
    
    collection_articles = db[COLLECTIONS['ARTICLES']]
    collection_images = db[COLLECTIONS['IMAGES']]
    
    # Obtener todos los artículos
    articulos = list(collection_articles.find({}, {"_id": 1, "tags": 1, "metadata.categoria": 1}))
    
    # Obtener todas las imágenes
    imagenes = list(collection_images.find({}, {"_id": 1, "tags": 1}))
    
    vinculaciones = 0
    
    for articulo in tqdm(articulos, desc="Vinculando"):
        tags_articulo = set(articulo.get("tags", []))
        categoria = articulo["metadata"]["categoria"].lower().replace(" ", "-")
        tags_articulo.add(categoria)
        
        # Encontrar imágenes con tags comunes
        imagenes_compatibles = []
        
        for imagen in imagenes:
            tags_imagen = set(imagen.get("tags", []))
            # Si hay al menos 1 tag en común
            if tags_articulo & tags_imagen:
                imagenes_compatibles.append(imagen["_id"])
        
        # Seleccionar 1-3 imágenes aleatorias
        if imagenes_compatibles:
            num_imagenes = random.randint(1, min(3, len(imagenes_compatibles)))
            imagenes_seleccionadas = random.sample(imagenes_compatibles, num_imagenes)
            
            # Actualizar artículo con referencias a imágenes
            collection_articles.update_one(
                {"_id": articulo["_id"]},
                {"$set": {"imagenes": imagenes_seleccionadas}}
            )
            
            # Actualizar imágenes con referencia al artículo
            for img_id in imagenes_seleccionadas:
                collection_images.update_one(
                    {"_id": img_id},
                    {"$addToSet": {"articulos_relacionados": articulo["_id"]}}
                )
            
            vinculaciones += num_imagenes
    
    print(f"✅ {vinculaciones} vinculaciones creadas")


def cargar_imagenes():
    """Función principal para cargar imágenes a MongoDB"""
    
    print("=" * 80)
    print(" " * 20 + "🖼️  CARGA DE IMÁGENES TÉCNICAS")
    print("=" * 80)
    
    # Conectar a MongoDB
    config = get_db_config()
    db = config.connect()
    collection = db[COLLECTIONS['IMAGES']]
    
    try:
        # Verificar si ya hay imágenes
        count_existente = collection.count_documents({})
        if count_existente > 0:
            print(f"\n⚠️  Ya existen {count_existente} imágenes en la base de datos.")
            respuesta = input("¿Deseas eliminarlas y cargar nuevas? (s/n): ")
            if respuesta.lower() == 's':
                collection.delete_many({})
                print("✅ Imágenes anteriores eliminadas")
            else:
                print("❌ Carga cancelada")
                return
        
        # Generar todas las imágenes
        print("\n🎨 Generando imágenes técnicas...")
        imagenes = generar_imagenes_completas()
        
        print(f"📝 Preparadas {len(imagenes)} imágenes para carga")
        print("   (Embeddings de 512 dimensiones)")
        
        # Insertar todas las imágenes
        print("\n💾 Insertando imágenes en MongoDB...")
        resultado = collection.insert_many(imagenes)
        
        print(f"\n✅ {len(resultado.inserted_ids)} imágenes insertadas exitosamente")
        
        # Vincular con artículos si existen
        count_articulos = db[COLLECTIONS['ARTICLES']].count_documents({})
        if count_articulos > 0:
            vincular_imagenes_con_articulos(db)
        else:
            print("\n⚠️  No hay artículos en la BD. Ejecuta 03_load_articles.py primero para vincular.")
        
        # Mostrar estadísticas
        print("\n" + "=" * 80)
        print(" " * 25 + "📊 ESTADÍSTICAS")
        print("=" * 80)
        
        # Contar por tipo
        pipeline_tipos = [
            {"$group": {"_id": "$metadata.tipo", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        tipos_stats = list(collection.aggregate(pipeline_tipos))
        print("\n🎨 Imágenes por tipo:")
        for stat in tipos_stats:
            print(f"   - {stat['_id'].capitalize()}: {stat['count']} imágenes")
        
        # Contar por formato
        pipeline_formatos = [
            {"$group": {"_id": "$metadata.formato", "count": {"$sum": 1}}}
        ]
        
        formatos_stats = list(collection.aggregate(pipeline_formatos))
        print("\n📁 Imágenes por formato:")
        for stat in formatos_stats:
            print(f"   - {stat['_id'].upper()}: {stat['count']} imágenes")
        
        # Tamaño promedio
        pipeline_tamaño = [
            {"$group": {"_id": None, "promedio_kb": {"$avg": "$metadata.tamaño_kb"}}}
        ]
        
        tamaño_stats = list(collection.aggregate(pipeline_tamaño))
        if tamaño_stats:
            print(f"\n💾 Tamaño promedio: {tamaño_stats[0]['promedio_kb']:.0f} KB")
        
        print("\n" + "=" * 80)
        print("🎉 ¡CARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 80)
        
        # Mostrar algunos ejemplos
        print("\n🖼️  Ejemplos de imágenes cargadas:")
        ejemplos = collection.find().limit(5)
        for i, doc in enumerate(ejemplos, 1):
            print(f"\n   {i}. {doc['nombre']}")
            print(f"      Tipo: {doc['metadata']['tipo']}")
            print(f"      Formato: {doc['metadata']['formato']}")
            print(f"      Resolución: {doc['metadata']['resolucion']}")
            print(f"      Embedding: {len(doc['image_embedding'])} dimensiones")
            print(f"      Artículos relacionados: {len(doc.get('articulos_relacionados', []))}")
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()
    finally:
        config.close()


if __name__ == "__main__":
    cargar_imagenes()
