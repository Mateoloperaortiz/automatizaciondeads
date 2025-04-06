"""
Paquete de simulación de datos para AdFlux.

Este paquete contiene todas las funcionalidades relacionadas con la simulación de datos
utilizadas por AdFlux, organizadas en módulos específicos según su funcionalidad.
"""

# Importar funciones de generación de trabajos
from .job_data import (
    generate_job_opening,
    generate_multiple_jobs
)

# Importar funciones de generación de candidatos
from .candidate_data import (
    generate_candidate_profile,
    generate_multiple_candidates
)

# Importar funciones de generación de aplicaciones
from .application_data import (
    generate_simulated_applications
)

# Importar funciones de utilidades
from .utils import (
    setup_gemini_client,
    generate_with_gemini
)

# Para mantener compatibilidad con el código existente
__all__ = [
    # Generación de trabajos
    'generate_job_opening',
    'generate_multiple_jobs',
    
    # Generación de candidatos
    'generate_candidate_profile',
    'generate_multiple_candidates',
    
    # Generación de aplicaciones
    'generate_simulated_applications',
    
    # Utilidades
    'setup_gemini_client',
    'generate_with_gemini'
]
