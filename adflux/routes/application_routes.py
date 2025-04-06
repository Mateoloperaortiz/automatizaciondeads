from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, Application  # Importar modelos necesarios
from ..schemas import application_schema, applications_schema  # Asumiendo que los esquemas existen
from ..extensions import csrf  # Import csrf extension
from ..services.application_service import ApplicationService  # Importar servicio de aplicaciones

# Namespace para Aplicaciones
applications_ns = Namespace("applications", description="Operaciones de Aplicación")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
application_model = applications_ns.model(
    "Application",
    {
        "id": fields.Integer(readonly=True, description="El identificador único de la aplicación"),
        "job_id": fields.String(
            required=True, description="ID del puesto de trabajo al que se aplica (e.g., JOB-0001)"
        ),
        "candidate_id": fields.String(
            required=True, description="ID del candidato que aplica (e.g., CAND-00001)"
        ),
        "application_date": fields.Date(
            readonly=True, description="Fecha en que se envió la aplicación"
        ),
        "status": fields.String(
            default="received",
            description="Estado de la aplicación (ej., recibido, cribado, entrevista, ofertado, rechazado, contratado)",
        ),
        "notes": fields.String(description="Notas internas sobre la aplicación"),
    },
)

# --- Analizadores de Argumentos ---
application_list_parser = reqparse.RequestParser()
application_list_parser.add_argument(
    "page", type=int, location="args", default=1, help="Número de página"
)
application_list_parser.add_argument(
    "per_page", type=int, location="args", default=10, help="Elementos por página"
)
application_list_parser.add_argument(
    "job_id", type=int, location="args", help="Filtrar por ID de puesto"
)
application_list_parser.add_argument(
    "candidate_id", type=int, location="args", help="Filtrar por ID de candidato"
)
application_list_parser.add_argument("status", type=str, location="args", help="Filtrar por estado")


# --- Recursos de Aplicación ---
@applications_ns.route("/")
class ApplicationListResource(Resource):
    # Apply decorators to all methods in this Resource
    decorators = [csrf.exempt]

    @applications_ns.doc("list_applications", parser=application_list_parser)
    @applications_ns.marshal_list_with(application_model)
    def get(self):
        """Listar todas las aplicaciones"""
        args = application_list_parser.parse_args()
        
        applications, pagination = ApplicationService.get_applications(
            page=args["page"],
            per_page=args["per_page"],
            job_id=args["job_id"],
            candidate_id=args["candidate_id"],
            status=args["status"]
        )
        
        return applications_schema.dump(applications), 200, {"X-Total-Count": pagination.total}

    @applications_ns.doc("create_application")
    @applications_ns.expect(application_model, validate=True)
    def post(self):
        """Crear una nueva aplicación"""
        try:
            application_data = application_schema.load(applications_ns.payload)
        except Exception as e:
            return {
                "message": "La validación del payload de entrada falló",
                "errors": getattr(e, "messages", str(e)),
            }, 400

        application, message, status_code = ApplicationService.create_application(application_data)
        
        if status_code != 201:
            return {"message": message}, status_code
            
        return application_schema.dump(application), 201


@applications_ns.route("/<int:application_id>")
@applications_ns.param("application_id", "El identificador de la aplicación")
@applications_ns.response(404, "Aplicación no encontrada")
class ApplicationResource(Resource):
    @applications_ns.doc("get_application")
    @applications_ns.marshal_with(application_model)
    def get(self, application_id):
        """Obtener una aplicación dado su identificador"""
        application = ApplicationService.get_application_by_id(application_id)
        if not application:
            applications_ns.abort(404, f"Aplicación con ID {application_id} no encontrada")
        return application_schema.dump(application)

    @applications_ns.doc("update_application")
    @applications_ns.expect(application_model)
    @applications_ns.marshal_with(application_model)
    def put(self, application_id):
        """Actualizar una aplicación (ej., cambiar estado)"""
        try:
            # Solo permitir actualizar ciertos campos como estado, notas
            update_data = application_schema.load(
                applications_ns.payload, partial=True, only=("status", "notes")
            )
        except Exception as e:
            return {"message": "La validación del payload de entrada falló", "errors": str(e)}, 400

        application, message, status_code = ApplicationService.update_application(
            application_id, update_data
        )
        
        if status_code != 200:
            applications_ns.abort(status_code, message)
            
        return application_schema.dump(application)

    @applications_ns.doc("delete_application")
    @applications_ns.response(204, "Aplicación eliminada")
    def delete(self, application_id):
        """Eliminar una aplicación"""
        success, message, status_code = ApplicationService.delete_application(application_id)
        
        if not success:
            applications_ns.abort(status_code, message)
            
        return "", 204
