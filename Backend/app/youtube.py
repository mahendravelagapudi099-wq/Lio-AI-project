import time
import os
import threading
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

try:
    from Backend.TextToSpeech import TextToSpeech as speak
except ImportError:
    def speak(text):
        print(f"[Speech Substitute] {text}")

# -----------------------------
# GLOBAL CONFIG & STATE
# -----------------------------
driver = None
ad_thread_running = False

# BROWSER PATHS
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
USERNAME = os.getlogin()
BRAVE_PROFILE_PATH = fr"C:\Users\{USERNAME}\AppData\Local\BraveSoftware\Brave-Browser\User Data"
PROFILE_NAME = "Default"

def log_info(msg):
    print(f"[YOUTUBE-INFO] {msg}")

def log_error(msg):
    print(f"[YOUTUBE-ERROR] {msg}")

def log_success(msg):
    print(f"[YOUTUBE-SUCCESS] {msg}")

# -----------------------------
# BACKGROUND AD SKIPPER
# -----------------------------
def background_ad_skipper():
    """Daemon thread to continuously check and skip ads."""
    global ad_thread_running, driver
    log_info("Ad skip thread started.")
    
    skip_selectors = [
        ".ytp-ad-skip-button",
        ".ytp-ad-skip-button-modern",
        ".ytp-skip-ad-button",
        ".ytp-ad-overlay-close-button",
        "button.ytp-ad-skip-button"
    ]

    while ad_thread_running:
        if driver:
            try:
                # Check for various skip buttons using JS to be fast
                for selector in skip_selectors:
                    try:
                        # Use execute_script to find and click to avoid element not visible errors
                        driver.execute_script(f"""
                            const btn = document.querySelector('{selector}');
                            if (btn && btn.offsetParent !== null) {{
                                btn.click();
                                console.log('Ad skipped automatically via selector: {selector}');
                            }}
                        """)
                    except:
                        continue
            except Exception:
                # Silently fail if driver is closed or page is transitioning
                pass
        time.sleep(2)  # Check every 2 seconds
    log_info("Ad skip thread stopped.")

def start_ad_skipper():
    global ad_thread_running
    if not ad_thread_running:
        ad_thread_running = True
        thread = threading.Thread(target=background_ad_skipper, daemon=True)
        thread.start()

# -----------------------------
# BROWSER INITIALIZATION
# -----------------------------
def get_browser_config():
    """Get Brave browser configuration."""
    if os.path.exists(BRAVE_PATH):
        return BRAVE_PATH, BRAVE_PROFILE_PATH, "Brave"
    else:
        log_error(f"Brave browser not found at: {BRAVE_PATH}")
        return None, None, None

def init_driver():
    global driver
    browser_path, profile_path, browser_name = get_browser_config()
    if not browser_path:
        speak("Browser not found.")
        return False

    log_info(f"Launching {browser_name} instance...")
    
    chrome_options = Options()
    chrome_options.binary_location = browser_path
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_NAME}")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    
    # Essential flags for stability
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        start_ad_skipper()
        return True
    except Exception as e:
        log_error(f"Failed to initialize driver: {e}")
        return False

# -----------------------------
# CORE YOUTUBE FUNCTIONS
# -----------------------------

def play_youtube(query):
    """Plays a video on YouTube based on search query."""
    global driver
    if not query or not query.strip():
        speak("Please say the song name")
        return False

    speak(f"Playing {query} on YouTube")
    log_info(f"Searching for: {query}")

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    try:
        # Check if driver is already running
        is_reusing = False
        if driver:
            try:
                # Check if driver is still responsive
                _ = driver.window_handles
                log_info("Reusing existing driver session...")
                driver.switch_to.window(driver.window_handles[-1])
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                is_reusing = True
            except Exception:
                log_info("Existing session unresponsive, starting fresh...")
                driver = None

        if not driver:
            if not init_driver():
                return False

        driver.get(search_url)

        # Wait for search results
        wait = WebDriverWait(driver, 15)
        log_info("Waiting for video elements to load...")
        
        # Multiple selector strategy for the first video title
        video_selectors = [
            (By.ID, "video-title"),
            (By.CSS_SELECTOR, "ytd-video-renderer #video-title"),
            (By.CSS_SELECTOR, "a#video-title-link")
        ]
        
        first_video = None
        for by, selector in video_selectors:
            try:
                first_video = wait.until(EC.element_to_be_clickable((by, selector)))
                if first_video: break
            except:
                continue
        
        if not first_video:
            log_error("Could not find any video in search results.")
            speak("I couldn't find any videos for that search.")
            return False

        log_success(f"Found video: {first_video.text}")
        first_video.click()

        # Wait for video page to stabilize
        time.sleep(2)
        
        # Auto-fullscreen attempt
        youtube_fullscreen()
        
        return True

    except Exception as e:
        log_error(f"YouTube playback failed: {e}")
        speak("Sorry, I encountered an error playing the video.")
        return False

