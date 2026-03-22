from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from models import db, Job, Application, User
from services import mailer

employer_bp = Blueprint('employer', __name__)

VALID_STATUSES = ('Applied', 'Reviewed', 'Selected', 'Rejected', 'Hired')


def _employer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('employer', 'admin'):
            flash('Employer access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@employer_bp.route('/employer/dashboard')
@login_required
@_employer_required
def dashboard():
    jobs = Job.query.filter_by(employer_id=current_user.id).order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]

    recent_applications = []
    if job_ids:
        recent_applications = (Application.query
                               .filter(Application.job_id.in_(job_ids))
                               .order_by(Application.applied_at.desc())
                               .limit(10).all())

    stats = {
        'total_jobs':       len(jobs),
        'active_jobs':      sum(1 for j in jobs if j.is_active),
        'total_applications': Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0,
        'pending':   Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Applied').count() if job_ids else 0,
        'selected':  Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Selected').count() if job_ids else 0,
    }

    return render_template('employer/dashboard.html',
                           jobs=jobs,
                           recent_applications=recent_applications,
                           stats=stats)


@employer_bp.route('/employer/jobs/new', methods=['GET', 'POST'])
@login_required
@_employer_required
def post_job():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        company     = request.form.get('company', '').strip()
        location    = request.form.get('location', '').strip()
        job_type    = request.form.get('job_type', 'Full-time')
        description = request.form.get('description', '').strip()
        requirements= request.form.get('requirements', '').strip()
        skills_req  = request.form.get('skills_required', '').strip()
        exp_level   = request.form.get('experience_level', 'Entry')
        category    = request.form.get('category', '').strip()
        salary_min  = request.form.get('salary_min')
        salary_max  = request.form.get('salary_max')
        deadline_str= request.form.get('deadline', '')

        if not all([title, company, description]):
            flash('Title, company, and description are required.', 'danger')
            return render_template('employer/post_job.html', form_data=request.form)

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                pass

        job = Job(
            employer_id=current_user.id,
            title=title, company=company, location=location,
            job_type=job_type, description=description,
            requirements=requirements, skills_required=skills_req,
            experience_level=exp_level, category=category,
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            deadline=deadline,
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/post_job.html', form_data={})


@employer_bp.route('/employer/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@_employer_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        job.title            = request.form.get('title', job.title)
        job.company          = request.form.get('company', job.company)
        job.location         = request.form.get('location', job.location)
        job.job_type         = request.form.get('job_type', job.job_type)
        job.description      = request.form.get('description', job.description)
        job.requirements     = request.form.get('requirements', job.requirements)
        job.skills_required  = request.form.get('skills_required', job.skills_required)
        job.experience_level = request.form.get('experience_level', job.experience_level)
        job.category         = request.form.get('category', job.category)
        job.is_active        = 'is_active' in request.form
        db.session.commit()
        flash('Job updated.', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/post_job.html', job=job, form_data={})


@employer_bp.route('/employer/jobs/<int:job_id>/toggle')
@login_required
@_employer_required
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('employer.dashboard'))
    job.is_active = not job.is_active
    db.session.commit()
    flash(f"Job {'activated' if job.is_active else 'deactivated'}.", 'success')
    return redirect(url_for('employer.dashboard'))


@employer_bp.route('/employer/jobs/<int:job_id>/applications')
@login_required
@_employer_required
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('employer.dashboard'))

    apps = (Application.query
            .filter_by(job_id=job_id)
            .order_by(Application.ats_match_score.desc())
            .all())
    return render_template('employer/job_applications.html',
                           job=job, applications=apps,
                           valid_statuses=VALID_STATUSES)


@employer_bp.route('/employer/applications/<int:app_id>/status', methods=['POST'])
@login_required
@_employer_required
def update_status(app_id):
    application = Application.query.get_or_404(app_id)
    job = application.job
    if job.employer_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('employer.dashboard'))

    new_status = request.form.get('status')
    if new_status not in VALID_STATUSES:
        flash('Invalid status.', 'danger')
        return redirect(url_for('employer.job_applications', job_id=job.id))

    old_status = application.status
    application.status         = new_status
    application.employer_notes = request.form.get('notes', application.employer_notes)
    db.session.commit()

    if old_status != new_status:
        try:
            mailer.notify_status_change(
                application.applicant.email,
                application.applicant.full_name,
                job, new_status,
            )
        except Exception:
            pass

    flash(f'Status updated to {new_status}.', 'success')
    return redirect(url_for('employer.job_applications', job_id=job.id))
