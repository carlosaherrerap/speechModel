# Script simple para descargar modelos Whisper
Write-Host "=== DESCARGANDO MODELOS WHISPER ===" -ForegroundColor Cyan

# Directorio actual
$scriptDir = Get-Location
$modelsDir = Join-Path $scriptDir "models"

# Crear directorio si no existe
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
}

# Modelos a descargar
$modelUrls = @{
    "large-v3" = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin"
    "base" = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
    "tiny" = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"
}

Write-Host "Descargando modelos a: $modelsDir"

foreach ($modelName in $modelUrls.Keys) {
    $url = $modelUrls[$modelName]
    $outputFile = Join-Path $modelsDir "ggml-$modelName.bin"
    
    Write-Host "Procesando $modelName..."
    
    if (Test-Path $outputFile) {
        Write-Host "  Ya existe, omitiendo..." -ForegroundColor Yellow
        continue
    }
    
    try {
        # Silenciar progreso para mejor legibilidad
        $ProgressPreference = 'SilentlyContinue'
        Write-Host "  Descargando..."
        Invoke-WebRequest -Uri $url -OutFile $outputFile -UseBasicParsing
        $ProgressPreference = 'Continue'
        
        if (Test-Path $outputFile) {
            $size = (Get-Item $outputFile).Length / 1MB
            Write-Host "  OK ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== COMPLETADO ===" -ForegroundColor Green
Write-Host "Modelos disponibles:"
Get-ChildItem $modelsDir | ForEach-Object {
    $size = $_.Length / 1MB
    Write-Host "  - $($_.Name) ($([math]::Round($size, 2)) MB)"
}