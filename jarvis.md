# 🎤 JARVIS - Asystent Głosowy w Pythonie

> **Uwaga: to jest pierwotna specyfikacja projektu, nie opis aktualnego kodu.**
> Zachowana jako zapis pierwotnych założeń. W trakcie realizacji kilka rzeczy
> zmieniło się świadomie:
>
> | Specyfikacja mówi | W kodzie jest |
> |---|---|
> | spaCy + model `pl_core_news_sm` do NLP | Dopasowanie po rdzeniach, bez spaCy — model 50 MB nie wnosił nic przy dopasowaniu po słowach kluczowych |
> | `discord.py` jako opcja integracji | Wyłącznie PyAutoGUI + pywinauto — wyciszenie osoby „tylko dla mnie" to lokalna funkcja klienta, niedostępna przez API bota |
> | Pomijanie reklamy strzałkami (`ARROW_RIGHT * n`) | Skok przez JavaScript — jedna strzałka to w YouTube 5 sekund, więc `n` strzałek przewijało `5n` sekund |
> | `play_pause()` jako jedna akcja | Rozdzielone `play()` / `pause()` — „odtwórz" nie może zapauzować grającego wideo |
> | Komendy multimedialne (Spotify, głośność) i pogoda | Niezaimplementowane — są w planach w README |
>
> Aktualny opis działania: **[README.md](README.md)**.
> Instrukcja uruchomienia: **[poradnik.md](poradnik.md)**.

---


