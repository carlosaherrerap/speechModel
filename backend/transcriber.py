import os
import colorama
from faster_whisper import WhisperModel
from pathlib import Path
from config import (
    MODEL_PATH,
    TRANSCRIPTION_CONFIG,
    CONFIDENCE_LEVELS,
    COLORS,
)

# Inicializar colorama para Windows
colorama.init(autoreset=True)


class AudioTranscriber:
    def __init__(self):
        """Inicializa el modelo Whisper."""
        self.model = None
        self.load_model()

    def load_model(self):
        """Carga el modelo large-v3 de Whisper."""
        print(f"🔄 Cargando modelo Whisper large-v3...")
        print(f"   (La primera vez descargará el modelo automáticamente)")
        
        try:
            # Usar faster-whisper con nombre de modelo
            # faster-whisper descarga automáticamente los modelos en formato CTranslate2
            # Los archivos .bin son para whisper.cpp, no para faster-whisper
            self.model = WhisperModel(
                "large-v3",  # Nombre del modelo, no ruta local
                device="auto",  # device="auto" detectará CUDA si está disponible, sino usará CPU
                compute_type="int8"  # Optimización para CPU
            )
            print(f"✅ Modelo large-v3 cargado correctamente")
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            print(f"   Intentando descargar modelo...")
            raise

    def transcribe(self, audio_path: str, show_colors=True):
        """
        Transcribe un archivo de audio y devuelve el texto con niveles de confianza.
        
        Args:
            audio_path: Ruta al archivo de audio
            show_colors: Si True, imprime en consola con colores
            
        Returns:
            dict con 'text', 'segments', y 'colored_text'
        """
        print(f"\n🎤 Transcribiendo: {Path(audio_path).name}")
        
        try:
            # Transcribir con faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                **TRANSCRIPTION_CONFIG
            )
            
            # Procesar segmentos
            full_text = []
            colored_text = []
            segment_data = []
            
            for segment in segments:
                segment_info = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "confidence": segment.avg_logprob,  # Confianza promedio del segmento
                    "words": []
                }
                
                # Procesar palabras individuales si están disponibles
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        word_info = {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        }
                        segment_info["words"].append(word_info)
                        
                        # Aplicar color según confianza
                        colored_word = self._colorize_word(
                            word.word, 
                            word.probability
                        )
                        colored_text.append(colored_word)
                else:
                    # Si no hay palabras individuales, usar el segmento completo
                    confidence = self._logprob_to_probability(segment.avg_logprob)
                    colored_segment = self._colorize_word(
                        segment.text,
                        confidence
                    )
                    colored_text.append(colored_segment)
                
                full_text.append(segment.text)
                segment_data.append(segment_info)
            
            result = {
                "text": " ".join(full_text),
                "segments": segment_data,
                "colored_text": " ".join(colored_text),
                "language": info.language,
                "language_probability": info.language_probability
            }
            
            # Mostrar en consola con colores
            if show_colors:
                print(f"\n📝 Transcripción:")
                print(result["colored_text"])
                print(f"\n🌐 Idioma detectado: {info.language} ({info.language_probability:.2%})")
            
            return result
            
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            raise

    def _logprob_to_probability(self, logprob):
        """Convierte log probability a probability (aproximado)."""
        import math
        # avg_logprob está en escala logarítmica, típicamente entre -1 y 0
        # Convertir a escala 0-1 (aproximado)
        return max(0, min(1, math.exp(logprob)))

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

    def get_confidence_color(self, confidence: float):
        """Devuelve el nombre del color para un nivel de confianza dado."""
        if confidence >= CONFIDENCE_LEVELS["high"]:
            return "green"
        elif confidence >= CONFIDENCE_LEVELS["medium"]:
            return "orange"
        elif confidence >= CONFIDENCE_LEVELS["low"]:
            return "yellow"
        else:
            return "red"


# Función auxiliar para uso directo
def transcribe_audio(audio_path: str, show_colors=True):
    """Función wrapper para transcribir un audio fácilmente."""
    transcriber = AudioTranscriber()
    return transcriber.transcribe(audio_path, show_colors)


if __name__ == "__main__":
    # Test del módulo
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python transcriber.py <archivo_audio>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    result = transcribe_audio(audio_file)
    print(f"\n✅ Transcripción completada: {len(result['text'])} caracteres")
