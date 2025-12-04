from flask import Flask
from .config import Config
from .extensions import init_extensions
from .logging_config import configure_logging
from .errors import register_error_handlers
from .blueprints import register_blueprints


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    configure_logging(app)
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    app.logger.info(
        "Application created with APP_ENV=%s, ENABLE_NGINX=%s",
        app.config.get("APP_ENV"),
        app.config.get("ENABLE_NGINX"),
    )

    return app
