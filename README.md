# 🎤 JARVIS — Asystent Głosowy

> Głosowy asystent w Pythonie: rozpoznaje polskie komendy i steruje YouTube oraz Discordem.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Development-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## Stan projektu

Szkielet jest kompletny i przetestowany logicznie (47 testów jednostkowych),
ale **nie był jeszcze uruchomiony na żywym sprzęcie** — mikrofonie, przeglądarce
i Discordzie. Traktuj to jako solidną bazę do dopieszczenia, nie gotowy produkt.

| Obszar | Stan |
|---|---|
| Rozpoznawanie mowy (lokalny Whisper, `pl`) | gotowe, nietestowane na mikrofonie |
| Synteza mowy (pyttsx3, offline) | gotowe, nietestowane na głośnikach |
| Parser komend | gotowe, pokryte testami |
| YouTube (Selenium) | gotowe, nietestowane w przeglądarce |
| Discord: mute / deafen / kanały | gotowe, wymaga konfiguracji skrótów |
| Discord: mute osoby, podgląd ekranu | **eksperymentalne** — zależy od układu UI Discorda |
| Interfejs graficzny (PyQt6) | gotowe |

Platforma: rozwijane i przewidziane pod **Windows**. Automatyzacja Discorda
opiera się o `pywinauto`, który działa wyłącznie na Windows.

---

## Szybki start

```bash
git clone https://github.com/bod3ritto/jarvis.git
cd jarvis

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

Pełna instrukcja krok po kroku, z konfiguracją Discorda i YouTube:
**[poradnik.md](poradnik.md)**.
Nie interesują Cię szczegóły techniczne, chcesz tylko wiedzieć co mówić?
**[jak-uzywac.md](jak-uzywac.md)**.

---

## Jak to działa

```
Mikrofon → Rozpoznawanie mowy → Parser komend → Automatyzacja → Odpowiedź głosowa
```

Parser dopasowuje wypowiedź do komend po **rdzeniach słów**, więc radzi sobie
z polską odmianą ("kanał" łapie też "kanału" i "kanale"). Pewność dopasowania
to udział wypowiedzi wyjaśniony przez daną komendę — dzięki temu dodanie
kolejnego synonimu nigdy nie psuje rozpoznawania istniejących fraz.
Świadomie **bez spaCy**: przy dopasowaniu po słowach kluczowych 50 MB model
nie wnosił nic poza wagą instalacji.

---

## Komendy głosowe

W trybie ciągłego nasłuchu poprzedź komendę słowem **„Dżarwis"**.
Przy trybie jednorazowym (przycisk w oknie) słowo aktywacyjne jest zbędne.

### YouTube
| Powiedz | Efekt |
|---|---|
| pomiń reklamę | Klika „Pomiń", a gdy przycisku brak — przeskakuje do przodu |
| pomiń reklamę 15 sekund | Przeskakuje o podaną liczbę sekund |
| odtwórz / wznów | Wznawia odtwarzanie |
| pauza / zatrzymaj / stop | Zatrzymuje odtwarzanie |
| następne wideo | Następne z playlisty |
| poprzednie wideo | Cofa do poprzedniej strony |
| pełny ekran | Przełącza pełny ekran |

### Discord
| Powiedz | Efekt |
|---|---|
| wycisz mikrofon / włącz mikrofon | Przełącza własny mikrofon |
| wycisz dźwięk | Przełącza wyciszenie dźwięku (deafen) |
| przełącz na kanał *nazwa* | Zmienia kanał (Quick Switcher) |
| dołącz do kanału *nazwa* | Dołącza do kanału |
| wycisz użytkownika *nick* | Wycisza osobę **tylko dla Ciebie** ⚠️ |
| pokaż ekran *nick* | Przełącza widok na czyjś udostępniony ekran ⚠️ |

⚠️ = eksperymentalne, oparte o UI Automation — może wymagać dostrojenia.
„Opuść kanał" wymaga własnego skrótu w Discordzie (szczegóły w poradniku).

### System
| Powiedz | Efekt |
|---|---|
| jaka godzina / która godzina | Podaje aktualny czas |
| wyłącz się / zamknij się | Zamyka aplikację i przeglądarkę |

---

## Konfiguracja

Wszystkie ustawienia siedzą w [config.py](config.py) — słowo aktywacyjne,
język, szybkość mowy, indeks mikrofonu, skróty Discorda, poziom logowania.

Nie wiesz, którego mikrofonu używa system?

```bash
python main.py --mikrofony
```

---

## Struktura projektu

```
jarvis/
├── main.py                       # Punkt wejścia (GUI + tryb --mikrofony)
├── config.py                     # Cała konfiguracja
│
├── voice/
│   ├── speech_engine.py          # Rozpoznawanie mowy
│   └── tts_engine.py             # Synteza mowy (wątek roboczy + kolejka)
│
├── commands/
│   ├── command_parser.py         # Tekst -> komenda + parametry
│   └── command_executor.py       # Komenda -> akcja
│
├── automation/
│   ├── youtube_automation.py     # Selenium
│   └── discord_automation.py     # PyAutoGUI + pywinauto
│
├── gui/main_window.py            # Okno PyQt6
├── utils/logger.py               # Logowanie
├── tests/test_commands.py        # Testy parsera i executora
│
├── logs/                         # Logi (jarvis.log)
└── data/                         # Profil Chrome, dane aplikacji
```

---

## Testy

Testy parsera i executora nie wymagają mikrofonu, przeglądarki ani Discorda —
zależności sprzętowe są zamockowane, a moduły automatyzacji importują się leniwie.

```bash
pytest tests/ -v
```

Testy wymagające prawdziwego sprzętu uruchamia się ręcznie:

```bash
python test_microphone.py           # mikrofon + rozpoznawanie
python test_voice_loop.py           # pełna pętla głosowa
python test_youtube_automation.py   # przeglądarka
python test_discord_automation.py   # Discord (menu interaktywne)
```

---

## Dodawanie własnej komendy

1. Dopisz wpis w `_init_commands()` w [command_parser.py](commands/command_parser.py) —
   `keywords` to **rdzenie**, nie pełne słowa (np. `"reklam"`, nie `"reklamę"`).
2. Dodaj handler i wpis w `_init_handlers()` w [command_executor.py](commands/command_executor.py).
3. Uruchom `pytest tests/ -v` — testy pilnują, że każda komenda ma handler,
   a każdy deklarowany przykład faktycznie trafia we własną komendę.

---

## Plany

- [ ] Uruchomienie i dostrojenie na żywym sprzęcie
- [ ] Dostrojenie selektorów UI Discorda (mute osoby, podgląd ekranu)
- [ ] „Opuść kanał" przez własny skrót Discorda
- [ ] Sterowanie odtwarzaczami systemowymi (Spotify, głośność)
- [ ] Panel ustawień w interfejsie zamiast edycji `config.py`

---

## Licencja

MIT — szczegóły w pliku [LICENSE](LICENSE).

---

## Dokumentacja

- [jak-uzywac.md](jak-uzywac.md) — **jak używać na co dzień**, opisane bez żargonu
- [poradnik.md](poradnik.md) — instalacja, konfiguracja, testowanie krok po kroku
- [jarvis.md](jarvis.md) — pierwotna specyfikacja projektu
