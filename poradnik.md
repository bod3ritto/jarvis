# 📖 Poradnik — jak uruchomić i przetestować JARVIS

Praktyczny przewodnik krok po kroku. `README.md` opisuje projekt ogólnie,
`jarvis.md` to pierwotna specyfikacja — tutaj masz **dokładną kolejność
czynności**, żeby to odpalić.

---

## 1. Instalacja

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Jeśli `pyaudio` nie chce się zainstalować (częste na Windows):

```bash
pip install pipwin
pipwin install pyaudio
```

Jeśli `pipwin` też się wysypie (najnowszy Python), zainstaluj Python 3.12 obok:

```bash
winget install python.python.3.12
```

Zamknij PowerShell, otwórz na nowo, i utwórz środowisko na wersji 3.12:

```bash
py -3.12 -m venv venv
venvScriptsctivate
pip install -r requirements.txt
```

> Modelu językowego nie trzeba pobierać — parser komend działa bez spaCy.

---

## 2. Sprawdź, który mikrofon widzi system

```bash
python main.py --mikrofony
```

Jeśli domyślne urządzenie to nie ten mikrofon, którego chcesz używać, wpisz
jego indeks z tej listy do `MICROPHONE_INDEX` w [config.py](config.py).

---

## 3. Jednorazowa konfiguracja Discorda

Dwie rzeczy trzeba ustawić ręcznie **w samej aplikacji Discord**:

1. **Ustawienia użytkownika → Dostępność → włącz „Obsługa czytnika ekranu"**
   (Screen Reader Support). Bez tego elementy interfejsu nie mają nazw
   czytelnych dla automatyzacji i komendy „wycisz użytkownika" oraz
   „pokaż ekran" nie zadziałają.

2. **Ustawienia użytkownika → Głos i wideo → Skróty klawiszowe** → dodaj:
   - „Toggle Mute" = `Ctrl+Shift+M`
   - „Toggle Deafen" = `Ctrl+Shift+D`
   - Dla obu zaznacz **„Ten skrót działa globalnie"** — inaczej zadziałają
     tylko wtedy, gdy okno Discorda jest aktywne.

   Kombinacje możesz zmienić w [config.py](config.py) (`DISCORD_MUTE_HOTKEY`,
   `DISCORD_DEAFEN_HOTKEY`), byle zgadzały się z tym, co ustawisz w Discordzie.

Komenda „opuść kanał" nie ma w Discordzie domyślnego skrótu — jeśli chcesz jej
używać, przypisz własny skrót do akcji „Disconnect" i dodaj go do `config.py`.

---

## 4. Jednorazowa konfiguracja YouTube

JARVIS otwiera **osobną przeglądarkę Chrome** z własnym profilem
(`data/chrome_profile/`), oddzielnym od Twojej codziennej przeglądarki.
Przy pierwszym uruchomieniu zaloguj się w niej do Google — sesja zostanie
zapamiętana na kolejne razy.

---

## 5. Kolejność testowania

Od najprostszego do najbardziej wymagającego — jeśli coś padnie, wiadomo
dokładnie na którym poziomie.

### 5.1 Logika komend (bez sprzętu, ~1 sekunda)

```bash
pytest tests/ -v
```

47 testów, nie wymagają mikrofonu, przeglądarki ani Discorda.

### 5.2 Mikrofon i rozpoznawanie mowy

```bash
python test_microphone.py
```

Powiedz coś po polsku i sprawdź, czy rozpoznany tekst się zgadza.

### 5.3 Pełna pętla głosowa

```bash
python test_voice_loop.py
```

JARVIS przywita się, wysłucha trzech wypowiedzi i każdą powtórzy.

### 5.4 YouTube

```bash
python test_youtube_automation.py
```

Otworzy się osobne okno Chrome — obserwuj pauzę, wznowienie i pełny ekran.

### 5.5 Discord

```bash
python test_discord_automation.py
```

