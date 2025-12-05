@echo off
echo ================================================================
echo               RAG TECH - INICIADOR RAPIDO
echo ================================================================
echo.

echo 📋 Verificando requisitos del sistema...

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo    Por favor, instala Python 3.8 o superior desde python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verificar si existe un entorno virtual
if not exist "venv\" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual existente encontrado
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Verificar si pip está actualizado
echo 📦 Actualizando pip...
python -m pip install --upgrade pip --quiet

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

REM Verificar archivo de configuración
if not exist ".env" (
    echo ⚙️  Creando archivo de configuración...
    copy ".env.example" ".env"
    echo.
    echo ⚠️  IMPORTANTE: Debes editar el archivo .env con tu URI de MongoDB Atlas
    echo    Abre .env y reemplaza la URI de ejemplo con tu conexión real
    echo.
    pause
)

echo.
echo ================================================================
echo                    CONFIGURACION COMPLETA
echo ================================================================
echo.
echo 🚀 Ya puedes ejecutar la aplicación:
echo.
echo    📊 Aplicación CLI:    python app.py
echo    🌐 Interfaz Web:      python web_app.py
echo.
echo 🔗 URLs de la interfaz web:
echo    Principal:            http://localhost:5000
echo    Búsqueda RAG:         http://localhost:5000/ragtech
echo    API:                  http://localhost:5000/api/stats
echo.
echo ⚠️  RECUERDA: Configura tu .env con la URI de MongoDB Atlas antes de usar
echo.
pause