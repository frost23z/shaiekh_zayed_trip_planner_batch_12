import logging

from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return jsonify(
            {
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": _format_validation_error(error),
            }
        ), 400

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.code, "message": error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify(
            {
                "error": error.name.upper().replace(" ", "_"),
                "message": error.description,
            }
        ), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception):
        logger.exception("Unhandled exception", exc_info=error)

        return jsonify(
            {
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            }
        ), 500


def _format_validation_error(error: ValidationError) -> list[dict]:
    error_details = []

    for item in error.errors(
        include_url=False,
        include_context=False,
        include_input=False,
    ):
        field = ".".join(str(part) for part in item["loc"])
        message = item["msg"]

        error_details.append(
            {
                "field": field,
                "message": message,
            }
        )

    return error_details
