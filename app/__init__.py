import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import mongo, login_manager

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    
    # DB connection - fallback to local if cloud fails
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("!! No MONGO_URI found, using localhost !!")
        mongo_uri = 'mongodb://localhost:27017/ai_shopping_kit'
    
    app.config['MONGO_URI'] = mongo_uri

    # Init extensions
    mongo.init_app(app)
    login_manager.init_app(app)

    # Need to import models here to avoid circular imports
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Blueprints
    from app.routes import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def index():
        # TODO: Replace this with a real landing page later
        return "API is live. Go to <a href='/auth/login'>/auth/login</a>"

    return app