# import cohere (Moved to Initialize)
import time
from rich import print
from dotenv import dotenv_values
from Backend.FailureHandler import FailureHandler, FailureTier, DegradedMode
from Backend.StateManager import StateManager

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars["CohereAPIKey"]

co = None

def InitializeCohere():
    """Explicit initialization for deferred/phased startup."""
    global co
    import cohere
    if co is None:
        try:
            print("[Model] Initialising Cohere Client...")
            co = cohere.Client(api_key=CohereAPIKey)
            return True
        except Exception as e:
            print(f"[Model] Cohere Initialization Failed: {e}")
            return False
    return True

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "weather", "forecast",
    "file", "task", "music", "monitor"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'weather (location)' if a query is asking about current weather, temperature, or climate conditions like if the query is 'what is the weather in alwal' respond with 'weather alwal', if the query is 'tell me the weather' respond with 'weather auto', if the query is 'how is the temperature today' respond with 'weather auto', if the query is 'is it sunny in delhi' respond with 'weather delhi', etc.
-> Respond with 'forecast (location)' if a query is asking about weather forecast or future weather predictions like if the query is 'weather forecast for tomorrow' respond with 'forecast auto', if the query is 'will it rain this week in mumbai' respond with 'forecast mumbai', etc.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc. DO NOT use 'realtime' for weather queries, always use 'weather' or 'forecast' instead.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder or timer like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting', or 'set a timer for 10 minutes' respond with 'reminder timer in 10 minutes'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails, jokes, poems, save files or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on. This also includes saving files like 'save the file' or 'save file name test.txt'.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
    {"role": "User", "message": "how are you ?"},
    {"role": "Chatbot", "message": "general how are you ?"},
    {"role": "User", "message": "do you like pizza ?"},
    {"role": "Chatbot", "message": "general do you like pizza ?"},
    {"role": "User", "message": "how are you ?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th at 11pm "},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "write a joke on notepad"},
    {"role": "Chatbot", "message": "content write a joke on notepad"},
    {"role": "User", "message": "save the file"},
    {"role": "Chatbot", "message": "content save the file"},
    {"role": "User", "message": "save file name test.txt"},
    {"role": "Chatbot", "message": "content save file name test.txt"}
]

