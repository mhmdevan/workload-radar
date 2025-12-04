from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from .exceptions import APIError


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers for API errors and unexpected exceptions."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        response = {
            "error": {
                "type": error.__class__.__name__,
                "message": error.message,
            }
        }
        if error.extra:
            response["error"]["details"] = error.extra
        return jsonify(response), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        response = {
            "error": {
                "type": "HTTPException",
                "message": error.description,
                "code": error.code,
            }
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception("Unhandled exception", exc_info=error)
        response = {
            "error": {
                "type": "InternalServerError",
                "message": "Internal server error",
            }
        }
        return jsonify(response), 500
