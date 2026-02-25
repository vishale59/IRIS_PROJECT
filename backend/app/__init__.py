import json
import logging
from pathlib import Path

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from app.docs.swagger_docs import SWAGGER_TEMPLATE
from config import DevelopmentConfig

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("DATABASE_URL is not configured. Set it in .env")

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    log_path = Path(app.config["LOG_FILE"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    register_jwt_error_handlers()

    configure_logging(app)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "openapi",
                "route": "/openapi.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
    }
    Swagger(app, template=SWAGGER_TEMPLATE, config=swagger_config)

    from app.models import application_model, job_model, resume_model, user_model  # noqa: F401
    from app.routes.application_routes import application_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.job_routes import job_bp
    from app.routes.resume_routes import resume_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(job_bp, url_prefix="/api/jobs")
    app.register_blueprint(resume_bp, url_prefix="/api/resumes")
    app.register_blueprint(application_bp, url_prefix="/api/applications")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    export_openapi_file(app)

    return app


def configure_logging(app):
    logger = logging.getLogger("iris")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        file_handler = logging.FileHandler(app.config["LOG_FILE"])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    app.logger.handlers = logger.handlers
    app.logger.setLevel(logging.INFO)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(_err):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(_err):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(_err):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(413)
    def too_large(_err):
        return jsonify({"error": "File too large"}), 413

    @app.errorhandler(500)
    def server_error(_err):
        return jsonify({"error": "Internal server error"}), 500


def register_jwt_error_handlers():
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Unauthorized", "message": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Unauthorized", "message": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"error": "Unauthorized", "message": "Token has expired"}), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"error": "Unauthorized", "message": "Fresh token required"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"error": "Unauthorized", "message": "Token has been revoked"}), 401


def export_openapi_file(app):
    output_path = Path("openapi.json")
    try:
        with app.test_client() as client:
            response = client.get("/openapi.json")
            if response.status_code == 200:
                output_path.write_text(
                    json.dumps(response.get_json(), indent=2), encoding="utf-8"
                )
    except Exception:
        app.logger.exception("Failed to export openapi.json")
