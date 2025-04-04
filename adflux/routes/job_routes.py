from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, JobOpening, Candidate # Importar modelos necesarios
from ..schemas import job_schema, jobs_schema # Asumiendo que los esquemas existen

# Namespace para Puestos
jobs_ns = Namespace('jobs', description='Operaciones de Ofertas de Empleo')

# --- Modelos Reutilizables para Documentación API (Swagger) ---
job_model = jobs_ns.model('JobOpening', {
    'job_id': fields.String(readonly=True, description='El identificador único del puesto (ej., JOB-0001)'),
    'title': fields.String(required=True, description='Título del puesto'),
    'description': fields.String(required=True, description='Descripción del puesto'),
    'location': fields.String(description='Ubicación del puesto'),
    'company': fields.String(description='Nombre de la empresa'),
    'required_skills': fields.List(fields.String, description='Lista de habilidades requeridas'),
    'salary_min': fields.Integer(description='Salario mínimo'),
    'salary_max': fields.Integer(description='Salario máximo'),
    'posted_date': fields.Date(description='Fecha en que se publicó el puesto'),
    'status': fields.String(default='open', description='Estado del puesto (ej., abierto, cerrado, cubierto)'),
    'target_segments': fields.List(fields.Integer, readonly=True, description='Lista de IDs de segmentos de candidatos objetivo')
})

# Modelo para el cuerpo de la solicitud de publicación de anuncios de Meta
publish_meta_ad_model = jobs_ns.model('PublishMetaAdRequest', {
    'ad_account_id': fields.String(required=True, description='ID de la cuenta publicitaria de Meta (ej., act_XXXXXXXX)'),
    'page_id': fields.String(required=True, description='ID de la página de Facebook para asociar con el anuncio'),
    'campaign_name': fields.String(required=True, description='Nombre para la nueva campaña de Meta'),
    'campaign_objective': fields.String(required=True, default='LINK_CLICKS', description='Objetivo de la campaña de Meta (ej., LINK_CLICKS, CONVERSIONS)'),
    'ad_set_name': fields.String(required=True, description='Nombre para el nuevo conjunto de anuncios de Meta'),
    'daily_budget_cents': fields.Integer(required=True, description='Presupuesto diario para el conjunto de anuncios en céntimos (ej., 500 para $5.00)'),
    'targeting_country_code': fields.String(required=True, default='US', description='Código de país ISO 3166-1 alfa-2 para la segmentación (ej., US, CA, GB)'),
    'ad_creative_name': fields.String(required=True, description='Nombre para el nuevo creativo del anuncio'),
    'ad_message': fields.String(required=True, description='El texto/mensaje principal para el creativo del anuncio'),
    'ad_link_url': fields.String(required=True, description='La URL de destino para el anuncio (ej., enlace a la solicitud de empleo)'),
    'ad_name': fields.String(required=True, description='Nombre para el nuevo anuncio de Meta'),
    'image_hash': fields.String(required=False, description='Opcional: Hash de imagen de una imagen pre-subida para el creativo del anuncio'),
    'image_local_path': fields.String(required=False, description='Opcional: Ruta local a un archivo de imagen para subir y usar (ej., images/image1.png)')
    # Añadir campos opcionales como image_hash, link_title, start/end times más tarde si es necesario
})

# --- Analizadores de Argumentos ---
job_list_parser = reqparse.RequestParser()
job_list_parser.add_argument('page', type=int, location='args', default=1, help='Número de página')
job_list_parser.add_argument('per_page', type=int, location='args', default=10, help='Elementos por página')
job_list_parser.add_argument('status', type=str, location='args', default='open', help='Filtrar por estado')

# --- Recursos de Puestos ---
@jobs_ns.route('/') # Ruta dentro del namespace
class JobListResource(Resource):
    @jobs_ns.doc('list_jobs', parser=job_list_parser)
    @jobs_ns.marshal_list_with(job_model)
    def get(self):
        """Listar todas las ofertas de empleo"""
        args = job_list_parser.parse_args()
        query = JobOpening.query
        if args['status']:
            query = query.filter_by(status=args['status'])

        pagination = query.paginate(page=args['page'], per_page=args['per_page'], error_out=False)
        # Usar esquema Marshmallow para la serialización real
        return jobs_schema.dump(pagination.items), 200, {'X-Total-Count': pagination.total}

    @jobs_ns.doc('create_job')
    @jobs_ns.expect(job_model, validate=True)
    @jobs_ns.marshal_with(job_model, code=201)
    def post(self):
        """Crear una nueva oferta de empleo"""
        # Usar esquema Marshmallow para deserialización y validación
        try:
            job_data = job_schema.load(jobs_ns.payload)
        except Exception as e: # Reemplazar con error específico de validación de Marshmallow
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        new_job = JobOpening(**job_data)
        db.session.add(new_job)
        db.session.commit()
        # Usar esquema Marshmallow para la serialización de la respuesta
        return job_schema.dump(new_job), 201

