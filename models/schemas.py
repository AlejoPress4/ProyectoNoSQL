"""
Definición de esquemas y modelos de datos para el sistema RAG.
"""

from datetime import datetime
from bson import ObjectId


class MarcaSchema:
    """Esquema para la colección de marcas."""
    
    @staticmethod
    def create(nombre, pais, sitio_web="", descripcion=""):
        """
        Crea un documento de marca.
        
        Args:
            nombre (str): Nombre de la marca
            pais (str): País de origen
            sitio_web (str): URL del sitio web oficial
            descripcion (str): Descripción de la marca
            
        Returns:
            dict: Documento de marca
        """
        return {
            "nombre": nombre,
            "pais": pais,
            "sitio_web": sitio_web,
            "descripcion": descripcion,
            "fecha_creacion": datetime.now()
        }


class CategoriaSchema:
    """Esquema para la colección de categorías."""
    
    @staticmethod
    def create(nombre, slug, descripcion="", id_categoria_padre=None):
        """
        Crea un documento de categoría.
        
        Args:
            nombre (str): Nombre de la categoría
            slug (str): Slug para URLs
            descripcion (str): Descripción de la categoría
            id_categoria_padre (ObjectId): ID de categoría padre (opcional)
            
        Returns:
            dict: Documento de categoría
        """
        return {
            "nombre": nombre,
            "slug": slug,
            "descripcion": descripcion,
            "id_categoria_padre": id_categoria_padre,
            "fecha_creacion": datetime.now()
        }


class UsuarioSchema:
    """Esquema para la colección de usuarios."""
    
    @staticmethod
    def create(nombre_usuario, correo, nombre_completo="", comprador_verificado=False):
        """
        Crea un documento de usuario.
        
        Args:
            nombre_usuario (str): Nombre de usuario único
            correo (str): Correo electrónico
            nombre_completo (str): Nombre completo del usuario
            comprador_verificado (bool): Si ha realizado compras verificadas
            
        Returns:
            dict: Documento de usuario
        """
        return {
            "nombre_usuario": nombre_usuario,
            "correo": correo,
            "nombre_completo": nombre_completo,
            "comprador_verificado": comprador_verificado,
            "fecha_creacion": datetime.now(),
            "ultimo_acceso": datetime.now()
        }


class ProductoSchema:
    """Esquema para la colección de productos."""
    
    @staticmethod
    def create(
        codigo_producto,
        nombre,
        descripcion,
        marca_id,
        marca_nombre,
        categoria_id,
        categoria_nombre,
        categoria_slug,
        especificaciones,
        precio_usd,
        fecha_lanzamiento,
        disponibilidad="en_stock",
        descripcion_embedding=None,
        imagen_principal=""
    ):
        """
        Crea un documento de producto.
        
        Args:
            codigo_producto (str): Código único del producto (PROD-XXX)
            nombre (str): Nombre del producto
            descripcion (str): Descripción detallada
            marca_id (ObjectId): ID de la marca
            marca_nombre (str): Nombre de la marca
            categoria_id (ObjectId): ID de la categoría
            categoria_nombre (str): Nombre de la categoría
            categoria_slug (str): Slug de la categoría
            especificaciones (dict): Especificaciones técnicas
            precio_usd (float): Precio en USD
            fecha_lanzamiento (datetime): Fecha de lanzamiento
            disponibilidad (str): Estado de disponibilidad
            descripcion_embedding (list): Vector de embedding
            imagen_principal (str): URL de imagen principal
            
        Returns:
            dict: Documento de producto
        """
        return {
            "codigo_producto": codigo_producto,
            "nombre": nombre,
            "descripcion": descripcion,
            "marca": {
                "id": marca_id,
                "nombre": marca_nombre
            },
            "categoria": {
                "id": categoria_id,
                "nombre": categoria_nombre,
                "slug": categoria_slug
            },
            "especificaciones": especificaciones,
            "metadata": {
                "precio_usd": precio_usd,
                "fecha_lanzamiento": fecha_lanzamiento,
                "disponibilidad": disponibilidad,
                "calificacion_promedio": 0.0,
                "cantidad_resenas": 0
            },
            "descripcion_embedding": descripcion_embedding or [],
            "imagen_principal": imagen_principal,
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": datetime.now()
        }


class ResenaSchema:
    """Esquema para la colección de reseñas."""
    
    @staticmethod
    def create(
        id_producto,
        id_usuario,
        nombre_usuario,
        comprador_verificado,
        calificacion,
        titulo,
        contenido,
        ventajas=None,
        desventajas=None,
        idioma="es",
        votos_utiles=0,
        compra_verificada=False,
        contenido_embedding=None
    ):
        """
        Crea un documento de reseña.
        
        Args:
            id_producto (ObjectId): ID del producto
            id_usuario (ObjectId): ID del usuario
            nombre_usuario (str): Nombre del usuario
            comprador_verificado (bool): Si el usuario está verificado
            calificacion (int): Calificación de 1 a 5
            titulo (str): Título de la reseña
            contenido (str): Contenido de la reseña
            ventajas (list): Lista de ventajas
            desventajas (list): Lista de desventajas
            idioma (str): Código de idioma
            votos_utiles (int): Número de votos útiles
            compra_verificada (bool): Si la compra está verificada
            contenido_embedding (list): Vector de embedding
            
        Returns:
            dict: Documento de reseña
        """
        return {
            "id_producto": id_producto,
            "id_usuario": id_usuario,
            "usuario": {
                "nombre_usuario": nombre_usuario,
                "comprador_verificado": comprador_verificado
            },
            "calificacion": calificacion,
            "titulo": titulo,
            "contenido": contenido,
            "ventajas": ventajas or [],
            "desventajas": desventajas or [],
            "idioma": idioma,
            "votos_utiles": votos_utiles,
            "compra_verificada": compra_verificada,
            "contenido_embedding": contenido_embedding or [],
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": datetime.now()
        }


class ImagenProductoSchema:
    """Esquema para la colección de imágenes de productos."""
    
    @staticmethod
    def create(
        id_producto,
        url_imagen,
        tipo_imagen="foto_producto",
        angulo_vista="frontal",
        metadata=None,
        texto_alternativo="",
        es_principal=False,
        orden_visualizacion=1,
        imagen_embedding=None
    ):
        """
        Crea un documento de imagen de producto.
        
        Args:
            id_producto (ObjectId): ID del producto
            url_imagen (str): URL de la imagen
            tipo_imagen (str): Tipo de imagen
            angulo_vista (str): Ángulo de la vista
            metadata (dict): Metadatos de la imagen (ancho, alto, formato, tamaño)
            texto_alternativo (str): Texto alternativo
            es_principal (bool): Si es la imagen principal
            orden_visualizacion (int): Orden de visualización
            imagen_embedding (list): Vector de embedding
            
        Returns:
            dict: Documento de imagen
        """
        return {
            "id_producto": id_producto,
            "url_imagen": url_imagen,
            "tipo_imagen": tipo_imagen,
            "angulo_vista": angulo_vista,
            "metadata": metadata or {},
            "imagen_embedding": imagen_embedding or [],
            "texto_alternativo": texto_alternativo,
            "es_principal": es_principal,
            "orden_visualizacion": orden_visualizacion,
            "fecha_subida": datetime.now()
        }
