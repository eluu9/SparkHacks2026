from pymongo.database import Database
import time
import datetime
import requests
from bs4 import BeautifulSoup

class SearchService:
    def __init__(self, mongo_db=None):
        self.db = mongo_db
        self.lastRequestTime = 0
        if self.db:
            self.db.search_cache.create_index("created_at", expireAfterSeconds=86400)

    def rateLimit(self):
        elapsedTime = time.time() - self.lastRequestTime
        if elapsedTime < 0.5:
            time.sleep(0.5 - elapsedTime)
        self.lastRequestTime = time.time()

    def getFromCache(self, query: str, source: str):
        result = self.db.search_cache.find_one({"query": query, "source": source})
        if result:
            return result.get("results")
        return None

    def saveToCache(self, query: str, source: str, results):
        if self.db.search_cache.find_one({"query": query, "source": source}):
            self.db.search_cache.update_one(
                {"query": query, "source": source},
                {"$set": {"query": query, "source": source, "results": results, "created_at": datetime.datetime.now(datetime.timezone.utc)}})
        else:
            self.db.search_cache.insert_one({"query": query, "source": source, "results": results, "created_at": datetime.datetime.now(datetime.timezone.utc)})

    def searchAmazon(self, query: str):
        self.rateLimit()
        cachedResults = self.getFromCache(query, "amazon")
        if cachedResults:
            return cachedResults

        try:
            url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = BeautifulSoup(response.content, "html.parser")
                results = []

                products = data.find_all("div", {"data-component-type": "s-search-result"})[:20]
                for info in products:
                    try:
                        title_elem = info.h2.a.span if info.h2 and info.h2.a else None
                        title = title_elem.text.strip() if title_elem else ""
                        
                        price_elem = info.find('span', 'a-price-whole')
                        price = price_elem.text.strip() if price_elem else None

                        link = info.h2.a['href'] if info.h2 and info.h2.a else None
                        product_url = f"https://amazon.com{link}" if link else ""
                        
                        results.append({
                            "title": title, 
                            "price": price,
                            'url': product_url,
                            'source': 'amazon',
                        })
                    except Exception as e:
                        print(f"Amazon API error: {e}")
                        continue
                
                self.saveToCache(query, "amazon", results)
                return results
        except Exception as e:
            print(f"Amazon API error: {e}")
            return []
        
        return []
    
    def searchAllSources(self, query: str):
        alreadySeen = set()
        uniqueResults = []
        try:
            resultList = self.searchAmazon(query)
            for result in resultList:
                if result['url'] not in alreadySeen:
                    alreadySeen.add(result['url'])
                    uniqueResults.append(result)
                    print(f"Found in Amazon: {result['title']}")
            return uniqueResults
        
        except Exception as e:
            print(f"Error occurred while searching all sources: {e}")
            return []

    def search(self, query: str):
        return self.searchAllSources(query)
    