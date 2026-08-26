"""
main.py — Punkt wejścia aplikacji JARVIS.

    python main.py                 # uruchamia okno aplikacji
    python main.py --mikrofony     # wypisuje mikrofony i ich indeksy
"""
import sys

from utils.logger import get_logger

logger = get_logger(__name__)


def list_microphones() -> int:
    """Wypisuje dostępne mikrofony — indeks wpisuje się do MICROPHONE_INDEX w config.py."""
    try:
        from voice.speech_engine import SpeechEngine
    except ImportError as e:
        print(f"❌ Brak biblioteki rozpoznawania mowy: {e}")
        print("   Zainstaluj zależności:  pip install -r requirements.txt")
        return 1

    try:
        names = SpeechEngine.list_microphones()
    except Exception as e:
        print(f"❌ Nie udało się odczytać listy mikrofonów: {e}")
        return 1

    if not names:
        print("❌ System nie zgłasza żadnego mikrofonu.")
        return 1

    print("🎤 Dostępne mikrofony (indeks -> nazwa):\n")
    for index, name in enumerate(names):
        print(f"  {index:>3}  {name}")
    print("\nWybrany indeks wpisz w config.py jako MICROPHONE_INDEX.")
    return 0


def run_app() -> int:
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        print("❌ Brak PyQt6 — interfejs graficzny nie może wystartować.")
        print("   Zainstaluj zależności:  pip install -r requirements.txt")
        return 1

    from gui.main_window import JarvisWindow

    logger.info("🚀 Uruchamianie JARVIS...")
    app = QApplication(sys.argv)

    try:
        window = JarvisWindow()
    except OSError as e:
        # Najczęstsza przyczyna: brak mikrofonu albo niezainstalowany PyAudio.
        logger.error(f"❌ Problem z urządzeniem audio: {e}")
        print("\n❌ Nie udało się przygotować wejścia audio.")
        print("   Sprawdź, czy mikrofon jest podłączony:  python main.py --mikrofony")
        print("   Jeśli brakuje PyAudio:  pip install pipwin && pipwin install pyaudio")
        return 1

    window.show()
    logger.info("✅ JARVIS gotowy!")
    return app.exec()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("--mikrofony", "--microphones", "-m"):
        return list_microphones()
    return run_app()


if __name__ == "__main__":
    sys.exit(main())
