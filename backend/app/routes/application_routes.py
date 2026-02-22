from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app import db
from app.docs.swagger_docs import APP_CREATE_DOC, APP_ME_DOC, APP_STATUS_DOC
from app.middleware.role_required import role_required
from app.models.application_model import Application
from app.models.job_model import Job
from app.models.resume_model import Resume
from app.services.matching_service import compute_match
from app.utils.skill_extractor import parse_skills

application_bp = Blueprint("application_bp", __name__)
ALLOWED_STATUSES = {
    "Applied",
    "Shortlisted",
    "Interview Scheduled",
    "Rejected",
    "Selected",
}


def classify_candidate(score):
    """Classify candidate based on match score."""
    normalized_score = float(score or 0)
    if normalized_score >= 80:
        return "Accepted"
    if normalized_score >= 60:
        return "Recommended"
    if normalized_score >= 40:
        return "Low Match"
    return "Rejected"


def generate_improvement_message(missing_skills):
    """Generate a clear message for missing skills."""
    if not missing_skills:
        return "Strong alignment with the job requirements."
    return "Consider improving these skills to increase your match: " + ", ".join(missing_skills) + "."


def suggest_alternative_jobs(resume_text, all_jobs, resume_skills):
    """
    Suggest up to 3 alternative jobs with score >= 60, sorted by score desc.
    Returns minimal payload required by API response.
    """
    suggestions = []

    for candidate_job in all_jobs:
        alt_match = compute_match(
            resume_text,
            candidate_job.description,
            resume_skills,
            parse_skills(candidate_job.required_skills),
        )
        score = float(alt_match["match_score"])
        if score >= 60:
            suggestions.append(
                {
                    "title": candidate_job.title,
                    "match_score": round(score, 2),
                }
            )

    suggestions.sort(key=lambda item: item["match_score"], reverse=True)
    return suggestions[:3]


@application_bp.post("")
@swag_from(APP_CREATE_DOC)
@role_required("jobseeker")
def apply_to_job():
    data = request.get_json(silent=True) or {}
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"error": "job_id is required"}), 400

    user_id = int(get_jwt_identity())

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    existing = Application.query.filter_by(user_id=user_id, job_id=job.id).first()
    if existing:
        return jsonify({"error": "Already applied for this job"}), 409

    resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).first()
    if not resume:
        return jsonify({"error": "Upload your resume before applying"}), 400

    resume_skills = parse_skills(resume.extracted_skills)
    job_required_skills = parse_skills(job.required_skills)

    match = compute_match(
        resume.extracted_text,
        job.description,
        resume_skills,
        job_required_skills,
    )

    recommendation = classify_candidate(match["match_score"])
    improvement_message = generate_improvement_message(match["missing_skills"])

    alternative_jobs = []
    if recommendation in {"Low Match", "Rejected"}:
        other_jobs = Job.query.filter(Job.id != job.id).all()
        alternative_jobs = suggest_alternative_jobs(
            resume.extracted_text,
            other_jobs,
            resume_skills,
        )

    application = Application(
        user_id=user_id,
        job_id=job.id,
        match_score=match["match_score"],
        status="Applied",
        recommendation=recommendation,
        improvement_message=improvement_message,
    )

    db.session.add(application)
    db.session.commit()

    current_app.logger.info(
        "Application created application_id=%s user_id=%s job_id=%s match_score=%.2f",
        application.id,
        user_id,
        job.id,
        application.match_score,
    )

    return jsonify(
        {
            "match_score": application.match_score,
            "recommendation": recommendation,
            "matched_skills": match["matched_skills"],
            "missing_skills": match["missing_skills"],
            "improvement_message": improvement_message,
            "alternative_jobs": alternative_jobs,
        }
    ), 201


@application_bp.patch("/<int:application_id>/status")
@swag_from(APP_STATUS_DOC)
@role_required("employer")
def update_application_status(application_id):
    data = request.get_json(silent=True) or {}
    next_status = str(data.get("status", "")).strip()
    if next_status not in ALLOWED_STATUSES:
        return jsonify({"error": f"Status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"}), 400

    application = Application.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    employer_id = int(get_jwt_identity())
    job = Job.query.get(application.job_id)
    if not job or job.employer_id != employer_id:
        return jsonify({"error": "You can only update applications for your own jobs"}), 403

    application.status = next_status
    db.session.commit()

    return jsonify({"message": "Application status updated", "status": application.status}), 200


@application_bp.get("/me")
@swag_from(APP_ME_DOC)
@role_required("jobseeker")
def my_applications():
    user_id = int(get_jwt_identity())
    records = (
        db.session.query(Application, Job)
        .join(Job, Job.id == Application.job_id)
        .filter(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
        .all()
    )

    payload = [
        {
            "application_id": app_rec.id,
            "job_id": job.id,
            "job_title": job.title,
            "location": job.location,
            "match_score": app_rec.match_score,
            "status": app_rec.status,
            "created_at": app_rec.created_at.isoformat(),
        }
        for app_rec, job in records
    ]

    return jsonify(payload), 200
