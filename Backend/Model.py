import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars["CohereAPIKey"]

co = cohere.Client(api_key=CohereAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
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
    Uses Cohere AI to classify user queries with fallback logic
    """
    
    # ========== PRE-PROCESSING FALLBACK ==========
    # Handle specific patterns before sending to Cohere
    prompt_lower = prompt.lower().strip()
    
    # Handle save commands (high priority)
    if "save" in prompt_lower and any(word in prompt_lower for word in ["file", "notepad", "document", "text", "the"]):
        print("[FirstLayerDMM] Detected save command via fallback")
        return [f"content {prompt}"]
    
    # Handle write/type commands with notepad
    if any(word in prompt_lower for word in ["write", "type"]) and "notepad" in prompt_lower:
        print("[FirstLayerDMM] Detected write command via fallback")
        return [f"content {prompt}"]
    
    # Handle general content creation with notepad
    if "notepad" in prompt_lower and any(word in prompt_lower for word in ["create", "make", "joke", "poem", "story"]):
        print("[FirstLayerDMM] Detected content creation via fallback")
        return [f"content {prompt}"]
    
    # Handle exit commands
    if prompt_lower in ["exit", "quit", "bye", "goodbye", "stop"]:
        print("[FirstLayerDMM] Detected exit command via fallback")
        return ["exit"]
    
    # ========== COHERE API PROCESSING ==========
    try:
        messages.append({"role": "user", "content": f"{prompt}"})

        stream = co.chat(
            model='command-xlarge-nightly', 
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )

        response = ""

        for event in stream:
            # Print the event to see its structure
            if event[0] == 'text':
                response = event[1]  # Get the text response
            
            if hasattr(event, 'event_type') and event.event_type == "text-generation":
                response += event.text

        response = response.replace("\n", "")
        response = response.split(",")

        response = [i.strip() for i in response]

        temp = []

        for task in response:
            for func in funcs:
                if task.startswith(func):
                    temp.append(task)
        
        response = temp

        # If response contains "(query)" placeholder, retry or use fallback
        if "(query)" in str(response) or not response:
            print("[FirstLayerDMM] Invalid response from Cohere, using fallback...")
            return FallbackDMM(prompt)
        
        print(f"[FirstLayerDMM] Cohere response: {response}")
        return response
    
    except Exception as e:
        print(f"[FirstLayerDMM] Error with Cohere API: {e}")
        return FallbackDMM(prompt)

def FallbackDMM(prompt: str):
    """
    Fallback Decision Making Model
    Used when Cohere API fails or returns invalid response
    """
    print("[FallbackDMM] Using fallback logic...")
    
    prompt_lower = prompt.lower().strip()
    
    # Save commands
    if "save" in prompt_lower:
        return [f"content {prompt}"]
    
    # Write/type commands
    if any(word in prompt_lower for word in ["write", "type", "create text", "create file"]):
        if "notepad" in prompt_lower:
            return [f"content {prompt}"]
        else:
            return [f"content {prompt}"]
    
    # Open commands
    if any(word in prompt_lower for word in ["open", "launch", "start"]):
        app_name = prompt_lower
        for word in ["open", "launch", "start"]:
            app_name = app_name.replace(word, "")
        app_name = app_name.strip()
        return [f"open {app_name}"]
    
    # Close commands
    if any(word in prompt_lower for word in ["close", "exit app", "quit"]):
        app_name = prompt_lower
        for word in ["close", "exit", "quit"]:
            app_name = app_name.replace(word, "")
        app_name = app_name.strip()
        if app_name:
            return [f"close {app_name}"]
    
    # Play commands
    if "play" in prompt_lower:
        song_name = prompt_lower.replace("play", "").strip()
        return [f"play {song_name}"]
    
    # Search commands
    if "search" in prompt_lower:
        if "youtube" in prompt_lower:
            search_query = prompt_lower.replace("youtube", "").replace("search", "").strip()
            return [f"youtube search {search_query}"]
        elif "google" in prompt_lower:
            search_query = prompt_lower.replace("google", "").replace("search", "").strip()
            return [f"google search {search_query}"]
        else:
            return [f"google search {prompt_lower.replace('search', '').strip()}"]
    
    # Image generation
    if any(word in prompt_lower for word in ["generate image", "create image", "make image"]):
        image_prompt = prompt_lower
        for word in ["generate image", "create image", "make image", "generate", "create", "make"]:
            image_prompt = image_prompt.replace(word, "")
        image_prompt = image_prompt.strip()
        return [f"generate image {image_prompt}"]
    
    # Reminder
    if any(word in prompt_lower for word in ["remind", "reminder", "set reminder"]):
        return [f"reminder {prompt}"]
    
    # System commands
    if any(word in prompt_lower for word in ["volume", "mute", "unmute", "brightness"]):
        return [f"system {prompt}"]
    
    # Realtime queries (news, weather, current events)
    if any(word in prompt_lower for word in ["news", "weather", "temperature", "current", "latest", "today's"]):
        return [f"realtime {prompt}"]
    
    # Exit commands
    if any(word in prompt_lower for word in ["exit", "quit", "bye", "goodbye", "stop assistant"]):
        return ["exit"]
    
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