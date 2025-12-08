# Script para descargar modelos Whisper para SpeechModel
Write-Host "📥 DESCARGANDO MODELOS WHISPER PARA ESPAÑOL" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Crear directorio para modelos (relativo al proyecto)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelsDir = Join-Path $scriptDir "models"
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null

Write-Host "📂 Directorio de modelos: $modelsDir" -ForegroundColor White

# URLs de modelos (usando Hugging Face)
# Priorizando large-v3 para mejor precisión en español
$models = [ordered]@{
    "large-v3" = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin"
    "base"     = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
    "tiny"     = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"
}

foreach ($model in $models.Keys) {
    $url = $models[$model]
    $output = "$modelsDir\ggml-$model.bin"
    
    Write-Host "`n🔽 Descargando modelo $model..." -ForegroundColor Yellow
    
    if (Test-Path $output) {
        Write-Host "   ✅ Ya existe: $output" -ForegroundColor Green
        continue
    }
    
    try {
        # Descargar con progreso
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $output
        
        # Verificar descarga
        $fileSize = (Get-Item $output).Length / 1MB
        Write-Host "   ✅ Descargado: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Error descargando $model : $_" -ForegroundColor Red
    }
}

Write-Host "`n📊 RESUMEN DE MODELOS DESCARGADOS:" -ForegroundColor Cyan
Get-ChildItem $modelsDir | ForEach-Object {
    $sizeMB = $_.Length / 1MB
    Write-Host "   • $($_.Name) - $([math]::Round($sizeMB, 2)) MB" -ForegroundColor White
}

Write-Host "`n🎯 LISTO! Los modelos están en: $modelsDir" -ForegroundColor Green