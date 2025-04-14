#!/usr/bin/env python3
"""
Script para análisis de vulnerabilidades en AdFlux.

Este script realiza análisis de seguridad en el código y dependencias de AdFlux,
detectando posibles vulnerabilidades y problemas de seguridad.
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('security_scan.log')
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


def check_dependencies() -> bool:
    """
    Verifica que las dependencias necesarias estén instaladas.
    
    Returns:
        True si todas las dependencias están instaladas, False en caso contrario
    """
    dependencies = [
        ('safety', ['safety', '--version']),
        ('bandit', ['bandit', '--version']),
        ('pip-audit', ['pip-audit', '--version']),
        ('semgrep', ['semgrep', '--version'])
    ]
    
    all_installed = True
    
    for name, command in dependencies:
        returncode, stdout, stderr = run_command(command)
        
        if returncode != 0:
            logger.error(f"Dependencia {name} no instalada")
            all_installed = False
        else:
            logger.info(f"Dependencia {name} instalada: {stdout.strip()}")
    
    return all_installed


def scan_dependencies() -> Dict[str, Any]:
    """
    Escanea dependencias en busca de vulnerabilidades.
    
    Returns:
        Resultados del escaneo
    """
    logger.info("Escaneando dependencias...")
    
    # Escanear con safety
    safety_returncode, safety_stdout, safety_stderr = run_command([
        'safety', 'check', '--json', '--full-report'
    ])
    
    # Escanear con pip-audit
    pip_audit_returncode, pip_audit_stdout, pip_audit_stderr = run_command([
        'pip-audit', '--format', 'json'
    ])
    
    # Procesar resultados
    safety_vulnerabilities = []
    pip_audit_vulnerabilities = []
    
    if safety_returncode == 0:
        logger.info("No se encontraron vulnerabilidades con safety")
    else:
        try:
            safety_results = json.loads(safety_stdout)
            safety_vulnerabilities = safety_results.get('vulnerabilities', [])
            logger.warning(f"Se encontraron {len(safety_vulnerabilities)} vulnerabilidades con safety")
        except json.JSONDecodeError:
            logger.error(f"Error al parsear resultados de safety: {safety_stdout}")
    
    if pip_audit_returncode == 0:
        logger.info("No se encontraron vulnerabilidades con pip-audit")
    else:
        try:
            pip_audit_results = json.loads(pip_audit_stdout)
            pip_audit_vulnerabilities = pip_audit_results.get('vulnerabilities', [])
            logger.warning(f"Se encontraron {len(pip_audit_vulnerabilities)} vulnerabilidades con pip-audit")
        except json.JSONDecodeError:
            logger.error(f"Error al parsear resultados de pip-audit: {pip_audit_stdout}")
    
    return {
        'safety': {
            'vulnerabilities': safety_vulnerabilities,
            'returncode': safety_returncode,
            'stdout': safety_stdout,
            'stderr': safety_stderr
        },
        'pip_audit': {
            'vulnerabilities': pip_audit_vulnerabilities,
            'returncode': pip_audit_returncode,
            'stdout': pip_audit_stdout,
            'stderr': pip_audit_stderr
        }
    }


def scan_code() -> Dict[str, Any]:
    """
    Escanea código en busca de vulnerabilidades.
    
    Returns:
        Resultados del escaneo
    """
    logger.info("Escaneando código...")
    
    # Escanear con bandit
    bandit_returncode, bandit_stdout, bandit_stderr = run_command([
        'bandit', '-r', 'adflux', '-f', 'json'
    ])
    
    # Escanear con semgrep
    semgrep_returncode, semgrep_stdout, semgrep_stderr = run_command([
        'semgrep', '--config', 'p/python', '--config', 'p/flask', '--config', 'p/security-audit',
        '--json', 'adflux'
    ])
    
    # Procesar resultados
    bandit_issues = []
    semgrep_issues = []
    
    if bandit_returncode == 0:
        logger.info("No se encontraron problemas con bandit")
    else:
        try:
            bandit_results = json.loads(bandit_stdout)
            bandit_issues = bandit_results.get('results', [])
            logger.warning(f"Se encontraron {len(bandit_issues)} problemas con bandit")
        except json.JSONDecodeError:
            logger.error(f"Error al parsear resultados de bandit: {bandit_stdout}")
    
    if semgrep_returncode == 0:
        logger.info("No se encontraron problemas con semgrep")
    else:
        try:
            semgrep_results = json.loads(semgrep_stdout)
            semgrep_issues = semgrep_results.get('results', [])
            logger.warning(f"Se encontraron {len(semgrep_issues)} problemas con semgrep")
        except json.JSONDecodeError:
            logger.error(f"Error al parsear resultados de semgrep: {semgrep_stdout}")
    
    return {
        'bandit': {
            'issues': bandit_issues,
            'returncode': bandit_returncode,
            'stdout': bandit_stdout,
            'stderr': bandit_stderr
        },
        'semgrep': {
            'issues': semgrep_issues,
            'returncode': semgrep_returncode,
            'stdout': semgrep_stdout,
            'stderr': semgrep_stderr
        }
    }


def generate_report(dependency_results: Dict[str, Any], code_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera un informe con los resultados del escaneo.
    
    Args:
        dependency_results: Resultados del escaneo de dependencias
        code_results: Resultados del escaneo de código
        
    Returns:
        Informe generado
    """
    logger.info("Generando informe...")
    
    # Contar vulnerabilidades
    safety_vulnerabilities = dependency_results['safety']['vulnerabilities']
    pip_audit_vulnerabilities = dependency_results['pip_audit']['vulnerabilities']
    bandit_issues = code_results['bandit']['issues']
    semgrep_issues = code_results['semgrep']['issues']
    
    # Generar informe
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_vulnerabilities': len(safety_vulnerabilities) + len(pip_audit_vulnerabilities),
            'total_code_issues': len(bandit_issues) + len(semgrep_issues),
            'safety_vulnerabilities': len(safety_vulnerabilities),
            'pip_audit_vulnerabilities': len(pip_audit_vulnerabilities),
            'bandit_issues': len(bandit_issues),
            'semgrep_issues': len(semgrep_issues)
        },
        'dependency_scan': dependency_results,
        'code_scan': code_results
    }
    
    return report


