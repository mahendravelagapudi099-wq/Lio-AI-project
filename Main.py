from Backend.FailureHandler import FailureHandler, DegradedMode
from Backend.StateManager import StateManager
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import sys
import signal
import argparse
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
execution_lock = threading.Lock()

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

    from Backend.InterfaceRouter import TempDirectoryPath, AnswerModifier
    temp_dir_path = TempDirectoryPath('')
    if not os.path.exists(temp_dir_path):
        os.makedirs(temp_dir_path)

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# Display the chat on the GUI
def ShowChatOnGUI():
    from Backend.InterfaceRouter import TempDirectoryPath
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
    from Backend.InterfaceRouter import SetMicrophoneStatus, ShowTextToScreen
    from Backend.app.reminder import load_persistent_reminders
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()
    load_persistent_reminders() # ✅ ADDED

def MainExecution(query=None):
    from Backend.InterfaceRouter import SetAsssistantStatus, ShowTextToScreen, SetMicrophoneStatus, QueryModifier
    from Backend.SpeechToText import SpeechRecognition
    from Backend.Model import FirstLayerDMM
    from Backend.AnswerEngine import answer_engine
    from Backend.TextToSpeech import TextToSpeech
    from Backend.Automation import Automation
    from Backend.app.weather import GetWeather, GetForecast
    from Backend.ContentModule import Content

    """
    Execute the recognized command(s).
    If `query` is None, use SpeechRecognition to get the query.
    """
    state = StateManager()
    current_mode = state.GetDegradedMode()
    
    if not execution_lock.acquire(blocking=False):
        # Silence the log if it's already busy to avoid spam
        # print("[MainExecution] Blocked: Another execution is already in progress.")
        return

    state.state["is_busy"] = True

    # Step 2: Interaction Guard (Phase 2 Safety)
    if not state.GetState().get("readiness", {}).get("cloud", False) and current_mode != DegradedMode.LOCAL:
        print("[MainExecution] Cloud not ready. Prompting user to wait.")
        SetAsssistantStatus("Still waking up...")
        if query:
            ShowTextToScreen(f"{Username}: {query}")
        ShowTextToScreen(f"{Assistantname}: I'm still connecting to my brain. Please wait a few seconds...")
        state.state["is_busy"] = False
        execution_lock.release()
        return

    try:
        # Check for LOBOTOMIZED mode
        if current_mode == DegradedMode.LOBOTOMIZED:
            print("[MainExecution] Blocked: LOBOTOMIZED mode. Silent waiting.")
            return

        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetMicrophoneStatus("True")
        SetAsssistantStatus("Processing...")

        if query:
            Query = query
        else:
            # Use new unified STT pipeline
            from Backend.STT import SpeechRecognition as stt_recognize
            result = stt_recognize()
            if result[0]:
                Query = result[0]
            else:
                print("[MainExecution] Speech recognition returned no result")
                return

        ShowTextToScreen(f"{Username}: {Query}")
        
        # LOCAL mode constraint: Identity only via PrivateMemory
        if current_mode == DegradedMode.LOCAL:
            from Backend.PrivateMemory import PrivateMemory
            memo_resp = PrivateMemory.check_query(Query)
            if memo_resp:
                SetAsssistantStatus("Thinking...")
                # We can call AnswerEngine here as it handles LOCAL mode by returning memo_resp correctly
                Answer = answer_engine.generate_response(Query)
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
                return
            else:
                msg = "I've lost my connection to the internet. I can only answer basic identity questions right now."
                ShowTextToScreen(f"{Assistantname}: {msg}")
                TextToSpeech(msg)
                SetAsssistantStatus("Available...")
                return

        SetAsssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)
        print(f"\nDecision from FirstLayerDMM: {Decision}\n")

        # FIX: If FirstLayerDMM returns empty, parse query directly
        if not Decision or Decision == []:
            print("[Fix] FirstLayerDMM returned empty. Parsing query directly...")
            Query_lower = Query.lower().strip()
            
            # Check for YouTube control commands
            if any(keyword in Query_lower for keyword in ["pause", "resume", "next", "skip", "volume up", "volume down"]):
                Decision = [Query_lower]
                print(f"[Fix] Detected YouTube control: {Decision}")
            
            # Check for automation commands
            elif any(keyword in Query_lower for keyword in ["open", "close", "play", "start", "launch"]):
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
            "list files", "file info",
            "reminder",
            "file", "task", "music", "monitor",
            # YouTube controls
            "pause", "resume", "next", "skip", "volume"
        ]
        
        # Categorize commands
        automation_commands = []
        general_queries = []
        realtime_queries = []
        image_queries = []
        weather_queries = []
        forecast_queries = []
        
        for cmd in Decision:
            cmd_lower = cmd.lower()
            
            # Check for YouTube control commands (using 'in' for better matching)
            youtube_controls = ["pause", "resume", "next", "skip", "volume up", "volume down"]
            if any(control in cmd_lower for control in youtube_controls):
                automation_commands.append(cmd)
            # Check if it's an automation command (starts with valid function)
            elif any(cmd_lower.startswith(func) for func in valid_functions):
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
            # Check for weather
            elif cmd_lower.startswith("weather"):
                weather_queries.append(cmd.replace("weather", "").strip())
            # Check for forecast
            elif cmd_lower.startswith("forecast"):
                forecast_queries.append(cmd.replace("forecast", "").strip())
            # Default to general query if no match
            else:
                general_queries.append(cmd)

        # Handle new command types
        file_queries = []
        task_queries = []
        music_queries = []
        monitor_queries = []
        
        for cmd in Decision:
            cmd_lower = cmd.lower().strip()
            if cmd_lower.startswith("file"):
                file_queries.append(cmd)
            elif cmd_lower.startswith("task"):
                task_queries.append(cmd)
            elif cmd_lower.startswith("music"):
                music_queries.append(cmd)
            elif cmd_lower.startswith("monitor"):
                monitor_queries.append(cmd)

        print(f"Automation commands: {automation_commands}")
        print(f"General queries: {general_queries}")
        print(f"Realtime queries: {realtime_queries}")
        print(f"Image queries: {image_queries}")
        print(f"Weather queries: {weather_queries}")
        print(f"Forecast queries: {forecast_queries}")
        print(f"File queries: {file_queries}")
        print(f"Task queries: {task_queries}")
        print(f"Music queries: {music_queries}")
        print(f"Monitor queries: {monitor_queries}\n")

        # Execute automation commands
        if automation_commands:
            print(f"[MainExecution] Running automation with: {automation_commands}")
            
            # --- SAFETY GATE START ---
            from Backend.Safety import SafetyValidator
            
            safe_commands = []
            for cmd in automation_commands:
                assessment = SafetyValidator.analyze_command(cmd)
                
                # 1. Block Forbidden Actions
                if not assessment.is_allowed:
                    print(f"[Safety] Blocked: {cmd} -> {assessment.warning_message}")
                    ShowTextToScreen(f"{Assistantname}: {assessment.warning_message}")
                    TextToSpeech(assessment.warning_message)
                    continue

                # 2. Confirm Critical Actions
                if assessment.requires_confirmation:
                    print(f"[Safety] Confirmation Required for: {cmd}")
                    warning = assessment.warning_message + " Say 'confirm' or 'yes' to proceed."
                    ShowTextToScreen(f"{Assistantname}: {warning}")
                    TextToSpeech(warning)
                    
                    # Wait for confirmation (Small delay to let TTS finish)
                    sleep(1) 
                    SetAsssistantStatus("Listening for confirmation...")
                    
                    # Reuse SpeechRecognition for input
                    user_response_text = SpeechRecognition() # This might be blocking or manual depending on env
                    
                    if user_response_text:
                        resp_lower = user_response_text.lower().strip()
                        if any(word in resp_lower for word in ["yes", "confirm", "proceed", "do it", "sure"]):
                            print(f"[Safety] Confirmed: {cmd}")
                            TextToSpeech("Confirmed.")
                            safe_commands.append(cmd)
                        else:
                            print(f"[Safety] Cancelled: {cmd} (User said: '{user_response_text}')")
                            TextToSpeech("Action cancelled.")
                    else:
                         print(f"[Safety] Cancelled: {cmd} (No response)")
                         TextToSpeech("Action cancelled due to no response.")
                
                else:
                    # 3. Allow Safe/Sensitive Actions
                    safe_commands.append(cmd)
            
            # Update the list to only run safe commands
            automation_commands = safe_commands

            # Add new command types to automation commands
            automation_commands.extend(file_queries)
            automation_commands.extend(task_queries)
            automation_commands.extend(music_queries)
            automation_commands.extend(monitor_queries)
            # --- SAFETY GATE END ---

            try:
                if automation_commands:
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
                
                # DUAL ROUTING: Use AnswerEngine instead of ChatBot
                Answer = answer_engine.generate_response(QueryModifier(query), mode="general")
                
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] AnswerEngine error: {e}")

        # Handle realtime queries
        for query in realtime_queries:
            try:
                SetAsssistantStatus("Searching...")
                # UNIFIED: Routed to AnswerEngine (Realtime Mode)
                Answer = answer_engine.generate_response(QueryModifier(query), mode="realtime")
                
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] AnswerEngine(Realtime) error: {e}")

        # Handle weather queries
        for loc in weather_queries:
            try:
                SetAsssistantStatus("Checking Weather...")
                Answer = GetWeather(loc if loc else "auto")
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] Weather error: {e}")

        # Handle forecast queries
        for loc in forecast_queries:
            try:
                SetAsssistantStatus("Checking Forecast...")
                Answer = GetForecast(loc if loc else "auto")
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAsssistantStatus("Answering...")
                TextToSpeech(Answer)
            except Exception as e:
                print(f"[MainExecution] Forecast error: {e}")

        # Handle exit command
        if "exit" in [cmd.lower() for cmd in Decision]:
            try:
                Answer = answer_engine.generate_response(QueryModifier("Okay, Bye!"))
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
            SetMicrophoneStatus("False")
            SetAsssistantStatus("Available...")

    except Exception as e:
        print(f"[MainExecution] Critical error: {e}")
        FailureHandler.handle_failure(e, context="MainExecution Global")
        SetMicrophoneStatus("False")
        SetAsssistantStatus("Available...")
    finally:
        state.state["is_busy"] = False
        execution_lock.release()

