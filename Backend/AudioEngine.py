"""
Backend/AudioEngine.py - Unified Audio Input/Output Engine
============================================================

This module provides a unified audio pipeline for the voice assistant:
1. Audio Input: Microphone capture using sounddevice (low latency)
2. Wake Word Detection: Porcupine for always-listening wake word
3. Voice Activity Detection: Silero VAD for detecting speech
4. Audio Output: Speaker output using pygame/sounddevice

Features:
- Continuous background listening mode
- Wake word triggered recording
- VAD-based speech endpointing (auto-stop when user stops speaking)
- Pre-roll buffer (keeps audio before wake word)
- Barge-in support (stop TTS when wake word detected)
- Cross-platform audio routing

Dependencies:
- sounddevice: Low-latency audio I/O
- pvporcupine: Wake word detection
- silero-vad: Voice Activity Detection
- pygame: Audio playback (fallback)
"""

import os
import threading
import time
import numpy as np
from collections import deque
from typing import Optional, Callable, List
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# Configuration
SAMPLE_RATE = int(env_vars.get("AUDIO_SAMPLE_RATE", "16000"))
CHANNELS = 1
CHUNK_SIZE = int(env_vars.get("AUDIO_CHUNK_SIZE", "512"))  # ~32ms at 16kHz
BUFFER_SIZE = int(env_vars.get("AUDIO_BUFFER_SIZE", "30"))  # 30 seconds buffer
PREROLL_SECONDS = float(env_vars.get("AUDIO_PREROLL", "1.0"))  # Keep 1 second before wake word

# Wake word configuration
DEFAULT_WAKE_WORDS = env_vars.get("WAKE_WORDS", "hey leo,ok leo,friday").split(",")
DEFAULT_WAKE_WORDS = [w.strip().lower() for w in DEFAULT_WAKE_WORDS]

# VAD configuration
VAD_THRESHOLD = float(env_vars.get("VAD_THRESHOLD", "0.5"))
VAD_MIN_SPEECH_MS = int(env_vars.get("VAD_MIN_SPEECH_MS", "250"))
VAD_SILENCE_MS = int(env_vars.get("VAD_SILENCE_MS", "1500"))


class AudioEngineError(Exception):
    """Custom exception for AudioEngine errors"""
    pass


