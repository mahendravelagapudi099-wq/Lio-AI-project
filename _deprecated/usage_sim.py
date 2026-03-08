# Mocking side effects for headless/background testing
import sys
from unittest.mock import MagicMock

sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pygame.time'] = MagicMock()
sys.modules['Frontend.GUI'] = MagicMock()
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtWidgets'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()

import time
import os

# Add local directory to path to import Leo's modules
sys.path.append(os.getcwd())

from Main import MainExecution
from Backend.StateManager import StateManager
from Backend.FailureHandler import DegradedMode

def simulate_command(query, delay=2):
    print(f"\n[UsageSim] Sending command: '{query}'")
    MainExecution(query=query)
    time.sleep(delay)

def main():
    state = StateManager()
    print("Starting mixed usage simulation...")
    
    # 1. Safe commands
    simulate_command("what is the time")
    simulate_command("open notepad")
    
    # 2. Blocked / Mode-specific commands
    # We will simulate a failure later, but first test general automation
    simulate_command("open chrome")
    
    # 3. Wait 5 seconds (simulating idle)
    print("[UsageSim] Idling for 5 seconds...")
    time.sleep(5)
    
    # 4. Scenario: Network Failure injection during usage
    print("\n[UsageSim] Injecting Tier 2 Network Failure...")
    # We can't easily drop real wifi, but we can call handle_failure directly or mock the exception
    from Backend.FailureHandler import FailureHandler
    FailureHandler.handle_failure(Exception("Connection Timeout simulation"), context="Usage Simulator")
    
    # 5. Test behavior in LOCAL mode
    print(f"[UsageSim] Current Mode: {state.GetDegradedMode()}")
    simulate_command("who are you") # Identity - Should work
    simulate_command("what is the news") # Cloud - Should be blocked
    
    # 6. Recovery
    print("\n[UsageSim] Restoring Network (Simulating recovery)...")
    state.SetDegradedMode(DegradedMode.FULL)
    simulate_command("what is the weather in Delhi") # Should work now
    
    print("\n[UsageSim] Simulation complete.")

if __name__ == "__main__":
    main()
