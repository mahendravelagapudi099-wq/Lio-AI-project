#!/usr/bin/env python3
"""
Basic test script for FirstLayerDMM - focuses on core functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import MagicMock, patch
from Backend.Model import FirstLayerDMM, FallbackDMM

def test_basic_functionality():
    print("Testing FirstLayerDMM basic functionality:")
    
    # Test shortcut commands work
    test_cases = [
        ("exit", ["exit"]),
        ("volume up", ["system volume up"]),
        ("open notepad", ["open notepad"]),
        ("play despacito", ["play despacito"]),
        ("save the file", ["content save the file"]),
        ("write a letter", ["content write a letter"]),
        ("youtube search python tutorial", ["youtube search python tutorial"]),
        ("google search weather", ["google search weather"]),
        ("weather today", ["weather today"]),
        ("forecast tomorrow", ["forecast tomorrow"]),
        ("set a reminder", ["reminder set a reminder"]),
        ("generate image of a cat", ["generate image of a cat"])
    ]
    
    for query, expected in test_cases:
        result = FirstLayerDMM(query)
        assert result == expected, "Query '%s' failed: expected %s, got %s" % (query, expected, result)
        print("OK: %s -> %s" % (query, result))
    
    print("\nAll basic functionality tests passed!")

def test_fallback_functionality():
    print("\nTesting FallbackDMM functionality:")
    
    test_cases = [
        ("save document", ["content save document"]),
        ("create a report", ["content create a report"]),
        ("read file", ["content read file"]),
        ("edit document", ["content edit document"]),
        ("delete file", ["content delete file"]),
        ("copy file", ["content copy file"]),
        ("move file", ["content move file"]),
        ("rename file", ["content rename file"])
    ]
    
    for query, expected in test_cases:
        result = FallbackDMM(query)
        assert result == expected, "Fallback query '%s' failed: expected %s, got %s" % (query, expected, result)
        print("OK: %s -> %s" % (query, result))
    
    print("\nAll FallbackDMM tests passed!")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("Testing FirstLayerDMM Basic Functionality")
        print("=" * 60)
        
        test_basic_functionality()
        test_fallback_functionality()
        
        print("\n" + "=" * 60)
        print("All tests passed! FirstLayerDMM is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print("\nTest failed: %s" % e)
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
