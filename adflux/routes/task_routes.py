from flask import jsonify
from flask_restx import Namespace, Resource, fields # Importar fields
from celery.result import AsyncResult
from ..extensions import celery # Importar tu instancia de celery

# Namespace para el Estado de las Tareas
tasks_ns = Namespace('tasks', description='Operaciones de Estado de Tareas Celery')

# Definir modelos de respuesta esperados para la documentación Swagger
# Parte genérica de la respuesta
task_status_base = tasks_ns.model('TaskStatusBase', {
    'task_id': fields.String(required=True, description='El ID de la tarea Celery'),
    'status': fields.String(required=True, description='Estado actual de la tarea (ej., PENDING, SUCCESS, FAILURE)'),
    'error': fields.String(description='Detalles del error si el estado de la tarea es FAILURE')
})

# Estructura específica para un resultado exitoso de tarea de publicación de Meta
meta_publish_result_fields = tasks_ns.model('MetaPublishResult', {
    'success': fields.Boolean(description='Indica si la operación de publicación tuvo éxito'),
    'message': fields.String(description='Mensaje de estado de la tarea'),
    'external_campaign_id': fields.String(description='ID de la campaña de Meta creada'),
    'external_ad_set_id': fields.String(description='ID del conjunto de anuncios de Meta creado'),
    'external_ad_id': fields.String(description='ID del anuncio de Meta creado'),
    'external_audience_id': fields.String(description='ID de la audiencia personalizada de Meta creada (si aplica)')
})

# Estructura específica para un resultado exitoso de tarea de publicación de Google Ads
google_publish_external_ids_fields = tasks_ns.model('GooglePublishExternalIDs', {
    'budget_id': fields.String(description='ID del presupuesto de Google Ads creado'),
    'campaign_id': fields.String(description='ID de la campaña de Google Ads creada'),
    'ad_group_id': fields.String(description='ID del grupo de anuncios de Google Ads creado'),
    'ad_id': fields.String(description='ID del anuncio de Google Ads creado')
})
google_publish_result_fields = tasks_ns.model('GooglePublishResult', {
    'success': fields.Boolean(description='Indica si la operación de publicación tuvo éxito'),
    'message': fields.String(description='Mensaje de estado de la tarea'),
    'external_campaign_id': fields.String(description='ID de la campaña de Google Ads creada (ID principal)'),
    'external_ids': fields.Nested(google_publish_external_ids_fields, description='Diccionario que contiene todos los IDs de entidades de Google Ads creadas')
})

# Combinar estado base con posibles estructuras de resultado
task_status_response = tasks_ns.model('TaskStatusResponse', {
    'task_id': fields.String(required=True, description='El ID de la tarea Celery'),
    'status': fields.String(required=True, description='Estado actual de la tarea (ej., PENDING, SUCCESS, FAILURE)'),
    'result': fields.Raw(description='Payload del resultado. La estructura depende del tipo de tarea y el estado. Puede ser una cadena simple (para estados PENDING/otros) o un objeto JSON específico (para SUCCESS/FAILURE de tareas de publicación). Ver MetaPublishResult o GooglePublishResult para estructuras de publicación exitosas.'),
    'error': fields.String(description='Detalles del error si el estado de la tarea es FAILURE')
})

@tasks_ns.route('/status/<string:task_id>')
@tasks_ns.param('task_id', 'El ID de la tarea Celery')
class TaskStatusResource(Resource):
    @tasks_ns.doc('get_task_status')
    # Usar el modelo combinado para la respuesta 200
    @tasks_ns.marshal_with(task_status_response, code=200, description='Estado de la tarea recuperado con éxito')
    @tasks_ns.response(404, 'Tarea no encontrada')
    def get(self, task_id):
        """Verifica el estado de una tarea asíncrona en segundo plano (ej., publicación de campaña).
        
        Proporciona el estado actual (PENDING, SUCCESS, FAILURE, etc.) y el payload del resultado.
        La estructura del campo 'result' depende de la tarea que se ejecutó.
        - Para publicaciones exitosas de Meta, ver el esquema MetaPublishResult.
        - Para publicaciones exitosas de Google Ads, ver el esquema GooglePublishResult.
        - Para tareas pendientes o fallidas, 'result' podría contener un mensaje de cadena o detalles del error.
        """
        task_result = AsyncResult(task_id, app=celery)

        response_data = {
            'task_id': task_id,
            'status': task_result.state,
            'result': None,
            'error': None
        }

        if task_result.state == 'PENDING':
            # La tarea está esperando ser ejecutada o es desconocida
            # Verificar si la tarea existe en el backend
            # Nota: El backend de Redis podría no saber de manera fiable sobre tareas PENDING a menos que hayan comenzado
            # Podemos asumir que PENDING significa esperando o desconocido
             response_data['result'] = 'La tarea está pendiente o no se encontró.'
             # No podemos decir definitivamente 404 aquí con todos los backends
             # Devolver 200 ya que consultamos el estado con éxito
             # return jsonify(response_data), 200
             return response_data, 200 # Devolver dict directamente

        elif task_result.state == 'SUCCESS':
            response_data['result'] = task_result.result # Obtener el valor de retorno de la tarea
            # return jsonify(response_data), 200
            return response_data, 200 # Devolver dict directamente

        elif task_result.state == 'FAILURE':
            # task_result.result contiene el objeto de excepción
            # task_result.info o task_result.traceback podrían contener más detalles
            response_data['result'] = str(task_result.result) # Representación básica en cadena del error
            response_data['error'] = task_result.info if isinstance(task_result.info, str) else repr(task_result.info)
            # return jsonify(response_data), 200 # Aún 200 OK, pero indica fallo en el payload
            return response_data, 200 # Devolver dict directamente

        else:
            # Manejar otros estados como STARTED, RETRY, REVOKED si es necesario
            response_data['result'] = f'La tarea está en estado: {task_result.state}'
            # return jsonify(response_data), 200
            return response_data, 200 # Devolver dict directamente