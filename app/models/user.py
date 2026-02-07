from flask_login import UserMixin
from app.extensions import mongo

class User(UserMixin):
    def __init__(self, user_data):
        # We use the Firebase 'uid' as the main ID for consistency
        self.id = user_data.get('uid') or str(user_data.get('_id'))
        self.email = user_data.get('email')
        self.name = user_data.get('name')

    @staticmethod
    def get_or_create(decoded_token):
        user_collection = mongo.db.users
        uid = decoded_token.get('uid')
        
        # Look for the user by their unique Firebase UID
        user_data = user_collection.find_one({"uid": uid})
        
        if not user_data:
            user_data = {
                "uid": uid,
                "email": decoded_token.get('email'),
                "name": decoded_token.get('name', 'New User'),
                "created_at": decoded_token.get('iat')
            }
            user_collection.insert_one(user_data)
        
        return User(user_data)

    @staticmethod
    def get(user_id):
        # Flask-Login calls this to reload the user from the session
        user_data = mongo.db.users.find_one({"uid": user_id})
        return User(user_data) if user_data else None