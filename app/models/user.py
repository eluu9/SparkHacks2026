from datetime import datetime
from flask_login import UserMixin
from app.extensions import mongo

class User(UserMixin):
    def __init__(self, uid, email):
        self.id = uid
        self.email = email

    def __repr__(self):
        return f'<User {self.email}>'

    @staticmethod
    def get_or_create(token_data):
        # Token data comes from Firebase verify_id_token
        uid = token_data['uid']
        email = token_data.get('email')

        # Check if user exists, if not create them
        user_doc = mongo.db.users.find_one({"_id": uid})
        if not user_doc:
            mongo.db.users.insert_one({
                "_id": uid,
                "email": email,
                "created_at": datetime.utcnow()
            })
        
        return User(uid=uid, email=email)

    @staticmethod
    def get(user_id):
        # Flask-Login callback
        u = mongo.db.users.find_one({"_id": user_id})
        if u:
            return User(uid=u['_id'], email=u.get('email'))
        return None