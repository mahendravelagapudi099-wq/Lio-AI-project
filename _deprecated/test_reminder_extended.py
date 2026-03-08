import asyncio
import os
import sys
import json
from datetime import datetime, timedelta

# Add the project root to sys.path
sys.path.append(os.getcwd())

from Backend.app.reminder import create_persistent_reminder, load_persistent_reminders, REMINDERS_FILE
from Backend.Automation import HandleReminder

async def run_extended_tests():
    print("\n" + "="*50)
    print("--- EXTENDED REMINDER SYSTEM TESTS ---")
    print("="*50 + "\n")

    # 1. Test Missing Message
    print("[Test 1] Testing Missing Message...")
    # Expected: "Please specify what you want to be reminded about."
    await HandleReminder("remind me at 10:00 PM")
    
    # 2. Test Invalid Time Format
    print("\n[Test 2] Testing Invalid Time Format...")
    # Expected: "Sorry, I could not understand the reminder time."
    await HandleReminder("remind me to go to gym sometime tomorrow")

    # 3. Test Invalid Unit
    print("\n[Test 3] Testing Invalid Unit...")
    # Expected: "Please specify the time for the reminder." (or similar fallback)
    await HandleReminder("remind me to blink in many seconds")

    # 4. Test "Tomorrow" explicit vs implicit
    print("\n[Test 4] Testing 'Tomorrow' Parsing...")
    # If it's 10 PM and I say "at 8 AM", it should be tomorrow.
    passed_time = datetime.now() - timedelta(hours=2)
    passed_time_str = passed_time.strftime("%I:%M %p").lower()
    print(f"Current Time: {datetime.now().strftime('%I:%M %p')}")
    print(f"Setting reminder for: {passed_time_str} (should assume tomorrow)")
    await HandleReminder(f"remind me to wake up at {passed_time_str}")

    # 5. Test Past Cleanup (Manual Creation)
    print("\n[Test 5] Testing Past Reminder Cleanup...")
    past_time = datetime.now() - timedelta(minutes=10)
    with open(REMINDERS_FILE, "r") as f:
        data = json.load(f)
    
    data.append({
        "id": "expired_test_001",
        "message": "This should be deleted",
        "time": past_time.isoformat()
    })
    
    with open(REMINDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)
    
    print("Added an expired reminder to file. Loading...")
    load_persistent_reminders()
    
    with open(REMINDERS_FILE, "r") as f:
        final_data = json.load(f)
    
    expired_found = any(r["id"] == "expired_test_001" for r in final_data)
    if not expired_found:
        print("[SUCCESS] Expired reminder was cleaned up correctly.")
    else:
        print("[FAILURE] Expired reminder is still in the file.")

    # 6. Concurrent Temporary Reminders
    print("\n[Test 6] Testing Concurrent Temporary Reminders...")
    await HandleReminder("remind me Alpha in 2 seconds")
    await HandleReminder("remind me Beta in 3 seconds")
    await HandleReminder("remind me Gamma in 4 seconds")

    print("\n[Info] Waiting for concurrent triggers...")
    await asyncio.sleep(6)

    print("\n" + "="*50)
    print("EXTENDED TESTS INITIATED")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_extended_tests())