## Spis Treści
1. [Wstęp](#wstęp)
2. [Wymagania Systemowe](#wymagania-systemowe)
3. [Instalacja](#instalacja)
4. [Konfiguracja](#konfiguracja)
5. [Proces Implementacji](#proces-implementacji)
6. [Struktura Projektu](#struktura-projektu)
7. [Komendy Głosowe](#komendy-głosowe)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Wstęp

**JARVIS** to inteligentny asystent głosowy oparty na Pythonie, który reaguje na komendę głosową "**Dżarwis**" i wykonuje zdefiniowane akcje takie jak:
- ⏭️ Pomijanie reklam na YouTube
- ▶️/⏸️ Sterowanie odtwarzaniem
- 🎙️ Kontrola Discord (wyciszanie, przełączanie kanałów)
- 🎵 Obsługa multimediów
- 💻 Automatyzacja aplikacji

### Architektura
```
Mikrofon → Speech Recognition → NLP Parser → Execution Engine → TTS Response
```

### Zalety
✅ Obsługa polskiego języka naturalnego  
✅ Działanie offline (opcja Vosk)  
✅ Rozszerzone API dla developerów  
✅ GUI do kontroli aplikacji  
✅ Logowanie i debugging  

---

## Wymagania Systemowe

### Hardware
- **Mikrofon** (jakikolwiek będzie, najlepiej USB)
- **Głośniki/Słuchawki** (dla odpowiedzi TTS)
- **Procesor**: min. Intel i5 / AMD Ryzen 5 (dla płynnego działania)
- **RAM**: min. 4GB
- **Dysk**: min. 2GB (dla modeli offline)

### System Operacyjny
- **Windows 10/11** (głównie testowane)
- **macOS 10.14+**
- **Linux** (Ubuntu 20.04+)

### Wersja Pythona
- **Python 3.10** lub wyższa
- **pip** (manager pakietów)
- **virtualenv** (izolowane środowisko)

---

## Instalacja

### Krok 1: Przygotowanie Środowiska

#### Na Windows:
```bash
# 1. Zainstaluj Python 3.10+ z https://www.python.org/
# Upewnij się, że zaznaczysz "Add Python to PATH"

# 2. Otwórz Command Prompt (cmd) lub PowerShell

# 3. Przejdź do folderu projektu
cd C:\Users\YourUsername\Desktop\jarvis

# 4. Utwórz wirtualne środowisko
python -m venv venv

# 5. Aktywuj środowisko
venv\Scripts\activate

# Powinien pojawić się prefix (venv) w konsoli
```

#### Na macOS/Linux:
```bash
# 1. Zainstaluj Python
# macOS: brew install python3.10
# Linux: sudo apt install python3.10 python3-pip

# 2. Przejdź do folderu projektu
cd ~/jarvis

# 3. Utwórz wirtualne środowisko
python3 -m venv venv

# 4. Aktywuj środowisko
source venv/bin/activate
```

### Krok 2: Instalacja Zależności

```bash
# Upewnij się, że wirtualne środowisko jest aktywne (venv)

# Zainstaluj wszystkie wymagane pakiety
pip install -r requirements.txt

# To instaluje:
# - SpeechRecognition (Google API lub offline)
# - pyttsx3 (Text-to-Speech offline)
# - Selenium (automatyzacja przeglądarki)
# - pyautogui (sterowanie myszą/klawiaturą)
# - discord.py (integracja Discord)
# - spacy (NLP do parsowania komend)
# - pydub (przetwarzanie audio)
# - PyQt6 (GUI - opcjonalnie)
```

### Krok 3: Dodatkowe Zależności Systemowe

#### Windows:
```bash
# Zainstaluj FFmpeg (do przetwarzania audio)
# Pobierz z https://ffmpeg.org/download.html
# LUB użyj chocolatey:
choco install ffmpeg

# Zainstaluj Chrome (do Selenium)
# Pobierz z https://www.google.com/chrome/
```

#### macOS:
```bash
# Zainstaluj FFmpeg
brew install ffmpeg

# Zainstaluj Chrome
brew install --cask google-chrome
```

#### Linux (Ubuntu):
```bash
# Zainstaluj FFmpeg
sudo apt install ffmpeg

# Zainstaluj Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### Krok 4: Pobierz Modele Spacy

```bash
# Pobierz model polskiego języka dla NLP
python -m spacy download pl_core_news_sm

# Pobierz model angielskiego (jako fallback)
python -m spacy download en_core_web_sm
```

---

## Konfiguracja

### Plik `config.py`

Utwórz plik `config.py` w głównym katalogu projektu:

```python
# config.py
import os

# ============= SPEECH RECOGNITION =============
SPEECH_ENGINE = "google"  # "google" lub "vosk" (offline)
RECOGNITION_LANGUAGE = "pl-PL"  # Polski
MICROPHONE_INDEX = None  # None = domyślny mikrofon
NOISE_THRESHOLD = 50  # Próg szumu (0-100)

# ============= TTS (TEXT-TO-SPEECH) =============
TTS_ENGINE = "pyttsx3"  # "pyttsx3" lub "gtts"
TTS_LANGUAGE = "pl"  # Polski
TTS_RATE = 150  # Szybkość mowy (100-200)
TTS_VOLUME = 0.9  # Głośność (0-1)

# ============= ACTIVATION KEYWORD =============
ACTIVATION_KEYWORD = "dżarwis"  # Słowo aktywacyjne
ACTIVATION_KEYWORDS_VARIANTS = ["jarvis", "dżarwis", "dzharvis", "jarvisa"]

# ============= YOUTUBE SETTINGS =============
YOUTUBE_SKIP_AD_TIME = 30  # Sekund do pominięcia (30s = typowa reklama)
YOUTUBE_SKIP_METHOD = "keyboard"  # "keyboard" lub "click"
YOUTUBE_BROWSER = "chrome"  # "chrome", "firefox", "edge"

# ============= DISCORD SETTINGS =============
DISCORD_AUTO_DETECT = True  # Auto-detect okna Discord
DISCORD_TIMEOUT = 5  # Timeout w sekundach

# ============= LOGGING =============
LOG_LEVEL = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
LOG_FILE = "logs/jarvis.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB

# ============= PATHS =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Tworzenie folderów jeśli nie istnieją
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ============= API KEYS (jeśli Google Cloud) =============
# GOOGLE_CREDENTIALS_PATH = "path/to/google-credentials.json"
```

### Plik `requirements.txt`

```
# Speech Recognition
SpeechRecognition==3.10.0
pyaudio==0.2.13
vosk==0.3.32
pocketsphinx==5.2

# Text-to-Speech
pyttsx3==2.90
gTTS==2.4.0

# Browser Automation
selenium==4.15.2
webdriver-manager==4.0.1
pyautogui==0.9.53

# Discord Integration
discord.py==2.3.2

# NLP
spacy==3.7.2
nltk==3.8.1

# Audio Processing
pydub==0.25.1

# GUI
PyQt6==6.6.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0
pywin32==305; sys_platform == 'win32'

# Logging & Debugging
colorlog==6.8.0
```

---

## Proces Implementacji

### FAZA 1: Fundacja (Speech Recognition + TTS)

#### Krok 1.1: Testowanie Mikrofonu

Utwórz plik `test_microphone.py`:

```python
# test_microphone.py
import speech_recognition as sr

def test_microphone():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Testowanie mikrofonu...")
        print("Mów coś...")
        
        try:
            audio = recognizer.listen(source, timeout=5)
            print("✅ Mikrofon działa! Audio nagrane.")
            
            # Test rozpoznawania
            text = recognizer.recognize_google(audio, language="pl-PL")
            print(f"📝 Rozpoznany tekst: {text}")
            
        except sr.UnknownValueError:
            print("❌ Nie mogłem zrozumieć audio")
        except sr.RequestError as e:
            print(f"❌ Błąd serwisu: {e}")

if __name__ == "__main__":
    test_microphone()
```

Uruchom:
```bash
python test_microphone.py
```

#### Krok 1.2: Implementacja Speech Recognition Engine

Utwórz plik `voice/speech_engine.py`:

```python
# voice/speech_engine.py
import speech_recognition as sr
import threading
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

class SpeechEngine:
    def __init__(self, language="pl-PL", engine="google"):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.engine = engine
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.on_recognized = None
        
    def recognize(self, timeout=10) -> Optional[str]:
        """Rozpoznaje jedną komendy głosową"""
        try:
            with self.microphone as source:
                # Kalibracja szumu
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                print("🎤 Słucham...")
                audio = self.recognizer.listen(source, timeout=timeout)
                
            # Rozpoznawanie
            if self.engine == "google":
                text = self.recognizer.recognize_google(audio, language=self.language)
            elif self.engine == "vosk":
                # Implementacja offline
                text = self.recognizer.recognize_vosk(audio, language=self.language)
            
            print(f"📝 Rozpoznano: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            print("❌ Nie zrozumiałem, spróbuj ponownie")
            return None
        except sr.RequestError as e:
            print(f"❌ Błąd API: {e}")
            return None
            
    def start_listening_async(self, callback: Callable):
        """Słuchanie w tle"""
        self.is_listening = True
        self.on_recognized = callback
        
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
        
    def _listen_loop(self):
        """Pętla nasłuchiwania"""
        while self.is_listening:
            text = self.recognize()
            if text and self.on_recognized:
                self.on_recognized(text)
                
    def stop_listening(self):
        """Zatrzymaj nasłuchiwanie"""
        self.is_listening = False
```

#### Krok 1.3: Implementacja Text-to-Speech

Utwórz plik `voice/tts_engine.py`:

```python
# voice/tts_engine.py
import pyttsx3
import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self, language="pl", rate=150, volume=0.9):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.language = language
        
        # Ustaw język polskiego głosu
        voices = self.engine.getProperty('voices')
        # Spróbuj znaleźć polski głos
        for voice in voices:
            if 'Polish' in voice.name or 'pl' in voice.languages:
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text: str, wait=True):
        """Mów tekst synchronicznie lub asynchronicznie"""
        print(f"🔊 Mówię: {text}")
        self.engine.say(text)
        
        if wait:
            self.engine.runAndWait()
        else:
            thread = threading.Thread(target=self.engine.runAndWait, daemon=True)
            thread.start()
    
    def speak_async(self, text: str):
        """Mów tekst asynchronicznie (nie czekaj)"""
        self.speak(text, wait=False)
    
    def stop(self):
        """Zatrzymaj mowę"""
        self.engine.stop()
```

#### Krok 1.4: Test - Połączenie Speech + TTS

Utwórz plik `test_voice_loop.py`:

```python
# test_voice_loop.py
from voice.speech_engine import SpeechEngine
from voice.tts_engine import TTSEngine
import config

def main():
    speech = SpeechEngine(language=config.RECOGNITION_LANGUAGE)
    tts = TTSEngine(language=config.TTS_LANGUAGE)
    
    tts.speak("Cześć, jestem Jarvis. Powiedz coś.")
    
    for i in range(3):
        text = speech.recognize(timeout=5)
        if text:
            tts.speak(f"Powiedziałeś: {text}")
        else:
            tts.speak("Nie usłyszałem, spróbuj ponownie")

if __name__ == "__main__":
    main()
```

---

### FAZA 2: Logika Komend (NLP Parser)

#### Krok 2.1: Command Parser

Utwórz plik `commands/command_parser.py`:

```python
# commands/command_parser.py
import spacy
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class CommandParser:
    def __init__(self):
        self.nlp = spacy.load("pl_core_news_sm")
        self.commands_db = self._init_commands()
        
    def _init_commands(self) -> Dict:
        """Baza komend z wariantami"""
        return {
            "youtube_skip_ad": {
                "keywords": ["pomiń", "reklamę", "ad", "skip"],
                "examples": ["pomiń reklamę", "skip ad"],
                "priority": 10
            },
            "youtube_play": {
                "keywords": ["odtwórz", "play", "start"],
                "examples": ["odtwórz", "zacznij"],
                "priority": 9
            },
            "youtube_pause": {
                "keywords": ["pauza", "pause", "zatrzymaj", "stop"],
                "examples": ["pauza", "zatrzymaj"],
                "priority": 9
            },
            "discord_mute": {
                "keywords": ["wycisz", "mikrofon", "mute"],
                "examples": ["wycisz mikrofon", "mute"],
                "priority": 8
            },
            "discord_unmute": {
                "keywords": ["włącz", "mikrofon", "unmute"],
                "examples": ["włącz mikrofon"],
                "priority": 8
            },
            "discord_switch_channel": {
                "keywords": ["przełącz", "kanał", "channel", "dołącz"],
                "examples": ["przełącz na kanał gaming"],
                "priority": 7
            }
        }
    
    def parse(self, text: str) -> Tuple[str, float, Dict]:
        """
        Parsuje tekst i zwraca (komenda, confidence, parametry)
        """
        text = text.lower().strip()
        doc = self.nlp(text)
        
        best_match = None
        best_score = 0
        
        # Szukaj najlepszego dopasowania
        for command_name, command_info in self.commands_db.items():
            score = self._calculate_match_score(text, command_info)
            
            if score > best_score:
                best_score = score
                best_match = command_name
        
        if best_score > 0.3:  # Próg zaufania
            return best_match, best_score, self._extract_parameters(text, best_match)
        
        return None, 0, {}
    
    def _calculate_match_score(self, text: str, command_info: Dict) -> float:
        """Oblicza score dopasowania"""
        score = 0
        keywords = command_info.get("keywords", [])
        
        for keyword in keywords:
            if keyword in text:
                score += 0.5
        
        return min(score / len(keywords) if keywords else 0, 1.0)
    
    def _extract_parameters(self, text: str, command: str) -> Dict:
        """Wyciąga parametry z tekstu"""
        params = {}
        
        if "kanał" in text or "channel" in text:
            # Wyciągnij nazwę kanału
            words = text.split()
            for i, word in enumerate(words):
                if word in ["kanał", "channel"] and i + 1 < len(words):
                    params["channel_name"] = words[i + 1]
        
        if any(x in text for x in ["sekund", "seconds"]):
            # Wyciągnij liczbę
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                params["seconds"] = int(numbers[0])
        
        return params
```

#### Krok 2.2: Command Executor

Utwórz plik `commands/command_executor.py`:

```python
# commands/command_executor.py
from typing import Dict, Callable
from voice.tts_engine import TTSEngine
import logging

logger = logging.getLogger(__name__)

class CommandExecutor:
    def __init__(self):
        self.tts = TTSEngine()
        self.handlers = self._init_handlers()
        
    def _init_handlers(self) -> Dict[str, Callable]:
        """Rejestruj handlery komend"""
        return {
            "youtube_skip_ad": self.handle_youtube_skip_ad,
            "youtube_play": self.handle_youtube_play,
            "youtube_pause": self.handle_youtube_pause,
            "discord_mute": self.handle_discord_mute,
            "discord_unmute": self.handle_discord_unmute,
            "discord_switch_channel": self.handle_discord_switch_channel,
        }
    
    def execute(self, command: str, params: Dict) -> bool:
        """Wykonaj komendę"""
        if command not in self.handlers:
            self.tts.speak(f"Nie znam komendy {command}")
            return False
        
        try:
            self.handlers[command](params)
            return True
        except Exception as e:
            logger.error(f"Błąd przy wykonywaniu {command}: {e}")
            self.tts.speak("Coś poszło nie tak")
            return False
    
    # YouTube Handlers
    def handle_youtube_skip_ad(self, params: Dict):
        """Pomiń reklamę na YouTube"""
        self.tts.speak("Pomijam reklamę")
        # Implementacja w FAZIE 3
        print("⏭️ Pomijanie reklamy...")
    
    def handle_youtube_play(self, params: Dict):
        self.tts.speak("Odtwarzam")
        print("▶️ Odtwarzanie...")
    
    def handle_youtube_pause(self, params: Dict):
        self.tts.speak("Pauza")
        print("⏸️ Pauza...")
    
    # Discord Handlers
    def handle_discord_mute(self, params: Dict):
        self.tts.speak("Wyciszam mikrofon")
        print("🔇 Wyciszanie mikrofonu...")
    
    def handle_discord_unmute(self, params: Dict):
        self.tts.speak("Włączam mikrofon")
        print("🔊 Włączanie mikrofonu...")
    
    def handle_discord_switch_channel(self, params: Dict):
        channel = params.get("channel_name", "kanał")
        self.tts.speak(f"Przełączam na {channel}")
        print(f"🔄 Przełączanie na {channel}...")
```

---

### FAZA 3: YouTube Automation

#### Krok 3.1: YouTube Automation Engine

Utwórz plik `automation/youtube_automation.py`:

```python
# automation/youtube_automation.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging

logger = logging.getLogger(__name__)

class YouTubeAutomation:
    def __init__(self, browser="chrome"):
        self.browser = browser
        self.driver = None
        
    def initialize(self):
        """Inicjalizuj przeglądarke"""
        if self.browser == "chrome":
            self.driver = webdriver.Chrome()
        elif self.browser == "firefox":
            self.driver = webdriver.Firefox()
        else:
            self.driver = webdriver.Edge()
    
    def close(self):
        if self.driver:
            self.driver.quit()
    
    def skip_ad(self, skip_time=30):
        """Pomiń reklamę na YouTube"""
        try:
            # Spróbuj znaleźć przycisk Skip Ad
            skip_button = self.driver.find_element(By.CLASS_NAME, "ytp-ad-skip-button")
            skip_button.click()
            logger.info("✅ Reklama pominięta")
            return True
        except:
            # Jeśli nie ma Skip Ad, przesuń video do przodu
            self.driver.find_element(By.TAG_NAME, "video").send_keys(Keys.ARROW_RIGHT * skip_time)
            logger.info(f"⏭️ Przesunięto o {skip_time} sekund")
            return True
    
    def play_pause(self):
        """Odtwórz/pauza"""
        try:
            video = self.driver.find_element(By.TAG_NAME, "video")
            video.send_keys(Keys.SPACE)
            logger.info("▶️/⏸️ Play/Pause")
            return True
        except Exception as e:
            logger.error(f"Błąd: {e}")
            return False
    
    def next_video(self):
        """Następne wideo"""
        try:
            next_btn = self.driver.find_element(By.CLASS_NAME, "ytp-next-button")
            next_btn.click()
            logger.info("⏭️ Następne wideo")
            return True
        except:
            logger.error("Nie znaleziono przycisku next")
            return False
    
    def full_screen(self):
        """Pełny ekran"""
        try:
            video = self.driver.find_element(By.TAG_NAME, "video")
            video.send_keys("f")
            logger.info("🖥️ Pełny ekran")
            return True
        except:
            return False
```

---

### FAZA 4: Discord Integration

#### Krok 4.1: Discord Automation

Utwórz plik `automation/discord_automation.py`:

```python
# automation/discord_automation.py
import pyautogui
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DiscordAutomation:
    def __init__(self):
        self.discord_window = None
        
    def find_discord_window(self) -> bool:
        """Znajdź okno Discord"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('Discord')
            if windows:
                self.discord_window = windows[0]
                return True
        except:
            pass
        return False
    
    def focus_discord(self):
        """Skoncentruj się na oknie Discord"""
        if self.discord_window:
            self.discord_window.activate()
            time.sleep(0.5)
    
    def toggle_mute(self):
        """Włącz/wyłącz wyciszenie mikrofonu"""
        self.focus_discord()
        # Domyślny shortcut Discord: Ctrl+M
        pyautogui.hotkey('ctrl', 'm')
        logger.info("🎙️ Toggle Mute")
    
    def toggle_deafen(self):
        """Włącz/wyłącz wyciszenie dźwięku"""
        self.focus_discord()
        # Domyślny shortcut Discord: Ctrl+D
        pyautogui.hotkey('ctrl', 'd')
        logger.info("🔊 Toggle Deafen")
    
    def switch_channel(self, channel_name: str):
        """Przełącz na inny kanał"""
        self.focus_discord()
        # Ctrl+K otwiera command palette
        pyautogui.hotkey('ctrl', 'k')
        time.sleep(0.3)
        pyautogui.typewrite(channel_name, interval=0.05)
        time.sleep(0.2)
        pyautogui.press('enter')
        logger.info(f"🔄 Switched to {channel_name}")
```

---

### FAZA 5: GUI (Interfejs Graficzny)

#### Krok 5.1: PyQt6 GUI

Utwórz plik `gui/main_window.py`:

```python
# gui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from voice.speech_engine import SpeechEngine
from commands.command_parser import CommandParser
from commands.command_executor import CommandExecutor
import logging

logger = logging.getLogger(__name__)

class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎤 JARVIS - Voice Assistant")
        self.setGeometry(100, 100, 900, 600)
        
        self.speech_engine = SpeechEngine()
        self.parser = CommandParser()
        self.executor = CommandExecutor()
        
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Stwórz interfejs"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🎤 JARVIS - Asystent Głosowy")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Status
        self.status_label = QLabel("Status: Gotowy")
        self.status_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_listen = QPushButton("🎤 Słuchaj")
        self.btn_listen.clicked.connect(self.start_listening)
        btn_layout.addWidget(self.btn_listen)
        
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self.stop_listening)
        btn_layout.addWidget(self.btn_stop)
        
        layout.addLayout(btn_layout)
        
        # Text Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier", 11))
        layout.addWidget(self.text_edit)
        
        main_widget.setLayout(layout)
    
    def apply_styles(self):
        """Stosuj style CSS"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTextEdit {
                background-color: #1a252f;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
            }
        """)
    
    def start_listening(self):
        self.status_label.setText("Status: Słucham...")
        self.status_label.setStyleSheet("color: #2ecc71;")
        
        def on_recognized(text):
            command, confidence, params = self.parser.parse(text)
            
            self.text_edit.append(f"\n🎤 Rozpoznano: {text}")
            self.text_edit.append(f"📊 Pewność: {confidence:.2%}")
            
            if command:
                self.text_edit.append(f"✅ Komenda: {command}")
                self.executor.execute(command, params)
            else:
                self.text_edit.append("❌ Komenda nieznana")
            
            self.status_label.setText("Status: Gotowy")
            self.status_label.setStyleSheet("color: white;")
        
        self.speech_engine.on_recognized = on_recognized
        text = self.speech_engine.recognize()
        if text:
            on_recognized(text)
    
    def stop_listening(self):
        self.speech_engine.stop_listening()
        self.status_label.setText("Status: Zatrzymano")
        self.status_label.setStyleSheet("color: #e74c3c;")
```

#### Krok 5.2: Główny plik aplikacji

Utwórz plik `main.py`:

```python
# main.py
import sys
import logging
from PyQt6.QtWidgets import QApplication
from gui.main_window import JarvisWindow
import config

# Konfiguruj logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Uruchamianie JARVIS...")
    
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    
    logger.info("✅ JARVIS gotowy!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

## Struktura Projektu

```
jarvis/
│
├── main.py                    # Główna aplikacja
├── config.py                  # Konfiguracja
├── requirements.txt           # Zależności
├── README.md                  # Dokumentacja
│
├── voice/
│   ├── __init__.py
│   ├── speech_engine.py       # Speech Recognition
│   ├── tts_engine.py          # Text-to-Speech
│   └── voice_config.py        # Konfiguracja dźwięku
│
├── commands/
│   ├── __init__.py
│   ├── command_parser.py      # Parser NLP
│   ├── command_executor.py    # Executor
│   ├── youtube_commands.py
│   ├── discord_commands.py
│   └── system_commands.py
│
├── automation/
│   ├── __init__.py
│   ├── youtube_automation.py  # YouTube Bot
│   ├── discord_automation.py  # Discord Bot
│   └── keyboard_mouse.py      # PyAutoGUI wrapper
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # PyQt6 GUI
│   └── settings_panel.py      # Ustawienia
│
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Custom logger
│   ├── helpers.py             # Funkcje pomocnicze
│   └── constants.py           # Stałe
│
├── tests/
│   ├── test_speech.py
│   ├── test_commands.py
│   └── test_automation.py
│
├── logs/                      # Logowanie
│   └── jarvis.log
│
└── data/                      # Dane aplikacji
    ├── commands_db.json
    └── user_preferences.json
```

---

## Komendy Głosowe

### YouTube
| Komenda | Akcja |
|---------|-------|
| "Dżarwis, pomiń reklamę" | Pomiń aktualną reklamę |
| "Dżarwis, odtwórz" | Wznów odtwarzanie |
| "Dżarwis, pauza" | Wstrzymaj odtwarzanie |
| "Dżarwis, następne wideo" | Przejdź do następnego wideo |
| "Dżarwis, pełny ekran" | Uruchom pełny ekran |

### Discord
| Komenda | Akcja |
|---------|-------|
| "Dżarwis, wycisz mikrofon" | Wycisz/włącz mikrofon |
| "Dżarwis, wycisz dźwięk" | Wycisz/włącz dźwięk |
| "Dżarwis, przełącz na [kanał]" | Przejdź do kanału |
| "Dżarwis, opuść kanał" | Opuść aktualny kanał |

### System
| Komenda | Akcja |
|---------|-------|
| "Dżarwis, jaka godzina" | Powiedz godzinę |
| "Dżarwis, jaka pogoda" | Powiedz pogodę |
| "Dżarwis, wyłącz się" | Zamknij aplikację |

---

## Troubleshooting

### Mikrofon nie jest rozpoznawany
```bash
# Windows - zainstaluj PyAudio
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt install portaudio19-dev
pip install pyaudio
```

### Speech Recognition nie działa
```python
# Sprawdź połączenie internetowe (jeśli używasz Google API)
# Lub pobierz modele Vosk:
# https://github.com/alphacep/vosk-models

# Test
python test_microphone.py
```

### YouTube Automation nie działą
```bash
# Zaktualizuj Chrome i ChromeDriver
# WebDriver Manager powinien automatycznie pobrać właściwą wersję
pip install --upgrade webdriver-manager

# Jeśli dalej nie działa, sprawdź czy Chrome jest zainstalowany
```

### Discord integracja nie działa
```python
# Upewnij się, że okno Discord jest widoczne
# Spróbuj zainstalować pygetwindow
pip install pygetwindow

# Na Linuksie może być potrzebne:
pip install python-xlib
```

---

## FAQ

**P: Czy mogę używać inny mikrofon niż domyślny?**
A: Tak, w `config.py` ustaw `MICROPHONE_INDEX` na numer urządzenia:
```python
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i))
# Następnie ustaw MICROPHONE_INDEX = twój_index
```

**P: Czy aplikacja pracuje offline?**
A: Częściowo. Speech Recognition (Google API) wymaga internetu, ale możesz użyć Vosk. TTS (pyttsx3) działa offline.

**P: Czy mogę zmienić aktywacyjne słowo "Dżarwis"?**
A: Oczywiście! W `config.py` zmień `ACTIVATION_KEYWORD`.

**P: Jak dodać nową komendę?**
A: 
1. Dodaj ją w `command_parser.py` - `_init_commands()`
2. Dodaj handler w `command_executor.py`
3. Dodaj akcję w `automation/`

**P: Czy mogę to uruchomić na systemach innych niż Windows?**
A: Tak! Aplikacja jest wieloplatformowa. PyAutoGUI może wymagać dodatkowych uprawnień na Linux/macOS.

---

## Licencja
MIT

## Autor
Created with ❤️ by Your Name

---

**Gotowy do startu?** Zainstaluj zależności i uruchom `python main.py` 🚀
