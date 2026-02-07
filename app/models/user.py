"""User model backed by MongoDB and Flask-Login."""

from flask_login import UserMixin

from app.extensions import mongo


class User(UserMixin):
    """Represents an authenticated user loaded from MongoDB."""

    def __init__(self, user_data):
        self.id = str(user_data.get("uid"))
        self.name = (
            user_data.get("name")
            or user_data.get("username")
            or "Lab Lead"
        )
        self.username = user_data.get("username") or user_data.get("email")
        self.email = user_data.get("email")

    @staticmethod
    def get(user_id):
        """Look up a user by UID; returns None if not found."""
        user_data = mongo.db.users.find_one({"uid": user_id})
        return User(user_data) if user_data else None

    @staticmethod
    def get_or_create(decoded_token):
        """Find an existing user or insert a new document from a Firebase token."""
        uid = decoded_token["uid"]
        user_data = mongo.db.users.find_one({"uid": uid})
        if not user_data:
            user_data = {
                "uid": uid,
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name", "Lab Lead"),
                "username": decoded_token.get("email", "user").split("@")[0],
            }
            mongo.db.users.insert_one(user_data)
        return user_data