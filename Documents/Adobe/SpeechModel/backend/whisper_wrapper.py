"""
Wrapper para ejecutar whisper.cpp desde Python y obtener transcripciones.
Este módulo reemplaza faster-whisper en el entorno Docker Ubuntu.
"""
import os
import json
import subprocess
import tempfile
import colorama
from pathlib import Path
from config import (
    CONFIDENCE_LEVELS,
    COLORS,
)

# Inicializar colorama
colorama.init(autoreset=True)

# Ruta a whisper.cpp
WHISPER_CPP_PATH = os.environ.get('WHISPER_CPP_PATH', '/app/whisper.cpp')
# El ejecutable está en el directorio build después de compilar
WHISPER_MAIN = os.path.join(WHISPER_CPP_PATH, 'build', 'bin', 'whisper-cli')


class AudioTranscriber:
    def __init__(self):
        """Inicializa el transcriber con whisper.cpp."""
        self.model_path = None
        self.load_model()

    def load_model(self):
        """Verifica que whisper.cpp y el modelo estén disponibles."""
        print(f"🔄 Verificando whisper.cpp...")
        
        if not os.path.exists(WHISPER_MAIN):
            raise FileNotFoundError(
                f"❌ whisper.cpp no encontrado en: {WHISPER_MAIN}\n"
                f"Asegúrate de que el contenedor se construyó correctamente."
            )
        
        # Buscar el modelo
        model_dir = Path("/app/models")
        model_file = model_dir / "ggml-large-v3.bin"
        
        if not model_file.exists():
            raise FileNotFoundError(
                f"❌ Modelo no encontrado: {model_file}\n"
                f"Asegúrate de haber ejecutado downloadModels.ps1 antes de construir el contenedor."
            )
        
        self.model_path = str(model_file)
        print(f"✅ whisper.cpp y modelo ggml-large-v3.bin encontrados")

    def transcribe(self, audio_path: str, show_colors=True):
        """
        Transcribe un archivo de audio usando whisper.cpp.
        
        Args:
            audio_path: Ruta al archivo de audio
            show_colors: Si True, imprime en consola con colores
            
        Returns:
            dict con 'text', 'segments', y 'colored_text'
        """
        print(f"\n🎤 Transcribiendo: {Path(audio_path).name}")
        
        try:
            # Construir comando para whisper.cpp (con timestamps para obtener más detalle)
            cmd = [
                WHISPER_MAIN,
                '-m', self.model_path,
                '-f', audio_path,
                '-l', 'es',  # Español
                '-t', '4',  # 4 threads
                '-pc',  # Print colors basado en confianza
            ]
            
            # Ejecutar whisper.cpp
            print(f"🔄 Ejecutando: {' '.join(cmd[:6])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                raise Exception(f"whisper.cpp falló (code {result.returncode}): {error_msg[:500]}")
            
            # Procesar la salida de texto
            # whisper-cli imprime la transcripción en stdout
            output_lines = result.stdout.split('\n')
            
            # Función para limpiar códigos ANSI
            import re
            def strip_ansi(text):
                """Elimina códigos ANSI de escape (colores)"""
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                return ansi_escape.sub('', text)
            
            # Extraer solo las líneas de transcripción (skip info lines)
            transcription_lines = []
            for line in output_lines:
                line = line.strip()
                # Limpiar códigos ANSI primero
                clean_line = strip_ansi(line)
                
                # Eliminar timestamps [00:00:00.000 --> 00:00:05.440]
                clean_line = re.sub(r'\[[\d:\.]+\s*-->\s*[\d:\.]+\]', '', clean_line)
                clean_line = clean_line.strip()
                
                # Skip líneas de info/debug
                if (clean_line and 
                    not clean_line.startswith('[') and 
                    'whisper' not in clean_line.lower() and
                    'processing' not in clean_line.lower() and
                    'model' not in clean_line.lower() and
                    'system_info' not in clean_line.lower() and
                    'time' not in clean_line.lower() and
                    'load' not in clean_line.lower() and
                    'sample' not in clean_line.lower() and
                    'encode' not in clean_line.lower() and
                    'decode' not in clean_line.lower() and
                    'ms' not in clean_line):
                    transcription_lines.append(clean_line)
            
            full_text = ' '.join(transcription_lines).strip()
            
            # Si no obtuvimos texto, revisar el output completo
            if not full_text:
                # Fallback: tomar todo excepto líneas obvias de debug
                for line in output_lines:
                    if line.strip() and not line.startswith('whisper_'):
                        full_text += line.strip() + ' '
                full_text = full_text.strip()
            
            # Crear datos de segmento simple (sin timestamps detallados)
            segment_data = [{
                "start": 0,
                "end": 0,
                "text": full_text,
                "confidence": 0.85,  # Confianza por defecto
                "words": []
            }]
            
            # Colorear el texto
            colored_text = self._colorize_word(full_text, 0.85)
            
            result_dict = {
                "text": full_text,
                "segments": segment_data,
                "colored_text": colored_text,
                "language": "es",
                "language_probability": 0.99
            }
            
            # Mostrar en consola con colores
            if show_colors:
                print(f"\n📝 Transcripción:")
                print(colored_text)
                print(f"\n🌐 Idioma: español")
                print(f"📊 {len(full_text)} caracteres transcritos")
            
            return result_dict
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout: El audio es muy largo o el proceso se colgó")
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            raise

    def _colorize_word(self, word: str, confidence: float):
        """
        Aplica color a una palabra según su nivel de confianza.
        
        Args:
            word: Palabra a colorear
            confidence: Nivel de confianza (0-1)
            
        Returns:
            Palabra con código de color ANSI
        """
        if confidence >= CONFIDENCE_LEVELS["high"]:
            color = COLORS["green"]
        elif confidence >= CONFIDENCE_LEVELS["medium"]:
            color = COLORS["orange"]
        elif confidence >= CONFIDENCE_LEVELS["low"]:
            color = COLORS["yellow"]
        else:
            color = COLORS["red"]
        
        return f"{color}{word}{COLORS['reset']}"


# Función auxiliar para uso directo
def transcribe_audio(audio_path: str, show_colors=True):
    """Función wrapper para transcribir un audio fácilmente."""
    transcriber = AudioTranscriber()
    return transcriber.transcribe(audio_path, show_colors)


if __name__ == "__main__":
    # Test del módulo
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python whisper_wrapper.py <archivo_audio>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    result = transcribe_audio(audio_file)
    print(f"\n✅ Transcripción completada: {len(result['text'])} caracteres")
