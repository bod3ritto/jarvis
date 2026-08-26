# 🎤 JARVIS - Inteligentny Asystent Głosowy

> Głosowy asystent AI napisany w Pythonie z obsługą YouTube, Discord i wielu innych aplikacji

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Development-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 🚀 Szybki Start

```bash
# 1. Klonuj repo
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# 2. Zainstaluj Python 3.10+
# https://www.python.org/

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Pobierz modele NLP
python -m spacy download pl_core_news_sm

# 5. Uruchom aplikację
python main.py
```

---

## 🎯 Główne Cechy

✨ **Speech Recognition** - Rozpoznawanie mowy w języku polskim (Google API + Vosk offline)

🔊 **Text-to-Speech** - Naturalne odpowiedzi głosowe aplikacji

⏭️ **YouTube Automation** - Inteligentne omijanie reklam, sterowanie odtwarzaniem

🎙️ **Discord Control** - Wyciszanie mikrofonu, przełączanie kanałów komendą głosową

🤖 **NLP Parser** - Zaawansowane przetwarzanie języka naturalnego

🎨 **GUI** - Nowoczesny interfejs graficzny z PyQt6

⚙️ **Customizable** - Łatwe dodawanie nowych komend i integracji

---

## 📋 Wymagania Systemowe

### Hardware
- 🎙️ Mikrofon USB (opcjonalnie - działa z wbudowanym)
- 🔊 Głośniki/Słuchawki
- 💻 Procesor: Intel i5 / AMD Ryzen 5 (min.)
- 💾 RAM: 4GB (min.), 8GB+ (rekomendowany)
- 📀 Dysk: 2GB wolnego miejsca

### Software
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 20.04+
- **Python**: 3.10 lub wyższa
- **Chrome/Chromium** (dla YouTube automation)
- **FFmpeg** (do przetwarzania audio)

### Instalacja Zależności Systemowych

**Windows (PowerShell as Admin):**
```powershell
# FFmpeg
choco install ffmpeg

# Chrome (jeśli brak)
choco install googlechrome
```

**macOS (Homebrew):**
```bash
brew install ffmpeg google-chrome
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install -y ffmpeg chromium-browser
wget -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo apt-get install google-chrome-stable
```

---

## 📦 Instalacja Wariantów

### Option A: Full Installation (Rekomendowany)
```bash
pip install -r requirements.txt
python -m spacy download pl_core_news_sm
```

### Option B: Minimalna instalacja (bez GUI)
```bash
pip install SpeechRecognition pyttsx3 pyautogui discord.py spacy
```

### Option C: Offline Mode (bez Google API)
```bash
pip install -r requirements.txt
# Pobierz Vosk modele: https://github.com/alphacep/vosk-models/releases
```

---

## 🎤 Komendy Głosowe

### 🎬 YouTube
```
"Dżarwis, pomiń reklamę"     → ⏭️ Pomiń aktualną reklamę (30s)
"Dżarwis, pomiń [X] sekund"  → ⏭️ Pomiń o X sekund
"Dżarwis, odtwórz"           → ▶️ Wznów odtwarzanie
"Dżarwis, pauza"             → ⏸️ Wstrzymaj odtwarzanie
"Dżarwis, następne wideo"    → ⏩ Następne wideo
"Dżarwis, poprzednie"        → ⏪ Poprzednie wideo
"Dżarwis, pełny ekran"       → 🖥️ Uruchom pełny ekran
"Dżarwis, zmień prędkość"    → ⚡ Zmień szybkość odtwarzania
```

### 💬 Discord
```
"Dżarwis, wycisz mikrofon"      → 🎙️ Toggle mute mikrofonu
"Dżarwis, włącz mikrofon"       → 🔊 Włącz mikrofon
"Dżarwis, wycisz dźwięk"        → 🔇 Toggle deafen
"Dżarwis, przełącz na [kanał]"  → 🔄 Przejdź do kanału
"Dżarwis, opuść kanał"          → 👋 Opuść aktualny kanał
"Dżarwis, dołącz do [kanału]"   → 👉 Dołącz do kanału
"Dżarwis, zmień status"         → 📝 Ustaw custom status
```

### 🖥️ System
```
"Dżarwis, jaka godzina"      → 🕐 Powiedz czas
"Dżarwis, jaka pogoda"       → 🌤️ Pogoda (wymaga API)
"Dżarwis, wyłącz się"        → 🛑 Zamknij aplikację
"Dżarwis, zapisz notatkę"    → 📝 Nagranie głosowe
"Dżarwis, gdzie jestem"      → 📍 Geolokacja (opcjonalnie)
```

