from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app(config_overrides: dict | None = None):
    app = Flask(__name__)

    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    # Accept /api/v1/trips and /api/v1/trips/ without a redirect.
    app.url_map.strict_slashes = False

    db.init_app(app)

    from app import models  # ruff: ignore[F401]

    with app.app_context():
        db.create_all()

    # Error handlers registration
    from app.errors import register_error_handlers

    register_error_handlers(app)

    # Routes registration
    from app.routes import trip_bp

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    app.register_blueprint(trip_bp, url_prefix="/api/v1/trips")

    return app
