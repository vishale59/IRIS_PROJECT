from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app import db
from app.docs.swagger_docs import (
    JOB_APPLICANTS_DOC,
    JOB_CREATE_DOC,
    JOB_DELETE_DOC,
    JOB_LIST_DOC,
    JOB_UPDATE_DOC,
)
from app.middleware.role_required import role_required
from app.models.application_model import Application
from app.models.job_model import Job
from app.models.user_model import User
from app.utils.skill_extractor import parse_skills

job_bp = Blueprint("job_bp", __name__)


@job_bp.post("")
@swag_from(JOB_CREATE_DOC)
@role_required("employer")
def create_job():
    data = request.get_json(silent=True) or {}

    required_fields = ["title", "description", "location", "required_skills"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    employer_id = int(get_jwt_identity())
    required_skills = parse_skills(data.get("required_skills"))

    job = Job(
        title=data["title"].strip(),
        description=data["description"].strip(),
        location=data["location"].strip(),
        required_skills=",".join(required_skills),
        employer_id=employer_id,
    )

    db.session.add(job)
    db.session.commit()

    current_app.logger.info("Job created job_id=%s employer_id=%s", job.id, employer_id)

    return jsonify({"message": "Job created successfully", "job_id": job.id}), 201


@job_bp.get("")
@swag_from(JOB_LIST_DOC)
def list_jobs():
    title = request.args.get("title", "", type=str).strip()
    location = request.args.get("location", "", type=str).strip()

    query = Job.query
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    jobs = query.order_by(Job.created_at.desc()).all()

    return jsonify(
        [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "required_skills": parse_skills(job.required_skills),
                "employer_id": job.employer_id,
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ]
    ), 200


@job_bp.put("/<int:job_id>")
@swag_from(JOB_UPDATE_DOC)
@role_required("employer")
def update_job(job_id):
    employer_id = int(get_jwt_identity())
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.employer_id != employer_id:
        return jsonify({"error": "You can only update your own jobs"}), 403

    data = request.get_json(silent=True) or {}

    if "title" in data and str(data["title"]).strip():
        job.title = str(data["title"]).strip()
    if "description" in data and str(data["description"]).strip():
        job.description = str(data["description"]).strip()
    if "location" in data and str(data["location"]).strip():
        job.location = str(data["location"]).strip()
    if "required_skills" in data:
        job.required_skills = ",".join(parse_skills(data.get("required_skills")))

    db.session.commit()

    return jsonify({"message": "Job updated successfully"}), 200


@job_bp.delete("/<int:job_id>")
@swag_from(JOB_DELETE_DOC)
@role_required("employer")
def delete_job(job_id):
    employer_id = int(get_jwt_identity())
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.employer_id != employer_id:
        return jsonify({"error": "You can only delete your own jobs"}), 403

    Application.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted successfully"}), 200


@job_bp.get("/<int:job_id>/applicants")
@swag_from(JOB_APPLICANTS_DOC)
@role_required("employer")
def view_applicants(job_id):
    employer_id = int(get_jwt_identity())
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.employer_id != employer_id:
        return jsonify({"error": "You can only view applicants for your own jobs"}), 403

    records = (
        db.session.query(Application, User)
        .join(User, User.id == Application.user_id)
        .filter(Application.job_id == job_id)
        .order_by(Application.match_score.desc())
        .all()
    )

    applicants = [
        {
            "application_id": app_rec.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "match_score": app_rec.match_score,
            "status": app_rec.status,
            "applied_at": app_rec.created_at.isoformat(),
        }
        for app_rec, user in records
    ]

    return jsonify({"job_id": job_id, "applicants": applicants}), 200