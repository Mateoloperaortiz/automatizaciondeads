from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, JobOpening, Candidate  # Mantener para tipos?
from ..schemas import job_schema, jobs_schema
from flask import current_app, request # Añadir request
from ..api.common.excepciones import AdFluxError, ErrorValidacion, ErrorRecursoNoEncontrado, ErrorBaseDatos # Asegurar ErrorBaseDatos
from ..api.common.error_handling import manejar_error_api

# Importar el servicio
from ..services.job_service import JobService

# Instanciar el servicio
job_service = JobService()

# Namespace para Puestos
jobs_ns = Namespace("jobs", description="Operaciones de Ofertas de Empleo")

# --- Modelos Reutilizables para Documentación API (Swagger) ---
job_model = jobs_ns.model(
    "JobOpening",
    {
        "job_id": fields.String(
            readonly=True, description="El identificador único del puesto (ej., JOB-0001)"
        ),
        "title": fields.String(required=True, description="Título del puesto"),
        "short_description": fields.String(description="Descripción corta"),
        "description": fields.String(description="Descripción completa"),
        "company_name": fields.String(description="Nombre de la empresa"),
        "location": fields.String(description="Ubicación del puesto"),
        "department": fields.String(description="Departamento"),
        "salary_min": fields.Integer(description="Salario mínimo"),
        "salary_max": fields.Integer(description="Salario máximo"),
        "employment_type": fields.String(description="Tipo de empleo"),
        "experience_level": fields.String(description="Nivel de experiencia"),
        "education_level": fields.String(description="Nivel de educación"),
        "posted_date": fields.Date(description="Fecha de publicación"),
        "closing_date": fields.Date(description="Fecha de cierre"),
        "status": fields.String(description="Estado del puesto (open, closed, draft)"),
        "remote": fields.Boolean(description="Indica si es trabajo remoto"),
        "required_skills": fields.List(fields.String, description="Lista de habilidades requeridas"),
        "benefits": fields.List(fields.String, description="Lista de beneficios"),
        "created_at": fields.DateTime(readonly=True, description="Fecha de creación"),
        "updated_at": fields.DateTime(readonly=True, description="Fecha de última actualización"),
    },
)

# Modelo para el cuerpo de la solicitud de publicación de anuncios de Meta
publish_meta_ad_model = jobs_ns.model(
    "PublishMetaAdRequest",
    {
        "ad_account_id": fields.String(
            required=True, description="ID de la cuenta publicitaria de Meta (ej., act_XXXXXXXX)"
        ),
        "page_id": fields.String(
            required=True, description="ID de la página de Facebook para asociar con el anuncio"
        ),
        "campaign_name": fields.String(
            required=True, description="Nombre para la nueva campaña de Meta"
        ),
        "campaign_objective": fields.String(
            required=True,
            default="LINK_CLICKS",
            description="Objetivo de la campaña de Meta (ej., LINK_CLICKS, CONVERSIONS)",
        ),
        "ad_set_name": fields.String(
            required=True, description="Nombre para el nuevo conjunto de anuncios de Meta"
        ),
        "daily_budget_cents": fields.Integer(
            required=True,
            description="Presupuesto diario para el conjunto de anuncios en céntimos (ej., 500 para $5.00)",
        ),
        "targeting_country_code": fields.String(
            required=True,
            default="US",
            description="Código de país ISO 3166-1 alfa-2 para la segmentación (ej., US, CA, GB)",
        ),
        "ad_creative_name": fields.String(
            required=True, description="Nombre para el nuevo creativo del anuncio"
        ),
        "ad_message": fields.String(
            required=True, description="El texto/mensaje principal para el creativo del anuncio"
        ),
        "ad_link_url": fields.String(
            required=True,
            description="La URL de destino para el anuncio (ej., enlace a la solicitud de empleo)",
        ),
        "ad_name": fields.String(required=True, description="Nombre para el nuevo anuncio de Meta"),
        "image_hash": fields.String(
            required=False,
            description="Opcional: Hash de imagen de una imagen pre-subida para el creativo del anuncio",
        ),
        "image_local_path": fields.String(
            required=False,
            description="Opcional: Ruta local a un archivo de imagen para subir y usar (ej., images/image1.png)",
        ),
    },
)

