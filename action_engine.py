import webbrowser
import os
import subprocess
import pyautogui
import time
import json
import requests
import re
from openai import OpenAI

STATE_FILE = "system_state.json"


# ---------------- STATE ----------------
def load_state():
    if not os.path.exists(STATE_FILE):
        return {"active_app": None, "awaiting_song": False}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def set_app(name):
    s = load_state()
    s["active_app"] = name
    save_state(s)


def set_waiting(val):
    s = load_state()
    s["awaiting_song"] = val
    save_state(s)


def is_waiting():
    return load_state()["awaiting_song"]


# ---------------- OPEN APPS ----------------
def open_chrome():
    subprocess.Popen("start chrome", shell=True)
    time.sleep(3)


def open_spotify():
    webbrowser.open("https://open.spotify.com")
    time.sleep(5)


# ---------------- YOUTUBE ----------------
def get_first_youtube_video(query):

    url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")

    html = requests.get(url).text

    match = re.search(r"watch\?v=(\S{11})", html)

    if match:
        return "https://www.youtube.com/watch?v=" + match.group(1)

    return None


# ---------------- AI SONG GENERATOR ----------------
def generate_song_from_ai():

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    prompt = "Name one popular song only."

    r = client.chat.completions.create(
        model="llama3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=20
    )

    song = r.choices[0].message.content.strip()

    with open("temp_memory.json", "w") as f:
        json.dump({"last_generated_song": song}, f)

    return song


# ---------------- SPOTIFY PLAY ----------------
def play_song(song):

    # open spotify search page for track results
    url = f"https://open.spotify.com/search/{song.replace(' ','%20')}"
    webbrowser.open(url)

    # wait for page to fully load
    time.sleep(7)

    # click the first play button
    PLAY_X = 562
    PLAY_Y = 635

    pyautogui.click(PLAY_X, PLAY_Y)

    return f"Playing {song}."


# =========================================================
# ===================== MAIN HANDLER ======================
# =========================================================
def handle_action(text):

    t = text.lower().strip()


    # ---------------- SONG FOLLOWUP ----------------
    if is_waiting():
        set_waiting(False)
        return play_song(text.strip())


    # ---------------- YOUTUBE PLAY ----------------
    if "youtube" in t:

        query = (
            t.replace("play", "")
            .replace("on youtube", "")
            .replace("youtube", "")
            .replace("video", "")
            .strip()
        )

        if query == "" or query in ["something", "anything", "random"]:

            client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

            r = client.chat.completions.create(
                model="llama3",
                messages=[{"role": "user", "content": "Give one YouTube video idea"}],
                temperature=0.9,
                max_tokens=20
            )

            query = r.choices[0].message.content.strip()

        video = get_first_youtube_video(query)

        if video:
            webbrowser.open(video)
            return f"Playing {query}."

        return "Couldn't find video."


    # ---------------- SPOTIFY PLAY ----------------
    if "play" in t:

        auto_words = ["something", "anything", "nice", "random"]

        if any(w in t for w in auto_words):
            song = generate_song_from_ai()
            return play_song(song)

        song = (
            t.replace("play", "")
            .replace("song", "")
            .replace("on spotify", "")
            .strip()
        )

        if song:
            return play_song(song)

        set_waiting(True)
        return "Which song?"


    # ---------------- OPEN APPS ----------------
    if "open chrome" in t:
        open_chrome()
        set_app("chrome")
        return "Opening Chrome."

    if "open spotify" in t:
        open_spotify()
        set_app("spotify")
        return "Opening Spotify."

    if "open youtube" in t:
        webbrowser.open("https://youtube.com")
        set_app("youtube")
        return "Opening YouTube."


    # ---------------- CLOSE APPS ----------------
    if "close chrome" in t:
        os.system("taskkill /f /im chrome.exe")
        return "Closed Chrome."

    if "close spotify" in t:
        os.system("taskkill /f /im spotify.exe")
        return "Closed Spotify."


    return None