# Mocking side effects BEFORE imports to avoid initialization issues
import sys
from unittest.mock import MagicMock

# Create a mock for pygame before it's imported by other modules
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pygame.time'] = MagicMock()

import os
import unittest
from unittest.mock import patch

# Mock other side-effects
sys.modules['Frontend.GUI'] = MagicMock()
sys.modules['Backend.TextToSpeech'] = MagicMock()

# Add current directory to path
sys.path.append(os.getcwd())

from Backend.FailureHandler import FailureHandler, DegradedMode, FailureTier
from Backend.StateManager import StateManager
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM

class TestFailureModel(unittest.TestCase):
    
    def setUp(self):
        self.state = StateManager()
        self.state.SetDegradedMode(DegradedMode.FULL)
        # Clear mock history
        if os.path.exists(r"Data\ChatLog.json"):
            with open(r"Data\ChatLog.json", "w") as f:
                f.write("[]")

    def test_tier1_cloud_failure_leads_to_limited(self):
        """Simulate a Groq API failure and verify transition to LIMITED mode."""
        with patch('groq.resources.chat.completions.Completions.create') as mock_create:
            mock_create.side_effect = Exception("API Key Expired/Rate Limit (429)")
            
            # This should trigger FailureHandler
            response = ChatBot("Tell me a joke")
            
            self.assertEqual(self.state.GetDegradedMode(), DegradedMode.LIMITED)
            self.assertIn("trouble connecting to my brain", response.lower() if isinstance(response, str) else "")

    def test_tier2_network_failure_leads_to_local(self):
        """Simulate a network timeout and verify transition to LOCAL mode."""
        with patch('groq.resources.chat.completions.Completions.create') as mock_create:
            mock_create.side_effect = Exception("Connection Timeout (socket.timeout)")
            
            # First attempt fails, retries, then triggers FailureHandler
            ChatBot("What is the news today?")
            
            self.assertEqual(self.state.GetDegradedMode(), DegradedMode.LOCAL)

    def test_local_mode_blocks_automation(self):
        """Verify that in LOCAL mode, cloud-dependent ChatBot calls are blocked."""
        self.state.SetDegradedMode(DegradedMode.LOCAL)
        
        # Mock PrivateMemory to return None (not an identity query)
        with patch('Backend.PrivateMemory.PrivateMemory.check_query', return_value=None):
            response = ChatBot("Open YouTube")
            self.assertIn("lost my connection", response.lower())

    def test_chatlog_preservation(self):
        """Verify that failures append to ChatLog instead of clearing it."""
        import json
        with open(r"Data\ChatLog.json", "w") as f:
            json.dump([{"role": "user", "content": "Hello"}], f)
            
        FailureHandler._append_system_note("Test Error Entry")
        
        with open(r"Data\ChatLog.json", "r") as f:
            logs = json.load(f)
            
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["content"], "Hello")
        self.assertIn("Test Error Entry", logs[1]["content"])

    def test_retry_logic(self):
        """Verify that cloud calls retry exactly once."""
        with patch('groq.resources.chat.completions.Completions.create') as mock_create:
            # Create a mock completion object that's serializable
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta.content = "Success"
            
            # First call fails, second succeeds
            mock_create.side_effect = [Exception("Temporary Error"), [mock_chunk]]
            
            # This should NOT trigger FailureHandler because second attempt succeeds
            ChatBot("Retry test")
            
            self.assertEqual(mock_create.call_count, 2)
            self.assertEqual(self.state.GetDegradedMode(), DegradedMode.FULL)

if __name__ == "__main__":
    unittest.main()
