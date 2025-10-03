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
            
            # Check for exit commands
            elif any(keyword in Query_lower for keyword in ["exit", "quit", "bye", "goodbye", "stop"]):
                Decision = ["exit"]
                print(f"[Fix] Detected exit command")
            
            # Otherwise treat as general query
            else:
                Decision = [f"general {Query}"]
                print(f"[Fix] Treating as general query")

        print(f"\nFinal Decision: {Decision}\n")

        valid_functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
        automation_commands = [cmd for cmd in Decision if any(cmd.startswith(func) for func in valid_functions)]
        general_queries = [cmd.replace("general", "").strip() for cmd in Decision if cmd.startswith("general")]
        realtime_queries = [cmd.replace("realtime", "").strip() for cmd in Decision if cmd.startswith("realtime")]
        image_queries = [cmd for cmd in Decision if "generate" in cmd]

        print(f"Automation commands: {automation_commands}")
        print(f"General queries: {general_queries}")
        print(f"Realtime queries: {realtime_queries}")
        print(f"Image queries: {image_queries}\n")

        if automation_commands:
            print(f"[MainExecution] Running automation with: {automation_commands}")
            run(Automation(automation_commands))
            TaskExecution = True

        if image_queries:
            ImageGenerationQuery = image_queries[0]
            ImageExecution = True
            with open(r'Frontend\Files\ImageGeneration.data', "w") as file:
                file.write(f"{ImageGenerationQuery},True")
            try:
                p1 = subprocess.Popen(
                    ['python', r"Backend\ImageGeneration.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )
                subprocess_list.append(p1)
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        for query in general_queries:
            SetAsssistantStatus("Thinking...")
            Answer = ChatBot(QueryModifier(query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAsssistantStatus("Answering...")
            TextToSpeech(Answer)

        for query in realtime_queries:
            SetAsssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAsssistantStatus("Answering...")
            TextToSpeech(Answer)

        if "exit" in [cmd.lower() for cmd in Decision]:
            Answer = ChatBot(QueryModifier("Okay, Bye!"))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAsssistantStatus("Answering...")
            TextToSpeech(Answer)
            os._exit(1)

    except Exception as e:
        print(f"Error in MainExecution: {e}")
        import traceback
        traceback.print_exc()

def FirstThread():
    last_microphone_status = ""
    last_assistant_status = ""

    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            AIStatus = GetAssistantStatus()

            if CurrentStatus != last_microphone_status:
                print(f"Current Microphone Status: {CurrentStatus}")
                last_microphone_status = CurrentStatus

            if AIStatus != last_assistant_status:
                print(f"Current Assistant Status: {AIStatus}")
                last_assistant_status = AIStatus

            if CurrentStatus.lower() == "true":
                print("Executing MainExecution")
                MainExecution()
            else:
                if "Available..." not in AIStatus:
                    SetAsssistantStatus("Available...")

            sleep(1)

        except Exception as e:
            print(f"Error in FirstThread: {e}")
            sleep(1)

def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in SecondThread: {e}")

if __name__ == "__main__":
    InitialExecution()
    StartHotwordThread(MainExecution)   # ✅ Pass callback here
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()
