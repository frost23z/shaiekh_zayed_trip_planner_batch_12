from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app.models import Trip  # ruff: ignore[F401]

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    return app