def save_report(report: Dict[str, Any], output_file: str) -> None:
    """
    Guarda el informe en un archivo.
    
    Args:
        report: Informe a guardar
        output_file: Ruta del archivo de salida
    """
    logger.info(f"Guardando informe en {output_file}...")
    
    try:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Informe guardado en {output_file}")
    
    except Exception as e:
        logger.error(f"Error al guardar informe: {str(e)}")


def main() -> int:
    """
    Función principal.
    
    Returns:
        Código de salida
    """
    # Parsear argumentos
    parser = argparse.ArgumentParser(description='Análisis de vulnerabilidades para AdFlux')
    parser.add_argument('--output', '-o', default='security_report.json',
                       help='Archivo de salida para el informe')
    args = parser.parse_args()
    
    # Verificar dependencias
    if not check_dependencies():
        logger.error("Faltan dependencias, instalando...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'safety', 'bandit', 'pip-audit', 'semgrep'])
    
    # Escanear dependencias
    dependency_results = scan_dependencies()
    
    # Escanear código
    code_results = scan_code()
    
    # Generar informe
    report = generate_report(dependency_results, code_results)
    
    # Guardar informe
    save_report(report, args.output)
    
    # Determinar código de salida
    if report['summary']['total_vulnerabilities'] > 0 or report['summary']['total_code_issues'] > 0:
        logger.warning(
            f"Se encontraron {report['summary']['total_vulnerabilities']} vulnerabilidades y "
            f"{report['summary']['total_code_issues']} problemas de código"
        )
        return 1
    
    logger.info("No se encontraron vulnerabilidades ni problemas de código")
    return 0


if __name__ == '__main__':
    sys.exit(main())
