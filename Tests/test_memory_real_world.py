import unittest
import os
import json
import shutil
import time
from unittest.mock import MagicMock
import sys

# MOCK HARDWARE DEPENDENCIES FOR HEADLESS TEST
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m
sys.modules['Backend.Hotword'] = m
sys.modules['speech_recognition'] = m

from Backend.Memory import MemoryManager
from Backend.StateManager import StateManager
from Backend.FailureHandler import DegradedMode

class TestMemoryRealWorld(unittest.TestCase):
    TEST_DIR = "Test_Data_RealWorld"

    @classmethod
    def setUpClass(cls):
        # Setup specific test directory to avoid messing with actual data
        os.makedirs(cls.TEST_DIR, exist_ok=True)
        MemoryManager.MEMORY_FILE = os.path.join(cls.TEST_DIR, "Memory.json")
        MemoryManager.LOG_FILE = os.path.join(cls.TEST_DIR, "ChatLog.json")

    @classmethod
    def tearDownClass(cls):
        # Cleanup after tests
        if os.path.exists(cls.TEST_DIR):
            shutil.rmtree(cls.TEST_DIR)

    def setUp(self):
        # Clean state for each test
        if os.path.exists(MemoryManager.MEMORY_FILE):
            os.remove(MemoryManager.MEMORY_FILE)
        if os.path.exists(MemoryManager.LOG_FILE):
            try:
                os.remove(MemoryManager.LOG_FILE)
            except PermissionError:
                pass # Retry or ignore if locked
        
        # Reset State
        state = StateManager()
        state.SetDegradedMode(DegradedMode.FULL)

    def test_1_explicit_memory(self):
        """1. Explicit Memory Test: Recall 'My name is Tharu' after restart."""
        print("\n[Test 1] Explicit Memory Recall")
        
        # Session A
        mem = MemoryManager()
        fact = "My name is Tharu"
        print(f"User says: '{fact}'")
        mem.save_interaction(fact, "Nice to meet you, Tharu.")
        
        # Simulate Restart (New Instance)
        print("Simulating Restart...")
        mem_new = MemoryManager()
        
        # Check Context
        enrichment, _ = mem_new.get_context()
        print(f"Memory Context: {enrichment}")
        
        self.assertIn("Tharu", enrichment, "Failed to recall name after restart")
        self.assertIn("My name is Tharu", enrichment)

    def test_2_noise_filtering(self):
        """2. Noise Filtering Test: Ensure random sentences are NOT saved to LTM."""
        print("\n[Test 2] Noise Filtering")
        
        mem = MemoryManager()
        noise = "The sky is blue today."
        print(f"User says: '{noise}'")
        mem.save_interaction(noise, "Yes, it is.")
        
        # Check LTM (handle missing file safely)
        data = mem._load_ltm()
            
        print(f"LTM Content: {data}")
        self.assertNotIn(noise, data["user_facts"], "Noise was incorrectly saved to LTM")

    def test_3_stm_window(self):
        """3. STM Window Test: Verify only last 10 exchanges are kept."""
        print("\n[Test 3] STM Window (Max 10)")
        
        mem = MemoryManager()
        
        # Feed 15 interactions
        for i in range(1, 16):
            mem.save_interaction(f"Q{i}", f"A{i}")
            
        # Verify STM length
        self.assertEqual(len(mem.stm), 10, f"STM size is {len(mem.stm)}, expected 10")
        
        # Verify Content (Should have Q6 to Q15, or last 10 entries. 
        # Note: STM stores *entries*, so 1 interaction = 2 entries (User+AI).
        # MemoryManager.stm is maxlen=10. So it holds 5 interactions max if purely chat.
        # Let's check the constraint.
        # Code: self.stm = deque(maxlen=self.STM_LIMIT) where STM_LIMIT=10.
        # save_interaction appends 2 items.
        # So it holds 5 turns.
        
        # Check last item
        last_item = mem.stm[-1]
        print(f"Last STM Item: {last_item['content']}")
        self.assertEqual(last_item['content'], "A15")
        
        # Check first item in STM (Should be Q11? 15-5+1 = 11. 
        # Wait, 10 items. Q11, A11, Q12, A12, Q13, A13, Q14, A14, Q15, A15)
        first_item = mem.stm[0]
        print(f"First STM Item: {first_item['content']}")
        self.assertEqual(first_item['content'], "Q11")

    def test_4_restart_hydration(self):
        """4. Restart Test: Ensure STM hydrates correctly from logs."""
        print("\n[Test 4] Restart Hydration")
        
        # Setup Logs
        mem = MemoryManager()
        mem.save_interaction("Pre-Restart Query", "Pre-Restart Answer")
        
        # Restart
        print("Simulating Restart...")
        mem_reloaded = MemoryManager()
        
        # Verify STM
        self.assertTrue(len(mem_reloaded.stm) >= 2)
        self.assertEqual(mem_reloaded.stm[-1]["content"], "Pre-Restart Answer")
        print("STM correctly hydrated from disk.")

    def test_5_failure_interaction(self):
        """5. Failure Interaction: Trigger degraded mode and check memory safety."""
        print("\n[Test 5] Failure Interaction Safety")
        
        # Set Degraded Mode
        state = StateManager()
        state.SetDegradedMode(DegradedMode.LOCAL)
        print("System in LOCAL mode.")
        
        mem = MemoryManager()
        fact = "I live in DefaultCity"
        
        # Even in failure mode, if we save interaction, memory should work
        # (ChatBot handles the logic, but MemoryManager is safe)
        mem.save_interaction(fact, "Local response.")
        
        # Check LTM (Should still extract fact if trigger matches)
        with open(MemoryManager.MEMORY_FILE, 'r') as f:
            data = json.load(f)
            
        self.assertIn(fact, data["user_facts"], "LTM failed during degraded mode")
        print("Memory system remained functional and safe.")

if __name__ == '__main__':
    unittest.main()
