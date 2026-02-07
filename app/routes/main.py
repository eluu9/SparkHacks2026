from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def root():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def index():
    return render_template('index.html')