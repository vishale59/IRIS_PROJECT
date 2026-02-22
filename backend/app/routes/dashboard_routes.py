from flasgger import swag_from
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

from app import db
from app.docs.swagger_docs import (
    DASH_ANALYTICS_DOC,
    DASH_DELETE_USER_DOC,
    DASH_SUMMARY_DOC,
    DASH_USERS_DOC,
)
from app.middleware.role_required import role_required
from app.models.application_model import Application
from app.models.job_model import Job
from app.models.resume_model import Resume
from app.models.user_model import User

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.get("")
@swag_from(DASH_SUMMARY_DOC)
@role_required("admin")
def dashboard_summary():
    avg_match_score = db.session.query(func.avg(Application.match_score)).scalar() or 0.0

    return jsonify(
        {
            "total_users": User.query.count(),
            "total_jobs": Job.query.count(),
            "total_applications": Application.query.count(),
            "average_match_score": round(float(avg_match_score), 2),
        }
    ), 200


@dashboard_bp.get("/users")
@swag_from(DASH_USERS_DOC)
@role_required("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ]
    ), 200


@dashboard_bp.delete("/users/<int:user_id>")
@swag_from(DASH_DELETE_USER_DOC)
@role_required("admin")
def delete_user(user_id):
    current_admin_id = int(get_jwt_identity())
    if current_admin_id == user_id:
        return jsonify({"error": "Admin cannot delete own account"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    Application.query.filter_by(user_id=user_id).delete()
    Resume.query.filter_by(user_id=user_id).delete()

    jobs = Job.query.filter_by(employer_id=user_id).all()
    for job in jobs:
        Application.query.filter_by(job_id=job.id).delete()
        db.session.delete(job)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


@dashboard_bp.get("/analytics")
@swag_from(DASH_ANALYTICS_DOC)
@role_required("admin")
def analytics():
    role_rows = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    role_distribution = {role: count for role, count in role_rows}

    avg_match_score = db.session.query(func.avg(Application.match_score)).scalar() or 0.0

    return jsonify(
        {
            "total_users": User.query.count(),
            "total_jobs": Job.query.count(),
            "total_applications": Application.query.count(),
            "average_match_score": round(float(avg_match_score), 2),
            "role_distribution": role_distribution,
        }
    ), 200