# Implementation Plan - IPC Enhancement

# Goal Description

Replace the current file-based IPC (writing/reading `.data` files every 5ms) with **PyQt Signals and Slots**. This will eliminate race conditions, reduce disk I/O to zero, and ensure immediate UI updates.

## User Review Required
>
> [!NOTE]
> **No Visual Changes**: The UI will look exactly the same, but it should feel more responsive and use less CPU.

## Proposed Changes

### Backend

#### [NEW] [Backend/Signals.py](file:///d:/Desktop/leo/Backend/Signals.py)

A Singleton class inheriting from `QObject`.

- **Signals**:
  - `chat_update(str)`: Carries chat text.
  - `status_update(str)`: Carries "Listening...", "Thinking..." status.
  - `mic_status_update(str)`: Carries "True"/"False".

### Frontend

#### [MODIFY] [Frontend/GUI.py](file:///d:/Desktop/leo/Frontend/GUI.py)

Refactor communication logic.

1. **Remove**:
    - `QTimer` polling loops in `ChatSection` and `InitialScreen`.
    - File reading logic (`open(..., 'r')`).
2. **Add**:
    - Imports from `Backend.Signals`.
    - `connect()` calls in `__init__` methods to link signals to UI update constraints.
    - Example: `SignalManager.instance().chat_update.connect(self.addMessage)`
3. **Update Exports**:
    - Modify `ShowTextToScreen`, `SetAssistantStatus`, `SetMicrophoneStatus` (global functions) to `emit` signals instead of writing to files.

## Phase 2 Proposed Changes (Failure & Recovery)

### Backend

#### [MODIFY] [Chatbot.py](file:///d:/Desktop/leo/Backend/Chatbot.py)

- **Logic Fix**: Remove `dump([], f)` in `except` blocks.
- **Recovery**: Append system error messages to logs instead of wiping them.
- **Context**: Ensure `PrivateMemory` fallback is robust if Groq API is blocked or down.

#### [MODIFY] [RealtimeSearchEngine.py](file:///d:/Desktop/leo/Backend/RealtimeSearchEngine.py)

- **Graceful Degrade**: If `GoogleSearch` fails, pivot to `Chatbot` general knowledge automatically with a "Search offline" warning.

#### [MODIFY] [Main.py](file:///d:/Desktop/leo/Main.py)

- **Subprocess Monitoring**: Add basic check to restart `ImageGeneration.py` if the process dies.

---

## Verification Plan

### Manual Verification

1. **Chat Flow**: Speak a command. Verify text appears instantly in the chat window.
2. **Status Updates**: Verify the status label changes from "Listening" -> "Thinking" -> "Answering" via signals.
3. **Mic Icon**: Verify clicking the mic icon updates the internal state and UI via signals.
