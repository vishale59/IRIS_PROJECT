"""Application configuration for the IRIS Job Portal."""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _build_database_uri() -> str:
    """Build a SQLAlchemy connection string from environment variables."""
    explicit_uri = os.getenv("DATABASE_URL")
    if explicit_uri:
        return explicit_uri

    if os.getenv("USE_SQLITE_FALLBACK", "true").lower() == "true":
        return os.getenv(
            "SQLITE_DATABASE_URI",
            f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'iris_job_portal.db')}",
        )

    db_driver = os.getenv("DB_DRIVER", "mysql+pymysql")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "iris_job_portal")
    return f"{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    """Base configuration shared across environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 8 * 1024 * 1024))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
    APP_NAME = "IRIS Job Portal"


class DevelopmentConfig(Config):
    """Development defaults."""

    DEBUG = True


class ProductionConfig(Config):
    """Production defaults."""

    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
