# Backend/Automation.py

import asyncio
import re
from datetime import datetime, timedelta
# StateManager is imported at top level as it is relatively light and used in multiple wrappers
from Backend.StateManager import StateManager

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
        # New command parsers
        elif cmd_lower.startswith("file "): return ("file", cmd_lower[5:].strip())
        elif cmd_lower.startswith("task "): return ("task", cmd_lower[5:].strip())
        elif cmd_lower.startswith("music "): return ("music", cmd_lower[6:].strip())
        elif cmd_lower.startswith("monitor "): return ("monitor", cmd_lower[8:].strip())
        
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
        
        # Reminder commands
        # Reminder commands
        reminder_keywords = [
            "remind", "timer", "alarm", "countdown", "alert", "warn", "ping", 
            "notify", "schedule", "clock", "tracker",
            "wake me", "buzz me", "count down", "set", "start", "begin"
        ]
        
        # Check for implicit "X minutes" at start (digits followed by unit)
        implicit_time_match = re.match(r"^\d+\s+(second|minute|hour)", cmd_lower)
        
        # Check for ambiguous starts that MUST be followed by digits (Time 3 minutes vs What time is it)
        ambiguous_time_match = re.match(r"^(time|signal|mark|log|record|halt)\s+\d+", cmd_lower)

        if any(kw in cmd_lower for kw in reminder_keywords) or implicit_time_match or ambiguous_time_match:
            return ("reminder", cmd_lower)
        
        # Default parsing
        parts = cmd_lower.split(maxsplit=1)
        if len(parts) == 2: return (parts[0], parts[1].strip())
        elif len(parts) == 1: return (parts[0], "")
    elif isinstance(cmd, list):
        if len(cmd) >= 2: return (cmd[0].lower(), " ".join(cmd[1:]).strip())
        elif len(cmd) == 1: return (cmd[0].lower(), "")
    return ("", "")

def ContextAwareVolumeUp(target=None):
    from Backend.volume_control import volume_up
    state = StateManager().GetState()
    if state["is_playing"]:# ... (rest of function unchanged, just need to bridge gap)
        import pyautogui # Re-import locally to avoid issues if moved
        pyautogui.press("volumeup")
    else:
        from Backend.volume_control import volume_up
        volume_up()

def ContextAwareVolumeDown(target=None):
    import pyautogui
    from Backend.volume_control import volume_down
    state = StateManager().GetState()
    if state["is_playing"]:
        pyautogui.press("volumedown")
    else:
        volume_down()

def ContextAwarePauseResume(target=None):
    import pyautogui
    from Backend.app.youtube import youtube_pause_resume
    state = StateManager().GetState()
    if state["is_playing"]:
        pyautogui.press("playpause")
    else:
        youtube_pause_resume(target)

def ContextAwareNext(target=None):
    import pyautogui
    from Backend.app.youtube import youtube_next
    state = StateManager().GetState()
    if state["is_playing"]:
        pyautogui.press("nexttrack")
    else:
        youtube_next(target)

async def PlayYoutubeWrapper(query):
    from Backend.Actions.Web import PlayYoutube
    result = await asyncio.to_thread(PlayYoutube, query)
    if result:
        StateManager().SetState("youtube", True, query)
    return result

async def CloseAppWrapper(app_name):
    from Backend.Actions.Apps import CloseApp
    await asyncio.to_thread(CloseApp, app_name)
    if "youtube" in app_name.lower() or "brave" in app_name.lower() or "chrome" in app_name.lower():
        StateManager().ClearState()


def SystemVolumeUp(target=None):
    from Backend.volume_control import volume_up
    from Backend.TextToSpeech import TextToSpeech
    volume_up()
    TextToSpeech("Volume increased")

def SystemVolumeDown(target=None):
    from Backend.volume_control import volume_down
    from Backend.TextToSpeech import TextToSpeech
    volume_down()
    TextToSpeech("Volume decreased")

