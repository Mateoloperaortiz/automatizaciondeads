"""
Constantes globales para la aplicación AdFlux.

Este módulo contiene constantes que se utilizan en toda la aplicación.
"""

# Mapeo de segmentos
SEGMENT_MAP = {
    0: "Segmento A",
    1: "Segmento B",
    2: "Segmento C",
    3: "Segmento D",
    4: "Segmento E",
    # Añadir más segmentos según sea necesario
}

# Colores para los segmentos
SEGMENT_COLORS = {
    0: "bg-blue-100 text-blue-800",
    1: "bg-green-100 text-green-800",
    2: "bg-yellow-100 text-yellow-800",
    3: "bg-purple-100 text-purple-800",
    4: "bg-pink-100 text-pink-800",
    # Añadir más colores según sea necesario
}

# Valor predeterminado para segmentos desconocidos
DEFAULT_SEGMENT_NAME = "Unknown"
DEFAULT_SEGMENT_COLOR = "bg-gray-100 text-gray-800"

# Estados de campaña estandarizados
CAMPAIGN_STATUS = {
    "DRAFT": "Draft",
    "PENDING": "Pending",
    "ACTIVE": "Active",
    "PAUSED": "Paused",
    "PUBLISHED": "Active",  # Mapear 'PUBLISHED' a 'Active' para consistencia
    "COMPLETED": "Completed",
    "ARCHIVED": "Archived",
    "REJECTED": "Rejected",
    "DELETED": "Deleted",
    "FAILED": "Failed",
}

# Colores para los estados de campaña
CAMPAIGN_STATUS_COLORS = {
    "Draft": "bg-gray-100 text-gray-800",
    "Pending": "bg-yellow-100 text-yellow-800",
    "Active": "bg-green-100 text-green-800",
    "Paused": "bg-blue-100 text-blue-800",
    "Completed": "bg-purple-100 text-purple-800",
    "Archived": "bg-gray-100 text-gray-800",
    "Rejected": "bg-red-100 text-red-800",
    "Deleted": "bg-red-100 text-red-800",
    "Failed": "bg-red-100 text-red-800",
}
