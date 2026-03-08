"""
DEPRECATED MODULE
This file is deprecated as of Backend Consolidation Phase 3.
All functionality has been migrated to:
- Backend/SearchTools.py (Search Logic)
- Backend/AnswerEngine.py (LLM & Logic)

DO NOT MODIFY THIS FILE.
It is kept for archival purposes and rollback safety.
"""
import os
import datetime
import json
import time
import re
import hashlib
from collections import Counter
from googlesearch import search
from groq import Groq
from dotenv import dotenv_values
from Backend.Memory import MemoryManager  # ✅ Integrated Memory System

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Initialize Memory Manager
memory = MemoryManager()

# Ensure Data folder exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Cache directory for search results
CACHE_DIR = "Data/SearchCache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Query history for analytics
QUERY_HISTORY_PATH = "Data/QueryHistory.json"

# Enhanced system prompt
System = f"""
You are {Assistantname}, an advanced AI assistant helping {Username}.

Core Principles:
- Provide accurate, concise, and well-structured answers
- Use proper grammar, punctuation, and formatting
- Cite sources when using search results
- If information is uncertain, acknowledge it
- Be conversational yet professional
- Use bullet points for lists when appropriate
- Keep responses clear and easy to understand

Current Context:
- Always consider real-time information provided
- Prioritize recent and authoritative sources
- Distinguish between facts and opinions

IMPORTANT: If the user specifies a length constraint like "in two lines", "briefly", "in one sentence", "in three words", etc., you MUST strictly follow that constraint and keep your response within the specified length.
"""

# Function to get real-time date and time with more context
def Information():
    now = datetime.datetime.now()
    day_name = now.strftime('%A')
    month_name = now.strftime('%B')
    year = now.strftime('%Y')
    date = now.strftime('%d')
    hour = now.strftime('%H')
    minute = now.strftime('%M')
    
    # Determine time of day
    hour_int = int(hour)
    if 5 <= hour_int < 12:
        time_of_day = "morning"
    elif 12 <= hour_int < 17:
        time_of_day = "afternoon"
    elif 17 <= hour_int < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    return f"Current Real-Time Information:\nDay: {day_name}\nDate: {date} {month_name} {year}\nTime: {hour}:{minute} ({time_of_day})\n\nUse this information to provide contextually relevant answers."

# Cache management functions
def get_cache_key(query):
    """Generate a unique cache key for a query"""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

def get_cached_results(query, cache_duration=3600):
    """
    Get cached search results if available and fresh
    cache_duration: in seconds (default 1 hour)
    """
    cache_key = get_cache_key(query)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time < cache_duration:
                # print(f"[Cache] Using cached results for: {query}")
                return cache_data.get('results')
        except:
            pass
    return None

def save_to_cache(query, results):
    """Save search results to cache"""
    cache_key = get_cache_key(query)
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
        print(f"[Cache] Error saving: {e}")

# Enhanced Google Search with caching and better formatting
def GoogleSearch(query, max_results=5, use_cache=True):
    """
    Perform Google search with caching and enhanced result formatting
    """
    print(f"[Search] Searching for: {query}")
    
    # Check cache first
    if use_cache:
        cached_results = get_cached_results(query)
        if cached_results:
            return cached_results
    
    try:
        results = list(search(query, advanced=True, num_results=max_results))
        if not results:
            return ""
        
        # Format results with better structure
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
        
        # Save to cache
        if use_cache:
            save_to_cache(query, answer)
        
        return answer
    except Exception as e:
        error_msg = f"Search error: {str(e)}"
        print(f"[Search Error] {error_msg}")
        return ""

# Detect query type for better handling
def DetectQueryType(query):
    """Detect what type of query this is to optimize response"""
    query_lower = query.lower()
    if any(word in query_lower for word in ["vs", "versus", "compare", "difference between", "better than"]): return "comparison"
    if any(word in query_lower for word in ["news", "latest", "recent", "today", "yesterday", "breaking"]): return "news"
    if any(word in query_lower for word in ["weather", "temperature", "forecast", "rain", "sunny", "climate"]): return "weather"
    if any(word in query_lower for word in ["time", "date", "day", "when is", "what day"]): return "datetime"
    if any(word in query_lower for word in ["what is", "who is", "where is", "define", "meaning", "explain"]): return "factual"
    if any(word in query_lower for word in ["how to", "tutorial", "guide", "steps", "instructions"]): return "howto"
    if any(word in query_lower for word in ["list of", "top 10", "best", "recommended", "suggestions"]): return "list"
    if any(word in query_lower for word in ["calculate", "solve", "math", "equation", "convert"]): return "calculation"
    if any(word in query_lower for word in ["review", "opinion", "should i", "is it worth", "recommend"]): return "opinion"
    return "general"

