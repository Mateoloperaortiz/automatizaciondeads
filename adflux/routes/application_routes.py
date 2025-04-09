from flask_restx import Namespace, Resource, fields, reqparse
from ..schemas import application_schema, applications_schema
from ..extensions import csrf
from ..services.application_service import ApplicationService
from flask import current_app, request
from ..api.common.excepciones import AdFluxError, ErrorValidacion, ErrorRecursoNoEncontrado
from ..api.common.error_handling import manejar_error_api

# Namespace para Aplicaciones
applications_ns = Namespace("applications", description="Operaciones de Aplicación")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
application_model = applications_ns.model(
    "Application",
    {
        "application_id": fields.Integer(readonly=True, description="El identificador único de la aplicación"),
        "job_id": fields.String(required=True, description="ID del puesto aplicado (ej., JOB-0001)", attribute="job.job_id"),
        "candidate_id": fields.String(required=True, description="ID del candidato (ej., CAND-00001)", attribute="candidate.candidate_id"),
        "application_date": fields.Date(readonly=True, description="Fecha de envío"),
        "status": fields.String(required=True, description="Estado actual (pending, approved, rejected, withdrawn, etc.)"),
        "notes": fields.String(description="Notas internas"),
        "created_at": fields.DateTime(readonly=True, description="Fecha de creación del registro"),
        "updated_at": fields.DateTime(readonly=True, description="Fecha de última actualización del registro"),
        "candidate_name": fields.String(readonly=True, attribute="candidate.name", description="Nombre del candidato"),
        "job_title": fields.String(readonly=True, attribute="job.title", description="Título del puesto"),
    },
)

# --- Analizadores de Argumentos ---
application_list_parser = reqparse.RequestParser()
application_list_parser.add_argument("page", type=int, location="args", default=1, help="Número de página")
application_list_parser.add_argument("per_page", type=int, location="args", default=10, help="Elementos por página")
application_list_parser.add_argument("job_id", type=str, location="args", help="Filtrar por ID de puesto (ej. JOB-0001)")
application_list_parser.add_argument("candidate_id", type=str, location="args", help="Filtrar por ID de candidato (ej. CAND-0001)")
application_list_parser.add_argument("status", type=str, location="args", help="Filtrar por estado")

# --- Recursos de Aplicación ---
@applications_ns.route("/")
class ApplicationListResource(Resource):
    decorators = [csrf.exempt]

    @applications_ns.doc("list_applications", parser=application_list_parser)
    @applications_ns.response(200, "Lista de aplicaciones", [application_model])
    def get(self):
        """Listar todas las aplicaciones usando ApplicationService"""
        args = application_list_parser.parse_args()
        try:
            if args['page'] < 1:
                 raise ErrorValidacion(mensaje="El número de página debe ser >= 1")
            if args['per_page'] < 1 or args['per_page'] > 100:
                 raise ErrorValidacion(mensaje="per_page debe estar entre 1 y 100")

            applications, pagination = ApplicationService.get_applications(
                page=args["page"],
                per_page=args["per_page"],
                job_id=args["job_id"],
                candidate_id=args["candidate_id"],
                status=args["status"]
            )

            result = applications_schema.dump(applications)
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
            current_app.logger.error(f"Error inesperado al listar aplicaciones: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al listar aplicaciones", codigo=500)
            return manejar_error_api(error)

    @applications_ns.doc("create_application")
    @applications_ns.expect(application_model, validate=True)
    @applications_ns.response(201, "Aplicación creada", application_model)
    @applications_ns.response(400, "Error de validación")
    def post(self):
        """Crear una nueva aplicación usando ApplicationService"""
        try:
            application_data = application_schema.load(request.json)
        except Exception as e:
            error = ErrorValidacion(mensaje="Validación de payload fallida", errores=str(e))
            return manejar_error_api(error)

        try:
            application, message, status_code = ApplicationService.create_application(application_data)
            return application_schema.dump(application), 201
        except (ErrorValidacion, ErrorRecursoNoEncontrado, AdFluxError) as e:
             return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al crear aplicación: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al crear aplicación", codigo=500)
            return manejar_error_api(error)

@applications_ns.route("/<int:application_id>")
@applications_ns.param("application_id", "El identificador de la aplicación")
@applications_ns.response(404, "Aplicación no encontrada")
class ApplicationResource(Resource):
    @applications_ns.doc("get_application")
    @applications_ns.response(200, "Detalles de la aplicación", application_model)
    def get(self, application_id):
        """Obtener una aplicación por su ID usando ApplicationService"""
        try:
            application = ApplicationService.get_application_by_id(application_id)
            return application_schema.dump(application), 200
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al obtener aplicación {application_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor", codigo=500)
            return manejar_error_api(error)

    @applications_ns.doc("update_application")
    @applications_ns.expect(application_model)
    @applications_ns.response(200, "Aplicación actualizada", application_model)
    @applications_ns.response(400, "Error de validación")
    def put(self, application_id):
        """Actualizar una aplicación (estado/notas) usando ApplicationService"""
        try:
            update_data = application_schema.load(request.json, partial=True, unknown='exclude', only=("status", "notes"))
            if not update_data:
                 raise ErrorValidacion(mensaje="Payload vacío o sin campos actualizables (status, notes).")
        except Exception as e:
            error = ErrorValidacion(mensaje="Validación de payload fallida", errores=str(e))
            return manejar_error_api(error)

        try:
            application, message, status_code = ApplicationService.update_application(application_id, update_data)
            return application_schema.dump(application), 200
        except (ErrorValidacion, ErrorRecursoNoEncontrado, AdFluxError) as e:
             return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al actualizar aplicación {application_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al actualizar aplicación", codigo=500)
            return manejar_error_api(error)

    @applications_ns.doc("delete_application")
    @applications_ns.response(204, "Aplicación eliminada")
    def delete(self, application_id):
        """Eliminar una aplicación usando ApplicationService"""
        try:
            success, message, status_code = ApplicationService.delete_application(application_id)
            if not success:
                 raise AdFluxError(mensaje=message or "Error al eliminar aplicación", codigo=status_code or 500)
            return "", 204
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except AdFluxError as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al eliminar aplicación {application_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al eliminar aplicación", codigo=500)
            return manejar_error_api(error)
