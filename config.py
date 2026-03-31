"""Application configuration for the IRIS Job Portal."""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _build_database_uri() -> str:
    """Build a MySQL SQLAlchemy connection string from environment variables."""
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")

    if not db_user or not db_name:
        raise RuntimeError(
            "MySQL configuration is incomplete. Set DB_USER and DB_NAME."
        )

    return (
        "mysql+pymysql://"
        f"{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
    )


def mask_database_uri(uri: str) -> str:
    """Hide the password when printing the active SQLAlchemy URI."""
    if "@" not in uri or "://" not in uri:
        return uri
    scheme, rest = uri.split("://", 1)
    credentials, host_part = rest.split("@", 1)
    if ":" not in credentials:
        return uri
    username, _password = credentials.split(":", 1)
    return f"{scheme}://{username}:***@{host_part}"


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
