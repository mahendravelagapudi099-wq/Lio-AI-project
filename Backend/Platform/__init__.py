# Backend/Platform/__init__.py - Platform Abstraction Factory
# ==========================================================

"""
Platform abstraction layer for cross-platform compatibility.
This module provides a unified interface for platform-specific operations.
"""

import platform
import os

# Detect current platform
CURRENT_PLATFORM = platform.system().lower()  # "windows", "linux", "darwin" (macOS)

# Import the appropriate platform module
if CURRENT_PLATFORM == "windows":
    from Backend.Platform.windows import WindowsPlatform
    Platform = WindowsPlatform()
elif CURRENT_PLATFORM == "linux":
    from Backend.Platform.linux import LinuxPlatform
    Platform = LinuxPlatform()
elif CURRENT_PLATFORM == "darwin":
    from Backend.Platform.macos import MacOSPlatform
    Platform = MacOSPlatform()
else:
    # Default to Windows behavior
    from Backend.Platform.windows import WindowsPlatform
    Platform = WindowsPlatform()
    print(f"[Platform] Unknown platform: {CURRENT_PLATFORM}, defaulting to Windows")


# Export common functions
open_app = Platform.open_app
close_app = Platform.close_app
get_volume = Platform.get_volume
set_volume = Platform.set_volume
mute_volume = Platform.mute_volume
unmute_volume = Platform.unmute_volume
get_brightness = Platform.get_brightness
set_brightness = Platform.set_brightness
open_url = Platform.open_url
take_screenshot = Platform.take_screenshot
get_system_info = Platform.get_system_info
play_media = Platform.play_media
pause_media = Platform.pause_media
stop_media = Platform.stop_media
next_track = Platform.next_track
prev_track = Platform.prev_track


def get_platform_name() -> str:
    """Get the current platform name"""
    return CURRENT_PLATFORM


def is_platform(supported: str) -> bool:
    """Check if current platform matches"""
    return CURRENT_PLATFORM == supported.lower()