class AudioEngine:
    """
    Unified audio engine for voice assistant.
    Handles microphone input, wake word detection, VAD, and audio output.
    """
    
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        chunk_size: int = CHUNK_SIZE,
        wake_words: List[str] = DEFAULT_WAKE_WORDS,
        on_wake_word: Optional[Callable] = None,
        on_speech_end: Optional[Callable[[np.ndarray], None]] = None,
        on_audio_chunk: Optional[Callable[[np.ndarray], None]] = None
    ):
        """
        Initialize the audio engine.
        
        Args:
            sample_rate: Audio sample rate (16000 recommended for STT)
            channels: Number of audio channels (1 = mono)
            chunk_size: Frames per buffer
            wake_words: List of wake word phrases
            on_wake_word: Callback when wake word detected
            on_speech_end: Callback when speech ends (after VAD)
            on_audio_chunk: Callback for each audio chunk (optional)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.wake_words = wake_words
        
        self.on_wake_word = on_wake_word
        self.on_speech_end = on_speech_end
        self.on_audio_chunk = on_audio_chunk
        
        # State
        self._is_listening = False
        self._is_recording = False
        self._stream = None
        self._porcupine = None
        self._vad_model = None
        self._audio_buffer = deque(maxlen=int(BUFFER_SIZE * sample_rate / chunk_size))
        self._preroll_buffer = deque(maxlen=int(PREROLL_SECONDS * sample_rate / chunk_size))
        self._recorded_audio = []
        self._speech_started = False
        self._lock = threading.Lock()
        
        # Initialize components
        self._init_porcupine()
        self._init_vad()
        
    def _init_porcupine(self):
        """Initialize Porcupine wake word engine"""
        try:
            import pvporcupine
            from pvporcupine import Porcupine
            
            # Get access key from .env
            porcupine_access_key = env_vars.get("PORCUPINE_ACCESS_KEY", "")
            
            if not porcupine_access_key:
                print("[AudioEngine] Warning: PORCUPINE_ACCESS_KEY not set in .env")
                print("[AudioEngine] Wake word detection will use fallback mode")
                self._porcupine = None
                return
            
            # Get keywords (use built-in keywords for simplicity)
            # Built-in keywords: alexa, americana, blueberry, bumblebee, computer, 
            # cortana, elevator, engine, friday, glass, gramophone, grasshopper,
            # hey google, hey siri, jarvis, ok google, picoclock, porcupine,
            # right now, semiconductor, sheila, snowboy, speechwatcher, subwoofer,
            # tarragon, terminator, toaster, tvocabulary, viewfinder, weather
            
            # Map custom wake words to built-in ones
            keyword_paths = []
            for ww in self.wake_words:
                if "leo" in ww:
                    # Custom - we'll handle with a custom model or keyword
                    # For now, use "jarvis" as closest match
                    keyword_paths.append("jarvis")
                elif "friday" in ww:
                    keyword_paths.append("friday")
                elif "ok" in ww:
                    # "ok google" is built-in
                    keyword_paths.append("hey google")
            
            if not keyword_paths:
                keyword_paths = ["friday"]  # Default
                
            print(f"[AudioEngine] Initializing Porcupine with keywords: {keyword_paths}")
            
            self._porcupine = Porcupine(
                access_key=porcupine_access_key,
                keywords=keyword_paths,
                sensitivities=[0.5] * len(keyword_paths)
            )
            
            print(f"[AudioEngine] Porcupine initialized! Frame size: {self._porcupine.frame_length}")
            
        except ImportError:
            print("[AudioEngine] Warning: pvporcupine not installed")
            print("[AudioEngine] Wake word detection will use fallback mode")
            self._porcupine = None
        except Exception as e:
            print(f"[AudioEngine] Porcupine init error: {e}")
            self._porcupine = None
    
    def _init_vad(self):
        """Initialize Silero VAD"""
        try:
            import torch
            from silero_vad import load_silero_vad, VADIterator
            
            print("[AudioEngine] Loading Silero VAD...")
            self._vad_model = load_silero_vad()
            self._vad_iterator = VADIterator(
                self._vad_model,
                threshold=VAD_THRESHOLD,
                min_speech_duration_ms=VAD_MIN_SPEECH_MS,
                min_silence_duration_ms=VAD_SILENCE_MS,
                sample_rate=self.sample_rate
            )
            print("[AudioEngine] Silero VAD loaded!")
            
        except ImportError:
            print("[AudioEngine] Warning: silero-vad not installed")
            print("[AudioEngine] Using simple energy-based VAD fallback")
            self._vad_model = None
        except Exception as e:
            print(f"[AudioEngine] VAD init error: {e}")
            self._vad_model = None
    
    def start_listening(self):
        """Start continuous listening for wake word"""
        if self._is_listening:
            return
            
        try:
            import sounddevice as sd
            
            self._is_listening = True
            
            # Start audio stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype='int16'
            )
            self._stream.start()
            
            print(f"[AudioEngine] Started listening for: {self.wake_words}")
            
        except ImportError:
            raise AudioEngineError("sounddevice not installed. Run: pip install sounddevice")
        except Exception as e:
            raise AudioEngineError(f"Failed to start audio stream: {e}")
    
    def stop_listening(self):
        """Stop continuous listening"""
        self._is_listening = False
        
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            
        print("[AudioEngine] Stopped listening")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Audio input callback - called for each audio chunk"""
        if not self._is_listening:
            return
            
        # Convert to numpy array
        audio_chunk = np.frombuffer(indata, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Store in buffers
        self._audio_buffer.append(audio_chunk)
        self._preroll_buffer.append(audio_chunk)
        
        # Call chunk callback if set
        if self.on_audio_chunk:
            self.on_audio_chunk(audio_chunk)
        
        # Check for wake word
        if self._porcupine and not self._is_recording:
            # Get porcupine frame size
            frame_length = self._porcupine.frame_length
            # Convert chunk to required format
            pcm_data = (audio_chunk * 32768).astype(np.int16).tobytes()
            
            # Pad or trim to match frame_length
            if len(pcm_data) >= frame_length * 2:
                # Take last frame_length * 2 bytes
                pcm_data = pcm_data[-frame_length * 2:]
                
                try:
                    keyword_index = self._porcupine.process(pcm_data)
                    if keyword_index >= 0:
                        self._handle_wake_word()
                except:
                    pass
        
        # Handle recording state
        if self._is_recording:
            self._recorded_audio.append(audio_chunk)
            
            # Check VAD for speech end
            if self._vad_model:
                self._check_vad_speech_end(audio_chunk)
            else:
                # Simple energy-based fallback
                self._check_energy_speech_end(audio_chunk)
    
    def _handle_wake_word(self):
        """Handle wake word detection"""
        print(f"[AudioEngine] Wake word detected!")
        
        # Start recording (include preroll)
        self._is_recording = True
        self._speech_started = True
        self._recorded_audio = list(self._preroll_buffer)  # Include preroll
        
        # Notify callback
        if self.on_wake_word:
            self.on_wake_word()
    
    def _check_vad_speech_end(self, audio_chunk: np.ndarray):
        """Check if speech has ended using Silero VAD"""
        try:
            # Convert to proper format for VAD
            audio_int16 = (audio_chunk * 32768).astype(np.int16)
            
            # Process through VAD
            vad_result = self._vad_iterator(audio_int16, return_seconds=True)
            
            if vad_result and "end" in vad_result:
                # Speech ended
                self._handle_speech_end()
                
        except Exception as e:
            # Fallback to energy-based
            self._check_energy_speech_end(audio_chunk)
    
    def _check_energy_speech_end(self, audio_chunk: np.ndarray):
        """Simple energy-based speech end detection"""
        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio_chunk ** 2))
        
        # If energy is very low for extended time, speech has ended
        if energy < 0.01:  # Threshold
            if not hasattr(self, '_silence_count'):
                self._silence_count = 0
            
            self._silence_count += 1
            
            # ~1 second of silence (30 chunks * 32ms = ~1s)
            if self._silence_count > 30:
                self._handle_speech_end()
                self._silence_count = 0
        else:
            self._silence_count = 0
    
    def _handle_speech_end(self):
        """Handle end of speech"""
        if not self._speech_started:
            return
            
        print("[AudioEngine] Speech ended")
        
        # Combine recorded audio
        if self._recorded_audio:
            full_audio = np.concatenate(self._recorded_audio)
            
            # Notify callback
            if self.on_speech_end:
                self.on_speech_end(full_audio)
        
        # Reset state
        self._is_recording = False
        self._speech_started = False
        self._recorded_audio = []
    
    def get_recorded_audio(self) -> Optional[np.ndarray]:
        """Get the last recorded audio segment"""
        with self._lock:
            if self._recorded_audio:
                return np.concatenate(self._recorded_audio)
        return None
    
    def is_listening(self) -> bool:
        """Check if engine is currently listening"""
        return self._is_listening
    
    def is_recording(self) -> bool:
        """Check if engine is currently recording speech"""
        return self._is_recording
    
    def get_audio_buffer(self) -> np.ndarray:
        """Get recent audio from buffer"""
        return np.concatenate(list(self._audio_buffer))
    
    def get_preroll_buffer(self) -> np.ndarray:
        """Get preroll audio (last ~1 second before wake word)"""
        return np.concatenate(list(self._preroll_buffer))
    
    def interrupt(self):
        """Interrupt current recording (for barge-in)"""
        if self._is_recording:
            print("[AudioEngine] Recording interrupted (barge-in)")
            self._is_recording = False
            self._speech_started = False
            self._recorded_audio = []
    
    def __del__(self):
        """Cleanup"""
        self.stop_listening()
        
        if self._porcupine:
            self._porcupine.delete()


