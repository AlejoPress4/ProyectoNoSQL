"""
Script 3: Cargar artículos tecnológicos con embeddings a MongoDB
- Genera artículos de ejemplo sobre tecnología
- Calcula embeddings usando sentence-transformers
- Inserta en la colección 'articles'
"""

import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)       

from config.db_config import get_db_config, COLLECTIONS
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
import random
from tqdm import tqdm

# Datos de ejemplo para generar artículos
CATEGORIAS = [
    "Machine Learning",
    "Backend",
    "Frontend",
    "DevOps",
    "Ciberseguridad",
    "Mobile",
    "Data Science",
    "Cloud",
    "IoT",
    "Blockchain"
]

DIFICULTADES = ["basico", "intermedio", "avanzado"]
IDIOMAS = ["es", "en"]

# Artículos de ejemplo 
ARTICULOS_EJEMPLO = [
    {
        "titulo": "Introducción a Redes Neuronales Convolucionales",
        "contenido": """Las Redes Neuronales Convolucionales (CNN) son un tipo de red neuronal profunda especialmente diseñada para procesar datos con estructura de grilla, como imágenes. A diferencia de las redes neuronales completamente conectadas, las CNN aprovechan la estructura espacial de los datos mediante capas de convolución que aplican filtros locales. 
        
        Una CNN típica consiste en varias capas: capas convolucionales que extraen características, capas de pooling que reducen la dimensionalidad, y capas densas finales para la clasificación. Las capas convolucionales utilizan filtros (kernels) que se deslizan sobre la imagen, detectando patrones como bordes, texturas y formas más complejas en capas más profundas.
        
        El proceso de entrenamiento utiliza backpropagation para ajustar los pesos de los filtros, aprendiendo automáticamente las características más relevantes para la tarea específica. Las CNN han revolucionado la visión por computadora, logrando resultados superiores en tareas como reconocimiento de imágenes, detección de objetos y segmentación semántica.
        
        Frameworks como TensorFlow, PyTorch y Keras facilitan la implementación de CNN, ofreciendo arquitecturas pre-entrenadas como VGG, ResNet, Inception y MobileNet. El transfer learning permite adaptar estas redes a nuevas tareas con menos datos de entrenamiento, siendo especialmente útil en aplicaciones prácticas donde los datos son limitados.""",
        "categoria": "Machine Learning",
        "dificultad": "intermedio",
        "idioma": "es",
        "tags": ["deep-learning", "computer-vision", "python", "tensorflow", "cnn"],
        "autor": "Dr. María García",
        "tiempo_lectura": 12
    },
    {
        "titulo": "GraphQL vs REST: Comparativa completa 2024",
        "contenido": """GraphQL es un lenguaje de consulta para APIs desarrollado por Facebook en 2015. A diferencia de REST, que expone múltiples endpoints fijos, GraphQL permite a los clientes solicitar exactamente los datos que necesitan mediante una única consulta, reduciendo el over-fetching y under-fetching de datos.
        
        En REST, cada recurso tiene su propio endpoint y los clientes deben hacer múltiples llamadas para obtener datos relacionados. GraphQL unifica esto en un solo endpoint donde el cliente especifica su esquema de consulta. El servidor entonces resuelve la consulta y devuelve exactamente lo solicitado en formato JSON.
        
        Las ventajas de GraphQL incluyen: tipado fuerte con esquemas autodocumentados, introspección para explorar la API, subscripciones para datos en tiempo real, y mayor flexibilidad para los clientes. Sin embargo, REST sigue siendo más simple para APIs pequeñas, tiene mejor caché HTTP nativo, y es más familiar para la mayoría de desarrolladores.
        
        La elección entre GraphQL y REST depende del caso de uso: GraphQL brilla en aplicaciones complejas con múltiples clientes (web, mobile, IoT) que necesitan diferentes vistas de datos, mientras que REST es suficiente para APIs simples con pocos endpoints y clientes homogéneos.""",
        "categoria": "Backend",
        "dificultad": "intermedio",
        "idioma": "es",
        "tags": ["graphql", "rest", "api", "backend", "nodejs"],
        "autor": "Carlos Rodríguez",
        "tiempo_lectura": 15
    },
    {
        "titulo": "Microservicios: Patrones de diseño y mejores prácticas",
        "contenido": """La arquitectura de microservicios descompone aplicaciones monolíticas en servicios pequeños e independientes que se comunican mediante APIs. Cada microservicio se enfoca en una capacidad de negocio específica, puede desplegarse independientemente, y permite escalar componentes individuales según demanda.
        
        Patrones clave incluyen: API Gateway como punto de entrada único, Service Discovery para localizar servicios dinámicamente, Circuit Breaker para manejar fallos de servicios dependientes, y Event Sourcing para mantener estado mediante eventos. La comunicación puede ser síncrona (REST, gRPC) o asíncrona (message queues).
        
        Los beneficios son significativos: equipos autónomos que pueden desarrollar y desplegar independientemente, tecnologías heterogéneas por servicio, escalabilidad granular, y mayor resiliencia ante fallos. Sin embargo, introducen complejidad en testing, debugging distribuido, transacciones entre servicios, y gestión de datos consistentes.
        
        Docker y Kubernetes son tecnologías fundamentales para orquestar microservicios. Service meshes como Istio añaden observabilidad, seguridad y gestión de tráfico. El éxito requiere inversión en DevOps, monitoring robusto con herramientas como Prometheus y Grafana, y cultura organizacional que soporte equipos descentralizados.""",
        "categoria": "Backend",
        "dificultad": "avanzado",
        "idioma": "es",
        "tags": ["microservicios", "arquitectura", "docker", "kubernetes", "devops"],
        "autor": "Ana López",
        "tiempo_lectura": 18
    },
    {
        "titulo": "React Hooks: Guía completa para principiantes",
        "contenido": """React Hooks, introducidos en React 16.8, permiten usar estado y otras características de React en componentes funcionales, eliminando la necesidad de componentes de clase. Los hooks más comunes son useState para gestionar estado local y useEffect para efectos secundarios como llamadas a APIs o suscripciones.
        
        useState devuelve un par [valor, función setter] que permite añadir estado a componentes funcionales. useEffect ejecuta código después del renderizado, útil para fetch de datos, manipulación del DOM, o limpieza de recursos. La dependencia array controla cuándo se ejecuta el efecto, optimizando performance.
        
        Otros hooks útiles incluyen: useContext para compartir datos sin prop drilling, useReducer para estado complejo con lógica similar a Redux, useMemo para memorizar cálculos costosos, y useCallback para memorizar funciones y evitar re-renders innecesarios. Custom hooks permiten extraer lógica reutilizable.
        
        Las reglas de los hooks son importantes: solo llamarlos en el nivel superior (no en bucles o condicionales) y solo desde componentes React o custom hooks. Esta restricción permite a React preservar el estado correctamente entre renders. Los hooks simplifican el código, facilitan la reutilización de lógica, y mejoran la legibilidad comparado con patrones anteriores como HOCs y render props.""",
        "categoria": "Frontend",
        "dificultad": "basico",
        "idioma": "es",
        "tags": ["react", "javascript", "frontend", "hooks", "web"],
        "autor": "Pedro Martínez",
        "tiempo_lectura": 10
    },
    {
        "titulo": "Docker y Kubernetes: De contenedores a orquestación",
        "contenido": """Docker revolucionó el desarrollo al empaquetar aplicaciones y sus dependencias en contenedores ligeros y portables. A diferencia de máquinas virtuales, los contenedores comparten el kernel del sistema operativo, siendo más eficientes en recursos. Un Dockerfile define la imagen del contenedor, docker-compose orquesta múltiples contenedores en desarrollo.
        
        Kubernetes (K8s) lleva Docker al siguiente nivel, orquestando contenedores en producción a escala. Automatiza despliegue, escalado, y gestión de aplicaciones containerizadas. Los conceptos clave son: Pods (grupo de contenedores), Services (abstracción de red), Deployments (declaración del estado deseado), y ConfigMaps/Secrets para configuración.
        
        La arquitectura de Kubernetes incluye el control plane (API server, scheduler, controller manager) y nodos workers donde corren los pods. kubectl es la herramienta CLI para interactuar con clusters. Helm facilita la gestión de aplicaciones complejas mediante charts reutilizables.
        
        Los beneficios incluyen: alta disponibilidad mediante réplicas, auto-scaling horizontal, rolling updates sin downtime, auto-healing de pods fallidos, y portabilidad entre clouds. Sin embargo, K8s tiene curva de aprendizaje pronunciada y overhead para aplicaciones simples. Alternativas como Docker Swarm o managed services como EKS, GKE, y AKS simplifican la adopción.""",
        "categoria": "DevOps",
        "dificultad": "intermedio",
        "idioma": "es",
        "tags": ["docker", "kubernetes", "devops", "contenedores", "cloud"],
        "autor": "Laura Sánchez",
        "tiempo_lectura": 16
    },
    {
        "titulo": "Ciberseguridad: Protegiendo APIs con OAuth 2.0 y JWT",
        "contenido": """La seguridad en APIs es crítica cuando se exponen servicios web. OAuth 2.0 es un framework de autorización que permite a aplicaciones obtener acceso limitado a cuentas de usuario mediante delegación. Define roles (resource owner, client, authorization server, resource server) y flujos de autorización según el tipo de aplicación.
        
        El flujo Authorization Code es el más seguro para aplicaciones web, donde el cliente obtiene un código de autorización que intercambia por tokens. El flujo Client Credentials es para comunicación máquina-a-máquina. El flujo Implicit (deprecated) se usaba en SPAs, ahora reemplazado por PKCE (Proof Key for Code Exchange) que añade seguridad extra.
        
        JWT (JSON Web Tokens) son tokens autocontenidos que codifican claims en formato JSON firmado. Consisten en header (algoritmo), payload (claims), y signature (verificación). Los claims pueden ser registered (iss, exp, sub), public, o private. JWTs eliminan la necesidad de almacenar sesiones en servidor, siendo stateless y escalables.
        
        Mejores prácticas incluyen: usar HTTPS siempre, tokens de corta duración con refresh tokens, validar firmas JWT, implementar rate limiting, sanitizar inputs, y usar bibliotecas probadas. Vulnerabilidades comunes son: XSS (Cross-Site Scripting) que roba tokens, CSRF (Cross-Site Request Forgery), y ataques de replay. Headers como CORS y CSP añaden capas de seguridad.""",
        "categoria": "Ciberseguridad",
        "dificultad": "avanzado",
        "idioma": "es",
        "tags": ["seguridad", "oauth", "jwt", "api", "autenticacion"],
        "autor": "Miguel Fernández",
        "tiempo_lectura": 14
    },
    {
        "titulo": "Machine Learning en producción: MLOps y mejores prácticas",
        "contenido": """Llevar modelos de Machine Learning a producción va más allá de entrenar un modelo preciso. MLOps (ML Operations) aplica principios DevOps al ciclo de vida de ML: versionado de datos y modelos, pipelines automatizados, monitoreo continuo, y reentrenamiento. Herramientas como MLflow, Kubeflow, y DVC facilitan estas prácticas.
        
        El ciclo MLOps incluye: recolección y versionado de datos, experimentación y tracking de métricas, empaquetado del modelo, despliegue en infraestructura escalable, monitoreo de performance y data drift, y reentrenamiento automático. CI/CD para ML añade tests de validación de datos, tests de modelo, y tests de integración.
        
        Desafíos únicos de ML en producción incluyen data drift (distribución de datos cambia con tiempo), concept drift (relación entre features y target cambia), y degradación de modelo. Monitoring debe capturar métricas de negocio, métricas de modelo (accuracy, latencia), y distribuciones de features. Alertas tempranas permiten reentrenar antes de impacto significativo.
        
        Arquitecturas comunes son: batch predictions para procesar grandes volúmenes offline, real-time predictions con APIs REST/gRPC para baja latencia, y streaming predictions con Kafka/Kinesis. Feature stores como Feast centralizan features reutilizables. Servicios managed como SageMaker, Vertex AI, y Azure ML aceleran adopción al abstraer infraestructura.""",
        "categoria": "Data Science",
        "dificultad": "avanzado",
        "idioma": "es",
        "tags": ["mlops", "machine-learning", "produccion", "devops", "ml"],
        "autor": "Sofía Torres",
        "tiempo_lectura": 17
    },
    {
        "titulo": "Flutter: Desarrollo multiplataforma con un solo código",
        "contenido": """Flutter es el framework de Google para crear aplicaciones nativas compiladas para móvil, web y desktop desde una única base de código en Dart. A diferencia de React Native que usa bridges, Flutter renderiza directamente usando su motor gráfico Skia, logrando performance cercana a nativo con 60 FPS consistentes.
        
        La arquitectura de Flutter se basa en widgets: todo es un widget, desde botones hasta layouts completos. Los widgets son inmutables y se reconstruyen eficientemente mediante un árbol virtual. StatelessWidget para componentes sin estado, StatefulWidget para componentes que cambian. El estado se gestiona con setState(), Provider, Bloc, o Riverpod.
        
        Hot reload es la killer feature de Flutter, permitiendo ver cambios instantáneamente sin perder estado de la app. El ecosistema pub.dev ofrece miles de paquetes para funcionalidades comunes. Material Design y Cupertino widgets permiten UIs nativas de Android e iOS respectivamente. Flutter Web y Desktop expanden el alcance más allá de móvil.
        
        Flutter brilla en: apps con UI custom compleja, equipos pequeños que quieren servir múltiples plataformas, MVPs rápidos, y apps con alta performance gráfica. Limitaciones incluyen tamaño de app mayor que nativo, menos plugins que React Native, y Dart menos popular que JavaScript. Empresas como Alibaba, BMW, y Google Ads usan Flutter en producción.""",
        "categoria": "Mobile",
        "dificultad": "intermedio",
        "idioma": "es",
        "tags": ["flutter", "mobile", "dart", "cross-platform", "app"],
        "autor": "Diego Ramírez",
        "tiempo_lectura": 13
    },
    {
        "titulo": "AWS vs Azure vs GCP: Comparativa de servicios cloud 2024",
        "contenido": """Los tres grandes proveedores cloud dominan el mercado: AWS con 32% de cuota, Azure con 23%, y GCP con 10%. Cada uno tiene fortalezas únicas. AWS lidera en cantidad de servicios (200+), madurez, y ecosistema. Azure brilla en integración con Microsoft (Active Directory, Office 365). GCP destaca en Big Data, ML, y networking.
        
        En compute: AWS EC2 vs Azure Virtual Machines vs GCP Compute Engine son equivalentes. Para serverless: Lambda vs Functions vs Cloud Functions. Kubernetes managed: EKS vs AKS vs GKE (GKE fue el primero y más maduro). Storage: S3 vs Blob Storage vs Cloud Storage son comparables en features y pricing.
        
        En bases de datos, AWS tiene mayor variedad: RDS, DynamoDB, Aurora, Redshift, Neptune. Azure ofrece SQL Database, Cosmos DB, Synapse. GCP tiene Cloud SQL, Firestore, BigQuery (líder en data warehousing). Para ML: SageMaker (AWS), Azure ML, y Vertex AI (GCP con ventaja en TensorFlow integration).
        
        Pricing es complejo en los tres. AWS generalmente más caro pero con mayor flexibilidad. Azure competitivo para clientes Microsoft. GCP ofrece descuentos automáticos por uso sostenido. Todos tienen free tiers y calculadoras de costos. Multicloud es tendencia, usando Terraform para IaC portable. La elección depende de: expertise existente, integraciones necesarias, y cargas de trabajo específicas.""",
        "categoria": "Cloud",
        "dificultad": "intermedio",
        "idioma": "es",
        "tags": ["cloud", "aws", "azure", "gcp", "arquitectura"],
        "autor": "Carmen Ruiz",
        "tiempo_lectura": 15
    },
    {
        "titulo": "Blockchain más allá de las criptomonedas: Casos de uso empresariales",
        "contenido": """Blockchain es una tecnología de registro distribuido (DLT) que permite transacciones seguras sin intermediarios. Aunque asociado a Bitcoin y Ethereum, blockchain tiene aplicaciones empresariales en supply chain, finanzas, salud, y más. La inmutabilidad, transparencia, y descentralización ofrecen ventajas únicas.
        
        En supply chain, blockchain permite trazabilidad completa desde fabricación hasta consumidor final. Walmart y Maersk usan blockchain para rastrear alimentos y containers respectivamente, reduciendo fraudes y mejorando eficiencia. Smart contracts en Ethereum automatizan pagos cuando se cumplen condiciones, eliminando intermediarios y reduciendo tiempos de liquidación.
        
        Hyperledger Fabric es la plataforma enterprise más popular, permitiendo blockchains privadas/permisionadas donde solo participantes autorizados pueden validar transacciones. A diferencia de blockchains públicas como Ethereum, Fabric ofrece privacidad, performance superior (1000+ TPS), y modularidad. IBM, Oracle, y AWS ofrecen servicios managed de blockchain.
        
        Desafíos incluyen: escalabilidad limitada comparada con bases de datos tradicionales, consumo energético en proof-of-work, regulación incierta, e interoperabilidad entre blockchains. Soluciones layer 2 como Lightning Network mejoran escalabilidad. Proof-of-stake reduce energía. A pesar de hype, adopción enterprise es gradual, enfocada en casos donde inmutabilidad y descentralización justifican la complejidad añadida.""",
        "categoria": "Blockchain",
        "dificultad": "avanzado",
        "idioma": "es",
        "tags": ["blockchain", "smart-contracts", "ethereum", "enterprise", "dlt"],
        "autor": "Roberto Vega",
        "tiempo_lectura": 16
    }
]


