# Backend/Automation.py

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
import subprocess
import os
import asyncio

valid_functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# Helper functions
def OpenApp(app_name):
    """Open application using AppOpener with fallback"""
    try:
        print(f"[OpenApp] Attempting to open: {app_name}")
        appopen(app_name, match_closest=True, output=True, throw_error=True)
        print(f"[OpenApp] Successfully opened: {app_name}")
        return True
    except Exception as e:
        print(f"[OpenApp] AppOpener failed for {app_name}: {e}")
        # Fallback to direct command for common apps
        try:
            app_name_lower = app_name.lower()
            if "notepad" in app_name_lower:
                subprocess.Popen(["notepad.exe"])
                print("[OpenApp] Opened notepad using fallback")
                return True
            elif "calculator" in app_name_lower or "calc" in app_name_lower:
                subprocess.Popen(["calc.exe"])
                print("[OpenApp] Opened calculator using fallback")
                return True
            elif "chrome" in app_name_lower:
                try:
                    subprocess.Popen(["chrome.exe"])
                except:
                    subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
                print("[OpenApp] Opened chrome using fallback")
                return True
            elif "paint" in app_name_lower:
                subprocess.Popen(["mspaint.exe"])
                print("[OpenApp] Opened paint using fallback")
                return True
            elif "cmd" in app_name_lower or "command prompt" in app_name_lower:
                subprocess.Popen(["cmd.exe"])
                print("[OpenApp] Opened command prompt using fallback")
                return True
            elif "explorer" in app_name_lower:
                subprocess.Popen(["explorer.exe"])
                print("[OpenApp] Opened explorer using fallback")
                return True
            elif "word" in app_name_lower:
                subprocess.Popen(["WINWORD.EXE"])
                print("[OpenApp] Opened Word using fallback")
                return True
            elif "excel" in app_name_lower:
                subprocess.Popen(["EXCEL.EXE"])
                print("[OpenApp] Opened Excel using fallback")
                return True
            elif "powerpoint" in app_name_lower or "ppt" in app_name_lower:
                subprocess.Popen(["POWERPNT.EXE"])
                print("[OpenApp] Opened PowerPoint using fallback")
                return True
            else:
                print(f"[OpenApp] No fallback available for: {app_name}")
                return False
        except Exception as fallback_error:
            print(f"[OpenApp] Fallback also failed: {fallback_error}")
            return False

def CloseApp(app_name):
    """Close application using AppOpener"""
    try:
        print(f"[CloseApp] Attempting to close: {app_name}")
        close(app_name, match_closest=True, output=True, throw_error=True)
        print(f"[CloseApp] Successfully closed: {app_name}")
        return True
    except Exception as e:
        print(f"[CloseApp] Error closing {app_name}: {e}")
        # Fallback for Windows
        try:
            app_name_lower = app_name.lower()
            if "notepad" in app_name_lower:
                os.system("taskkill /f /im notepad.exe")
            elif "calculator" in app_name_lower:
                os.system("taskkill /f /im calculator.exe")
            elif "chrome" in app_name_lower:
                os.system("taskkill /f /im chrome.exe")
            elif "paint" in app_name_lower:
                os.system("taskkill /f /im mspaint.exe")
            else:
                return False
            print(f"[CloseApp] Closed {app_name} using fallback")
            return True
        except Exception as fallback_error:
            print(f"[CloseApp] Fallback failed: {fallback_error}")
            return False

