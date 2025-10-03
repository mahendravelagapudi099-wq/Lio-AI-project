# Backend/Automation.py

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
import subprocess
import os
import asyncio
import shutil
from pathlib import Path

valid_functions = [
    "open", "close", "play", "system", "content", 
    "google search", "youtube search",
    "open file", "edit file", "read file", "create file", 
    "delete file", "copy file", "move file", "rename file",
    "list files", "file info"
]

# ==================== APP FUNCTIONS ====================

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

# ==================== WEB FUNCTIONS ====================

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

# ==================== FILE FUNCTIONS ====================

def OpenFile(file_path):
    """Open a file with its default application"""
    try:
        print(f"[OpenFile] Opening: {file_path}")
        
        # Expand user path and resolve
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"[OpenFile] File not found: {file_path}")
            return False
        
        # Open file with default app
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # Linux/Mac
            subprocess.run(['xdg-open', file_path])
        
        print(f"[OpenFile] Successfully opened: {file_path}")
        return True
    except Exception as e:
        print(f"[OpenFile] Error: {e}")
        return False

def EditFile(file_path):
    """Open a file in notepad/default text editor"""
    try:
        print(f"[EditFile] Editing: {file_path}")
        
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"[EditFile] File not found: {file_path}")
            return False
        
        # Open in text editor
        if os.name == 'nt':  # Windows
            subprocess.Popen(['notepad.exe', file_path])
        else:  # Linux/Mac
            subprocess.Popen(['nano', file_path])
        
        print(f"[EditFile] Opened in editor: {file_path}")
        return True
    except Exception as e:
        print(f"[EditFile] Error: {e}")
        return False

def ReadFile(file_path):
    """Read and display file contents"""
    try:
        print(f"[ReadFile] Reading: {file_path}")
        
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"[ReadFile] File not found: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"[ReadFile] File contents ({len(content)} chars):")
        print("-" * 50)
        print(content[:500])  # Show first 500 chars
        if len(content) > 500:
            print(f"... (truncated, total {len(content)} characters)")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"[ReadFile] Error: {e}")
        return False

def CreateFile(params):
    """
    Create a new file
    params format: "path|content" or just "path"
    Example: "test.txt|Hello World" or "test.txt"
    """
    try:
        parts = params.split('|', 1)
        file_path = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ""
        
        print(f"[CreateFile] Creating: {file_path}")
        
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[CreateFile] Successfully created: {file_path}")
        return True
    except Exception as e:
        print(f"[CreateFile] Error: {e}")
        return False

def DeleteFile(file_path):
    """Delete a file"""
    try:
        print(f"[DeleteFile] Deleting: {file_path}")
        
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            print(f"[DeleteFile] File not found: {file_path}")
            return False
        
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
        
        print(f"[DeleteFile] Successfully deleted: {file_path}")
        return True
    except Exception as e:
        print(f"[DeleteFile] Error: {e}")
        return False

def CopyFile(params):
    """
    Copy a file
    params format: "source|destination"
    Example: "file1.txt|file2.txt"
    """
    try:
        parts = params.split('|')
        if len(parts) != 2:
            print("[CopyFile] Invalid format. Use: source|destination")
            return False
        
        src = os.path.expanduser(parts[0].strip())
        dst = os.path.expanduser(parts[1].strip())
        
        print(f"[CopyFile] Copying: {src} -> {dst}")
        
        if not os.path.exists(src):
            print(f"[CopyFile] Source not found: {src}")
            return False
        
        # Create destination directory if needed
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
        
        print(f"[CopyFile] Successfully copied to: {dst}")
        return True
    except Exception as e:
        print(f"[CopyFile] Error: {e}")
        return False

def MoveFile(params):
    """
    Move/rename a file
    params format: "source|destination"
    Example: "file1.txt|file2.txt"
    """
    try:
        parts = params.split('|')
        if len(parts) != 2:
            print("[MoveFile] Invalid format. Use: source|destination")
            return False
        
        src = os.path.expanduser(parts[0].strip())
        dst = os.path.expanduser(parts[1].strip())
        
        print(f"[MoveFile] Moving: {src} -> {dst}")
        
        if not os.path.exists(src):
            print(f"[MoveFile] Source not found: {src}")
            return False
        
        # Create destination directory if needed
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        shutil.move(src, dst)
        
        print(f"[MoveFile] Successfully moved to: {dst}")
        return True
    except Exception as e:
        print(f"[MoveFile] Error: {e}")
        return False

def RenameFile(params):
    """Alias for MoveFile"""
    return MoveFile(params)

