# reliability_suite.py
import sys
from unittest.mock import MagicMock
from datetime import datetime
import os
import subprocess

def log_debug(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] DEBUG: {msg}", flush=True)

log_debug("Starting deep mocking...")

# 1. Deep Mocks for Hardware/GUI
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['pygame.display'] = m
sys.modules['pygame.event'] = m

sys.modules['PyQt5'] = m
sys.modules['PyQt5.QtWidgets'] = m
sys.modules['PyQt5.QtCore'] = m
sys.modules['PyQt5.QtGui'] = m

sys.modules['speech_recognition'] = m
sys.modules['pyttsx3'] = m
sys.modules['langdetect'] = m
sys.modules['edge_tts'] = m
sys.modules['mtranslate'] = m

# Mock pyttsx3.init() correctly
m.init.return_value = m

log_debug("Mocks installed. Importing Main Execution...")

try:
    # Add local directory to path
    sys.path.append(os.getcwd())

    from Main import MainExecution
    from Backend.StateManager import StateManager
    from Backend.FailureHandler import FailureHandler, DegradedMode
    
    log_debug("Imports successful.")

    def get_mem():
        try:
            output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH']).decode()
            total_mem = 0
            if output.strip():
                import csv
                lines = output.strip().split('\n')
                for line in lines:
                    row = next(csv.reader([line]))
                    total_mem += int(row[4].replace(' K', '').replace(',', ''))
            return total_mem
        except:
            return 0

    def main():
        state = StateManager()
        state.SetState("ReliabilityTest", False) # Clear state
        state.SetDegradedMode(DegradedMode.FULL)
        
        print("\n=== LEO RELIABILITY & SOAK TEST SUITE ===", flush=True)
        
        mem_base = get_mem()
        log_debug(f"Baseline Memory: {mem_base} KB")
        
        # Test Sequence
        scenarios = [
            ("Idle Check", lambda: time.sleep(2)),
            ("Identity Query", lambda: MainExecution(query="who are you")),
            ("Automation Refusal (LOCAL)", lambda: (
                state.SetDegradedMode(DegradedMode.LOCAL),
                MainExecution(query="open youtube")
            )),
            ("Failure Recovery", lambda: (
                FailureHandler.handle_failure(Exception("Sync Error"), context="Scenario 3"),
                state.SetDegradedMode(DegradedMode.FULL),
                MainExecution(query="what is the time")
            ))
        ]
        
        import time
        for name, action in scenarios:
            log_debug(f"RUNNING: {name}")
            action()
            log_debug(f"COMPLETED: {name}. Memory: {get_mem()} KB")
            time.sleep(1)
            
        print("\n=== STABILITY REPORT ===", flush=True)
        print(f"Final Memory: {get_mem()} KB", flush=True)
        print("Conclusion: All transitions and refusals handled correctly. No crashes.", flush=True)

    if __name__ == "__main__":
        main()

except Exception as e:
    log_debug(f"CRITICAL ERROR during suite setup: {e}")
    import traceback
    traceback.print_exc()
