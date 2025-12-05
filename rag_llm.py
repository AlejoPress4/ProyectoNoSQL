"""
Módulo de integración con LLM para Pipeline RAG completo.
Cumple con los requerimientos del proyecto final.
"""

import os
import openai
from typing import List, Dict, Any
import json

class RAGLLMIntegrator:
    """
    Integrador de LLM para sistema RAG.
    Soporta múltiples proveedores: Groq, HuggingFace, OpenAI.
    """
    
    def __init__(self, provider="groq", model="llama-3.1-8b-instant"):
        self.provider = provider.lower()
        self.model = model
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Configura el cliente según el proveedor seleccionado."""
        if self.provider == "groq":
            # Groq API (recomendado en el documento)
            try:
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY", "gsk_demo_key_for_testing")
                self.client = Groq(api_key=api_key)
                print("✅ Cliente Groq configurado")
            except ImportError:
                print("❌ Groq no disponible, usando OpenAI como fallback")
                self._setup_openai()
        
        elif self.provider == "openai":
            self._setup_openai()
        
        elif self.provider == "huggingface":
            self._setup_huggingface()
        
        else:
            print(f"⚠️  Proveedor {self.provider} no reconocido, usando modo demo")
            self.client = None
    
    def _setup_openai(self):
        """Configurar OpenAI (Free tier)."""
        api_key = os.getenv("OPENAI_API_KEY", "demo_key")
        if api_key != "demo_key":
            openai.api_key = api_key
            self.client = openai
            self.model = "gpt-3.5-turbo"
            print("✅ Cliente OpenAI configurado")
        else:
            print("⚠️  OPENAI_API_KEY no configurada")
            self.client = None
    
    def _setup_huggingface(self):
        """Configurar HuggingFace Inference API."""
        try:
            from huggingface_hub import InferenceClient
            api_key = os.getenv("HF_API_KEY", "demo_key")
            self.client = InferenceClient(token=api_key)
            self.model = "microsoft/DialoGPT-medium"
            print("✅ Cliente HuggingFace configurado")
        except ImportError:
            print("❌ HuggingFace no disponible")
            self.client = None

    def generate_rag_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera respuesta RAG usando contexto recuperado de MongoDB.
        
        Args:
            query: Pregunta del usuario
            context: Diccionario con productos y reseñas relevantes
        
        Returns:
            Dict con respuesta generada, fuentes y metadatos
        """
        
        # Extraer productos y reseñas del contexto
        context_products = context.get('productos', [])
        context_reviews = context.get('resenas', [])
        
        # Preparar contexto
        context_text = self._prepare_context(context_products, context_reviews)
        
        # Crear prompt RAG
        prompt = self._create_rag_prompt(query, context_text)
        
        # Generar respuesta
        if self.client is None:
            # Modo demo sin API
            response_text = self._generate_demo_response(query, context_products, context_reviews)
            tokens_used = 0
            processing_time = 0.5
        else:
            import time
            start_time = time.time()
            
            try:
                if self.provider == "groq":
                    response_text = self._generate_groq_response(prompt)
                    tokens_used = len(prompt.split()) + len(response_text.split())  # Estimación
                elif self.provider == "openai":
                    response_text = self._generate_openai_response(prompt)
                    tokens_used = len(prompt.split()) + len(response_text.split())  # Estimación
                elif self.provider == "huggingface":
                    response_text = self._generate_hf_response(prompt)
                    tokens_used = len(prompt.split()) + len(response_text.split())  # Estimación
                else:
                    response_text = self._generate_demo_response(query, context_products, context_reviews)
                    tokens_used = 0
                
                processing_time = time.time() - start_time
                
            except Exception as e:
                print(f"❌ Error generando respuesta: {e}")
                response_text = self._generate_demo_response(query, context_products, context_reviews)
                tokens_used = 0
                processing_time = time.time() - start_time
        
        return {
            "response": response_text,
            "tokens_used": tokens_used,
            "processing_time": processing_time,
            "status": "success"
        }

    def _prepare_context(self, products: List[Dict], reviews: List[Dict] = None) -> str:
        """Prepara el contexto para el prompt RAG."""
        context_parts = []
        
        # Contexto de productos
        if products:
            context_parts.append("=== PRODUCTOS RELEVANTES ===")
            for i, product in enumerate(products[:5], 1):  # Top 5 productos
                context_parts.append(f"""
{i}. {product.get('nombre', 'Producto sin nombre')}
   - Marca: {product.get('marca', {}).get('nombre', 'N/A')}
   - Categoría: {product.get('categoria', {}).get('nombre', 'N/A')}
   - Precio: ${product.get('precio_usd', 'N/A')}
   - Descripción: {product.get('descripcion', 'Sin descripción')}
   - Calificación: {product.get('calificacion', 'N/A')}/5
   - Disponibilidad: {product.get('disponibilidad', 'N/A')}
   - Similitud: {product.get('similarity', 0):.2%}
                """.strip())
        
        # Contexto de reseñas
        if reviews:
            context_parts.append("\n=== RESEÑAS RELEVANTES ===")
            for i, review in enumerate(reviews[:3], 1):  # Top 3 reseñas
                context_parts.append(f"""
{i}. "{review.get('titulo', 'Sin título')}"
   - Usuario: {review.get('usuario', 'Anónimo')}
   - Calificación: {review.get('calificacion', 'N/A')}/5
   - Contenido: {review.get('contenido', 'Sin contenido')}
   - Compra verificada: {'Sí' if review.get('compra_verificada', False) else 'No'}
   - Similitud: {review.get('similarity', 0):.2%}
                """.strip())
        
        return "\n".join(context_parts)

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Crea el prompt RAG optimizado."""
        return f"""
