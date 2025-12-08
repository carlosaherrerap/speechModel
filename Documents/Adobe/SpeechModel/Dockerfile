# Dockerfile para SpeechModel API con whisper.cpp
FROM ubuntu:22.04

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    cmake \
    wget \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Clonar y compilar whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git && \
    cd whisper.cpp && \
    make

# Copiar archivos de requisitos del backend
COPY backend/requirements.txt /app/backend/requirements.txt

# Instalar dependencias Python (versión simplificada sin faster-whisper)
RUN pip3 install flask flask-cors colorama python-multipart

# Copiar código del backend
COPY backend/ /app/backend/

# Copiar script de wrapper para whisper.cpp
COPY backend/whisper_wrapper.py /app/backend/

# Crear directorios necesarios
RUN mkdir -p /app/models /app/auds /app/audProd /app/speeching

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV WHISPER_CPP_PATH=/app/whisper.cpp

# Comando por defecto
CMD ["python3", "backend/app.py"]