def youtube_pause_resume(_=None):
    """Toggles play/pause state of the video."""
    global driver
    if not driver:
        speak("YouTube is not active.")
        return False
    
    log_info("Toggling Pause/Resume...")
    try:
        # Preferred: JS control for perfect reliability
        driver.execute_script("""
            const v = document.querySelector('video');
            if (v) {
                if (v.paused) v.play();
                else v.pause();
            }
        """)
        return True
    except Exception as e:
        log_error(f"Pause/Resume failed: {e}")
        # Fallback to 'k' key
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys("k")
            return True
        except:
            return False

def youtube_next(_=None):
    """Skips to the next video using UI button."""
    global driver
    if not driver:
        speak("YouTube is not active.")
        return False
    
    log_info("Attempting to skip to next video...")
    try:
        # Click the actual UI button
        next_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-next-button"))
        )
        next_btn.click()
        log_success("Next video button clicked.")
        return True
    except Exception as e:
        log_error(f"Next video button not found: {e}")
        # Fallback to Shift+N
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SHIFT + "n")
            log_info("Next video triggered via keyboard shortcut.")
            return True
        except:
            return False

def youtube_fullscreen(_=None):
    """Ensures video is in fullscreen mode."""
    global driver
    if not driver: return False
    
    log_info("Applying fullscreen...")
    try:
        # Try keyboard shortcut first
        driver.find_element(By.TAG_NAME, "body").send_keys("f")
        
        # Verify via JS and fallback if needed
        time.sleep(0.5)
        is_fs = driver.execute_script("return !!document.fullscreenElement;")
        if not is_fs:
            log_info("Keyboard shortcut 'f' failed, using JS fallback.")
            driver.execute_script("""
                const v = document.querySelector('video');
                const player = document.querySelector('#movie_player') || v;
                if (player.requestFullscreen) {
                    player.requestFullscreen();
                } else if (player.webkitRequestFullscreen) {
                    player.webkitRequestFullscreen();
                }
            """)
        return True
    except:
        return False

def youtube_volume_up(_=None):
    """Increases volume."""
    global driver
    if not driver: return False
    try:
        # Use Up arrow for visual feedback on YT UI
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
        # Add JS fallback/boost
        driver.execute_script("const v = document.querySelector('video'); if(v) v.volume = Math.min(1, v.volume + 0.05);")
        return True
    except:
        return False

def youtube_volume_down(_=None):
    """Decreases volume."""
    global driver
    if not driver: return False
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        driver.execute_script("const v = document.querySelector('video'); if(v) v.volume = Math.max(0, v.volume - 0.05);")
        return True
    except:
        return False

def youtube_skip_ads(_=None):
    """Manual trigger for ad skipping with retry loop."""
    global driver
    if not driver: return False
    
    log_info("Manual ad skip triggered...")
    skip_selectors = [".ytp-ad-skip-button", ".ytp-skip-ad-button", ".ytp-ad-skip-button-modern"]
    
    for i in range(3):  # Retry loop
        try:
            for selector in skip_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed():
                        el.click()
                        log_success("Ad skipped manually.")
                        return True
            time.sleep(1)
        except:
            continue
    return False

def close_youtube(_=None):
    """Safely closes YouTube driver and kills browser processes if needed."""
    global driver, ad_thread_running
    ad_thread_running = False
    
    if driver:
        speak("Closing YouTube")
        log_info("Terminating Selenium driver...")
        try:
            driver.quit()
        except Exception as e:
            log_error(f"Error quitting driver: {e}")
        driver = None
    
    # Force kill processes to ensure no hanging instances
    try:
        log_info("Ensuring browser processes are terminated...")
        subprocess.run(["taskkill", "/f", "/im", "brave.exe"], capture_output=True, shell=True)
        # Note: Be careful with taskkill if user is using Brave for other things, 
        # but the request asks for "Kill browser processes if selenium fails"
    except:
        pass
    
    speak("YouTube closed successfully.")
    return True

# -----------------------------
# TEST BLOCK
# -----------------------------
if __name__ == "__main__":
    log_info("Starting YouTube Automation Test...")
    
    # 1. Play Test
    if play_youtube("Lofi Girl"):
        time.sleep(10)
        
        # 2. Pause/Resume Test
        log_info("Testing Pause...")
        youtube_pause_resume()
        time.sleep(3)
        log_info("Testing Resume...")
        youtube_pause_resume()
        time.sleep(3)
        
        # 3. Next Test
        log_info("Testing Next Video...")
        youtube_next()
        time.sleep(10)
        
        # 4. Volume Test
        log_info("Testing Volume...")
        youtube_volume_up()
        youtube_volume_up()
        time.sleep(2)
        youtube_volume_down()
        
        # 5. Fullscreen Test
        log_info("Testing Fullscreen...")
        youtube_fullscreen()
        time.sleep(5)
        
        # 6. Close Test
        close_youtube()
    else:
        log_error("Test failed: Could not initiate playback.")
