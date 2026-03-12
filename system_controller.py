import webbrowser
import subprocess
import os
import time
import pyautogui
import screen_brightness_control as sbc

pyautogui.FAILSAFE = False


# =====================================================
# HELPERS
# =====================================================

def normalize(text):
    return text.lower().strip()


def open_url(url):
    webbrowser.open(url)
    time.sleep(6)


def launch_app(name):
    subprocess.Popen(f"start {name}", shell=True)


def close_app(proc):
    os.system(f"taskkill /f /im {proc}.exe")


def press(keys):
    if isinstance(keys, tuple):
        pyautogui.hotkey(*keys)
    else:
        pyautogui.press(keys)


# =====================================================
# BRIGHTNESS CONTROL
# =====================================================

def brightness_down():

    current = sbc.get_brightness(display=0)[0]
    new = max(10, current - 20)

    sbc.set_brightness(new)

    return "Brightness lowered."


def brightness_up():

    current = sbc.get_brightness(display=0)[0]
    new = min(100, current + 20)

    sbc.set_brightness(new)

    return "Brightness increased."


# =====================================================
# VOLUME CONTROL
# =====================================================

def volume_up():
    pyautogui.press("volumeup")
    return "Volume increased."


def volume_down():
    pyautogui.press("volumedown")
    return "Volume lowered."


def volume_mute():
    pyautogui.press("volumemute")
    return "Muted."


# =====================================================
# MEDIA CONTROL
# =====================================================

def next_song():
    pyautogui.press("nexttrack")
    return "Next track."


def previous_song():
    pyautogui.press("prevtrack")
    return "Previous track."


def pause_music():
    pyautogui.press("playpause")
    return "Playback toggled."


# =====================================================
# PLAY SONG
# =====================================================

def play_song(song):

    subprocess.Popen("start spotify", shell=True)

    time.sleep(6)

    pyautogui.hotkey("ctrl", "l")

    time.sleep(1)

    pyautogui.write(song, interval=0.05)

    time.sleep(1)

    pyautogui.press("enter")

    time.sleep(3)

    pyautogui.press("playpause")

    return f"Playing {song}"


# =====================================================
# MAIN COMMAND ROUTER
# =====================================================

def handle_system_command(text):

    t = normalize(text)


    # ---------------- OPEN APPS ----------------
    if "open youtube" in t:
        open_url("https://youtube.com")
        return "Opening YouTube."

    if "open spotify" in t:
        open_url("https://open.spotify.com")
        return "Opening Spotify."

    if "open chrome" in t:
        launch_app("chrome")
        return "Opening Chrome."


    # ---------------- PLAY SONG ----------------
    if t.startswith("play "):
        song = t.replace("play ", "").strip()
        return play_song(song)


    # ---------------- BRIGHTNESS ----------------
    if "brightness" in t or "bright" in t:

        if "lower" in t or "down" in t or "dim" in t:
            return brightness_down()

        if "increase" in t or "up" in t:
            return brightness_up()

    if "eyes hurt" in t or "too bright" in t:
        return brightness_down()


    # ---------------- VOLUME ----------------
    if "volume up" in t:
        return volume_up()

    if "volume down" in t:
        return volume_down()

    if "mute" in t:
        return volume_mute()


    # ---------------- MEDIA ----------------
    if "next song" in t:
        return next_song()

    if "previous song" in t:
        return previous_song()

    if "pause music" in t:
        return pause_music()


    # ---------------- CLOSE APPS ----------------
    if "close chrome" in t:
        close_app("chrome")
        return "Chrome closed."

    if "close spotify" in t:
        close_app("spotify")
        return "Spotify closed."


    # ---------------- TAB CONTROL ----------------
    if "close tab" in t:
        press(("ctrl", "w"))
        return "Tab closed."

    if "new tab" in t:
        press(("ctrl", "t"))
        return "New tab opened."


    # ---------------- WINDOW SWITCH ----------------
    if "switch window" in t:
        press(("alt", "tab"))
        return "Switched window."


    # ---------------- SEARCH ----------------
    if t.startswith("search "):
        query = t.replace("search ", "")
        open_url(f"https://www.google.com/search?q={query}")
        return f"Searching {query}."


    return None