"""
Backend/STTCloud.py - Cloud Speech-to-Text using Google Web Speech API
=========================================================================

This module provides cloud-based speech recognition as a fallback when
local STT (Faster Whisper) is unavailable or fails.

Uses the Google Web Speech API via the speech_recognition library.
This is free but requires internet connection.

Note: Google Web Speech API has limitations:
- Not for production use
- Limited requests per day
- Audio must be < 60 seconds
- Language support varies

For production, consider:
- Google Cloud Speech-to-Text (paid)
- AWS Transcribe (paid)
- Deepgram (paid, excellent quality)
- OpenAI Whisper API (paid, excellent quality)
"""

import os
import tempfile
import threading
from typing import Optional, Callable
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")


class STTCloudError(Exception):
    """Custom exception for STTCloud errors"""
    pass


class RecognitionListener:
    """
    Continuous recognition listener for real-time transcription.
    Uses Google Web Speech API with callbacks.
    """
    
    def __init__(
        self,
        language: str = "en-US",
        callback: Optional[Callable] = None,
        phrase_time_limit: Optional[float] = 10
    ):
        """
        Args:
            language: Language code (e.g., "en-US", "hi-IN")
            callback: Function to call with transcription results
            phrase_time_limit: Max seconds per phrase (None for no limit)
        """
        self.language = language
        self.callback = callback
        self.phrase_time_limit = phrase_time_limit
        self._recognizer = None
        self._microphone = None
        self._stop_event = threading.Event()
        self._listening = False
        
    def _init_hardware(self):
        """Initialize speech recognition hardware"""
        global _recognizer, _microphone
        
        if self._recognizer is None:
            try:
                import speech_recognition as sr
                self._recognizer = sr.Recognizer()
            except ImportError:
                raise STTCloudError("speech_recognition not installed. Run: pip install SpeechRecognition")
        
        if self._microphone is None:
            try:
                import speech_recognition as sr
                self._microphone = sr.Microphone()
            except ImportError:
                raise STTCloudError("pyaudio not installed. Run: pip install pyaudio")
                
    def start_listening(self):
        """Start continuous listening in background thread"""
        if self._listening:
            return
            
        self._init_hardware()
        self._stop_event.clear()
        self._listening = True
        
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        print("[STTCloud] Continuous listening started")
        
    def stop_listening(self):
        """Stop continuous listening"""
        self._stop_event.set()
        self._listening = False
        print("[STTCloud] Continuous listening stopped")
        
    def _listen_loop(self):
        """Main listening loop"""
        import speech_recognition as sr
        
        with self._microphone as source:
            # Adjust for ambient noise
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while not self._stop_event.is_set():
                try:
                    audio = self._recognizer.listen(
                        source,
                        phrase_time_limit=self.phrase_time_limit,
                        timeout=1
                    )
                    
                    # Recognize in background
                    thread = threading.Thread(
                        target=self._recognize_async,
                        args=(audio,),
                        daemon=True
                    )
                    thread.start()
                    
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"[STTCloud] Listen error: {e}")
                    if self._stop_event.is_set():
                        break
                        
    def _recognize_async(self, audio):
        """Recognize audio in background"""
        try:
            text = self._recognizer.recognize_google(
                audio,
                language=self.language
            )
            
            if text and self.callback:
                self.callback(text)
                
        except sr.UnknownValueError:
            pass  # Speech not understood
        except sr.RequestError as e:
            print(f"[STTCloud] API error: {e}")


def recognize_speech(
    audio_path: Optional[str] = None,
    audio_data: Optional[bytes] = None,
    language: str = None,
    duration: float = 10,
    sample_rate: int = 16000
) -> dict:
    """
    Recognize speech from audio file or microphone.
    
    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
        audio_data: Raw audio bytes (mutually exclusive with audio_path)
        language: Language code (e.g., "en-US", "hi-IN")
                  If None, uses InputLanguage from .env
        duration: Max recording duration in seconds (for mic input)
        sample_rate: Audio sample rate
        
    Returns:
        dict with keys:
        - text: Recognized text
        - confidence: Confidence score (Google doesn't provide, returns 1.0)
        - language: Language used
        - source: "file", "mic", or "api"
    """
    language = language or InputLanguage
    
    if audio_path:
        return _recognize_from_file(audio_path, language)
    elif audio_data:
        return _recognize_from_bytes(audio_data, language, sample_rate)
    else:
        return _recognize_from_microphone(language, duration)


