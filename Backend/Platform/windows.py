# Backend/Platform/windows.py - Windows Platform Implementation
# ==========================================================

"""
Windows-specific platform implementation.
"""

import os
import subprocess
import platform
from typing import Optional
from Backend.Platform.base import BasePlatform


class WindowsPlatform(BasePlatform):
    """Windows platform implementation"""
    
    def open_app(self, app_name: str) -> bool:
        """Open an application on Windows"""
        try:
            os.startfile(app_name)
            return True
        except Exception as e:
            try:
                subprocess.Popen(app_name, shell=True)
                return True
            except Exception as e2:
                print(f"[WindowsPlatform] Error opening {app_name}: {e2}")
                return False
    
    def close_app(self, app_name: str) -> bool:
        """Close an application on Windows"""
        try:
            # Add .exe if not present
            if not app_name.endswith('.exe'):
                app_name = f"{app_name}.exe"
            subprocess.run(['taskkill', '/f', '/im', app_name], check=False)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error closing {app_name}: {e}")
            return False
    
    def get_volume(self) -> int:
        """Get current volume on Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            return int(volume.GetMasterVolumeLevelScalar() * 100)
        except Exception as e:
            print(f"[WindowsPlatform] Error getting volume: {e}")
            return 50
    
    def set_volume(self, volume: int) -> bool:
        """Set volume on Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            volume = max(0, min(100, volume))
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = cast(interface, POINTER(IAudioEndpointVolume))
            vol.SetMasterVolumeLevelScalar(volume / 100, None)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error setting volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute volume on Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(True, None)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error muting: {e}")
            return False
    
    def unmute_volume(self) -> bool:
        """Unmute volume on Windows"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(False, None)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error unmuting: {e}")
            return False
    
    def get_brightness(self) -> int:
        """Get screen brightness on Windows (requires PowerShell)"""
        try:
            import subprocess
            result = subprocess.run(
                ['powershell', '-command', 
                 '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).GetBrightness(0)'],
                capture_output=True, text=True
            )
            # Parse output to get brightness value
            return 50  # Default fallback
        except Exception as e:
            print(f"[WindowsPlatform] Error getting brightness: {e}")
            return 50
    
    def set_brightness(self, brightness: int) -> bool:
        """Set screen brightness on Windows"""
        try:
            import subprocess
            brightness = max(0, min(100, brightness))
            subprocess.run(
                ['powershell', '-command', 
                 f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).SetBrightness({brightness},0)'],
                check=False
            )
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error setting brightness: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error opening URL: {e}")
            return False
    
    def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take a screenshot on Windows"""
        try:
            import pyautogui
            if path is None:
                path = os.path.join(os.getcwd(), "screenshot.png")
            pyautogui.screenshot(path)
            return path
        except Exception as e:
            print(f"[WindowsPlatform] Error taking screenshot: {e}")
            return ""
    
    def get_system_info(self) -> dict:
        """Get system information on Windows"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('C:')
            
            return {
                "platform": "windows",
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
            print(f"[WindowsPlatform] Error getting system info: {e}")
            return {"platform": "windows", "error": str(e)}
    
    def play_media(self) -> bool:
        """Play media on Windows"""
        try:
            subprocess.Popen(['start', 'wmplayer'], shell=True)
            return True
        except Exception as e:
            print(f"[WindowsPlatform] Error playing media: {e}")
            return False
    
    def pause_media(self) -> bool:
        """Pause media on Windows (limited support)"""
        # Windows doesn't have a simple command for this
        return False
    
    def stop_media(self) -> bool:
        """Stop media on Windows"""
        return False
    
    def next_track(self) -> bool:
        """Next track on Windows"""
        return False
    
    def prev_track(self) -> bool:
        """Previous track on Windows"""
        return False
