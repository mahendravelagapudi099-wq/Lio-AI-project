from Frontend.GUI import (
    GraphicalUserInterface,
    SetAsssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.Hotword import StartHotwordThread
from Backend.ContentModule import Content  # ✅ ADDED
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f""" {Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you? """

functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
subprocess_list = []

# Ensure a default chat log exists if no chats are logged
def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as temp_file:
                    temp_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                    response_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json file not found. Creating default response.")
        os.makedirs("Data", exist_ok=True)
        with open(r'Data\ChatLog.json', "w", encoding='utf-8') as file:
            file.write("[]")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
            response_file.write(DefaultMessage)

# Read chat log from JSON
def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except FileNotFoundError:
        print("ChatLog.json not found.")
        return []

# Integrate chat logs into a readable format
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"

    temp_dir_path = TempDirectoryPath('')
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Display the chat on the GUI
def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
        if len(str(data)) > 0:
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as response_file:
                response_file.write(data)
    except FileNotFoundError:
        print("Database.data file not found.")

# Initial execution setup
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

def MainExecution(query=None):
    """
    Execute the recognized command(s).
    If `query` is None, use SpeechRecognition to get the query.
    """
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAsssistantStatus("Listening...")

        if query:
            Query = query
        else:
            Query = SpeechRecognition()

        ShowTextToScreen(f"{Username}: {Query}")
        SetAsssistantStatus("Thinking...")

        Decision = FirstLayerDMM(Query)
        print(f"\nDecision from FirstLayerDMM: {Decision}\n")

        # FIX: If FirstLayerDMM returns empty, parse query directly
        if not Decision or Decision == []:
            print("[Fix] FirstLayerDMM returned empty. Parsing query directly...")
            Query_lower = Query.lower().strip()
            
            # Check for automation commands
            if any(keyword in Query_lower for keyword in ["open", "close", "play", "start", "launch"]):
                Decision = [Query_lower]
                print(f"[Fix] Detected automation command: {Decision}")
            
            # Check for search commands
            elif "search" in Query_lower:
                if "youtube" in Query_lower:
                    Decision = [Query_lower]
                elif "google" in Query_lower:
                    Decision = [Query_lower]
                else:
                    Decision = [f"google search {Query_lower.replace('search', '').strip()}"]
                print(f"[Fix] Detected search command: {Decision}")
            
            # Check for content/notepad commands
            elif any(keyword in Query_lower for keyword in ["write", "create", "type"]) and "notepad" in Query_lower:
                Decision = [f"content {Query}"]
                print(f"[Fix] Detected content command: {Decision}")
            
            # Check for exit commands
            elif any(keyword in Query_lower for keyword in ["exit", "quit", "bye", "goodbye", "stop"]):
                Decision = ["exit"]
                print(f"[Fix] Detected exit command")
            
            # Otherwise treat as general query
            else:
                Decision = [f"general {Query}"]
                print(f"[Fix] Treating as general query")

        print(f"\nFinal Decision: {Decision}\n")

        # Define valid functions for automation
        valid_functions = [
            "open", "close", "play", "system", "content", 
            "google search", "youtube search",
            "open file", "edit file", "read file", "create file",
            "delete file", "copy file", "move file", "rename file",
            "list files", "file info"
        ]
        
        # Categorize commands
        automation_commands = []
        general_queries = []
        realtime_queries = []
        image_queries = []
        
        for cmd in Decision:
            cmd_lower = cmd.lower()
            
            # Check if it's an automation command
            if any(cmd_lower.startswith(func) for func in valid_functions):
                automation_commands.append(cmd)
            # Check for general queries
            elif cmd_lower.startswith("general"):
                general_queries.append(cmd.replace("general", "").strip())
            # Check for realtime queries
            elif cmd_lower.startswith("realtime"):
                realtime_queries.append(cmd.replace("realtime", "").strip())
            # Check for image generation
            elif "generate" in cmd_lower or "image" in cmd_lower:
                image_queries.append(cmd)
            # Default to general query if no match
            else:
                general_queries.append(cmd)

        print(f"Automation commands: {automation_commands}")
        print(f"General queries: {general_queries}")
        print(f"Realtime queries: {realtime_queries}")
        print(f"Image queries: {image_queries}\n")

        # Execute automation commands
        if automation_commands:
            print(f"[MainExecution] Running automation with: {automation_commands}")
            try:
                run(Automation(automation_commands))
                TaskExecution = True
            except Exception as e:
                print(f"[MainExecution] Automation error: {e}")
                import traceback
                traceback.print_exc()

        # Handle image generation
        if image_queries:
            ImageGenerationQuery = image_queries[0]
            ImageExecution = True
            try:
                with open(r'Frontend\Files\ImageGeneration.data', "w") as file:
                    file.write(f"{ImageGenerationQuery},True")
                
                p1 = subprocess.Popen(
                    ['python', r"Backend\ImageGeneration.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocess_list.append(p1)
                print(f"[MainExecution] Image generation started")
            except Exception as e:
                print(f"[MainExecution] Error starting ImageGeneration.py: {e}")

        # Handle general queries
        for query in general_queries:
            try:
                SetAsssistantStatus("Thinking...")
                Answer = ChatBot(QueryModifier(query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] ChatBot error: {e}")

        # Handle realtime queries
        for query in realtime_queries:
            try:
                SetAsssistantStatus("Searching...")
                Answer = RealtimeSearchEngine(QueryModifier(query))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] RealtimeSearch error: {e}")

        # Handle exit command
        if "exit" in [cmd.lower() for cmd in Decision]:
            try:
                Answer = ChatBot(QueryModifier("Okay, Bye!"))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                sleep(2)
                os._exit(1)
            except Exception as e:
                print(f"[MainExecution] Exit error: {e}")
                os._exit(1)

        # Set back to available if no speaking required
        if not general_queries and not realtime_queries:
            SetAsssistantStatus("Available...")

    except Exception as e:
        print(f"[MainExecution] Critical error: {e}")
        import traceback
        traceback.print_exc()
        SetAsssistantStatus("Available...")

def FirstThread():
    """Monitor microphone status and trigger MainExecution"""
    last_microphone_status = ""
    last_assistant_status = ""

    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            AIStatus = GetAssistantStatus()

            # Log status changes
            if CurrentStatus != last_microphone_status:
                print(f"Current Microphone Status: {CurrentStatus}")
                last_microphone_status = CurrentStatus

            if AIStatus != last_assistant_status:
                print(f"Current Assistant Status: {AIStatus}")
                last_assistant_status = AIStatus

            # Execute if microphone is active
            if CurrentStatus.lower() == "true":
                print("Executing MainExecution")
                MainExecution()
            else:
                if "Available..." not in AIStatus:
                    SetAsssistantStatus("Available...")

            sleep(1)

        except Exception as e:
            print(f"[FirstThread] Error: {e}")
            import traceback
            traceback.print_exc()
            sleep(1)

def SecondThread():
    """Start the graphical user interface"""
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"[SecondThread] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("STARTING LIO AI ASSISTANT")
    print("="*70 + "\n")
    
    try:
        # Initialize the application
        InitialExecution()
        
        # Start hotword detection thread
        print("[Main] Starting hotword detection...")
        StartHotwordThread(MainExecution)
        
        # Start monitoring thread
        print("[Main] Starting monitoring thread...")
        thread1 = threading.Thread(target=FirstThread, daemon=True)
        thread1.start()
        
        # Start GUI (blocking)
        print("[Main] Starting GUI...")
        SecondThread()
        
    except KeyboardInterrupt:
        print("\n[Main] Shutting down gracefully...")
        os._exit(0)
    except Exception as e:
        print(f"[Main] Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        os._exit(1)