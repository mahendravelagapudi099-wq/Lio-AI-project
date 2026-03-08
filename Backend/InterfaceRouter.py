import os
import importlib

class InterfaceRouter:
    """
    Proxy class that routes interface calls to either the GUI or Terminal implementation.
    Leo defaults to GUI mode unless LEO_MODE environment variable is set.
    """
    _interface = None
    
    # Mode detection: Check environment first, then sys.argv for early startup safety
    _mode = os.environ.get("LEO_MODE", "GUI").upper()
    if _mode == "GUI":
        import sys
        if "--terminal" in sys.argv:
            _mode = "TERMINAL"
        elif "--daemon" in sys.argv:
            _mode = "DAEMON"

    @classmethod
    def _load_interface(cls):
        if cls._interface is not None:
            return cls._interface

        if cls._mode == "GUI":
            # Lazy import to avoid loading PyQt5 unless strictly necessary
            try:
                cls._interface = importlib.import_module("Frontend.GUI")
                print(f"[InterfaceRouter] Routed to GUI implementation.")
            except ImportError as e:
                print(f"[InterfaceRouter] Error loading GUI: {e}. Falling back to TERMINAL.")
                cls._interface = importlib.import_module("Interfaces.Terminal")
        else:
            cls._interface = importlib.import_module("Interfaces.Terminal")
            print(f"[InterfaceRouter] Routed to {cls._mode} implementation.")
        
        return cls._interface

    @classmethod
    def get_interface(cls):
        return cls._load_interface()

# Export common functions explicitly to match the GUI contract
# This ensures 'from Backend.InterfaceRouter import ...' works reliably.

def AnswerModifier(Answer):
    return InterfaceRouter.get_interface().AnswerModifier(Answer)

def QueryModifier(Query):
    return InterfaceRouter.get_interface().QueryModifier(Query)

def SetMicrophoneStatus(Command):
    return InterfaceRouter.get_interface().SetMicrophoneStatus(Command)

def GetMicrophoneStatus():
    return InterfaceRouter.get_interface().GetMicrophoneStatus()

def SetAsssistantStatus(Status):
    return InterfaceRouter.get_interface().SetAsssistantStatus(Status)

def GetAssistantStatus():
    return InterfaceRouter.get_interface().GetAssistantStatus()

def GraphicsDirectoryPath(Filename):
    return InterfaceRouter.get_interface().GraphicsDirectoryPath(Filename)

def TempDirectoryPath(Filename):
    return InterfaceRouter.get_interface().TempDirectoryPath(Filename)

def ShowTextToScreen(Text):
    return InterfaceRouter.get_interface().ShowTextToScreen(Text)

def GraphicalUserInterface():
    return InterfaceRouter.get_interface().GraphicalUserInterface()
