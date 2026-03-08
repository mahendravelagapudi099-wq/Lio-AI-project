# LEO_CONTEXT.md: PROJECT CONSTITUTION

## 1. MISSION & INTENT

Leo AI is an autonomous, terminal-first, daemon-capable assistant designed for high reliability and low resource consumption. The primary goal is a robust backend-centric execution model that preserves legacy GUI accessibility without allowing it to dictate the system's architecture or dependencies.

## 2. CURRENT PHASE & NEXT INTENT

Current State: ARCHITECTURALLY HARDENED.
The system has successfully transitioned to a decoupled interface model using an Interface Router. Phased startup and hardware initialization are implemented.
Next Intent: Continuous stability and extension of terminal-first capabilities while maintaining GUI-dormancy compatibility.

## 3. ARCHITECTURAL STATE (FROZEN VS LIVING)

### FROZEN LAYER (READ-ONLY)

- **Frontend/ (GUI Implementation)**: Must not be refactored, restyled, or modified. Any bug fixes in this layer must be minimal and strictly necessary for backward compatibility.
- **Decision Logic Core**: The regex-based routing and command categorization in Main.py are partially frozen to prevent logical regressions.

### LIVING LAYER (ACTIVE)

- **Backend/ (Core Logic & Engines)**: Active area for enhancement.
- **Interfaces/ (Terminal & Future Interfaces)**: Primary development area for user interaction.
- **Main.py Lifecycle**: Entry point logic, daemon management, and signal handling.

## 4. INTERFACE CONTRACT (PROXY PATTERN)

All core-to-interface communication MUST pass through `Backend.InterfaceRouter`.

### Mandatory Contract Functions

- `ShowTextToScreen(Text)`
- `SetAsssistantStatus(Status)`
- `SetMicrophoneStatus(Command)`
- `GetMicrophoneStatus()`
- `GetAssistantStatus()`
- `AnswerModifier(Answer)`
- `QueryModifier(Query)`
- `GraphicalUserInterface()`

## 5. DAEMON LIFECYCLE & SAFETY GATES

- **PID Control**: `leo.pid` in root directory enforces single-instance execution.
- **Log Security**: In daemon mode, all output is redirected to `Data/leo.log`.
- **Audio Safety**: Microphone and TTS hardware MUST be disabled in daemon mode by default. Initialization is controlled by the `AUTO_VOICE_DAEMON` toggle in `.env`.

## 6. RECENT ARCHITECTURAL HARDENING

- Implementation of `InterfaceRouter.py` for lazy loading of PyQt5.
- Introduction of `Terminal.py` as the default headless interface.
- Migration from global GUI imports to scoped, routed imports in `Main.py`.
- Formalization of PID-locking using `psutil`.

## 7. DECISION HISTORY (RATIONALE)

- **GUI Freeze**: Decided to freeze the GUI to prevent PyQt5 dependencies from bloating the "Hardened" backend-first design.
- **Proxy Pattern**: Chosen to allow the Core to remain interface-agnostic while supporting multiple frontends.
- **Signal Handling**: Implemented standard SIGINT/SIGTERM handlers to ensure `.pid` cleanup on Windows/Linux environments.

## 8. RULES OF ENGAGEMENT (STRICT)

- **Rule 1**: AI must never remove or refactor existing code in the `Frontend/` directory.
- **Rule 2**: All new UI-facing functionality must be implemented in the `Interfaces/` layer and exposed via the `InterfaceRouter`.
- **Rule 3**: `Main.py` global scope must be kept minimal; imports should be placed in local scopes where possible to ensure mode-based isolation.
- **Rule 4**: Any change affecting startup MUST be verified in `--terminal` and `--daemon` modes.

## 9. FORBIDDEN MODIFICATIONS

- DO NOT convert the system back to a GUI-first import model.
- DO NOT add heavy UI dependencies to the root `Requirements.txt` that are not PyQt5-related.
- DO NOT bypass the `InterfaceRouter` for any screen or status output.
- DO NOT remove the `leo.pid` safety check.

## 10. REGRESSION CHECKLIST

- [ ] Does `python Main.py --terminal` produce console output?
- [ ] Is `leo.pid` created in root and cleaned up on exit?
- [ ] Does the GUI still launch when `--terminal` is omitted?
- [ ] Are logs correctly appending to `Data/leo.log` in daemon mode?
- [ ] Do `SetAsssistantStatus` and `ShowTextToScreen` work across all modes?
