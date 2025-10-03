import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values
from langdetect import detect
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
DEFAULT_VOICE = env_vars.get("AssistantVoice", "en-US-GuyNeural")

# Supported languages by Edge TTS
VOICE_MAP = {
    "en": "en-US-GuyNeural",
    "hi": "hi-IN-SwaraNeural",
    "te": "te-IN-SwaraNeural",
}
FallbackLanguage = "en"  # Translate to English if language not supported

# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)
SpeechFilePath = r"Data\speech.mp3"

async def TextToAudioFile(text: str, voice: str, retries=3):
    """Generate speech audio from text using Edge TTS with retry mechanism."""
    if os.path.exists(SpeechFilePath):
        os.remove(SpeechFilePath)

    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, voice, pitch='-3Hz', rate='+5%')
            await communicate.save(SpeechFilePath)
            return True
        except edge_tts.exceptions.NoAudioReceived:
            print(f"[Warning] No audio received. Retrying {attempt+1}/{retries}...")
    print("[Error] Failed to generate audio after retries.")
    return False

def TranslateIfNeeded(text: str) -> str:
    """Detect language and translate if not supported by Edge TTS."""
    try:
        lang = detect(text)
        if lang not in VOICE_MAP:
            text = mt.translate(text, FallbackLanguage)
        return text, lang
    except Exception as e:
        print(f"[Warning] Language detection failed: {e}")
        return text, "en"

def TTS(text: str, func=lambda r=None: True):
    """Convert text to speech and play using pygame."""
    while True:
        try:
            text_to_speak, lang = TranslateIfNeeded(text)
            voice = VOICE_MAP.get(lang[:2], DEFAULT_VOICE)
            print(f"[Info] Speaking in '{lang}' using voice '{voice}'")
            asyncio.run(TextToAudioFile(text_to_speak, voice))

            # Play audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(SpeechFilePath)
            pygame.mixer.music.play()
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                if not func():
                    break
                clock.tick(10)

            return True

        except Exception as e:
            print(f"[Error] TTS failed: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except:
                pass

def TextToSpeech(text: str, func=lambda r=None: True):
    """Decide whether to speak full text or a shortened version."""
    sentences = str(text).split(".")
    responses = [
        "The rest of the text is available on the chat screen, kindly check it out sir.",
        "Sir, please look at the chat screen for the remaining information.",
    ]

    if len(sentences) > 4 and len(text) >= 250:
        short_text = " ".join(sentences[:2]) + "." + random.choice(responses)
        TTS(short_text, func)
    else:
        TTS(text, func)

if __name__ == "__main__":
    print("Jarvis TTS running. Enter your text (Ctrl+C to exit).")
    while True:
        try:
            user_text = input("\nEnter the text: ").strip()
            if user_text:
                TextToSpeech(user_text)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