def generar_articulos_adicionales(num_articulos=20):
    """Generar artículos adicionales con variaciones"""
    articulos_generados = []
    
    titulos_adicionales = [
        "Introducción a TypeScript para desarrolladores JavaScript",
        "Python vs JavaScript: ¿Cuál aprender en 2024?",
        "Testing automatizado: Jest, Pytest y mejores prácticas",
        "CI/CD con GitHub Actions: Automatización completa",
        "Redis: Cache distribuido para aplicaciones de alto tráfico",
        "PostgreSQL vs MongoDB: Eligiendo la base de datos correcta",
        "Next.js 14: Server Components y App Router",
        "Vue 3 Composition API: Guía completa",
        "Terraform: Infrastructure as Code para múltiples clouds",
        "Nginx vs Apache: Comparativa de servidores web",
        "WebSockets: Comunicación en tiempo real",
        "Git avanzado: Rebase, cherry-pick y bisect",
        "Linux para desarrolladores: Comandos esenciales",
        "Arquitectura hexagonal: Clean Architecture en la práctica",
        "TensorFlow vs PyTorch: Frameworks de Deep Learning",
        "Swift UI: Desarrollo iOS moderno",
        "Android Jetpack Compose: UI declarativa",
        "Elasticsearch: Motor de búsqueda distribuido",
        "Apache Kafka: Streaming de datos en tiempo real",
        "Observabilidad: Logs, métricas y traces con OpenTelemetry"
    ]
    
    for i in range(min(num_articulos, len(titulos_adicionales))):
        categoria = random.choice(CATEGORIAS)
        idioma = random.choice(IDIOMAS)
        dificultad = random.choice(DIFICULTADES)
        
        contenido = f"""Este es un artículo sobre {titulos_adicionales[i]}. 
        
        La tecnología moderna requiere mantenerse actualizado constantemente. En este artículo exploramos conceptos fundamentales y avanzados de esta tecnología, proporcionando ejemplos prácticos y mejores prácticas de la industria.
        
        Cubrimos desde los conceptos básicos hasta implementaciones avanzadas, con ejemplos de código comentados y explicaciones detalladas. También discutimos casos de uso reales, arquitecturas comunes, y consideraciones de performance y escalabilidad.
        
        Al final del artículo, tendrás una comprensión sólida de la tecnología y podrás aplicarla en tus propios proyectos. Incluimos referencias a documentación oficial, recursos de aprendizaje adicionales, y repositorios de código abierto relevantes.""" * 3
        
        articulo = {
            "titulo": titulos_adicionales[i],
            "contenido": contenido,
            "categoria": categoria,
            "dificultad": dificultad,
            "idioma": idioma,
            "tags": [categoria.lower().replace(" ", "-"), "tutorial", "tecnologia"],
            "autor": random.choice(["Juan Pérez", "María López", "Carlos García", "Ana Martínez"]),
            "tiempo_lectura": random.randint(8, 20)
        }
        
        articulos_generados.append(articulo)
    
    return articulos_generados


