import threading
from time import sleep
from Backend.TextToSpeech import TextToSpeech
from Frontend.GUI import SetAsssistantStatus, ShowTextToScreen, SetMicrophoneStatus
from dotenv import dotenv_values
import datetime
import speech_recognition as sr
import random

# Load environment variables
env_vars = dotenv_values(".env")
AssistantName = env_vars.get("Assistantname", "friday")
Username = env_vars.get("Username", "User")

# Hotword configuration
HOTWORDS = ["friday", f"hey {AssistantName.lower()}", f"ok {AssistantName.lower()}"]

# Time-based greeting responses with natural, contextual variations
GREETINGS = {
    "morning": [
        f"Good morning {Username}. Hope you slept well.",
        f"Morning {Username}. Fresh start to the day ahead.",
        f"Hello {Username}. Ready to tackle today?",
        f"Good morning {Username}. How can I assist you today?",
        f"Morning {Username}. What's on your agenda?",
        f"Good morning {Username}. Beautiful day to get things done.",
        f"Hello {Username}. Let's make today productive.",
        f"Morning {Username}. Coffee ready? Let's begin.",
        f"Good morning {Username}. Early start, that's great.",
        f"Morning {Username}. How are you feeling today?",
    ],
    "afternoon": [
        f"Good afternoon {Username}. How's your day going?",
        f"Afternoon {Username}. Need any help with your tasks?",
        f"Hello {Username}. Hope the morning was productive.",
        f"Good afternoon {Username}. What can I help you with?",
        f"Afternoon {Username}. Time for a quick break?",
        f"Hello {Username}. Halfway through the day already.",
        f"Good afternoon {Username}. Keeping up with everything?",
        f"Afternoon {Username}. Need to organize anything?",
        f"Hello {Username}. What's next on your list?",
        f"Good afternoon {Username}. How can I support you?",
    ],
    "evening": [
        f"Good evening {Username}. How was your day?",
        f"Evening {Username}. Wrapping things up?",
        f"Hello {Username}. Ready to unwind?",
        f"Good evening {Username}. Need help with anything before you relax?",
        f"Evening {Username}. Day coming to a close.",
        f"Hello {Username}. Time to wind down soon.",
        f"Good evening {Username}. Did you accomplish what you planned?",
        f"Evening {Username}. What do you need help with?",
        f"Hello {Username}. Switching to evening mode.",
        f"Good evening {Username}. Let's finish up your tasks.",
    ],
    "night": [
        f"Hello {Username}. Working late tonight?",
        f"Evening {Username}. Getting quite late.",
        f"Hello {Username}. Don't forget to rest when you're done.",
        f"Late evening {Username}. What do you need help with?",
        f"Hello {Username}. Still going strong I see.",
        f"Evening {Username}. Remember to take breaks.",
        f"Hello {Username}. Burning the midnight oil?",
        f"Late night {Username}. How can I assist?",
        f"Hello {Username}. Almost time to call it a day.",
        f"Evening {Username}. Need anything before bed?",
    ]
}

# Casual acknowledgments for subsequent activations
ACKNOWLEDGMENTS = [
    f"Yes {Username}?",
    f"I'm listening {Username}.",
    f"How can I help {Username}?",
    f"What do you need {Username}?",
    f"I'm here {Username}.",
    f"Ready when you are {Username}.",
    "Yes, I'm here.",
    "What can I do for you?",
    "Go ahead.",
    "Listening.",
]

# Quick responses for common queries
QUICK_RESPONSES = {
    "how are you": [
        "I'm functioning perfectly! How can I assist you?",
        "All systems operational! What do you need?",
        "I'm doing great! Ready to help you.",
    ],
    "what's your name": [
        f"I'm {AssistantName}, your AI assistant!",
        f"My name is {AssistantName}. How can I help?",
    ],
    "thank you": [
        f"You're welcome {Username}!",
        f"Happy to help {Username}!",
        "Anytime!",
        "My pleasure!",
    ],
    "thanks": [
        f"You're welcome {Username}!",
        "No problem!",
        "Happy to help!",
    ],
}

