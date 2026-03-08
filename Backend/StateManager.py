# Backend/StateManager.py

class StateManager:
    """
    Singleton class to manage the assistant's global state.
    Tracks active applications, media playback status, and metadata.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.state = {
                "current_app": None,
                "is_playing": False,
                "is_busy": False,
                "media_name": None,
                "degraded_mode": "FULL POWER",
                "readiness": {
                    "cloud": False,
                    "audio": False,
                    "automation": False
                }
            }
        return cls._instance

    def SetState(self, app_name, is_playing, media_name=None):
        """
        Set the current state of the assistant.
        :param app_name: Name of the active application (e.g., "youtube", "spotify")
        :param is_playing: Boolean indicating if media is playing
        :param media_name: Optional name of the media (e.g., song title)
        """
        self.state["current_app"] = app_name
        self.state["is_playing"] = is_playing
        self.state["media_name"] = media_name
        print(f"[StateManager] State Updated: {self.state}")

    def SetReadiness(self, service, is_ready):
        """Update the readiness status of a specific service."""
        if "readiness" in self.state and service in self.state["readiness"]:
            self.state["readiness"][service] = is_ready
            print(f"[StateManager] Readiness: {service} set to {is_ready}")

    def SetDegradedMode(self, mode):
        """Update the assistant's operation mode (FULL, LIMITED, LOCAL, LOBOTOMIZED)"""
        self.state["degraded_mode"] = mode
        print(f"[StateManager] Operation Mode Changed to: {mode}")

    def GetDegradedMode(self):
        """Return the current operation mode."""
        return self.state.get("degraded_mode", "FULL POWER")

    def GetState(self):
        """
        Get the current state dictionary.
        :return: dict
        """
        return self.state

    def ClearState(self):
        """
        Reset the state to default values (preserves mode).
        """
        self.state["current_app"] = None
        self.state["is_playing"] = False
        self.state["media_name"] = None
        print("[StateManager] State Cleared")
