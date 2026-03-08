# Engineering Analysis: Leo AI Assistant

## A. Leo’s Current Identity

Leo is a **Hybrid Desktop Commander**. It sits between a traditional **Conversational Agent** (like ChatGPT) and a **System Macro Tool** (like AutoHotKey).

* **Role:** It is primarily an **Operator**. Unlike a passive chatbot that just gives answers, Leo is designed to *act* on the host OS (open apps, control media, manage files).
* **Mode:** It is **Reactive**. It waits for a specific trigger (Hotword "Jarvis/Friday" or GUI input) to execute a command pipeline. It does not predominantly run proactive agents in the background, except for a simple reminder poller.

## B. Real-Life Usage Model

* **Environment:** Strictly **Windows Desktop (Single User)**. The code heavily relies on `pyautogui`, `os.startfile`, and `taskkill`.
* **Interaction:** "Always-On" background daemon with a "Voice-First, GUI-Second" interface. The user is expected to shout commands while doing other work, or type into the overlay window.
* **Data Flow:** local -> Cloud API (Groq/Cohere) -> local. It is **not** offline-capable; it requires a constant internet connection for its "brain" and voice synthesis.

## C. Authority & Safety Boundaries

* **Authority Level:** **High / Unrestricted User**. The assistant runs with the same privileges as the user.
* **Mechanism:** `Backend/Actions/Apps.py` uses `os.system(f"taskkill /f /im {app_name}.exe")` and `os.startfile(app_name)`.
* **Gap:** There are **NO CONFIRMATION GATES**. If the intent classifier (Cohere) mistakenly maps a vague query to "Close Word", Leo will aggressively force-kill `winword.exe` immediately, potentially causing data loss.
* **Explicit Safety:** None found. There is no "whitelist" of safe apps or "blacklist" of critical system processes.

## D. Failure & Recovery Behavior

1. **API Failure (Network/Key):**
    * *Behavior:* **Loud Failure**. `Chatbot.py` catches exceptions and returns "Connection error". The assistant effectively becomes lobotomized (cannot think or speak).
    * *Recovery:* None. It requires a restart or network restoration to work again.
2. **Speech Recognition Failure:**
    * *Behavior:* **Silent Drop**. If `SpeechRecognition` returns `None`, `Main.py` loop likely just continues waiting.
    * *Recovery:* User must repeat the command.
3. **Automation Failure:**
    * *Behavior:* **Log & Continue**. If `OpenApp` fails, it prints an exception to stdout. The user might get no feedback if TTS also fails or if the error isn't propagated to the response bus.

## E. Memory & Persistence (As-Is)

* **Short-Term (Context):** `Backend/StateManager.py` holds volatile state (current app, media status). **Lost on restart.**
* **Long-Term (Logs):** `Data/ChatLog.json` acts as the "Memory". It stores the *entire* conversation history.
* **Issue:** **Unbounded Growth**. The system reloads this JSON on every request to prompt the LLM. Over time, this file will become too large for the context window or disk I/O, causing the assistant to slow down and eventually crash (Context Length Exceeded).

## F. Production-Ready vs Prototype Components

* **Production-Ready:**
  * *None.* (Strictly speaking, no component meets engineering reliability standards for 24/7 deployment).
* **Near-Production:**
  * **Intent Classification (`Model.py`)**: The logic separating "General", "Realtime", and "Command" is sound, though the prompt is fragile.
* **Prototype-Only:**
  * **IPC (Inter-Process Communication):** The file-polling mechanism (`Mic.data`, `Responses.data`) is a "hack" suitable only for demos. It is the root cause of high CPU usage and race conditions.
  * **Subprocess Management:** Processes are spawned without robust lifecycle management/heartbeats.

## G. Single Biggest Risk to Real-Life Use

**Accidental Destructive Action via `taskkill`**.
The combination of specific, powerful commands (`taskkill /f`) and probabilistic AI (LLMs/Cohere) without a "Human-in-the-Loop" confirmation step means Leo is one misunderstanding away from closing unsaved work or killing a critical system process.
