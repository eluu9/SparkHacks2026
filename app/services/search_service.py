"""Product search service with caching and rate limiting."""

import datetime
import json
import os
import time

import requests


class SearchService:
    """Searches external shopping APIs and caches results in MongoDB."""

    def __init__(self, mongo_db=None):
        self.db = mongo_db
        self.last_request_time = 0
        if self.db is not None:
            self.db.search_cache.create_index(
                "created_at", expireAfterSeconds=86400
            )

    # -- Rate limiting & caching helpers --

    def _rate_limit(self):
        """Ensure at least 0.5 s between consecutive API calls."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        self.last_request_time = time.time()

    def _get_from_cache(self, query, source):
        if self.db is not None:
            result = self.db.search_cache.find_one(
                {"query": query, "source": source}
            )
            if result:
                return result.get("results")
        return None

    def _save_to_cache(self, query, source, results):
        if self.db is None:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        if self.db.search_cache.find_one({"query": query, "source": source}):
            self.db.search_cache.update_one(
                {"query": query, "source": source},
                {"$set": {"results": results, "created_at": now}},
            )
        else:
            self.db.search_cache.insert_one({
                "query": query,
                "source": source,
                "results": results,
                "created_at": now,
            })

    # -- External API calls --

    def _search_google_shopping(self, query):
        """Fetch shopping results from Google via the Serper API."""
        self._rate_limit()
        cached = self._get_from_cache(query, "google_shopping")
        if cached:
            return cached

        url = "https://google.serper.dev/shopping"
        api_key = os.getenv("SERPER_API_KEY")

        payload = json.dumps({"q": query})
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url, headers=headers, data=payload, timeout=10
            )
            if response.status_code != 200:
                print(f"Serper API Error {response.status_code}")
                return []

            data = response.json()
            results = []
            for item in data.get("shopping", [])[:8]:
                results.append({
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "img_url": item.get("imageUrl"),
                    "url": item.get("link"),
                    "source": item.get("source", "google_shopping"),
                })

            self._save_to_cache(query, "google_shopping", results)
            return results
        except Exception as exc:
            print(f"Serper request failed: {exc}")

        return []

    # -- Public interface --

    def _search_all_sources(self, query):
        """Aggregate and deduplicate results across all sources."""
        unique_results = []
        try:
            result_list = self._search_google_shopping(query)
            seen_titles = set()
            for result in result_list:
                if result["title"] not in seen_titles:
                    seen_titles.add(result["title"])
                    unique_results.append(result)
            return unique_results
        except Exception as exc:
            print(f"Error in _search_all_sources: {exc}")
            return []

    def search(self, query):
        """Entry point — returns deduplicated product results."""
        return self._search_all_sources(query)