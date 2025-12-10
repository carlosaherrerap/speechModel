# SpeechModel - API de Transcripción en Español

Sistema completo de transcripción de audio usando Whisper (ggml-large-v3) optimizado para español, con API REST y procesamiento en lote para más de 1000 archivos.

## 🎯 Características

- ✅ Transcripción de alta precisión usando modelo large-v3
- ✅ Optimizado para español
- ✅ API REST con Flask
- ✅ Procesamiento en lote (1000+ archivos)
- ✅ Docker para fácil deployment
- ✅ Múltiples formatos: MP3, WAV, M4A, OGG, FLAC, AAC

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose
- ~3 GB espacio para el modelo
- Python 3.8+ (solo para desarrollo local)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/speechmodel.git
cd speechmodel

# Crear directorios
mkdir -p models auds audProd speeching

# Descargar modelo (usar PowerShell en Windows)
.\downloadModels.ps1

# O en Linux/Mac:
cd models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin

# Construir y ejecutar
docker-compose up --build -d
```

### Uso Básico

```bash
# Verificar que funciona
curl http://localhost:5000/health

# Procesar archivos
cd frontend
npm install
npm run start
```

## 📁 Estructura

```
SpeechModel/
├── backend/          # API Flask + whisper.cpp
├── frontend/         # Procesador en lote Node.js
├── models/           # Modelo ggml-large-v3.bin (no en Git)
├── auds/             # Archivos de prueba
├── audProd/          # Archivos de producción (input)
└── speeching/        # Transcripciones (output)
```

## 📚 Documentación

- [STATUS.md](STATUS.md) - Estado actual y uso
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía de deployment en servidor
- [README.md](README.md) - Documentación completa

## ⚡ Rendimiento

| Hardware | Velocidad |
|----------|-----------|
| CPU | ~1-2 min/min de audio |
| GPU NVIDIA | ~10-20 seg/min de audio |

## 🛠️ Tecnologías

- **Backend**: Python, Flask, whisper.cpp
- **Frontend**: Node.js, Axios
- **Container**: Docker, Ubuntu 22.04
- **Modelo**: Whisper large-v3 (3GB)

## 📝 Licencia

MIT

## 🤝 Contribuir

Pull requests bienvenidos. Para cambios grandes, abre un issue primero.
