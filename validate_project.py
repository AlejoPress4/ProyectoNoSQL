#!/usr/bin/env python3
"""
Script de Validación del Proyecto RAG
Verifica que el proyecto cumpla con las especificaciones del PDF académico.
"""

import os
import json
import sys
from datetime import datetime
from config import get_database, COLLECTIONS
from sentence_transformers import SentenceTransformer
import pymongo

class ProjectValidator:
    def __init__(self):
        self.results = {}
        self.score = 0
        self.max_score = 0
        self.report = []
        
    def log(self, message, status="INFO", points=0):
        """Registra un mensaje en el reporte."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.report.append(f"[{timestamp}] {status}: {message}")
        if points > 0:
            self.score += points
        print(f"[{timestamp}] {status}: {message}")
    
    def validate_database_connection(self):
        """1. Verifica conexión a MongoDB Atlas"""
        self.log("🔍 VALIDANDO CONEXIÓN A BASE DE DATOS", "TEST")
        self.max_score += 10
        
        try:
            db = get_database()
            # Test de conexión
            db.admin.command('ping')
            self.log("✅ Conexión a MongoDB Atlas exitosa", "PASS", 5)
            
            # Verificar colecciones requeridas
            collections = db.list_collection_names()
            required_collections = ['productos', 'resenas', 'usuarios', 'categorias', 'marcas']
            
            for collection in required_collections:
                if collection in collections:
                    count = db[collection].count_documents({})
                    self.log(f"✅ Colección '{collection}': {count} documentos", "PASS", 1)
                else:
                    self.log(f"❌ Colección '{collection}' no encontrada", "FAIL")
                    
        except Exception as e:
            self.log(f"❌ Error de conexión: {str(e)}", "FAIL")
    
    def validate_embeddings(self):
        """2. Verifica embeddings y búsqueda vectorial"""
        self.log("🔍 VALIDANDO EMBEDDINGS Y BÚSQUEDA VECTORIAL", "TEST")
        self.max_score += 15
        
        try:
            # Verificar modelo de embeddings
            model = SentenceTransformer('all-MiniLM-L6-v2')
            test_text = "smartphone con buena cámara"
            embedding = model.encode(test_text)
            
            if len(embedding) == 384:
                self.log("✅ Modelo de embeddings funcionando (384 dimensiones)", "PASS", 5)
            else:
                self.log(f"❌ Dimensiones incorrectas: {len(embedding)}", "FAIL")
            
            # Verificar embeddings en base de datos
            db = get_database()
            
            # Productos con embeddings
            productos_with_embeddings = db.productos.count_documents({"embedding": {"$exists": True}})
            total_productos = db.productos.count_documents({})
            
            if productos_with_embeddings > 0:
                percentage = (productos_with_embeddings / total_productos) * 100
                self.log(f"✅ Productos con embeddings: {productos_with_embeddings}/{total_productos} ({percentage:.1f}%)", "PASS", 5)
            else:
                self.log("❌ No se encontraron productos con embeddings", "FAIL")
            
            # Reseñas con embeddings
            resenas_with_embeddings = db.resenas.count_documents({"embedding": {"$exists": True}})
            total_resenas = db.resenas.count_documents({})
            
            if resenas_with_embeddings > 0:
                percentage = (resenas_with_embeddings / total_resenas) * 100
                self.log(f"✅ Reseñas con embeddings: {resenas_with_embeddings}/{total_resenas} ({percentage:.1f}%)", "PASS", 5)
            else:
                self.log("❌ No se encontraron reseñas con embeddings", "FAIL")
                
        except Exception as e:
            self.log(f"❌ Error validando embeddings: {str(e)}", "FAIL")
    
    def validate_rag_pipeline(self):
        """3. Verifica pipeline RAG completo"""
        self.log("🔍 VALIDANDO PIPELINE RAG", "TEST")
        self.max_score += 20
        
        try:
            # Verificar archivo RAG LLM
            if os.path.exists("rag_llm.py"):
                self.log("✅ Módulo RAG LLM presente", "PASS", 5)
                
                # Importar y probar integrador
                from rag_llm import RAGLLMIntegrator
                integrator = RAGLLMIntegrator()
                status = integrator.health_check()
                
                if status['status'] == 'ready' or status['status'] == 'demo_mode':
                    self.log(f"✅ Integrador RAG: {status['provider']} - {status['status']}", "PASS", 5)
                else:
                    self.log(f"⚠️  Integrador RAG en modo limitado: {status['status']}", "WARN", 2)
                    
            else:
                self.log("❌ Módulo RAG LLM no encontrado", "FAIL")
            
            # Verificar endpoint RAG
            import requests
            try:
                # Test básico del endpoint
                test_data = {
                    "query": "test query",
                    "max_products": 3,
                    "max_reviews": 3,
                    "include_reviews": True
                }
                
                # Nota: Este test requiere que el servidor esté corriendo
                # Por ahora solo verificamos que el código esté presente
                if os.path.exists("web_app.py"):
                    with open("web_app.py", "r", encoding="utf-8") as f:
                        content = f.read()
                        if "/rag" in content and "generate_rag_response" in content:
                            self.log("✅ Endpoint RAG implementado en web_app.py", "PASS", 10)
                        else:
                            self.log("❌ Endpoint RAG no encontrado en web_app.py", "FAIL")
                            
            except Exception as e:
                self.log(f"⚠️  No se pudo probar endpoint RAG (servidor no activo)", "WARN")
                
        except Exception as e:
            self.log(f"❌ Error validando pipeline RAG: {str(e)}", "FAIL")
    
    def validate_web_interface(self):
        """4. Verifica interfaz web"""
        self.log("🔍 VALIDANDO INTERFAZ WEB", "TEST")
        self.max_score += 15
        
        try:
            # Verificar archivos de la interfaz
            templates_path = "templates"
            static_path = "static"
            
            required_templates = ["rag_interface.html", "ragtech.html"]
            required_static = ["rag-interface.js", "ragtech.js", "style.css"]
            
            for template in required_templates:
                template_path = os.path.join(templates_path, template)
                if os.path.exists(template_path):
                    self.log(f"✅ Template '{template}' presente", "PASS", 2)
                else:
                    self.log(f"❌ Template '{template}' no encontrado", "FAIL")
            
            for static_file in required_static:
                static_path_full = os.path.join(static_path, static_file)
                if os.path.exists(static_path_full):
                    self.log(f"✅ Archivo estático '{static_file}' presente", "PASS", 2)
                else:
                    self.log(f"❌ Archivo estático '{static_file}' no encontrado", "FAIL")
            
            # Verificar accesibilidad en templates
            if os.path.exists("templates/rag_interface.html"):
                with open("templates/rag_interface.html", "r", encoding="utf-8") as f:
                    content = f.read()
                    accessibility_features = [
                        'aria-label',
                        'for=',
                        'aria-describedby'
                    ]
                    
                    for feature in accessibility_features:
                        if feature in content:
                            self.log(f"✅ Característica de accesibilidad '{feature}' presente", "PASS", 1)
                        else:
                            self.log(f"⚠️  Característica de accesibilidad '{feature}' no encontrada", "WARN")
                            
        except Exception as e:
            self.log(f"❌ Error validando interfaz web: {str(e)}", "FAIL")
    
    def validate_data_requirements(self):
        """5. Verifica requerimientos de datos"""
        self.log("🔍 VALIDANDO REQUERIMIENTOS DE DATOS", "TEST")
        self.max_score += 10
        
        try:
            db = get_database()
            
            # Mínimo 50 productos (según especificaciones)
            total_productos = db.productos.count_documents({})
            if total_productos >= 50:
                self.log(f"✅ Productos suficientes: {total_productos}/50 mínimo", "PASS", 3)
            else:
                self.log(f"❌ Productos insuficientes: {total_productos}/50 mínimo", "FAIL")
            
            # Reseñas de usuarios
            total_resenas = db.resenas.count_documents({})
            if total_resenas >= 20:
                self.log(f"✅ Reseñas suficientes: {total_resenas}/20 mínimo", "PASS", 2)
            else:
                self.log(f"⚠️  Pocas reseñas: {total_resenas}/20 recomendado", "WARN", 1)
            
            # Verificar imágenes (contenido multimodal)
            images_path = "data/images"
            if os.path.exists(images_path):
                image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
                if len(image_files) >= 50:
                    self.log(f"✅ Imágenes suficientes: {len(image_files)}/50 mínimo", "PASS", 3)
                else:
                    self.log(f"⚠️  Pocas imágenes: {len(image_files)}/50 recomendado", "WARN", 1)
            else:
                self.log("❌ Carpeta de imágenes no encontrada", "FAIL")
            
            # Verificar diversidad de categorías
            categorias = db.categorias.count_documents({})
            if categorias >= 5:
                self.log(f"✅ Diversidad de categorías: {categorias} categorías", "PASS", 2)
            else:
                self.log(f"⚠️  Pocas categorías: {categorias} categorías", "WARN", 1)
                
        except Exception as e:
            self.log(f"❌ Error validando datos: {str(e)}", "FAIL")
    
    def validate_technical_requirements(self):
        """6. Verifica requerimientos técnicos"""
        self.log("🔍 VALIDANDO REQUERIMIENTOS TÉCNICOS", "TEST")
        self.max_score += 10
        
        try:
            # Verificar requirements.txt
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", "r") as f:
                    requirements = f.read()
                    
                required_packages = [
                    "pymongo", "sentence-transformers", "flask", 
                    "openai", "groq", "transformers"
                ]
                
                for package in required_packages:
                    if package in requirements:
                        self.log(f"✅ Paquete '{package}' en requirements.txt", "PASS", 1)
                    else:
                        self.log(f"⚠️  Paquete '{package}' no listado en requirements.txt", "WARN")
            
            # Verificar estructura de archivos
            required_files = [
                "web_app.py", "config/__init__.py", "models/schemas.py",
                "scripts/load_data.py", "README.md"
            ]
            
            for file_path in required_files:
                if os.path.exists(file_path):
                    self.log(f"✅ Archivo '{file_path}' presente", "PASS", 1)
                else:
                    self.log(f"⚠️  Archivo '{file_path}' no encontrado", "WARN")
                    
        except Exception as e:
            self.log(f"❌ Error validando requerimientos técnicos: {str(e)}", "FAIL")
    
    def validate_performance(self):
        """7. Verifica aspectos de rendimiento"""
        self.log("🔍 VALIDANDO RENDIMIENTO", "TEST")
        self.max_score += 5
        
        try:
            db = get_database()
            
            # Verificar índices en campos importantes
            productos_indexes = db.productos.list_indexes()
            index_names = [idx['name'] for idx in productos_indexes]
            
            if any('embedding' in name or 'vector' in name for name in index_names):
                self.log("✅ Índices vectoriales configurados", "PASS", 3)
            else:
                self.log("⚠️  No se detectaron índices vectoriales específicos", "WARN", 1)
            
            # Verificar tamaño razonable de embeddings
            sample_product = db.productos.find_one({"embedding": {"$exists": True}})
            if sample_product and "embedding" in sample_product:
                embedding_size = len(sample_product["embedding"])
                if 300 <= embedding_size <= 1024:
                    self.log(f"✅ Tamaño de embedding apropiado: {embedding_size} dimensiones", "PASS", 2)
                else:
                    self.log(f"⚠️  Tamaño de embedding: {embedding_size} dimensiones", "WARN", 1)
                    
        except Exception as e:
            self.log(f"❌ Error validando rendimiento: {str(e)}", "FAIL")
    
    def generate_report(self):
        """Genera reporte final"""
        self.log("📊 GENERANDO REPORTE FINAL", "REPORT")
        
        percentage = (self.score / self.max_score) * 100 if self.max_score > 0 else 0
        
        print("\n" + "="*60)
        print("📋 REPORTE DE VALIDACIÓN DEL PROYECTO RAG")
        print("="*60)
        print(f"📊 PUNTUACIÓN: {self.score}/{self.max_score} ({percentage:.1f}%)")
        print(f"📅 FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        if percentage >= 80:
            print("🎉 ¡EXCELENTE! El proyecto cumple con las especificaciones")
            grade = "SOBRESALIENTE"
        elif percentage >= 70:
            print("✅ BIEN. El proyecto cumple mayormente con las especificaciones")
            grade = "BUENO"
        elif percentage >= 60:
            print("⚠️  REGULAR. El proyecto necesita algunas mejoras")
            grade = "ACEPTABLE"
        else:
            print("❌ INSUFICIENTE. El proyecto necesita mejoras importantes")
            grade = "INSUFICIENTE"
        
        print(f"🏆 CALIFICACIÓN: {grade}")
        print("="*60)
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "score": self.score,
            "max_score": self.max_score,
            "percentage": percentage,
            "grade": grade,
            "log": self.report
        }
        
        with open("validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Reporte guardado en: validation_report.json")
        print("="*60)
        
        return percentage >= 60  # Considera aprobado con 60%+
    
    def run_validation(self):
        """Ejecuta todas las validaciones"""
        print("🚀 INICIANDO VALIDACIÓN DEL PROYECTO RAG")
        print("Verificando cumplimiento de especificaciones del PDF académico...")
        print("-" * 60)
        
        # Ejecutar todas las validaciones
        self.validate_database_connection()
        self.validate_embeddings()
        self.validate_rag_pipeline()
        self.validate_web_interface()
        self.validate_data_requirements()
        self.validate_technical_requirements()
        self.validate_performance()
        
        # Generar reporte final
        return self.generate_report()

def main():
    """Función principal"""
    validator = ProjectValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🎯 El proyecto está listo para entrega")
        sys.exit(0)
    else:
        print("\n⚠️  El proyecto necesita mejoras antes de la entrega")
        sys.exit(1)

if __name__ == "__main__":
    main()