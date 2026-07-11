"""
JARVIS Config
=============
All the knobs you'll actually want to tweak live here.
"""

import os

# ----- Wake word & listening behaviour -----
WAKE_WORD = "jarvis"                 # say this to get its attention
CONTINUOUS_MODE = True               # if True, keeps listening after wake word until you say "stop listening"
LISTEN_TIMEOUT = 5                   # seconds to wait for speech to start
PHRASE_TIME_LIMIT = 8                # max seconds for a single command
AMBIENT_NOISE_ADJUST_DURATION = 0.6  # seconds spent calibrating mic noise on startup

# ----- Voice (TTS) -----
TTS_RATE = 180        # words per minute (lower = slower/clearer)
TTS_VOLUME = 1.0      # 0.0 - 1.0
TTS_VOICE_INDEX = 0   # 0 = default installed voice, 1 = usually the alternate (often female) voice on Windows

# ----- Speech recognition -----
# "google"  -> free, needs internet, very accurate (default)
# "sphinx"  -> offline, less accurate, needs pocketsphinx installed
STT_ENGINE = "google"
STT_LANGUAGE = "en-in"   # change to "en-us", "en-gb" etc. as you prefer

# ----- Applications JARVIS can open by voice -----
# Add/edit freely. Key = what you say ("open chrome"), Value = path or command Windows can run.
APP_PATHS = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "vscode": "code",
    "visual studio code": "code",
    "spotify": "spotify.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "settings": "start ms-settings:",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
}

# ----- Quick-access folders (say: "open downloads") -----
USER_HOME = os.path.expanduser("~")
FOLDER_PATHS = {
    "downloads": os.path.join(USER_HOME, "Downloads"),
    "documents": os.path.join(USER_HOME, "Documents"),
    "desktop": os.path.join(USER_HOME, "Desktop"),
    "pictures": os.path.join(USER_HOME, "Pictures"),
    "music": os.path.join(USER_HOME, "Music"),
    "videos": os.path.join(USER_HOME, "Videos"),
}

# ----- Misc -----
NOTES_FILE = os.path.join(os.path.dirname(__file__), "data", "notes.json")
SCREENSHOT_DIR = os.path.join(USER_HOME, "Pictures", "Jarvis Screenshots")

# Commands that require a verbal "yes"/"confirm" before executing (safety)
DESTRUCTIVE_COMMANDS = {"shutdown", "restart", "empty recycle bin", "sign out"}
