from flask_login import UserMixin
from app.extensions import mongo

class User(UserMixin):
    def __init__(self, user_data):
        # Using Firebase UID as the unique session ID
        self.id = str(user_data.get('uid')) 
        # Adding 'name' so Jinja2 doesn't throw an UndefinedError
        self.name = user_data.get('name') or user_data.get('username') or "Lab Lead"
        self.username = user_data.get('username') or user_data.get('email')
        self.email = user_data.get('email')

    @staticmethod
    def get(user_id):
        # Flask-Login calls this to reload the user from the session ID
        user_data = mongo.db.users.find_one({"uid": user_id})
        return User(user_data) if user_data else None

    @staticmethod
    def get_or_create(decoded_token):
        uid = decoded_token['uid']
        user_data = mongo.db.users.find_one({"uid": uid})
        if not user_data:
            user_data = {
                "uid": uid,
                "email": decoded_token.get('email'),
                "name": decoded_token.get('name', 'Lab Lead'),
                "username": decoded_token.get('email', 'user').split('@')[0]
            }
            mongo.db.users.insert_one(user_data)
        return user_data