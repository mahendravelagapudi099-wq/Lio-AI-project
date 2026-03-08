# Backend/FailureHandler.py

import os
import json
import datetime
from Backend.StateManager import StateManager
from Backend.TextToSpeech import TextToSpeech
from Backend.InterfaceRouter import ShowTextToScreen

class DegradedMode:
    FULL = "FULL POWER"
    LIMITED = "LIMITED SEARCH"
    LOCAL = "LOCAL EMERGENCY"
    LOBOTOMIZED = "LOBOTOMIZED"

class FailureTier:
    T1_CLOUD = "Tier 1: Cloud Dependency"
    T2_NETWORK = "Tier 2: Network Connectivity"
    T3_PERCEPTION = "Tier 3: Perception & Input"
    T4_EXECUTION = "Tier 4: Execution & OS"
    T5_LOGICAL = "Tier 5: Logical Core"

class FailureHandler:
    """
    Centralized Failure & Recovery Model Implementation.
    Maps exceptions to tiers and manages state transitions.
    """
    
    @staticmethod
    def classify_exception(e):
        """Classify common exceptions into defined failure tiers."""
        e_str = str(e).lower()
        
        # Tier 1: Cloud Dependency
        if any(kw in e_str for kw in ["api_key", "rate_limit", "authentication", "quota", "groq", "cohere", "401", "429"]):
            return FailureTier.T1_CLOUD
            
        # Tier 2: Network Connectivity
        if any(kw in e_str for kw in ["connection", "timeout", "unreachable", "wifi", "dns", "http", "socket"]):
            return FailureTier.T2_NETWORK
            
        # Tier 4: Execution & OS
        if any(kw in e_str for kw in ["not found", "permission", "access denied", "oserror", "filelocked"]):
            return FailureTier.T4_EXECUTION
            
        # Default to Logical Core for internal crashes
        return FailureTier.T5_LOGICAL

    @staticmethod
    def handle_failure(exception, tier=None, context=""):
        """Handle failure by updating state, logging, and providing user feedback."""
        state = StateManager()
        if not tier:
            tier = FailureHandler.classify_exception(exception)
            
        error_msg = f"[{tier}] {context}: {str(exception)}"
        print(f"[FailureHandler] {error_msg}")
        
        # 1. Update Mode based on Tier
        if tier == FailureTier.T1_CLOUD:
            state.SetDegradedMode(DegradedMode.LIMITED)
            FailureHandler._provide_feedback("Cloud Down")
        elif tier == FailureTier.T2_NETWORK:
            state.SetDegradedMode(DegradedMode.LOCAL)
            FailureHandler._provide_feedback("No Network")
        elif tier == FailureTier.T5_LOGICAL:
            state.SetDegradedMode(DegradedMode.LOBOTOMIZED)
            # Silent failure as per LOBOTOMIZED rule
        elif tier == FailureTier.T4_EXECUTION:
            # Remain in current mode but report specific error
            FailureHandler._provide_feedback("Execution Error", context)

        # 2. Safety Buffer: Preserve ChatLog
        FailureHandler._append_system_note(f"ERROR: {tier} - {context}")

    @staticmethod
    def _provide_feedback(error_type, detail=""):
        """Provide contextual user feedback as per rules."""
        messages = {
            "Cloud Down": "I'm having trouble connecting to my brain right now. Please check my API keys or my internet.",
            "No Network": "I've lost my connection to the internet. I can only answer basic identity questions.",
            "Execution Error": f"I tried to perform that task, but Windows had an issue: {detail}.",
            "Partial Understanding": "I caught that you wanted to do something, but I didn't get all the details. Could you repeat that?"
        }
        
        feedback = messages.get(error_type, "I encountered an unexpected issue.")
        ShowTextToScreen(f"System: {feedback}")
        # Only speak if not in LOBOTOMIZED mode
        if StateManager().GetDegradedMode() != DegradedMode.LOBOTOMIZED:
            TextToSpeech(feedback)

    @staticmethod
    def _append_system_note(note):
        """Append a system note to ChatLog.json instead of clearing it."""
        try:
            log_path = r"Data\ChatLog.json"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
                
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logs.append({"role": "system", "content": f"[{timestamp}] {note}"})
            
            with open(log_path, "w", encoding='utf-8') as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"[FailureHandler] Critical Error preserving ChatLog: {e}")

    @staticmethod
    def check_mode_allows_action(action_type):
        """Return True if the current mode allows the specific action."""
        mode = StateManager().GetDegradedMode()
        
        if mode == DegradedMode.FULL:
            return True
            
        if mode == DegradedMode.LIMITED:
            # Block Real-time search, allow local automation and identity
            return action_type not in ["realtime"]
            
        if mode == DegradedMode.LOCAL:
            # Block everything except local identity (PrivateMemory)
            return action_type == "identity"
            
        if mode == DegradedMode.LOBOTOMIZED:
            return False
            
        return True
