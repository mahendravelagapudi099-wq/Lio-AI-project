import os
import time
import pygame
import pyttsx3
from dotenv import dotenv_values
from langdetect import detect
import mtranslate as mt
from threading import Lock, current_thread
from datetime import datetime
import random
import asyncio
import edge_tts

# =========================
# GLOBAL INITIALIZATION
# =========================

# Load environment variables
env_vars = dotenv_values(".env")

DEFAULT_VOICE = env_vars.get("AssistantVoice", "en-IN-PrabhatNeural")

VOICE_MAP = {
    "en": DEFAULT_VOICE,
    "hi": env_vars.get("AssistantVoice_hi", "hi-IN-SwaraNeural"),
    "te": "te-IN-SwaraNeural",
}

FallbackLanguage = "en"

# Create Data folder
os.makedirs("Data", exist_ok=True)

# Use MP3 (stable with Edge-TTS and Pygame)
SpeechFilePath = r"Data\speech.mp3"

# Deferred Hardware Initialization for Phased Startup
offline_engine = None
_init_lock = Lock()
_initialized = False

def InitializeTTSHardware():
    """Explicit initialization for deferred/phased hardware setup. Thread-safe and idempotent."""
    global offline_engine, _initialized
    
    # 1. Double-checked locking to avoid overhead
    if _initialized:
        return True
        
    with _init_lock:
        # Check again inside the lock
        if _initialized:
            return True
            
        try:
            # Initialize Pygame Mixer
            if not pygame.mixer.get_init():
                print("[TTS] Initialising Pygame Mixer...")
                pygame.mixer.init()
            
            # Initialize Offline Engine
            if offline_engine is None:
                print("[TTS] Initialising Offline TTS Engine...")
                offline_engine = pyttsx3.init()
                voices = offline_engine.getProperty('voices')
                if voices:
                    offline_engine.setProperty('voice', voices[0].id)
                offline_engine.setProperty('rate', 170)
            
            _initialized = True
            return True
        except Exception as e:
            print(f"[TTS] Hardware Initialization Failed: {e}")
            return False

# Prevent multiple audio access
tts_lock = Lock()

# Concurrency & Rate Limiting Globals
last_tts_request_time = 0.0
last_tts_text = ""
COOLDOWN_DURATION = 1.0  # Seconds between requests
DUPLICATE_THRESHOLD = 0.5 # Seconds to ignore exact same text

def Log(message, level="Info"):
    """Enhanced logging with timestamp and thread name."""
    now = datetime.now().strftime("%H:%M:%S")
    thread_name = current_thread().name
    print(f"[{now}] [{thread_name}] [{level}] {message}")

# =========================
# HELPER FUNCTIONS
# =========================

def wait_for_audio_file(path, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1000:
                return True
        time.sleep(0.1)

    Log("Audio file timed out or too small", "Warning")
    return False


def TranslateIfNeeded(text):

    # Force English for short assistant responses & commands
    if len(text) < 120:
        return text, "en"

    try:
        lang = detect(text)

        if lang not in VOICE_MAP:
            text = mt.translate(text, FallbackLanguage)

        return text, lang

    except Exception as e:
        print("[Warning] Language detection failed:", e)
        return text, "en"



# =========================
# OFFLINE FALLBACK
# =========================

def TTS_Offline(text):
    global offline_engine
    try:
        InitializeTTSHardware()
            
        Log("Speaking using OFFLINE TTS (pyttsx3)", "Fallback")
        if offline_engine:
            offline_engine.say(text)
            offline_engine.runAndWait()
    except Exception as e:
        Log(f"Offline TTS failed: {e}", "Critical")


# =========================
# EDGE TTS GENERATOR
# =========================

async def TextToAudioFile(text, voice, retries=3):

    for attempt in range(retries):

        try:
            # Safe deletion with retries (Windows file lock protection)
            if os.path.exists(SpeechFilePath):
                for _ in range(5):
                    try:
                        os.remove(SpeechFilePath)
                        break
                    except PermissionError:
                        time.sleep(0.2)

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate="+5%",
                pitch="-3Hz"
            )

            await communicate.save(SpeechFilePath)

            if wait_for_audio_file(SpeechFilePath):
                Log("Edge TTS: Audio file ready")
                return True

            Log(f"Edge TTS: Audio not ready. Retry {attempt+1}/{retries}", "Warning")

        except edge_tts.exceptions.NoAudioReceived:
            Log(f"Edge TTS: No audio received. Retry {attempt+1}/{retries}", "Warning")

        except Exception as e:
            Log(f"Edge TTS Error: {e}. Retry {attempt+1}/{retries}", "Error")

        # ✅ IMPORTANT — Delay BETWEEN retries (Anti-throttle)
        time.sleep(0.6)

    Log("Edge TTS: Failed completely after retries", "Error")
    return False