async def HandleReminder(cmd):
    from Backend.app.reminder import create_temporary_reminder, create_persistent_reminder
    from Backend.TextToSpeech import TextToSpeech
    """Parses and schedules reminders based on natural language input."""
    # Normalize synonyms to standard "timer in" or "reminder" syntax
    cmd = cmd.lower()
    
    # Synonym Mapping
    cmd = cmd.replace("alarm", "timer").replace("countdown", "timer").replace("alert", "timer").replace("warn", "timer").replace("ping", "timer").replace("notify", "timer").replace("schedule", "reminder").replace("clock", "timer").replace("tracker", "timer").replace("log", "timer").replace("record", "timer").replace("halt", "timer").replace("wake me up", "timer").replace("wake me", "timer").replace("buzz me", "timer").replace("count down", "timer")
    
    # Handle implicit starts (e.g. "5 minutes") -> "timer in 5 minutes"
    if re.match(r"^\d+\s+(second|minute|hour)", cmd):
        cmd = "timer in " + cmd

    # Standard cleanups
    cmd = cmd.replace("remind me to ", "").replace("set reminder to ", "").replace("remind me ", "").replace("set reminder ", "").replace("set a timer for ", "timer in ").replace("set timer for ", "timer in ").replace("set a reminder for ", "reminder in ").replace("set reminder for ", "reminder in ")
    
    # 1. Temporary Reminder Logic (in/after X seconds/minutes/hours)
    # Handle 'an hour' case
    an_hour_match = re.search(r"(.*?)\s*(in|after)?\s*an\s*hour\b(.*)", cmd)
    if an_hour_match:
        prefix_msg = an_hour_match.group(1).strip()
        suffix_msg = an_hour_match.group(3).strip() if an_hour_match.lastindex >= 3 else ""
        
        if prefix_msg in ["timer", "reminder"] and suffix_msg:
            message = suffix_msg
        else:
            message = f"{prefix_msg} {suffix_msg}".strip()
            
        if create_temporary_reminder(message, 3600):
            TextToSpeech("Reminder set for 1 hour.")
            return True
        return False
        
    # Handle 'a sec' or 'a second' case
    a_sec_match = re.search(r"(.*?)\s*(in|after)?\s*a\s*(sec|second)\b(.*)", cmd)
    if a_sec_match:
        prefix_msg = a_sec_match.group(1).strip()
        suffix_msg = a_sec_match.group(4).strip() if a_sec_match.lastindex >= 4 else ""
        
        if prefix_msg in ["timer", "reminder"] and suffix_msg:
            message = suffix_msg
        else:
            message = f"{prefix_msg} {suffix_msg}".strip()
            
        if create_temporary_reminder(message, 1):
            TextToSpeech("Reminder set for 1 second.")
            return True
        return False
        
    # Handle standard cases with numbers and units
    temp_match = re.search(r"(.*?)\s*(in|after)?\s*(\d+)\s*([smh]|secs?|seconds?|mins?|minutes?|hrs?|hours?)\b(.*)", cmd)
    if temp_match:
        prefix_msg = temp_match.group(1).strip()
        unit = temp_match.group(4).lower()
        value = int(temp_match.group(3))
        suffix_msg = temp_match.group(5).strip() if temp_match.lastindex >= 5 else ""
        
        # Smart message construction
        if prefix_msg in ["timer", "reminder"] and suffix_msg:
            message = suffix_msg
        else:
            message = f"{prefix_msg} {suffix_msg}".strip()

        # Calculate delay in seconds
        if any(u in unit for u in ["s", "second"]):
            delay = value
        elif any(u in unit for u in ["m", "minute"]):
            delay = value * 60
        elif any(u in unit for u in ["h", "hour"]):
            delay = value * 3600
        else:
            # Default to minutes if unit is unclear
            delay = value * 60
            
        if create_temporary_reminder(message, delay):
            TextToSpeech(f"Reminder set for {value} {unit}.")
            return True
        return False
        
    # Handle cases with just number (assume minutes by default)
    number_only_match = re.search(r"(.*?)\s*(timer|reminder)\s*(\d+)\b(.*)", cmd)
    if number_only_match:
        prefix_msg = number_only_match.group(1).strip()
        reminder_type = number_only_match.group(2)
        value = int(number_only_match.group(3))
        suffix_msg = number_only_match.group(4).strip() if number_only_match.lastindex >= 4 else ""
        
        if suffix_msg:
            message = suffix_msg
        else:
            message = prefix_msg
            
        if create_temporary_reminder(message, value * 60):
            TextToSpeech(f"Reminder set for {value} minutes.")
            return True
        return False

    # 2. Persistent Reminder Logic (at X am/pm, tomorrow at X)
    # This is a bit more complex, let's try to find common time indicators
    time_match = re.search(r"(.*?)\s*(at|today at|tomorrow at)?\s*(\d{1,2})(:?\d{0,2})\s?(am|pm)?\b(.*)", cmd)
    if time_match:
        message = time_match.group(1).strip()
        day_type = time_match.group(2) if time_match.group(2) else "at"
        hour = int(time_match.group(3))
        minute = int(time_match.group(4).replace(":", "")) if time_match.group(4) and time_match.group(4) != ":" else 0
        meridiem = time_match.group(5)
        suffix_msg = time_match.group(6).strip() if time_match.lastindex >= 6 else ""
        
        # Combine message and suffix
        if message and suffix_msg:
            message = f"{message} {suffix_msg}"
        elif suffix_msg:
            message = suffix_msg

        if not message:
            TextToSpeech("Please specify what you want to be reminded about.")
            return False

        # Convert to 24-hour format
        if meridiem == "pm" and hour < 12: hour += 12
        elif meridiem == "am" and hour == 12: hour = 0
        
        if hour > 23 or minute > 59:
            TextToSpeech("Invalid time format. Please try again.")
            return False

        target_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if "tomorrow" in day_type:
            target_time += timedelta(days=1)
        elif target_time < datetime.now():
            # If time already passed today and they didn't say tomorrow, assume they meant tomorrow
            target_time += timedelta(days=1)

        if create_persistent_reminder(message, target_time):
            time_str = target_time.strftime("%I:%M %p")
            date_str = "tomorrow" if "tomorrow" in day_type or target_time.day != datetime.now().day else "today"
            TextToSpeech(f"Reminder saved for {date_str} at {time_str}.")
            return True
        return False

    # 3. Handle missing time
    if "tomorrow" in cmd or "today" in cmd or " at " in cmd:
        TextToSpeech("Sorry, I could not understand the reminder time.")
    else:
        TextToSpeech("Please specify the time for the reminder.")
    return False

