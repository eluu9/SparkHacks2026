"""Flask application factory."""

import os

import certifi
from dotenv import load_dotenv
from flask import Flask

from .extensions import login_manager, mongo

load_dotenv()


def create_app():
    """Create and configure the Flask app instance."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-123")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["MONGO_TLS_CA_FILE"] = certifi.where()

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_page"

    # Allow Firebase popup auth to communicate with this origin
    @app.after_request
    def add_header(response):
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        return response

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register route blueprints
    from app.routes import auth, main, kit
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(kit.bp)

    return app