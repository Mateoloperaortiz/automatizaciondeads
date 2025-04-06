#!/usr/bin/env python
"""
Script para ejecutar herramientas de linting y formateo de código.

Este script ejecuta flake8, black, mypy y pydocstyle en el código del proyecto.
Puede ejecutarse con diferentes opciones para controlar qué herramientas se ejecutan.
"""

import argparse
import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[int, str]:
    """
    Ejecuta un comando y devuelve el código de salida y la salida.

    Args:
        command: Lista con el comando y sus argumentos.
        description: Descripción del comando para mostrar.

    Returns:
        Tupla con el código de salida y la salida del comando.
    """
    print(f"\n\033[1;34m=== Ejecutando {description} ===\033[0m")
    print(f"Comando: {' '.join(command)}")
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        print(f"\033[1;31m{description} encontró problemas:\033[0m")
        print(result.stderr)
    else:
        print(f"\033[1;32m{description} completado sin problemas.\033[0m")
    
    return result.returncode, result.stdout + result.stderr


def main():
    """Función principal que ejecuta las herramientas de linting según los argumentos."""
    parser = argparse.ArgumentParser(description="Ejecutar herramientas de linting y formateo")
    parser.add_argument("--flake8", action="store_true", help="Ejecutar flake8")
    parser.add_argument("--black", action="store_true", help="Ejecutar black")
    parser.add_argument("--black-fix", action="store_true", help="Ejecutar black con --write")
    parser.add_argument("--mypy", action="store_true", help="Ejecutar mypy")
    parser.add_argument("--pydocstyle", action="store_true", help="Ejecutar pydocstyle")
    parser.add_argument("--all", action="store_true", help="Ejecutar todas las herramientas")
    parser.add_argument("--fix", action="store_true", help="Arreglar problemas cuando sea posible")
    parser.add_argument("--path", default="adflux", help="Ruta a analizar (default: adflux)")
    
    args = parser.parse_args()
    
    # Si no se especifica ninguna herramienta, ejecutar todas
    if not (args.flake8 or args.black or args.black_fix or args.mypy or args.pydocstyle or args.all):
        args.all = True
    
    exit_codes = []
    
    # Ejecutar flake8
    if args.flake8 or args.all:
        code, _ = run_command(["flake8", args.path], "flake8")
        exit_codes.append(code)
    
    # Ejecutar black
    if args.black or args.all:
        black_args = ["black", "--check"]
        if args.fix or args.black_fix:
            black_args = ["black"]
        black_args.append(args.path)
        
        code, _ = run_command(black_args, "black")
        exit_codes.append(code)
    
    # Ejecutar mypy
    if args.mypy or args.all:
        code, _ = run_command(["mypy", args.path], "mypy")
        exit_codes.append(code)
    
    # Ejecutar pydocstyle
    if args.pydocstyle or args.all:
        code, _ = run_command(["pydocstyle", args.path], "pydocstyle")
        exit_codes.append(code)
    
    # Resumen
    print("\n\033[1;34m=== Resumen ===\033[0m")
    if all(code == 0 for code in exit_codes):
        print("\033[1;32mTodas las verificaciones pasaron correctamente.\033[0m")
        return 0
    else:
        print("\033[1;31mAlgunas verificaciones fallaron. Revisa los mensajes anteriores.\033[0m")
        return 1


if __name__ == "__main__":
    sys.exit(main())