def FirstThread():
    from Backend.InterfaceRouter import GetMicrophoneStatus, GetAssistantStatus, SetMicrophoneStatus, SetAsssistantStatus, ShowTextToScreen
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

def BackgroundServiceInitializer():
    """
    Step 4-6: Background thread to initialize heavy services.
    Updates readiness flags in StateManager.
    """
    from Backend.InterfaceRouter import SetAsssistantStatus
    from Backend.Model import InitializeCohere
    from Backend.AnswerEngine import InitializeGroq
    state_mgr = StateManager()
    
    print("[Main] Background Service Initializer started.")
    
    # Step 5: Cloud Initialization
    # Initialize both Cohere and Groq
    co_ok = InitializeCohere()
    gr_ok = InitializeGroq()
    
    if co_ok and gr_ok:
        state_mgr.SetReadiness("cloud", True)
    else:
        # Fallback to degraded mode if critical cloud services fail
        print("[Main] Warning: Cloud services failed to initialize correctly.")
        state_mgr.SetReadiness("cloud", False)
        # FailureHandler will pick this up via Step 2 guard or AnswerEngine logic
    
    # Step 6: Audio Initialization
    from Backend.Hotword import InitializeHotwordHardware
    from Backend.TextToSpeech import InitializeTTSHardware
    
    mic_ok = InitializeHotwordHardware()
    tts_ok = InitializeTTSHardware()
    
    if mic_ok and tts_ok:
        state_mgr.SetReadiness("audio", True)
    else:
        print("[Main] Warning: Audio services failed to initialize correctly.")
    
    # Step 3 marked automation as JIT, but we track readiness for consistency
    state_mgr.SetReadiness("automation", True)
    
    print("[Main] Background Services marked as READY.")