@jobs_ns.route('/<int:job_id>')
@jobs_ns.param('job_id', 'El identificador del puesto')
@jobs_ns.response(404, 'Puesto no encontrado')
class JobResource(Resource):
    @jobs_ns.doc('get_job')
    @jobs_ns.marshal_with(job_model)
    def get(self, job_id):
        """Obtener una oferta de empleo dado su identificador"""
        job = JobOpening.query.get_or_404(job_id)
        return job_schema.dump(job)

    @jobs_ns.doc('update_job')
    @jobs_ns.expect(job_model)
    @jobs_ns.marshal_with(job_model)
    def put(self, job_id):
        """Actualizar una oferta de empleo"""
        job = JobOpening.query.get_or_404(job_id)
        try:
            job_data = job_schema.load(jobs_ns.payload, partial=True) # Permitir actualizaciones parciales
        except Exception as e:
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        for key, value in job_data.items():
            setattr(job, key, value)

        db.session.commit()
        return job_schema.dump(job)

    @jobs_ns.doc('delete_job')
    @jobs_ns.response(204, 'Puesto eliminado')
    def delete(self, job_id):
        """Eliminar una oferta de empleo"""
        job = JobOpening.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return '', 204

# --- Endpoint de Publicación de Anuncios de Meta ---
@jobs_ns.route('/<string:job_id>/publish-meta-ad') # Usar job_id de tipo string del modelo
@jobs_ns.param('job_id', 'El identificador del puesto (ej., JOB-0001)')
class JobPublishMetaAdResource(Resource):
    @jobs_ns.doc('publish_meta_ad_for_job')
    @jobs_ns.expect(publish_meta_ad_model, validate=True)
    # Actualizar códigos de respuesta y descripciones para tarea asíncrona
    @jobs_ns.response(202, 'Tarea de creación de estructura de Meta aceptada.')
    @jobs_ns.response(400, 'Solicitud Incorrecta / Error de Validación')
    @jobs_ns.response(404, 'Puesto no encontrado')
    @jobs_ns.response(500, 'Error al enviar la tarea')
    def post(self, job_id):
        """Desencadena una tarea asíncrona para crear la estructura de la campaña de Meta para una oferta de empleo específica."""
        # 0. Importar la tarea Celery
        from ..tasks import async_create_meta_structure_for_job
        from flask import current_app # Para logging

        # 1. Verificar que el Puesto Existe (Verificación rápida antes de encolar la tarea)
        job_exists = JobOpening.query.filter_by(job_id=job_id).count() > 0
        if not job_exists:
            return {'message': f'Puesto con ID {job_id} no encontrado.'}, 404

        # 2. Obtener Payload (Esto se pasa directamente a la tarea)
        payload = jobs_ns.payload
        # La validación básica puede ocurrir aquí, pero la validación detallada debería estar en la tarea
        # Por ejemplo, verificar las claves requeridas para la tarea misma
        required_keys = [
            'ad_account_id', 'page_id', 'campaign_name', 'ad_set_name',
            'daily_budget_cents', 'ad_creative_name', 'ad_message',
            'ad_link_url', 'ad_name'
        ]
        missing_keys = [k for k in required_keys if k not in payload]
        if missing_keys:
             return {'message': f'Faltan campos requeridos en el payload: {missing_keys}'}, 400

        # 3. Desencadenar Tarea Celery
        try:
            current_app.logger.info(f"Enviando tarea de creación de estructura de Meta para el ID de Puesto: {job_id}")
            # Pasar el job_id y el diccionario completo del payload a la tarea
            task = async_create_meta_structure_for_job.delay(job_id=job_id, params=payload)
            current_app.logger.info(f"Tarea {task.id} enviada para el ID de Puesto: {job_id}")
            # Devolver 202 Aceptado
            return {
                'message': 'Tarea de creación de estructura de Meta aceptada.',
                'task_id': task.id
            }, 202
        except Exception as e:
            current_app.logger.error(f"Error al enviar la tarea para el puesto {job_id}: {e}", exc_info=True)
            return {'message': 'Error al enviar la tarea a la cola.'}, 500
