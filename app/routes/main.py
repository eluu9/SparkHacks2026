"""Top-level page routes (root redirect and dashboard)."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

bp = Blueprint("main", __name__)


@bp.route("/")
def root():
    """Redirect to login or dashboard based on auth state."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login_page"))
    return redirect(url_for("main.index"))


@bp.route("/dashboard")
@login_required
def index():
    return render_template("index.html")