def FirstLayerDMM(prompt: str = "test"):
    """
    First Layer Decision Making Model
    Uses Cohere AI to classify user queries with fallback logic.
    Includes exponential backoff (1 retry) and Failure Model enforcement.
    """
    
    # Check if we are in LOBOTOMIZED mode
    if StateManager().GetDegradedMode() == DegradedMode.LOBOTOMIZED:
        print("[FirstLayerDMM] Blocked: LOBOTOMIZED mode.")
        return []

    # ========== SAFE REGEX SHORTCUTS ==========
    # Handle specific, atomic commands immediately (Bypass AI for speed/safety)
    prompt_lower = prompt.lower().strip()

    # 1. Exit Commands (Exact match preferred for safety)
    if any(keyword in prompt_lower for keyword in ["exit", "quit", "bye", "goodbye", "stop"]):
        print("[FirstLayerDMM] Shortcut: Exit")
        return ["exit"]

    # 2. System Commands (Volume/Mute - Reliability)
    if any(word in prompt_lower for word in ["volume", "mute", "unmute", "brightness"]):
        print("[FirstLayerDMM] Shortcut: System")
        return [f"system {prompt}"]

    # 3. Open/Launch Commands
    if any(word in prompt_lower for word in ["open ", "launch ", "start "]):
        print("[FirstLayerDMM] Shortcut: Open")
        return [f"open {prompt_lower.replace('open ', '').replace('launch ', '').replace('start ', '').strip()}"]

    # 4. Close Commands
    if any(word in prompt_lower for word in ["close ", "quit ", "exit "]):
        # Skip if it's the exit command handled earlier
        if len(prompt_lower.split()) > 1:
            print("[FirstLayerDMM] Shortcut: Close")
            return [f"close {prompt_lower.replace('close ', '').replace('quit ', '').replace('exit ', '').strip()}"]

    # 5. Play Commands
    if "play " in prompt_lower:
        print("[FirstLayerDMM] Shortcut: Play")
        return [f"play {prompt_lower.replace('play ', '').strip()}"]

    # 6. Save Commands
    if any(word in prompt_lower for word in ["save ", "save file", "save the file"]):
        print("[FirstLayerDMM] Shortcut: Content (Save)")
        return [f"content {prompt}"]

    # 7. Write/Create Commands
    if any(word in prompt_lower for word in ["write ", "create ", "type "]):
        print("[FirstLayerDMM] Shortcut: Content (Write)")
        return [f"content {prompt}"]

    # 8. Search Commands
    if "search " in prompt_lower:
        if "youtube" in prompt_lower:
            print("[FirstLayerDMM] Shortcut: YouTube Search")
            return [f"youtube search {prompt_lower.replace('youtube ', '').replace('search ', '').strip()}"]
        elif "google" in prompt_lower:
            print("[FirstLayerDMM] Shortcut: Google Search")
            return [f"google search {prompt_lower.replace('google ', '').replace('search ', '').strip()}"]
        else:
            print("[FirstLayerDMM] Shortcut: Google Search (Default)")
            return [f"google search {prompt_lower.replace('search ', '').strip()}"]

    # 9. Weather/Forecast Commands
    if any(word in prompt_lower for word in ["weather", "temperature", "forecast", "climate"]):
        if "forecast" in prompt_lower:
            print("[FirstLayerDMM] Shortcut: Forecast")
            return [f"forecast {prompt_lower.replace('forecast', '').strip()}"]
        else:
            print("[FirstLayerDMM] Shortcut: Weather")
            return [f"weather {prompt_lower.replace('weather', '').strip()}"]

    # 10. Reminder/Timer Commands
    if any(word in prompt_lower for word in ["remind", "reminder", "set reminder", "timer", "set timer", "set a timer"]):
        print("[FirstLayerDMM] Shortcut: Reminder")
        return [f"reminder {prompt}"]

    # 11. Image Generation Commands
    if any(word in prompt_lower for word in ["generate image", "create image", "make image"]):
        print("[FirstLayerDMM] Shortcut: Generate Image")
        image_prompt = prompt_lower
        for word in ["generate image", "create image", "make image", "generate", "create", "make"]:
            image_prompt = image_prompt.replace(word, "")
        return [f"generate image {image_prompt.strip()}"]

    # 12. File Operation Commands
    if any(word in prompt_lower for word in ["file ", "read file", "edit file", "delete file", "copy file", "move file", "rename file", "list files"]):
        print("[FirstLayerDMM] Shortcut: File Operation")
        return [f"file {prompt}"]

    # 13. Task Management Commands
    if any(word in prompt_lower for word in ["task ", "todo ", "list tasks", "create task", "complete task", "delete task"]):
        print("[FirstLayerDMM] Shortcut: Task Management")
        return [f"task {prompt}"]

    # 14. Music Control Commands
    if any(word in prompt_lower for word in ["music ", "play music", "pause music", "stop music", "next track", "previous track"]):
        print("[FirstLayerDMM] Shortcut: Music Control")
        return [f"music {prompt}"]

    # 15. System Monitoring Commands
    if any(word in prompt_lower for word in ["monitor ", "system info", "cpu usage", "memory usage", "disk usage", "battery status"]):
        print("[FirstLayerDMM] Shortcut: System Monitoring")
        return [f"monitor {prompt}"]
    
    # ========== COHERE API PROCESSING WITH RETRY ==========
    if co is None:
        print("[FirstLayerDMM] Cohere not initialized, using FallbackDMM")
        return FallbackDMM(prompt)
        
    max_retries = 2  # 1 initial + 1 retry
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            messages.append({"role": "user", "content": f"{prompt}"})

            stream = co.chat(
                model='command-xlarge-nightly', 
                message=prompt,
                temperature=0.5,  # Lower temperature for more consistent responses
                chat_history=ChatHistory,
                prompt_truncation='OFF',
                connectors=[],
                preamble=preamble
            )

            response = ""

            for event in stream:
                # Handle both tuple format and object format from Cohere API
                if isinstance(event, tuple) and len(event) >= 2 and event[0] == 'text':
                    response = event[1]
                elif hasattr(event, 'event_type') and event.event_type == "text-generation":
                    response += event.text

            # Clean and parse response
            response = response.replace("\n", "").replace("\r", "").strip()
            
            if not response:
                raise ValueError("Empty response from Cohere")

            # Split multiple commands
            response = [task.strip() for task in response.split(",") if task.strip()]

            # Validate and filter responses
            valid_response = []
            for task in response:
                # Check if task starts with any valid function
                task_valid = False
                for func in funcs:
                    if task.lower().startswith(func.lower()):
                        valid_response.append(task.strip())
                        task_valid = True
                        break
                
                # If not valid, try to extract command from task
                if not task_valid:
                    # Attempt to classify unrecognized tasks using fallback logic
                    fallback_result = FallbackDMM(task)
                    if fallback_result and fallback_result != [f"general {task}"]:
                        valid_response.extend(fallback_result)

            # Check if we have valid responses
            if not valid_response or "(query)" in str(valid_response):
                if attempt < max_retries - 1:
                    print(f"[FirstLayerDMM] Invalid response, retrying {attempt+1}/{max_retries-1}...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                print("[FirstLayerDMM] Invalid response from Cohere, using fallback...")
                return FallbackDMM(prompt)
            
            # Recovery: If successful, reset mode to FULL if it was LIMITED
            if StateManager().GetDegradedMode() == DegradedMode.LIMITED:
                print("[FirstLayerDMM] Cloud restored, returning to FULL POWER.")
                StateManager().SetDegradedMode(DegradedMode.FULL)
                
            print(f"[FirstLayerDMM] Cohere response: {valid_response}")
            return valid_response
        
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[FirstLayerDMM] Retry {attempt+1}/{max_retries-1} after {retry_delay}s due to: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            
            # All retries failed - Enforce Failure Model
            FailureHandler.handle_failure(e, context="FirstLayerDMM (Cohere)")
            return FallbackDMM(prompt)

def FallbackDMM(prompt: str):
    """
    Fallback Decision Making Model
    Used when Cohere API fails or returns invalid response
    Enhanced with more comprehensive rule-based classification
    """
    print("[FallbackDMM] Using fallback logic...")
    
    prompt_lower = prompt.lower().strip()
    
    # Exit commands
    if any(keyword in prompt_lower for keyword in ["exit", "quit", "bye", "goodbye", "stop"]):
        return ["exit"]
    
    # System commands (Volume/Mute - Reliability)
    if any(word in prompt_lower for word in ["volume", "mute", "unmute", "brightness"]):
        return [f"system {prompt}"]
    
    # Open/Launch commands
    if any(word in prompt_lower for word in ["open ", "launch ", "start "]):
        app_name = prompt_lower
        for word in ["open ", "launch ", "start "]:
            app_name = app_name.replace(word, "")
        app_name = app_name.strip()
        return [f"open {app_name}"]
    
    # Close commands
    if any(word in prompt_lower for word in ["close ", "quit ", "exit "]):
        # Skip if it's the exit command handled earlier
        if len(prompt_lower.split()) > 1:
            app_name = prompt_lower
            for word in ["close ", "quit ", "exit "]:
                app_name = app_name.replace(word, "")
            app_name = app_name.strip()
            if app_name:
                return [f"close {app_name}"]
    
    # Play commands
    if "play " in prompt_lower:
        song_name = prompt_lower.replace("play ", "").strip()
        return [f"play {song_name}"]
    
    # Save commands
    if any(word in prompt_lower for word in ["save ", "save file", "save the file"]):
        return [f"content {prompt}"]
    
    # Write/Create commands
    if any(word in prompt_lower for word in ["write ", "create ", "type "]):
        return [f"content {prompt}"]
    
    # File operation commands (read, edit, delete, copy, move, rename)
    if any(word in prompt_lower for word in ["read ", "edit ", "delete ", "copy ", "move ", "rename "]):
        return [f"content {prompt}"]
    
    # Search commands
    if "search " in prompt_lower:
        if "youtube" in prompt_lower:
            search_query = prompt_lower.replace('youtube', '').replace('search', '').strip()
            return [f"youtube search {search_query}"]
        elif "google" in prompt_lower:
            search_query = prompt_lower.replace('google', '').replace('search', '').strip()
            return [f"google search {search_query}"]
        else:
            return [f"google search {prompt_lower.replace('search ', '').strip()}"]
    
    # Image generation commands
    if any(word in prompt_lower for word in ["generate image", "create image", "make image"]):
        image_prompt = prompt_lower
        for word in ["generate image", "create image", "make image", "generate ", "create ", "make "]:
            image_prompt = image_prompt.replace(word, "")
        image_prompt = image_prompt.strip()
        return [f"generate image {image_prompt}"]

    # File operation commands
    if any(word in prompt_lower for word in ["file ", "read file", "edit file", "delete file", "copy file", "move file", "rename file", "list files"]):
        return [f"file {prompt}"]

    # Task management commands
    if any(word in prompt_lower for word in ["task ", "todo ", "list tasks", "create task", "complete task", "delete task"]):
        return [f"task {prompt}"]

    # Music control commands
    if any(word in prompt_lower for word in ["music ", "play music", "pause music", "stop music", "next track", "previous track"]):
        return [f"music {prompt}"]

    # System monitoring commands
    if any(word in prompt_lower for word in ["monitor ", "system info", "cpu usage", "memory usage", "disk usage", "battery status"]):
        return [f"monitor {prompt}"]
    
    # Reminder/Timer commands
    if any(word in prompt_lower for word in ["remind", "reminder", "set reminder", "timer", "set timer", "set a timer"]):
        return [f"reminder {prompt}"]
    
    # Weather/Forecast queries
    if any(word in prompt_lower for word in ["weather", "temperature", "forecast", "climate"]):
        if "forecast" in prompt_lower:
            return [f"forecast {prompt_lower.replace('forecast', '').strip()}"]
        else:
            return [f"weather {prompt_lower.replace('weather', '').strip()}"]
    
    # Realtime queries (news, current events)
    if any(word in prompt_lower for word in ["news", "current", "latest", "today's", "headline"]):
        return [f"realtime {prompt}"]
    
    # File operations commands
    if any(word in prompt_lower for word in ["read file", "edit file", "delete file", "copy file", "move file", "rename file"]):
        return [f"content {prompt}"]
    
    # YouTube control commands
    if any(word in prompt_lower for word in ["pause", "resume", "next", "skip", "volume up", "volume down"]):
        return [prompt_lower]
    
    # Default to general query
    return [f"general {prompt}"]

if __name__ == "__main__":
    print("\n" + "="*60)
    print("First Layer Decision Making Model - Test Mode")
    print("="*60 + "\n")
    
    # Test cases
    test_queries = [
        "write a joke on notepad",
        "save the file",
        "save file name test.txt",
        "open notepad",
        "play despacito",
        "what's the weather today",
        "how are you",
        "exit"
    ]
    
    print("Running test queries:\n")
    for query in test_queries:
        print(f"Query: '{query}'")
        result = FirstLayerDMM(query)
        print(f"Result: {result}")
        print("-" * 60)
    
    print("\n" + "="*60)
    print("Interactive Mode (type 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            result = FirstLayerDMM(user_input)
            print(f"Decision: {result}\n")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")