import os
from flask import Flask
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

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register Blueprints
    from app.routes import auth, main, kit
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(kit.bp)

    return app