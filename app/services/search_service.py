from pymongo import MongoClient
from pymongo.database import Database

class searchService:
    def __init__(self):
        self.db = mongo_db
    def searchOpenLibrary(self, query: str):
        