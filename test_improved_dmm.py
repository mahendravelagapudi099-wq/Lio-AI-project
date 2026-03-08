#!/usr/bin/env python3
"""
Test script for improved FirstLayerDMM implementation
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import MagicMock, patch
from Backend.Model import FirstLayerDMM, FallbackDMM

def test_shortcut_commands():
    """Test that shortcut commands are handled correctly"""
    print("Testing shortcut commands:")
    
    # Test exit commands
    for cmd in ["exit", "quit", "bye", "goodbye", "stop"]:
        result = FirstLayerDMM(cmd)
        assert result == ["exit"], f"Expected 'exit' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> exit")
    
    # Test system commands
    for cmd in ["volume up", "mute", "unmute", "brightness"]:
        result = FirstLayerDMM(cmd)
        assert result == [f"system {cmd}"], f"Expected 'system {cmd}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> system {cmd}")
    
    # Test open commands
    for cmd in ["open notepad", "launch chrome", "start firefox"]:
        result = FirstLayerDMM(cmd)
        expected = [cmd.replace("open ", "").replace("launch ", "").replace("start ", "open ")]
        assert result == expected, f"Expected '{expected}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> {expected[0]}")
    
    # Test play commands
    for cmd in ["play despacito", "play music"]:
        result = FirstLayerDMM(cmd)
        expected = [cmd]
        assert result == expected, f"Expected '{expected}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> {expected[0]}")
    
    print("\nAll shortcut commands passed!")

def test_fallback_dmm():
    """Test FallbackDMM implementation"""
    print("\nTesting FallbackDMM:")
    
    # Test content commands
    for cmd in ["save the file", "write a letter", "create a document"]:
        result = FallbackDMM(cmd)
        assert result == [f"content {cmd}"], f"Expected 'content {cmd}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> content {cmd}")
    
    # Test search commands
    for cmd in ["youtube search python tutorial", "google search weather today"]:
        result = FallbackDMM(cmd)
        assert cmd in result[0], f"Expected command containing '{cmd}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> {result[0]}")
    
    # Test weather commands
    for cmd in ["weather today", "forecast for tomorrow"]:
        result = FallbackDMM(cmd)
        assert cmd in result[0], f"Expected command containing '{cmd}' for '{cmd}', got '{result}'"
        print(f"✅ {cmd} -> {result[0]}")
    
    print("\nAll FallbackDMM tests passed!")

def test_cohere_integration():
    """Test Cohere API integration with mocked response"""
    print("\nTesting Cohere integration with mocked response:")
    
    # Mock Cohere API
    mock_response = "content write a report, open chrome"
    
    class MockCohereStream:
        def __init__(self, response):
            self.response = response
            
        def __iter__(self):
            yield ('text', self.response)
    
    with patch('Backend.Model.co') as mock_co:
        mock_co.chat.return_value = MockCohereStream(mock_response)
        
        result = FirstLayerDMM("write a report and open chrome")
        
        # Verify the API was called
        assert mock_co.chat.called, "Cohere API should be called"
        
        # Verify the response was parsed correctly
        assert len(result) == 2, "Should extract 2 commands"
        assert "content write a report" in result, "Should contain content command"
        assert "open chrome" in result, "Should contain open command"
        
        print("✅ Cohere integration test passed!")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing Improved FirstLayerDMM Implementation")
        print("=" * 60)
        
        test_shortcut_commands()
        test_fallback_dmm()
        test_cohere_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! FirstLayerDMM is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
