
import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.Automation import ParseCommand

# The 100 generated phrases
phrases = [
    # Category 1: Short Commands
    "5 minute timer", "timer 10 mins", "20 seconds", "1 hour reminder", "timer 5m",
    "reminder 2h", "10m timer", "30s reminder", "5 min break", "45 minute focus",
    "timer 15", "10 minute nap", "2 hour meeting", "5s test", "1 minute plank",
    "3m eggs", "25m pomodoro", "reminder 10", "1h workout", "timer 30",

    # Category 2: Missing Connectors
    "timer 5 minutes pasta", "set timer 10 minutes run", "reminder 1 hour call mom",
    "timer 20 mins check oven", "reminder 30 seconds stretch", "set timer 15 minutes laundry",
    "timer 5m tea", "remind me 2 hours pills", "timer 45 minutes study", "reminder 10 mins water",
    "timer 1 hour meeting prep", "set timer 3 minutes noodles", "remind 15 mins check email",
    "timer 20 seconds plank", "reminder 4 hours feed dog", "timer 10m yoga",
    "set timer 5s debug", "remind 30m lunch", "timer 1h deep work", "reminder 50m bus",

    # Category 3: Reordered Phrases
    "pasta timer 10 minutes", "meeting reminder 1 hour", "call dad remind me in 20 mins",
    "stretch timer 30 minutes", "pizzatimer 15 mins", "check server reminder 5 minutes",
    "break time 10 mins set timer", "laundry done in 1 hour remind me", "water check 30 minutes reminder",
    "eggs boil 3 minutes timer", "nap 20 minutes start", "focus mode 25 minutes timer",
    "workout 1 hour set reminder", "pills 10 am remind me", "tea ready 5 minutes timer",
    "download check 20 mins reminder", "meeting start 2pm reminder", "oven off 30 minutes timer",
    "pick up kids 3 pm remind", "wifi reset 10 seconds timer",

    # Category 4: Casual Speech
    "hey set a timer for like 10 minutes", "can you remind me to leave in 1 hour",
    "i need a timer for 5 minutes please", "give me 20 minutes for a nap",
    "please let me know when 30 minutes is up", "throw a timer on for 15 mins",
    "actually make that a 45 minute timer", "remind me in a sec to check the logs",
    "set an alarm or something for 10 minutes", "count down 1 minute for me",
    "remind me about the meeting in 2 hours", "quick timer 5 seconds",
    "wake me up in 20 minutes", "don't let me forget to call in 10 mins",
    "ping me in an hour", "buzz me in 30 seconds", "i need 5 minutes",
    "create a timeline for 1 hour", "let's do a 15 minute sprint", "remind me later say 4 hours",

    # Category 5: Imperative Style
    "Timer. 5 minutes.", "Remind me. 1 hour.", "Start countdown 10 minutes",
    "Mark 20 minutes", "Alert me in 30 seconds", "Notify 1 hour",
    "Begin timer 15 mins", "Schedule reminder 2 hours", "Clock 5 minutes",
    "Tracker 10 mins", "Countdown 60 seconds", "Set 25 minutes",
    "Time 3 minutes", "Alarm 10 minutes", "Warn me in 5 mins",
    "Signal 1 hour", "Trigger reminder 45 mins", "Log 30 minutes",
    "Record 1 hour", "Halt in 10 minutes"
]

print("| Phrase | Intent | Routed | Pass/Fail |")
print("|---|---|---|---|")

passes = 0
fails = 0

for phrase in phrases:
    # Normalize simply for print
    phrase_clean = phrase.replace("\n", " ")
    
    intent, routed_cmd = ParseCommand(phrase)
    
    # Validation Rule: Must return "reminder" intent
    pass_fail = "PASS"
    if intent != "reminder":
        pass_fail = "**FAIL**"
        fails += 1
    else:
        passes += 1
        
    print(f"| {phrase_clean} | {intent} | {routed_cmd} | {pass_fail} |")

print(f"\nTotal: {passes} Passed, {fails} Failed")
