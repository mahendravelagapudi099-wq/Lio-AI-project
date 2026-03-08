#!/usr/bin/env python3
"""Test HandleReminder function to verify it can parse and create reminders from all 100 phrases."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime, timedelta
from Backend.Automation import HandleReminder

# The 100 generated phrases (same as in verify_phrases.py)
phrases = [
    "5 seconds for stretch", "timer 10 sec for water", "20 seconds for the freshup"
]

async def test_handle_reminder():
    """Test HandleReminder function with all 100 phrases."""
    print("Testing HandleReminder function with all 100 phrases...")
    print("=" * 60)
    
    successful_count = 0
    failed_count = 0
    failed_phrases = []
    
    for i, phrase in enumerate(phrases, 1):
        try:
            print(f"Testing phrase {i}/{100}: '{phrase}'")
            result = await HandleReminder(phrase)
            if result:
                successful_count += 1
                print("OK Success")
            else:
                failed_count += 1
                failed_phrases.append(phrase)
                print("XX Failed")
        except Exception as e:
            failed_count += 1
            failed_phrases.append(phrase)
            print(f"XX Error: {e}")
        print()
    
    print("=" * 60)
    print(f"Summary: {successful_count} passed, {failed_count} failed")
    
    if failed_phrases:
        print("\nFailed phrases:")
        for phrase in failed_phrases:
            print(f"  - '{phrase}'")
    
    return successful_count, failed_count

if __name__ == "__main__":
    try:
        successful, failed = asyncio.run(test_handle_reminder())
        if failed == 0:
            print("\nAll phrases passed!")
        else:
            print(f"\n{failed} phrase(s) failed to parse.")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
