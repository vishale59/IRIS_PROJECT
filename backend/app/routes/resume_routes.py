from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.docs.swagger_docs import RESUME_ME_DOC, RESUME_UPLOAD_DOC
from app.middleware.role_required import role_required
from app.models.resume_model import Resume
from app.utils.file_handler import extract_text_from_pdf, save_resume_file, validate_pdf_file
from app.utils.skill_extractor import extract_skills

resume_bp = Blueprint("resume_bp", __name__)


@resume_bp.post("/upload")
@swag_from(RESUME_UPLOAD_DOC)
@jwt_required()
@role_required("jobseeker")
def upload_resume():
    file = request.files.get("file")
    is_valid, message = validate_pdf_file(file, current_app.config["MAX_CONTENT_LENGTH"])
    if not is_valid:
        return jsonify({"error": message}), 400

    filename, file_path = save_resume_file(file, current_app.config["UPLOAD_FOLDER"])
    extracted_text = extract_text_from_pdf(file_path)
    extracted_skills = extract_skills(extracted_text)

    user_id = int(get_jwt_identity())

    resume = Resume(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        extracted_text=extracted_text,
        extracted_skills=",".join(extracted_skills),
    )

    db.session.add(resume)
    db.session.commit()

    current_app.logger.info("Resume uploaded user_id=%s resume_id=%s", user_id, resume.id)

    return jsonify(
        {
            "message": "Resume uploaded successfully",
            "resume_id": resume.id,
            "extracted_skills": extracted_skills,
        }
    ), 201


@resume_bp.get("/me")
@swag_from(RESUME_ME_DOC)
@jwt_required()
@role_required("jobseeker")
def get_latest_resume():
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).first()

    if not resume:
        return jsonify({"error": "No resume found"}), 404

    skills = [s for s in resume.extracted_skills.split(",") if s]

    return jsonify(
        {
            "id": resume.id,
            "filename": resume.filename,
            "uploaded_at": resume.uploaded_at.isoformat(),
            "extracted_skills": skills,
        }
    ), 200
