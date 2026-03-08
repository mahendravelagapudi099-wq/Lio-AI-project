# Authority & Safety Contract: Leo AI Assistant

## A. Authority Tier Definitions

| Tier | Name | Definition | Examples |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **SAFE** | Read-only actions, non-disruptive state changes, or creating new isolated data. No risk of data loss. | `OpenApp`, `GoogleSearch`, `ReadFile`, `ListFiles`, `Weather`, `Time`, `PlayMusic` |
| **Tier 2** | **SENSITIVE** | Actions that modify state or consume significant resources but are generally distinct or reversible. | `EditFile` (Launch Editor), `CopyFile`, `CreateFile` (New), `Volume` (Moderate change) |
| **Tier 3** | **CRITICAL** | Irreversible destructive actions, force-stopping processes, or overwriting data. **HIGH RISK.** | `DeleteFile`, `CloseApp` (Taskkill), `MoveFile`, `RenameFile`, `Overwrite File` |

---

## B. Confirmation Rules

| Tier | Policy | Voice Feedback Example |
| :--- | :--- | :--- |
| **Tier 1** | **Execute Immediately** | *Silent execution or succinct "Opening Notepad."* |
| **Tier 2** | **Implicit Confirmation** | "(Repetitive Command) Opening Notepad to **write new file**..." (Slow execution to allow cancel) |
| **Tier 3** | **EXPLICIT CONFIRMATION REQUIRED** | "I am about to **delete** 'report.txt'. **Confirm?**" |

---

## C. Forbidden Actions List

**Leo is STRICTLY FORBIDDEN from executing the following, even with confirmation:**

1. **System Nuking:** `DeleteFile` targeting `C:\Windows\*`, `C:\Program Files\*`, or the Root User Folder (`C:\Users\Name`).
2. **Suicide:** Deleting or modifying its own source code (`Leo\Backend\*`, `Leo\Main.py`) while running.
3. **Critical Process Kill:** Killing `explorer.exe`, `svchost.exe`, `csrss.exe`, `winlogon.exe`.
4. **Blind Shell Execution:** Running raw `cmd` or `powershell` strings passed directly from LLM output without sanitization.

---

## D. Voice-Based Confirmation Flow

*Designed for Tier 3 Actions*

1. **User Trigger:** "Jarvis, delete the backups folder."
2. **Leo Analysis:** Intent = `DeleteFile`. Tier = `CRITICAL`.
3. **Leo Pause state:** Action is **queued**, not executed.
4. **Leo Challenge:** "That action is permanent. Are you sure you want to delete the 'backups' folder?"
5. **User Response:**
    * *Positive:* "Yes", "Confirm", "Do it", "Affirmative". -> **ACTION EXECUTED.**
    * *Negative:* "No", "Cancel", "Stop". -> **ACTION DROPPED.**
    * *Unclear:* "Maybe", "Wait", [Silence > 5s]. -> **ACTION DROPPED.**

---

## E. Failure-Safe Behavior

1. **Unclear Voice Input:** If confidence < 70% or confirmation is ambiguous, **DEFAULT TO CANCEL**.
    * *Leo:* "I didn't catch that. Cancelling delete command."
2. **Timeout:** If user does not respond to a confirmation challenge within **10 seconds**, the action auto-cancels.
3. **App Close Failure:** If `CloseApp` fails (e.g., access denied), Leo **MUST NOT** retry with higher privileges (Admin) automatically. It must report the error.
4. **API Outage:** If Groq/Cohere fails mid-chain, Leo defaults to a "Brain Freeze" state and **DOES NOT** execute the last buffered command.

---

## F. Why This Contract Is Necessary

Currently, Leo uses `os.system("taskkill /f ...")` and `os.remove()`. A single misheard word (e.g., "Delete *all* files" vs "Delete *old* files") or a hallucination by the LLM could wipe the user's hard drive or close unsaved work. This contract moves Leo from a "Demo Toy" to a "Resilient Tool" by adding the necessary friction to dangerous actions.
