# 🚀 Guía de Deployment en Servidor

## 📦 Preparación del Proyecto para GitHub

### 1. Subir a GitHub

```bash
# En tu máquina local (Windows)
cd C:\Users\mmois\Documents\Adobe\SpeechModel
git init
git add .
git commit -m "Initial commit - SpeechModel API"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/speechmodel.git
git push -u origin main
```

---

## 🖥️ Instalación en Servidor

### Requisitos del Servidor
- Ubuntu 20.04+ o similar
- Docker y Docker Compose instalados
- Git instalado
- Al menos 4GB RAM
- 10GB espacio en disco

---

## 📝 Pasos de Instalación

### 1. Conectar al Servidor

```bash
ssh usuario@tu-servidor.com
```

### 2. Instalar Docker (si no está instalado)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose -y

# Agregar usuario actual a grupo docker
sudo usermod -aG docker $USER

# Recargar grupo (o cerrar sesión y volver a entrar)
newgrp docker
```

### 3. Clonar el Repositorio

```bash
# Ir a home o donde quieras instalar
cd ~

# Clonar repositorio
git clone https://github.com/TU_USUARIO/speechmodel.git

# Entrar al directorio
cd speechmodel
```

### 4. Crear Estructura de Directorios

```bash
# Crear carpetas necesarias
mkdir -p models auds audProd speeching
```

### 5. Descargar el Modelo

**Opción A: Desde tu máquina local (recomendado)**

En tu Windows, copia el modelo al servidor:
```powershell
# Desde PowerShell en Windows
scp models\ggml-large-v3.bin usuario@tu-servidor:~/speechmodel/models/
```

**Opción B: Descargar directo en el servidor**

```bash
cd ~/speechmodel/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

### 6. Construir y Levantar Docker

```bash
cd ~/speechmodel

# Construir el contenedor (toma 5-10 minutos)
docker-compose build

# Iniciar el servicio
docker-compose up -d
```

### 7. Verificar que Funciona

```bash
# Ver logs
docker-compose logs -f

# Verificar salud de la API
curl http://localhost:5000/health
```

Deberías ver:
```json
{"status":"healthy","model_loaded":true}
```

---

## 🎯 Usar el Sistema en el Servidor

### Subir Archivos de Audio

**Opción A: Via SCP desde Windows**

```powershell
# Copiar muchos archivos
scp C:\MisAudios\*.mp3 usuario@tu-servidor:~/speechmodel/audProd/
```

**Opción B: Via SFTP**

Usa FileZilla o WinSCP para transferir archivos gráficamente.

### Iniciar Procesamiento

```bash
cd ~/speechmodel/frontend
npm install  # Solo la primera vez
npm run start
```

### Descargar Resultados

```powershell
# En Windows, descargar transcripciones
scp -r usuario@tu-servidor:~/speechmodel/speeching C:\MisTranscripciones\
```

---

## 🔧 Comandos Útiles en el Servidor

### Ver logs en tiempo real
```bash
docker-compose logs -f speechmodel-api
```

### Reiniciar servicio
```bash
docker-compose restart
```

### Detener servicio
```bash
docker-compose down
```

### Ver estado
```bash
docker-compose ps
```

### Limpiar todo y empezar de cero
```bash
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Monitoreo

### Ver uso de recursos
```bash
docker stats speechmodel-api
```

### Ver espacio en disco
```bash
df -h
du -sh ~/speechmodel/*
```

---

## 🔒 Seguridad (Opcional pero Recomendado)

### Configurar Firewall

```bash
# Solo permitir SSH y API local
sudo ufw allow 22/tcp
sudo ufw enable
```

Si quieres acceder a la API remotamente:
```bash
sudo ufw allow 5000/tcp
```

### Usar Reverse Proxy (Nginx)

```bash
sudo apt install nginx -y

# Crear configuración
sudo nano /etc/nginx/sites-available/speechmodel

# Pegar:
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Activar
sudo ln -s /etc/nginx/sites-available/speechmodel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 Actualizar el Código

Cuando hagas cambios y los subas a GitHub:

```bash
cd ~/speechmodel
git pull origin main
docker-compose build
docker-compose restart
```

---

## 📝 Automatización (Opcional)

### Script para procesar automáticamente

Crea `~/speechmodel/auto-process.sh`:

```bash
#!/bin/bash
cd ~/speechmodel/frontend
npm run start

# Mover resultados
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p ~/transcripciones/$DATE
mv ../speeching/*.txt ~/transcripciones/$DATE/
echo "Procesamiento completado: $DATE"
```

Dale permisos:
```bash
chmod +x ~/speechmodel/auto-process.sh
```

Ejecutar:
```bash
./auto-process.sh
```

---

## 🆘 Troubleshooting

### API no responde
```bash
docker-compose logs speechmodel-api
docker-compose restart
```

### Sin espacio en disco
```bash
# Limpiar logs de Docker
docker system prune -a

# Limpiar archivos procesados
rm -rf ~/speechmodel/audProd/*
```

### Modelo no encontrado
```bash
# Verificar que existe
ls -lh ~/speechmodel/models/

# Re-descargar si es necesario
cd ~/speechmodel/models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

---

**¡Listo para producción! 🎉**
