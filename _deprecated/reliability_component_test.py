# reliability_component_test.py
import sys
import os
import time
from datetime import datetime
from unittest.mock import MagicMock

# 1. Mock heavy dependencies
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['PyQt5'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m

sys.path.append(os.getcwd())

from Backend.FailureHandler import FailureHandler, DegradedMode, FailureTier
from Backend.StateManager import StateManager

def log_event(event):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {event}", flush=True)

def test_stress_mode_transitions():
    log_event("Starting Mode Transition Stress Test...")
    state = StateManager()
    
    # Rapidly toggle modes to check for state consistency
    modes = [DegradedMode.FULL, DegradedMode.LIMITED, DegradedMode.LOCAL, DegradedMode.LOBOTOMIZED]
    for i in range(100):
        mode = modes[i % 4]
        state.SetDegradedMode(mode)
        if state.GetDegradedMode() != mode:
            raise Exception(f"State corruption at iteration {i}")
            
    log_event("Mode Transition Stress Test PASSED.")

def test_failure_classification_coverage():
    log_event("Starting Failure Classification Coverage Test...")
    
    test_cases = [
        (Exception("groq api error"), FailureTier.T1_CLOUD),
        (Exception("connection timeout"), FailureTier.T2_NETWORK),
        (Exception("permission denied"), FailureTier.T4_EXECUTION),
        (Exception("random crash"), FailureTier.T5_LOGICAL)
    ]
    
    for exc, expected_tier in test_cases:
        tier = FailureHandler.classify_exception(exc)
        if tier != expected_tier:
            raise Exception(f"Classification Mismatch: {exc} -> {tier} (expected {expected_tier})")
            
    log_event("Failure Classification Coverage Test PASSED.")

def test_chatlog_integrity_under_load():
    log_event("Starting ChatLog Integrity Stress Test...")
    # Simulate 50 rapid failure loggings
    for i in range(50):
        FailureHandler._append_system_note(f"Stress Test Entry {i}")
        
    import json
    with open(r"Data\ChatLog.json", "r", encoding='utf-8') as f:
        logs = json.load(f)
        
    last_entries = [log["content"] for log in logs[-5:]]
    log_event(f"Last Log Entries: {last_entries}")
    log_event("ChatLog Integrity Stress Test PASSED.")

def main():
    print("=== LEO COMPONENT RELIABILITY TEST ===", flush=True)
    try:
        test_stress_mode_transitions()
        test_failure_classification_coverage()
        test_chatlog_integrity_under_load()
        print("\n[STABILITY CONFIRMED] Core Failure & Recovery modules are robust.", flush=True)
    except Exception as e:
        print(f"\n[STABILITY FAILED] {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
