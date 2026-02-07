import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import mongo

app = create_app()

with app.app_context():
    print(f"Connecting to: {mongo.db.name}")
    mongo.db.search_cache.create_index("created_at", expireAfterSeconds=86400)
    print("Indexes created successfully!")