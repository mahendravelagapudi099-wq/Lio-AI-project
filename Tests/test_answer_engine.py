import unittest
from unittest.mock import MagicMock, patch
import sys

# MOCK HARDWARE
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m

from Backend.AnswerEngine import AnswerEngine
from Backend.Memory import MemoryManager

class TestAnswerEngine(unittest.TestCase):
    @patch('Backend.AnswerEngine.client.chat.completions.create')
    def test_general_query(self, mock_groq):
        print("\n[Phase 2 Testing] AnswerEngine (General)")
        
        # 1. Setup Mock
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content="I am a test bot."))]
        mock_groq.return_value = [mock_chunk]
        
        # 2. Instantiate Engine
        engine = AnswerEngine()
        
        # 3. Test Generate Response
        query = "What is the color of the sky?"
        print(f"Sending Query: {query}")
        answer = engine.generate_response(query, mode="general")
        print(f"Received Answer: {answer}")
        
        # 4. Verify Content
        self.assertEqual(answer, "I am a test bot.")
        
        # 5. Verify Memory Interaction
        # We need to check if it was written to memory.
        # Since MemoryManager is instantiated inside AnswerEngine, access it via engine.memory
        last_stm = list(engine.memory.stm)[-1]
        self.assertEqual(last_stm["role"], "assistant")
        self.assertIn("test bot", last_stm["content"])
        print("✅ AnswerEngine verified.")

if __name__ == '__main__':
    unittest.main()
