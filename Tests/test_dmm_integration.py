import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['Backend.FailureHandler'] = MagicMock()
sys.modules['Backend.StateManager'] = MagicMock()

from Backend.Model import FirstLayerDMM

class TestDMMIntegration(unittest.TestCase):

    def mock_cohere_response(self, text_response):
        """Helper to create a mock Cohere stream event"""
        mock_event = MagicMock()
        mock_event.__getitem__ = MagicMock(return_value="text") # for event[0]
        # Simulate format: event[0] == 'text', event[1] == actual text
        # actually Model.py code: 
        # for event in stream: if event[0] == 'text': response = event[1]
        
        # So we return a list of tuples/lists
        return [('text', text_response)]

    @patch('Backend.Model.co')
    def test_1_general_language_safety(self, mock_co):
        print("\n[Test] Scenario 1: General Language Safety")
        # Simulate AI correctly identifying this as GENERAL
        mock_co.chat.return_value = self.mock_cohere_response("general what is the capital of France")
        
        res = FirstLayerDMM("what is the capital of France")
        
        # Verify AI was called (because regex shouldn't catch it)
        self.assertTrue(mock_co.chat.called, "AI should be consulted for general questions")
        # Verify correct routing
        self.assertEqual(res, ["general what is the capital of France"])
        print("'what is the capital of France' -> general (General query correctly identified)")

    @patch('Backend.Model.co')
    def test_2_legitimate_commands(self, mock_co):
        print("\n[Test] Scenario 2: Legitimate Commands")
        # Simulate AI identifying as CONTENT
        mock_co.chat.return_value = self.mock_cohere_response("content save this file")
        
        res = FirstLayerDMM("save this file")
        
        self.assertEqual(res, ["content save this file"])
        print("'save this file' -> content (Correct intent)")

    @patch('Backend.Model.co')
    def test_3_atomic_shortcuts(self, mock_co):
        print("\n[Test] Scenario 3: Atomic Shortcuts")
        
        # Exit
        res = FirstLayerDMM("exit")
        self.assertEqual(res, ["exit"])
        mock_co.chat.assert_not_called()
        print("'exit' -> bypasses AI")

        # System
        res = FirstLayerDMM("volume up")
        self.assertEqual(res, ["system volume up"])
        mock_co.chat.assert_not_called()
        print("'volume up' -> bypasses AI")

    @patch('Backend.Model.co')
    def test_4_offline_fallback(self, mock_co):
        print("\n[Test] Scenario 4: Offline Mode (Fallback)")
        # Simulate Exception
        mock_co.chat.side_effect = Exception("Connection Refused")
        
        # Fallback Logic should catch "open notepad" via regex
        res = FirstLayerDMM("open notepad")
        
        self.assertEqual(res, ["open notepad"])
        print("AI Failure -> FallbackDMM caught 'open notepad'")

    @patch('Backend.Model.co')
    def test_5_safety_validation_prep(self, mock_co):
        print("\n[Test] Scenario 5: Safety Routing Prep")
        # Ensure that DMM output format is compatiable with Main.py's expectations
        # Main.py expects specific keywords to trigger automation.
        
        mock_co.chat.return_value = self.mock_cohere_response("open chrome")
        res = FirstLayerDMM("open chrome")
        
        # Verify format matches Main.py's valid_functions list
        cmd = res[0]
        valid_start = any(cmd.startswith(x) for x in ["open", "close", "play", "system", "content"])
        self.assertTrue(valid_start, f"Command '{cmd}' format must trigger Automation in Main.py")
        print("Command format compatible with Safety Loop")

if __name__ == '__main__':
    unittest.main()
