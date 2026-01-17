import os
import subprocess

def OpenApp(app_name):
    try:
        print(f"[OpenApp] Opening: {app_name}")
        os.startfile(app_name)
    except Exception as e:
        try:
            subprocess.Popen(app_name, shell=True)
        except Exception as e2:
            print(f"[OpenApp] Error opening {app_name}: {e2}")

def CloseApp(app_name):
    try:
        print(f"[CloseApp] Closing: {app_name}")
        os.system(f"taskkill /f /im {app_name}.exe")
    except Exception as e:
        print(f"[CloseApp] Error closing {app_name}: {e}")
