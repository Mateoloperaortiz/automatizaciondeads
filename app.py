from app import create_app, db, socketio
from app.models.job_opening import JobOpening
from app.models.candidate import Candidate
from app.utils.celery_config import make_celery

# Create Flask application with in-memory database for testing
config = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'DEBUG': True
}
app = create_app(config)

# Initialize Celery with the Flask app
celery = make_celery(app)

@app.shell_context_processor
def make_shell_context():
    """Add database and models to flask shell context."""
    return {
        'db': db,
        'JobOpening': JobOpening,
        'Candidate': Candidate,
        'celery': celery,
        'socketio': socketio
    }

if __name__ == '__main__':
    # Use SocketIO to run the app instead of regular Flask run
    socketio.run(app, debug=True, port=5002)