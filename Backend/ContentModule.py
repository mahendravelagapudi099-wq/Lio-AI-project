import subprocess
import os
import time
import pyautogui
from pathlib import Path
import random
import re
from dotenv import dotenv_values

# Load API keys
env_vars = dotenv_values(".env")

# Try to import Cohere (optional, will use fallback if not available)
try:
    import cohere
    COHERE_AVAILABLE = True
    CohereAPIKey = env_vars.get("CohereAPIKey", "")
    if CohereAPIKey:
        co = cohere.Client(api_key=CohereAPIKey)
    else:
        COHERE_AVAILABLE = False
        print("[ContentModule] No Cohere API key found in .env")
except ImportError:
    COHERE_AVAILABLE = False
    print("[ContentModule] Cohere not installed")

# Try to import psutil and pygetwindow (optional)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[ContentModule] psutil not installed - some features limited")

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    print("[ContentModule] pygetwindow not installed - window focus disabled")

def Content(query):
    """
    Handle content creation tasks in Notepad using AI
    Supports:
    - AI Generation: "write a love letter", "write a leave application", "write a poem about sunset"
    - Simple text: "write hello world"
    - Saving: "save file", "save filename as test"
    - Combined: "write a love letter and save as love"
    - Clearing: "clear notepad", "clear all content"
    """
    try:
        print(f"[Content] Processing: {query}")
        
        query_lower = query.lower().strip()
        
        # Handle COMBINED operations (write + save)
        if ("write" in query_lower or "create" in query_lower or "generate" in query_lower) and "save" in query_lower:
            return HandleCombinedWriteAndSave(query)
        
        # Handle CLEAR operations
        if "clear" in query_lower and ("notepad" in query_lower or "content" in query_lower):
            return ClearNotepad()
        
        # Handle SAVE operations
        if "save" in query_lower and not any(word in query_lower for word in ["write", "create", "generate"]):
            return SaveNotepadFile(query)
        
        # Handle WRITE/TYPE operations (with AI)
        return WriteToNotepad(query)
        
    except Exception as e:
        print(f"[Content] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def WriteToNotepad(query):
    """Write AI-generated or simple content to Notepad"""
    try:
        query_lower = query.lower()
        
        # Determine what content to write
        content_to_write = ""
        
        # Check if it's a request for AI-generated content
        if COHERE_AVAILABLE and NeedsAIGeneration(query_lower):
            print("[Content] Generating content using AI...")
            content_to_write = GenerateAIContent(query)
            if not content_to_write:
                print("[Content] AI generation failed, using fallback")
                content_to_write = GenerateFallbackContent(query_lower)
        else:
            # Use simple/fallback content
            content_to_write = GenerateFallbackContent(query_lower)
        
        # Check if Notepad is already open
        notepad_open = IsNotepadOpen()
        
        if not notepad_open:
            print("[Content] Opening Notepad...")
            subprocess.Popen(["notepad.exe"])
            time.sleep(1.5)
        else:
            print("[Content] Using existing Notepad window...")
            FocusNotepad()
            time.sleep(0.5)
        
        # Type the content
        print(f"[Content] Typing content ({len(content_to_write)} characters)...")
        
        # For longer content, type faster
        interval = 0.01 if len(content_to_write) > 100 else 0.05
        
        # Split into lines and type with proper formatting
        lines = content_to_write.split('\n')
        for i, line in enumerate(lines):
            pyautogui.write(line, interval=interval)
            if i < len(lines) - 1:  # Don't press enter on last line
                pyautogui.press('enter')
        
        print("[Content] ✅ Successfully wrote content to Notepad")
        return True
        
    except Exception as e:
        print(f"[WriteToNotepad] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def NeedsAIGeneration(query_lower):
    """Determine if query needs AI generation"""
    ai_keywords = [
        "letter", "application", "email", "essay", "story", "poem", 
        "article", "report", "speech", "script", "code", "program",
        "proposal", "resume", "cv", "bio", "description", "review",
        "summary", "analysis", "explanation", "tutorial", "guide",
        "apology", "thank", "invitation", "announcement", "notice"
    ]
    
    # Check if query contains any AI-worthy keywords
    for keyword in ai_keywords:
        if keyword in query_lower:
            return True
    
    # If it's asking to "write" something with multiple words, probably needs AI
    if "write" in query_lower or "create" in query_lower or "generate" in query_lower:
        words_after = query_lower.split("write")[-1].strip() if "write" in query_lower else ""
        if not words_after:
            words_after = query_lower.split("create")[-1].strip() if "create" in query_lower else ""
        if not words_after:
            words_after = query_lower.split("generate")[-1].strip()
        
        # If more than 3 words, probably needs AI
        if len(words_after.split()) > 3:
            return True
    
    return False

def GenerateAIContent(query):
    """Generate content using Cohere AI"""
    try:
        if not COHERE_AVAILABLE:
            return None
        
        # Extract the actual content request
        content_request = ExtractContentRequest(query)
        
        # Create a proper prompt
        prompt = f"""Write {content_request}. Make it professional, well-formatted, and complete.
        
Do not include any meta-commentary. Just write the requested content directly."""
        
        print(f"[AI] Generating: {content_request}")
        
        response = co.chat(
            model='command-xlarge-nightly',
            message=prompt,
            temperature=0.8,
            max_tokens=1000
        )
        
        # Extract text from response
        generated_text = ""
        if hasattr(response, 'text'):
            generated_text = response.text
        elif hasattr(response, 'message'):
            generated_text = response.message
        else:
            # Try to get text from stream
            for event in response:
                if hasattr(event, 'text'):
                    generated_text += event.text
        
        if generated_text:
            print(f"[AI] Generated {len(generated_text)} characters")
            return generated_text.strip()
        else:
            print("[AI] No text generated")
            return None
            
    except Exception as e:
        print(f"[AI] Error: {e}")
        return None

def ExtractContentRequest(query):
    """Extract what the user wants to write"""
    query_lower = query.lower()
    
    # Remove common prefixes
    for prefix in ["write", "create", "generate", "make", "type", "a ", "an ", "on notepad", "in notepad", "to notepad"]:
        query_lower = query_lower.replace(prefix, "")
    
    return query_lower.strip()

def GenerateFallbackContent(query_lower):
    """Generate simple content without AI"""
    if "joke" in query_lower:
        return GenerateJoke()
    elif "poem" in query_lower:
        return GeneratePoem()
    elif "hello" in query_lower:
        return "Hello World!"
    elif "test" in query_lower:
        return "This is a test message from Lio AI Assistant."
    else:
        # Extract text to write
        for keyword in ["write", "type", "create", "make"]:
            if keyword in query_lower:
                parts = query_lower.split(keyword, 1)
                if len(parts) > 1:
                    text = parts[1].strip()
                    # Remove "on notepad", etc.
                    for phrase in ["on notepad", "in notepad", "to notepad", "notepad"]:
                        text = text.replace(phrase, "")
                    text = text.strip()
                    if text:
                        return text
        
        return "Content created by Lio AI Assistant"

def HandleCombinedWriteAndSave(query):
    """Handle commands that both write and save"""
    try:
        print("[Content] Handling combined write + save operation")
        
        # First, write the content
        WriteToNotepad(query)
        time.sleep(1.0)
        
        # Then, save the file
        SaveNotepadFile(query)
        
        return True
    except Exception as e:
        print(f"[HandleCombinedWriteAndSave] ❌ Error: {e}")
        return False

def SaveNotepadFile(query):
    """Save the current Notepad file"""
    try:
        query_lower = query.lower()
        
        # Extract filename
        filename = ExtractFilename(query)
        
        print(f"[SaveNotepadFile] Attempting to save as: {filename}")
        
        # Focus Notepad window
        if not IsNotepadOpen():
            print("[SaveNotepadFile] ⚠️ No Notepad window found!")
            return False
        
        FocusNotepad()
        time.sleep(0.3)
        
        # Use Ctrl+S to open Save dialog
        print("[SaveNotepadFile] Pressing Ctrl+S...")
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1.2)
        
        # Type filename
        print(f"[SaveNotepadFile] Typing filename: {filename}")
        pyautogui.write(filename, interval=0.05)
        time.sleep(0.3)
        
        # Press Enter to save
        print("[SaveNotepadFile] Pressing Enter to save...")
        pyautogui.press('enter')
        time.sleep(0.5)
        
        print(f"[SaveNotepadFile] ✅ File saved as: {filename}")
        return True
        
    except Exception as e:
        print(f"[SaveNotepadFile] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def ExtractFilename(query):
    """Extract filename from query"""
    query_lower = query.lower()
    
    # Look for patterns like "save as X" or "filename X" or "name X"
    patterns = [
        r'(?:save\s+)?(?:as|name|filename)\s+([a-zA-Z0-9_\-]+)',
        r'(?:save\s+)?file\s+name\s+([a-zA-Z0-9_\-]+)',
        r'(?:save\s+)?filename\s+as\s+([a-zA-Z0-9_\-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            filename = match.group(1)
            # Add .txt if no extension
            if "." not in filename:
                filename += ".txt"
            return filename
    
    # Fallback: try to extract the last meaningful word
    words = query_lower.split()
    keywords_to_skip = ["save", "the", "file", "as", "name", "filename", "notepad", "in", "on", "to", "a", "an"]
    
    for word in reversed(words):
        word_clean = word.strip('.,!?')
        if word_clean and word_clean not in keywords_to_skip and len(word_clean) > 1:
            filename = word_clean
            if "." not in filename:
                filename += ".txt"
            return filename
    
    # Ultimate fallback
    return "document.txt"

def ClearNotepad():
    """Clear all content in Notepad"""
    try:
        print("[ClearNotepad] Clearing Notepad content...")
        
        if not IsNotepadOpen():
            print("[ClearNotepad] ⚠️ No Notepad window found!")
            return False
        
        FocusNotepad()
        time.sleep(0.3)
        
        # Select all (Ctrl+A) and delete
        print("[ClearNotepad] Selecting all content...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        
        print("[ClearNotepad] Deleting content...")
        pyautogui.press('delete')
        time.sleep(0.2)
        
        print("[ClearNotepad] ✅ Content cleared")
        return True
        
    except Exception as e:
        print(f"[ClearNotepad] ❌ Error: {e}")
        return False

def IsNotepadOpen():
    """Check if Notepad is currently open"""
    if not PSUTIL_AVAILABLE:
        return False
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'notepad.exe' in proc.info['name'].lower():
                return True
        return False
    except:
        return False

def FocusNotepad():
    """Bring Notepad window to focus"""
    if not PYGETWINDOW_AVAILABLE:
        return False
    try:
        windows = gw.getWindowsWithTitle('Notepad')
        if not windows:
            windows = gw.getWindowsWithTitle('notepad')
        if windows:
            windows[0].activate()
            return True
        return False
    except:
        return False

def GenerateJoke():
    """Generate a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why couldn't the bicycle stand up by itself? It was two tired!",
        "What did the ocean say to the beach? Nothing, it just waved!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "What's a computer's favorite snack? Microchips!"
    ]
    return random.choice(jokes)

def GeneratePoem():
    """Generate a simple poem"""
    poems = [
        "Roses are red,\nViolets are blue,\nAI is awesome,\nAnd so are you!",
        "In circuits and code,\nI find my way,\nTo help and assist,\nEvery single day!",
        "Binary dreams,\nIn silicon sleep,\nAwakened by voice,\nPromises to keep!"
    ]
    return random.choice(poems)