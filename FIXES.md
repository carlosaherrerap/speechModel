# 🔧 Correcciones Aplicadas

## Problema Detectado en Logs

**Error**: `whisper.cpp falló (code -9)`

**Causa**: Procesamiento concurrente (3 archivos simultáneos) × 3GB modelo = **9GB RAM requeridos**
- El sistema mata los procesos por Out Of Memory (OOM)

## ✅ Soluciones Aplicadas

### 1. Reducida Concurrencia
**Archivo**: `frontend/transcribe-batch.js`
```javascript
const CONCURRENT_LIMIT = 1; // Antes: 3
```

**Efecto**: Procesa 1 archivo a la vez = **solo 3GB RAM** usados

### 2. Timeout Extendido  
**Archivo**: `backend/whisper_wrapper.py`
```python
timeout=3600  # 60 minutos (antes: 10 min)
```

**Efecto**: Audios largos no fallarán por timeout

## 📊 Rendimiento Esperado

**Antes** (3 concurrentes):
- ❌ OOM errors constantes
- ❌ Procesos matados

**Ahora** (1 serial):
- ✅ Sin errores de memoria
- ✅ Procesamiento estable
- ⏱️ Más lento pero confiable

### Velocidad Estimada
- **CPU**: ~2 min por minuto de audio
- **1000 archivos** de 1 min c/u: ~33 horas
- **Solución**: Dejar corriendo de noche/fin de semana

## 🔄 Próximos Pasos

1. Reinicia el contenedor (ya ejecutado)
2. Prueba de nuevo: `cd frontend && npm run start`
3. Si continúan errores, verifica RAM disponible:
   ```bash
   docker stats speechmodel-api
   ```

## 💡 Optimizaciones Futuras (Opcional)

Si necesitas más velocidad:

**Opción A: Modelo Más Pequeño**
- Usar `ggml-medium` en vez de `large-v3`
- Menos preciso pero 3x más rápido
- Solo ocupa ~1.5GB RAM

**Opción B: GPU en Servidor**
- En servidor con GPU NVIDIA
- 10-20x más rápido
- Procesar 1000 archivos en ~3-6 horas

**Opción C: Más RAM**
- Con 16GB+ RAM puedes volver a `CONCURRENT_LIMIT = 3`
