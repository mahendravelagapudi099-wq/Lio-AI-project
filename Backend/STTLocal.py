"""
Backend/STTLocal.py - Local Speech-to-Text using Faster Whisper
=========================================================================

Faster Whisper is a reimplementation of OpenAI's Whisper model using CTranslate2,
which is significantly faster (up to 4x) and uses less memory.

Model Sizes:
- tiny: ~39 MB - Fastest, lower accuracy
- base: ~74 MB - Good balance
- small: ~244 MB - Better accuracy
- medium: ~769 MB - High accuracy (requires GPU for speed)
- large: ~1550 MB - Best accuracy

This implementation supports:
- Multiple model sizes (configurable via .env)
- Language auto-detection
- INT8/INT16 quantization for faster inference
- VAD (Voice Activity Detection) integration
- Streaming transcription for real-time use
"""

import os
import tempfile
from typing import Optional, Union, Generator
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Configuration
DEFAULT_MODEL_SIZE = env_vars.get("WHISPER_MODEL", "base")
DEFAULT_LANGUAGE = env_vars.get("WHISPER_LANGUAGE", "auto")
DEFAULT_DEVICE = "auto"  # "auto", "cuda", "cpu"
DEFAULT_COMPUTE_TYPE = "auto"  # "auto", "int8", "int8_float16", "float16"

# Global model instance (lazy loaded)
_model = None
_model_size = None


class STTLocalError(Exception):
    """Custom exception for STTLocal errors"""
    pass


def get_model():
    """
    Get or load the Faster Whisper model.
    Uses lazy loading to avoid blocking startup.
    """
    global _model, _model_size
    
    # Check if model needs to be reloaded (size changed)
    if _model is not None and _model_size != DEFAULT_MODEL_SIZE:
        print(f"[STTLocal] Model size changed from {_model_size} to {DEFAULT_MODEL_SIZE}, reloading...")
        _model = None
    
    if _model is None:
        try:
            from faster_whisper import WhisperModel
            
            print(f"[STTLocal] Loading Faster Whisper model: {DEFAULT_MODEL_SIZE}")
            print(f"[STTLocal] Device: {DEFAULT_DEVICE}, Compute: {DEFAULT_COMPUTE_TYPE}")
            
            _model = WhisperModel(
                DEFAULT_MODEL_SIZE,
                device=DEFAULT_DEVICE,
                compute_type=DEFAULT_COMPUTE_TYPE,
                download_root=os.path.join(os.getcwd(), "models", "whisper")
            )
            _model_size = DEFAULT_MODEL_SIZE
            print(f"[STTLocal] Model loaded successfully!")
            
        except ImportError:
            raise STTLocalError("faster-whisper not installed. Run: pip install faster-whisper")
        except Exception as e:
            raise STTLocalError(f"Failed to load Whisper model: {e}")
    
    return _model


def is_model_loaded() -> bool:
    """Check if the model is currently loaded"""
    global _model
    return _model is not None


def unload_model():
    """Unload the model to free memory"""
    global _model, _model_size
    _model = None
    _model_size = None
    print("[STTLocal] Model unloaded")


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    task: str = "transcribe",
    beam_size: int = 5,
    vad_filter: bool = True,
    vad_parameters: Optional[dict] = None,
    initial_prompt: Optional[str] = None,
    word_timestamps: bool = False
) -> dict:
    """
    Transcribe audio file to text.
    
    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
        language: Language code (e.g., "en", "hi") or "auto" for auto-detection
        task: "transcribe" or "translate" (translate to English)
        beam_size: Beam size for decoding (higher = more accurate, slower)
        vad_filter: Whether to use VAD to filter out non-speech segments
        vad_parameters: Custom VAD parameters
        initial_prompt: Prompt to guide the model's style
        word_timestamps: Whether to include word-level timestamps
        
    Returns:
        dict with keys:
        - text: Transcribed text
        - language: Detected language code
        - segments: List of segments with timing info
        - full_result: Full Whisper result object
    """
    if not os.path.exists(audio_path):
        raise STTLocalError(f"Audio file not found: {audio_path}")
    
    model = get_model()
    
    # Set language
    lang = language or DEFAULT_LANGUAGE
    
    # VAD parameters
    vad_params = vad_parameters or {
        "min_silence_duration_ms": 500,
        "speech_pad_ms": 400
    }
    
    try:
        print(f"[STTLocal] Transcribing: {audio_path}")
        print(f"[STTLocal] Language: {lang}, Task: {task}")
        
        segments, info = model.transcribe(
            audio_path,
            language=lang if lang != "auto" else None,
            task=task,
            beam_size=beam_size,
            vad_filter=vad_filter,
            vad_parameters=vad_params,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps
        )
        
        # Collect all segments
        segments_list = []
        full_text = []
        
        for segment in segments:
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "words": [
                    {
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                        "probability": w.probability
                    } for w in segment.words
                ] if word_timestamps else []
            })
            full_text.append(segment.text)
        
        result = {
            "text": " ".join(full_text).strip(),
            "language": info.language if info.language else lang,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": segments_list,
            "full_result": info
        }
        
        print(f"[STTLocal] Transcription complete!")
        print(f"[STTLocal] Detected language: {result['language']} ({result['language_probability']:.2f})")
        print(f"[STTLocal] Duration: {result['duration']:.2f}s")
        print(f"[STTLocal] Text: {result['text'][:100]}...")
        
        return result
        
    except Exception as e:
        raise STTLocalError(f"Transcription failed: {e}")


