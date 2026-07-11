"""
JARVIS Intents
==============
Turns raw recognized text ("open chrome please", "set volume to 40")
into a (skill_function, response_text) call.

Add a new voice command by adding one entry to INTENTS below —
no need to touch the listening loop in jarvis.py.
"""

import re
import config
import skills

# Each pattern maps to a handler(match, text) -> str (what JARVIS should say)
# Patterns are tried in order, first match wins, so put more specific ones first.

INTENTS = []


def intent(pattern):
    """Decorator to register a regex -> handler mapping."""
    compiled = re.compile(pattern, re.IGNORECASE)

    def wrapper(func):
        INTENTS.append((compiled, func))
        return func
    return wrapper


# ----- Time / date -----
@intent(r"\bwhat('?s| is) the time\b|\bcurrent time\b")
def _time(m, text):
    return skills.get_time()


@intent(r"\bwhat('?s| is) (the )?date\b|\btoday'?s date\b|\bwhat day is it\b")
def _date(m, text):
    return skills.get_date()


# ----- Apps -----
@intent(r"\bopen\s+(the\s+)?(?P<name>.+?)(\s+for me)?$")
def _open_app_or_folder(m, text):
    name = m.group("name").strip()
    if name in config.FOLDER_PATHS or skills._closest_match(name, config.FOLDER_PATHS.keys()):
        return skills.open_folder(name)
    return skills.open_app(name)


@intent(r"\bclose\s+(the\s+)?(?P<name>.+)")
def _close_app(m, text):
    return skills.close_app(m.group("name").strip())


# ----- Web -----
@intent(r"\bsearch (for )?(?P<query>.+?)( on (the )?(web|google|internet))?$")
def _search(m, text):
    return skills.web_search(m.group("query").strip())


@intent(r"\bplay\s+(?P<query>.+?)( on youtube)?$")
def _play(m, text):
    return skills.youtube_search(m.group("query").strip())


@intent(r"\b(who|what) is\s+(?P<query>.+)")
def _wiki(m, text):
    return skills.wikipedia_summary(m.group("query").strip())


# ----- Volume -----
@intent(r"\bvolume (to|at)\s*(?P<pct>\d{1,3})")
def _vol_set(m, text):
    return skills.set_volume(int(m.group("pct")))


@intent(r"\b(volume up|increase volume|louder)\b")
def _vol_up(m, text):
    return skills.change_volume(10)


@intent(r"\b(volume down|decrease volume|lower volume|quieter)\b")
def _vol_down(m, text):
    return skills.change_volume(-10)


@intent(r"\b(mute|unmute)\b")
def _mute(m, text):
    return skills.mute()


# ----- Brightness -----
@intent(r"\bbrightness (to|at)\s*(?P<pct>\d{1,3})")
def _bright_set(m, text):
    return skills.set_brightness(int(m.group("pct")))


@intent(r"\b(brightness up|increase brightness|screen brighter)\b")
def _bright_up(m, text):
    return skills.change_brightness(10)


@intent(r"\b(brightness down|decrease brightness|screen dimmer|dim (the )?screen)\b")
def _bright_down(m, text):
    return skills.change_brightness(-10)


# ----- Power -----
@intent(r"\bshut ?down\b")
def _shutdown(m, text):
    return skills.shutdown()


@intent(r"\brestart\b")
def _restart(m, text):
    return skills.restart()


@intent(r"\b(go to )?sleep\b")
def _sleep(m, text):
    return skills.sleep()


@intent(r"\bsign ?out\b|\blog ?off\b")
def _signout(m, text):
    return skills.sign_out()


@intent(r"\block( the)? (screen|(this )?(pc|computer|laptop))\b|\block it\b")
def _lock(m, text):
    return skills.lock()


@intent(r"\bcancel shutdown\b|\bstop shutdown\b")
def _cancel_shutdown(m, text):
    return skills.cancel_shutdown()


@intent(r"\bempty (the )?recycle bin\b")
def _empty_bin(m, text):
    return skills.empty_recycle_bin()


# ----- System info -----
@intent(r"\bbattery\b")
def _battery(m, text):
    return skills.battery_status()


@intent(r"\b(system status|cpu usage|ram usage|how'?s my (system|pc|laptop) doing)\b")
def _sys_status(m, text):
    return skills.system_status()


@intent(r"\b(take a )?screenshot\b")
def _screenshot(m, text):
    return skills.take_screenshot()


# ----- Notes -----
@intent(r"\b(take a note|make a note|note that|remember that|write down)\s*(?P<text>.+)?")
def _add_note(m, text):
    content = (m.group("text") or "").strip()
    return skills.add_note(content)


@intent(r"\bread (my )?notes\b|\bwhat are my notes\b")
def _read_notes(m, text):
    return skills.read_notes()


@intent(r"\bclear (my )?notes\b|\bdelete (my )?notes\b")
def _clear_notes(m, text):
    return skills.clear_notes()


# ----- Fun / misc -----
@intent(r"\btell me a joke\b|\bmake me laugh\b")
def _joke(m, text):
    return skills.tell_joke()


@intent(r"\bhow are you\b")
def _how_are_you(m, text):
    return "Running at full capacity and ready to help."


@intent(r"\bwho are you\b|\byour name\b")
def _who_are_you(m, text):
    return "I'm JARVIS, your personal voice assistant."


def resolve(text):
    """
    Try every registered intent pattern against the text.
    Returns the spoken response string, or None if nothing matched.
    """
    text = text.strip().lower()
    for pattern, handler in INTENTS:
        match = pattern.search(text)
        if match:
            try:
                return handler(match, text)
            except Exception as e:
                return f"I hit an error running that: {e}"
    return None
