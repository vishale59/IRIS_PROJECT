from flasgger import swag_from
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token

from app import db
from app.docs.swagger_docs import AUTH_LOGIN_DOC, AUTH_REGISTER_DOC
from app.models.user_model import User

auth_bp = Blueprint("auth_bp", __name__)
ALLOWED_ROLES = {"admin", "employer", "jobseeker"}


@auth_bp.post("/register")
@swag_from(AUTH_REGISTER_DOC)
def register():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "password", "role"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    role = str(data.get("role", "")).lower().strip()
    if role not in ALLOWED_ROLES:
        return jsonify({"error": "Role must be admin, employer, or jobseeker"}), 400

    if User.query.filter_by(email=data["email"].strip().lower()).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        name=data["name"].strip(),
        email=data["email"].strip().lower(),
        role=role,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.post("/login")
@swag_from(AUTH_LOGIN_DOC)
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        current_app.logger.warning("Failed login attempt for email=%s", email)
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name},
    )

    current_app.logger.info("Successful login for user_id=%s role=%s", user.id, user.role)

    return jsonify(
        {
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        }
    ), 200