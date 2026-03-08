#!/usr/bin/env python3
"""
Simple test script for improved FirstLayerDMM implementation (without Unicode characters)
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
        assert result == ["exit"], "Expected 'exit' for '%s', got '%s'" % (cmd, result)
        print("OK: %s -> exit" % cmd)
    
    # Test system commands
    for cmd in ["volume up", "mute", "unmute", "brightness"]:
        result = FirstLayerDMM(cmd)
        assert result == ["system %s" % cmd], "Expected 'system %s' for '%s', got '%s'" % (cmd, cmd, result)
        print("OK: %s -> system %s" % (cmd, cmd))
    
    # Test open commands
    for cmd in ["open notepad", "launch chrome", "start firefox"]:
        result = FirstLayerDMM(cmd)
        if cmd.startswith("open "):
            expected = cmd
        elif cmd.startswith("launch "):
            expected = "open " + cmd.replace("launch ", "")
        elif cmd.startswith("start "):
            expected = "open " + cmd.replace("start ", "")
        assert result == [expected], "Expected '%s' for '%s', got '%s'" % (expected, cmd, result)
        print("OK: %s -> %s" % (cmd, expected))
    
    # Test play commands
    for cmd in ["play despacito", "play music"]:
        result = FirstLayerDMM(cmd)
        expected = cmd
        assert result == [expected], "Expected '%s' for '%s', got '%s'" % (expected, cmd, result)
        print("OK: %s -> %s" % (cmd, expected))
    
    print("\nAll shortcut commands passed!")

def test_fallback_dmm():
    """Test FallbackDMM implementation"""
    print("\nTesting FallbackDMM:")
    
    # Test content commands
    for cmd in ["save the file", "write a letter", "create a document"]:
        result = FallbackDMM(cmd)
        assert result == ["content %s" % cmd], "Expected 'content %s' for '%s', got '%s'" % (cmd, cmd, result)
        print("OK: %s -> content %s" % (cmd, cmd))
    
    # Test search commands
    for cmd in ["youtube search python tutorial", "google search weather today"]:
        result = FallbackDMM(cmd)
        assert cmd in result[0], "Expected command containing '%s' for '%s', got '%s'" % (cmd, cmd, result)
        print("OK: %s -> %s" % (cmd, result[0]))
    
    # Test weather commands
    for cmd in ["weather today", "forecast for tomorrow"]:
        result = FallbackDMM(cmd)
        assert cmd in result[0], "Expected command containing '%s' for '%s', got '%s'" % (cmd, cmd, result)
        print("OK: %s -> %s" % (cmd, result[0]))
    
    print("\nAll FallbackDMM tests passed!")

def test_cohere_integration():
    """Test Cohere API integration with mocked response"""
    print("\nTesting Cohere integration with mocked response:")
    
    # Mock Cohere API
    mock_response = "content write a detailed report about AI, google search latest AI news"
    
    class MockCohereStream:
        def __init__(self, response):
            self.response = response
            
        def __iter__(self):
            yield ('text', self.response)
    
    with patch('Backend.Model.co') as mock_co:
        mock_co.chat.return_value = MockCohereStream(mock_response)
        
        result = FirstLayerDMM("write a detailed report about AI and search for latest AI news")
        
        # Verify the API was called
        assert mock_co.chat.called, "Cohere API should be called"
        
        # Verify the response was parsed correctly
        assert len(result) == 2, "Should extract 2 commands"
        assert "content write a detailed report about AI" in result, "Should contain content command"
        assert "google search latest AI news" in result, "Should contain google search command"
        
        print("OK: Cohere integration test passed!")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing Improved FirstLayerDMM Implementation")
        print("=" * 60)
        
        test_shortcut_commands()
        test_fallback_dmm()
        test_cohere_integration()
        
        print("\n" + "=" * 60)
        print("All tests passed! FirstLayerDMM is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print("\nTest failed: %s" % e)
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
