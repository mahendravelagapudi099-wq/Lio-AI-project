"""
Backend/STT.py - Unified Speech-to-Text Router
==============================================

This module routes speech recognition requests between:
1. Local STT (Faster Whisper) - Fast, private, works offline
2. Cloud STT (Google Web Speech API) - Fallback when local fails

Configuration (via .env):
- STT_MODE: "local", "cloud", or "hybrid" (try local first, fall back to cloud)
- WHISPER_MODEL: Model size for local STT ("tiny", "base", "small")
- WHISPER_LANGUAGE: Language code or "auto"
"""

import os
import tempfile
import numpy as np
from typing import Optional
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Configuration
STT_MODE = env_vars.get("STT_MODE", "hybrid")  # local, cloud, hybrid
DEFAULT_LANGUAGE = env_vars.get("WHISPER_LANGUAGE", "auto")


class STTError(Exception):
    """Custom exception for STT errors"""
    pass


def transcribe(
    audio_data: Optional[np.ndarray] = None,
    audio_path: Optional[str] = None,
    language: Optional[str] = None,
    mode: Optional[str] = None
) -> dict:
    """
    Unified transcription function.
    
    Args:
        audio_data: Audio as numpy array (float32, -1 to 1)
        audio_path: Path to audio file (alternative to audio_data)
        language: Language code or "auto"
        mode: Override STT_MODE ("local", "cloud", "hybrid")
        
    Returns:
        dict with keys:
        - text: Transcribed text
        - language: Detected/used language
        - source: "local" or "cloud"
        - confidence: Confidence score (if available)
    """
    mode = mode or STT_MODE
    lang = language or DEFAULT_LANGUAGE
    
    # Handle audio input
    temp_file = None
    
    try:
        # Convert audio data to temp file if needed
        if audio_data is not None:
            temp_file = _save_temp_audio(audio_data)
            audio_path = temp_file
            
        if not audio_path:
            raise STTError("Either audio_data or audio_path must be provided")
        
        # Route based on mode
        if mode == "local":
            return _transcribe_local(audio_path, lang)
        elif mode == "cloud":
            return _transcribe_cloud(audio_path, lang)
        elif mode == "hybrid":
            # Try local first, fall back to cloud
            try:
                return _transcribe_local(audio_path, lang)
            except Exception as e:
                print(f"[STT] Local STT failed: {e}, trying cloud...")
                try:
                    return _transcribe_cloud(audio_path, lang)
                except Exception as e2:
                    raise STTError(f"All STT methods failed. Local: {e}, Cloud: {e2}")
        else:
            raise STTError(f"Unknown STT mode: {mode}")
            
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass


def _transcribe_local(audio_path: str, language: str) -> dict:
    """Transcribe using local Faster Whisper"""
    try:
        from Backend.STTLocal import transcribe_audio
        
        result = transcribe_audio(
            audio_path=audio_path,
            language=language,
            vad_filter=True
        )
        
        return {
            "text": result["text"],
            "language": result["language"],
            "source": "local",
            "confidence": result.get("language_probability", 1.0),
            "duration": result.get("duration", 0)
        }
        
    except ImportError:
        raise STTError("Local STT not available (faster-whisper not installed)")
    except Exception as e:
        raise STTError(f"Local STT failed: {e}")


def _transcribe_cloud(audio_path: str, language: str) -> dict:
    """Transcribe using cloud Google Web Speech API"""
    try:
        from Backend.STTCloud import recognize_speech
        
        # Convert language format (en-US -> en)
        lang_code = language.split("-")[0] if "-" in language else language
        
        result = recognize_speech(
            audio_path=audio_path,
            language=f"{lang_code}-{lang_code.upper()}"
        )
        
        return {
            "text": result["text"],
            "language": result["language"],
            "source": "cloud",
            "confidence": result.get("confidence", 0.9),
            "duration": 0
        }
        
    except ImportError:
        raise STTError("Cloud STT not available (speech_recognition not installed)")
    except Exception as e:
        raise STTError(f"Cloud STT failed: {e}")


def _save_temp_audio(audio_data: np.ndarray) -> str:
    """Save audio data to temporary WAV file"""
    import scipy.io.wavfile as wav
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    # Convert float32 to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    
    wav.write(temp_file.name, 16000, audio_int16)
    temp_file.close()
    
    return temp_file.name


def get_stt_info() -> dict:
    """Get current STT configuration info"""
    from Backend.STTLocal import is_model_loaded, get_model_info
    
    return {
        "mode": STT_MODE,
        "language": DEFAULT_LANGUAGE,
        "local_available": True,  # Will be True if faster-whisper is installed
        "cloud_available": True,  # Will be True if speech_recognition is installed
        "local_model_info": get_model_info() if is_model_loaded() else None
    }


def is_local_available() -> bool:
    """Check if local STT is available"""
    try:
        from Backend.STTLocal import get_model
        return True
    except:
        return False


def is_cloud_available() -> bool:
    """Check if cloud STT is available"""
    try:
        from Backend.STTCloud import test_microphone
        result = test_microphone()
        return result.get("available", False)
    except:
        return False


# Legacy function for backward compatibility
def SpeechRecognition() -> tuple:
    """
    Legacy function for backward compatibility.
    Uses cloud STT (Google Web Speech) as it's more reliable for mic input.
    """
    try:
        from Backend.STTCloud import recognize_speech
        result = recognize_speech(language=DEFAULT_LANGUAGE, duration=10)
        return result["text"], result["language"]
    except Exception as e:
        print(f"[STT] Speech recognition error: {e}")
        return None, None


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("STT Router - Test Mode")
    print("=" * 60)
    
    print(f"\nCurrent Configuration:")
    info = get_stt_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Test local STT (from file)")
    print("  2. Test cloud STT (from microphone)")
    print("  3. Test hybrid mode (local -> cloud fallback)")
    print("  4. Check availability")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        audio_file = input("Enter audio file path: ").strip()
        if audio_file:
            result = transcribe(audio_path=audio_file, mode="local")
            print(f"\nResult: {result['text']}")
            print(f"Source: {result['source']}")
        else:
            print("No file specified")
            
    elif choice == "2":
        print("Recording from microphone...")
        try:
            from Backend.STTCloud import recognize_speech
            result = recognize_speech(duration=5)
            print(f"\nResult: {result['text']}")
        except Exception as e:
            print(f"Error: {e}")
            
    elif choice == "3":
        audio_file = input("Enter audio file path: ").strip()
        if audio_file:
            result = transcribe(audio_path=audio_file, mode="hybrid")
            print(f"\nResult: {result['text']}")
            print(f"Source: {result['source']}")
        else:
            print("No file specified")
            
    elif choice == "4":
        print("\nLocal STT available:", is_local_available())
        print("Cloud STT available:", is_cloud_available())
        
    else:
        print("Invalid choice")
