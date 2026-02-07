from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required
from firebase_admin import auth as firebase_auth
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login_page():
    return render_template('login.html')

@bp.route('/session-login', methods=['POST'])
def session_login():
    # Frontend sends the Firebase ID token here
    data = request.json
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({'error': 'Missing ID token'}), 400

    try:
        # Verify with Firebase Admin
        decoded_token = firebase_auth.verify_id_token(id_token)
        
        # Sync user to our DB
        user = User.get_or_create(decoded_token)
        
        # Establish Flask session
        login_user(user, remember=True)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"!! Auth Failed: {e}")
        return jsonify({'error': 'Invalid token'}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))