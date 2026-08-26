"""
test_voice_loop.py — Test pętli: JARVIS mówi, słucha, odpowiada (3 razy).

    python test_voice_loop.py
"""
from voice.speech_engine import SpeechEngine
from voice.tts_engine import TTSEngine

ROUNDS = 3


def main() -> int:
    tts = TTSEngine()
    if not tts.available:
        print("❌ Silnik mowy nie wystartował — sprawdź instalację pyttsx3.")
        return 1

    try:
        speech = SpeechEngine()
    except OSError as e:
        print(f"❌ Nie udało się otworzyć mikrofonu: {e}")
        tts.shutdown()
        return 1

    try:
        tts.speak("Cześć, jestem Jarvis. Powiedz coś.")
        for _ in range(ROUNDS):
            text = speech.recognize()
            tts.speak(f"Powiedziałeś: {text}" if text else "Nie usłyszałem, spróbuj ponownie")
    finally:
        tts.shutdown()  # bez tego wątek mowy zostaje aktywny
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
