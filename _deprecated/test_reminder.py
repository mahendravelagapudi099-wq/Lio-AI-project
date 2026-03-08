import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the project root to sys.path
sys.path.append(os.getcwd())

from Backend.app.reminder import create_temporary_reminder, create_persistent_reminder, load_persistent_reminders
from Backend.Automation import HandleReminder

async def run_tests():
    print("\n--- Starting Reminder System Tests ---\n")

    # 1. Test Temporary Reminder via HandleReminder
    print("[Test 1] Testing Temporary Reminder Parsing...")
    # Expected: "Reminder set for 5 seconds."
    await HandleReminder("remind me to check mail in 5 seconds")
    
    # 2. Test Persistent Reminder via HandleReminder (Fixed Time)
    print("\n[Test 2] Testing Persistent Reminder Parsing...")
    # Calculate a time 10 seconds from now
    target_time = datetime.now() + timedelta(seconds=10)
    time_str = target_time.strftime("%I:%M %p").lower()
    
    # Expected: "Reminder saved for today at ..."
    await HandleReminder(f"remind me to call mom at {time_str}")

    # 3. Test Manual Persistent Creation
    print("\n[Test 3] Testing Manual Persistent Creation (for reload test)...")
    manual_time = datetime.now() + timedelta(seconds=20)
    create_persistent_reminder("Deep test reminder", manual_time)
    
    print("\n[Info] Waiting 6 seconds for temporary reminder to trigger...")
    await asyncio.sleep(6)

    # 4. Test Reload Logic
    print("\n[Test 4] Testing Reload Logic (simulating restart)...")
    # This will resume the "Deep test reminder" and the "call mom" reminder if it hasn't fired
    load_persistent_reminders()

    print("\n[Info] Tests initiated. Check console for 'Reminder: ...' messages over the next 20 seconds.")
    print("[Info] Reminder JSON content:")
    if os.path.exists("Backend/Data/reminders.json"):
        with open("Backend/Data/reminders.json", "r") as f:
            print(f.read())

if __name__ == "__main__":
    asyncio.run(run_tests())
