const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const pLimitModule = require('p-limit');
// p-limit v4 en Node v22 exporta como ESM con default
const pLimit = pLimitModule.default || pLimitModule;
const cliProgress = require('cli-progress');
const colors = require('colors');

// Configuración
const API_URL = 'http://localhost:5000';
const AUD_PROD_DIR = path.join(__dirname, '..', 'audProd');
const SPEECHING_DIR = path.join(__dirname, '..', 'speeching');
const CONCURRENT_LIMIT = 1; // Solo 1 archivo a la vez (modelo ocupa 3GB RAM)
const SUPPORTED_FORMATS = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'];

// Límite de concurrencia
const limit = pLimit(CONCURRENT_LIMIT);

// Estadísticas
const stats = {
    total: 0,
    success: 0,
    failed: 0,
    skipped: 0,
    startTime: null,
    endTime: null
};

/**
 * Verifica que la API esté disponible
 */
async function checkApiHealth() {
    try {
        const response = await axios.get(`${API_URL}/health`);
        if (response.data.status === 'healthy') {
            console.log('✅ API está disponible y funcionando'.green);
            return true;
        } else {
            console.log('❌ API no está saludable'.red);
            return false;
        }
    } catch (error) {
        console.log('❌ No se puede conectar a la API'.red);
        console.log(`   Asegúrate de que el servidor esté corriendo en ${API_URL}`.yellow);
        console.log('   Comando: cd backend && python app.py'.gray);
        return false;
    }
}

/**
 * Obtiene todos los archivos de audio de audProd
 */
async function getAudioFiles() {
    try {
        await fs.ensureDir(AUD_PROD_DIR);
        const files = await fs.readdir(AUD_PROD_DIR);

        const audioFiles = files.filter(file => {
            const ext = path.extname(file).toLowerCase();
            return SUPPORTED_FORMATS.includes(ext);
        });

        return audioFiles.map(file => path.join(AUD_PROD_DIR, file));
    } catch (error) {
        console.error('❌ Error leyendo archivos:'.red, error.message);
        return [];
    }
}

/**
 * Transcribe un archivo de audio
 */
async function transcribeFile(filePath, progressBar) {
    const fileName = path.basename(filePath);
    const outputFileName = `${path.parse(fileName).name}.txt`;
    const outputPath = path.join(SPEECHING_DIR, outputFileName);

    try {
        // Verificar si ya existe la transcripción
        if (await fs.pathExists(outputPath)) {
            stats.skipped++;
            progressBar.increment();
            return {
                success: true,
                skipped: true,
                file: fileName,
                message: 'Ya existe'
            };
        }

        // Leer el archivo y enviarlo usando multipart/form-data
        const FormData = require('form-data');
        const formData = new FormData();
        const fileStream = fs.createReadStream(filePath);
        formData.append('audio', fileStream, fileName);

        // Transcribir usando el endpoint /transcribe con multipart upload
        const response = await axios.post(
            `${API_URL}/transcribe`,
            formData,
            {
                headers: formData.getHeaders(),
                timeout: 1800000, // 30 minutos timeout (para audios largos)
                maxContentLength: Infinity,
                maxBodyLength: Infinity
            }
        );

        if (response.data.success) {
            // Guardar transcripción en /speeching
            await fs.ensureDir(SPEECHING_DIR);
            await fs.writeFile(outputPath, response.data.text, 'utf-8');

            stats.success++;
            progressBar.increment();

            return {
                success: true,
                file: fileName,
                wordCount: response.data.word_count,
                language: response.data.language,
                outputPath: outputPath
            };
        } else {
            throw new Error('API no devolvió éxito');
        }

    } catch (error) {
        stats.failed++;
        progressBar.increment();

        return {
            success: false,
            file: fileName,
            error: error.message
        };
    }
}

/**
 * Procesa todos los archivos de audio
 */
