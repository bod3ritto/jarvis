"""
test_voice_loop.py — Test pętli: JARVIS mówi, słucha, odpowiada (3 razy).

Uruchom:
    python test_voice_loop.py
"""
from voice.speech_engine import SpeechEngine
from voice.tts_engine import TTSEngine


def main():
    speech = SpeechEngine()
    tts = TTSEngine()

    tts.speak("Cześć, jestem Jarvis. Powiedz coś.")

    for i in range(3):
        text = speech.recognize()
        if text:
            tts.speak(f"Powiedziałeś: {text}")
        else:
            tts.speak("Nie usłyszałem, spróbuj ponownie")


if __name__ == "__main__":
    main()