# ============ Output (TTS) Management ============

class AudioOutput:
    """
    Unified audio output manager.
    Handles TTS playback with barge-in support.
    """
    
    def __init__(self):
        self._is_playing = False
        self._stop_event = threading.Event()
        self._current_stream = None
        
    def play_audio(self, audio_data: np.ndarray, sample_rate: int = SAMPLE_RATE):
        """
        Play audio data.
        
        Args:
            audio_data: Audio as numpy array (float32, -1 to 1)
            sample_rate: Sample rate
        """
        try:
            import sounddevice as sd
            
            self._stop_event.clear()
            self._is_playing = True
            
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Play
            self._current_stream = sd.play(audio_int16, sample_rate)
            
            # Wait until done or interrupted
            while sd.get_stream().active and not self._stop_event.is_set():
                time.sleep(0.01)
                
            sd.stop()
            self._is_playing = False
            
        except ImportError:
            # Fallback to pygame
            self._play_with_pygame(audio_data, sample_rate)
    
    def _play_with_pygame(self, audio_data: np.ndarray, sample_rate: int):
        """Fallback playback using pygame"""
        try:
            import pygame as pg
            import numpy as np
            import scipy.io.wavfile as wav
            import tempfile
            
            if not pg.mixer.get_init():
                pg.mixer.init(frequency=sample_rate, size=-16, channels=1)
            
            # Save to temp file
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                wav.write(f.name, sample_rate, audio_int16)
                temp_path = f.name
            
            try:
                pg.mixer.music.load(temp_path)
                pg.mixer.music.play()
                while pg.mixer.music.get_busy() and not self._stop_event.is_set():
                    time.sleep(0.01)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"[AudioOutput] Playback error: {e}")
    
    def stop(self):
        """Stop current playback (for barge-in)"""
        self._stop_event.set()
        try:
            import sounddevice as sd
            sd.stop()
        except:
            pass
        try:
            import pygame as pg
            pg.mixer.music.stop()
        except:
            pass
        self._is_playing = False
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        return self._is_playing


