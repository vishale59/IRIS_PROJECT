from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='jobseeker')  # jobseeker|employer|admin
    phone         = db.Column(db.String(20))
    location      = db.Column(db.String(100))
    bio           = db.Column(db.Text)
    degree        = db.Column(db.String(100))   # NEW: for categorization
    category      = db.Column(db.String(100))   # NEW: auto-detected category
    profile_pic   = db.Column(db.String(200), default='default.png')
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    resumes      = db.relationship('Resume', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', cascade='all, delete-orphan')
    jobs_posted  = db.relationship('Job', backref='poster', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Resume(db.Model):
    __tablename__ = 'resumes'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename      = db.Column(db.String(200), nullable=False)
    original_name = db.Column(db.String(200))
    file_path     = db.Column(db.String(500))
    extracted_text= db.Column(db.Text)
    ats_score     = db.Column(db.Float, default=0.0)
    matched_skills= db.Column(db.Text)   # JSON
    missing_skills= db.Column(db.Text)   # JSON
    suggestions   = db.Column(db.Text)   # JSON
    detected_category = db.Column(db.String(100))  # NEW
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)
    is_primary    = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Resume {self.filename}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id               = db.Column(db.Integer, primary_key=True)
    employer_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title            = db.Column(db.String(200), nullable=False)
    company          = db.Column(db.String(200), nullable=False)
    location         = db.Column(db.String(100))
    job_type         = db.Column(db.String(50), default='Full-time')
    salary_min       = db.Column(db.Integer)
    salary_max       = db.Column(db.Integer)
    description      = db.Column(db.Text, nullable=False)
    requirements     = db.Column(db.Text)
    skills_required  = db.Column(db.Text)   # comma-separated
    experience_level = db.Column(db.String(50), default='Entry')
    category         = db.Column(db.String(100))
    is_active        = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    deadline         = db.Column(db.DateTime)

    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.title} @ {self.company}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id          = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    resume_id       = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    cover_letter    = db.Column(db.Text)
    # Status: Applied → Reviewed → Selected → Rejected  (also: shortlisted, hired)
    status          = db.Column(db.String(30), default='Applied')
    ats_match_score = db.Column(db.Float, default=0.0)
    applied_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employer_notes  = db.Column(db.Text)

    resume = db.relationship('Resume', backref='applications')

    def __repr__(self):
        return f'<Application user={self.user_id} job={self.job_id}>'
