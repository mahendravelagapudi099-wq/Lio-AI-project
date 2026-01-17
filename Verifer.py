import asyncio
import os
import time
from Backend.Automation import Automation
from Backend.app.weather import GetWeather

async def test_all():
    print("\n" + "="*70)
    print("STARTING ALL FUNCTIONS TEST")
    print("="*70 + "\n")

    # 1. Test App Opening
    print("[TEST 1] Opening Notepad...")
    await Automation(["open notepad"])
    time.sleep(2)

    # 2. Test Content Creation (Notepad AI)
    print("[TEST 2] Writing a joke to Notepad...")
    await Automation(["content write a funny joke about robots"])
    time.sleep(3)

    # 3. Test Weather
    print("[TEST 3] Checking Weather...")
    try:
        weather = GetWeather("Delhi")
        print(f"Weather Result: {weather}")
    except Exception as e:
        print(f"Weather Error: {e}")

    # 4. Test YouTube Playback
    print("[TEST 4] Playing Music on YouTube...")
    await Automation(["play Lofi hip hop"])
    time.sleep(10) # Wait for it to play

    # 5. Test YouTube Controls (Volume/Pause)
    print("[TEST 5] Testing Volume and Pause...")
    await Automation(["volume down"])
    time.sleep(2)
    await Automation(["pause"])
    time.sleep(2)
    await Automation(["play"]) # Test resume
    time.sleep(2)

    # 6. Test File Operations
    print("[TEST 6] Testing File Creation...")
    test_file = "test_verification.txt"
    await Automation([f"create file {test_file}|Verification Content"])
    if os.path.exists(test_file):
        print(f"✅ File {test_file} created successfully.")
        await Automation([f"delete file {test_file}"])
        print(f"✅ File {test_file} cleaned up.")
    else:
        print(f"❌ File creation failed.")

    # 7. Test Closing
    print("[TEST 7] Closing Apps...")
    await Automation(["close notepad"])
    # await Automation(["close youtube"]) # Closing youtube driver might be handled by yt_driver.quit()

    print("\n" + "="*70)
    print("TESTS COMPLETED")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all())
