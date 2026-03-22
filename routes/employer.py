"""Employer routes for posting jobs and reviewing applicants."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import Application, Job, db
from routes.auth import login_required, roles_required

employer_bp = Blueprint("employer", __name__, url_prefix="/employer")


@employer_bp.route("/dashboard")
@login_required
@roles_required("employer")
def dashboard():
    """Render the employer dashboard."""
    jobs = (
        Job.query.filter_by(employer_id=session["user_id"])
        .order_by(Job.created_at.desc())
        .all()
    )
    application_total = sum(len(job.applications) for job in jobs)
    return render_template(
        "employer/dashboard.html",
        jobs=jobs,
        application_total=application_total,
    )


@employer_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@roles_required("employer")
def post_job():
    """Create a new job posting."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not description:
            flash("Job title and description are required.", "error")
            return render_template("employer/post_job.html", job=None)

        try:
            job = Job(title=title, description=description, employer_id=session["user_id"])
            db.session.add(job)
            db.session.commit()
            flash("Job posted successfully.", "success")
            return redirect(url_for("employer.dashboard"))
        except Exception:
            db.session.rollback()
            flash("Unable to post the job.", "error")

    return render_template("employer/post_job.html", job=None)


@employer_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("employer")
def edit_job(job_id: int):
    """Update an existing job posting."""
    job = Job.query.get_or_404(job_id)
    if job.employer_id != session["user_id"]:
        flash("You cannot edit that job.", "error")
        return redirect(url_for("employer.dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Job title and description are required.", "error")
            return render_template("employer/post_job.html", job=job)

        try:
            job.title = title
            job.description = description
            db.session.commit()
            flash("Job updated successfully.", "success")
            return redirect(url_for("employer.dashboard"))
        except Exception:
            db.session.rollback()
            flash("Unable to update the job.", "error")

    return render_template("employer/post_job.html", job=job)


@employer_bp.route("/jobs/<int:job_id>/applicants")
@login_required
@roles_required("employer")
def applicants(job_id: int):
    """View applicants for a specific job."""
    job = Job.query.get_or_404(job_id)
    if job.employer_id != session["user_id"]:
        flash("You cannot view applicants for that job.", "error")
        return redirect(url_for("employer.dashboard"))

    applications = (
        Application.query.filter_by(job_id=job.id)
        .order_by(Application.score.desc(), Application.applied_at.desc())
        .all()
    )
    return render_template("employer/job_applications.html", job=job, applications=applications)
