from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    return app
