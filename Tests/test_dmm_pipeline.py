import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock hardware dependencies
m = MagicMock()
sys.modules['pygame'] = m
sys.modules['Backend.FailureHandler'] = MagicMock()
sys.modules['Backend.StateManager'] = MagicMock()

# Import Target
from Backend.Model import FirstLayerDMM

class TestDMMPipeline(unittest.TestCase):
    
    @patch('Backend.Model.co')
    def test_safe_shortcuts(self, mock_co):
        print("\n[Test] Pipeline: Shortcuts")
        # Exit should NOT call AI
        res = FirstLayerDMM("exit")
        self.assertEqual(res, ["exit"])
        mock_co.chat.assert_not_called()
        print("Exit shortcut works (No AI).")

        # Volume should NOT call AI
        res = FirstLayerDMM("volume up")
        self.assertEqual(res, ["system volume up"])
        mock_co.chat.assert_not_called()
        print("Volume shortcut works (No AI).")

    @patch('Backend.Model.co')
    def test_ai_routing(self, mock_co):
        print("\n[Test] Pipeline: AI Routing")
        
        # Setup Mock AI Response for a query that won't trigger any shortcuts
        mock_stream = [('text', 'general what is the capital of France')]
        mock_co.chat.return_value = mock_stream
        
        res = FirstLayerDMM("what is the capital of France")
        self.assertTrue(mock_co.chat.called, "AI should be called for general questions!")
        self.assertEqual(res, ["general what is the capital of France"])
        print("General question correctly routed to AI.")

if __name__ == '__main__':
    unittest.main()
