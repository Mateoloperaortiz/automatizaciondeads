"""
Rutas MVC para candidatos en AdFlux.

Este módulo define las rutas HTTP relacionadas con candidatos
utilizando el patrón MVC (Modelo-Vista-Controlador).
"""

from flask import Blueprint, current_app

from ..controllers import CandidateController
from ..services import CandidateService


def create_candidate_mvc_routes() -> Blueprint:
    """
    Crea un Blueprint con las rutas MVC para candidatos.
    
    Returns:
        Blueprint con las rutas para candidatos
    """
    candidate_bp = Blueprint('candidate_mvc', __name__, url_prefix='/mvc/candidates')
    
    # Crear servicio y controlador
    candidate_service = CandidateService()
    candidate_controller = CandidateController(candidate_service)
    
    # Definir rutas
    @candidate_bp.route('/', methods=['GET'])
    def get_candidates():
        """Obtiene una lista paginada de candidatos."""
        return candidate_controller.get_candidates()
    
    @candidate_bp.route('/<int:candidate_id>', methods=['GET'])
    def get_candidate(candidate_id):
        """Obtiene un candidato por su ID."""
        return candidate_controller.get_candidate(candidate_id)
    
    @candidate_bp.route('/', methods=['POST'])
    def create_candidate():
        """Crea un nuevo candidato."""
        return candidate_controller.create_candidate()
    
    @candidate_bp.route('/<int:candidate_id>', methods=['PUT'])
    def update_candidate(candidate_id):
        """Actualiza un candidato existente."""
        return candidate_controller.update_candidate(candidate_id)
    
    @candidate_bp.route('/<int:candidate_id>', methods=['DELETE'])
    def delete_candidate(candidate_id):
        """Elimina un candidato existente."""
        return candidate_controller.delete_candidate(candidate_id)
    
    return candidate_bp