# =========================
# MAIN TTS FUNCTION
# =========================

def TTS(text, func=lambda r=None: True):
    global last_tts_request_time, last_tts_text

    current_time = time.time()
    
    # 1. PRE-LOCK CHECKS (Avoid unnecessary blocking)
    # Check for Duplicate suppression (burst protection)
    if text == last_tts_text and (current_time - last_tts_request_time) < DUPLICATE_THRESHOLD:
        Log(f"Skipping duplicate TTS request: '{text[:30]}...'", "BurstProtection")
        return False

    # Check for Cooldown
    time_since_last = current_time - last_tts_request_time
    if time_since_last < COOLDOWN_DURATION:
        wait_needed = COOLDOWN_DURATION - time_since_last
        Log(f"Throttling TTS request (Cooldown: {wait_needed:.2f}s remaining)", "RateLimit")
        time.sleep(wait_needed)
    
    # Update state
    last_tts_request_time = time.time()
    last_tts_text = text

    Log(f"TTS Invocated for: '{text[:50]}...'", "Queue")

    # Step 6: Ensure hardware is ready (Hardened Idempotent Init)
    # Step 6: Ensure hardware is ready (Hardened Idempotent Init)
    InitializeTTSHardware()

    success = False
    
    # Attempt Edge TTS with Lock
    with tts_lock:
        Log("Acquired TTS lock", "Lock")
        try:
            text_to_speak, lang = TranslateIfNeeded(text)
            voice = VOICE_MAP.get(lang[:2], DEFAULT_VOICE)

            Log(f"Generating audio in '{lang}' using voice '{voice}'")
            
            # Windows Threading Fix for Asyncio
            if os.name == 'nt':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # Safe async loop for threads
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if loop.run_until_complete(TextToAudioFile(text_to_speak, voice)):
                    success = True
            finally:
                loop.close()

            if success:
                # 0.1s is enough for file system sync
                time.sleep(0.1) 
                
                try:
                    pygame.mixer.music.load(SpeechFilePath)
                    pygame.mixer.music.play()
                except Exception as e:
                    Log(f"Pygame load/play failed: {e}", "Error")
                    raise  # Trigger fallback handling (outside lock)

                Log("Playback started", "Audio")
                clock = pygame.time.Clock()

                while pygame.mixer.music.get_busy():
                    if not func():
                        Log("Playback interrupted by user function", "Audio")
                        break
                    clock.tick(10)

                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                time.sleep(0.2) # Give OS time to release file handle
                Log("Playback finished", "Audio")
            
            else:
                Log("Edge TTS failed — marking for fallback", "Warning")
                success = False

        except Exception as e:
            Log(f"TTS System Crash: {e}", "Critical")
            success = False

        finally:
            try:
                func(False)
            except:
                pass
            Log("Released TTS lock", "Lock")

    # Handle Fallback OUTSIDE the lock to prevent deadlocks
    if not success:
        Log("Delegating to Offline TTS (Outside Lock)", "Fallback")
        TTS_Offline(text)
        return True
    
    return True


# =========================
# SMART TEXT SPEAKER
# =========================

def TextToSpeech(text, func=lambda r=None: True):

    sentences = str(text).split(".")

    responses = [
        "The rest of the text is available on the chat screen, kindly check it out sir.",
        "Sir, please look at the chat screen for the remaining information.",
    ]

    if len(sentences) > 4 and len(text) >= 250:
        short_text = " ".join(sentences[:2]) + ". " + random.choice(responses)
        TTS(short_text, func)
    else:
        TTS(text, func)


# =========================
# TEST MODE
# =========================

if __name__ == "__main__":

    print("\nLIO TTS SYSTEM READY")
    print("Type text and press Enter\n")

    while True:
        try:
            user_text = input("Say: ").strip()
            if user_text:
                TextToSpeech(user_text)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