def _recognize_from_file(audio_path: str, language: str) -> dict:
    """Recognize from audio file"""
    if not os.path.exists(audio_path):
        raise STTCloudError(f"Audio file not found: {audio_path}")
    
    try:
        import speech_recognition as sr
    except ImportError:
        raise STTCloudError("speech_recognition not installed")
    
    recognizer = sr.Recognizer()
    
    # Load audio file
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    
    try:
        # Recognize using Google Web Speech API
        text = recognizer.recognize_google(audio, language=language)
        
        return {
            "text": text,
            "confidence": 1.0,  # Google doesn't provide confidence
            "language": language,
            "source": "file"
        }
        
    except sr.UnknownValueError:
        raise STTCloudError("Speech not understood")
    except sr.RequestError as e:
        raise STTCloudError(f"API request failed: {e}")


def _recognize_from_bytes(audio_data: bytes, language: str, sample_rate: int) -> dict:
    """Recognize from raw audio bytes"""
    try:
        import speech_recognition as sr
        import io
        import wave
    except ImportError:
        raise STTCloudError("speech_recognition not installed")
    
    # Save bytes to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
        f.write(audio_data)
        temp_path = f.name
    
    try:
        return _recognize_from_file(temp_path, language)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _recognize_from_microphone(language: str, duration: float) -> dict:
    """Recognize from microphone (records for duration seconds)"""
    try:
        import speech_recognition as sr
    except ImportError:
        raise STTCloudError("speech_recognition not installed")
    
    recognizer = sr.Recognizer()
    
    print(f"[STTCloud] Recording for {duration} seconds...")
    
    with sr.Microphone() as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Record audio
        audio = recognizer.listen(source, phrase_time_limit=duration)
    
    try:
        # Recognize
        text = recognizer.recognize_google(audio, language=language)
        
        return {
            "text": text,
            "confidence": 1.0,
            "language": language,
            "source": "mic"
        }
        
    except sr.UnknownValueError:
        raise STTCloudError("Speech not understood")
    except sr.RequestError as e:
        raise STTCloudError(f"API request failed: {e}")


def test_microphone() -> dict:
    """
    Test microphone availability and return device info.
    
    Returns:
        dict with microphone information
    """
    try:
        import speech_recognition as sr
        
        mic = sr.Microphone()
        device_count = len(sr.Microphone.list_microphone_names())
        
        # Try to get default mic info
        try:
            with mic as source:
                pass
            mic_works = True
        except:
            mic_works = False
            
        return {
            "device_count": device_count,
            "default_mic_works": mic_works,
            "available": mic_works
        }
        
    except ImportError:
        return {
            "available": False,
            "error": "speech_recognition not installed"
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


def get_supported_languages() -> list:
    """Get list of supported language codes"""
    return [
        "en-US", "en-GB", "hi-IN", "te-IN", "ta-IN", "bn-IN",
        "mr-IN", "gu-IN", "kn-IN", "ml-IN", "pa-IN",
        "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR",
        "ru-RU", "ja-JP", "ko-KR", "zh-CN", "ar-SA"
    ]


# Legacy function for backward compatibility
def SpeechRecognition() -> tuple:
    """
    Legacy function for backward compatibility with old SpeechToText.py
    Returns: (text, language)
    """
    result = recognize_speech(language=InputLanguage, duration=10)
    return result["text"], result["language"]


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("STTCloud - Google Web Speech API Test Mode")
    print("=" * 60)
    
    # Test microphone
    print("\nTesting microphone...")
    mic_info = test_microphone()
    print(f"Microphone: {mic_info}")
    
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Record from microphone (10 seconds)")
    print("  2. List supported languages")
    print("  3. Test continuous listening (5 seconds)")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        try:
            result = recognize_speech(language=InputLanguage, duration=10)
            print(f"\nRecognized: {result['text']}")
            print(f"Language: {result['language']}")
        except STTCloudError as e:
            print(f"Error: {e}")
            
    elif choice == "2":
        print("\nSupported languages:")
        for lang in get_supported_languages():
            print(f"  - {lang}")
            
    elif choice == "3":
        results = []
        
        def callback(text):
            print(f"Recognized: {text}")
            results.append(text)
        
        listener = RecognitionListener(language=InputLanguage, callback=callback)
        listener.start_listening()
        
        print("Listening for 5 seconds...")
        import time
        time.sleep(5)
        listener.stop_listening()
        
        print(f"\nResults: {results}")
        
    else:
        print("Invalid choice")
