import unittest
import os
import json
import six
from unittest.mock import MagicMock, patch
import sys

# MOCK HARDWARE DEPENDENCIES
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m

from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Memory import MemoryManager

class TestRSEPhase1(unittest.TestCase):
    @patch('Backend.RealtimeSearchEngine.GoogleSearch')
    @patch('Backend.RealtimeSearchEngine.client.chat.completions.create')
    def test_rse_memory_integration(self, mock_groq, mock_google):
        print("\n[Phase 1 Testing] RSE + Memory V1 (Mocked)")
        
        # 1. Setup Mocks
        mock_google.return_value = "Paris is the capital of France."
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content="Paris is the capital."))]
        mock_groq.return_value = [mock_chunk]
        
        # 2. Setup Memory
        memory = MemoryManager()
        # Ensure we start fresh-ish or know the length
        start_len = len(memory.stm)
        
        # 3. Execute RSE
        query = "What is the capital of France?"
        print(f"Sending Query: {query}")
        answer = RealtimeSearchEngine(query, use_cache=False)
        print(f"Received Answer: {answer}")
        
        # 4. Verify Memory Update
        # Check in-memory STM (Note: Length might stay same if full, so check content)
        # self.assertEqual(len(memory.stm), start_len + 2) 
        
        last_exchange = list(memory.stm)[-1]
        self.assertEqual(last_exchange["role"], "assistant")
        self.assertIn("Paris", last_exchange["content"])
        
        print("✅ Memory Integration Verified: RSE successfully wrote to MemoryManager.")

if __name__ == '__main__':
    unittest.main()
