from flask_restx import Namespace, Resource, fields, reqparse
from ..models import db, Candidate # Importar modelos necesarios
from ..schemas import candidate_schema, candidates_schema # Asumiendo que los esquemas existen

# Namespace para Candidatos
candidates_ns = Namespace('candidates', description='Operaciones de Candidatos')

# --- Modelos Reutilizables para Documentación API (Swagger) ---
candidate_model = candidates_ns.model('Candidate', {
    'id': fields.Integer(readonly=True, description='El identificador único del candidato'),
    'first_name': fields.String(required=True, description='Nombre del candidato'),
    'last_name': fields.String(required=True, description='Apellido del candidato'),
    'email': fields.String(required=True, description='Dirección de correo electrónico del candidato'),
    'phone': fields.String(description='Número de teléfono del candidato'),
    'resume_url': fields.String(description='URL al currículum del candidato'),
    'linkedin_profile': fields.String(description='URL al perfil de LinkedIn')
})

# --- Analizadores de Argumentos ---
candidate_list_parser = reqparse.RequestParser()
candidate_list_parser.add_argument('page', type=int, location='args', default=1, help='Número de página')
candidate_list_parser.add_argument('per_page', type=int, location='args', default=10, help='Elementos por página')
# Añadir otros filtros si es necesario (ej., buscar por nombre/email)

# --- Recursos de Candidatos ---
@candidates_ns.route('/')
class CandidateListResource(Resource):
    @candidates_ns.doc('list_candidates', parser=candidate_list_parser)
    @candidates_ns.marshal_list_with(candidate_model)
    def get(self):
        """Listar todos los candidatos"""
        args = candidate_list_parser.parse_args()
        query = Candidate.query
        # Añadir lógica de filtrado aquí si aplica
        pagination = query.paginate(page=args['page'], per_page=args['per_page'], error_out=False)
        return candidates_schema.dump(pagination.items), 200, {'X-Total-Count': pagination.total}

    @candidates_ns.doc('create_candidate')
    @candidates_ns.expect(candidate_model, validate=True)
    @candidates_ns.marshal_with(candidate_model, code=201)
    def post(self):
        """Crear un nuevo candidato"""
        try:
            candidate_data = candidate_schema.load(candidates_ns.payload)
        except Exception as e:
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        # ¿Verificar correo electrónico existente?
        existing = Candidate.query.filter_by(email=candidate_data['email']).first()
        if existing:
            return {'message': f'El candidato con el correo electrónico {candidate_data["email"]} ya existe'}, 409

        new_candidate = Candidate(**candidate_data)
        db.session.add(new_candidate)
        db.session.commit()
        return candidate_schema.dump(new_candidate), 201

@candidates_ns.route('/<int:candidate_id>')
@candidates_ns.param('candidate_id', 'El identificador del candidato')
@candidates_ns.response(404, 'Candidato no encontrado')
class CandidateResource(Resource):
    @candidates_ns.doc('get_candidate')
    @candidates_ns.marshal_with(candidate_model)
    def get(self, candidate_id):
        """Obtener un candidato dado su identificador"""
        candidate = Candidate.query.get_or_404(candidate_id)
        return candidate_schema.dump(candidate)

    @candidates_ns.doc('update_candidate')
    @candidates_ns.expect(candidate_model)
    @candidates_ns.marshal_with(candidate_model)
    def put(self, candidate_id):
        """Actualizar un candidato"""
        candidate = Candidate.query.get_or_404(candidate_id)
        try:
            candidate_data = candidate_schema.load(candidates_ns.payload, partial=True)
        except Exception as e:
            return {'message': 'La validación del payload de entrada falló', 'errors': str(e)}, 400

        for key, value in candidate_data.items():
            setattr(candidate, key, value)

        db.session.commit()
        return candidate_schema.dump(candidate)

    @candidates_ns.doc('delete_candidate')
    @candidates_ns.response(204, 'Candidato eliminado')
    def delete(self, candidate_id):
        """Eliminar un candidato"""
        candidate = Candidate.query.get_or_404(candidate_id)
        # Considerar implicaciones: ¿eliminar aplicaciones relacionadas? ¿Marcar como inactivo?
        db.session.delete(candidate)
        db.session.commit()
        return '', 204