Menu: `1`/`2` (mute/deafen — zadziałają, jeśli zrobiłeś krok 3), `3` (zmiana
kanału), `4`/`5` (**eksperymentalne** — wyciszenie osoby, podgląd ekranu).

Gdy `4` lub `5` nie znajdują użytkownika:

```bash
python test_discord_automation.py dump
```

Wypisze drzewo elementów interfejsu Discorda. Poszukaj tam nicku danej osoby —
jeśli go nie ma, znaczy że „Obsługa czytnika ekranu" jest wyłączona. Jeśli jest,
a mimo to nie działa, wyślij ten zrzut — na jego podstawie da się dostroić
selektory.

### 5.6 Cała aplikacja

```bash
python main.py
```

- **„Słuchaj (jedno polecenie)"** — jedno rozpoznanie; słowo aktywacyjne zbędne.
- **„Nasłuchuj ciągle"** — pętla w tle; reaguje dopiero po usłyszeniu
  „Dżarwis, ...", żeby nie wykonywać przypadkowych fraz z rozmowy.

---

## 6. Ściąga komend

Pełna lista z opisem działania jest w [README.md](README.md#komendy-głosowe).
Najczęściej używane:

```
Dżarwis, pomiń reklamę            Dżarwis, wycisz mikrofon
Dżarwis, pauza                    Dżarwis, wycisz dźwięk
Dżarwis, odtwórz                  Dżarwis, przełącz na kanał ogólny
Dżarwis, pełny ekran              Dżarwis, wycisz użytkownika kowalski
Dżarwis, jaka godzina             Dżarwis, pokaż ekran kowalskiego
Dżarwis, wyłącz się
```

---

## 7. Gdy coś nie działa

| Objaw | Co zrobić |
|---|---|
| `pip install pyaudio` się wywala | `pip install pipwin` a potem `pipwin install pyaudio` |
| Nie słychać odpowiedzi, w logu „Nie znaleziono głosu" | Windows → Ustawienia → Czas i język → Mowa → dodaj polski pakiet głosowy |
| JARVIS nie słyszy / słyszy nie ten mikrofon | `python main.py --mikrofony`, ustaw `MICROPHONE_INDEX` w `config.py` |
| „Błąd usługi rozpoznawania" | Silnik `google` (jeśli aktywny) idzie przez internet — sprawdź połączenie |
| Pierwsze uruchomienie długo "myśli" po komendzie głosowej | Normalne — lokalny model Whisper pobiera się i ładuje się do pamięci przy pierwszym użyciu |
| Rozpoznaje słowa błędnie / od czapy | Domyślny silnik to lokalny Whisper (`SPEECH_ENGINE = "whisper"` w `config.py`) — dokładniejszy niż darmowe API Google. Możesz też podbić `WHISPER_MODEL_SIZE` z `"small"` na `"medium"` kosztem szybkości |
| Selenium nie startuje / błąd ChromeDrivera | `pip install --upgrade webdriver-manager`; sprawdź, czy Chrome jest zainstalowany |
| „Nie znaleziono okna Discord" | Uruchom aplikację **desktopową** Discorda (wersja w przeglądarce nie zadziała) |
| Wyciszenie osoby / podgląd ekranu nie działa | Krok 3 punkt 1, potem `python test_discord_automation.py dump` |
| Komenda rozpoznana, ale nie ta co trzeba | Zajrzyj do `logs/jarvis.log` — jest tam rozpoznany tekst i pewność dopasowania |

Wszystko, co się dzieje, ląduje w `logs/jarvis.log` — to pierwsze miejsce
do sprawdzenia przy każdym problemie.

---

## 8. Czego jeszcze nie ma

- Nic nie było uruchomione na żywym sprzęcie — spodziewaj się drobnych poprawek.
- Wyciszanie konkretnej osoby i podgląd cudzego ekranu opierają się o układ
  interfejsu Discorda i mogą wymagać dostrojenia selektorów.
- „Opuść kanał" czeka na własny skrót w Discordzie (patrz krok 3).
