#!/usr/bin/env node

/**
 * Script para optimizar imágenes.
 * 
 * Este script optimiza todas las imágenes en el directorio de imágenes estáticas,
 * reduciendo su tamaño sin pérdida significativa de calidad.
 * 
 * Uso:
 *   node scripts/optimize_images.js [--quality=80] [--webp] [--avif]
 * 
 * Opciones:
 *   --quality=N    Calidad de compresión (1-100, por defecto: 80)
 *   --webp         Generar versiones WebP de las imágenes
 *   --avif         Generar versiones AVIF de las imágenes
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const glob = promisify(require('glob'));
const sharp = require('sharp');
const chalk = require('chalk');
const ora = require('ora');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parsear argumentos
const argv = yargs(hideBin(process.argv))
  .option('quality', {
    alias: 'q',
    type: 'number',
    description: 'Calidad de compresión (1-100)',
    default: 80
  })
  .option('webp', {
    type: 'boolean',
    description: 'Generar versiones WebP',
    default: false
  })
  .option('avif', {
    type: 'boolean',
    description: 'Generar versiones AVIF',
    default: false
  })
  .help()
  .alias('help', 'h')
  .argv;

// Configuración
const config = {
  quality: Math.min(Math.max(argv.quality, 1), 100),
  generateWebP: argv.webp,
  generateAVIF: argv.avif,
  inputDir: path.resolve(__dirname, '../adflux/static/src/images'),
  outputDir: path.resolve(__dirname, '../adflux/static/dist/images')
};

// Asegurar que el directorio de salida existe
if (!fs.existsSync(config.outputDir)) {
  fs.mkdirSync(config.outputDir, { recursive: true });
}

// Función para optimizar una imagen
async function optimizeImage(inputPath, outputPath, options = {}) {
  const { quality, format } = options;
  
  try {
    // Crear instancia de sharp
    let image = sharp(inputPath);
    
    // Obtener metadatos
    const metadata = await image.metadata();
    
    // Determinar formato de salida
    let outputFormat = format || metadata.format;
    let outputQuality = quality || config.quality;
    
    // Configurar opciones según formato
    switch (outputFormat) {
      case 'jpeg':
      case 'jpg':
        image = image.jpeg({ quality: outputQuality, progressive: true });
        break;
      case 'png':
        image = image.png({ quality: outputQuality, progressive: true });
        break;
      case 'webp':
        image = image.webp({ quality: outputQuality });
        break;
      case 'avif':
        image = image.avif({ quality: outputQuality });
        break;
      default:
        // Mantener formato original
        break;
    }
    
    // Guardar imagen optimizada
    await image.toFile(outputPath);
    
    // Obtener tamaños de archivo
    const inputSize = fs.statSync(inputPath).size;
    const outputSize = fs.statSync(outputPath).size;
    const savings = ((1 - outputSize / inputSize) * 100).toFixed(2);
    
    return {
      path: outputPath,
      format: outputFormat,
      width: metadata.width,
      height: metadata.height,
      inputSize,
      outputSize,
      savings
    };
  } catch (error) {
    console.error(`Error al optimizar ${inputPath}:`, error);
    throw error;
  }
}

// Función principal
async function main() {
  console.log(chalk.blue('=== Optimizador de Imágenes ==='));
  console.log(chalk.gray(`Calidad: ${config.quality}%`));
  console.log(chalk.gray(`WebP: ${config.generateWebP ? 'Sí' : 'No'}`));
  console.log(chalk.gray(`AVIF: ${config.generateAVIF ? 'Sí' : 'No'}`));
  console.log(chalk.gray(`Directorio de entrada: ${config.inputDir}`));
  console.log(chalk.gray(`Directorio de salida: ${config.outputDir}`));
  console.log();
  
  // Buscar todas las imágenes
  const spinner = ora('Buscando imágenes...').start();
  const imageFiles = await glob('**/*.{jpg,jpeg,png,gif,svg}', { cwd: config.inputDir });
  spinner.succeed(`Encontradas ${imageFiles.length} imágenes`);
  
  if (imageFiles.length === 0) {
    console.log(chalk.yellow('No se encontraron imágenes para optimizar.'));
    return;
  }
  
  // Estadísticas
  let totalInputSize = 0;
  let totalOutputSize = 0;
  let totalImages = 0;
  let failedImages = 0;
  
  // Procesar cada imagen
  for (const [index, file] of imageFiles.entries()) {
    const inputPath = path.join(config.inputDir, file);
    const outputPath = path.join(config.outputDir, file);
    const outputDir = path.dirname(outputPath);
    
    // Asegurar que el directorio de salida existe
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Mostrar progreso
    spinner.start(`Optimizando ${index + 1}/${imageFiles.length}: ${file}`);
    
    try {
      // Optimizar imagen original
      const result = await optimizeImage(inputPath, outputPath);
      
      totalInputSize += result.inputSize;
      totalOutputSize += result.outputSize;
      totalImages++;
      
      // Generar versión WebP si está habilitado
      if (config.generateWebP && !file.endsWith('.svg') && !file.endsWith('.webp')) {
        const webpPath = outputPath.replace(/\.(jpg|jpeg|png|gif)$/i, '.webp');
        await optimizeImage(inputPath, webpPath, { format: 'webp' });
      }
      
      // Generar versión AVIF si está habilitado
      if (config.generateAVIF && !file.endsWith('.svg') && !file.endsWith('.avif')) {
        const avifPath = outputPath.replace(/\.(jpg|jpeg|png|gif)$/i, '.avif');
        await optimizeImage(inputPath, avifPath, { format: 'avif' });
      }
      
      spinner.succeed(`Optimizado ${file} (${result.savings}% reducción)`);
    } catch (error) {
      spinner.fail(`Error al optimizar ${file}`);
      failedImages++;
    }
  }
  
  // Mostrar resumen
  console.log();
  console.log(chalk.green('=== Resumen ==='));
  console.log(`Imágenes procesadas: ${totalImages}/${imageFiles.length}`);
  console.log(`Imágenes fallidas: ${failedImages}`);
  
  if (totalImages > 0) {
    const totalSavings = ((1 - totalOutputSize / totalInputSize) * 100).toFixed(2);
    const inputSizeMB = (totalInputSize / 1024 / 1024).toFixed(2);
    const outputSizeMB = (totalOutputSize / 1024 / 1024).toFixed(2);
    const savedMB = (totalInputSize - totalOutputSize) / 1024 / 1024;
    
    console.log(`Tamaño original: ${inputSizeMB} MB`);
    console.log(`Tamaño optimizado: ${outputSizeMB} MB`);
    console.log(chalk.green(`Ahorro total: ${savedMB.toFixed(2)} MB (${totalSavings}%)`));
  }
}

// Ejecutar script
main().catch(error => {
  console.error(chalk.red('Error:'), error);
  process.exit(1);
});
