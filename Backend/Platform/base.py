# Backend/Platform/base.py - Base Platform Class
# ==============================================

"""
Abstract base class for platform-specific operations.
All platform implementations must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BasePlatform(ABC):
    """Abstract base class for platform implementations"""
    
    @abstractmethod
    def open_app(self, app_name: str) -> bool:
        """Open an application"""
        pass
    
    @abstractmethod
    def close_app(self, app_name: str) -> bool:
        """Close an application"""
        pass
    
    @abstractmethod
    def get_volume(self) -> int:
        """Get current volume (0-100)"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)"""
        pass
    
    @abstractmethod
    def mute_volume(self) -> bool:
        """Mute volume"""
        pass
    
    @abstractmethod
    def unmute_volume(self) -> bool:
        """Unmute volume"""
        pass
    
    @abstractmethod
    def get_brightness(self) -> int:
        """Get screen brightness (0-100)"""
        pass
    
    @abstractmethod
    def set_brightness(self, brightness: int) -> bool:
        """Set screen brightness (0-100)"""
        pass
    
    @abstractmethod
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        pass
    
    @abstractmethod
    def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take a screenshot and return path"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> dict:
        """Get system information"""
        pass
    
    # Media controls
    @abstractmethod
    def play_media(self) -> bool:
        """Play media"""
        pass
    
    @abstractmethod
    def pause_media(self) -> bool:
        """Pause media"""
        pass
    
    @abstractmethod
    def stop_media(self) -> bool:
        """Stop media"""
        pass
    
    @abstractmethod
    def next_track(self) -> bool:
        """Next track"""
        pass
    
    @abstractmethod
    def prev_track(self) -> bool:
        """Previous track"""
        pass
