"""
Utilidad para cargar variables de entorno desde archivos .env y .envrc.

Este módulo proporciona funciones para cargar variables de entorno desde
archivos .env y .envrc, permitiendo compatibilidad con ambos formatos.
"""

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def load_env_files(base_dir=None, override=True):
    """
    Carga variables de entorno desde archivos .env y .envrc.
    
    Intenta cargar primero desde .env y luego desde .envrc si el primero
    no existe. Si ambos existen, carga ambos con prioridad para .env
    a menos que override=False.
    
    Args:
        base_dir (str): Directorio base donde buscar los archivos.
                        Si es None, usa el directorio actual.
        override (bool): Si es True, las variables ya definidas serán sobrescritas.
                         Si es False, las variables existentes no serán modificadas.
    
    Returns:
        bool: True si al menos un archivo fue cargado, False en caso contrario.
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    env_path = os.path.join(base_dir, '.env')
    envrc_path = os.path.join(base_dir, '.envrc')
    
    env_loaded = False
    envrc_loaded = False
    
    if os.path.exists(env_path):
        load_dotenv(env_path, override=override)
        env_loaded = True
        logger.debug(f"Variables de entorno cargadas desde {env_path}")
    
    if os.path.exists(envrc_path):
        try:
            with open(envrc_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('export '):
                            line = line[7:]
                        
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            if override or key not in os.environ:
                                os.environ[key] = value
            
            envrc_loaded = True
            logger.debug(f"Variables de entorno cargadas desde {envrc_path}")
        except Exception as e:
            logger.error(f"Error cargando variables desde {envrc_path}: {e}")
    
    if not env_loaded and not envrc_loaded:
        logger.warning(f"No se encontraron archivos .env o .envrc en {base_dir}")
        return False
    
    return True
