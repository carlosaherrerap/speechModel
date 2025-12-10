# Script de instalación para Windows - SpeechModel API
Write-Host "`n🚀 INSTALACIÓN DE SPEECHMODEL API" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Verificar Python
Write-Host "`n📌 Paso 1: Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion encontrado" -ForegroundColor Green
    
    # Verificar que sea Python 3.8+
    $versionOutput = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $majorMinor = $versionOutput.Split('.')
    $major = [int]$majorMinor[0]
    $minor = [int]$majorMinor[1]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "   ❌ Se requiere Python 3.8 o superior (tienes $major.$minor)" -ForegroundColor Red
        Write-Host "   Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ❌ Python no encontrado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Asegúrate de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    exit 1
}

# Verificar pip
Write-Host "`n📌 Paso 2: Verificando pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "   ✅ pip encontrado" -ForegroundColor Green
} catch {
    Write-Host "   ❌ pip no encontrado, instalando..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# Actualizar pip
Write-Host "`n📌 Paso 3: Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Crear entorno virtual
Write-Host "`n📌 Paso 4: Creando entorno virtual..." -ForegroundColor Yellow
$venvPath = ".\venv"
if (Test-Path $venvPath) {
    Write-Host "   ℹ️  Entorno virtual ya existe" -ForegroundColor Blue
} else {
    python -m venv venv
    Write-Host "   ✅ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "`n📌 Paso 5: Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✅ Entorno virtual activado" -ForegroundColor Green

# Instalar dependencias del backend
Write-Host "`n📌 Paso 6: Instalando dependencias Python..." -ForegroundColor Yellow
Write-Host "   (Esto puede tardar varios minutos)" -ForegroundColor Gray

if (Test-Path ".\backend\requirements.txt") {
    pip install -r .\backend\requirements.txt
    Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "   ❌ No se encontró backend\requirements.txt" -ForegroundColor Red
    exit 1
}

# Crear estructura de directorios
Write-Host "`n📌 Paso 7: Creando estructura de directorios..." -ForegroundColor Yellow
$directories = @("models", "auds", "audProd", "speeching")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   ✅ Creado: /$dir" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Ya existe: /$dir" -ForegroundColor Blue
    }
}

# Descargar modelos
Write-Host "`n📌 Paso 8: Descargando modelos Whisper..." -ForegroundColor Yellow
if (Test-Path ".\models\ggml-large-v3.bin") {
    Write-Host "   ℹ️  Modelo ggml-large-v3.bin ya existe" -ForegroundColor Blue
    $download = Read-Host "   ¿Descargar nuevamente? (s/N)"
    if ($download -eq "s" -or $download -eq "S") {
        & .\downloadModels.ps1
    }
} else {
    & .\downloadModels.ps1
}

# Verificar que el modelo se descargó
if (!(Test-Path ".\models\ggml-large-v3.bin")) {
    Write-Host "`n   ❌ ERROR: No se pudo descargar el modelo" -ForegroundColor Red
    Write-Host "   Intenta descargar manualmente desde:" -ForegroundColor Yellow
    Write-Host "   https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin" -ForegroundColor Yellow
    Write-Host "   Y colócalo en ./models/" -ForegroundColor Yellow
    exit 1
}

# Crear audio de ejemplo si no existe
Write-Host "`n📌 Paso 9: Verificando audios de ejemplo..." -ForegroundColor Yellow
$exampleAudios = Get-ChildItem -Path ".\auds" -Include @("*.mp3", "*.wav", "*.m4a") -File
if ($exampleAudios.Count -eq 0) {
    Write-Host "   ⚠️  No hay audios de ejemplo en /auds" -ForegroundColor Yellow
    Write-Host "   Coloca algunos archivos .mp3, .wav o .m4a en /auds para probar" -ForegroundColor Gray
} else {
    Write-Host "   ✅ Encontrados $($exampleAudios.Count) archivos de audio de ejemplo" -ForegroundColor Green
}

# Resumen
Write-Host "`n" -NoNewline
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n📋 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Activar entorno virtual (si no está activo):" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Iniciar API:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  La API estará disponible en:" -ForegroundColor White
Write-Host "   http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "4️⃣  Para probar directamente un audio:" -ForegroundColor White
Write-Host "   python backend\transcriber.py auds\tu_audio.mp3" -ForegroundColor Gray
Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""
