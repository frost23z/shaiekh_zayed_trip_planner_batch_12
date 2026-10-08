import os

from dotenv import load_dotenv

load_dotenv()


DEFAULT_DATABASE_URI = "sqlite:///trip_planner.db"


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        DEFAULT_DATABASE_URI,
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
