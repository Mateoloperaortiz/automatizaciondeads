#!/usr/bin/env python3
"""
Script para ejecutar pruebas de AdFlux.

Este script proporciona una interfaz para ejecutar diferentes tipos de pruebas
y generar informes de cobertura.
"""

import os
import sys
import argparse
import subprocess
from typing import List, Optional


def run_command(command: List[str]) -> int:
    """
    Ejecuta un comando y devuelve su código de salida.
    
    Args:
        command: Comando a ejecutar
        
    Returns:
        Código de salida
    """
    print(f"Ejecutando: {' '.join(command)}")
    return subprocess.call(command)


def run_tests(args: argparse.Namespace) -> int:
    """
    Ejecuta pruebas según los argumentos proporcionados.
    
    Args:
        args: Argumentos de línea de comandos
        
    Returns:
        Código de salida
    """
    # Construir comando base
    command = [sys.executable, '-m', 'pytest']
    
    # Añadir opciones según argumentos
    if args.verbose:
        command.append('-v')
    
    if args.quiet:
        command.append('-q')
    
    if args.failfast:
        command.append('-x')
    
    if args.coverage:
        command.extend(['--cov=adflux', '--cov-report=term', '--cov-report=html'])
    
    # Añadir marcadores según tipo de prueba
    if args.unit:
        command.append('-m unit')
    elif args.integration:
        command.append('-m integration')
    elif args.functional:
        command.append('-m functional')
    elif args.security:
        command.append('-m security')
    elif args.performance:
        command.append('-m performance')
    
    # Añadir directorio o archivo específico
    if args.path:
        command.append(args.path)
    
    # Ejecutar comando
    return run_command(command)


def main() -> int:
    """
    Función principal.
    
    Returns:
        Código de salida
    """
    # Parsear argumentos
    parser = argparse.ArgumentParser(description='Ejecutar pruebas de AdFlux')
    
    # Opciones generales
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar salida detallada')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Mostrar salida mínima')
    parser.add_argument('--failfast', '-x', action='store_true',
                       help='Detener pruebas al primer fallo')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Generar informe de cobertura')
    parser.add_argument('--path', '-p', type=str,
                       help='Directorio o archivo específico de pruebas')
    
    # Tipos de pruebas
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--unit', '-u', action='store_true',
                      help='Ejecutar pruebas unitarias')
    group.add_argument('--integration', '-i', action='store_true',
                      help='Ejecutar pruebas de integración')
    group.add_argument('--functional', '-f', action='store_true',
                      help='Ejecutar pruebas funcionales')
    group.add_argument('--security', '-s', action='store_true',
                      help='Ejecutar pruebas de seguridad')
    group.add_argument('--performance', '-p', action='store_true',
                      help='Ejecutar pruebas de rendimiento')
    group.add_argument('--all', '-a', action='store_true',
                      help='Ejecutar todas las pruebas')
    
    args = parser.parse_args()
    
    # Ejecutar pruebas
    return run_tests(args)


if __name__ == '__main__':
    sys.exit(main())