### 🎵 Multimedia
```
"Dżarwis, zbałsiędzość"      → 🔊 Zwiększ głośność
"Dżarwis, ucisz"             → 🔇 Zmniejsz głośność
"Dżarwis, odtwórz"           → ▶️ Play/Pause
"Dżarwis, Spotify"           → 🎵 Otwórz Spotify
```

---

## ⚙️ Konfiguracja

### config.py
```python
# Speech Recognition
SPEECH_ENGINE = "google"  # "google" lub "vosk" (offline)
RECOGNITION_LANGUAGE = "pl-PL"
ACTIVATION_KEYWORD = "dżarwis"

# Text-to-Speech
TTS_ENGINE = "pyttsx3"  # "pyttsx3" lub "gtts"
TTS_LANGUAGE = "pl"
TTS_RATE = 150  # Szybkość (100-200)
TTS_VOLUME = 0.9  # Głośność (0-1)

# YouTube
YOUTUBE_SKIP_AD_TIME = 30  # Sekund
YOUTUBE_BROWSER = "chrome"

# Discord
DISCORD_AUTO_DETECT = True
DISCORD_TIMEOUT = 5

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/jarvis.log"
```

---

## 📁 Struktura Projektu

```
jarvis/
├── main.py                      # Entry point aplikacji
├── config.py                    # Konfiguracja globalna
├── requirements.txt             # Zależności
├── README.md                    # Ta dokumentacja
│
├── voice/                       # 🎤 Speech Recognition & TTS
│   ├── speech_engine.py         # Przetwarzanie mowy
│   ├── tts_engine.py            # Synteza mowy
│   └── voice_config.py          # Konfiguracja dźwięku
│
├── commands/                    # 🤖 Logika komend
│   ├── command_parser.py        # NLP Parser
│   ├── command_executor.py      # Executor
│   ├── youtube_commands.py      # YouTube komendy
│   ├── discord_commands.py      # Discord komendy
│   └── system_commands.py       # Komendy systemowe
│
├── automation/                  # ⚙️ Automatyzacja aplikacji
│   ├── youtube_automation.py    # YouTube Bot (Selenium)
│   ├── discord_automation.py    # Discord Bot (PyAutoGUI)
│   ├── browser_automation.py    # Browser Bot
│   └── keyboard_mouse.py        # Input wrapper
│
├── gui/                         # 🎨 Interfejs Graficzny
│   ├── main_window.py           # Główne okno PyQt6
│   ├── settings_panel.py        # Panel ustawień
│   └── widgets/                 # Custom widgety
│
├── utils/                       # 🛠️ Narzędzia
│   ├── logger.py                # Custom logging
│   ├── helpers.py               # Funkcje pomocnicze
│   ├── constants.py             # Stałe
│   └── decorators.py            # Dekoratory
│
├── tests/                       # ✅ Testy
│   ├── test_speech.py
│   ├── test_commands.py
│   ├── test_automation.py
│   └── test_integration.py
│
├── logs/                        # 📋 Pliki logów
│   └── jarvis.log
│
└── data/                        # 💾 Dane aplikacji
    ├── commands_db.json         # Baza komend
    ├── user_preferences.json    # Preferencje użytkownika
    └── voice_profiles/          # Profile głosu
```

---

## 🔧 Rozwiązywanie Problemów

### ❌ "Microphone not found"
```bash
# Windows - Zainstaluj PyAudio
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt install portaudio19-dev python3-dev
pip install pyaudio
```

### ❌ "Google API Error"
```bash
# Sprawdź połączenie internetowe
# Lub użyj Vosk (offline):
pip install vosk
# Pobierz model z: https://github.com/alphacep/vosk-models
```

### ❌ "Chrome not found"
```bash
# Pobierz Chrome: https://www.google.com/chrome/
# WebDriver Manager powinien automatycznie pobrać ChromeDriver
pip install --upgrade webdriver-manager
```

### ❌ "Discord window not responding"
```python
# Spróbuj zainstalować pygetwindow
pip install pygetwindow

# Na Linuksie:
pip install python-xlib
```

### ❌ "No sound output"
```bash
# Sprawdź głośniki systemowe
# Ustaw TTS_VOLUME w config.py
# Test:
python -c "from voice.tts_engine import TTSEngine; TTSEngine().speak('Test')"
```

---

