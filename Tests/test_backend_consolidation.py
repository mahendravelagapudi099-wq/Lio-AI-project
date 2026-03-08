import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import io

# 1. Mock Hardware/GUI to prevent initialization errors
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['pygame.mixer'] = m
sys.modules['pygame.time'] = m
sys.modules['Frontend.GUI'] = m
sys.modules['Backend.TextToSpeech'] = m

# 2. Import Target (AnswerEngine)
from Backend.AnswerEngine import AnswerEngine

class TestBackendConsolidation(unittest.TestCase):

    def setUp(self):
        # Create engine instance for testing
        self.engine = AnswerEngine()
        # Mock the internal memory manager to track saving without disk I/O
        self.engine.memory = MagicMock()
        self.engine.memory.get_context.return_value = ("", [{"role": "user", "content": "prev context"}])

    @patch('Backend.AnswerEngine.client.chat.completions.create')
    def test_scenario_1_general_query(self, mock_groq):
        """Verify General Query path matches Phase 2 behavior."""
        print("\n[Test] Scenario 1: General Query")
        
        # Setup Mock LLM
        mock_response = "I am operating normally."
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content=mock_response))]
        mock_groq.return_value = [mock_chunk]

        # Execute
        query = "Status report?"
        response = self.engine.generate_response(query, mode="general")

        # Verify Response
        self.assertEqual(response, mock_response)
        
        # Verify Logging (Once)
        self.engine.memory.save_interaction.assert_called_once_with(query, mock_response)
        print("✅ General Query: Response correct, Logged once.")

    @patch('Backend.AnswerEngine.client.chat.completions.create')
    @patch('Backend.AnswerEngine.SearchTools')
    def test_scenario_2_realtime_query(self, mock_search, mock_groq):
        """Verify Realtime Query path injects search results."""
        print("\n[Test] Scenario 2: Realtime Query")

        # Setup Mock Search
        search_results = "Results: Python 3.14 released."
        mock_search.google_search.return_value = search_results

        # Setup Mock LLM
        mock_response = "According to search, Python 3.14 is out."
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content=mock_response))]
        mock_groq.return_value = [mock_chunk]

        # Execute
        query = "Latest python version?"
        response = self.engine.generate_response(query, mode="realtime")

        # Verify Search Logic
        mock_search.google_search.assert_called_once_with(query)
        
        # Verify Context Injection (search results in system prompt)
        call_args = mock_groq.call_args
        messages = call_args.kwargs['messages']
        system_prompts = [m['content'] for m in messages if m['role'] == 'system']
        found_context = any(search_results in s for s in system_prompts)
        self.assertTrue(found_context, "Search results NOT injected into prompt.")

        # Verify Logging
        self.engine.memory.save_interaction.assert_called_once_with(query, mock_response)
        print("✅ Realtime Query: Search called, Context injected, Logged once.")

    @patch('Backend.AnswerEngine.client.chat.completions.create')
    @patch('Backend.AnswerEngine.SearchTools')
    def test_scenario_4_search_failure_handling(self, mock_search, mock_groq):
        """Verify graceful degradation when search fails."""
        print("\n[Test] Scenario 4: Search Failure Handling")

        # Setup Search Failure (Empty results or Exception safety)
        # Case A: Empty results
        mock_search.google_search.return_value = ""

        # Setup Mock LLM (should still answer generically)
        mock_response = "I couldn't find specific news, but I can speculate."
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content=mock_response))]
        mock_groq.return_value = [mock_chunk]

        # Execute
        query = "Obscure topic?"
        response = self.engine.generate_response(query, mode="realtime")

        # Verify Prompt contains failure fallback note
        call_args = mock_groq.call_args
        messages = call_args.kwargs['messages']
        system_prompts = [m['content'] for m in messages if m['role'] == 'system']
        found_fallback = any("No specific search results found" in s for s in system_prompts)
        self.assertTrue(found_fallback, "Fallback prompt NOT injected on search missing.")

        # Verify No Crash & Logging
        self.assertEqual(response, mock_response)
        self.engine.memory.save_interaction.assert_called_once()
        print("✅ Failure Handling: Degraded to generic answer, Logged once.")

    def test_scenario_5_legacy_isolation(self):
        """Verify AnswerEngine does NOT import/use legacy modules."""
        print("\n[Test] Scenario 5: Legacy Isolation")
        
        # Check imports in AnswerEngine module
        import Backend.AnswerEngine
        
        # Use dir() to inspect namespace
        names = dir(Backend.AnswerEngine)
        
        self.assertNotIn("ChatBot", names, "AnswerEngine should NOT import ChatBot")
        self.assertNotIn("RealtimeSearchEngine", names, "AnswerEngine should NOT import RealtimeSearchEngine")
        print("✅ Legacy Isolation: No legacy modules imported in AnswerEngine.")

if __name__ == '__main__':
    unittest.main()
