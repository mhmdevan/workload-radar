from flask import Flask, jsonify
from .exceptions import APIError


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for the Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = jsonify(
            {
                "error": {
                    "message": error.message,
                    "code": error.code,
                }
            }
        )
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return (
            jsonify(
                {
                    "error": {
                        "message": "Resource not found",
                        "code": "not_found",
                    }
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return (
            jsonify(
                {
                    "error": {
                        "message": "Internal server error",
                        "code": "internal_error",
                    }
                }
            ),
            500,
        )
