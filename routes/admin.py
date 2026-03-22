from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from models import db, User, Job, Application, Resume

admin_bp = Blueprint('admin', __name__)


def _admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin/dashboard')
@login_required
@_admin_required
def dashboard():
    # Core stats
    stats = {
        'total_users': User.query.count(),
        'jobseekers': User.query.filter_by(role='jobseeker').count(),
        'employers': User.query.filter_by(role='employer').count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'total_applications': Application.query.count(),
        'total_resumes': Resume.query.count(),
        'pending': Application.query.filter_by(status='pending').count(),
        'shortlisted': Application.query.filter_by(status='shortlisted').count(),
        'hired': Application.query.filter_by(status='hired').count(),
        'rejected': Application.query.filter_by(status='rejected').count(),
    }

    # Applications per day (last 14 days)
    today = datetime.utcnow().date()
    daily_data = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        count = Application.query.filter(
            func.date(Application.applied_at) == day
        ).count()
        daily_data.append({'date': day.strftime('%b %d'), 'count': count})

    # Status distribution
    status_dist = {
        'pending': stats['pending'],
        'reviewed': Application.query.filter_by(status='reviewed').count(),
        'shortlisted': stats['shortlisted'],
        'rejected': stats['rejected'],
        'hired': stats['hired'],
    }

    # Top companies by job count
    top_companies = (db.session.query(Job.company, func.count(Job.id).label('cnt'))
                     .group_by(Job.company)
                     .order_by(func.count(Job.id).desc())
                     .limit(5).all())

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           daily_data=daily_data,
                           status_dist=status_dist,
                           top_companies=top_companies,
                           recent_users=recent_users)


@admin_bp.route('/admin/users')
@login_required
@_admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/admin/users/<int:user_id>/toggle')
@login_required
@_admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't deactivate yourself.", 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'deactivated'}.", 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/jobs')
@login_required
@_admin_required
def jobs():
    all_jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=all_jobs)


@admin_bp.route('/admin/jobs/<int:job_id>/toggle')
@login_required
@_admin_required
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    flash(f"Job {'activated' if job.is_active else 'deactivated'}.", 'success')
    return redirect(url_for('admin.jobs'))


@admin_bp.route('/admin/applications')
@login_required
@_admin_required
def applications():
    apps = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin/applications.html', applications=apps)


@admin_bp.route('/admin/api/stats')
@login_required
@_admin_required
def api_stats():
    """JSON endpoint for live dashboard refresh."""
    return jsonify({
        'users': User.query.count(),
        'jobs': Job.query.count(),
        'applications': Application.query.count(),
    })
