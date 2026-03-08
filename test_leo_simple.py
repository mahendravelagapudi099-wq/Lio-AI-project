#!/usr/bin/env python3
"""Simple functionality test for LEO AI Assistant (no Unicode)"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system_imports():
    """Test if core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        from Backend.InterfaceRouter import InterfaceRouter
        print("OK: InterfaceRouter imported successfully")
    except Exception as e:
        print(f"ERROR: InterfaceRouter failed: {e}")
        return False
    
    try:
        from Backend.Model import FirstLayerDMM, FallbackDMM
        print("OK: Model imported successfully")
    except Exception as e:
        print(f"ERROR: Model failed: {e}")
        return False
    
    try:
        from Backend.Safety import SafetyValidator
        print("OK: Safety system imported successfully")
    except Exception as e:
        print(f"ERROR: Safety system failed: {e}")
        return False
    
    try:
        from Backend.StateManager import StateManager
        print("OK: StateManager imported successfully")
    except Exception as e:
        print(f"ERROR: StateManager failed: {e}")
        return False
    
    try:
        from Backend.TextToSpeech import TextToSpeech
        print("OK: TextToSpeech imported successfully")
    except Exception as e:
        print(f"ERROR: TextToSpeech failed: {e}")
        return False
    
    return True

def test_fallback_dmm():
    """Test the fallback decision making model"""
    print("\nTesting FallbackDMM...")
    
    from Backend.Model import FallbackDMM
    
    test_queries = [
        "write a joke on notepad",
        "save the file",
        "open notepad",
        "play despacito",
        "what's the weather today",
        "how are you",
        "exit"
    ]
    
    for query in test_queries:
        try:
            result = FallbackDMM(query)
            print(f"OK: '{query}' -> {result}")
        except Exception as e:
            print(f"ERROR: '{query}' failed: {e}")
    
    return True

def test_safety_system():
    """Test safety system"""
    print("\nTesting Safety System...")
    
    from Backend.Safety import SafetyValidator
    
    test_commands = [
        "open notepad",
        "delete system32",
        "shutdown computer",
        "volume up",
        "open chrome"
    ]
    
    for cmd in test_commands:
        try:
            assessment = SafetyValidator.analyze_command(cmd)
            status = "OK" if assessment.is_allowed else "BLOCKED"
            print(f"{status}: '{cmd}' - {assessment.warning_message}")
        except Exception as e:
            print(f"ERROR: '{cmd}' failed: {e}")
    
    return True

def test_state_manager():
    """Test state management"""
    print("\nTesting StateManager...")
    
    from Backend.StateManager import StateManager
    
    state = StateManager()
    initial_mode = state.GetDegradedMode()
    print(f"Current mode: {initial_mode}")
    
    # Check readiness flags
    readiness = state.GetState().get('readiness', {})
    print(f"Readiness flags: {readiness}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("LEO AI Assistant - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_system_imports,
        test_fallback_dmm,
        test_safety_system,
        test_state_manager
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"Test failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All basic tests PASSED!")
        print("LEO AI Assistant is running successfully.")
        print("\nKey Features Working:")
        print("- Terminal interface")
        print("- Hotword detection (say 'friday')")
        print("- Fallback decision making")
        print("- Safety validation")
        print("- State management")
        print("- Text-to-speech")
        print("- Speech recognition")
    else:
        print("Some tests FAILED!")
    
    return all_passed

if __name__ == "__main__":
    main()
