"""
config.py — Globalna konfiguracja JARVIS.

Decyzje architektoniczne (ustalone z użytkownikiem):
- Speech Recognition: darmowy, nieoficjalny endpoint Google przez
  SpeechRecognition.recognize_google() — bez klucza API.
- TTS: pyttsx3 (offline, głosy systemowe).
"""
import os

# ============= SPEECH RECOGNITION =============
SPEECH_ENGINE = "google"  # "google" (darmowy, wymaga internetu) lub "vosk" (offline, do dodania później)
RECOGNITION_LANGUAGE = "pl-PL"  # Polski
MICROPHONE_INDEX = None  # None = domyślny mikrofon systemowy
NOISE_THRESHOLD = 50  # Próg szumu (0-100), używany do kalibracji ambient noise
LISTEN_TIMEOUT = 5  # Sekund oczekiwania na rozpoczęcie mowy
PHRASE_TIME_LIMIT = 10  # Maks. długość jednej wypowiedzi w sekundach

# ============= TTS (TEXT-TO-SPEECH) =============
TTS_ENGINE = "pyttsx3"  # offline
TTS_LANGUAGE = "pl"  # Polski
TTS_RATE = 150  # Szybkość mowy (100-200)
TTS_VOLUME = 0.9  # Głośność (0-1)

# ============= ACTIVATION KEYWORD =============
ACTIVATION_KEYWORD = "dżarwis"  # Słowo aktywacyjne
ACTIVATION_KEYWORDS_VARIANTS = ["jarvis", "dżarwis", "dzharvis", "jarvisa"]

# ============= YOUTUBE SETTINGS (Faza 3) =============
YOUTUBE_SKIP_AD_TIME = 30  # Sekund do pominięcia (30s = typowa reklama)
YOUTUBE_SKIP_METHOD = "keyboard"  # "keyboard" lub "click"
YOUTUBE_BROWSER = "chrome"  # Osobna, zautomatyzowana przeglądarka Selenium

# ============= DISCORD SETTINGS (Faza 4) =============
# Sterowanie przez PyAutoGUI na już otwartym kliencie Discord użytkownika.
DISCORD_AUTO_DETECT = True  # Auto-detect okna Discord
DISCORD_TIMEOUT = 5  # Timeout w sekundach
DISCORD_WINDOW_TITLE = "Discord"  # Fragment tytułu okna używany przez pygetwindow

# UWAGA: Discord nie ma domyślnych globalnych skrótów do mute/deafen — trzeba je
# ręcznie skonfigurować identycznie jak poniżej w:
# Discord > Ustawienia użytkownika > Głos i wideo > Skróty klawiszowe
# Dla obu wpisów zaznacz "Ten skrót działa globalnie" (This keybind works globally),
# żeby zadziałało nawet gdy Discord nie jest aktywnym oknem.
DISCORD_MUTE_HOTKEY = ["ctrl", "shift", "m"]  # Toggle Mute (własny mikrofon)
DISCORD_DEAFEN_HOTKEY = ["ctrl", "shift", "d"]  # Toggle Deafen (własny dźwięk)

# UI Automation (pywinauto) — mute konkretnej osoby "tylko dla mnie" i przełączanie
# widoku na czyjś udostępniony ekran. WYMAGA włączenia w Discordzie:
# Ustawienia użytkownika > Dostępność > "Obsługa czytnika ekranu" (Screen Reader
# Support) — inaczej elementy UI nie mają nazw czytelnych dla automatyzacji.
# Etykiety menu kontekstowego zależą od języka klienta Discord — obie sprawdzane.
DISCORD_MUTE_MENU_LABELS = ["Wycisz", "Mute"]
DISCORD_UIA_SEARCH_TIMEOUT = 5  # sekund na odnalezienie elementu w drzewie UI

# ============= LOGGING =============
LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
LOG_FILE_NAME = "jarvis.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB

# ============= PATHS =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(LOG_DIR, LOG_FILE_NAME)

# Tworzenie folderów jeśli nie istnieją
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
