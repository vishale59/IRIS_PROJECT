"""Application entry point for the IRIS Job Portal."""

import os

from flask import Flask, g, redirect, render_template, session, url_for
import pymysql
from sqlalchemy.exc import OperationalError

from config import config, mask_database_uri
from models import Application, Job, ResumeData, User, db


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config[config_name])

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    ensure_database_exists()

    db.init_app(app)
    app.logger.info(
        "Active database URI: %s",
        mask_database_uri(app.config["SQLALCHEMY_DATABASE_URI"]),
    )

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.employer import employer_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def load_logged_in_user() -> None:
        """Expose the current user to templates."""
        user_id = session.get("user_id")
        g.user = User.query.get(user_id) if user_id else None

    @app.context_processor
    def inject_globals() -> dict:
        """Inject app-wide template values."""
        return {"app_name": app.config["APP_NAME"]}

    @app.route("/")
    def index():
        """Redirect visitors based on their role."""
        role = session.get("user_role")
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
        if role == "employer":
            return redirect(url_for("employer.dashboard"))
        if role == "user":
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(_error):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    with app.app_context():
        bootstrap_database()

    return app


def ensure_database_exists() -> None:
    """Create the configured MySQL database automatically if it does not exist."""
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{os.getenv('DB_NAME', 'iris_db')}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def reset_database() -> None:
    """Drop and recreate the configured MySQL database."""
    database_name = os.getenv("DB_NAME", "iris_db")
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{database_name}`")
            cursor.execute(
                f"CREATE DATABASE `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def bootstrap_database() -> None:
    """Initialize tables and recover automatically from stale schema mismatches."""
    try:
        db.create_all()
        seed_data()
    except OperationalError as exc:
        from flask import current_app

        current_app.logger.warning("Database bootstrap failed, resetting schema: %s", exc)
        db.session.rollback()
        reset_database()
        db.create_all()
        seed_data()


def seed_data() -> None:
    """Insert baseline users and jobs for quick local testing."""
    if User.query.count() > 0:
        return

    admin = User(username="admin", email="admin@irisportal.com", role="admin")
    admin.set_password("Admin@123")

    employer = User(username="techcorp", email="employer@irisportal.com", role="employer")
    employer.set_password("Employer@123")

    applicant = User(username="jobseeker", email="user@irisportal.com", role="user")
    applicant.set_password("User@123")

    db.session.add_all([admin, employer, applicant])
    db.session.flush()

    jobs = [
        Job(
            title="Python Backend Developer",
            description=(
                "Build Flask APIs, integrate MySQL, and work with REST services. "
                "Required skills: python flask sql mysql api git docker."
            ),
            employer_id=employer.id,
        ),
        Job(
            title="Frontend UI Engineer",
            description=(
                "Create responsive interfaces with HTML, CSS, and JavaScript. "
                "Required skills: html css javascript accessibility ux."
            ),
            employer_id=employer.id,
        ),
    ]
    db.session.add_all(jobs)
    db.session.flush()

    resume = ResumeData(
        user_id=applicant.id,
        extracted_text="Python Flask SQL MySQL HTML CSS JavaScript Git Docker",
        file_name="seed_resume.txt",
        original_name="seed_resume.txt",
        score=90,
        keywords="python, flask, sql, mysql, html, css, javascript, git, docker",
    )
    db.session.add(resume)

    application = Application(
        user_id=applicant.id,
        job_id=jobs[0].id,
        resume_path=os.path.join("uploads", "seed_resume.txt"),
        score=90,
    )
    db.session.add(application)
    db.session.commit()


app = create_app(os.getenv("FLASK_ENV", "default"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
