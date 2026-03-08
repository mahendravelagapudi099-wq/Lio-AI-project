import unittest
import os
import json
import shutil
from Backend.Memory import MemoryManager

class TestMemorySystem(unittest.TestCase):
    TEST_DIR = "Test_Data"

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.TEST_DIR, exist_ok=True)
        # Patch paths
        MemoryManager.MEMORY_FILE = os.path.join(cls.TEST_DIR, "Memory.json")
        MemoryManager.LOG_FILE = os.path.join(cls.TEST_DIR, "ChatLog.json")
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.TEST_DIR)

    def setUp(self):
        # Reset files for each test
        if os.path.exists(MemoryManager.MEMORY_FILE):
            os.remove(MemoryManager.MEMORY_FILE)
        if os.path.exists(MemoryManager.LOG_FILE):
            os.remove(MemoryManager.LOG_FILE)
            
    def test_ltm_trigger(self):
        mem = MemoryManager()
        fact = "My name is LeoTestUser"
        mem.save_interaction(fact, "Nice to meet you.")
        
        # Verify LTM written
        with open(MemoryManager.MEMORY_FILE, 'r') as f:
            data = json.load(f)
            self.assertIn(fact, data["user_facts"])
            
    def test_stm_hydration(self):
        # 1. Write some logs
        mem = MemoryManager()
        for i in range(15):
            mem.save_interaction(f"User {i}", f"AI {i}")
            
        # 2. New Instance (Simulate Restart)
        mem2 = MemoryManager()
        
        # Should have last 10 entries
        self.assertEqual(len(mem2.stm), 10)
        self.assertEqual(mem2.stm[-1]["content"], "AI 14")
        
    def test_context_assembly(self):
        mem = MemoryManager()
        
        # Add fact
        mem.save_interaction("I live in TestCity", "Cool.")
        
        # Get context
        enrichment, stm = mem.get_context()
        
        # Check Enrichment
        self.assertIn("I live in TestCity", enrichment)
        
        # Check STM
        self.assertEqual(stm[-1]["content"], "Cool.")

if __name__ == '__main__':
    unittest.main()