# ============ Utility Functions ============

def test_microphone() -> dict:
    """Test microphone availability"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        return {
            "available": True,
            "default_input": devices['name'],
            "default_input_channels": devices['max_input_channels'],
            "default_sample_rate": devices['default_samplerate']
        }
    except ImportError:
        return {"available": False, "error": "sounddevice not installed"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def test_output() -> dict:
    """Test audio output availability"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        return {
            "available": True,
            "default_output": devices['name'] if devices['max_output_channels'] > 0 else None
        }
    except ImportError:
        return {"available": False, "error": "sounddevice not installed"}
    except Exception as e:
        return {"available": False, "error": str(e)}


def list_audio_devices() -> dict:
    """List all available audio devices"""
    try:
        import sounddevice as sd
        
        inputs = []
        outputs = []
        
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                inputs.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels'],
                    'sample_rate': dev['default_samplerate']
                })
            if dev['max_output_channels'] > 0:
                outputs.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_output_channels'],
                    'sample_rate': dev['default_samplerate']
                })
        
        return {
            "inputs": inputs,
            "outputs": outputs
        }
    except ImportError:
        return {"error": "sounddevice not installed"}


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("AudioEngine - Test Mode")
    print("=" * 60)
    
    # Test audio devices
    print("\nTesting audio devices...")
    mic_info = test_microphone()
    print(f"Microphone: {mic_info}")
    
    output_info = test_output()
    print(f"Speaker: {output_info}")
    
    devices = list_audio_devices()
    if "inputs" in devices:
        print("\nInput devices:")
        for d in devices["inputs"][:5]:
            print(f"  [{d['index']}] {d['name']}")
    
    print("\n" + "=" * 60)
    print("Options:")
    print("  1. Start continuous listening (wake word + VAD)")
    print("  2. List all audio devices")
    print("  3. Test audio playback")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting audio engine...")
        
        def on_wake():
            print(">>> WAKE WORD DETECTED <<<")
        
        def on_speech(audio):
            print(f"Speech captured! Duration: {len(audio) / 16000:.2f}s")
        
        engine = AudioEngine(
            on_wake_word=on_wake,
            on_speech_end=on_speech
        )
        
        engine.start_listening()
        
        print("\nListening for wake words...")
        print("Say one of: hey leo, ok leo, friday")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            engine.stop_listening()
            
    elif choice == "2":
        devices = list_audio_devices()
        print("\nInput devices:")
        for d in devices.get("inputs", []):
            print(f"  [{d['index']}] {d['name']} ({d['channels']}ch)")
        
        print("\nOutput devices:")
        for d in devices.get("outputs", []):
            print(f"  [{d['index']}] {d['name']} ({d['channels']}ch)")
            
    elif choice == "3":
        print("\nGenerating test tone...")
        
        # Generate 1 second of 440Hz tone
        duration = 1.0
        frequency = 440
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        audio = np.sin(2 * np.pi * frequency * t) * 0.5
        
        output = AudioOutput()
        output.play_audio(audio)
        print("Playback complete!")
        
    else:
        print("Invalid choice")
