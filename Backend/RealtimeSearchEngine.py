import os
import datetime
import json
from json import load, dump
from googlesearch import search
from groq import Groq
from dotenv import dotenv_values
import hashlib
import time
import re
from collections import Counter

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Ensure Data folder exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Cache directory for search results
CACHE_DIR = "Data/SearchCache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Query history for analytics
QUERY_HISTORY_PATH = "Data/QueryHistory.json"

# Fact checking database
FACT_CHECK_PATH = "Data/FactCheck.json"

# Initialize ChatLog
ChatLogPath = r"Data\ChatLog.json"
try:
    with open(ChatLogPath, "r", encoding='utf-8') as f:
        messages = load(f)
except:
    messages = []
    with open(ChatLogPath, "w", encoding='utf-8') as f:
        dump(messages, f, indent=4)

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
"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": f"Hello {Username}, I'm here to help. What would you like to know?"}
]

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
    
    return f"""Current Real-Time Information:
Day: {day_name}
Date: {date} {month_name} {year}
Time: {hour}:{minute} ({time_of_day})

Use this information to provide contextually relevant answers."""

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
                print(f"[Cache] Using cached results for: {query}")
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
        print(f"[Cache] Saved results for: {query}")
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
                # Limit description length
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
    """
    Detect what type of query this is to optimize response
    """
    query_lower = query.lower()
    
    # Comparison queries
    if any(word in query_lower for word in ["vs", "versus", "compare", "difference between", "better than"]):
        return "comparison"
    
    # News-related queries
    if any(word in query_lower for word in ["news", "latest", "recent", "today", "yesterday", "breaking"]):
        return "news"
    
    # Weather queries
    if any(word in query_lower for word in ["weather", "temperature", "forecast", "rain", "sunny", "climate"]):
        return "weather"
    
    # Time/date queries
    if any(word in query_lower for word in ["time", "date", "day", "when is", "what day"]):
        return "datetime"
    
    # Factual queries
    if any(word in query_lower for word in ["what is", "who is", "where is", "define", "meaning", "explain"]):
        return "factual"
    
    # How-to queries
    if any(word in query_lower for word in ["how to", "tutorial", "guide", "steps", "instructions"]):
        return "howto"
    
    # List queries
    if any(word in query_lower for word in ["list of", "top 10", "best", "recommended", "suggestions"]):
        return "list"
    
    # Calculation/Math
    if any(word in query_lower for word in ["calculate", "solve", "math", "equation", "convert"]):
        return "calculation"
    
    # Opinion/Review queries
    if any(word in query_lower for word in ["review", "opinion", "should i", "is it worth", "recommend"]):
        return "opinion"
    
    return "general"


# Advanced query preprocessing
def PreprocessQuery(query):
    """
    Clean and enhance the query for better search results
    """
    # Remove extra spaces
    query = ' '.join(query.split())
    
    # Add context for ambiguous queries
    query_lower = query.lower()
    
    # If asking about current events, add temporal context
    if any(word in query_lower for word in ["latest", "recent", "today", "now"]):
        current_year = datetime.datetime.now().year
        if str(current_year) not in query:
            query = f"{query} {current_year}"
    
    return query


# Multi-source search aggregation
def MultiSourceSearch(query, max_results=5):
    """
    Search multiple sources and aggregate results
    """
    all_results = []
    
    # Google Search
    try:
        google_results = list(search(query, advanced=True, num_results=max_results))
        all_results.extend(google_results)
    except Exception as e:
        print(f"[MultiSearch] Google error: {e}")
    
    return all_results


# Extract key information from search results
def ExtractKeyInfo(search_results_text):
    """
    Extract important information like dates, numbers, names
    """
    key_info = {
        "dates": [],
        "numbers": [],
        "urls": []
    }
    
    # Extract dates (basic patterns)
    date_patterns = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}\b'
    key_info["dates"] = re.findall(date_patterns, search_results_text)
    
    # Extract numbers with context
    number_patterns = r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|thousand|%|percent)?\b'
    key_info["numbers"] = re.findall(number_patterns, search_results_text, re.IGNORECASE)
    
    # Extract URLs
    url_patterns = r'https?://[^\s]+'
    key_info["urls"] = re.findall(url_patterns, search_results_text)
    
    return key_info