# Flag to prevent overlapping speech
is_speaking = threading.Event()
last_activation_time = None
hotword_triggered = False

# Initialize recognizer and microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone()


def get_time_based_greeting():
    """Return a contextual greeting based on the current time and day."""
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    day_of_week = now.strftime("%A")
    is_weekend = day_of_week in ["Saturday", "Sunday"]
    
    # Very early morning (5 AM - 6:59 AM)
    if 5 <= hour < 7:
        early_greetings = [
            f"Very early start {Username}. Impressive dedication.",
            f"Good morning {Username}. You're up early today.",
            f"Early bird {Username}. How can I help?",
            f"Morning {Username}. Getting a head start on the day.",
        ]
        return random.choice(early_greetings)
    
    # Morning (7 AM - 11:59 AM)
    elif 7 <= hour < 12:
        if is_weekend:
            weekend_morning = [
                f"Good morning {Username}. Enjoying your {day_of_week}?",
                f"Morning {Username}. Nice to have a relaxed {day_of_week}.",
                f"Hello {Username}. What's planned for today?",
            ]
            return random.choice(weekend_morning)
        else:
            return random.choice(GREETINGS["morning"])
    
    # Lunch time (12 PM - 1:30 PM)
    elif 12 <= hour < 14 and minute < 30:
        lunch_greetings = [
            f"Afternoon {Username}. Lunch time already.",
            f"Good afternoon {Username}. Time for a break?",
            f"Hello {Username}. Have you had lunch yet?",
            f"Afternoon {Username}. Midday check-in.",
        ]
        return random.choice(lunch_greetings)
    
    # Afternoon (12 PM - 4:59 PM)
    elif 12 <= hour < 17:
        if is_weekend:
            weekend_afternoon = [
                f"Good afternoon {Username}. Hope you're having a nice {day_of_week}.",
                f"Afternoon {Username}. Relaxing weekend so far?",
                f"Hello {Username}. Making the most of your day off?",
            ]
            return random.choice(weekend_afternoon)
        else:
            return random.choice(GREETINGS["afternoon"])
    
    # Evening (5 PM - 8:59 PM)
    elif 17 <= hour < 21:
        if is_weekend:
            weekend_evening = [
                f"Good evening {Username}. How was your weekend?",
                f"Evening {Username}. Enjoying your free time?",
                f"Hello {Username}. Weekend coming to a close.",
            ]
            return random.choice(weekend_evening)
        else:
            return random.choice(GREETINGS["evening"])
    
    # Late night (9 PM - 11:59 PM)
    elif 21 <= hour < 24:
        late_night = [
            f"Late evening {Username}. Still some work to do?",
            f"Hello {Username}. Getting quite late now.",
            f"Evening {Username}. Don't forget to rest soon.",
            f"Late night {Username}. What do you need help with?",
        ]
        return random.choice(late_night)
    
    # Very late night (12 AM - 4:59 AM)
    else:
        very_late = [
            f"Very late {Username}. You should rest when possible.",
            f"Hello {Username}. It's past midnight.",
            f"Late night {Username}. Remember to take care of yourself.",
            f"Hello {Username}. Working through the night?",
        ]
        return random.choice(very_late)


def get_current_time():
    """Return current time in HH:MM AM/PM format."""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")


