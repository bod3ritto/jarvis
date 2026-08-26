"""
automation/discord_automation.py — Sterowanie własnym, otwartym klientem Discord.

Decyzja architektoniczna: PyAutoGUI (symulacja skrótów/kliknięć), NIE bot discord.py —
bo funkcja "wycisz kogoś tylko dla mnie" to lokalna funkcja klienta, niedostępna przez API bota.

Dwie kategorie akcji o różnej niezawodności:
1. Toggle Mute / Toggle Deafen — używają GLOBALNYCH skrótów Discorda (patrz config.py,
   DISCORD_MUTE_HOTKEY / DISCORD_DEAFEN_HOTKEY). Muszą być ręcznie skonfigurowane
   w Discordzie z opcją "działa globalnie" — wtedy działają nawet gdy Discord nie
   jest aktywnym oknem. Najbardziej niezawodna część.
2. Przełączanie kanału (Ctrl+K) — to jest skrót WEWNĄTRZ aplikacji, więc wymaga
   najpierw skupienia (focus) okna Discord.
3. Mute konkretnego użytkownika "tylko dla mnie" i przełączanie widoku na czyjś
   udostępniony ekran — zaimplementowane przez UI Automation (pywinauto), bo Discord
   nie ma do tego ŻADNEGO skrótu klawiszowego. Szuka elementów w drzewie dostępności
   po nazwie (np. nick użytkownika), więc działa niezależnie od rozmiaru okna/
   rozdzielczości — ale WYMAGA włączenia w Discordzie:
   Ustawienia użytkownika > Dostępność > "Obsługa czytnika ekranu"
   (Screen Reader Support) — bez tego elementy UI nie mają czytelnych nazw.

   To wciąż EKSPERYMENTALNE — dokładne nazwy/etykiety elementów w Discordzie mogą się
   różnić i wymagać dostrojenia po pierwszym teście na żywym ekranie. Użyj
   test_discord_automation.py do zrzucenia drzewa UI i kalibracji.
"""
import time

import pyautogui

import config
from utils.logger import get_logger

logger = get_logger(__name__)

FOCUS_SETTLE_DELAY = 0.3  # sekund po aktywacji okna, zanim wyślemy dalsze klawisze
TYPE_INTERVAL = 0.05  # sekund między znakami przy wpisywaniu nazwy kanału
CONTEXT_MENU_SETTLE_DELAY = 0.4  # sekund na pojawienie się menu kontekstowego po right-click
UIA_POLL_INTERVAL = 0.2  # sekund między próbami przy szukaniu menu kontekstowego


class DiscordWindowNotFoundError(Exception):
    """Nie znaleziono okna Discorda — upewnij się, że aplikacja jest uruchomiona."""


