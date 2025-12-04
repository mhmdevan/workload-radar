import os


class Config:
    """Base configuration for the application."""

    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = APP_ENV == "development"
    TESTING = APP_ENV == "test"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    # Enable/disable Nginx integration hints
    ENABLE_NGINX = os.getenv("ENABLE_NGINX", "false").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Database
    DB_PROVIDER = os.getenv("DB_PROVIDER", "postgres")
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "radar")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "radar")
    DB_NAME = os.getenv("DB_NAME", "radar")

    # Celery / RabbitMQ
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://radar:radar@rabbitmq:5672//",
    )
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "rpc://",
    )