def ListFiles(directory="."):
    """List files in a directory"""
    try:
        directory = os.path.expanduser(directory)
        directory = os.path.abspath(directory)
        
        print(f"[ListFiles] Listing files in: {directory}")
        
        if not os.path.exists(directory):
            print(f"[ListFiles] Directory not found: {directory}")
            return False
        
        items = os.listdir(directory)
        print(f"\n{'='*60}")
        print(f"Files in {directory}:")
        print(f"{'='*60}")
        
        for item in sorted(items):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                print(f"📁 {item}/")
            else:
                size = os.path.getsize(full_path)
                print(f"📄 {item} ({size} bytes)")
        
        print(f"{'='*60}\n")
        return True
    except Exception as e:
        print(f"[ListFiles] Error: {e}")
        return False

def FileInfo(file_path):
    """Get file information"""
    try:
        file_path = os.path.expanduser(file_path)
        file_path = os.path.abspath(file_path)
        
        print(f"[FileInfo] Getting info for: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[FileInfo] File not found: {file_path}")
            return False
        
        stat = os.stat(file_path)
        
        print(f"\n{'='*60}")
        print(f"File Information:")
        print(f"{'='*60}")
        print(f"Path: {file_path}")
        print(f"Name: {os.path.basename(file_path)}")
        print(f"Size: {stat.st_size} bytes")
        print(f"Type: {'Directory' if os.path.isdir(file_path) else 'File'}")
        print(f"Created: {stat.st_ctime}")
        print(f"Modified: {stat.st_mtime}")
        print(f"{'='*60}\n")
        return True
    except Exception as e:
        print(f"[FileInfo] Error: {e}")
        return False

# ==================== SYSTEM FUNCTIONS ====================

def SystemCommand(command):
    """Execute system command"""
    try:
        print(f"[SystemCommand] Executing: {command}")
        os.system(command)
        return True
    except Exception as e:
        print(f"[SystemCommand] Error: {e}")
        return False

# ==================== PARSER ====================

def ParseCommand(cmd):
    """
    Parse command from string or list format
    Returns: (function_name, target)
    
    Examples:
    - "open notepad" -> ("open", "notepad")
    - ["open", "notepad"] -> ("open", "notepad")
    - "open file document.txt" -> ("open file", "document.txt")
    - "edit file test.py" -> ("edit file", "test.py")
    """
    if isinstance(cmd, str):
        # String format: "open notepad"
        cmd_lower = cmd.lower().strip()
        
        # Check for multi-word functions first (longest first)
        if cmd_lower.startswith("google search"):
            return ("google search", cmd[13:].strip())
        elif cmd_lower.startswith("youtube search"):
            return ("youtube search", cmd[14:].strip())
        elif cmd_lower.startswith("open file"):
            return ("open file", cmd[9:].strip())
        elif cmd_lower.startswith("edit file"):
            return ("edit file", cmd[9:].strip())
        elif cmd_lower.startswith("read file"):
            return ("read file", cmd[9:].strip())
        elif cmd_lower.startswith("create file"):
            return ("create file", cmd[11:].strip())
        elif cmd_lower.startswith("delete file"):
            return ("delete file", cmd[11:].strip())
        elif cmd_lower.startswith("copy file"):
            return ("copy file", cmd[9:].strip())
        elif cmd_lower.startswith("move file"):
            return ("move file", cmd[9:].strip())
        elif cmd_lower.startswith("rename file"):
            return ("rename file", cmd[11:].strip())
        elif cmd_lower.startswith("list files"):
            return ("list files", cmd[10:].strip() if len(cmd) > 10 else ".")
        elif cmd_lower.startswith("file info"):
            return ("file info", cmd[9:].strip())
        
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

# ==================== MAIN AUTOMATION ====================

async def Automation(commands):
    """
    Main automation function
    Accepts commands in multiple formats:
    - List of strings: ["open notepad", "play song", "open file test.txt"]
    - List of lists: [["open", "notepad"], ["open file", "test.txt"]]
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
        
        elif func_name == "open file":
            funcs.append(asyncio.to_thread(OpenFile, target))
        
        elif func_name == "edit file":
            funcs.append(asyncio.to_thread(EditFile, target))
        
        elif func_name == "read file":
            funcs.append(asyncio.to_thread(ReadFile, target))
        
        elif func_name == "create file":
            funcs.append(asyncio.to_thread(CreateFile, target))
        
        elif func_name == "delete file":
            funcs.append(asyncio.to_thread(DeleteFile, target))
        
        elif func_name == "copy file":
            funcs.append(asyncio.to_thread(CopyFile, target))
        
        elif func_name == "move file":
            funcs.append(asyncio.to_thread(MoveFile, target))
        
        elif func_name == "rename file":
            funcs.append(asyncio.to_thread(RenameFile, target))
        
        elif func_name == "list files":
            funcs.append(asyncio.to_thread(ListFiles, target))
        
        elif func_name == "file info":
            funcs.append(asyncio.to_thread(FileInfo, target))
        
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