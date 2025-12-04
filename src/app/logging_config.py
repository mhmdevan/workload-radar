import logging
import sys
from flask import Flask


def configure_logging(app: Flask) -> None:
    """Configure structured logging to stdout based on app config."""
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    app.logger.setLevel(log_level)
    app.logger.propagate = True

    app.logger.info("Logging configured with level %s", log_level_name)
