from . import create_app
from .extensions import celery

# Create Flask app and bind Celery to it so that workers can run tasks.
app = create_app()

# Re-export Celery instance for "celery -A app.celery_app.celery worker"
__all__ = ["celery"]
