# Script de prueba de la API - SpeechModel
Write-Host "`n🧪 PROBANDO API DE TRANSCRIPCIÓN" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$apiUrl = "http://localhost:5000"

# Verificar que la API está corriendo
Write-Host "`n📌 Verificando estado de la API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$apiUrl/health" -Method GET
    if ($health.status -eq "healthy") {
        Write-Host "   ✅ API funcionando correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ❌ API no está saludable" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ API no responde" -ForegroundColor Red
    Write-Host "   Asegúrate de que el servidor esté corriendo:" -ForegroundColor Yellow
    Write-Host "   cd backend && python app.py" -ForegroundColor Gray
    exit 1
}

# Buscar archivos de audio en /auds
Write-Host "`n📌 Buscando archivos de audio en /auds..." -ForegroundColor Yellow
$audioFiles = Get-ChildItem -Path ".\auds" -File | Where-Object {
    $_.Extension -match '\.(mp3|wav|m4a|ogg|flac|aac)$'
}

if ($audioFiles.Count -eq 0) {
    Write-Host "   ⚠️  No se encontraron archivos de audio en /auds" -ForegroundColor Yellow
    Write-Host "   Coloca algunos archivos .mp3, .wav o .m4a en /auds para probar" -ForegroundColor Gray
    exit 0
}

Write-Host "   ✅ Encontrados $($audioFiles.Count) archivos de audio" -ForegroundColor Green

# Transcribir cada archivo
$count = 1
foreach ($audioFile in $audioFiles) {
    Write-Host "`n" -NoNewline
    Write-Host "="*60 -ForegroundColor Blue
    Write-Host "[$count/$($audioFiles.Count)] Transcribiendo: $($audioFile.Name)" -ForegroundColor White
    Write-Host "="*60 -ForegroundColor Blue
    
    try {
        # Preparar el archivo para envío
        $filePath = $audioFile.FullName
        
        # Crear form data
        $boundary = [System.Guid]::NewGuid().ToString()
        $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
        $fileName = $audioFile.Name
        
        # Construir el cuerpo multipart
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"audio`"; filename=`"$fileName`"",
            "Content-Type: application/octet-stream",
            "",
            [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes),
            "--$boundary--"
        )
        $body = $bodyLines -join "`r`n"
        
        # Enviar request
        $response = Invoke-RestMethod `
            -Uri "$apiUrl/transcribe" `
            -Method POST `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body
        
        # Mostrar resultados
        Write-Host "`n📝 RESULTADO:" -ForegroundColor Green
        Write-Host "   Idioma: $($response.language) ($([math]::Round($response.language_probability * 100, 1))%)" -ForegroundColor Cyan
        Write-Host "   Palabras: $($response.word_count)" -ForegroundColor Cyan
        Write-Host "   Caracteres: $($response.character_count)" -ForegroundColor Cyan
        Write-Host "`n   Transcripción:" -ForegroundColor Yellow
        Write-Host "   $($response.text)" -ForegroundColor White
        
        # Analizar niveles de confianza
        $confidenceStats = @{
            "high" = 0
            "medium" = 0
            "low" = 0
            "very_low" = 0
        }
        
        foreach ($segment in $response.segments) {
            foreach ($word in $segment.words) {
                if ($word.probability -ge 0.85) {
                    $confidenceStats["high"]++
                } elseif ($word.probability -ge 0.70) {
                    $confidenceStats["medium"]++
                } elseif ($word.probability -ge 0.50) {
                    $confidenceStats["low"]++
                } else {
                    $confidenceStats["very_low"]++
                }
            }
        }
        
        $totalWords = $confidenceStats["high"] + $confidenceStats["medium"] + $confidenceStats["low"] + $confidenceStats["very_low"]
        
        if ($totalWords -gt 0) {
            Write-Host "`n   📊 Estadísticas de Confianza:" -ForegroundColor Cyan
            Write-Host "      🟢 Alta (>85%):    $($confidenceStats['high']) palabras" -ForegroundColor Green
            Write-Host "      🟠 Media (70-85%): $($confidenceStats['medium']) palabras" -ForegroundColor DarkYellow
            Write-Host "      🟡 Baja (50-70%):  $($confidenceStats['low']) palabras" -ForegroundColor Yellow
            Write-Host "      🔴 Muy baja (<50%): $($confidenceStats['very_low']) palabras" -ForegroundColor Red
        }
        
        Write-Host "`n   ✅ Transcripción exitosa" -ForegroundColor Green
        
    } catch {
        Write-Host "   ❌ Error: $_" -ForegroundColor Red
    }
    
    $count++
}

Write-Host "`n" -NoNewline
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "✅ PRUEBA COMPLETADA" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""
