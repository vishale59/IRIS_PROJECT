"""Authentication routes for registration, login, and logout."""

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """Require an authenticated session before allowing access."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def roles_required(*allowed_roles):
    """Limit access to a specific set of roles."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "error")
                return redirect(url_for("auth.login"))
            if session.get("user_role") not in allowed_roles:
                flash("You do not have permission to access that page.", "error")
                return redirect(url_for("auth.login"))
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Create a new user or employer account."""
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        if role not in {"user", "employer"}:
            flash("Invalid account type selected.", "error")
            return render_template("auth/register.html")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("A user with that username or email already exists.", "error")
            return render_template("auth/register.html")

        try:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please sign in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("Unable to create your account right now.", "error")

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user and create a session."""
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        session.clear()
        session["user_id"] = user.id
        session["user_role"] = user.role
        session["username"] = user.username
        flash("Welcome back.", "success")
        return redirect(url_for("index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Clear the active session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