# --- Analizadores de Argumentos ---
job_list_parser = reqparse.RequestParser()
job_list_parser.add_argument("page", type=int, location="args", default=1, help="Número de página")
job_list_parser.add_argument(
    "per_page", type=int, location="args", default=10, help="Elementos por página"
)
job_list_parser.add_argument(
    "status", type=str, location="args", help="Filtrar por estado (open, closed, draft)"
)
job_list_parser.add_argument(
    "query", type=str, location="args", help="Término de búsqueda para título o descripción"
)
job_list_parser.add_argument(
    "sort_by", type=str, location="args", default="created_at", help="Campo para ordenar"
)
job_list_parser.add_argument(
    "sort_order", type=str, location="args", default="desc", help="Orden (asc o desc)"
)

# --- Recursos de Puestos ---
@jobs_ns.route("/")
class JobListResource(Resource):
    @jobs_ns.doc("list_jobs", parser=job_list_parser)
    @jobs_ns.response(200, "Lista de trabajos obtenida", job_model)
    def get(self):
        """Listar todas las ofertas de empleo usando JobService"""
        args = job_list_parser.parse_args()
        try:
            # Validar paginación
            if args['page'] < 1:
                 raise ErrorValidacion(mensaje="El número de página debe ser >= 1")
            if args['per_page'] < 1 or args['per_page'] > 100:
                 raise ErrorValidacion(mensaje="per_page debe estar entre 1 y 100")

            # Llamar al servicio
            jobs, pagination = JobService.get_jobs(
                page=args["page"],
                per_page=args["per_page"],
                status=args["status"],
                query=args["query"],
                sort_by=args["sort_by"],
                sort_order=args["sort_order"],
            )

            # Usar esquema Marshmallow para la serialización
            result = jobs_schema.dump(jobs)
            # Devolver metadatos de paginación en encabezados
            headers = {
                 "X-Total-Count": pagination.total,
                 "X-Page": pagination.page,
                 "X-Per-Page": pagination.per_page,
                 "X-Total-Pages": pagination.pages,
            }
            return result, 200, headers

        except (ErrorValidacion, ErrorBaseDatos) as e:
            return manejar_error_api(e)
        except Exception as e:
            # Capturar errores inesperados
            current_app.logger.error(f"Error inesperado al listar trabajos: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al listar trabajos", codigo=500)
            return manejar_error_api(error)

    @jobs_ns.doc("create_job")
    @jobs_ns.expect(job_model, validate=True)
    @jobs_ns.response(201, "Trabajo creado exitosamente", job_model)
    @jobs_ns.response(400, "Error de validación")
    @jobs_ns.response(500, "Error interno del servidor")
    def post(self):
        """Crear una nueva oferta de empleo usando JobService"""
        try:
            # La validación con Marshmallow debería hacerse en el servicio
            # para mantener la lógica de negocio allí.
            # Aquí solo pasamos el payload.
            job_data = request.json # Obtener payload JSON
            if not job_data:
                 raise ErrorValidacion(mensaje="Payload JSON vacío o faltante.")

            # Llamar al servicio para crear
            # El servicio se encarga de la validación detallada (Marshmallow) y creación
            job, message, status_code = job_service.create_job(job_data)

            # El servicio debería lanzar excepciones para errores, que se capturan abajo
            # O manejar el código de estado devuelto
            if status_code == 201:
                 return job_schema.dump(job), 201
            else:
                 # Si el servicio devuelve código de error sin lanzar excepción
                 # (se prefiere lanzar excepciones específicas)
                 raise AdFluxError(mensaje=message, codigo=status_code)

        except (ErrorValidacion, ErrorBaseDatos) as e:
             # Errores específicos lanzados por el servicio
             return manejar_error_api(e)
        except Exception as e:
             # Otros errores inesperados
             current_app.logger.error(f"Error inesperado al crear trabajo: {e}", exc_info=True)
             error = AdFluxError(mensaje="Error interno del servidor al crear trabajo", codigo=500)
             return manejar_error_api(error)


