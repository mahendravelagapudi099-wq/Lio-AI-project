from pycaw.pycaw import AudioUtilities


try:
    # Simpler initialization using pycaw wrapper
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume
except Exception as e:
    print(f"Error initializing volume control: {e}")
    volume = None

def volume_up():
    if volume:
        try:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(current + 0.05, 1.0), None)
        except Exception as e:
            print(f"Error increasing volume: {e}")

def volume_down():
    if volume:
        try:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(current - 0.05, 0.0), None)
        except Exception as e:
            print(f"Error decreasing volume: {e}")
