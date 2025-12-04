from flask import Flask
from celery import Celery
from .models import db


celery = Celery("workload_radar")


def _bind_database(app: Flask) -> None:
    """
    Bind Pony ORM database according to config and generate mapping.

    Pony's Database instance is global. In tests or some environments
    create_app() can be called multiple times within the same process.
    We guard against rebinding the already bound database.
    """
    # If already bound, do nothing (idempotent binding).
    if db.provider is not None:
        return

    provider = app.config["DB_PROVIDER"]

    if provider == "sqlite":
        # Simple setup for tests or local experiments
        db.bind(
            provider="sqlite",
            filename=app.config["DB_NAME"],
            create_db=True,
        )
        db.generate_mapping(create_tables=True)
    else:
        # Production: PostgreSQL with migrations-managed schema
        db.bind(
            provider=provider,
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            database=app.config["DB_NAME"],
        )
        # Tables must be created with migrations beforehand
        db.generate_mapping(create_tables=False)


def _configure_celery(app: Flask) -> None:
    """Configure Celery to work with Flask application context."""
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]

    class ContextTask(celery.Task):
        """Task that runs inside Flask application context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def init_extensions(app: Flask) -> None:
    """Initialize all integrations for the Flask app."""
    _bind_database(app)
    _configure_celery(app)
