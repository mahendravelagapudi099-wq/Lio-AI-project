# Failure & Recovery Model: Leo AI Assistant

## A. Failure Categories

| Category | Specific Failures | Root Cause |
| :--- | :--- | :--- |
| **Tier 1: Cloud Dependency** | Groq/Cohere Timeout, API Key Expired, Rate Limited | External API availability or configuration issue. |
| **Tier 2: Network Connectivity** | WiFi Disconnect, High Latency, Packet Loss | Physical environment or ISP issues. |
| **Tier 3: Perception & Input** | Mic Noise, Dead Air, Partial Transcription | Hardware limits or speech-to-text ambiguity. |
| **Tier 4: Execution & OS** | App Not Found, Permission Denied, File Locked | OS-level constraints or state mismatch. |
| **Tier 5: Logical Core** | IPC Deadlock, Thread Crash, Out of Memory | Internal software instability. |

---

## B. Degraded Operation Modes

| Mode | Trigger | Capabilities Left |
| :--- | :--- | :--- |
| **FULL POWER** | All services green. | Full OS automation, Real-time search, LLM personality. |
| **LIMITED SEARCH** | Search API Fail / Network Slow. | General conversation (Chatbot only), OS automation. |
| **LOCAL EMERGENCY** | Cloud LLM Down / No Internet. | **Identity Only:** Responds to "Who are you?" via `PrivateMemory`. Automation blocked. |
| **LOBOTOMIZED** | Speech/IPC Crash. | Silent waiting. Hotword detection might still work to trigger a reboot. |

---

## C. User Feedback Rules

1. **Contextual Errors:** Never use "An error occurred." Use:
    * *Cloud Down:* "I'm having trouble connecting to my brain right now. Please check my API keys."
    * *No Network:* "I've lost my connection to the internet. I can only answer basic identity questions."
2. **Explicit Failure:** If an automation fails (e.g. `taskkill`), say: "I tried to close Chrome, but Windows didn't let me."
3. **Partial Understanding:** If Speech ID is low, say: "I caught that you wanted to open something, but I didn't get the name. Could you repeat that?"

---

## D. Retry & Recovery Strategy

1. **The "Safety Buffer":** NEVER clear `ChatLog.json` on error. Instead, append a system note: `[ERROR: Connection failed, context preserved]`.
2. **Exponential Backoff:** APIs (Groq/Cohere) should retry once after 1s, then fail-fast. No infinite loops.
3. **Process Heartbeat:** If the Image Generation or Automation subprocess crashes, the Main loop should catch the SIGCHILD and restart the thread on the next trigger.
4. **State Rollback:** If a multi-step automation fails (e.g. Move + Rename), Leo must report the failure at the exact step it stopped.

---

## E. Silent vs Spoken Failure Rules

| Situation | Behavior | Rationale |
| :--- | :--- | :--- |
| **Hotword "False Alarm"** | **Silent** | Minimizes user annoyance. |
| **API Failure mid-sentence** | **Spoken** | User is waiting for a response; silence feels like a crash. |
| **Background Task (Reminder)** | **Spoken (Notify)** | Error in background sync should be surfaced if it affects data. |
| **Ambiguous Intent** | **Spoken (Query)** | Asking for clarification is better than executing a wrong command. |

---

## F. Why This Model Improves Trust

Leo currently fails "loud and dumb" (generic messages) or "silent and dangerous" (wiping chat logs). By moving to **Predictable Degradation**, the user always knows *why* Leo is limited. If the internet goes out, Leo doesn't just crash; it acknowledges it and pivots to its local `PrivateMemory`. This prevents the "Black Box" frustration and makes Leo feel like a resilient tool rather than a fragile demo.