async def Automation(commands):
    from Backend.Actions.Apps import OpenApp
    from Backend.Actions.Files import (
        OpenFile, EditFile, ReadFile, CreateFile, 
        DeleteFile, CopyFile, MoveFile, RenameFile, 
        ListFiles, FileInfo
    )
    from Backend.Actions.Web import GoogleSearch, YoutubeSearch
    from Backend.app.youtube import youtube_skip_ads
    """Facade for executing automation commands concurrently"""
    if not commands: return False
    tasks = []
    
    for cmd in commands:
        func_name, target = ParseCommand(cmd)
        if not func_name: continue
        
        if func_name == "open": tasks.append(asyncio.to_thread(OpenApp, target))
        elif func_name == "close": tasks.append(CloseAppWrapper(target))
        elif func_name == "play": 
            if not target: tasks.append(asyncio.to_thread(ContextAwarePauseResume, ""))
            else: tasks.append(PlayYoutubeWrapper(target))
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
        elif func_name in ["pause", "resume"]: tasks.append(asyncio.to_thread(ContextAwarePauseResume, target))
        elif func_name == "next video": tasks.append(asyncio.to_thread(ContextAwareNext, target))
        elif func_name == "skip ads": tasks.append(asyncio.to_thread(youtube_skip_ads, target))
        elif func_name == "volume up": tasks.append(asyncio.to_thread(ContextAwareVolumeUp, target))
        elif func_name == "volume down": tasks.append(asyncio.to_thread(ContextAwareVolumeDown, target))
        elif func_name == "content":
            try:
                from Backend.ContentModule import Content
                tasks.append(asyncio.to_thread(Content, target))
            except ImportError: pass
        
        elif func_name == "reminder":
            tasks.append(HandleReminder(target))
        elif func_name == "file":
            # File operations
            if "read" in target: tasks.append(asyncio.to_thread(ReadFile, target))
            elif "edit" in target: tasks.append(asyncio.to_thread(EditFile, target))
            elif "delete" in target: tasks.append(asyncio.to_thread(DeleteFile, target))
            elif "copy" in target: tasks.append(asyncio.to_thread(CopyFile, target))
            elif "move" in target: tasks.append(asyncio.to_thread(MoveFile, target))
            elif "rename" in target: tasks.append(asyncio.to_thread(RenameFile, target))
            elif "list" in target: tasks.append(asyncio.to_thread(ListFiles, target))
            elif "info" in target: tasks.append(asyncio.to_thread(FileInfo, target))
            elif "create" in target: tasks.append(asyncio.to_thread(CreateFile, target))
            elif "open" in target: tasks.append(asyncio.to_thread(OpenFile, target))
        elif func_name == "task":
            from Backend.app.tasks import (
                create_task, edit_task, delete_task, get_tasks,
                complete_task, get_task_statistics
            )
            from Backend.TextToSpeech import TextToSpeech
            if "list" in target or "show" in target: 
                tasks.append(asyncio.to_thread(get_tasks))
            elif "create" in target or "add" in target: 
                tasks.append(asyncio.to_thread(create_task, target))
            elif "complete" in target or "finish" in target: 
                tasks.append(asyncio.to_thread(complete_task, target))
            elif "delete" in target or "remove" in target: 
                tasks.append(asyncio.to_thread(delete_task, target))
            elif "statistic" in target or "report" in target: 
                tasks.append(asyncio.to_thread(get_task_statistics))
        elif func_name == "music":
            from Backend.Actions.Music import (
                play_music, pause_music, stop_music,
                next_track, previous_track, set_volume,
                get_current_track, get_playlist
            )
            from Backend.TextToSpeech import TextToSpeech
            if "play" in target: tasks.append(asyncio.to_thread(play_music))
            elif "pause" in target: tasks.append(asyncio.to_thread(pause_music))
            elif "stop" in target: tasks.append(asyncio.to_thread(stop_music))
            elif "next" in target: tasks.append(asyncio.to_thread(next_track))
            elif "previous" in target: tasks.append(asyncio.to_thread(previous_track))
            elif "volume" in target:
                volume_match = re.search(r"\d+", target)
                volume = int(volume_match.group()) if volume_match else 50
                tasks.append(asyncio.to_thread(set_volume, volume))
            elif "current" in target: 
                tasks.append(asyncio.to_thread(get_current_track))
            elif "playlist" in target: 
                tasks.append(asyncio.to_thread(get_playlist))
        elif func_name == "monitor":
            from Backend.Actions.SystemMonitor import (
                get_system_info, format_system_info,
                get_cpu_usage, get_memory_usage, get_disk_usage,
                get_battery_status, get_network_activity
            )
            from Backend.TextToSpeech import TextToSpeech
            if "system" in target or "info" in target: 
                tasks.append(asyncio.to_thread(get_system_info))
            elif "cpu" in target: tasks.append(asyncio.to_thread(get_cpu_usage))
            elif "memory" in target: tasks.append(asyncio.to_thread(get_memory_usage))
            elif "disk" in target: tasks.append(asyncio.to_thread(get_disk_usage))
            elif "battery" in target: tasks.append(asyncio.to_thread(get_battery_status))
            elif "network" in target: tasks.append(asyncio.to_thread(get_network_activity))

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                cmd_failed = commands[i] if i < len(commands) else "Unknown step"
                print(f"[Automation] Step failed: {cmd_failed} -> {res}")
                from Backend.FailureHandler import FailureHandler
                FailureHandler.handle_failure(res, context=f"Automation: {cmd_failed}")
    return True