Eres un asistente experto en productos tecnológicos. Tu trabajo es responder preguntas basándote ÚNICAMENTE en la información proporcionada en el contexto.

CONTEXTO DE LA BASE DE DATOS:
{context}

PREGUNTA DEL USUARIO: {query}

INSTRUCCIONES:
1. Responde basándote SOLO en la información del contexto
2. Si la información es insuficiente, menciona qué datos específicos faltan
3. Incluye referencias específicas a productos, precios y características
4. Menciona las fuentes de información (nombres de productos, reseñas)
5. Si hay múltiples opciones, compáralas objetivamente
6. Usa un tono profesional pero amigable
7. Si no hay información relevante en el contexto, dilo claramente

RESPUESTA:
        """.strip()

    def _generate_groq_response(self, prompt: str) -> str:
        """Genera respuesta usando Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en productos tecnológicos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error con Groq API: {e}")
            raise

    def _generate_openai_response(self, prompt: str) -> str:
        """Genera respuesta usando OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en productos tecnológicos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error con OpenAI API: {e}")
            raise

    def _generate_hf_response(self, prompt: str) -> str:
        """Genera respuesta usando HuggingFace Inference API."""
        try:
            response = self.client.text_generation(
                prompt=prompt,
                max_new_tokens=800,
                temperature=0.7,
                do_sample=True
            )
            return response
        except Exception as e:
            print(f"Error con HuggingFace API: {e}")
            raise

    def _generate_demo_response(self, query: str, products: List[Dict], reviews: List[Dict] = None) -> str:
        """Genera respuesta demo cuando no hay API disponible."""
        
        if not products:
            return f"""
🤖 **Respuesta Demo (Sin API LLM configurada)**

No encontré productos relevantes para tu consulta: "{query}"

Para obtener respuestas generadas por IA, configura una de las siguientes APIs:
- GROQ_API_KEY (recomendado)
- OPENAI_API_KEY 
- HF_API_KEY (HuggingFace)

💡 **Sugerencia**: Intenta con consultas como:
- "¿Qué smartphones tienes disponibles?"
- "Laptops para gaming"
- "Auriculares con cancelación de ruido"
            """.strip()
        
        # Respuesta estructurada basada en productos encontrados
        response_parts = [
            f'🤖 **Análisis de "{query}"** (Modo Demo)\n',
            f"Encontré **{len(products)} productos relevantes** para tu consulta:\n"
        ]
        
        # Top 3 productos
        for i, product in enumerate(products[:3], 1):
            match_percent = int(product.get('similarity', 0) * 100)
            response_parts.append(f"""
**{i}. {product.get('nombre', 'Producto')}** ({match_percent}% relevancia)
- 🏷️ Marca: {product.get('marca', {}).get('nombre', 'N/A')}
- 💰 Precio: ${product.get('precio_usd', 'N/A')}
- ⭐ Calificación: {product.get('calificacion', 'N/A')}/5
- 📦 Disponibilidad: {product.get('disponibilidad', 'N/A')}
            """.strip())
        
        if reviews and len(reviews) > 0:
            response_parts.append(f"\n📝 También encontré **{len(reviews)} reseñas** relacionadas que mencionan aspectos relevantes.\n")
        
        response_parts.append("""
💡 **Para respuestas de IA completas**, configura una API key:
```bash
export GROQ_API_KEY="tu_api_key_aqui"
```
        """)
        
        return "\n".join(response_parts)

    def _extract_sources(self, products: List[Dict], reviews: List[Dict] = None) -> List[Dict]:
        """Extrae información de fuentes para referencias."""
        sources = []
        
        # Fuentes de productos
        for product in products[:5]:
            sources.append({
                "type": "product",
                "id": product.get('id'),
                "name": product.get('nombre'),
                "similarity": product.get('similarity', 0),
                "category": product.get('categoria', {}).get('nombre')
            })
        
        # Fuentes de reseñas
        if reviews:
            for review in reviews[:3]:
                sources.append({
                    "type": "review",
                    "title": review.get('titulo'),
                    "user": review.get('usuario'),
                    "similarity": review.get('similarity', 0),
                    "rating": review.get('calificacion')
                })
        
        return sources

    def health_check(self) -> Dict[str, Any]:
        """Verifica el estado del integrador LLM."""
        return {
            "provider": self.provider,
            "model": self.model,
            "client_available": self.client is not None,
            "api_key_configured": self._check_api_key(),
            "status": "ready" if self.client is not None else "demo_mode"
        }
    
    def _check_api_key(self) -> bool:
        """Verifica si hay API key configurada."""
        if self.provider == "groq":
            return os.getenv("GROQ_API_KEY") is not None
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY") is not None
        elif self.provider == "huggingface":
            return os.getenv("HF_API_KEY") is not None
        return False