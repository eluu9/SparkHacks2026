"""Shared extension instances (Mongo, LoginManager, Firebase)."""

import json
import os

import certifi
import firebase_admin
from firebase_admin import credentials
from flask_login import LoginManager
from flask_pymongo import PyMongo

mongo = PyMongo(tlsCAFile=certifi.where())

login_manager = LoginManager()
login_manager.login_view = "auth.login_page"

# Initialize Firebase from env var JSON or local key file
if not firebase_admin._apps:
    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    cred_path = os.environ.get("FIREBASE_CREDENTIALS", "firebase-key.json")

    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred)
    elif os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)