# Query analytics and tracking
def TrackQuery(query, query_type, response_time):
    """
    Track query statistics for analytics
    """
    try:
        if os.path.exists(QUERY_HISTORY_PATH):
            with open(QUERY_HISTORY_PATH, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append({
            "timestamp": time.time(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "type": query_type,
            "response_time": response_time
        })
        
        # Keep only last 1000 queries
        if len(history) > 1000:
            history = history[-1000:]
        
        with open(QUERY_HISTORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Analytics] Error tracking query: {e}")


# Get query statistics
def GetQueryStats():
    """
    Get analytics about query usage
    """
    try:
        if not os.path.exists(QUERY_HISTORY_PATH):
            return None
        
        with open(QUERY_HISTORY_PATH, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if not history:
            return None
        
        types = [q['type'] for q in history]
        type_counts = Counter(types)
        
        avg_response_time = sum(q.get('response_time', 0) for q in history) / len(history)
        
        stats = {
            "total_queries": len(history),
            "query_types": dict(type_counts),
            "avg_response_time": round(avg_response_time, 2),
            "most_common_type": type_counts.most_common(1)[0] if type_counts else None
        }
        
        return stats
    except Exception as e:
        print(f"[Analytics] Error getting stats: {e}")
        return None


# Source credibility checker
def CheckSourceCredibility(url):
    """
    Basic credibility check for sources
    """
    trusted_domains = [
        'wikipedia.org', 'britannica.com', 'nature.com', 'science.org',
        'reuters.com', 'apnews.com', 'bbc.com', 'cnn.com',
        'nytimes.com', 'theguardian.com', 'forbes.com',
        'gov', 'edu', 'ieee.org', 'acm.org'
    ]
    
    url_lower = url.lower()
    
    for domain in trusted_domains:
        if domain in url_lower:
            return "high"
    
    # Check for common unreliable patterns
    unreliable_patterns = ['clickbait', 'viral', 'shocking']
    for pattern in unreliable_patterns:
        if pattern in url_lower:
            return "low"
    
    return "medium"


# Summarize long responses
def SummarizeIfTooLong(text, max_length=500):
    """
    Summarize response if it's too long
    """
    if len(text) <= max_length:
        return text
    
    # Keep first part and add summary indicator
    sentences = text.split('.')
    summary = ''
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length - 50:
            summary += sentence + '.'
        else:
            break
    
    summary += "\n\n[Response summarized for brevity]"
    return summary


# Fact verification prompt
def AddFactCheckPrompt(query_type):
    """
    Add fact-checking instructions based on query type
    """
    if query_type in ["news", "factual", "datetime"]:
        return "\n\nIMPORTANT: Verify facts from multiple sources. If information conflicts, mention the discrepancy."
    
    if query_type == "opinion":
        return "\n\nNote: Present balanced viewpoints and acknowledge this is subjective."
    
    return ""

# Clean and modify AI response
def AnswerModifier(Answer):
    """Enhanced answer formatting"""
    lines = Answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    formatted = "\n".join(non_empty_lines)
    
    # Remove common AI artifacts
    formatted = formatted.replace("</s>", "").strip()
    
    return formatted

# Response quality check
def ValidateResponse(response):
    """Check if response is valid and useful"""
    if not response or len(response) < 10:
        return False
    
    # Check for common error patterns
    error_phrases = [
        "i don't have access",
        "i cannot browse",
        "as an ai",
        "i don't have real-time",
    ]
    
    response_lower = response.lower()
    if any(phrase in response_lower for phrase in error_phrases):
        return False
    
    return True

# Main Realtime Search Engine function
def RealtimeSearchEngine(prompt, max_results=5, use_cache=True):
    """
    Enhanced realtime search with better accuracy and features
    """
    global SystemChatBot, messages

    print(f"\n[RealtimeSearch] Processing query: {prompt}")
    
    # Detect query type
    query_type = DetectQueryType(prompt)
    print(f"[RealtimeSearch] Query type: {query_type}")

    # Load chat history
    try:
        with open(ChatLogPath, "r", encoding='utf-8') as f:
            messages = load(f)
    except:
        messages = []

    # Add user query
    messages.append({"role": "user", "content": prompt})

    # Get Google Search results with caching
    search_results = GoogleSearch(prompt, max_results=max_results, use_cache=use_cache)
    
    if not search_results:
        search_context = f"No specific search results found for '{prompt}'. Provide a general, accurate answer based on your knowledge."
    else:
        search_context = f"Use these search results to answer accurately:\n\n{search_results}\n\nProvide a concise answer citing relevant sources."

    # Append system message with search results
    SystemChatBot.append({"role": "system", "content": search_context})

    # Send request to Groq with retry logic
    max_retries = 2
    for attempt in range(max_retries):
        try:
            print(f"[RealtimeSearch] Sending request to AI (attempt {attempt + 1})")
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages[-10:],  # Last 10 messages for context
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
            
            # Save to chat log
            messages.append({"role": "assistant", "content": Answer})
            
            with open(ChatLogPath, "w", encoding='utf-8') as f:
                dump(messages, f, indent=4, ensure_ascii=False)

            SystemChatBot.pop()
            print(f"[RealtimeSearch] Response generated successfully")
            return Answer

        except Exception as e:
            print(f"[RealtimeSearch] Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                SystemChatBot.pop()
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
                    print(f"[Cache] Removed old cache: {filename}")
    except Exception as e:
        print(f"[Cache] Error clearing cache: {e}")

# Main loop for testing
if __name__ == "__main__":
    print(f"{Assistantname} Realtime Search Engine is online!\n")
    
    # Clear old cache on startup
    ClearOldCache()
    
    while True:
        prompt = input("\nEnter Your Query (or 'exit' to quit): ").strip()
        
        if prompt.lower() in ["exit", "quit", "bye"]:
            print(f"{Assistantname}: Goodbye!")
            break
        
        if not prompt:
            continue
        
        answer = RealtimeSearchEngine(prompt)
        print(f"\n{Assistantname}: {answer}\n")
        print("-" * 60)