"""
Aplicación principal del Sistema RAG de Tecnología
Integra FastAPI para la API REST y las funcionalidades RAG
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from sentence_transformers import SentenceTransformer
from config.db_config import get_db_config, COLLECTIONS
import uvicorn

# Inicializar FastAPI
app = FastAPI(
    title="Sistema RAG de Tecnología",
    description="API REST para el Sistema RAG de artículos técnicos y búsqueda semántica",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class Article(BaseModel):
    titulo: str
    contenido: str
    resumen: Optional[str] = None
    metadata: Dict
    tags: List[str] = []

class Query(BaseModel):
    query_text: str
    query_type: str = "semantic"
    filtros: Optional[Dict] = None

# Rutas de la API
@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "mensaje": "Bienvenido al Sistema RAG de Tecnología",
        "documentacion": "/docs",
        "endpoints": [
            "GET /articulos",
            "GET /articulos/{id}",
            "GET /imagenes",
            "POST /buscar"
        ]
    }

@app.get("/articulos")
async def get_articles(
    skip: int = 0,
    limit: int = 10,
    categoria: Optional[str] = None,
    idioma: Optional[str] = None
):
    """Obtener lista de artículos con filtros opcionales"""
    try:
        db = get_db_config()
        collection = db.get_collection(COLLECTIONS['ARTICLES'])
        
        # Construir filtros
        filtros = {}
        if categoria:
            filtros["metadata.categoria"] = categoria
        if idioma:
            filtros["metadata.idioma"] = idioma
            
        # Ejecutar consulta
        articulos = list(collection.find(
            filtros,
            {"_id": 1, "titulo": 1, "resumen": 1, "metadata": 1}
        ).skip(skip).limit(limit))
        
        # Convertir ObjectId a str
        for art in articulos:
            art["_id"] = str(art["_id"])
            
        return articulos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articulos/{articulo_id}")
async def get_article(articulo_id: str):
    """Obtener un artículo por su ID"""
    try:
        from bson.objectid import ObjectId
        
        db = get_db_config()
        collection = db.get_collection(COLLECTIONS['ARTICLES'])
        
        articulo = collection.find_one({"_id": ObjectId(articulo_id)})
        if not articulo:
            raise HTTPException(status_code=404, detail="Artículo no encontrado")
            
        articulo["_id"] = str(articulo["_id"])
        return articulo
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/imagenes")
async def get_images(
    skip: int = 0,
    limit: int = 10,
    tipo: Optional[str] = None
):
    """Obtener lista de imágenes con filtros opcionales"""
    try:
        db = get_db_config()
        collection = db.get_collection(COLLECTIONS['IMAGES'])
        
        # Construir filtros
        filtros = {}
        if tipo:
            filtros["metadata.tipo"] = tipo
            
        # Ejecutar consulta
        imagenes = list(collection.find(
            filtros,
            {"_id": 1, "nombre": 1, "descripcion": 1, "url": 1, "metadata": 1}
        ).skip(skip).limit(limit))
        
        # Convertir ObjectId a str
        for img in imagenes:
            img["_id"] = str(img["_id"])
            
        return imagenes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/buscar")
async def search(query: Query):
    """Realizar búsqueda semántica/híbrida en artículos"""
    try:
        # Obtener colecciones
        db = get_db_config()
        articles_col = db.get_collection(COLLECTIONS['ARTICLES'])
        queries_col = db.get_collection(COLLECTIONS['QUERY_HISTORY'])
        
        # Modelo de embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query.query_text).tolist()
        
        # Pipeline de agregación
        pipeline = [
            {
                "$search": {
                    "index": "articulos_vector",
                    "knnBeta": {
                        "vector": query_embedding,
                        "path": "texto_embedding",
                        "k": 5
                    }
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "titulo": 1,
                    "resumen": 1,
                    "metadata": 1,
                    "score": {"$meta": "searchScore"}
                }
            }
        ]
        
        # Aplicar filtros adicionales si existen
        if query.filtros:
            pipeline.insert(1, {"$match": query.filtros})
        
        # Ejecutar búsqueda
        resultados = list(articles_col.aggregate(pipeline))
        
        # Convertir ObjectId a str
        for doc in resultados:
            doc["_id"] = str(doc["_id"])
        
        # Registrar consulta en historial
        queries_col.insert_one({
            "query_text": query.query_text,
            "query_type": query.query_type,
            "query_embedding": query_embedding,
            "filtros_aplicados": query.filtros,
            "resultados": {
                "count": len(resultados),
                "top_docs": [doc["_id"] for doc in resultados]
            }
        })
        
        return resultados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Configurar host y puerto
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    # Iniciar servidor
    uvicorn.run("app:app", host=host, port=port, reload=True)