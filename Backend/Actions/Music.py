import os
import platform
import subprocess

def play_music():
    """Play music - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            # Try to play music using Windows Media Player
            subprocess.Popen(['start', 'wmplayer'], shell=True)
            return "Playing music"
        elif platform.system() == 'Darwin':
            # macOS - use iTunes
            subprocess.Popen(['open', '-a', 'iTunes'])
            return "Playing music"
        else:
            # Linux - try to use rhythmbox or similar
            try:
                subprocess.Popen(['rhythmbox', '--play'])
                return "Playing music"
            except FileNotFoundError:
                try:
                    subprocess.Popen(['vlc', '--play-and-exit'])
                    return "Playing music"
                except FileNotFoundError:
                    return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Play error: {e}")
        return "Failed to play music"

def pause_music():
    """Pause music - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            # Windows doesn't have built-in command for this
            return "Pause not available"
        elif platform.system() == 'Darwin':
            # macOS - AppleScript to pause iTunes
            script = 'tell application "iTunes" to pause'
            subprocess.Popen(['osascript', '-e', script])
            return "Music paused"
        else:
            # Linux - try rhythmbox
            try:
                subprocess.Popen(['rhythmbox-client', '--pause'])
                return "Music paused"
            except FileNotFoundError:
                return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Pause error: {e}")
        return "Failed to pause music"

def stop_music():
    """Stop music - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            # Windows media player control
            return "Stop not available"
        elif platform.system() == 'Darwin':
            script = 'tell application "iTunes" to stop'
            subprocess.Popen(['osascript', '-e', script])
            return "Music stopped"
        else:
            try:
                subprocess.Popen(['rhythmbox-client', '--stop'])
                return "Music stopped"
            except FileNotFoundError:
                return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Stop error: {e}")
        return "Failed to stop music"

def next_track():
    """Skip to next track - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            return "Next track not available"
        elif platform.system() == 'Darwin':
            script = 'tell application "iTunes" to next track'
            subprocess.Popen(['osascript', '-e', script])
            return "Next track"
        else:
            try:
                subprocess.Popen(['rhythmbox-client', '--next'])
                return "Next track"
            except FileNotFoundError:
                return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Next track error: {e}")
        return "Failed to skip track"

def previous_track():
    """Go to previous track - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            return "Previous track not available"
        elif platform.system() == 'Darwin':
            script = 'tell application "iTunes" to previous track'
            subprocess.Popen(['osascript', '-e', script])
            return "Previous track"
        else:
            try:
                subprocess.Popen(['rhythmbox-client', '--previous'])
                return "Previous track"
            except FileNotFoundError:
                return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Previous track error: {e}")
        return "Failed to skip track"

def set_volume(volume_level):
    """Set music volume (0-100)."""
    try:
        volume = int(volume_level)
        if not (0 <= volume <= 100):
            return "Volume must be between 0 and 100"
            
        if platform.system() == 'Windows':
            # Use powershell to set volume
            import ctypes
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_obj = cast(interface, POINTER(IAudioEndpointVolume))
            volume_obj.SetMasterVolumeLevelScalar(volume / 100, None)
            return f"Volume set to {volume}%"
            
        elif platform.system() == 'Darwin':
            # macOS - AppleScript to set volume
            script = f'set volume output volume {volume}'
            subprocess.Popen(['osascript', '-e', script])
            return f"Volume set to {volume}%"
            
        else:
            # Linux - use pactl or amixer
            try:
                subprocess.Popen(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'])
                return f"Volume set to {volume}%"
            except FileNotFoundError:
                try:
                    subprocess.Popen(['amixer', 'set', 'Master', f'{volume}%'])
                    return f"Volume set to {volume}%"
                except FileNotFoundError:
                    return "Volume control not available"
                    
    except ValueError:
        return "Invalid volume level"
    except Exception as e:
        print(f"[MusicControl] Volume error: {e}")
        return "Failed to set volume"

def get_current_track():
    """Get current playing track information - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            return "Current track information not available"
        elif platform.system() == 'Darwin':
            # macOS - AppleScript to get track info
            script = '''tell application "iTunes"
                if player state is playing then
                    set track_name to name of current track
                    set artist_name to artist of current track
                    set album_name to album of current track
                    return track_name & " - " & artist_name & " (" & album_name & ")"
                else
                    return "Not playing"
                end if
            end tell'''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return result.stdout.strip()
        else:
            # Linux - rhythmbox client
            try:
                result = subprocess.run(['rhythmbox-client', '--print-playing'], capture_output=True, text=True)
                return result.stdout.strip() if result.stdout.strip() else "Not playing"
            except FileNotFoundError:
                return "No media player found"
    except Exception as e:
        print(f"[MusicControl] Track info error: {e}")
        return "Failed to get track information"

def get_playlist():
    """Get playlist information - platform specific implementation."""
    try:
        if platform.system() == 'Windows':
            return "Playlist information not available"
        elif platform.system() == 'Darwin':
            # macOS - AppleScript to get current playlist
            script = '''tell application "iTunes"
                if exists current playlist then
                    return name of current playlist
                else
                    return "No playlist"
                end if
            end tell'''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return result.stdout.strip()
        else:
            # Linux - rhythmbox client doesn't support this well
            return "Playlist information not available"
    except Exception as e:
        print(f"[MusicControl] Playlist error: {e}")
        return "Failed to get playlist information"

if __name__ == "__main__":
    # Test the music control functions
    print("Testing Music Control...")
    
    print("\n1. Play Music:")
    print(play_music())
    
    print("\n2. Set Volume to 50%:")
    print(set_volume(50))
    
    print("\n3. Current Track:")
    print(get_current_track())
    
    print("\n4. Playlist:")
    print(get_playlist())
