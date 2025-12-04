import os
import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    """Configuration for running tests with SQLite in-memory DB."""
    APP_ENV = "test"
    DEBUG = False
    TESTING = True

    DB_PROVIDER = "sqlite"
    DB_NAME = ":memory:"

    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "rpc://"


@pytest.fixture(scope="session")
def app():
    """Flask application fixture for tests."""
    os.environ["APP_ENV"] = "test"
    application = create_app(TestConfig)
    return application


@pytest.fixture
def client(app):
    """Flask test client fixture."""
    return app.test_client()