## 📚 Dokumentacja Rozwojnika

### Dodawanie nowej komendy

**1. Dodaj do Command Parser** (`commands/command_parser.py`):
```python
"new_command": {
    "keywords": ["słowo", "kluczowe"],
    "examples": ["przykład komendy"],
    "priority": 8
}
```

**2. Dodaj Handler** (`commands/command_executor.py`):
```python
def handle_new_command(self, params: Dict):
    self.tts.speak("Wykonuję nową komendę")
    # ... twój kod
```

**3. Test**:
```bash
python -m pytest tests/test_commands.py -v
```

### Dodawanie nowej integracji

1. Stwórz plik w `automation/`
2. Dziedziczy z `BaseAutomation` (opcjonalnie)
3. Zaimplementuj metody akcji
4. Integruj w `command_executor.py`

---

## 🧪 Testowanie

```bash
# Uruchom wszystkie testy
pytest

# Test konkretnego modułu
pytest tests/test_speech.py -v

# Test z pokryciem kodu
pytest --cov=. tests/

# Test z logami
pytest -v -s
```

---

## 🚀 Deployment

### Pakowanie do EXE (Windows)

```bash
# Zainstaluj PyInstaller
pip install pyinstaller

# Tworzenie EXE
pyinstaller --onefile --windowed --icon=icon.ico main.py

# Exe będzie w folder dist/
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
docker build -t jarvis .
docker run -it jarvis
```

---

## 📊 Benchmarki Wydajności

| Komponent | Czas | CPU | RAM |
|-----------|------|-----|-----|
| Speech Recognition | ~2-3s | 15% | 150MB |
| NLP Parsing | ~100ms | 5% | 50MB |
| YouTube Skip | ~500ms | 20% | 100MB |
| Discord Switch | ~300ms | 10% | 80MB |
| **Razem (idle)** | - | 5% | 300MB |

---

## 🤝 Współudział

Chętnie przyjmę pull requesty! Procedura:

1. Fork repo
2. Stwórz branch (`git checkout -b feature/amazing-feature`)
3. Commit zmiany (`git commit -m 'Add amazing feature'`)
4. Push do brancha (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

### Konwencje Kodu
- **Python**: PEP 8
- **Naming**: snake_case dla funkcji, PascalCase dla klas
- **Dokumentacja**: Docstrings dla każdej publicznej funkcji
- **Testy**: Każda nowa feature powinna mieć test

---

## 📝 Roadmap

- [x] Speech Recognition (Phase 1)
- [x] TTS & Voice Responses
- [x] NLP Command Parser
- [x] YouTube Automation
- [x] Discord Integration
- [ ] Web UI (Flask)
- [ ] Mobile App (React Native)
- [ ] Cloud Deployment
- [ ] Advanced AI (GPT Integration)
- [ ] Custom Voice Models
- [ ] Multi-language Support
- [ ] Hardware Integrations (IoT, Smart Home)

---

## 🎓 Nauka & Zasoby

- **Speech Recognition**: https://github.com/Uberi/speech_recognition
- **Spacy NLP**: https://spacy.io/
- **Selenium**: https://selenium.dev/
- **PyQt6**: https://www.riverbankcomputing.com/software/pyqt/
- **Discord.py**: https://discordpy.readthedocs.io/

---

## 📞 Wsparcie & Kontakt

- 🐛 Bug Reports: [Issues](https://github.com/yourusername/jarvis/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/jarvis/discussions)
- 📧 Email: your-email@example.com
- 💬 Discord: Dołącz do serwera

---

## 📄 Licencja

Projekt jest licencjonowany na licencji MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

---

## 🙏 Credits & Acknowledgments

Dziękuję:
- Uberi za [speech_recognition](https://github.com/Uberi/speech_recognition)
- spaCy team za NLP framework
- Selenium contributors
- Społeczności Python

---

## ⭐ Jeśli ci się podoba projekt...

Daj mi gwiazdkę! ⭐ To motywuje do dalszego rozwoju projektu.

```bash
# Klonuj i gwizdnij jak nie masz git
git clone https://github.com/yourusername/jarvis.git
⭐ STAR THIS REPO ⭐
```

---

**Made with ❤️ by [Your Name]**  
*Ostatnia aktualizacja: 2026-08-26*

---

### Quick Links
- [Full Documentation](jarvis.md)
- [Installation Guide](INSTALL.md)
- [API Reference](API.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

**Jesteś gotowy? Zainstaluj i uruchom:** `python main.py` 🚀
