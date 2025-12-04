from flask import Flask
from .auth import auth_bp
from .projects import projects_bp
from .tasks import tasks_bp
from .reports import reports_bp
from .health import health_bp


def register_blueprints(app: Flask) -> None:
    """Register all API blueprints on the Flask app."""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(health_bp, url_prefix="")
