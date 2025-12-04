# 📝 Guía de Configuración Inicial

## ¡Bienvenido! 👋

Esta guía te ayudará a configurar el proyecto para que funcione correctamente.

## 1️⃣ Configurar Variables de Entorno

El proyecto necesita un archivo `.env` con tus credenciales. Sigue estos pasos:

### Paso 1: Copiar el archivo de ejemplo

```bash
# En Windows PowerShell
Copy-Item .env.example .env

# En Linux/Mac
cp .env.example .env
```

### Paso 2: Editar el archivo `.env`

Abre el archivo `.env` con tu editor favorito y configura:

```env
# MongoDB Atlas (usa tus propias credenciales o las que te proporcioné por otro medio)
MONGODB_URI=mongodb+srv://usuario:password@cluster.xxxxx.mongodb.net/?appName=RAG
DATABASE_NAME=ragtech

# Groq API Key (obtén una gratis en console.groq.com)
GROQ_API_KEY=gsk_tu_api_key_aqui
```

**🔐 Importante:** 
- **MongoDB:** Usa las credenciales que te compartí de forma privada, o crea tu propia base de datos
- **Groq API:** 
  1. Ve a [console.groq.com](https://console.groq.com)
  2. Crea una cuenta gratis
  3. Genera tu API Key
  4. Agrégala al `.env`

## 2️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

⏳ **Esto tarda 5-10 minutos la primera vez** (descarga modelos de IA ~1.5 GB)

## 3️⃣ Iniciar el Servidor

```bash
py web_app.py
```

Deberías ver:
```
============================================================
🚀 INICIANDO SERVIDOR WEB RAG TECH
============================================================
📍 URL Principal: http://localhost:5000
...
```

## 4️⃣ Probar el Sistema

Abre tu navegador en **http://localhost:5000**

### Prueba 1: Interfaz Web
1. Ve a la sección "Búsqueda RAG"
2. Escribe: `laptop gaming con buena refrigeración bajo $1500`
3. Presiona "Buscar con IA"
4. ✨ ¡Deberías ver una respuesta inteligente con recomendaciones!

### Prueba 2: Con Python

```python
import requests

response = requests.post('http://localhost:5000/rag', json={
    "query": "smartphone con mejor cámara",
    "max_products": 3
})

print(response.json()['rag_response'])
```

### Prueba 3: Ejemplos Automáticos

```bash
py ejemplos_uso_groq.py
```

## 🛠️ Solución de Problemas

### ❌ Error: "GROQ_API_KEY no configurada"
- Asegúrate de haber creado el archivo `.env`
- Verifica que tiene las credenciales correctas
- Reinicia el servidor

### ❌ Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### ❌ Error de conexión MongoDB
- Usa las credenciales que te proporcioné arriba
- O crea tu propia base de datos en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

### ❌ El servidor está muy lento
- La primera vez descarga modelos (~1.5 GB)
- Solo pasa la primera vez
- Siguiente inicio: ~5 segundos

## 📚 Siguiente Pasos

1. **Lee el README.md** para ejemplos de consultas
2. **Explora `RESUMEN_IMPLEMENTACION.md`** para detalles técnicos
3. **Revisa `docs/INTEGRACION_GROQ_LLM.md`** para entender cómo funciona la IA

## 💡 Tips

- **Consultas específicas** dan mejores resultados que genéricas
- `include_images=false` → búsqueda más rápida
- `max_products=3` → respuestas más rápidas
- `include_reviews=true` → contexto más rico para la IA

---

¿Todo funcionando? 🎉 ¡Disfruta el sistema!

¿Problemas? Revisa el README.md sección "Solución de Problemas"
