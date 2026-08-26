"""
test_microphone.py — Szybki test: nagraj jedno zdanie i rozpoznaj je.

    python test_microphone.py
"""
from voice.speech_engine import SpeechEngine


def main() -> int:
    try:
        engine = SpeechEngine()
    except OSError as e:
        print(f"❌ Nie udało się otworzyć mikrofonu: {e}")
        print("   Lista urządzeń:  python main.py --mikrofony")
        return 1

    print("🎤 Testowanie mikrofonu — mów po polsku (masz 5 sekund na start)...")
    text = engine.recognize()

    if text:
        print(f"✅ Działa. Rozpoznany tekst: {text}")
        return 0

    print("❌ Nic nie rozpoznano.")
    print("   Sprawdź: czy mikrofon jest domyślnym urządzeniem, czy jest internet")
    print("   (rozpoznawanie idzie przez Google), i czy nie mówisz za cicho.")
    print("   Lista urządzeń:  python main.py --mikrofony")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
