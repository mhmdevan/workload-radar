import os


class Config:
    """Base configuration for the application."""

    # Environment
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = APP_ENV == "development"
    TESTING = APP_ENV == "test"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Application host/port
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    # Nginx integration flag (used for runtime hints, logging, etc.)
    ENABLE_NGINX = os.getenv("ENABLE_NGINX", "false").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Database configuration
    # In production the application is expected to talk to an external PostgreSQL instance.
    DB_PROVIDER = os.getenv("DB_PROVIDER", "postgres")
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_USER = os.getenv("DB_USER", "radar")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "radar")
    DB_NAME = os.getenv("DB_NAME", "radar")

    # Celery / RabbitMQ configuration
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://radar:radar@rabbitmq:5672//",
    )
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "rpc://",
    )

    # Offline analytics configuration
    # This directory is used to store Parquet exports and derived analytics produced
    # by the DuckDB + Polars pipeline (e.g. tasks.parquet, analytics_summary.parquet).
    # In Docker this is typically mapped to a host volume.
    ANALYTICS_DATA_DIR = os.getenv("ANALYTICS_DATA_DIR", "/data/analytics")
