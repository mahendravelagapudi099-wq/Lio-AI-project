"""
Test script for YouTube automation with Brave browser
"""
import time
from Backend.app.youtube import play_youtube, youtube_pause_resume, youtube_volume_up, close_youtube

def test_youtube():
    print("\n" + "="*60)
    print("TESTING YOUTUBE AUTOMATION WITH BRAVE BROWSER")
    print("="*60 + "\n")
    
    # Test 1: Play a video
    print("TEST 1: Playing 'counting stars'...")
    result = play_youtube("counting stars")
    if result:
        print("✓ Test 1 PASSED: Video started successfully\n")
    else:
        print("✗ Test 1 FAILED: Could not start video\n")
        return
    
    # Wait for video to load
    print("Waiting 5 seconds for video to load...")
    time.sleep(5)
    
    # Test 2: Pause/Resume
    print("\nTEST 2: Pausing video...")
    result = youtube_pause_resume()
    if result:
        print("✓ Test 2 PASSED: Video paused\n")
    else:
        print("✗ Test 2 FAILED: Could not pause\n")
    
    time.sleep(2)
    
    # Test 3: Volume up
    print("TEST 3: Increasing volume...")
    result = youtube_volume_up()
    if result:
        print("✓ Test 3 PASSED: Volume increased\n")
    else:
        print("✗ Test 3 FAILED: Could not increase volume\n")
    
    # Wait before closing
    print("\nWaiting 3 seconds before cleanup...")
    time.sleep(3)
    
    # Cleanup
    print("\nCleaning up: Closing YouTube...")
    close_youtube()
    print("✓ Cleanup complete\n")
    
    print("="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_youtube()
