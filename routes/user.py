import os
import json
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db, Resume, Job, Application
from services.resume_parser import extract_text_from_resume
from services.ats_analyzer import analyze_resume, extract_skills_from_text, clean_text
from services.job_recommender import recommend_jobs, suggest_jobs_from_resume_text
from services.categorizer import final_category
from services import mailer

user_bp = Blueprint('user', __name__)
ALLOWED = {'pdf', 'docx', 'doc'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ('jobseeker',):
        return redirect(url_for('auth.login'))

    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    applications = (Application.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Application.applied_at.desc())
                    .limit(5).all())

    recommended = []
    extracted_skills = []
    role_suggestions = {
        'recommended': [],
        'alternative': [],
        'primary': [],
        'details': [],
        'best_match': None,
    }
    primary = next((r for r in resumes if r.is_primary), resumes[0] if resumes else None)
    if primary and primary.extracted_text:
        all_jobs = Job.query.filter_by(is_active=True).all()
        recommended = recommend_jobs(primary.extracted_text, all_jobs, top_n=6)
        extracted_skills = extract_skills_from_text(clean_text(primary.extracted_text))
        role_suggestions = suggest_jobs_from_resume_text(primary.extracted_text)

    stats = {
        'total_applications': Application.query.filter_by(user_id=current_user.id).count(),
        'pending':     Application.query.filter_by(user_id=current_user.id, status='Applied').count(),
        'shortlisted': Application.query.filter_by(user_id=current_user.id, status='Selected').count(),
        'hired':       Application.query.filter_by(user_id=current_user.id, status='Hired').count(),
    }

    return render_template('user/dashboard.html',
                           resumes=resumes,
                           applications=applications,
                           recommended=recommended,
                           extracted_skills=extracted_skills,
                           role_suggestions=role_suggestions,
                           stats=stats,
                           primary_resume=primary)


@user_bp.route('/resume/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        jd_text = request.form.get('job_description', '')
        degree  = request.form.get('degree', '').strip()

        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not _allowed_file(file.filename):
            flash('Unsupported format. Please upload PDF or DOCX.', 'danger')
            return redirect(request.url)

        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)

        try:
            text = extract_text_from_resume(save_path)
        except Exception as e:
            os.remove(save_path)
            flash(f'Could not read resume: {str(e)}', 'danger')
            return redirect(request.url)

        if not text or len(text.strip()) < 50:
            os.remove(save_path)
            flash('Resume appears empty or unreadable. Please upload a text-based PDF/DOCX.', 'danger')
            return redirect(request.url)

        result   = analyze_resume(text, jd_text)
        category = final_category(degree, text)

        # Update user degree/category if provided
        if degree:
            current_user.degree   = degree
            current_user.category = category

        Resume.query.filter_by(user_id=current_user.id, is_primary=True).update({'is_primary': False})

        resume = Resume(
            user_id=current_user.id,
            filename=unique_name,
            original_name=secure_filename(file.filename),
            file_path=save_path,
            extracted_text=text,
            ats_score=result['ats_score'],
            matched_skills=json.dumps(result['matched_skills']),
            missing_skills=json.dumps(result['missing_skills']),
            suggestions=json.dumps(result['suggestions']),
            detected_category=category,
            is_primary=True,
        )
        db.session.add(resume)
        db.session.commit()

        flash('Resume uploaded and analyzed successfully!', 'success')
        return redirect(url_for('user.resume_result', resume_id=resume.id))

    return render_template('user/upload_resume.html')


@user_bp.route('/resume/<int:resume_id>')
@login_required
def resume_result(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('user.dashboard'))

    matched     = json.loads(resume.matched_skills or '[]')
    missing     = json.loads(resume.missing_skills or '[]')
    suggestions = json.loads(resume.suggestions    or '[]')
    job_suggestions = suggest_jobs_from_resume_text(resume.extracted_text)

    return render_template('user/resume_result.html',
                           resume=resume,
                           matched=matched,
                           missing=missing,
                           suggestions=suggestions,
                           job_suggestions=job_suggestions)


@user_bp.route('/jobs')
@login_required
def job_listings():
    search   = request.args.get('q', '')
    location = request.args.get('location', '')
    job_type = request.args.get('type', '')
    category = request.args.get('category', '')

    query = Job.query.filter_by(is_active=True)
    if search:
        query = query.filter(
            db.or_(Job.title.ilike(f'%{search}%'),
                   Job.company.ilike(f'%{search}%'),
                   Job.description.ilike(f'%{search}%'))
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter_by(job_type=job_type)
    if category:
        query = query.filter(Job.category.ilike(f'%{category}%'))

    jobs = query.order_by(Job.created_at.desc()).all()
    applied_ids = {a.job_id for a in Application.query.filter_by(user_id=current_user.id).all()}

    return render_template('user/job_listings.html',
                           jobs=jobs,
                           applied_ids=applied_ids,
                           search=search,
                           location=location,
                           job_type=job_type,
                           category=category)


@user_bp.route('/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    already_applied = Application.query.filter_by(
        user_id=current_user.id, job_id=job_id).first() is not None

    skill_gap = None
    primary = next((r for r in resumes if r.is_primary), resumes[0] if resumes else None)
    if primary and primary.extracted_text:
        from services.job_recommender import get_skill_gap
        skill_gap = get_skill_gap(primary.extracted_text, job)

    return render_template('user/job_detail.html',
                           job=job,
                           resumes=resumes,
                           already_applied=already_applied,
                           skill_gap=skill_gap)


@user_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)

    if Application.query.filter_by(user_id=current_user.id, job_id=job_id).first():
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('user.job_detail', job_id=job_id))

    resume_id    = request.form.get('resume_id')
    cover_letter = request.form.get('cover_letter', '')

    resume    = None
    ats_match = 0.0
    if resume_id:
        resume = Resume.query.get(int(resume_id))
        if resume and resume.user_id == current_user.id and resume.extracted_text:
            jd_text   = f"{job.title} {job.description} {job.skills_required or ''}"
            result    = analyze_resume(resume.extracted_text, jd_text)
            ats_match = result['ats_score']

    application = Application(
        user_id=current_user.id,
        job_id=job_id,
        resume_id=resume.id if resume else None,
        cover_letter=cover_letter,
        ats_match_score=ats_match,
        status='Applied',
    )
    db.session.add(application)
    db.session.commit()

    try:
        mailer.notify_application_submitted(current_user.email, current_user.full_name, job)
        employer = job.poster
        if employer:
            mailer.notify_application_received(current_user, job, employer.email)
    except Exception:
        pass

    flash(f'Application submitted for {job.title}!', 'success')
    return redirect(url_for('user.my_applications'))


@user_bp.route('/my-applications')
@login_required
def my_applications():
    applications = (Application.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Application.applied_at.desc())
                    .all())
    return render_template('user/my_applications.html', applications=applications)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone     = request.form.get('phone', '').strip()
        current_user.location  = request.form.get('location', '').strip()
        current_user.bio       = request.form.get('bio', '').strip()
        current_user.degree    = request.form.get('degree', '').strip()
        # Recalculate category if degree changed
        if current_user.degree:
            from services.categorizer import detect_degree_category
            cat = detect_degree_category(current_user.degree)
            if cat:
                current_user.category = cat
        db.session.commit()
        flash('Profile updated.', 'success')
    return render_template('user/profile.html')
