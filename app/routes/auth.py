"""Authentication routes (login, signup, session management)."""

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from firebase_admin import auth as firebase_auth

from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login")
def login_page():
    return render_template("login.html")


@bp.route("/signup")
def signup_page():
    return render_template("signup.html")


@bp.route("/session-login", methods=["POST"])
def session_login():
    """Verify a Firebase ID token and start a Flask session."""
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")

    if not id_token:
        return jsonify({"status": "error", "error": "Missing ID token"}), 400

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_data = User.get_or_create(decoded_token)
        user = User(user_data)
        login_user(user, remember=True)
        session["is_secure_lab"] = True

        return jsonify({"status": "success", "user": user.username})

    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 401


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))
    session.clear()
    return redirect(url_for('auth.login_page'))