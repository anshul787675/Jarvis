"""
JARVIS - Personal Voice Assistant for Windows
==============================================
Run this file, say "Jarvis" to wake it up, then speak a command.

    python jarvis.py

See README.md for setup instructions.
"""

import sys
import time

import config
import intents
import traceback

try:
    import speech_recognition as sr
except ImportError:
    print("Missing dependency. Run: pip install SpeechRecognition pyaudio")
    sys.exit(1)

try:
    import pyttsx3
except ImportError:
    print("Missing dependency. Run: pip install pyttsx3")
    sys.exit(1)


EXIT_PHRASES = {"stop listening", "go to sleep now", "exit", "quit", "shut up jarvis"}
CONFIRM_YES = {"yes", "yeah", "confirm", "do it", "go ahead"}
CONFIRM_NO = {"no", "cancel", "nevermind", "never mind", "stop"}


class Jarvis:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.engine = pyttsx3.init()
        self._configure_voice()
        self.awake = False

        print("Calibrating for ambient noise... stay quiet for a moment.")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(
                source, duration=config.AMBIENT_NOISE_ADJUST_DURATION
            )
        print("Ready. Say the wake word:", config.WAKE_WORD)

    def _configure_voice(self):
        self.engine.setProperty("rate", config.TTS_RATE)
        self.engine.setProperty("volume", config.TTS_VOLUME)
        voices = self.engine.getProperty("voices")
        if voices and 0 <= config.TTS_VOICE_INDEX < len(voices):
            self.engine.setProperty("voice", voices[config.TTS_VOICE_INDEX].id)

    def say(self, text):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout=None, phrase_time_limit=None):
        """Returns recognized text (lowercase) or '' if nothing/unclear."""
        with self.mic as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout or config.LISTEN_TIMEOUT,
                    phrase_time_limit=phrase_time_limit or config.PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                return ""

        try:
            if config.STT_ENGINE == "sphinx":
                text = self.recognizer.recognize_sphinx(audio)
            else:
                # Try online Google STT first, but handle network/timeouts and
                # fall back to offline Sphinx if available.
                try:
                    text = self.recognizer.recognize_google(
                        audio, language=config.STT_LANGUAGE
                    )
                except (sr.RequestError, TimeoutError, OSError) as e:
                    # Network or service error — attempt offline fallback
                    print(f"Speech service error: {e}")
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                    except Exception as e2:
                        print(f"Offline STT failed: {e2}")
                        return ""

            print(f"You: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
            return ""

    def handle_command(self, text):
        if not text:
            return

        # Destructive actions get a spoken confirmation step
        for keyword in config.DESTRUCTIVE_COMMANDS:
            if keyword in text:
                self.say(f"Are you sure you want to {keyword}? Say yes to confirm.")
                confirmation = self.listen(timeout=6, phrase_time_limit=4)
                if confirmation not in CONFIRM_YES:
                    self.say("Okay, cancelled.")
                    return
                break

        response = intents.resolve(text)
        if response:
            self.say(response)
        else:
            self.say("I didn't catch a command I know how to run. Try rephrasing.")

    def run(self):
        while True:
            try:
                heard = self.listen(timeout=None, phrase_time_limit=3)
                if config.WAKE_WORD in heard:
                    self.say("Yes?")
                    self._conversation_loop()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print("Unhandled error in main loop:", e)
                traceback.print_exc()
                # continue listening after a short delay
                time.sleep(1)

    def _conversation_loop(self):
        """After wake word: keep taking commands until an exit phrase or silence."""
        idle_count = 0
        while True:
            try:
                text = self.listen()
                if not text:
                    idle_count += 1
                    if idle_count >= 3 or not config.CONTINUOUS_MODE:
                        return  # go back to sleep, wait for wake word again
                    continue
                idle_count = 0

                if any(phrase in text for phrase in EXIT_PHRASES):
                    self.say("Going back to sleep.")
                    return

                try:
                    self.handle_command(text)
                except Exception as e:
                    print(f"Error handling command: {e}")
                    traceback.print_exc()
                    self.say("I hit an error while running that command.")

                if not config.CONTINUOUS_MODE:
                    return
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print("Unhandled error in conversation loop:", e)
                traceback.print_exc()
                # break back to main loop
                return


def main():
    print("=" * 50)
    print("  J.A.R.V.I.S. — Personal Voice Assistant")
    print("=" * 50)
    assistant = Jarvis()
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\nShutting down JARVIS. Goodbye.")


if __name__ == "__main__":
    main()
