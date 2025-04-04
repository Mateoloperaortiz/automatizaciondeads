from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, Application, JobOpening, Candidate # Importar modelos necesarios
from ..schemas import application_schema, applications_schema # Asumiendo que los esquemas existen

# Namespace para Aplicaciones
applications_ns = Namespace('applications', description='Operaciones de Aplicación')

# --- Modelos Reutilizables para Documentación API (Swagger) ---
application_model = applications_ns.model('Application', {
    'id': fields.Integer(readonly=True, description='El identificador único de la aplicación'),
    'job_id': fields.Integer(required=True, description='ID del puesto de trabajo al que se aplica'),
    'candidate_id': fields.Integer(required=True, description='ID del candidato que aplica'),
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
    @applications_ns.marshal_with(application_model, code=201)
    def post(self):
        """Crear una nueva aplicación"""
        try:
            app_data = application_schema.load(applications_ns.payload)
        except Exception as e:
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        # Verificar que el puesto y el candidato existen
        job = JobOpening.query.get(app_data['job_id'])
        candidate = Candidate.query.get(app_data['candidate_id'])
        if not job or not candidate:
            return {'message': 'Puesto o Candidato no encontrado'}, 404

        # ¿Verificar aplicación duplicada?
        existing = Application.query.filter_by(job_id=app_data['job_id'], candidate_id=app_data['candidate_id']).first()
        if existing:
             return {'message': 'El candidato ya ha aplicado a este puesto'}, 409

        new_application = Application(**app_data)
        db.session.add(new_application)
        db.session.commit()
        return application_schema.dump(new_application), 201

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
