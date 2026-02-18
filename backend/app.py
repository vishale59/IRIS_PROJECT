from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root123@localhost:3306/iris_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(50), nullable=False)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default="Applied")


with app.app_context():
    db.create_all()

# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role=data["role"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Incorrect password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role
        }
    })


# ================= CREATE JOB =================

@app.route("/create-job", methods=["POST"])
def create_job():
    data = request.get_json()

    employer = User.query.get(data["employer_id"])

    if not employer or employer.role != "employer":
        return jsonify({"error": "Only employer can create jobs"}), 403

    job = Job(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        employer_id=data["employer_id"]
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created successfully"}), 201


# ================= VIEW JOBS =================

@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = Job.query.all()

    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "location": j.location,
            "employer_id": j.employer_id
        }
        for j in jobs
    ])


# ================= APPLY JOB =================

@app.route("/apply-job", methods=["POST"])
def apply_job():
    data = request.get_json()

    user = User.query.get(data["user_id"])
    job = Job.query.get(data["job_id"])

    if not user or user.role != "jobseeker":
        return jsonify({"error": "Only jobseeker can apply"}), 403

    if not job:
        return jsonify({"error": "Job not found"}), 404

    if Application.query.filter_by(user_id=user.id, job_id=job.id).first():
        return jsonify({"error": "Already applied"}), 400

    application = Application(
        user_id=user.id,
        job_id=job.id
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Applied successfully"}), 201


# ================= VIEW APPLICATIONS =================

@app.route("/applications", methods=["GET"])
def get_applications():
    applications = Application.query.all()

    return jsonify([
        {
            "id": a.id,
            "user_id": a.user_id,
            "job_id": a.job_id,
            "status": a.status
        }
        for a in applications
    ])


# ================= DASHBOARD =================

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify({
        "total_users": User.query.count(),
        "total_jobs": Job.query.count(),
        "total_applications": Application.query.count()
    })


if __name__ == "__main__":
    app.run(debug=True)
