import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
AUDS_DIR = BASE_DIR / "auds"
AUD_PROD_DIR = BASE_DIR / "audProd"
SPEECHING_DIR = BASE_DIR / "speeching"

# Crear directorios si no existen
for directory in [MODELS_DIR, AUDS_DIR, AUD_PROD_DIR, SPEECHING_DIR]:
    directory.mkdir(exist_ok=True)

# Configuración del modelo
MODEL_PATH = MODELS_DIR / "ggml-large-v3.bin"

# Parámetros de transcripción para español
TRANSCRIPTION_CONFIG = {
    "language": "es",  # Español
    "task": "transcribe",
    "beam_size": 5,  # Mayor precisión
    "best_of": 5,
    "temperature": 0.0,  # Determinístico
    "word_timestamps": True,  # Para obtener confianza por palabra
    "vad_filter": True,  # Filtro de detección de voz
}

# Niveles de confianza para colores
CONFIDENCE_LEVELS = {
    "high": 0.85,      # Verde
    "medium": 0.70,    # Naranja
    "low": 0.50,       # Amarillo
    # < 0.50           # Rojo
}

# Colores ANSI para terminal (Windows con colorama)
COLORS = {
    "green": "\033[92m",
    "orange": "\033[38;5;208m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

# Configuración de Flask
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
}

# Formatos de audio soportados
SUPPORTED_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"]
