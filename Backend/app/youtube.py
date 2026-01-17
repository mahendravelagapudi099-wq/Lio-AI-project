import time
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from Backend.TextToSpeech import TextToSpeech as speak

# -----------------------------
# GLOBAL DRIVER
# -----------------------------
driver = None

# -----------------------------
# BROWSER CONFIG
# -----------------------------
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# CHANGE USERNAME ONLY
USERNAME = os.getlogin()
BRAVE_PROFILE_PATH = fr"C:\Users\{USERNAME}\AppData\Local\BraveSoftware\Brave-Browser\User Data"
PROFILE_NAME = "Default"

def get_browser_config():
    """Get Brave browser configuration."""
    if os.path.exists(BRAVE_PATH):
        return BRAVE_PATH, BRAVE_PROFILE_PATH, "Brave"
    else:
        print(f"[ERROR] Brave browser not found at: {BRAVE_PATH}")
        return None, None, None

# -----------------------------
# YOUTUBE CONTROLS
# -----------------------------

def play_youtube(query):
    global driver
    if not query or not query.strip():
        speak("Please say the song name")
        return False

    speak(f"Playing {query}")
    print(f"[YouTube] Attempting to play: {query}")

    browser_path, profile_path, browser_name = get_browser_config()
    if not browser_path:
        speak("Brave browser was not found.")
        return False

    print(f"[YouTube] Using {browser_name} at: {browser_path}")
    print(f"[YouTube] Profile path: {profile_path}")

    chrome_options = Options()
    chrome_options.binary_location = browser_path
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_NAME}")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--log-level=3")
    
    # Fix for DevToolsActivePort error
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    try:
        print("[YouTube] Installing/loading ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("[YouTube] Launching browser...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        print(f"[YouTube] Navigating to: {search_url}")
        driver.get(search_url)

        print("[YouTube] Waiting for first video...")
        wait = WebDriverWait(driver, 10)
        first_video = wait.until(EC.element_to_be_clickable((By.ID, "video-title")))
        
        print("[YouTube] Clicking first video...")
        first_video.click()

        # Wait a moment then trigger fullscreen
        print("[YouTube] Waiting 3 seconds before fullscreen...")
        time.sleep(3)
        try:
            print("[YouTube] Attempting fullscreen with 'f' key...")
            driver.find_element(By.TAG_NAME, "body").send_keys("f")
        except:
            print("[YouTube] Fullscreen key failed, trying JS...")
            driver.execute_script("document.querySelector('video').requestFullscreen()")

        print(f"[SUCCESS] Playing on {browser_name}: {query}")
        return True

    except Exception as e:
        print(f"[ERROR] YouTube playback failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        speak("Sorry, I could not play the video.")
        if driver:
            driver.quit()
            driver = None
        return False

def youtube_pause_resume(_=None):
    global driver
    if not driver:
        speak("YouTube is not open.")
        return False
    try:
        # Preferred: Send 'k' key (standard YouTube pause/unpause)
        driver.find_element(By.TAG_NAME, "body").send_keys("k")
        return True
    except:
        try:
            # Fallback: JS
            driver.execute_script("const v = document.querySelector('video'); if(v.paused){v.play();}else{v.pause();}")
            return True
        except Exception as e:
            print(f"[ERROR] Pause/Resume: {e}")
            return False

def youtube_next(_=None):
    global driver
    if not driver:
        speak("YouTube is not open.")
        return False
    try:
        # Standard shortcut: Shift + N
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SHIFT + "n")
        return True
    except:
        try:
            driver.execute_script("document.querySelector('.ytp-next-button').click()")
            return True
        except:
            return False

def youtube_volume_up(_=None):
    global driver
    if not driver: return False
    try:
        # Standard shortcut: Up arrow
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
        return True
    except:
        try:
            driver.execute_script("const v = document.querySelector('video'); v.volume = Math.min(1, v.volume + 0.1);")
            return True
        except: return False

def youtube_volume_down(_=None):
    global driver
    if not driver: return False
    try:
        # Standard shortcut: Down arrow
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        return True
    except:
        try:
            driver.execute_script("const v = document.querySelector('video'); v.volume = Math.max(0, v.volume - 0.1);")
            return True
        except: return False

def youtube_skip_ads(_=None):
    global driver
    if not driver: return False
    try:
        driver.execute_script("""
            const skipButton = document.querySelector('.ytp-ad-skip-button') || document.querySelector('.ytp-skip-ad-button');
            if (skipButton) skipButton.click();
        """)
        return True
    except: return False

def close_youtube(_=None):
    global driver
    if driver:
        speak("Closing YouTube")
        try:
            driver.quit()
        except:
            pass
        driver = None
        return True
    else:
        os.system("taskkill /f /im brave.exe")
        os.system("taskkill /f /im chrome.exe")
        speak("Browser closed.")
        return True

def open_youtube(query=None):
    if query:
        return play_youtube(query)
    
    browser_path, _, browser_name = get_browser_config()
    if not browser_path:
        speak("No browser found.")
        return False
        
    speak(f"Opening YouTube")
    subprocess.Popen([browser_path, "https://www.youtube.com"], shell=False)
    return True

if __name__ == "__main__":
    play_youtube("Lofi hip hop radio")
    time.sleep(10)
    youtube_pause_resume()
    time.sleep(2)
    youtube_volume_up()
    close_youtube()