def SecondThread():
    from Backend.InterfaceRouter import GraphicalUserInterface
    """Start the graphical user interface"""
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"[SecondThread] Error: {e}")
        import traceback
        traceback.print_exc()

def cleanup_and_exit(signum, frame):
    """Graceful shutdown handler."""
    print(f"\n[Main] Received signal {signum}. Shutting down...")
    pid_file = "leo.pid"
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except:
            pass
    os._exit(0)

if __name__ == "__main__":
    # 1. Register Signal Handlers
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # 2. Argument Parsing
    parser = argparse.ArgumentParser(description="Leo AI Terminal & Daemon Entry Point")
    parser.add_argument("--daemon", action="store_true", help="Run Leo as a background daemon")
    parser.add_argument("--terminal", action="store_true", help="Run Leo in terminal mode")
    args = parser.parse_args()

    # 3. Environment Overrides
    if args.daemon:
        os.environ["LEO_MODE"] = "DAEMON"
    elif args.terminal:
        os.environ["LEO_MODE"] = "TERMINAL"

    # 4. Single-Instance (PID) Lock
    pid_file = "leo.pid"
    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            old_pid = f.read().strip()
            if old_pid:
                # Basic check if process is still running (Windows/Linux)
                try:
                    import psutil
                    if psutil.pid_exists(int(old_pid)):
                        print(f"[Main] Error: Another instance of Leo is already running (PID: {old_pid})")
                        sys.exit(1)
                except ImportError:
                    # Fallback if psutil not installed
                    print(f"[Main] Warning: leo.pid exists. Ensure no other Leo instance is running.")
    
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    # 5. Daemonization (Simplistic redirect for Windows utility)
    if args.daemon:
        print(f"[Main] Entering DAEMON mode. Logs redirected to Data/leo.log")
        os.makedirs("Data", exist_ok=True)
        log_file = open("Data/leo.log", "a", encoding="utf-8")
        sys.stdout = log_file
        sys.stderr = log_file

    try:
        from utils.branding import show_banner
        show_banner()
    except ImportError:
        pass
    
    try:
        # Initialize the application
        InitialExecution()
        
        # Start hotword detection thread
        from Backend.Hotword import StartHotwordThread
        
        # Audio Safety: Disable Mic/TTS in DAEMON mode unless explicitly allowed
        mode = os.environ.get("LEO_MODE", "GUI").upper()
        auto_voice = env_vars.get("AUTO_VOICE_DAEMON", "False").lower() == "true"
        
        if mode == "DAEMON" and not auto_voice:
            print("[Main] DAEMON mode: Audio hardware (Mic/TTS) disabled for safety.")
        else:
            print("[Main] Starting hotword detection...")
            StartHotwordThread(MainExecution)

        # Step 4: Start background service initialization
        init_thread = threading.Thread(target=BackgroundServiceInitializer, daemon=True)
        init_thread.start()
        
        # Start monitoring thread
        # print("[Main] Starting monitoring thread...")
        # thread1 = threading.Thread(target=FirstThread, daemon=True)
        # thread1.start()
        
        # Start GUI (blocking)
        print("[Main] Starting GUI...")
        if mode == "TERMINAL":
            print("[Main] TERMINAL mode active. Enter commands:")
            # Simple REPL for testing
            while True:
                try:
                    cmd = input()
                    if cmd.strip():
                        # Run in thread to not block input loop if MainExecution takes time
                        threading.Thread(target=MainExecution, args=(cmd,), daemon=True).start()
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n[Main] Shutting down...")
                    break
        else:
            SecondThread()
        
    except KeyboardInterrupt:
        print("\n[Main] Shutting down gracefully...")
        os._exit(0)
    except Exception as e:
        print(f"[Main] Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        os._exit(1)