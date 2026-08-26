"""
test_microphone.py — Szybki test: nagraj jedno zdanie i rozpoznaj je.

Uruchom:
    python test_microphone.py
"""
from voice.speech_engine import SpeechEngine


def test_microphone():
    engine = SpeechEngine()

    print("🎤 Testowanie mikrofonu...")
    print("Mów coś (masz 5 sekund na rozpoczęcie)...")

    text = engine.recognize()

    if text:
        print(f"✅ Mikrofon działa! Rozpoznany tekst: {text}")
    else:
        print("❌ Nie udało się rozpoznać mowy — sprawdź mikrofon / połączenie internetowe.")


if __name__ == "__main__":
    test_microphone()
