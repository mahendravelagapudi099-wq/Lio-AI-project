# Backend/Automation.py

import asyncio
from Backend.Actions.Apps import OpenApp, CloseApp
from Backend.Actions.Files import (
    OpenFile, EditFile, ReadFile, CreateFile, 
    DeleteFile, CopyFile, MoveFile, RenameFile, 
    ListFiles, FileInfo
)
from Backend.Actions.Web import GoogleSearch, YoutubeSearch, PlayYoutube
from Backend.app.youtube import (
    youtube_pause_resume, youtube_next, 
    youtube_volume_up, youtube_volume_down, 
    youtube_skip_ads
)
from Backend.volume_control import volume_up, volume_down
from Backend.TextToSpeech import TextToSpeech

def ParseCommand(cmd):
    """Parse command from string or list format"""
    if isinstance(cmd, str):
        cmd_lower = cmd.lower().strip()
        
        # Strip common prefixes that FirstLayerDMM might add
        for prefix in ["system ", "general ", "automation "]:
            if cmd_lower.startswith(prefix):
                cmd_lower = cmd_lower[len(prefix):].strip()
                break
        
        # Specific command parsing
        if cmd_lower.startswith("google search"): return ("google search", cmd_lower[13:].strip())
        elif cmd_lower.startswith("youtube search"): return ("youtube search", cmd_lower[14:].strip())
        elif cmd_lower.startswith("open file"): return ("open file", cmd_lower[9:].strip())
        elif cmd_lower.startswith("edit file"): return ("edit file", cmd_lower[9:].strip())
        elif cmd_lower.startswith("read file"): return ("read file", cmd_lower[9:].strip())
        elif cmd_lower.startswith("create file"): return ("create file", cmd_lower[11:].strip())
        elif cmd_lower.startswith("delete file"): return ("delete file", cmd_lower[11:].strip())
        elif cmd_lower.startswith("copy file"): return ("copy file", cmd_lower[9:].strip())
        elif cmd_lower.startswith("move file"): return ("move file", cmd_lower[9:].strip())
        elif cmd_lower.startswith("rename file"): return ("rename file", cmd_lower[11:].strip())
        elif cmd_lower.startswith("list files"): return ("list files", cmd_lower[10:].strip() if len(cmd_lower) > 10 else ".")
        elif cmd_lower.startswith("file info"): return ("file info", cmd_lower[9:].strip())
        
        # YouTube controls - check for exact matches or keywords
        elif cmd_lower in ["pause", "resume"] or any(kw in cmd_lower for kw in ["pause", "resume"]):
            return ("pause", "")
        elif "next" in cmd_lower and ("video" in cmd_lower or cmd_lower == "next"):
            return ("next video", "")
        elif "skip" in cmd_lower:
            return ("skip ads", "")
        elif "volume up" in cmd_lower or cmd_lower == "volume up":
            return ("volume up", "")
        elif "volume down" in cmd_lower or cmd_lower == "volume down":
            return ("volume down", "")
        
        # Default parsing
        parts = cmd_lower.split(maxsplit=1)
        if len(parts) == 2: return (parts[0], parts[1].strip())
        elif len(parts) == 1: return (parts[0], "")
    elif isinstance(cmd, list):
        if len(cmd) >= 2: return (cmd[0].lower(), " ".join(cmd[1:]).strip())
        elif len(cmd) == 1: return (cmd[0].lower(), "")
    return ("", "")

def SystemVolumeUp(target=None):
    volume_up()
    TextToSpeech("Volume increased")

def SystemVolumeDown(target=None):
    volume_down()
    TextToSpeech("Volume decreased")

async def Automation(commands):
    """Facade for executing automation commands concurrently"""
    if not commands: return False
    tasks = []
    
    for cmd in commands:
        func_name, target = ParseCommand(cmd)
        if not func_name: continue
        
        if func_name == "open": tasks.append(asyncio.to_thread(OpenApp, target))
        elif func_name == "close": tasks.append(asyncio.to_thread(CloseApp, target))
        elif func_name == "play": 
            if not target: tasks.append(asyncio.to_thread(youtube_pause_resume, ""))
            else: tasks.append(asyncio.to_thread(PlayYoutube, target))
        elif func_name == "google search": tasks.append(asyncio.to_thread(GoogleSearch, target))
        elif func_name == "youtube search": tasks.append(asyncio.to_thread(YoutubeSearch, target))
        elif func_name == "open file": tasks.append(asyncio.to_thread(OpenFile, target))
        elif func_name == "edit file": tasks.append(asyncio.to_thread(EditFile, target))
        elif func_name == "read file": tasks.append(asyncio.to_thread(ReadFile, target))
        elif func_name == "create file": tasks.append(asyncio.to_thread(CreateFile, target))
        elif func_name == "delete file": tasks.append(asyncio.to_thread(DeleteFile, target))
        elif func_name == "copy file": tasks.append(asyncio.to_thread(CopyFile, target))
        elif func_name == "move file": tasks.append(asyncio.to_thread(MoveFile, target))
        elif func_name == "rename file": tasks.append(asyncio.to_thread(RenameFile, target))
        elif func_name == "list files": tasks.append(asyncio.to_thread(ListFiles, target))
        elif func_name == "file info": tasks.append(asyncio.to_thread(FileInfo, target))
        elif func_name in ["pause", "resume"]: tasks.append(asyncio.to_thread(youtube_pause_resume, target))
        elif func_name == "next video": tasks.append(asyncio.to_thread(youtube_next, target))
        elif func_name == "skip ads": tasks.append(asyncio.to_thread(youtube_skip_ads, target))
        elif func_name == "volume up": tasks.append(asyncio.to_thread(SystemVolumeUp, target))
        elif func_name == "volume down": tasks.append(asyncio.to_thread(SystemVolumeDown, target))
        elif func_name == "content":
            try:
                from Backend.ContentModule import Content
                tasks.append(asyncio.to_thread(Content, target))
            except ImportError: pass

    if tasks: await asyncio.gather(*tasks, return_exceptions=True)
    return True
