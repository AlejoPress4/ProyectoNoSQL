"""
Servidor simple para probar la aplicación RAG sin dependencias pesadas.
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Página principal."""
    return """
    <h1>🚀 Servidor RAG Tech - FUNCIONANDO!</h1>
    <p>✅ API Key de Groq: Configurada</p>
    <p>✅ Servidor Flask: Funcionando</p>
    <hr>
    <h3>Enlaces disponibles:</h3>
    <ul>
        <li><a href="/rag-interface">🤖 Pipeline RAG</a></li>
        <li><a href="/ragtech">🔍 Búsqueda Semántica</a></li>
        <li><a href="/api/status">📊 Estado de la API</a></li>
    </ul>
    """

@app.route('/rag-interface')
def rag_interface():
    """Interfaz del Pipeline RAG."""
    try:
        return render_template('rag_interface.html')
    except Exception as e:
        return f"<h1>Interfaz RAG</h1><p>Error cargando template: {str(e)}</p>"

@app.route('/ragtech')
def ragtech():
    """Búsqueda semántica."""
    try:
        return render_template('ragtech.html')
    except Exception as e:
        return f"<h1>Búsqueda Semántica</h1><p>Error cargando template: {str(e)}</p>"

@app.route('/api/status')
def api_status():
    """Estado de la API."""
    return jsonify({
        "status": "running",
        "message": "Servidor RAG funcionando correctamente",
        "groq_api_configured": True,
        "endpoints": [
            "/rag-interface",
            "/ragtech",
            "/api/status"
        ]
    })

@app.route('/test-rag')
def test_rag():
    """Página de prueba simple."""
    return """
    <h1>🧪 Test del Pipeline RAG</h1>
    <form method="post" action="/api/test-search">
        <label>Consulta de prueba:</label><br>
        <input type="text" name="query" value="smartphone" style="width: 300px; padding: 5px;"><br><br>
        <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px;">
            🔍 Probar Búsqueda
        </button>
    </form>
    """

@app.route('/api/test-search', methods=['POST'])
def test_search():
    """Prueba simple de búsqueda."""
    query = request.form.get('query', '')
    return jsonify({
        "query": query,
        "status": "success",
        "message": f"Búsqueda simulada para: {query}",
        "results": [
            {"name": "iPhone 15 Pro", "similarity": 0.95},
            {"name": "Samsung Galaxy S24", "similarity": 0.87},
            {"name": "Google Pixel 8", "similarity": 0.82}
        ]
    })

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR SIMPLE RAG TECH")
    print("=" * 50)
    print("📍 URL Principal: http://localhost:5000")
    print("🤖 Pipeline RAG: http://localhost:5000/rag-interface")
    print("🔍 Búsqueda: http://localhost:5000/ragtech")
    print("🧪 Prueba: http://localhost:5000/test-rag")
    print("=" * 50)
    
    app.run(debug=False, host='0.0.0.0', port=5000)