# 📘 Guía de Configuración MongoDB Atlas

## Paso a Paso para Configurar el Cluster

### 1️⃣ Crear Cuenta en MongoDB Atlas

1. Ir a: https://www.mongodb.com/cloud/atlas/register
2. Registrarse con email o cuenta de Google/GitHub
3. Verificar email si es necesario

### 2️⃣ Crear Nuevo Proyecto

1. Click en "New Project"
2. Nombre: `tech-rag-project`
3. Click "Next" → "Create Project"

### 3️⃣ Crear Cluster Gratuito (M0)

1. Click en "Build a Database"
2. Seleccionar **FREE (M0 Sandbox)**
3. Configuración:
   - **Provider**: AWS, Google Cloud o Azure
   - **Region**: Elegir la más cercana (ej: Virginia, São Paulo)
   - **Cluster Name**: `tech-rag-cluster`
4. Click "Create"

⏱️ **Nota**: El cluster tardará 3-5 minutos en crearse

### 4️⃣ Configurar Seguridad

#### A. Método de Autenticación

1. Seleccionar "Username and Password"
2. Configurar:
   ```
   Username: tech_rag_admin
   Password: [Click en "Autogenerate Secure Password" o crear uno]
   ```
3. **⚠️ IMPORTANTE**: Guardar la contraseña en un lugar seguro
4. Click "Create User"

#### B. Acceso de Red

1. En "Where would you like to connect from?"
2. Click "Add My Current IP Address"
3. **Para desarrollo**, también agregar: `0.0.0.0/0` (acceso desde cualquier IP)
   - Click "Add IP Address"
   - IP Address: `0.0.0.0/0`
   - Description: `Anywhere (Development)`
4. Click "Finish and Close"

### 5️⃣ Obtener Connection String

1. Click en "Connect" (botón en el cluster)
2. Seleccionar "Drivers"
3. Driver: **Python** / Version: **3.12 or later**
4. Copiar el connection string:
   ```
   mongodb+srv://tech_rag_admin:<password>@tech-rag-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Reemplazar `<password>` con tu contraseña real

### 6️⃣ Configurar en el Proyecto

Editar archivo `.env`:

```env
MONGODB_URI=mongodb+srv://tech_rag_admin:TU_PASSWORD_AQUI@tech-rag-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=tech_rag_db
```

### 7️⃣ Crear Base de Datos y Colecciones

Ejecutar scripts:

```powershell
# 1. Crear colecciones con validación
python scripts/01_setup_database.py

# 2. Crear índices
python scripts/02_create_indexes.py

# 3. Verificar
python scripts/05_test_connection.py
```

### 8️⃣ Crear Índices Vectoriales (Atlas Search)

Los índices vectoriales **deben crearse manualmente** en la UI de Atlas:

#### Para la colección `articles`:

1. En Atlas, ir a tu cluster
2. Click en pestaña **"Search"**
3. Click **"Create Search Index"**
4. Seleccionar **"JSON Editor"**
5. En "Database and Collection":
   - Database: `tech_rag_db`
   - Collection: `articles`
6. En "Index Name": `vector_index_articles`
7. Pegar esta configuración JSON:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "texto_embedding": {
        "type": "knnVector",
        "dimensions": 384,
        "similarity": "cosine"
      },
      "metadata": {
        "type": "document",
        "fields": {
          "idioma": {
            "type": "string"
          },
          "categoria": {
            "type": "string"
          },
          "fecha_publicacion": {
            "type": "date"
          }
        }
      }
    }
  }
}
```

8. Click **"Create Search Index"**

#### Para la colección `images`:

Repetir el proceso anterior pero con:
- Collection: `images`
- Index Name: `vector_index_images`
- Configuración:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "image_embedding": {
        "type": "knnVector",
        "dimensions": 512,
        "similarity": "cosine"
      },
      "metadata": {
        "type": "document",
        "fields": {
          "tipo": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

⏱️ **Nota**: Los índices pueden tardar 5-10 minutos en estar listos

### 9️⃣ Verificar Índices Vectoriales

1. En la pestaña "Search", deberías ver:
   - ✅ `vector_index_articles` (Status: Active)
   - ✅ `vector_index_images` (Status: Active)

### 🔟 Explorar con MongoDB Compass (Opcional)

1. Descargar [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. Abrir Compass
3. Pegar tu connection string
4. Conectar y explorar colecciones visualmente

---

## 🎯 Checklist de Configuración

- [ ] Cuenta de Atlas creada
- [ ] Proyecto `tech-rag-project` creado
- [ ] Cluster `tech-rag-cluster` (M0) creado
- [ ] Usuario `tech_rag_admin` configurado
- [ ] IP `0.0.0.0/0` agregada a Network Access
- [ ] Connection string copiado
- [ ] Archivo `.env` configurado
- [ ] Script `01_setup_database.py` ejecutado exitosamente
- [ ] Script `02_create_indexes.py` ejecutado exitosamente
- [ ] Índices vectoriales creados en Atlas UI
- [ ] Script `05_test_connection.py` pasa todos los tests

---

## ⚠️ Troubleshooting

### Error: "Authentication failed"

**Solución:**
1. Verificar que la contraseña en `.env` sea correcta
2. No debe tener caracteres especiales sin escapar
3. Si tiene `@` o `#`, reemplazar con URL encoding:
   - `@` → `%40`
   - `#` → `%23`

### Error: "ServerSelectionTimeoutError"

**Causas comunes:**
1. Connection string incorrecto
2. IP no está en whitelist
3. Firewall bloqueando conexión
4. Cluster aún no está listo

**Solución:**
- Verificar connection string
- Agregar `0.0.0.0/0` a Network Access
- Esperar a que el cluster esté en estado "Active"

### Error: "Database 'tech_rag_db' not found"

**Solución:**
- Normal en primera ejecución
- La base de datos se creará automáticamente al ejecutar `01_setup_database.py`

---

## 📊 Recursos Adicionales

- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [Vector Search Guide](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- [Connection String Format](https://www.mongodb.com/docs/manual/reference/connection-string/)
- [Python Driver (PyMongo)](https://pymongo.readthedocs.io/)

---

**¿Necesitas ayuda?**
- [MongoDB Community Forums](https://www.mongodb.com/community/forums/)
- [Stack Overflow - mongodb-atlas](https://stackoverflow.com/questions/tagged/mongodb-atlas)
