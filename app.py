import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager

from config import config
from models import db, User
from services.mailer import mail


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.employer import employer_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('errors/413.html'), 413

    with app.app_context():
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    with app.app_context():
        admin = User.query.filter_by(email='admin@iris.com').first()
        if not admin:
            admin = User(full_name='IRIS Admin', email='admin@iris.com', role='admin')
            admin.set_password('Admin@1234')
            db.session.add(admin)

        employer = User.query.filter_by(email='employer@iris.com').first()
        if not employer:
            employer = User(full_name='TechCorp HR', email='employer@iris.com', role='employer')
            employer.set_password('Employer@1234')
            db.session.add(employer)

        jobseeker = User.query.filter_by(email='jobseeker@iris.com').first()
        if not jobseeker:
            jobseeker = User(
                full_name='Aarav Sharma',
                email='jobseeker@iris.com',
                role='jobseeker',
                degree='B.Tech Computer Science',
                category='Engineering',
            )
            jobseeker.set_password('Jobseeker@1234')
            db.session.add(jobseeker)

        db.session.flush()

        from models import Job
        if employer.jobs_posted.count() == 0:
            demo_jobs = [
                Job(employer_id=employer.id, title='Senior Python Developer',
                    company='TechCorp', location='Bangalore, India',
                    job_type='Full-time', experience_level='Senior', category='Engineering',
                    skills_required='python,flask,django,sql,docker,aws',
                    description='We are looking for a senior Python developer to join our backend team. You will design scalable APIs, work with microservices, and mentor junior developers.',
                    requirements='5+ years Python. Strong Flask/Django. Cloud (AWS/GCP). Problem-solving skills.'),
                Job(employer_id=employer.id, title='React Frontend Engineer',
                    company='TechCorp', location='Remote',
                    job_type='Remote', experience_level='Mid', category='Engineering',
                    skills_required='react,typescript,javascript,css,html,git',
                    description='Build beautiful, performant UIs for our SaaS platform used by thousands of customers.',
                    requirements='3+ years React. TypeScript proficiency. Eye for design.'),
                Job(employer_id=employer.id, title='Data Scientist',
                    company='DataAI Labs', location='Hyderabad, India',
                    job_type='Full-time', experience_level='Mid', category='Data Science',
                    skills_required='python,machine learning,pandas,numpy,scikit-learn,sql,tensorflow',
                    description='Drive data-driven decisions by building ML models and analytical pipelines.',
                    requirements='3+ years data science. Python, ML frameworks. Strong statistics.'),
                Job(employer_id=employer.id, title='DevOps Engineer',
                    company='CloudScale', location='Mumbai, India',
                    job_type='Full-time', experience_level='Senior', category='DevOps',
                    skills_required='docker,kubernetes,aws,terraform,jenkins,linux,ci/cd',
                    description='Own and evolve our cloud infrastructure. Build CI/CD pipelines, manage Kubernetes clusters.',
                    requirements='4+ years DevOps. Kubernetes preferred. AWS/GCP expertise.'),
                Job(employer_id=employer.id, title='UI/UX Designer',
                    company='DesignStudio', location='Pune, India',
                    job_type='Contract', experience_level='Mid', category='Design',
                    skills_required='figma,css,html,user research,prototyping,adobe',
                    description='Create compelling user experiences for mobile and web applications.',
                    requirements='Portfolio required. 2+ years product design. Figma expert.'),
                Job(employer_id=employer.id, title='Finance Analyst',
                    company='FinCorp', location='Mumbai, India',
                    job_type='Full-time', experience_level='Mid', category='Finance',
                    skills_required='accounting,excel,financial modeling,tally,gst,taxation',
                    description='Analyse financial data, prepare reports and support strategic decisions.',
                    requirements='BCom/MBA Finance. 2+ years. Excel proficiency. CA preferred.'),
            ]
            for j in demo_jobs:
                db.session.add(j)

        db.session.commit()


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
