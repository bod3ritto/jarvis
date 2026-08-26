# 🎤 Rozmowy z Dżarwisem — poradnik dla początkujących

Dżarwis słucha przez mikrofon i robi to, co mu powiesz — pomija reklamy na
YouTube, wycisza mikrofon na Discordzie, przełącza kanały. Ten poradnik pokazuje,
co dokładnie mówić i czego się spodziewać.

> Wersja do czytania w przeglądarce (ładniejsza): patrz link do poradnika
> przekazany przy jego utworzeniu.
>
> Instalacja krok po kroku: [poradnik.md](poradnik.md) ·
> Opis techniczny: [README.md](README.md)

---

## Zanim zaczniesz

Cztery rzeczy, które warto wiedzieć od razu:

- **Program jest nowy i nie był jeszcze sprawdzony w działaniu.** Pierwsze
  uruchomienie może wymagać drobnych poprawek — to normalne na tym etapie.
- **Potrzebny jest internet.** Rozpoznawanie mowy odbywa się przez Google.
- **Discord musi być otwarty** — w wersji zainstalowanej na komputerze,
  nie na stronie w przeglądarce.
- **YouTube otwiera się w osobnym oknie Chrome.** To nie jest Twoja zwykła
  przeglądarka — Dżarwis ma własną, żeby nie mieszać Ci w kartach.

---

## Uruchomienie

### 1. Włącz Dżarwisa

Otwórz folder z programem i uruchom:

```bash
python main.py
```

Pojawi się okno z trzema przyciskami. To cały interfejs.

### 2. Ustaw dwa skróty w Discordzie *(tylko za pierwszym razem)*

Bez tego Dżarwis nie wyciszy Ci mikrofonu. W Discordzie wejdź w
**Ustawienia użytkownika → Głos i wideo → Skróty klawiszowe** i dodaj:

| Akcja | Skrót |
|---|---|
| Toggle Mute | `Ctrl + Shift + M` |
| Toggle Deafen | `Ctrl + Shift + D` |

Przy obu zaznacz **„Ten skrót działa globalnie"** — inaczej zadziałają tylko
wtedy, gdy okno Discorda będzie akurat na wierzchu.

Jeszcze jedno: w **Ustawienia → Dostępność** włącz **„Obsługa czytnika ekranu"**.
Dzięki temu Dżarwis rozpoznaje, kto jest na liście — bez tego nie wyciszy
konkretnej osoby ani nie pokaże jej ekranu.

### 3. Zaloguj się do YouTube *(tylko za pierwszym razem)*

Przy pierwszej komendzie dotyczącej YouTube otworzy się nowe okno Chrome.
Zaloguj się w nim do konta Google — Dżarwis zapamięta to na przyszłość.

---

## Dwa sposoby mówienia

To najważniejsza rzecz do zrozumienia — od wybranego trybu zależy, czy trzeba
wołać Dżarwisa po imieniu.

**🎤 Słuchaj (jedno polecenie)** — klikasz, Dżarwis wysłucha jednej rzeczy
i ją wykona. **Nie musisz mówić „Dżarwis"**; kliknięcie wystarczy za zaproszenie.

**🔁 Nasłuchuj ciągle** — program nasłuchuje w tle, ale reaguje dopiero, gdy
usłyszy swoje imię. **Każde polecenie zacznij od „Dżarwis"** — dzięki temu nie
wykona przypadkiem czegoś, co powiesz w zwykłej rozmowie.

---

## Co możesz powiedzieć

W trybie ciągłym dodaj na początku „Dżarwis," — w trybie jednorazowym mów od razu
samo polecenie.

Nie musisz trafiać w słowa co do joty. Dżarwis rozumie odmianę, więc
„przełącz na kanał ogólny" i „przełącz na kanale ogólnym" zadziałają tak samo.

### YouTube

| Powiedz | Co się stanie |
|---|---|
| „pomiń reklamę" | Klika „Pomiń", a jeśli przycisku jeszcze nie ma — przewija film do przodu |
| „pomiń reklamę 15 sekund" | To samo, ale przewija o tyle sekund, ile powiesz |
| „odtwórz" / „wznów" | Wznawia film. Na grającym filmie nic nie zepsuje |
| „pauza" / „zatrzymaj" / „stop" | Zatrzymuje film |
| „następne wideo" | Przeskakuje do kolejnego filmu z playlisty |
| „poprzednie wideo" | Wraca do poprzednio oglądanej strony |
| „pełny ekran" | Włącza i wyłącza tryb pełnoekranowy |

### Discord

| Powiedz | Co się stanie |
|---|---|
| „wycisz mikrofon" / „włącz mikrofon" | Wycisza i odcisza Twój własny mikrofon |
| „wycisz dźwięk" | Wycisza wszystko, co słyszysz (discordowe „deafen") |
| „przełącz na kanał ogólny" | Przechodzi na wskazany kanał — powiedz nazwę swojego |
| „dołącz do kanału gaming" | Dołącza do wskazanego kanału głosowego |
| „wycisz użytkownika kowalski" ⚠️ | Wycisza tę osobę **tylko dla Ciebie** — reszta kanału słyszy ją normalnie |
| „pokaż ekran kowalskiego" ⚠️ | Przełącza widok na ekran udostępniany przez tę osobę |

⚠️ = bywa kapryśne; opiera się na rozpoznawaniu wyglądu Discorda.

### Pozostałe

| Powiedz | Co się stanie |
|---|---|
| „jaka godzina" / „która godzina" | Mówi na głos aktualny czas |
| „wyłącz się" / „zamknij się" | Żegna się, zamyka okno Chrome i kończy pracę |

---

## Kiedy coś nie działa

**Dżarwis w ogóle mnie nie słyszy.**
Najczęściej komputer słucha przez inny mikrofon, niż myślisz — np. przez kamerkę
zamiast słuchawek. Uruchom `python main.py --mikrofony`, żeby zobaczyć listę
urządzeń, i wpisz numer właściwego do `config.py` w miejscu `MICROPHONE_INDEX`.

**Słyszy, ale nic nie odpowiada głosem.**
Brakuje polskiego głosu w systemie: Windows → Ustawienia → Czas i język → Mowa →
dodaj polski pakiet głosowy. Dżarwis działa też bez tego, tylko milczy.

**Wykonuje nie tę komendę, co trzeba.**
Powiedz to krócej i wyraźniej — im więcej dodatkowych słów w zdaniu, tym mniej
pewne dopasowanie. W oknie programu zobaczysz, co usłyszał i na ile był pewny.

**Nie wycisza konkretnej osoby / nie pokazuje jej ekranu.**
Sprawdź, czy w Discordzie masz włączoną „Obsługę czytnika ekranu" (krok 2).
To najczęstsza przyczyna.

**Nie działa nic związanego z Discordem.**
Discord musi być uruchomiony jako aplikacja na komputerze — wersja w przeglądarce
nie zadziała.

**Coś się wysypało i nie wiadomo dlaczego.**
Wszystko zapisuje się w pliku `logs/jarvis.log`. To pierwsze miejsce do zajrzenia.

---

## Czego jeszcze nie potrafi

Żeby nie było rozczarowań — tych rzeczy Dżarwis **nie** zrobi, choć brzmią
sensownie: sterowanie Spotify, zmiana głośności, pogoda, notatki głosowe,
wychodzenie z kanału głosowego (ostatnia wymaga dodatkowego skrótu w Discordzie
i czeka na dokończenie).

Wszystkie rozumiane polecenia są wypisane wyżej. Jeśli powiesz coś spoza listy,
Dżarwis zgłosi, że nie rozpoznał komendy — i nic się nie stanie.