@jobs_ns.route("/<string:job_id>")
@jobs_ns.param("job_id", "El identificador del puesto (ej., JOB-0001)")
@jobs_ns.response(404, "Puesto no encontrado")
class JobResource(Resource):
    @jobs_ns.doc("get_job")
    @jobs_ns.response(200, "Detalles del trabajo", job_model)
    def get(self, job_id):
        """Obtener una oferta de empleo por su ID usando JobService"""
        try:
            job = job_service.get_job_by_id(job_id)
            # El servicio debe lanzar ErrorRecursoNoEncontrado si no existe
            return job_schema.dump(job), 200
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al obtener trabajo {job_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor", codigo=500)
            return manejar_error_api(error)

    @jobs_ns.doc("update_job")
    @jobs_ns.expect(job_model, validate=True)
    @jobs_ns.response(200, "Trabajo actualizado", job_model)
    @jobs_ns.response(400, "Error de validación")
    @jobs_ns.response(404, "Puesto no encontrado")
    def put(self, job_id):
        """Actualizar una oferta de empleo usando JobService"""
        try:
            job_data = request.json
            if not job_data:
                 raise ErrorValidacion(mensaje="Payload JSON vacío o faltante.")

            # Llamar al servicio para actualizar
            # El servicio se encarga de buscar, validar (partial) y actualizar
            updated_job, message, status_code = job_service.update_job(job_id, job_data)

            if status_code == 200:
                 return job_schema.dump(updated_job), 200
            else:
                 # Asumiendo que el servicio lanza excepciones para 404, 400, etc.
                 # Si no, manejar el código de estado aquí.
                 raise AdFluxError(mensaje=message, codigo=status_code)

        except (ErrorValidacion, ErrorRecursoNoEncontrado, ErrorBaseDatos) as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al actualizar trabajo {job_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al actualizar trabajo", codigo=500)
            return manejar_error_api(error)

    @jobs_ns.doc("delete_job")
    @jobs_ns.response(204, "Puesto eliminado")
    @jobs_ns.response(404, "Puesto no encontrado")
    def delete(self, job_id):
        """Eliminar una oferta de empleo usando JobService"""
        try:
            success, message = job_service.delete_job(job_id)
            # El servicio debe lanzar ErrorRecursoNoEncontrado si no existe
            # y devolver True/False para éxito/error genérico
            if success:
                return "", 204
            else:
                # Si el servicio no lanza excepción pero falla
                raise AdFluxError(mensaje=message or "Error al eliminar trabajo", codigo=500)
        except ErrorRecursoNoEncontrado as e:
            return manejar_error_api(e)
        except Exception as e:
            current_app.logger.error(f"Error inesperado al eliminar trabajo {job_id}: {e}", exc_info=True)
            error = AdFluxError(mensaje="Error interno del servidor al eliminar trabajo", codigo=500)
            return manejar_error_api(error)


# --- Endpoint de Publicación de Anuncios de Meta ---
@jobs_ns.route("/<string:job_id>/publish-meta-ad")
@jobs_ns.param("job_id", "El identificador del puesto (ej., JOB-0001)")
class JobPublishMetaAdResource(Resource):
    @jobs_ns.doc("publish_meta_ad_for_job")
    @jobs_ns.expect(publish_meta_ad_model, validate=True)
    @jobs_ns.response(202, "Tarea de creación de estructura de Meta aceptada.")
    @jobs_ns.response(400, "Solicitud Incorrecta / Error de Validación")
    @jobs_ns.response(404, "Puesto no encontrado")
    @jobs_ns.response(500, "Error al enviar la tarea")
    def post(self, job_id):
        """Desencadena una tarea asíncrona para crear la estructura de Meta para un trabajo."""
        from ..tasks import async_create_meta_structure_for_job

        try:
            # 1. Verificar que el Puesto Existe usando el servicio
            job_service.get_job_by_id(job_id) # Lanza ErrorRecursoNoEncontrado si no existe

            # 2. Obtener Payload y validación básica
            payload = request.json

            # 2. Validar Payload usando el servicio
            job_service.validate_meta_publish_payload(payload)

            # 3. Desencadenar Tarea Celery
            current_app.logger.info(f"Enviando tarea de creación de estructura de Meta para Job ID: {job_id}")
            task = async_create_meta_structure_for_job.delay(job_id=job_id, params=payload)
            current_app.logger.info(f"Tarea {task.id} enviada para Job ID: {job_id}")
            return {
                "message": "Tarea de creación de estructura de Meta aceptada.",
                "task_id": task.id,
            }, 202

        except (ErrorValidacion, ErrorRecursoNoEncontrado) as e:
             # Errores conocidos
             return manejar_error_api(e)
        except Exception as e:
             # Error al encolar la tarea u otro error inesperado
             current_app.logger.error(f"Error al enviar la tarea para el puesto {job_id}: {e}", exc_info=True)
             error = AdFluxError(mensaje="Error interno al enviar la tarea a la cola.", codigo=500)
             return manejar_error_api(error)
