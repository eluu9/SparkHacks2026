import os
from dotenv import load_dotenv

# Load env vars from project root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this')
    
    # Database config
    MONGO_URI = os.getenv('MONGO_URI')
    
    if not MONGO_URI:
        # Fallback for local development
        MONGO_URI = 'mongodb://localhost:27017/ai_shopping_kit'
        print(f"!! Using Local DB: {MONGO_URI}")

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False # set to True in prod