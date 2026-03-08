# Backend/Platform/linux.py - Linux Platform Implementation
# ========================================================

"""
Linux-specific platform implementation.
"""

import os
import subprocess
import platform
from typing import Optional
from Backend.Platform.base import BasePlatform


class LinuxPlatform(BasePlatform):
    """Linux platform implementation"""
    
    def open_app(self, app_name: str) -> bool:
        """Open an application on Linux"""
        try:
            subprocess.Popen([app_name], start_new_session=True)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error opening {app_name}: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """Close an application on Linux"""
        try:
            subprocess.run(['pkill', '-f', app_name], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error closing {app_name}: {e}")
            return False
    
    def get_volume(self) -> int:
        """Get current volume on Linux"""
        try:
            result = subprocess.run(
                ['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
                capture_output=True, text=True
            )
            # Parse output: "Volume: 0-65536: 65536 /100%"
            if '/100%' in result.stdout:
                volume = result.stdout.split('/100%')[0].split()[-1]
                return int(volume)
        except Exception as e:
            print(f"[LinuxPlatform] Error getting volume: {e}")
        return 50
    
    def set_volume(self, volume: int) -> bool:
        """Set volume on Linux"""
        try:
            volume = max(0, min(100, volume))
            subprocess.run(
                ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'],
                check=False
            )
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error setting volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute volume on Linux"""
        try:
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '1'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error muting: {e}")
            return False
    
    def unmute_volume(self) -> bool:
        """Unmute volume on Linux"""
        try:
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error unmuting: {e}")
            return False
    
    def get_brightness(self) -> int:
        """Get screen brightness on Linux"""
        try:
            # Try using xrandr
            result = subprocess.run(
                ['xrandr', '--verbose'],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'Brightness:' in line:
                    brightness = float(line.split(':')[1].strip())
                    return int(brightness * 100)
        except Exception as e:
            print(f"[LinuxPlatform] Error getting brightness: {e}")
        return 50
    
    def set_brightness(self, brightness: int) -> bool:
        """Set screen brightness on Linux"""
        try:
            brightness = max(0, min(100, brightness))
            subprocess.run(
                ['xrandr', '--output', 'DP-1', '--brightness', str(brightness / 100)],
                check=False
            )
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error setting brightness: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error opening URL: {e}")
            return False
    
    def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take a screenshot on Linux"""
        try:
            import pyautogui
            if path is None:
                path = os.path.join(os.getcwd(), "screenshot.png")
            pyautogui.screenshot(path)
            return path
        except Exception as e:
            print(f"[LinuxPlatform] Error taking screenshot: {e}")
            return ""
    
    def get_system_info(self) -> dict:
        """Get system information on Linux"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            return {
                "platform": "linux",
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "cpu_percent": cpu,
                "memory_total": memory.total / (1024**3),  # GB
                "memory_available": memory.available / (1024**3),  # GB
                "memory_percent": memory.percent,
                "disk_total": disk.total / (1024**3),  # GB
                "disk_used": disk.used / (1024**3),  # GB
                "disk_percent": disk.percent
            }
        except Exception as e:
            print(f"[LinuxPlatform] Error getting system info: {e}")
            return {"platform": "linux", "error": str(e)}
    
    def play_media(self) -> bool:
        """Play media on Linux"""
        try:
            subprocess.Popen(['rhythmbox-client', '--play'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error playing media: {e}")
            return False
    
    def pause_media(self) -> bool:
        """Pause media on Linux"""
        try:
            subprocess.Popen(['rhythmbox-client', '--pause'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error pausing media: {e}")
            return False
    
    def stop_media(self) -> bool:
        """Stop media on Linux"""
        try:
            subprocess.Popen(['rhythmbox-client', '--stop'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error stopping media: {e}")
            return False
    
    def next_track(self) -> bool:
        """Next track on Linux"""
        try:
            subprocess.Popen(['rhythmbox-client', '--next'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error next track: {e}")
            return False
    
    def prev_track(self) -> bool:
        """Previous track on Linux"""
        try:
            subprocess.Popen(['rhythmbox-client', '--previous'], check=False)
            return True
        except Exception as e:
            print(f"[LinuxPlatform] Error previous track: {e}")
            return False
