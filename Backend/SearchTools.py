import os
import datetime
import json
import time
import re
import hashlib
from googlesearch import search

# Cache directory for search results
CACHE_DIR = "Data/SearchCache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class SearchTools:
    """
    Stateless helper for Google Search and Caching.
    Extracted from RealtimeSearchEngine.py.
    """

    @staticmethod
    def get_cache_key(query):
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    @staticmethod
    def get_cached_results(query, cache_duration=3600):
        cache_key = SearchTools.get_cache_key(query)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Check validity
                cache_time = cache_data.get('timestamp', 0)
                if time.time() - cache_time < cache_duration:
                    return cache_data.get('results')
            except:
                pass
        return None

    @staticmethod
    def save_to_cache(query, results):
        cache_key = SearchTools.get_cache_key(query)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        cache_data = {
            'query': query,
            'timestamp': time.time(),
            'results': results
        }
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=4)
        except Exception as e:
            print(f"[SearchTools] Cache save error: {e}")

    @staticmethod
    def google_search(query, max_results=5, use_cache=True):
        """
        Perform Google search with caching.
        Returns formatted string.
        """
        if use_cache:
            cached = SearchTools.get_cached_results(query)
            if cached:
                return cached
        
        try:
            results = list(search(query, advanced=True, num_results=max_results))
            if not results:
                return ""
            
            # Format results
            answer = f"Search Results for '{query}':\n\n"
            for i, r in enumerate(results, start=1):
                title = r.title if hasattr(r, 'title') else "No title"
                url = r.url if hasattr(r, 'url') else (r.link if hasattr(r, 'link') else r)
                description = r.description if hasattr(r, 'description') else ""
                
                answer += f"[{i}] {title}\n"
                if description:
                    description = description[:200] + "..." if len(description) > 200 else description
                    answer += f"    {description}\n"
                answer += f"    Source: {url}\n\n"
            
            if use_cache:
                SearchTools.save_to_cache(query, answer)
            
            return answer
        except Exception as e:
            print(f"[SearchTools] Search error: {e}")
            return ""
