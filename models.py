"""SQLAlchemy data models for the IRIS Job Portal."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """System users with role-based access."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    jobs = db.relationship("Job", back_populates="employer", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="user", cascade="all, delete-orphan")
    resume_data = db.relationship("ResumeData", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        """Hash and store a password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Validate a plaintext password."""
        return check_password_hash(self.password, raw_password)


class Job(db.Model):
    """Jobs posted by employers."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    employer = db.relationship("User", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Application(db.Model):
    """Job applications submitted by users."""

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    resume_path = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="applications")
    job = db.relationship("Job", back_populates="applications")

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )


class ResumeData(db.Model):
    """Extracted resume content used for lightweight analysis."""

    __tablename__ = "resume_data"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    keywords = db.Column(db.Text, nullable=False, default="")
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="resume_data")