def transcribe_audio_streaming(
    audio_path: str,
    language: Optional[str] = None,
    chunk_length: int = 30,
    **kwargs
) -> Generator[dict, None, None]:
    """
    Stream transcription results segment by segment.
    Useful for real-time applications.
    
    Args:
        audio_path: Path to audio file
        language: Language code or "auto"
        chunk_length: Length of audio chunks in seconds
        **kwargs: Additional arguments passed to transcribe
        
    Yields:
        dict for each segment
    """
    model = get_model()
    lang = language or DEFAULT_LANGUAGE
    
    try:
        segments, info = model.transcribe(
            audio_path,
            language=lang if lang != "auto" else None,
            chunk_length=chunk_length,
            **kwargs
        )
        
        for segment in segments:
            yield {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "language": info.language
            }
            
    except Exception as e:
        raise STTLocalError(f"Streaming transcription failed: {e}")


def transcribe_microphone(
    duration: Optional[float] = None,
    language: Optional[str] = None,
    sample_rate: int = 16000,
    device: Optional[int] = None
) -> dict:
    """
    Record from microphone and transcribe.
    
    Args:
        duration: Recording duration in seconds (None = until Ctrl+C)
        language: Language code or "auto"
        sample_rate: Audio sample rate ( Whisper expects 16000)
        device: Microphone device index (None = default)
        
    Returns:
        dict with transcription results
    """
    try:
        import sounddevice as sd
    except ImportError:
        raise STTLocalError("sounddevice not installed. Run: pip install sounddevice")
    
    # Determine device
    if device is None:
        devices = sd.query_devices()
        if devices['max_input_channels'] < 1:
            raise STTLocalError("No microphone found")
    
    print(f"[STTLocal] Recording from microphone (sample_rate={sample_rate})...")
    
    # Record audio
    try:
        audio_data = sd.rec(
            int(duration * sample_rate) if duration else None,
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device
        )
        
        if duration is None:
            print("[STTLocal] Recording... Press Ctrl+C to stop")
            sd.wait()  # Wait until Ctrl+C
        else:
            sd.wait()
            
    except KeyboardInterrupt:
        print("\n[STTLocal] Recording stopped by user")
    
    # Save to temporary file
    try:
        import numpy as np
        import scipy.io.wavfile as wav
        
        # Convert to int16 for Whisper
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            wav.write(f.name, sample_rate, audio_int16)
            temp_path = f.name
        
        # Transcribe
        result = transcribe_audio(temp_path, language=language)
        
        # Cleanup
        os.unlink(temp_path)
        
        return result
        
    except Exception as e:
        raise STTLocalError(f"Mic recording/transcription failed: {e}")


def transcribe_bytes(
    audio_bytes: bytes,
    format: str = "wav",
    language: Optional[str] = None,
    sample_rate: int = 16000
) -> dict:
    """
    Transcribe raw audio bytes.
    
    Args:
        audio_bytes: Raw audio data
        format: Audio format ("wav", "mp3", etc.)
        language: Language code or "auto"
        sample_rate: Audio sample rate
        
    Returns:
        dict with transcription results
    """
    # Save bytes to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format}') as f:
        f.write(audio_bytes)
        temp_path = f.name
    
    try:
        result = transcribe_audio(temp_path, language=language)
        return result
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def get_available_models() -> list:
    """Get list of available Whisper model sizes"""
    return ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]


def get_model_info() -> dict:
    """Get information about the current model configuration"""
    return {
        "model_size": DEFAULT_MODEL_SIZE,
        "language": DEFAULT_LANGUAGE,
        "device": DEFAULT_DEVICE,
        "compute_type": DEFAULT_COMPUTE_TYPE,
        "is_loaded": is_model_loaded(),
        "available_models": get_available_models()
    }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("STTLocal - Faster Whisper Test Mode")
    print("=" * 60)
    print(f"\nCurrent Configuration:")
    for key, value in get_model_info().items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Test model loading")
    print("  2. Transcribe a file")
    print("  3. Record from microphone")
    print("  4. List available models")
    print("  5. Unload model")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("\nLoading model...")
        model = get_model()
        print(f"Model loaded: {model}")
        
    elif choice == "2":
        audio_file = input("Enter audio file path: ").strip()
        if audio_file:
            result = transcribe_audio(audio_file)
            print(f"\nResult:\n{result['text']}")
        else:
            print("No file specified")
            
    elif choice == "3":
        duration = input("Recording duration (seconds, or press Enter for manual stop): ").strip()
        duration = float(duration) if duration else None
        result = transcribe_microphone(duration=duration)
        print(f"\nResult:\n{result['text']}")
        
    elif choice == "4":
        print("\nAvailable models:")
        for model in get_available_models():
            print(f"  - {model}")
            
    elif choice == "5":
        unload_model()
        print("Model unloaded")
        
    else:
        print("Invalid choice")