def get_current_date():
    """Return current date in a friendly format."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")


def check_quick_response(query):
    """Check if query matches a quick response pattern."""
    query_lower = query.lower().strip()
    
    for key, responses in QUICK_RESPONSES.items():
        if key in query_lower:
            return random.choice(responses)
    
    return None


def should_use_acknowledgment():
    """Determine if we should use a quick acknowledgment instead of full greeting."""
    global last_activation_time
    
    if last_activation_time is None:
        return False
    
    # If last activation was within 5 minutes, use acknowledgment
    time_diff = (datetime.datetime.now() - last_activation_time).total_seconds()
    return time_diff < 300  # 5 minutes


def HotwordListener(main_execution_callback):
    """
    Continuously listens for the hotword using the real microphone.
    Provides context-aware responses.
    """
    global hotword_triggered, last_activation_time
    
    SetAsssistantStatus("Listening for hotword...")
    print(f"Hotword listener started. Say '{HOTWORDS[0]}' to activate!")

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = recognizer.listen(source, phrase_time_limit=5)

            try:
                query = recognizer.recognize_google(audio).lower()
                print(f"Heard: {query}")

                # Check if hotword is detected
                if any(hotword in query for hotword in HOTWORDS):
                    if is_speaking.is_set():
                        print("Already processing, please wait...")
                        continue

                    is_speaking.set()
                    last_activation_time = datetime.datetime.now()
                    SetAsssistantStatus("Hotword detected...")

                    # First time activation - Full greeting
                    if not hotword_triggered:
                        greeting = get_time_based_greeting()
                        current_time = f"The current time is {get_current_time()}."
                        date_info = f"Today is {get_current_date()}."

                        ShowTextToScreen(f"{AssistantName}: {greeting}\n{date_info}\n{current_time}")
                        
                        TextToSpeech(greeting)
                        TextToSpeech(date_info)
                        TextToSpeech(current_time)
                        TextToSpeech("How can I help you today?")

                        hotword_triggered = True
                        SetMicrophoneStatus("True")
                        SetAsssistantStatus("Ready for commands...")
                    
                    # Subsequent activations - Quick acknowledgment
                    else:
                        # Remove hotword from query to get actual command
                        command = query
                        for hotword in HOTWORDS:
                            command = command.replace(hotword, "").strip()
                        
                        # If there's a command after the hotword
                        if len(command) > 3:
                            # Check for quick response
                            quick_response = check_quick_response(command)
                            if quick_response:
                                ShowTextToScreen(f"{Username}: {command}\n{AssistantName}: {quick_response}")
                                TextToSpeech(quick_response)
                            else:
                                # Process as normal command
                                acknowledgment = random.choice(ACKNOWLEDGMENTS)
                                ShowTextToScreen(f"{Username}: {command}")
                                TextToSpeech(acknowledgment)
                                
                                SetMicrophoneStatus("True")
                                SetAsssistantStatus("Processing command...")
                                
                                threading.Thread(
                                    target=main_execution_callback,
                                    args=(command,),
                                    daemon=True
                                ).start()
                        else:
                            # Just hotword, no command
                            acknowledgment = random.choice(ACKNOWLEDGMENTS)
                            TextToSpeech(acknowledgment)
                            SetMicrophoneStatus("True")
                            SetAsssistantStatus("Listening for commands...")

                    is_speaking.clear()

                # If hotword was triggered before, listen for direct commands
                elif hotword_triggered and len(query) > 3:
                    if is_speaking.is_set():
                        continue

                    is_speaking.set()
                    
                    # Check for quick response
                    quick_response = check_quick_response(query)
                    if quick_response:
                        ShowTextToScreen(f"{Username}: {query}\n{AssistantName}: {quick_response}")
                        TextToSpeech(quick_response)
                    else:
                        SetMicrophoneStatus("True")
                        SetAsssistantStatus("Processing command...")
                        
                        threading.Thread(
                            target=main_execution_callback,
                            args=(query,),
                            daemon=True
                        ).start()

                    is_speaking.clear()

            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Speech Recognition error: {e}")
                sleep(1)

        except Exception as e:
            print(f"[Hotword Listener Error]: {e}")
            sleep(1)


def StartHotwordThread(main_execution_callback):
    """Start hotword detection in a separate daemon thread."""
    thread = threading.Thread(
        target=HotwordListener,
        args=(main_execution_callback,),
        daemon=True
    )
    thread.start()
    print("Hotword listener thread started.")