def PlayYoutube(query):
    """Play video on YouTube"""
    try:
        print(f"[PlayYoutube] Playing: {query}")
        playonyt(query)
        return True
    except Exception as e:
        print(f"[PlayYoutube] Error: {e}")
        # Fallback: open YouTube search
        try:
            webopen(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            print(f"[PlayYoutube] Opened YouTube search as fallback")
            return True
        except:
            return False

def GoogleSearch(query):
    """Search on Google"""
    try:
        print(f"[GoogleSearch] Searching: {query}")
        search(query)
        return True
    except Exception as e:
        print(f"[GoogleSearch] Error: {e}")
        # Fallback: direct browser open
        try:
            webopen(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            print(f"[GoogleSearch] Opened Google search as fallback")
            return True
        except:
            return False

def YoutubeSearch(query):
    """Search on YouTube"""
    try:
        print(f"[YoutubeSearch] Searching: {query}")
        webopen(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        return True
    except Exception as e:
        print(f"[YoutubeSearch] Error: {e}")
        return False

def SystemCommand(command):
    """Execute system command"""
    try:
        print(f"[SystemCommand] Executing: {command}")
        os.system(command)
        return True
    except Exception as e:
        print(f"[SystemCommand] Error: {e}")
        return False

def ParseCommand(cmd):
    """
    Parse command from string or list format
    Returns: (function_name, target)
    
    Examples:
    - "open notepad" -> ("open", "notepad")
    - ["open", "notepad"] -> ("open", "notepad")
    - "play despacito song" -> ("play", "despacito song")
    """
    if isinstance(cmd, str):
        # String format: "open notepad"
        cmd_lower = cmd.lower().strip()
        
        # Check for multi-word functions first
        if cmd_lower.startswith("google search"):
            return ("google search", cmd[13:].strip())
        elif cmd_lower.startswith("youtube search"):
            return ("youtube search", cmd[14:].strip())
        
        # Single word functions
        parts = cmd.split(maxsplit=1)
        if len(parts) == 2:
            return (parts[0].lower(), parts[1].strip())
        elif len(parts) == 1:
            return (parts[0].lower(), "")
        else:
            return ("", "")
    
    elif isinstance(cmd, list):
        # List format: ["open", "notepad"]
        if len(cmd) >= 2:
            func_name = cmd[0].lower()
            target = " ".join(cmd[1:]).strip()
            return (func_name, target)
        elif len(cmd) == 1:
            return (cmd[0].lower(), "")
        else:
            return ("", "")
    
    return ("", "")

async def Automation(commands):
    """
    Main automation function
    Accepts commands in multiple formats:
    - List of strings: ["open notepad", "play song"]
    - List of lists: [["open", "notepad"], ["play", "song"]]
    - Mixed formats
    """
    if not commands:
        print("[Automation] No commands to execute")
        return False

    print(f"\n{'='*60}")
    print(f"[Automation] Starting Automation")
    print(f"[Automation] Received {len(commands)} command(s)")
    print(f"{'='*60}\n")

    funcs = []
    command_descriptions = []

    for idx, cmd in enumerate(commands):
        print(f"[Automation] Processing command {idx + 1}/{len(commands)}: {cmd}")
        
        func_name, target = ParseCommand(cmd)
        
        if not func_name:
            print(f"[Automation] ⚠️  Could not parse command: {cmd}")
            continue
        
        if not target:
            print(f"[Automation] ⚠️  No target specified for: {func_name}")
            continue

        print(f"[Automation] ✓ Parsed -> Function: '{func_name}', Target: '{target}'")

        # Store command description
        if func_name in valid_functions:
            action_text = f"{func_name.replace('_', ' ').title()} {target}"
            command_descriptions.append(action_text)
            print(f"[Automation] Action: {action_text}")

        # Map function to async task
        if func_name == "open":
            funcs.append(asyncio.to_thread(OpenApp, target))
        
        elif func_name == "close":
            funcs.append(asyncio.to_thread(CloseApp, target))
        
        elif func_name == "play":
            funcs.append(asyncio.to_thread(PlayYoutube, target))
        
        elif func_name == "google search":
            funcs.append(asyncio.to_thread(GoogleSearch, target))
        
        elif func_name == "youtube search":
            funcs.append(asyncio.to_thread(YoutubeSearch, target))
        
        elif func_name == "system":
            funcs.append(asyncio.to_thread(SystemCommand, target))
        
        elif func_name == "content":
            try:
                from Backend.ContentModule import Content
                funcs.append(asyncio.to_thread(Content, target))
            except ImportError:
                print("[Automation] ⚠️  ContentModule not found")
        
        else:
            print(f"[Automation] ⚠️  No handler for function: {func_name}")

    # Execute all functions concurrently
    if funcs:
        print(f"\n[Automation] Executing {len(funcs)} task(s)...\n")
        results = await asyncio.gather(*funcs, return_exceptions=True)
        
        print(f"\n{'='*60}")
        print(f"[Automation] Execution Results")
        print(f"{'='*60}")
        
        for i, result in enumerate(results):
            desc = command_descriptions[i] if i < len(command_descriptions) else f"Command {i+1}"
            if isinstance(result, Exception):
                print(f"❌ {desc} - FAILED: {result}")
            elif result:
                print(f"✅ {desc} - SUCCESS")
            else:
                print(f"⚠️  {desc} - COMPLETED (with warnings)")
    else:
        print("[Automation] ⚠️  No valid tasks to execute")

    print(f"\n{'='*60}")
    print(f"[Automation] Automation Complete")
    print(f"{'='*60}\n")
    
    return True


