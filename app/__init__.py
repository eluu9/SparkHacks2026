import os
from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from dotenv import load_dotenv
from .extensions import mongo, login_manager

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_shopping_kit')

    # Initialize Extensions
    mongo.init_app(app)
    login_manager.init_app(app)

    # 1. CONFIGURE LOGIN REDIRECT
    # This tells @login_required where to send users
    login_manager.login_view = 'auth.login_page'

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        print(f"DEBUG: Loading user with ID: {user_id}") 
        return User.get(user_id)

    # Register Blueprints
    from app.routes import auth, main, kit
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp) # Ensure main is registered
    app.register_blueprint(kit.bp)
    
    # 2. UPDATED ROOT ROUTE
   # Ensure this matches exactl

    return app