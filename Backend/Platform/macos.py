# Backend/Platform/macos.py - macOS Platform Implementation
# ========================================================

"""
macOS-specific platform implementation.
"""

import os
import subprocess
import platform
from typing import Optional
from Backend.Platform.base import BasePlatform


class MacOSPlatform(BasePlatform):
    """macOS platform implementation"""
    
    def open_app(self, app_name: str) -> bool:
        """Open an application on macOS"""
        try:
            subprocess.Popen(['open', '-a', app_name], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error opening {app_name}: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """Close an application on macOS"""
        try:
            subprocess.run(['osascript', '-e', f'quit app "{app_name}"'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error closing {app_name}: {e}")
            return False
    
    def get_volume(self) -> int:
        """Get current volume on macOS"""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'output volume of (get volume settings)'],
                capture_output=True, text=True
            )
            return int(result.stdout.strip())
        except Exception as e:
            print(f"[MacOSPlatform] Error getting volume: {e}")
            return 50
    
    def set_volume(self, volume: int) -> bool:
        """Set volume on macOS"""
        try:
            volume = max(0, min(100, volume))
            subprocess.run(
                ['osascript', '-e', f'set volume output volume {volume}'],
                check=False
            )
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error setting volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute volume on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'set volume with output muted'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error muting: {e}")
            return False
    
    def unmute_volume(self) -> bool:
        """Unmute volume on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'set volume without output muted'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error unmuting: {e}")
            return False
    
    def get_brightness(self) -> int:
        """Get screen brightness on macOS"""
        try:
            result = subprocess.run(
                ['brightness'],
                capture_output=True, text=True
            )
            return int(float(result.stdout.strip()) * 100)
        except Exception as e:
            print(f"[MacOSPlatform] Error getting brightness: {e}")
        return 50
    
    def set_brightness(self, brightness: int) -> bool:
        """Set screen brightness on macOS"""
        try:
            brightness = max(0, min(100, brightness))
            subprocess.run(
                ['brightness', str(brightness / 100)],
                check=False
            )
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error setting brightness: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error opening URL: {e}")
            return False
    
    def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take a screenshot on macOS"""
        try:
            import pyautogui
            if path is None:
                path = os.path.join(os.getcwd(), "screenshot.png")
            pyautogui.screenshot(path)
            return path
        except Exception as e:
            print(f"[MacOSPlatform] Error taking screenshot: {e}")
            return ""
    
    def get_system_info(self) -> dict:
        """Get system information on macOS"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            return {
                "platform": "darwin",
                "os": platform.system(),
                "os_version": platform.mac_ver()[0],
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
            print(f"[MacOSPlatform] Error getting system info: {e}")
            return {"platform": "darwin", "error": str(e)}
    
    def play_media(self) -> bool:
        """Play media on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'tell application "Music" to play'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error playing media: {e}")
            return False
    
    def pause_media(self) -> bool:
        """Pause media on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'tell application "Music" to pause'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error pausing media: {e}")
            return False
    
    def stop_media(self) -> bool:
        """Stop media on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'tell application "Music" to stop'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error stopping media: {e}")
            return False
    
    def next_track(self) -> bool:
        """Next track on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'tell application "Music" to next track'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error next track: {e}")
            return False
    
    def prev_track(self) -> bool:
        """Previous track on macOS"""
        try:
            subprocess.run(['osascript', '-e', 'tell application "Music" to previous track'], check=False)
            return True
        except Exception as e:
            print(f"[MacOSPlatform] Error previous track: {e}")
            return False
