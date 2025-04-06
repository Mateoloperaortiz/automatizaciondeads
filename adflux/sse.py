"""
Módulo para Server-Sent Events (SSE) en AdFlux.

Este módulo proporciona funcionalidad para enviar eventos en tiempo real
a los clientes usando Server-Sent Events (SSE).
"""

from flask import Blueprint, Response, current_app
import json
import queue
import threading

event_queue = queue.Queue()

lock = threading.Lock()

clients = []

sse_bp = Blueprint("sse", __name__)


@sse_bp.route("/stream")
def stream():
    """
    Endpoint para establecer una conexión SSE con el cliente.
    
    Returns:
        Respuesta SSE con los eventos en tiempo real.
    """
    def generate():
        client_queue = queue.Queue()
        with lock:
            clients.append(client_queue)
        
        try:
            yield "event: connected\ndata: {}\n\n"
            
            while True:
                event = client_queue.get()
                
                if event is None:
                    break
                
                yield event
        finally:
            with lock:
                clients.remove(client_queue)
    
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Para Nginx
            "Connection": "keep-alive"
        }
    )


def push_notification(notification_data):
    """
    Envía una notificación a todos los clientes conectados.
    
    Args:
        notification_data: Datos de la notificación a enviar.
    """
    event = f"event: notification\ndata: {json.dumps(notification_data)}\n\n"
    
    with lock:
        for client_queue in clients:
            client_queue.put(event)


def push_event(event_type, data):
    """
    Envía un evento personalizado a todos los clientes conectados.
    
    Args:
        event_type: Tipo de evento a enviar.
        data: Datos del evento.
    """
    event = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    
    with lock:
        for client_queue in clients:
            client_queue.put(event)
