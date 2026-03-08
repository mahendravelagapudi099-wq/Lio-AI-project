"""
Test YouTube voice commands through the main execution pipeline
"""
import time
from Main import MainExecution

def test_voice_commands():
    print("\n" + "="*70)
    print("TESTING YOUTUBE VOICE COMMANDS")
    print("="*70 + "\n")
    
    # Test 1: Play a video
    print("TEST 1: Simulating voice command 'play counting stars'...")
    MainExecution(query="play counting stars")
    print("✓ Test 1 completed\n")
    
    # Wait for video to load
    print("Waiting 8 seconds for video to load...")
    time.sleep(8)
    
    # Test 2: Pause command
    print("\nTEST 2: Simulating voice command 'pause'...")
    MainExecution(query="pause")
    print("✓ Test 2 completed\n")
    
    time.sleep(3)
    
    # Test 3: Resume command
    print("TEST 3: Simulating voice command 'resume'...")
    MainExecution(query="resume")
    print("✓ Test 3 completed\n")
    
    time.sleep(3)
    
    # Test 4: Volume up command
    print("TEST 4: Simulating voice command 'volume up'...")
    MainExecution(query="volume up")
    print("✓ Test 4 completed\n")
    
    time.sleep(2)
    
    # Test 5: Volume down command
    print("TEST 5: Simulating voice command 'volume down'...")
    MainExecution(query="volume down")
    print("✓ Test 5 completed\n")
    
    time.sleep(2)
    
    # Test 6: Next video command
    print("TEST 6: Simulating voice command 'next'...")
    MainExecution(query="next")
    print("✓ Test 6 completed\n")
    
    print("="*70)
    print("ALL VOICE COMMAND TESTS COMPLETED")
    print("="*70)
    print("\nNote: Please manually verify that each command worked correctly.")
    print("You can close the browser manually when done.")

if __name__ == "__main__":
    test_voice_commands()
