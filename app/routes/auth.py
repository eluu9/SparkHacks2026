import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from firebase_admin import auth as firebase_auth
from app.models.user import User
from app.extensions import mongo

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Routes
@bp.route('/login')
def login_page():
    return render_template('login.html')

@bp.route('/signup')
def signup_page():
    return render_template('signup.html')

@bp.route('/session-login', methods=['POST'])
def session_login():
    data = request.json
    id_token = data.get('idToken')
    
    if not id_token:
        return jsonify({'status': 'error', 'error': 'Missing ID token'}), 400

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_data = User.get_or_create(decoded_token)
        user = User(user_data)
        login_user(user, remember=True)
        session['is_secure_lab'] = True
        
        return jsonify({
            'status': 'success', 
            'user': user.username
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 401

@bp.route('/logout')
@login_required
def logout():
    session.pop('is_secure_lab', None)
    logout_user()
    return redirect(url_for('auth.login_page'))