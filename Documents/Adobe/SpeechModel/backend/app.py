import os
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import colorama

# Intentar importar whisper_wrapper (Docker) o transcriber (Windows)
try:
    from whisper_wrapper import AudioTranscriber
    print("✅ Usando whisper.cpp (Docker/Ubuntu)")
except ImportError:
    from transcriber import AudioTranscriber
    print("✅ Usando faster-whisper (Windows)")
    
from config import (
    AUDS_DIR,
    AUD_PROD_DIR,
    SPEECHING_DIR,
    SUPPORTED_FORMATS,
    FLASK_CONFIG,
)

# Inicializar colorama para Windows
colorama.init(autoreset=True)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Inicializar transcriber global
transcriber = None


def init_transcriber():
    """Inicializa el transcriber al arrancar la app."""
    global transcriber
    try:
        print("\n" + "="*60)
        print("🚀 INICIANDO API DE TRANSCRIPCIÓN")
        print("="*60)
        transcriber = AudioTranscriber()
        print("✅ API lista para transcribir")
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error inicializando transcriber: {e}")
        print("\n⚠️  Asegúrate de:")
        print("   1. Haber ejecutado downloadModels.ps1")
        print("   2. Tener el modelo ggml-large-v3.bin en /models")
        raise


@app.route('/', methods=['GET'])
def index():
    """Endpoint raíz con información de la API."""
    return jsonify({
        "name": "SpeechModel API",
        "version": "1.0.0",
        "description": "API de transcripción de audio usando Whisper (ggml-large-v3)",
        "endpoints": {
            "/": "GET - Información de la API",
            "/transcribe": "POST - Transcribir un archivo de audio",
            "/transcribe-file": "POST - Transcribir un archivo por ruta",
            "/health": "GET - Estado del servicio"
        },
        "status": "running"
    })


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check."""
    status = {
        "status": "healthy" if transcriber else "unhealthy",
        "model_loaded": transcriber is not None
    }
    return jsonify(status), 200 if transcriber else 503


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe un archivo de audio enviado en la request.
    
    Expects:
        - Multipart form data con campo 'audio'
        
    Returns:
        JSON con transcripción y metadatos
    """
    try:
        # Verificar que el transcriber esté inicializado
        if not transcriber:
            return jsonify({
                "error": "Transcriber no inicializado",
                "message": "El modelo no está cargado"
            }), 503
        
        # Verificar que se envió un archivo
        if 'audio' not in request.files:
            return jsonify({
                "error": "No se envió ningún archivo",
                "message": "Incluye un archivo en el campo 'audio'"
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({
                "error": "Nombre de archivo vacío",
                "message": "El archivo debe tener un nombre válido"
            }), 400
        
        # Verificar extensión
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            return jsonify({
                "error": "Formato no soportado",
                "message": f"Formatos soportados: {', '.join(SUPPORTED_FORMATS)}",
                "received": file_ext
            }), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        temp_path = AUDS_DIR / filename
        file.save(str(temp_path))
        
        print(f"\n📥 Recibido: {filename}")
        
        # Transcribir
        result = transcriber.transcribe(str(temp_path), show_colors=True)
        
        # Opcional: eliminar archivo temporal
        # temp_path.unlink()  # Descomentar si quieres borrar después
        
        # Preparar respuesta
        response = {
            "success": True,
            "filename": filename,
            "text": result["text"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "segments": result["segments"],
            "character_count": len(result["text"]),
            "word_count": len(result["text"].split())
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error en /transcribe: {e}")
        return jsonify({
            "error": "Error en transcripción",
            "message": str(e)
        }), 500


@app.route('/transcribe-file', methods=['POST'])
def transcribe_file():
    """
    Transcribe un archivo por su ruta en el sistema.
    Útil para el frontend que procesa archivos de /audProd.
    
    Expects:
        JSON: {"filepath": "ruta/al/audio.mp3"}
        
    Returns:
        JSON con transcripción y metadatos
    """
    try:
        if not transcriber:
            return jsonify({
                "error": "Transcriber no inicializado",
                "message": "El modelo no está cargado"
            }), 503
        
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify({
                "error": "Campo 'filepath' requerido",
                "message": "Envía JSON con {\"filepath\": \"ruta/al/audio.mp3\"}"
            }), 400
        
        filepath = Path(data['filepath'])
        
        if not filepath.exists():
            return jsonify({
                "error": "Archivo no encontrado",
                "message": f"No existe: {filepath}"
            }), 404
        
        # Verificar extensión
        if filepath.suffix.lower() not in SUPPORTED_FORMATS:
            return jsonify({
                "error": "Formato no soportado",
                "message": f"Formatos soportados: {', '.join(SUPPORTED_FORMATS)}"
            }), 400
        
        # Transcribir
        result = transcriber.transcribe(str(filepath), show_colors=True)
        
        # Guardar resultado en /speeching si se especifica
        if data.get('save_result', False):
            output_filename = filepath.stem + '.txt'
            output_path = SPEECHING_DIR / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result["text"])
            print(f"💾 Guardado en: {output_path}")
        
        response = {
            "success": True,
            "filename": filepath.name,
            "text": result["text"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "segments": result["segments"],
            "character_count": len(result["text"]),
            "word_count": len(result["text"].split())
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error en /transcribe-file: {e}")
        return jsonify({
            "error": "Error en transcripción",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    # Inicializar transcriber antes de arrancar
    init_transcriber()
    
    # Iniciar servidor
    print(f"\n🌐 Servidor corriendo en http://{FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}")
    print(f"📁 Carpeta de audios de prueba: {AUDS_DIR}")
    print(f"📁 Carpeta de producción: {AUD_PROD_DIR}")
    print(f"📁 Carpeta de resultados: {SPEECHING_DIR}")
    print("\n💡 Usa Ctrl+C para detener el servidor\n")
    
    app.run(**FLASK_CONFIG)
