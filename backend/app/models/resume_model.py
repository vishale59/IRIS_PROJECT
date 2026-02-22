from datetime import datetime

from app import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    extracted_skills = db.Column(db.Text, nullable=False, default="")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
