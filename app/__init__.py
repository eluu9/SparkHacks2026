# app/__init__.py
import os
import certifi # <--- IMPORT THIS
from flask import Flask
from dotenv import load_dotenv
from .extensions import mongo, login_manager

# Force load .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 1. Load Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # 2. Configure MongoDB with SSL Fix
    # If using Atlas, we MUST verify the SSL cert using certifi
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['MONGO_TLS_CA_FILE'] = certifi.where() # <--- CRITICAL FOR WINDOWS

    # 3. Debug Print (Check your terminal when you start the app!)
    print(f"DEBUG: Connecting to MongoDB at... {app.config['MONGO_URI'][:20]}...")

    # 4. Initialize Extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    
    # ... rest of your code (login_manager settings, blueprints) ...
    login_manager.login_view = 'auth.login_page'

    @app.after_request
    def add_header(response):
        # Allow the popup to communicate back to the main window
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    from app.routes import auth, main, kit
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(kit.bp)

    return app