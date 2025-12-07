# src/scripts/run_offline_analytics.py

import logging

from app import create_app
from app.config import Config
from app.analytics.pipeline import run_offline_analytics

logger = logging.getLogger(__name__)


def main() -> None:
    """
    CLI entrypoint for running the offline analytics pipeline.

    This function:
    - creates the Flask application,
    - enters the application context,
    - and invokes the analytics pipeline.
    """
    # Use the base Config class; environment-specific behavior
    # is still driven by APP_ENV and other env variables.
    app = create_app(Config)

    with app.app_context():
        result = run_offline_analytics()
        logger.info("Offline analytics finished", extra={"analytics": result})
        print("Offline analytics completed:")
        for key, value in result.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