async function processAllAudios() {
    console.log('\n🎤 PROCESAMIENTO EN LOTE DE TRANSCRIPCIONES'.cyan.bold);
    console.log('='.repeat(60).cyan);

    // Verificar API
    console.log('\n📌 Verificando API...'.yellow);
    const apiHealthy = await checkApiHealth();
    if (!apiHealthy) {
        process.exit(1);
    }

    // Obtener archivos
    console.log('\n📌 Buscando archivos de audio...'.yellow);
    const audioFiles = await getAudioFiles();

    if (audioFiles.length === 0) {
        console.log('⚠️  No se encontraron archivos de audio en /audProd'.yellow);
        console.log(`   Formatos soportados: ${SUPPORTED_FORMATS.join(', ')}`.gray);
        process.exit(0);
    }

    stats.total = audioFiles.length;
    console.log(`✅ Encontrados ${audioFiles.length} archivos de audio`.green);

    // Crear directorio de salida
    await fs.ensureDir(SPEECHING_DIR);

    // Configurar barra de progreso
    const progressBar = new cliProgress.SingleBar({
        format: '📊 Progreso |' + '{bar}'.cyan + '| {percentage}% | {value}/{total} archivos | {eta_formatted} restante',
        barCompleteChar: '\u2588',
        barIncompleteChar: '\u2591',
        hideCursor: true
    });

    console.log(`\n📌 Iniciando procesamiento (${CONCURRENT_LIMIT} archivos simultáneos)...`.yellow);
    console.log('');

    stats.startTime = Date.now();
    progressBar.start(audioFiles.length, 0);

    // Procesar archivos con límite de concurrencia
    const results = await Promise.all(
        audioFiles.map(file =>
            limit(() => transcribeFile(file, progressBar))
        )
    );

    progressBar.stop();
    stats.endTime = Date.now();

    // Mostrar resultados
    console.log('\n');
    console.log('='.repeat(60).cyan);
    console.log('📊 RESUMEN DE PROCESAMIENTO'.cyan.bold);
    console.log('='.repeat(60).cyan);
    console.log('');
    console.log(`   Total de archivos:     ${stats.total}`.white);
    console.log(`   ✅ Exitosos:           ${stats.success}`.green);
    console.log(`   ⏭️  Omitidos:           ${stats.skipped}`.blue);
    console.log(`   ❌ Fallidos:           ${stats.failed}`.red);
    console.log('');

    // Tiempo transcurrido
    const duration = (stats.endTime - stats.startTime) / 1000;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    console.log(`   ⏱️  Tiempo total:        ${minutes}m ${seconds}s`.gray);

    if (stats.success > 0) {
        const avgTime = duration / stats.success;
        console.log(`   📈 Promedio/archivo:   ${avgTime.toFixed(1)}s`.gray);
    }

    console.log('');

    // Mostrar archivos fallidos si los hay
    if (stats.failed > 0) {
        console.log('❌ ARCHIVOS FALLIDOS:'.red.bold);
        results
            .filter(r => !r.success)
            .forEach(r => {
                console.log(`   • ${r.file}: ${r.error}`.red);
            });
        console.log('');
    }

    // Ubicación de resultados
    console.log(`📁 Transcripciones guardadas en: ${SPEECHING_DIR}`.green);
    console.log('');
    console.log('='.repeat(60).cyan);
    console.log('');

    // Exit code basado en si hubo errores
    process.exit(stats.failed > 0 ? 1 : 0);
}

// Manejo de errores no capturados
process.on('unhandledRejection', (error) => {
    console.error('\n❌ Error no manejado:'.red, error);
    process.exit(1);
});

// Banner inicial
console.clear();
console.log('');
console.log('╔═══════════════════════════════════════════════════════════╗'.cyan);
console.log('║         🎤 SpeechModel - Procesamiento en Lote          ║'.cyan.bold);
console.log('╚═══════════════════════════════════════════════════════════╝'.cyan);

// Ejecutar
processAllAudios().catch(error => {
    console.error('\n❌ Error fatal:'.red, error);
    process.exit(1);
});
