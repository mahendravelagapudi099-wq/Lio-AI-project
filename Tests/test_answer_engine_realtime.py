import unittest
from unittest.mock import MagicMock, patch
import sys

# MOCK HARDWARE to prevent audio init
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m

from Backend.AnswerEngine import AnswerEngine

class TestAnswerEngineRealtime(unittest.TestCase):
    
    @patch('Backend.AnswerEngine.client.chat.completions.create')
    @patch('Backend.AnswerEngine.SearchTools')
    def test_realtime_query(self, mock_search_tools, mock_groq):
        print("\n[Phase 3 Testing] AnswerEngine (Realtime)")
        
        # 1. Setup Mock Search
        mock_search_tools.google_search.return_value = "Mocked Search Result: The sky is blue."
        
        # 2. Setup Mock Cloud AI
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content="According to search results, the sky is blue."))]
        mock_groq.return_value = [mock_chunk]
        
        # 3. Instantiate
        engine = AnswerEngine()
        
        # 4. Test Generate Response
        query = "What is the color of the sky now?"
        print(f"Sending Query: {query}")
        answer = engine.generate_response(query, mode="realtime")
        print(f"Received Answer: {answer}")
        
        # 5. Verify Search was called
        mock_search_tools.google_search.assert_called_with(query)
        print("✅ SearchTools.google_search() called.")
        
        # 6. Verify Context Injection
        # Check args passed to Groq
        call_args = mock_groq.call_args
        messages = call_args.kwargs['messages']
        
        # The prompt payload should contain search results
        has_search_context = any("Mocked Search Result" in msg['content'] for msg in messages if msg['role'] == "system")
        self.assertTrue(has_search_context, "Search results NOT found in system prompt!")
        print("✅ Search context injected into prompt.")
        
        self.assertIn("blue", answer)

if __name__ == '__main__':
    unittest.main()