def preparar_articulo_para_mongo(articulo, embedding_texto, fecha_base):
    """Preparar un artículo con todos los campos necesarios para MongoDB"""
    
    # Generar fecha aleatoria en los últimos 12 meses
    dias_atras = random.randint(0, 365)
    fecha_publicacion = fecha_base - timedelta(days=dias_atras)
    
    documento = {
        "titulo": articulo["titulo"],
        "contenido": articulo["contenido"],
        "resumen": articulo["contenido"][:300] + "...",
        "texto_embedding": embedding_texto.tolist(),
        "metadata": {
            "fecha_publicacion": fecha_publicacion,
            "idioma": articulo["idioma"],
            "categoria": articulo["categoria"],
            "dificultad": articulo["dificultad"],
            "tiempo_lectura_min": articulo["tiempo_lectura"],
            "fuente": "https://tech-blog.com/articles/" + articulo["titulo"].lower().replace(" ", "-")[:50]
        },
        "autor": {
            "nombre": articulo["autor"],
            "perfil": "https://github.com/" + articulo["autor"].lower().replace(" ", "")
        },
        "tags": articulo["tags"],
        "imagenes": [],  # Se agregarán referencias después de cargar imágenes
        "estadisticas": {
            "vistas": random.randint(50, 5000),
            "valoracion": round(random.uniform(3.5, 5.0), 1)
        },
        "fecha_creacion": datetime.now(),
        "fecha_actualizacion": datetime.now()
    }
    
    return documento


