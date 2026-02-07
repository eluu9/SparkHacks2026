import os
import certifi
from flask_pymongo import PyMongo
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials

mongo = PyMongo(tlsCAFile=certifi.where())

login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'

if not firebase_admin._apps:
    cred_path = os.environ.get('FIREBASE_CREDENTIALS', 'firebase-key.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)