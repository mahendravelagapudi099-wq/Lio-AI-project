import os

# Internal state for terminal mode
_microphone_status = "False"
_assistant_status = "Available..."

def AnswerModifier(Answer):
    """Mirror GUI logic: Cleans/formats the answer."""
    return str(Answer).replace('\n', ' ')

def QueryModifier(Query):
    """Bridge to the Brain's QueryModifier to ensure single ownership and behavioral identity."""
    from Backend.AnswerEngine import QueryModifier as BrainModifier
    return BrainModifier(Query)

def SetMicrophoneStatus(Command):
    global _microphone_status
    _microphone_status = str(Command)
    print(f"[Terminal] Mic Status: {_microphone_status}")

def GetMicrophoneStatus():
    return _microphone_status

def SetAsssistantStatus(Status):
    global _assistant_status
    _assistant_status = str(Status)
    print(f"[Terminal] Leo Status: {_assistant_status}")

def GetAssistantStatus():
    return _assistant_status

def GraphicsDirectoryPath(Filename):
    current_dir = os.getcwd()
    return os.path.join(current_dir, "Frontend", "Graphics", Filename)

def TempDirectoryPath(Filename):
    current_dir = os.getcwd()
    return os.path.join(current_dir, "Frontend", "Files", Filename)

def ShowTextToScreen(Text):
    # In terminal mode, we just print the interaction
    if Text.strip():
        print(f"\n>>> {Text}\n")

def GraphicalUserInterface():
    """
    Mock main loop for Terminal mode. 
    In GUI mode, this blocks. In terminal/daemon mode, we might just wait or do nothing
    if the core loop is handled differently in Main.py.
    """
    import time
    print("[Terminal] Interface initialized. Waiting for Core signals...")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("[Terminal] Shutting down...")
