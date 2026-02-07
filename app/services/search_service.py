import os
import json
from pymongo.database import Database
import time
import datetime
import requests
from bs4 import BeautifulSoup


class SearchService:
    def __init__(self, mongo_db=None):
        self.db = mongo_db
        self.lastRequestTime = 0
        # FIXED: Explicit comparison for PyMongo compatibility
        if self.db is not None:
            self.db.search_cache.create_index("created_at", expireAfterSeconds=86400)

    def rateLimit(self):
        elapsedTime = time.time() - self.lastRequestTime
        if elapsedTime < 0.5:
            time.sleep(0.5 - elapsedTime)
        self.lastRequestTime = time.time()

    def getFromCache(self, query: str, source: str):
        # FIXED: Explicit comparison
        if self.db is not None:
            result = self.db.search_cache.find_one({"query": query, "source": source})
            if result:
                return result.get("results")
        return None

    def saveToCache(self, query: str, source: str, results):
        # FIXED: Explicit comparison
        if self.db is not None:
            if self.db.search_cache.find_one({"query": query, "source": source}):
                self.db.search_cache.update_one(
                    {"query": query, "source": source},
                    {"$set": {
                        "results": results, 
                        "created_at": datetime.datetime.now(datetime.timezone.utc)
                    }}
                )
            else:
                self.db.search_cache.insert_one({
                    "query": query, 
                    "source": source, 
                    "results": results, 
                    "created_at": datetime.datetime.now(datetime.timezone.utc)
                })

    def searchGoogleShopping(self, query: str):
        self.rateLimit()
        cachedResults = self.getFromCache(query, "google_shopping")
        if cachedResults: return cachedResults

        url = "https://google.serper.dev/shopping"
        
        # Get your key from .env
        api_key = os.getenv("SERPER_API_KEY") 
        
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []

                # Serper returns a clean 'shopping' array
                for item in data.get('shopping', [])[:8]:
                    results.append({
                        "title": item.get('title'),
                        "price": item.get('price'),
                        "img_url": item.get('imageUrl'),
                        "url": item.get('link'),
                        "source": item.get('source', 'google_shopping')
                    })
                
                self.saveToCache(query, "google_shopping", results)
                return results
            else:
                print(f"DEBUG: Serper API Error {response.status_code}")
        except Exception as e:
            print(f"DEBUG: Serper logic crash: {e}")
        
        return []
    def searchAllSources(self, query: str):
        uniqueResults = []
        try:
            # CHANGE: Call searchGoogleShopping instead of searchAmazon
            resultList = self.searchGoogleShopping(query)
            
            seen_titles = set()
            for result in resultList:
                if result['title'] not in seen_titles:
                    seen_titles.add(result['title'])
                    uniqueResults.append(result)
            return uniqueResults
        except Exception as e:
            print(f"Error in searchAllSources: {e}")
            return []

    def search(self, query: str):
        # This now points to searchAllSources -> searchGoogleShopping
        return self.searchAllSources(query)