"""
test_youtube_automation.py — Ręczny test automatyzacji YouTube.

Otwiera osobną przeglądarkę Chrome (profil w data/chrome_profile/), odtwarza
przykładowe wideo i testuje play/pause/fullscreen. Obserwuj okno przeglądarki.

Uruchom:
    python test_youtube_automation.py
"""
import time

from automation.youtube_automation import YouTubeAutomation

# Dowolne, dłuższe wideo do testów (np. muzyka lofi bez końca)
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=jfKfPfyJRdk"


def main():
    yt = YouTubeAutomation()
    yt.initialize()
    yt.open_video(TEST_VIDEO_URL)

    print("⏳ Czekam 5s aż wideo się załaduje...")
    time.sleep(5)

    print("⏸️ Test: pauza")
    yt.pause()
    time.sleep(2)

    print("▶️ Test: wznowienie")
    yt.play()
    time.sleep(2)

    print("🖥️ Test: pełny ekran")
    yt.fullscreen()
    time.sleep(2)

    input("Naciśnij Enter, aby zamknąć przeglądarkę...")
    yt.close()


if __name__ == "__main__":
    main()
