"""
JARVIS Skills
=============
Every real "action" JARVIS can take lives here as a plain function.
jarvis.py just figures out WHICH function to call; this file does the work.

Keeping actions separate from the listening loop means you can add a new
skill by writing one function + one line in intents.py, without touching
the voice pipeline at all.
"""

import os
import sys
import json
import subprocess
import datetime
import webbrowser
import difflib

import config

try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _PYCAW_OK = True
except ImportError:
    _PYCAW_OK = False


# ---------------------------------------------------------------------------
# Time / date
# ---------------------------------------------------------------------------

def get_time():
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')}."


def get_date():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}."


# ---------------------------------------------------------------------------
# Applications & folders
# ---------------------------------------------------------------------------

def _closest_match(name, options):
    matches = difflib.get_close_matches(name, options, n=1, cutoff=0.6)
    return matches[0] if matches else None


def open_app(name):
    name = name.strip().lower()
    target = config.APP_PATHS.get(name)
    if not target:
        closest = _closest_match(name, config.APP_PATHS.keys())
        if closest:
            target = config.APP_PATHS[closest]
            name = closest
    if not target:
        return f"I don't have {name} registered. Add it to APP_PATHS in config.py."
    try:
        if target.startswith("start "):
            os.system(target)
        else:
            subprocess.Popen(target, shell=True)
        return f"Opening {name}."
    except Exception as e:
        return f"I couldn't open {name}: {e}"


def close_app(name):
    """Force-closes an app by process/image name, e.g. 'chrome' -> chrome.exe"""
    name = name.strip().lower()
    target = config.APP_PATHS.get(name, name)
    image_name = target if target.endswith(".exe") else f"{name}.exe"
    try:
        result = subprocess.run(
            ["taskkill", "/IM", image_name, "/F"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return f"Closed {name}."
        return f"{name} doesn't seem to be running."
    except Exception as e:
        return f"I couldn't close {name}: {e}"


def open_folder(name):
    name = name.strip().lower()
    path = config.FOLDER_PATHS.get(name)
    if not path:
        closest = _closest_match(name, config.FOLDER_PATHS.keys())
        if closest:
            path = config.FOLDER_PATHS[closest]
    if not path or not os.path.exists(path):
        return f"I couldn't find a folder called {name}."
    os.startfile(path)
    return f"Opening {name}."


# ---------------------------------------------------------------------------
# Web
# ---------------------------------------------------------------------------

def web_search(query):
    if not query:
        return "What should I search for?"
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching the web for {query}."


def youtube_search(query):
    if not query:
        return "What should I play?"
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Looking that up on YouTube."


def wikipedia_summary(query):
    try:
        import wikipedia
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except Exception:
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
        return f"I opened the Wikipedia page for {query} in your browser."


# ---------------------------------------------------------------------------
# Volume (Windows, via pycaw)
# ---------------------------------------------------------------------------

def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def set_volume(percent):
    if not _PYCAW_OK:
        return "Volume control needs pycaw installed: pip install pycaw comtypes"
    percent = max(0, min(100, int(percent)))
    vol = _get_volume_interface()
    vol.SetMasterVolumeLevelScalar(percent / 100, None)
    return f"Volume set to {percent} percent."


def change_volume(delta):
    if not _PYCAW_OK:
        return "Volume control needs pycaw installed: pip install pycaw comtypes"
    vol = _get_volume_interface()
    current = vol.GetMasterVolumeLevelScalar()
    new_val = max(0.0, min(1.0, current + delta / 100))
    vol.SetMasterVolumeLevelScalar(new_val, None)
    return f"Volume {'up' if delta > 0 else 'down'} to {int(new_val * 100)} percent."


def mute():
    if not _PYCAW_OK:
        return "Volume control needs pycaw installed: pip install pycaw comtypes"
    vol = _get_volume_interface()
    currently_muted = vol.GetMute()
    vol.SetMute(0 if currently_muted else 1, None)
    return "Unmuted." if currently_muted else "Muted."


# ---------------------------------------------------------------------------
# Brightness
# ---------------------------------------------------------------------------

def set_brightness(percent):
    if not sbc:
        return "Brightness control needs: pip install screen-brightness-control"
    percent = max(0, min(100, int(percent)))
    try:
        sbc.set_brightness(percent)
        return f"Brightness set to {percent} percent."
    except Exception as e:
        return f"Couldn't change brightness: {e}"


def change_brightness(delta):
    if not sbc:
        return "Brightness control needs: pip install screen-brightness-control"
    try:
        current = sbc.get_brightness()[0]
        new_val = max(0, min(100, current + delta))
        sbc.set_brightness(new_val)
        return f"Brightness {'up' if delta > 0 else 'down'} to {new_val} percent."
    except Exception as e:
        return f"Couldn't change brightness: {e}"


# ---------------------------------------------------------------------------
# Power / session control
# ---------------------------------------------------------------------------

def shutdown():
    os.system("shutdown /s /t 5")
    return "Shutting down in 5 seconds."


def restart():
    os.system("shutdown /r /t 5")
    return "Restarting in 5 seconds."


def sleep():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Going to sleep."


def sign_out():
    os.system("shutdown /l")
    return "Signing out."


def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "Locking the screen."


def cancel_shutdown():
    os.system("shutdown /a")
    return "Shutdown cancelled."


def empty_recycle_bin():
    try:
        import winshell
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
        return "Recycle bin emptied."
    except ImportError:
        return "Emptying the recycle bin needs: pip install winshell pywin32"
    except Exception as e:
        return f"Couldn't empty the recycle bin: {e}"


# ---------------------------------------------------------------------------
# System info
# ---------------------------------------------------------------------------

def battery_status():
    if not psutil:
        return "System info needs: pip install psutil"
    battery = psutil.sensors_battery()
    if not battery:
        return "No battery detected — looks like a desktop."
    plugged = "and charging" if battery.power_plugged else "and not charging"
    return f"Battery is at {battery.percent} percent {plugged}."


def system_status():
    if not psutil:
        return "System info needs: pip install psutil"
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"CPU usage is {cpu} percent, RAM usage is {ram} percent."


def take_screenshot():
    if not pyautogui:
        return "Screenshots need: pip install pyautogui"
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    filename = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(config.SCREENSHOT_DIR, filename)
    pyautogui.screenshot().save(path)
    return f"Screenshot saved to {path}."


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def _load_notes():
    os.makedirs(os.path.dirname(config.NOTES_FILE), exist_ok=True)
    if not os.path.exists(config.NOTES_FILE):
        return []
    with open(config.NOTES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_notes(notes):
    os.makedirs(os.path.dirname(config.NOTES_FILE), exist_ok=True)
    with open(config.NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2)


def add_note(text):
    if not text:
        return "What should the note say?"
    notes = _load_notes()
    entry = {"text": text, "timestamp": datetime.datetime.now().isoformat(timespec="seconds")}
    notes.append(entry)
    _save_notes(notes)
    return "Noted."


def read_notes():
    notes = _load_notes()
    if not notes:
        return "You don't have any notes yet."
    if len(notes) == 1:
        return f"You have one note: {notes[0]['text']}"
    latest = notes[-3:]
    lines = "; ".join(n["text"] for n in latest)
    return f"Here are your last {len(latest)} notes: {lines}"


def clear_notes():
    _save_notes([])
    return "All notes cleared."


# ---------------------------------------------------------------------------
# Fun
# ---------------------------------------------------------------------------

import random

_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I would tell you a UDP joke, but you might not get it.",
    "There are 10 types of people: those who understand binary, and those who don't.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: can I join you?",
]


def tell_joke():
    return random.choice(_JOKES)
