"""User-facing job browsing, resume upload, and job application routes."""

import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from models import Application, Job, ResumeData, db
from routes.auth import login_required, roles_required
from services.resume_parser import analyze_resume_keywords, extract_text_from_file

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required
@roles_required("user")
def dashboard():
    """Render the user dashboard."""
    user_id = session["user_id"]
    resumes = ResumeData.query.filter_by(user_id=user_id).order_by(ResumeData.uploaded_at.desc()).all()
    applications = (
        Application.query.filter_by(user_id=user_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template(
        "user/dashboard.html",
        resumes=resumes,
        applications=applications,
        jobs=jobs[:5],
    )


@user_bp.route("/jobs")
@login_required
@roles_required("user")
def job_listings():
    """List available jobs."""
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    applied_job_ids = {
        application.job_id
        for application in Application.query.filter_by(user_id=session["user_id"]).all()
    }
    return render_template("user/job_listings.html", jobs=jobs, applied_job_ids=applied_job_ids)


@user_bp.route("/resume/upload", methods=["GET", "POST"])
@login_required
@roles_required("user")
def upload_resume():
    """Upload a resume and store extracted analysis data."""
    if request.method == "POST":
        uploaded_file = request.files.get("resume")
        if not uploaded_file or uploaded_file.filename == "":
            flash("Please choose a resume file to upload.", "error")
            return redirect(url_for("user.upload_resume"))

        if not _allowed_file(uploaded_file.filename):
            flash("Only PDF, DOC, and DOCX files are allowed.", "error")
            return redirect(url_for("user.upload_resume"))

        safe_name = secure_filename(uploaded_file.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        stored_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        uploaded_file.save(stored_path)

        try:
            extracted_text = extract_text_from_file(stored_path)
            analysis = analyze_resume_keywords(extracted_text)
            resume_data = ResumeData(
                user_id=session["user_id"],
                extracted_text=extracted_text or "No readable text found.",
                file_name=unique_name,
                original_name=safe_name,
                score=analysis["score"],
                keywords=", ".join(analysis["keywords"]),
            )
            db.session.add(resume_data)
            db.session.commit()
            flash("Resume uploaded and analyzed successfully.", "success")
            return redirect(url_for("user.resume_result", resume_id=resume_data.id))
        except Exception:
            db.session.rollback()
            if os.path.exists(stored_path):
                os.remove(stored_path)
            flash("The resume could not be processed.", "error")

    return render_template("user/upload_resume.html")


@user_bp.route("/resume/<int:resume_id>")
@login_required
@roles_required("user")
def resume_result(resume_id: int):
    """Display a resume analysis result."""
    resume = ResumeData.query.get_or_404(resume_id)
    if resume.user_id != session["user_id"]:
        flash("You cannot access that resume.", "error")
        return redirect(url_for("user.dashboard"))
    return render_template("user/resume_result.html", resume=resume)


@user_bp.route("/jobs/<int:job_id>")
@login_required
@roles_required("user")
def job_detail(job_id: int):
    """Show details for a single job."""
    job = Job.query.get_or_404(job_id)
    latest_resume = (
        ResumeData.query.filter_by(user_id=session["user_id"])
        .order_by(ResumeData.uploaded_at.desc())
        .first()
    )
    has_applied = Application.query.filter_by(user_id=session["user_id"], job_id=job_id).first()
    return render_template(
        "user/job_detail.html",
        job=job,
        latest_resume=latest_resume,
        has_applied=has_applied,
    )


@user_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@login_required
@roles_required("user")
def apply_job(job_id: int):
    """Apply for a job with the latest uploaded resume."""
    job = Job.query.get_or_404(job_id)
    user_id = session["user_id"]

    if Application.query.filter_by(user_id=user_id, job_id=job_id).first():
        flash("You have already applied for this job.", "error")
        return redirect(url_for("user.job_detail", job_id=job_id))

    latest_resume = (
        ResumeData.query.filter_by(user_id=user_id)
        .order_by(ResumeData.uploaded_at.desc())
        .first()
    )
    if not latest_resume:
        flash("Please upload a resume before applying.", "error")
        return redirect(url_for("user.upload_resume"))

    try:
        analysis = analyze_resume_keywords(latest_resume.extracted_text, job.description)
        application = Application(
            user_id=user_id,
            job_id=job.id,
            resume_path=os.path.join("uploads", latest_resume.file_name),
            score=analysis["score"],
        )
        db.session.add(application)
        db.session.commit()
        flash("Application submitted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("Unable to submit the application.", "error")

    return redirect(url_for("user.my_applications"))


@user_bp.route("/applications")
@login_required
@roles_required("user")
def my_applications():
    """List applications for the logged-in user."""
    applications = (
        Application.query.filter_by(user_id=session["user_id"])
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template("user/my_applications.html", applications=applications)


def _allowed_file(filename: str) -> bool:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in current_app.config["ALLOWED_EXTENSIONS"]
