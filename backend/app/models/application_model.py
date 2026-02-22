from datetime import datetime

from app import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    match_score = db.Column(db.Float, nullable=False, default=0.0)
    recommendation = db.Column(db.String(32), nullable=True)
    improvement_message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Applied")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_job_application"),
    )