# Advanced query preprocessing
def PreprocessQuery(query):
    """Clean and enhance the query for better search results"""
    query = ' '.join(query.split())
    query_lower = query.lower()
    if any(word in query_lower for word in ["latest", "recent", "today", "now"]):
        current_year = datetime.datetime.now().year
        if str(current_year) not in query:
            query = f"{query} {current_year}"
    return query

# Clean and modify AI response
def AnswerModifier(Answer):
    """Enhanced answer formatting"""
    lines = Answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    formatted = "\n".join(non_empty_lines)
    formatted = formatted.replace("</s>", "").strip()
    return formatted

# Response quality check
def ValidateResponse(response):
    """Check if response is valid and useful"""
    if not response or len(response) < 10: return False
    error_phrases = ["i don't have access", "i cannot browse", "as an ai", "i don't have real-time"]
    response_lower = response.lower()
    if any(phrase in response_lower for phrase in error_phrases): return False
    return True

# Main Realtime Search Engine function
def RealtimeSearchEngine(prompt, max_results=5, use_cache=True):
    """
    Enhanced realtime search - Now uses Centralized Memory.
    """
    print(f"\n[RealtimeSearch] Processing query: {prompt}")
    
    # 1. Get Context from Memory (includes STM and LTM)
    # Note: Search Engine specific system prompt + Memory Context
    enrichment, stm_history = memory.get_context()
    
    # Add Search Results
    search_results = GoogleSearch(prompt, max_results=max_results, use_cache=use_cache)
    if not search_results:
        search_context = f"No specific search results found for '{prompt}'. Provide a general answer."
    else:
        search_context = f"Use these search results to answer accurately:\n\n{search_results}\n\nProvide a detailed answer citing sources."
    
    # Build Messages Payload
    # System Prompt + [Memory Enrichment] + [Search Context] + [Realtime Info] + [STM] + [User Query]
    
    system_block = [
        {"role": "system", "content": System + enrichment},
        {"role": "system", "content": search_context},
        {"role": "system", "content": Information()}
    ]
    
    # Append current user query which is NOT in STM yet
    user_block = [{"role": "user", "content": prompt}]
    
    # Combined messages
    messages_payload = system_block + stm_history + user_block

    # Send request to Groq with retry logic
    max_retries = 2
    for attempt in range(max_retries):
        try:
            print(f"[RealtimeSearch] Thinking... (attempt {attempt + 1})")
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_payload,
                max_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                stream=True,
                stop=None
            )

            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content

            Answer = AnswerModifier(Answer)
            
            # Validate response quality
            if not ValidateResponse(Answer):
                if attempt < max_retries - 1:
                    print("[RealtimeSearch] Response quality low, retrying...")
                    continue
                else:
                    Answer = "I couldn't generate a satisfactory answer. Please try rephrasing your query."
            
            # ✅ SAVE TO MEMORY (Centralized State)
            memory.save_interaction(prompt, Answer)
            
            print(f"[RealtimeSearch] Response generated successfully")
            return Answer

        except Exception as e:
            print(f"[RealtimeSearch] Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                return f"I encountered an error processing your query. Please try again."

    return "Unable to process query after multiple attempts."

# Clear old cache (optional cleanup function)
def ClearOldCache(max_age_hours=24):
    """Remove cache files older than specified hours"""
    try:
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        for filename in os.listdir(CACHE_DIR):
            filepath = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
    except Exception as e:
        print(f"[Cache] Error clearing cache: {e}")

# Main loop for testing
if __name__ == "__main__":
    print(f"{Assistantname} Realtime Search Engine is online!\n")
    ClearOldCache()
    while True:
        prompt = input("\nEnter Your Query (or 'exit' to quit): ").strip()
        if prompt.lower() in ["exit", "quit", "bye"]: break
        if not prompt: continue
        
        answer = RealtimeSearchEngine(prompt)
        print(f"\n{Assistantname}: {answer}\n")
        print("-" * 60)
