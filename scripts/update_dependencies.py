#!/usr/bin/env python3
"""
Script para actualizar dependencias de AdFlux.

Este script actualiza las dependencias de AdFlux a las últimas versiones seguras,
verificando que no haya vulnerabilidades conocidas.
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple


# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('update_dependencies.log')
    ]
)
logger = logging.getLogger(__name__)


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """
    Ejecuta un comando y devuelve su salida.
    
    Args:
        command: Comando a ejecutar
        
    Returns:
        Tupla con (código de salida, salida estándar, salida de error)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    
    except Exception as e:
        logger.error(f"Error al ejecutar comando {' '.join(command)}: {str(e)}")
        return 1, '', str(e)


def get_outdated_packages() -> List[Dict[str, str]]:
    """
    Obtiene la lista de paquetes desactualizados.
    
    Returns:
        Lista de paquetes desactualizados
    """
    logger.info("Obteniendo paquetes desactualizados...")
    
    # Ejecutar pip list --outdated --format=json
    returncode, stdout, stderr = run_command([
        sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'
    ])
    
    if returncode != 0:
        logger.error(f"Error al obtener paquetes desactualizados: {stderr}")
        return []
    
    try:
        outdated = json.loads(stdout)
        logger.info(f"Se encontraron {len(outdated)} paquetes desactualizados")
        return outdated
    
    except json.JSONDecodeError:
        logger.error(f"Error al parsear resultado de pip list: {stdout}")
        return []


def check_package_vulnerabilities(package: str, version: str) -> bool:
    """
    Verifica si un paquete tiene vulnerabilidades conocidas.
    
    Args:
        package: Nombre del paquete
        version: Versión del paquete
        
    Returns:
        True si el paquete tiene vulnerabilidades, False en caso contrario
    """
    logger.info(f"Verificando vulnerabilidades para {package}=={version}...")
    
    # Ejecutar safety check
    returncode, stdout, stderr = run_command([
        'safety', 'check', '--json', '--full-report', f"{package}=={version}"
    ])
    
    if returncode != 0:
        try:
            safety_results = json.loads(stdout)
            vulnerabilities = safety_results.get('vulnerabilities', [])
            
            if vulnerabilities:
                logger.warning(f"Se encontraron {len(vulnerabilities)} vulnerabilidades en {package}=={version}")
                return True
        
        except json.JSONDecodeError:
            logger.error(f"Error al parsear resultados de safety: {stdout}")
    
    return False


def update_package(package: str, version: Optional[str] = None) -> bool:
    """
    Actualiza un paquete a la versión especificada o a la última versión.
    
    Args:
        package: Nombre del paquete
        version: Versión a instalar (opcional)
        
    Returns:
        True si la actualización fue exitosa, False en caso contrario
    """
    # Construir comando
    if version:
        logger.info(f"Actualizando {package} a la versión {version}...")
        command = [sys.executable, '-m', 'pip', 'install', '--upgrade', f"{package}=={version}"]
    else:
        logger.info(f"Actualizando {package} a la última versión...")
        command = [sys.executable, '-m', 'pip', 'install', '--upgrade', package]
    
    # Ejecutar comando
    returncode, stdout, stderr = run_command(command)
    
    if returncode != 0:
        logger.error(f"Error al actualizar {package}: {stderr}")
        return False
    
    logger.info(f"Paquete {package} actualizado correctamente")
    return True


def update_requirements_file(requirements_file: str) -> bool:
    """
    Actualiza el archivo de requisitos con las versiones actuales.
    
    Args:
        requirements_file: Ruta del archivo de requisitos
        
    Returns:
        True si la actualización fue exitosa, False en caso contrario
    """
    logger.info(f"Actualizando archivo de requisitos {requirements_file}...")
    
    # Ejecutar pip freeze
    returncode, stdout, stderr = run_command([
        sys.executable, '-m', 'pip', 'freeze'
    ])
    
    if returncode != 0:
        logger.error(f"Error al obtener paquetes instalados: {stderr}")
        return False
    
    try:
        # Leer archivo de requisitos actual
        with open(requirements_file, 'r') as f:
            current_requirements = f.readlines()
        
        # Obtener paquetes instalados
        installed_packages = {}
        for line in stdout.splitlines():
            if '==' in line:
                package, version = line.split('==', 1)
                installed_packages[package.lower()] = version
        
        # Actualizar versiones en el archivo de requisitos
        new_requirements = []
        for line in current_requirements:
            line = line.strip()
            
            # Ignorar líneas vacías y comentarios
            if not line or line.startswith('#'):
                new_requirements.append(line)
                continue
            
            # Procesar requisito
            if '==' in line:
                package, _ = line.split('==', 1)
                package = package.strip().lower()
                
                if package in installed_packages:
                    new_requirements.append(f"{package}=={installed_packages[package]}")
                else:
                    new_requirements.append(line)
            else:
                new_requirements.append(line)
        
        # Guardar archivo actualizado
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(new_requirements) + '\n')
        
        logger.info(f"Archivo de requisitos {requirements_file} actualizado correctamente")
        return True
    
    except Exception as e:
        logger.error(f"Error al actualizar archivo de requisitos: {str(e)}")
        return False


def main() -> int:
    """
    Función principal.
    
    Returns:
        Código de salida
    """
    # Parsear argumentos
    parser = argparse.ArgumentParser(description='Actualización de dependencias para AdFlux')
    parser.add_argument('--requirements', '-r', default='requirements.txt',
                       help='Archivo de requisitos')
    parser.add_argument('--check-only', '-c', action='store_true',
                       help='Solo verificar paquetes desactualizados sin actualizarlos')
    parser.add_argument('--skip-vulnerable', '-s', action='store_true',
                       help='Omitir paquetes con vulnerabilidades conocidas')
    args = parser.parse_args()
    
    # Verificar que el archivo de requisitos existe
    if not os.path.isfile(args.requirements):
        logger.error(f"Archivo de requisitos {args.requirements} no encontrado")
        return 1
    
    # Obtener paquetes desactualizados
    outdated_packages = get_outdated_packages()
    
    if not outdated_packages:
        logger.info("No hay paquetes desactualizados")
        return 0
    
    # Mostrar paquetes desactualizados
    logger.info("Paquetes desactualizados:")
    for package in outdated_packages:
        logger.info(f"  {package['name']} {package['version']} -> {package['latest_version']}")
    
    # Si solo se quiere verificar, terminar aquí
    if args.check_only:
        return 0
    
    # Actualizar paquetes
    updated_packages = []
    skipped_packages = []
    
    for package in outdated_packages:
        name = package['name']
        current_version = package['version']
        latest_version = package['latest_version']
        
        # Verificar vulnerabilidades si se especificó --skip-vulnerable
        if args.skip_vulnerable and check_package_vulnerabilities(name, latest_version):
            logger.warning(f"Omitiendo {name} debido a vulnerabilidades conocidas")
            skipped_packages.append(name)
            continue
        
        # Actualizar paquete
        if update_package(name, latest_version):
            updated_packages.append(name)
    
    # Actualizar archivo de requisitos
    if updated_packages:
        update_requirements_file(args.requirements)
    
    # Mostrar resumen
    logger.info(f"Paquetes actualizados: {len(updated_packages)}")
    logger.info(f"Paquetes omitidos: {len(skipped_packages)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