class DiscordAutomation:
    def __init__(self):
        self.discord_window = None

    def find_discord_window(self) -> bool:
        """Znajdź okno Discord (desktop client). Zwraca True jeśli znalezione."""
        try:
            import pygetwindow as gw
        except ImportError:
            logger.error("❌ Brak pygetwindow — zainstaluj: pip install pygetwindow")
            return False

        windows = gw.getWindowsWithTitle(config.DISCORD_WINDOW_TITLE)
        if windows:
            self.discord_window = windows[0]
            return True

        logger.warning("⚠️ Nie znaleziono okna Discord — czy aplikacja jest uruchomiona?")
        return False

    def focus_discord(self) -> bool:
        """Aktywuj i skup okno Discord. Wymagane przed skrótami działającymi tylko in-app (np. Ctrl+K)."""
        if self.discord_window is None and not self.find_discord_window():
            return False

        try:
            if self.discord_window.isMinimized:
                self.discord_window.restore()
            self.discord_window.activate()
            time.sleep(FOCUS_SETTLE_DELAY)
            return True
        except Exception as e:
            logger.error(f"❌ Nie udało się aktywować okna Discord: {e}")
            return False

    def toggle_mute(self) -> bool:
        """Włącz/wyłącz mikrofon (globalny skrót Discorda — nie wymaga focusu)."""
        pyautogui.hotkey(*config.DISCORD_MUTE_HOTKEY)
        logger.info("🎙️ Toggle Mute (globalny skrót)")
        return True

    def toggle_deafen(self) -> bool:
        """Włącz/wyłącz dźwięk (globalny skrót Discorda — nie wymaga focusu)."""
        pyautogui.hotkey(*config.DISCORD_DEAFEN_HOTKEY)
        logger.info("🔊 Toggle Deafen (globalny skrót)")
        return True

    def switch_channel(self, channel_name: str) -> bool:
        """Przełącz na kanał przez Quick Switcher (Ctrl+K) — wymaga focusu Discorda."""
        if not self.focus_discord():
            return False

        pyautogui.hotkey("ctrl", "k")
        time.sleep(FOCUS_SETTLE_DELAY)
        pyautogui.typewrite(channel_name, interval=TYPE_INTERVAL)
        time.sleep(0.3)
        pyautogui.press("enter")
        logger.info(f"🔄 Przełączono na: {channel_name}")
        return True

    def join_channel(self, channel_name: str) -> bool:
        """Alias na switch_channel — Quick Switcher działa tak samo dla dołączania do kanału głosowego."""
        return self.switch_channel(channel_name)

    def leave_channel(self) -> bool:
        """
        Opuść aktualny kanał głosowy.

        UWAGA: Discord nie ma domyślnego skrótu do opuszczenia kanału głosowego.
        Jeśli masz przypisany własny skrót globalny (Ustawienia > Głos i wideo >
        Skróty klawiszowe > "Disconnect"), dodaj go do config.py jako
        DISCORD_LEAVE_CHANNEL_HOTKEY i podmień implementację poniżej.
        """
        logger.warning(
            "⚠️ 'Opuść kanał' niezaimplementowane — Discord nie ma domyślnego skrótu. "
            "Skonfiguruj własny skrót 'Disconnect' w Discordzie i dodaj go do config.py."
        )
        return False

    # ---------------- UI Automation (pywinauto) — eksperymentalne ----------------

    def _connect_uia(self):
        """Podłącza się do okna Discord przez pywinauto (backend UIA). Zwraca None przy błędzie."""
        try:
            from pywinauto import Desktop
        except ImportError:
            logger.error("❌ Brak pywinauto — zainstaluj: pip install pywinauto")
            return None

        try:
            window = Desktop(backend="uia").window(title_re=f".*{config.DISCORD_WINDOW_TITLE}.*")
            window.wait("exists visible", timeout=config.DISCORD_UIA_SEARCH_TIMEOUT)
            return window
        except Exception as e:
            logger.error(
                f"❌ Nie udało się podłączyć do okna Discord przez UI Automation: {e}. "
                "Upewnij się, że Discord jest uruchomiony i widoczny."
            )
            return None

    def _find_by_name(self, root, name_substr: str):
        """Szuka w drzewie descendantów elementu, którego tekst zawiera name_substr (case-insensitive)."""
        needle = name_substr.lower()
        try:
            candidates = root.descendants()
        except Exception as e:
            logger.error(f"❌ Błąd przeglądania drzewa UI Discorda: {e}")
            return None

        for element in candidates:
            try:
                text = element.window_text() or ""
            except Exception:
                continue
            if needle in text.lower():
                return element
        return None

    def _find_context_menu_item(self, labels):
        """Po otwarciu menu kontekstowego (right-click) szuka pozycji menu pasującej do jednej z etykiet."""
        from pywinauto import Desktop

        lowered_labels = [l.lower() for l in labels]
        deadline = time.time() + config.DISCORD_UIA_SEARCH_TIMEOUT

        while time.time() < deadline:
            try:
                for window in Desktop(backend="uia").windows():
                    for item in window.descendants(control_type="MenuItem"):
                        text = (item.window_text() or "").lower()
                        if any(label in text for label in lowered_labels):
                            return item
            except Exception:
                pass  # okno menu mogło jeszcze się nie pojawić — spróbuj ponownie
            time.sleep(UIA_POLL_INTERVAL)

        return None

    def mute_user(self, user_name: str) -> bool:
        """
        Wycisz konkretnego użytkownika TYLKO DLA MNIE (lokalny mute klienta).

        EKSPERYMENTALNE: znajduje element po nazwie użytkownika w widocznej liście
        (member list / lista w kanale głosowym), otwiera jego menu kontekstowe
        (prawy klik) i klika pozycję "Wycisz"/"Mute". Jeśli user_name pasuje do
        wielu miejsc (np. też widoczny na czacie), może trafić w zły element —
        w razie problemów użyj test_discord_automation.py do diagnostyki.
        """
        window = self._connect_uia()
        if window is None:
            return False

        target = self._find_by_name(window, user_name)
        if target is None:
            logger.warning(
                f"⚠️ Nie znaleziono '{user_name}' w oknie Discorda. Upewnij się, że "
                "'Obsługa czytnika ekranu' jest włączona (Ustawienia > Dostępność) "
                "i że dana osoba jest widoczna na liście."
            )
            return False

        try:
            target.right_click_input()
        except Exception as e:
            logger.error(f"❌ Nie udało się kliknąć prawym na '{user_name}': {e}")
            return False

        time.sleep(CONTEXT_MENU_SETTLE_DELAY)
        menu_item = self._find_context_menu_item(config.DISCORD_MUTE_MENU_LABELS)
        if menu_item is None:
            logger.warning(
                f"⚠️ Otworzyłem menu kontekstowe dla '{user_name}', ale nie znalazłem "
                f"opcji {config.DISCORD_MUTE_MENU_LABELS} — sprawdź etykiety w swojej "
                "wersji językowej Discorda."
            )
            return False

        menu_item.click_input()
        logger.info(f"🔇 Wyciszono '{user_name}' lokalnie (tylko dla mnie)")
        return True

    def view_user_screen(self, user_name: str) -> bool:
        """
        Przełącz widok na udostępniony ekran danego użytkownika w rozmowie głosowej.

        EKSPERYMENTALNE: znajduje kafelek/element powiązany z nazwą użytkownika
        i klika go, żeby przełączyć na jego widok. Wymaga, żeby dana osoba aktualnie
        udostępniała ekran w tym samym kanale głosowym.
        """
        window = self._connect_uia()
        if window is None:
            return False

        target = self._find_by_name(window, user_name)
        if target is None:
            logger.warning(
                f"⚠️ Nie znaleziono ekranu/kafelka '{user_name}' — czy ta osoba "
                "aktualnie udostępnia ekran w Twoim kanale głosowym?"
            )
            return False

        try:
            target.click_input()
            logger.info(f"🖥️ Przełączono widok na ekran '{user_name}'")
            return True
        except Exception as e:
            logger.error(f"❌ Nie udało się przełączyć widoku na '{user_name}': {e}")
            return False
