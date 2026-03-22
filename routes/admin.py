"""Admin routes for managing users and jobs."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import Application, Job, ResumeData, User, db
from routes.auth import login_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@roles_required("admin")
def dashboard():
    """Render the admin dashboard."""
    return render_template(
        "admin/dashboard.html",
        user_count=User.query.count(),
        job_count=Job.query.count(),
        application_count=Application.query.count(),
        resume_count=ResumeData.query.count(),
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
