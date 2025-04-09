from flask_restx import Namespace, Resource, fields, reqparse
from ..schemas import candidate_schema, candidates_schema
from ..services.candidate_service import CandidateService
from flask import current_app, request
from ..api.common.excepciones import ErrorValidacion, ErrorRecursoNoEncontrado, AdFluxError
from ..api.common.error_handling import manejar_error_api

# Namespace para Candidatos
candidates_ns = Namespace("candidates", description="Operaciones de Candidatos")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
candidate_model = candidates_ns.model(
    "Candidate",
    {
        "candidate_id": fields.String(readonly=True, description="El ID único del candidato (ej. CAND-0001)"),
        "name": fields.String(required=True, description="Nombre completo del candidato"),
        "email": fields.String(required=False, description="Correo electrónico"),
        "phone": fields.String(description="Número de teléfono"),
        "location": fields.String(description="Ubicación"),
        "years_experience": fields.Integer(description="Años de experiencia"),
        "education_level": fields.String(description="Nivel de educación"),
        "primary_skill": fields.String(description="Habilidad principal"),
        "desired_salary": fields.Integer(description="Salario deseado"),
        "desired_position": fields.String(description="Cargo deseado"),
        "summary": fields.String(description="Resumen profesional"),
        "availability": fields.String(description="Disponibilidad"),
        "skills": fields.List(fields.String, description="Lista de habilidades"),
        "languages": fields.List(fields.String, description="Lista de idiomas"),
        "job_id": fields.String(description="ID del trabajo asociado (ej. JOB-0001)", attribute="job.job_id"),
        "segment_id": fields.Integer(description="ID del segmento de ML asignado"),
        "created_at": fields.DateTime(readonly=True, description="Fecha de creación"),
        "updated_at": fields.DateTime(readonly=True, description="Fecha de última actualización"),
    },
)

# --- Analizadores de Argumentos ---
candidate_list_parser = reqparse.RequestParser()
candidate_list_parser.add_argument("page", type=int, location="args", default=1, help="Número de página")
candidate_list_parser.add_argument("per_page", type=int, location="args", default=10, help="Elementos por página")
candidate_list_parser.add_argument("query", type=str, location="args", help="Término de búsqueda")
candidate_list_parser.add_argument("sort_by", type=str, location="args", default="name", help="Campo para ordenar")
candidate_list_parser.add_argument("sort_order", type=str, location="args", default="asc", help="Orden (asc/desc)")
candidate_list_parser.add_argument("segment", type=str, location="args", help="Filtro por segmento (ID)")

# --- Recursos de Candidatos ---
@candidates_ns.route("/")
class CandidateListResource(Resource):
    @candidates_ns.doc("list_candidates", parser=candidate_list_parser)
    @candidates_ns.response(200, "Lista de candidatos obtenida", [candidate_model])
    def get(self):
        """Listar todos los candidatos usando CandidateService"""
        args = candidate_list_parser.parse_args()
        try:
            if args['page'] < 1:
                 raise ErrorValidacion(mensaje="El número de página debe ser >= 1")
            if args['per_page'] < 1 or args['per_page'] > 100:
                 raise ErrorValidacion(mensaje="per_page debe estar entre 1 y 100")

            candidates, pagination = CandidateService.get_candidates(
                page=args["page"],
                per_page=args["per_page"],
                query=args.get("query", ""),
                sort_by=args.get("sort_by", "name"),
                sort_order=args.get("sort_order", "asc"),
                segment_filter=args.get("segment")
            )

            result = candidates_schema.dump(candidates)
            headers = {
                 "X-Total-Count": pagination.total,
                 "X-Page": pagination.page,
                 "X-Per-Page": pagination.per_page,
                 "X-Total-Pages": pagination.pages,
            }
            return result, 200, headers

        except ErrorValidacion as e:
             return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al listar candidatos: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al listar candidatos", codigo=500)
            return manejar_error_api(error)

    @candidates_ns.doc("create_candidate")
    @candidates_ns.expect(candidate_model, validate=True)
    @candidates_ns.response(201, "Candidato creado", candidate_model)
    @candidates_ns.response(400, "Error de validación")
    def post(self):
        """Crear un nuevo candidato usando CandidateService"""
        try:
            candidate_data = candidate_schema.load(request.json)
        except Exception as e:
            error = ErrorValidacion(mensaje="Validación de payload fallida", errores=str(e))
            return manejar_error_api(error)

        try:
            candidate, message, status_code = CandidateService.create_candidate(candidate_data)
            return candidate_schema.dump(candidate), 201
        except (ErrorValidacion, AdFluxError) as e:
             return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al crear candidato: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al crear candidato", codigo=500)
            return manejar_error_api(error)


@candidates_ns.route("/<string:candidate_id>")
@candidates_ns.param("candidate_id", "El identificador del candidato (ej. CAND-0001)")
@candidates_ns.response(404, "Candidato no encontrado")
class CandidateResource(Resource):
    @candidates_ns.doc("get_candidate")
    @candidates_ns.response(200, "Detalles del candidato", candidate_model)
    def get(self, candidate_id):
        """Obtener un candidato por su ID usando CandidateService"""
        try:
            candidate = CandidateService.get_candidate_by_id(candidate_id)
            return candidate_schema.dump(candidate), 200
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al obtener candidato {candidate_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor", codigo=500)
            return manejar_error_api(error)

    @candidates_ns.doc("update_candidate")
    @candidates_ns.expect(candidate_model)
    @candidates_ns.response(200, "Candidato actualizado", candidate_model)
    @candidates_ns.response(400, "Error de validación")
    def put(self, candidate_id):
        """Actualizar un candidato usando CandidateService"""
        try:
            candidate_data = candidate_schema.load(request.json, partial=True)
            if not candidate_data:
                raise ErrorValidacion(mensaje="Payload JSON vacío o faltante para actualizar.")
        except Exception as e:
            error = ErrorValidacion(mensaje="Validación de payload fallida", errores=str(e))
            return manejar_error_api(error)

        try:
            candidate, message, status_code = CandidateService.update_candidate(candidate_id, candidate_data)
            return candidate_schema.dump(candidate), 200
        except (ErrorValidacion, ErrorRecursoNoEncontrado, AdFluxError) as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al actualizar candidato {candidate_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al actualizar candidato", codigo=500)
            return manejar_error_api(error)

    @candidates_ns.doc("delete_candidate")
    @candidates_ns.response(204, "Candidato eliminado")
    def delete(self, candidate_id):
        """Eliminar un candidato usando CandidateService"""
        try:
            success, message, status_code = CandidateService.delete_candidate(candidate_id)
            if not success:
                 raise AdFluxError(mensaje=message or "Error al eliminar candidato", codigo=status_code or 500)
            return "", 204
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except AdFluxError as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al eliminar candidato {candidate_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al eliminar candidato", codigo=500)
            return manejar_error_api(error)
