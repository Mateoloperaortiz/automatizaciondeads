from flask_restx import Namespace, Resource, fields, reqparse
from ..schemas import candidate_schema, candidates_schema  # Asumiendo que los esquemas existen
from ..services.candidate_service import CandidateService  # Importar el servicio de candidatos
from flask import current_app
from ..api.common.excepciones import ErrorValidacion
from ..api.common.error_handling import manejar_error_api

# Namespace para Candidatos
candidates_ns = Namespace("candidates", description="Operaciones de Candidatos")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
candidate_model = candidates_ns.model(
    "Candidate",
    {
        "id": fields.Integer(readonly=True, description="El identificador único del candidato"),
        "first_name": fields.String(required=True, description="Nombre del candidato"),
        "last_name": fields.String(required=True, description="Apellido del candidato"),
        "email": fields.String(
            required=True, description="Dirección de correo electrónico del candidato"
        ),
        "phone": fields.String(description="Número de teléfono del candidato"),
        "resume_url": fields.String(description="URL al currículum del candidato"),
        "linkedin_profile": fields.String(description="URL al perfil de LinkedIn"),
    },
)

# --- Analizadores de Argumentos ---
candidate_list_parser = reqparse.RequestParser()
candidate_list_parser.add_argument(
    "page", type=int, location="args", default=1, help="Número de página"
)
candidate_list_parser.add_argument(
    "per_page", type=int, location="args", default=10, help="Elementos por página"
)
candidate_list_parser.add_argument(
    "query", type=str, location="args", help="Término de búsqueda"
)
candidate_list_parser.add_argument(
    "sort_by", type=str, location="args", default="name", help="Campo para ordenar"
)
candidate_list_parser.add_argument(
    "sort_order", type=str, location="args", default="asc", help="Orden (asc/desc)"
)
candidate_list_parser.add_argument(
    "segment", type=str, location="args", help="Filtro por segmento"
)


# --- Recursos de Candidatos ---
@candidates_ns.route("/")
class CandidateListResource(Resource):
    @candidates_ns.doc("list_candidates", parser=candidate_list_parser)
    @candidates_ns.marshal_list_with(candidate_model)
    def get(self):
        """Listar todos los candidatos"""
        args = candidate_list_parser.parse_args()
        
        candidates, pagination = CandidateService.get_candidates(
            page=args["page"],
            per_page=args["per_page"],
            query=args.get("query", ""),
            sort_by=args.get("sort_by", "name"),
            sort_order=args.get("sort_order", "asc"),
            segment_filter=args.get("segment")
        )
        
        return candidates_schema.dump(candidates), 200, {"X-Total-Count": pagination.total}

    @candidates_ns.doc("create_candidate")
    @candidates_ns.expect(candidate_model, validate=True)
    @candidates_ns.marshal_with(candidate_model, code=201)
    def post(self):
        """Crear un nuevo candidato"""
        try:
            candidate_data = candidate_schema.load(candidates_ns.payload)
        except Exception as e:
            error = ErrorValidacion(
                mensaje="La validación del payload de entrada falló",
                errores=str(e),
                codigo=400
            )
            return manejar_error_api(error)

        candidate, message, status_code = CandidateService.create_candidate(candidate_data)
        
        if status_code != 201:
            return {"message": message}, status_code
            
        return candidate_schema.dump(candidate), 201


@candidates_ns.route("/<string:candidate_id>")
@candidates_ns.param("candidate_id", "El identificador del candidato")
@candidates_ns.response(404, "Candidato no encontrado")
class CandidateResource(Resource):
    @candidates_ns.doc("get_candidate")
    @candidates_ns.marshal_with(candidate_model)
    def get(self, candidate_id):
        """Obtener un candidato dado su identificador"""
        candidate = CandidateService.get_candidate_by_id(candidate_id)
        
        if not candidate:
            from ..api.common.excepciones import ErrorRecursoNoEncontrado
            error = ErrorRecursoNoEncontrado(
                recurso="Candidato",
                identificador=candidate_id
            )
            return manejar_error_api(error)
            
        return candidate_schema.dump(candidate)

    @candidates_ns.doc("update_candidate")
    @candidates_ns.expect(candidate_model)
    @candidates_ns.marshal_with(candidate_model)
    def put(self, candidate_id):
        """Actualizar un candidato"""
        try:
            candidate_data = candidate_schema.load(candidates_ns.payload, partial=True)
        except Exception as e:
            error = ErrorValidacion(
                mensaje="La validación del payload de entrada falló",
                errores=str(e),
                codigo=400
            )
            return manejar_error_api(error)

        candidate, message, status_code = CandidateService.update_candidate(candidate_id, candidate_data)
        
        if status_code != 200:
            return {"message": message}, status_code
            
        return candidate_schema.dump(candidate)

    @candidates_ns.doc("delete_candidate")
    @candidates_ns.response(204, "Candidato eliminado")
    def delete(self, candidate_id):
        """Eliminar un candidato"""
        success, message, status_code = CandidateService.delete_candidate(candidate_id)
        
        if not success:
            from ..api.common.excepciones import AdFluxError
            error = AdFluxError(
                mensaje=message,
                codigo=status_code
            )
            return manejar_error_api(error)
            
        return "", 204
