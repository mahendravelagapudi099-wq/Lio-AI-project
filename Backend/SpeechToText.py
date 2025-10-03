from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "auto")  # auto-detect if not specified

# HTML content for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (webkitSpeechRecognition || SpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };

            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject chosen language
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save HTML file
os.makedirs("Data", exist_ok=True)
html_file_path = os.path.join("Data", "Voice.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

print(f"Open this file in your browser to use speech recognition:\n{html_file_path}")

# Temporary assistant status path
TempDirPath = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Update assistant status."""
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    """Format the text properly with punctuation."""
    new_query = Query.strip()
    if not new_query.endswith(('.', '?', '!')):
        new_query += "?"
    return new_query.capitalize()

def UniversalTranslator(Text, target_lang="en"):
    """Translate text to English (if needed)."""
    return mt.translate(Text, target_lang, "auto")

def SpeechRecognition():
    """
    Instructions for the user to open the HTML file and get the speech input.
    Supports multiple languages (Hindi, Telugu, etc.) and translates to English if needed.
    """
    print("\nOpen the HTML file in your browser to start speech recognition.")
    print(f"File location: {html_file_path}")
    print("After speaking, copy the text from the browser output and paste it here.")
    
    Text = input("Paste recognized text here: ").strip()
    if not Text:
        return None, None

    # Translate to English if input language is not English
    if InputLanguage.lower() not in ["en", "english", "auto"]:
        SetAssistantStatus("Translating...")
        Text = UniversalTranslator(Text, "en")
    
    return QueryModifier(Text), InputLanguage

# Run the assistant
if __name__ == "__main__":
    while True:
        Text, lang = SpeechRecognition()
        if Text:
            print(f"Processed Text: {Text} (Language: {lang})")
