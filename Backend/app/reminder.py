import json
import os
import threading
import time
import uuid
from datetime import datetime, timedelta

# Import TTS to notify the user
try:
    from Backend.TextToSpeech import TextToSpeech as speak
except ImportError:
    def speak(text):
        print(f"[Speech Substitute] {text}")

# -----------------------------
# CONFIG & PATHS
# -----------------------------
DATA_DIR = os.path.join("Backend", "Data")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")

# Ensure Data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize file if not exists
if not os.path.exists(REMINDERS_FILE):
    with open(REMINDERS_FILE, "w", encoding='utf-8') as f:
        json.dump([], f)

# Lock for thread-safe file access
file_lock = threading.Lock()

# Global dictionary to keep track of active timers to prevent garbage collection
active_timers = {}

def log_info(msg):
    print(f"[REMINDER-INFO] {msg}")

# -----------------------------
# CORE FUNCTIONS
# -----------------------------

def trigger_reminder(message, reminder_id=None, is_persistent=False):
    """Triggers the reminder notification and cleans up data."""
    print(f"TEMP REMINDER FIRED: {message}")
    log_info(f"Triggering reminder: {message}")
    speak(f"Reminder: {message}")
    
    if is_persistent and reminder_id:
        remove_persistent_reminder(reminder_id)
    
    # Remove from active_timers dictionary if present (cleanup)
    global active_timers
    active_timers = {k: v for k, v in active_timers.items() if v.is_alive()}

def remove_persistent_reminder(reminder_id):
    """Removes a specific reminder from the persistent storage."""
    with file_lock:
        try:
            with open(REMINDERS_FILE, "r", encoding='utf-8') as f:
                reminders = json.load(f)
            
            reminders = [r for r in reminders if r.get("id") != reminder_id]
            
            with open(REMINDERS_FILE, "w", encoding='utf-8') as f:
                json.dump(reminders, f, indent=4)
            log_info(f"Removed persistent reminder: {reminder_id}")
        except Exception as e:
            print(f"[REMINDER-ERROR] Failed to remove persistent reminder: {e}")

def create_temporary_reminder(message, delay_seconds):
    """Schedules a temporary reminder in RAM only."""
    if delay_seconds <= 0:
        print("[REMINDER-ERROR] Delay must be greater than zero.")
        return False

    reminder_id = f"temp_{uuid.uuid4().hex[:8]}"
    print(f"TEMP REMINDER CREATED: {message} {delay_seconds}")
    log_info(f"Scheduling temporary reminder in {delay_seconds}s: {message}")
    
    t = threading.Timer(delay_seconds, trigger_reminder, args=(message, reminder_id, False))
    active_timers[reminder_id] = t
    t.start()
    return True

def create_persistent_reminder(message, target_datetime):
    """Saves and schedules a persistent reminder."""
    reminder_id = f"pers_{uuid.uuid4().hex[:8]}"
    
    # Calculate delay
    now = datetime.now()
    delay = (target_datetime - now).total_seconds()
    
    if delay <= 0:
        log_info("Attempted to set reminder in the past. Skipping.")
        return False

    # Save to file
    with file_lock:
        try:
            with open(REMINDERS_FILE, "r", encoding='utf-8') as f:
                reminders = json.load(f)
            
            reminders.append({
                "id": reminder_id,
                "message": message,
                "time": target_datetime.isoformat()
            })
            
            with open(REMINDERS_FILE, "w", encoding='utf-8') as f:
                json.dump(reminders, f, indent=4)
        except Exception as e:
            print(f"[REMINDER-ERROR] Failed to save persistent reminder: {e}")
            return False

    # Schedule Timer
    log_info(f"Scheduling persistent reminder at {target_datetime}: {message}")
    t = threading.Timer(delay, trigger_reminder, args=(message, reminder_id, True))
    active_timers[reminder_id] = t
    t.start()
    return True

def load_persistent_reminders():
    """Loads reminders from file and resumes them. Runs on startup."""
    log_info("Loading persistent reminders...")
    with file_lock:
        try:
            with open(REMINDERS_FILE, "r", encoding='utf-8') as f:
                reminders = json.load(f)
            
            now = datetime.now()
            updated_reminders = []
            
            for r in reminders:
                try:
                    target_time = datetime.fromisoformat(r["time"])
                    delay = (target_time - now).total_seconds()
                    
                    if delay > 0:
                        # Resume timer
                        reminder_id = r["id"]
                        message = r["message"]
                        log_info(f"Resuming reminder {reminder_id} in {delay}s: {message}")
                        
                        timer = threading.Timer(delay, trigger_reminder, [message, reminder_id, True])
                        active_timers[reminder_id] = timer
                        timer.start()
                        updated_reminders.append(r)
                    else:
                        log_info(f"Skipping expired reminder: {r['message']} ({r['time']})")
                except Exception as e:
                    print(f"[REMINDER-ERROR] Error processing loaded reminder: {e}")
            
            # Save cleaned list back to file
            with open(REMINDERS_FILE, "w", encoding='utf-8') as f:
                json.dump(updated_reminders, f, indent=4)
                
        except Exception as e:
            print(f"[REMINDER-ERROR] Failed to load reminders: {e}")

# -----------------------------
# TEST BLOCK
# -----------------------------
if __name__ == "__main__":
    # Test temporary
    # create_temporary_reminder("Drink water", 5)
    
    # Test persistent (set for 10 seconds from now)
    # test_time = datetime.now() + timedelta(seconds=10)
    # create_persistent_reminder("Take a break", test_time)
    
    # load_persistent_reminders()
    pass
