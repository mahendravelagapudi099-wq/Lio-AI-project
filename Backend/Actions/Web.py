import webbrowser
from googlesearch import search
from Backend.app.youtube import play_youtube

def GoogleSearch(query):
    print(f"[Web] Searching Google: {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def YoutubeSearch(query):
    print(f"[Web] Searching YouTube: {query}")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

def PlayYoutube(query):
    print(f"[Web] Playing on YouTube: {query}")
    return play_youtube(query)

