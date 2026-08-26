# 📖 Poradnik — jak uruchomić i przetestować JARVIS

Ten plik to praktyczny przewodnik krok po kroku. `README.md` to ogólna dokumentacja
projektu, `jarvis.md` to pełna specyfikacja implementacji — tutaj masz **dokładną
kolejność czynności**, żeby uruchomić i przetestować to, co już jest zaimplementowane.

---

## 1. Instalacja od zera

```bash
# 1. Wirtualne środowisko
python -m venv venv
venv\Scripts\activate

# 2. Zależności
pip install -r requirements.txt

# 3. Model NLP (polski)
python -m spacy download pl_core_news_sm
```

Jeśli `pip install pyaudio` się wysypie (częste na Windows):
```bash
pip install pipwin
pipwin install pyaudio
```

---

## 2. Jednorazowa konfiguracja Discorda

Zanim automatyzacja Discorda zadziała, trzeba ręcznie ustawić dwie rzeczy
**w samej aplikacji Discord**:

1. **Ustawienia użytkownika → Dostępność → włącz "Obsługa czytnika ekranu"**
   (Screen Reader Support). Bez tego elementy UI nie mają nazw czytelnych dla
   automatyzacji (`mute_user`, `view_user_screen` nie zadziałają).

2. **Ustawienia użytkownika → Głos i wideo → Skróty klawiszowe** → dodaj:
   - "Toggle Mute" = `Ctrl+Shift+M`
   - "Toggle Deafen" = `Ctrl+Shift+D`
   - Dla obu zaznacz **"Ten skrót działa globalnie"** — inaczej JARVIS musiałby
     mieć aktywne okno Discorda, żeby zadziałały.

   (Kombinacje klawiszy możesz zmienić w [config.py](config.py) —
   `DISCORD_MUTE_HOTKEY` / `DISCORD_DEAFEN_HOTKEY` — ale muszą być identyczne
   z tym, co ustawisz w Discordzie.)

---

## 3. Jednorazowa konfiguracja YouTube

`test_youtube_automation.py` / `main.py` otwierają **osobną, dedykowaną
przeglądarkę Chrome** (profil w `data/chrome_profile/`, oddzielny od Twojej
normalnej przeglądarki). Przy pierwszym uruchomieniu zaloguj się tam ręcznie do
konta Google — sesja zostanie zapamiętana i nie trzeba będzie się logować przy
kolejnych uruchomieniach.

---

## 4. Kolejność testowania (od najprostszych do najbardziej wymagających)

### 4.1 Parser komend — bez mikrofonu, bez GUI (najszybszy test)
```bash
pytest tests/test_commands.py -v
```

### 4.2 Mikrofon + rozpoznawanie mowy
```bash
python test_microphone.py
```
Powie "🎤 Testowanie mikrofonu..." — powiedz cokolwiek po polsku, sprawdź czy
rozpoznany tekst się zgadza.

### 4.3 Pełna pętla głosowa (Speech + TTS)
```bash
python test_voice_loop.py
```

### 4.4 Automatyzacja YouTube (otworzy się osobne okno Chrome)
```bash
python test_youtube_automation.py
```

### 4.5 Automatyzacja Discord
```bash
python test_discord_automation.py
```
Wybierz z menu: `1`/`2` (mute/deafen — powinny zadziałać od razu, jeśli zrobiłeś
krok 2), `3` (zmiana kanału), `4`/`5` (**eksperymentalne** — mute konkretnej
osoby / podgląd ekranu).

Jeśli `4` lub `5` nie znajdują użytkownika, uruchom diagnostykę:
```bash
python test_discord_automation.py dump
```
To wypisze całe drzewo elementów UI Discorda (nazwa + typ) — poszukaj tam
nicku danej osoby, żeby sprawdzić, czy w ogóle jest widoczny dla automatyzacji.
Wklej mi wynik, jeśli coś nie działa — dostroję selektory.

### 4.6 Cała aplikacja z GUI
```bash
python main.py
```
- **"🎤 Słuchaj (jedno polecenie)"** — jednorazowe rozpoznanie i wykonanie (nie
  trzeba mówić "Dżarwis").
- **"🔁 Nasłuchuj ciągle"** — pętla w tle; wykonuje komendę TYLKO gdy usłyszy
  słowo aktywacyjne ("Dżarwis, ..."), żeby nie reagować na przypadkową mowę.

---

## 5. Ściąga komend głosowych

| Powiedz (po "Dżarwis, ...") | Robi |
|---|---|
| pomiń reklamę | Pomija reklamę na YouTube |
| odtwórz / pauza | Play / Pause |
| następne / poprzednie wideo | Zmiana wideo |
| pełny ekran | Fullscreen YouTube |
| wycisz mikrofon / włącz mikrofon | Toggle własny mikrofon (Discord) |
| wycisz dźwięk | Toggle deafen (Discord) |
| przełącz na kanał [nazwa] | Zmiana kanału (Discord) |
| dołącz do kanału [nazwa] | Dołączenie do kanału (Discord) |
| wycisz użytkownika [nazwa] | Lokalny mute osoby, tylko dla Ciebie ⚠️ eksperymentalne |
| pokaż ekran [nazwa] | Podgląd czyjegoś udostępnionego ekranu ⚠️ eksperymentalne |
| jaka godzina | Mówi aktualną godzinę |
| wyłącz się | Zamyka aplikację (i przeglądarkę YouTube) |

---

## 6. Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---|---|
| `pip install pyaudio` błąd | `pip install pipwin && pipwin install pyaudio` |
| Brak polskiego głosu TTS (log: "Nie znaleziono głosu") | Windows → Ustawienia → Czas i język → Mowa → dodaj polski pakiet głosowy |
| spaCy: `OSError: [E050]` | `python -m spacy download pl_core_news_sm` |
| Selenium nie startuje / błąd ChromeDriver | `pip install --upgrade webdriver-manager`, upewnij się że Chrome jest zainstalowany |
| "Nie znaleziono okna Discord" | Upewnij się, że aplikacja desktopowa Discord jest uruchomiona (nie wersja przeglądarkowa) |
| `mute_user`/`view_user_screen` nie znajdują osoby | Sprawdź krok 2 (Screen Reader Support), uruchom `python test_discord_automation.py dump` i poszukaj nicku w wyniku |
| Rozpoznawanie mowy nie działa / `RequestError` | Sprawdź połączenie internetowe — `recognize_google()` wymaga internetu |

---

## 7. Status projektu

✅ Gotowe i przetestowane logicznie (czeka na testy na żywym sprzęcie):
Speech Recognition, TTS, NLP Parser, YouTube Automation, Discord (mute/deafen/kanały).

⚠️ Eksperymentalne (może wymagać dostrojenia po pierwszym teście):
`discord_mute_user`, `discord_view_screen` — zależą od dokładnych etykiet UI
w Twojej wersji/języku Discorda.
