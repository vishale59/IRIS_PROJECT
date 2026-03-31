"""Admin routes for managing users and jobs."""

from collections import defaultdict
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import Application, Job, ResumeData, User, db
from routes.auth import login_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@roles_required("admin")
def dashboard():
    """Render the admin dashboard."""
    users = User.query.order_by(User.created_at.desc()).all()
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    resumes = ResumeData.query.order_by(ResumeData.uploaded_at.desc()).all()

    monthly_metrics = defaultdict(lambda: {"users": 0, "jobs": 0, "applications": 0})
    for user in users:
        monthly_metrics[user.created_at.strftime("%b %Y")]["users"] += 1
    for job in jobs:
        monthly_metrics[job.created_at.strftime("%b %Y")]["jobs"] += 1
    for application in applications:
        monthly_metrics[application.applied_at.strftime("%b %Y")]["applications"] += 1

    sorted_labels = sorted(
        monthly_metrics.keys(),
        key=lambda label: datetime.strptime(label, "%b %Y"),
    )

    recent_activity = []
    for user in users[:3]:
        recent_activity.append(
            {
                "icon": "fa-user-plus",
                "title": f"{user.username} joined the portal",
                "meta": f"{user.role.title()} account created",
                "timestamp": user.created_at,
            }
        )
    for job in jobs[:3]:
        recent_activity.append(
            {
                "icon": "fa-briefcase",
                "title": f"{job.title} was posted",
                "meta": f"Published by {job.employer.username}",
                "timestamp": job.created_at,
            }
        )
    for application in applications[:4]:
        recent_activity.append(
            {
                "icon": "fa-file-circle-check",
                "title": f"{application.user.username} applied for {application.job.title}",
                "meta": f"Application score: {application.score}%",
                "timestamp": application.applied_at,
            }
        )
    recent_activity.sort(key=lambda item: item["timestamp"], reverse=True)

    top_jobs = sorted(jobs, key=lambda job: len(job.applications), reverse=True)[:5]

    return render_template(
        "admin/dashboard.html",
        user_count=len(users),
        job_count=len(jobs),
        application_count=len(applications),
        resume_count=len(resumes),
        chart_labels=sorted_labels,
        chart_users=[monthly_metrics[label]["users"] for label in sorted_labels],
        chart_jobs=[monthly_metrics[label]["jobs"] for label in sorted_labels],
        chart_applications=[monthly_metrics[label]["applications"] for label in sorted_labels],
        recent_activity=recent_activity[:6],
        recent_users=users[:5],
        top_jobs=top_jobs,
    )


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def users():
    """Display users and handle user deletion."""
    if request.method == "POST":
        user_id = request.form.get("user_id", type=int)
        if user_id == session["user_id"]:
            flash("You cannot delete your own admin account.", "error")
            return redirect(url_for("admin.users"))

        user = User.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("Unable to delete that user.", "error")
        return redirect(url_for("admin.users"))

    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@admin_bp.route("/jobs", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def jobs():
    """Display jobs and handle job deletion."""
    if request.method == "POST":
        job_id = request.form.get("job_id", type=int)
        job = Job.query.get_or_404(job_id)
        try:
            db.session.delete(job)
            db.session.commit()
            flash("Job deleted successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("Unable to delete that job.", "error")
        return redirect(url_for("admin.jobs"))

    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template("admin/jobs.html", jobs=jobs)


@admin_bp.route("/applications")
@login_required
@roles_required("admin")
def applications():
    """Display all submitted applications."""
    records = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template("admin/applications.html", applications=records)
