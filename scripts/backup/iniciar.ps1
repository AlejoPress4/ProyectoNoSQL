# Script de inicialización rápida para RAG Tech
# PowerShell Version

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "               RAG TECH - INICIADOR RAPIDO" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Verificando requisitos del sistema..." -ForegroundColor Yellow

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Por favor, instala Python 3.8 o superior desde python.org" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Verificar si existe un entorno virtual
if (-Not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        Read-Host "Presiona Enter para continuar"
        exit 1
    }
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "✅ Entorno virtual existente encontrado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar si pip está actualizado
Write-Host "📦 Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

Write-Host "✅ Dependencias instaladas correctamente" -ForegroundColor Green

# Verificar archivo de configuración
if (-Not (Test-Path ".env")) {
    Write-Host "⚙️ Creando archivo de configuración..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Debes editar el archivo .env con tu URI de MongoDB Atlas" -ForegroundColor Yellow
    Write-Host "   Abre .env y reemplaza la URI de ejemplo con tu conexión real" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter cuando hayas configurado el archivo .env"
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                    CONFIGURACION COMPLETA" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Ya puedes ejecutar la aplicación:" -ForegroundColor Green
Write-Host ""
Write-Host "   📊 Aplicación CLI:    python app.py" -ForegroundColor White
Write-Host "   🌐 Interfaz Web:      python web_app.py" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URLs de la interfaz web:" -ForegroundColor Cyan
Write-Host "   Principal:            http://localhost:5000" -ForegroundColor White
Write-Host "   Búsqueda RAG:         http://localhost:5000/ragtech" -ForegroundColor White
Write-Host "   API:                  http://localhost:5000/api/stats" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  RECUERDA: Configura tu .env con la URI de MongoDB Atlas antes de usar" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona Enter para continuar"