def cargar_articulos():
    """Función principal para cargar artículos a MongoDB"""
    
    print("=" * 80)
    print(" " * 20 + "📚 CARGA DE ARTÍCULOS TECNOLÓGICOS")
    print("=" * 80)
    
    # Conectar a MongoDB
    config = get_db_config()
    db = config.connect()
    collection = db[COLLECTIONS['ARTICLES']]
    
    try:
        # Verificar si ya hay artículos
        count_existente = collection.count_documents({})
        if count_existente > 0:
            print(f"\n⚠️  Ya existen {count_existente} artículos en la base de datos.")
            respuesta = input("¿Deseas eliminarlos y cargar nuevos? (s/n): ")
            if respuesta.lower() == 's':
                collection.delete_many({})
                print("✅ Artículos anteriores eliminados")
            else:
                print("❌ Carga cancelada")
                return
        
        # Cargar modelo de embeddings
        print("\n🤖 Cargando modelo de embeddings...")
        print("   Modelo: all-MiniLM-L6-v2 (384 dimensiones)")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modelo cargado")
        
        # Combinar artículos de ejemplo con generados
        todos_articulos = ARTICULOS_EJEMPLO.copy()
        articulos_adicionales = generar_articulos_adicionales(20)
        todos_articulos.extend(articulos_adicionales)
        
        print(f"\n📝 Preparando {len(todos_articulos)} artículos para carga...")
        
        documentos_para_insertar = []
        fecha_base = datetime.now()
        
        # Procesar cada artículo
        for articulo in tqdm(todos_articulos, desc="Generando embeddings"):
            # Generar embedding del título + resumen
            texto_para_embedding = f"{articulo['titulo']}. {articulo['contenido'][:500]}"
            embedding = model.encode(texto_para_embedding)
            
            # Preparar documento
            documento = preparar_articulo_para_mongo(articulo, embedding, fecha_base)
            documentos_para_insertar.append(documento)
        
        # Insertar todos los documentos
        print("\n💾 Insertando artículos en MongoDB...")
        resultado = collection.insert_many(documentos_para_insertar)
        
        print(f"\n✅ {len(resultado.inserted_ids)} artículos insertados exitosamente")
        
        # Mostrar estadísticas
        print("\n" + "=" * 80)
        print(" " * 25 + "📊 ESTADÍSTICAS")
        print("=" * 80)
        
        # Contar por categoría
        pipeline_categorias = [
            {"$group": {"_id": "$metadata.categoria", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        categorias_stats = list(collection.aggregate(pipeline_categorias))
        print("\n📂 Artículos por categoría:")
        for stat in categorias_stats:
            print(f"   - {stat['_id']}: {stat['count']} artículos")
        
        # Contar por idioma
        pipeline_idiomas = [
            {"$group": {"_id": "$metadata.idioma", "count": {"$sum": 1}}}
        ]
        
        idiomas_stats = list(collection.aggregate(pipeline_idiomas))
        print("\n🌍 Artículos por idioma:")
        for stat in idiomas_stats:
            idioma_nombre = "Español" if stat['_id'] == "es" else "Inglés"
            print(f"   - {idioma_nombre}: {stat['count']} artículos")
        
        # Contar por dificultad
        pipeline_dificultad = [
            {"$group": {"_id": "$metadata.dificultad", "count": {"$sum": 1}}}
        ]
        
        dificultad_stats = list(collection.aggregate(pipeline_dificultad))
        print("\n📈 Artículos por dificultad:")
        for stat in dificultad_stats:
            print(f"   - {stat['_id'].capitalize()}: {stat['count']} artículos")
        
        print("\n" + "=" * 80)
        print("🎉 ¡CARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 80)
        
        # Mostrar algunos ejemplos
        print("\n📄 Ejemplos de artículos cargados:")
        ejemplos = collection.find().limit(3)
        for i, doc in enumerate(ejemplos, 1):
            print(f"\n   {i}. {doc['titulo']}")
            print(f"      Categoría: {doc['metadata']['categoria']}")
            print(f"      Dificultad: {doc['metadata']['dificultad']}")
            print(f"      Tags: {', '.join(doc['tags'][:3])}")
            print(f"      Embedding: {len(doc['texto_embedding'])} dimensiones")
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        import traceback
        traceback.print_exc()
    finally:
        config.close()


if __name__ == "__main__":
    cargar_articulos()
