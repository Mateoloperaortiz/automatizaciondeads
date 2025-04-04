from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, Application, JobOpening, Candidate # Importar modelos necesarios
from ..schemas import application_schema, applications_schema # Asumiendo que los esquemas existen
from ..extensions import csrf # Import csrf extension

# Namespace para Aplicaciones
applications_ns = Namespace('applications', description='Operaciones de Aplicación')

# --- Modelos Reutilizables para Documentación API (Swagger) ---
application_model = applications_ns.model('Application', {
    'id': fields.Integer(readonly=True, description='El identificador único de la aplicación'),
    'job_id': fields.String(required=True, description='ID del puesto de trabajo al que se aplica (e.g., JOB-0001)'),
    'candidate_id': fields.String(required=True, description='ID del candidato que aplica (e.g., CAND-00001)'),
    'application_date': fields.Date(readonly=True, description='Fecha en que se envió la aplicación'),
    'status': fields.String(default='received', description='Estado de la aplicación (ej., recibido, cribado, entrevista, ofertado, rechazado, contratado)'),
    'notes': fields.String(description='Notas internas sobre la aplicación')
})

# --- Analizadores de Argumentos ---
application_list_parser = reqparse.RequestParser()
application_list_parser.add_argument('page', type=int, location='args', default=1, help='Número de página')
application_list_parser.add_argument('per_page', type=int, location='args', default=10, help='Elementos por página')
application_list_parser.add_argument('job_id', type=int, location='args', help='Filtrar por ID de puesto')
application_list_parser.add_argument('candidate_id', type=int, location='args', help='Filtrar por ID de candidato')
application_list_parser.add_argument('status', type=str, location='args', help='Filtrar por estado')

# --- Recursos de Aplicación ---
@applications_ns.route('/')
class ApplicationListResource(Resource):
    # Apply decorators to all methods in this Resource
    decorators = [csrf.exempt]

    @applications_ns.doc('list_applications', parser=application_list_parser)
    @applications_ns.marshal_list_with(application_model)
    def get(self):
        """Listar todas las aplicaciones"""
        args = application_list_parser.parse_args()
        query = Application.query
        if args['job_id']:
            query = query.filter_by(job_id=args['job_id'])
        if args['candidate_id']:
            query = query.filter_by(candidate_id=args['candidate_id'])
        if args['status']:
            query = query.filter_by(status=args['status'])

        pagination = query.paginate(page=args['page'], per_page=args['per_page'], error_out=False)
        return applications_schema.dump(pagination.items), 200, {'X-Total-Count': pagination.total}

    @applications_ns.doc('create_application')
    @applications_ns.expect(application_model, validate=True)
    # @applications_ns.marshal_with(application_model, code=201) # We will handle marshalling manually on success
    def post(self):
        """Crear una nueva aplicación"""
        try:
            # 1. Load and validate input using schema
            # Consider specifying expected fields: only=('job_id', 'candidate_id', 'status', 'notes')
            # Provide the db session for validation/deserialization involving db lookups
            app_data = application_schema.load(applications_ns.payload, session=db.session)
        except Exception as e: # Typically ValidationError from Marshmallow
            # Return Marshmallow validation errors
            return {'message': 'Input payload validation failed', 'errors': getattr(e, 'messages', str(e))}, 400

        # 2. Check if job and candidate exist (using attribute access on the loaded Application instance)
        job = JobOpening.query.get(app_data.job_id)
        candidate = Candidate.query.get(app_data.candidate_id)
        if not job or not candidate:
            return {'message': 'JobOpening or Candidate not found for the provided IDs',
                    'details': f"Job ID: {app_data.job_id}, Candidate ID: {app_data.candidate_id}"}, 404

        # 3. Check for duplicate application (using attribute access)
        existing = Application.query.filter_by(job_id=app_data.job_id, candidate_id=app_data.candidate_id).first()
        if existing:
             return {'message': 'Candidate has already applied to this job opening'}, 409 # Conflict

        # 4. Create Application object explicitly and handle potential errors
        # Since app_data is already an instance, we can just add it, but let's be sure
        # it has everything set correctly. Re-creating might be safer if load() did partial loading.
        # Let's stick with using the loaded instance directly now that we know what it is.
        try:
            # The app_data object *is* the new_application instance already due to load_instance=True
            # We just need to add and commit it.
            new_application = app_data 

            # 5. Add to session and commit
            db.session.add(new_application)
            db.session.commit()

            # 6. Return the created object, marshalled manually, with 201 status
            # Use the *committed* instance for marshalling to get IDs etc.
            return application_schema.dump(new_application), 201

        except Exception as e:
            db.session.rollback() # Rollback on error during creation/commit
            # Log the internal error
            from flask import current_app
            current_app.logger.error(f"Error creating application record in database: {e}", exc_info=True)
            # Return a generic server error message
            return {'message': 'Internal server error while creating application record.'}, 500

@applications_ns.route('/<int:application_id>')
@applications_ns.param('application_id', 'El identificador de la aplicación')
@applications_ns.response(404, 'Aplicación no encontrada')
class ApplicationResource(Resource):
    @applications_ns.doc('get_application')
    @applications_ns.marshal_with(application_model)
    def get(self, application_id):
        """Obtener una aplicación dado su identificador"""
        application = Application.query.get_or_404(application_id)
        return application_schema.dump(application)

    @applications_ns.doc('update_application')
    @applications_ns.expect(application_model)
    @applications_ns.marshal_with(application_model)
    def put(self, application_id):
        """Actualizar una aplicación (ej., cambiar estado)"""
        application = Application.query.get_or_404(application_id)
        try:
            # Solo permitir actualizar ciertos campos como estado, notas
            update_data = application_schema.load(applications_ns.payload, partial=True,
                                                  only=('status', 'notes'))
        except Exception as e:
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        for key, value in update_data.items():
            setattr(application, key, value)

        db.session.commit()
        return application_schema.dump(application)

    @applications_ns.doc('delete_application')
    @applications_ns.response(204, 'Aplicación eliminada')
    def delete(self, application_id):
        """Eliminar una aplicación"""
        application = Application.query.get_or_404(application_id)
        db.session.delete(application)
        db.session.commit()
        return '', 204
