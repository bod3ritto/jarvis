"""
commands/command_executor.py — Wykonuje rozpoznane komendy.

Wszystkie komendy YouTube i Discord podłączone do prawdziwej automatyzacji
(Selenium — Faza 3, PyAutoGUI/pywinauto — Faza 4). Komendy System obsłużone
bezpośrednio.
"""
from typing import Callable, Dict, Optional

from voice.tts_engine import TTSEngine
from automation.youtube_automation import YouTubeAutomation
from automation.discord_automation import DiscordAutomation
from utils.logger import get_logger

logger = get_logger(__name__)


class CommandExecutor:
    def __init__(self, tts: TTSEngine = None):
        self.tts = tts or TTSEngine()
        self.handlers: Dict[str, Callable[[Dict], None]] = self._init_handlers()
        self._youtube: Optional[YouTubeAutomation] = None
        self._discord: Optional[DiscordAutomation] = None

    def _get_youtube(self) -> YouTubeAutomation:
        """Leniwa inicjalizacja — przeglądarka startuje dopiero przy pierwszej komendzie YouTube."""
        if self._youtube is None:
            self._youtube = YouTubeAutomation()
            self._youtube.initialize()
            self._youtube.open_video("https://www.youtube.com")
        return self._youtube

    def _get_discord(self) -> DiscordAutomation:
        if self._discord is None:
            self._discord = DiscordAutomation()
        return self._discord

    def _init_handlers(self) -> Dict[str, Callable[[Dict], None]]:
        return {
            # YouTube
            "youtube_skip_ad": self.handle_youtube_skip_ad,
            "youtube_play": self.handle_youtube_play,
            "youtube_pause": self.handle_youtube_pause,
            "youtube_next": self.handle_youtube_next,
            "youtube_previous": self.handle_youtube_previous,
            "youtube_fullscreen": self.handle_youtube_fullscreen,
            # Discord
            "discord_mute": self.handle_discord_mute,
            "discord_unmute": self.handle_discord_unmute,
            "discord_deafen": self.handle_discord_deafen,
            "discord_switch_channel": self.handle_discord_switch_channel,
            "discord_join_channel": self.handle_discord_join_channel,
            "discord_leave_channel": self.handle_discord_leave_channel,
            "discord_mute_user": self.handle_discord_mute_user,
            "discord_view_screen": self.handle_discord_view_screen,
            # System
            "system_time": self.handle_system_time,
            "system_exit": self.handle_system_exit,
        }

    def execute(self, command: str, params: Dict) -> bool:
        """Wykonaj komendę po nazwie. Zwraca True/False (sukces)."""
        if command not in self.handlers:
            logger.warning(f"❓ Nieznana komenda: {command}")
            self.tts.speak(f"Nie znam komendy {command}")
            return False

        try:
            self.handlers[command](params)
            return True
        except Exception as e:
            logger.error(f"💥 Błąd przy wykonywaniu {command}: {e}")
            self.tts.speak("Coś poszło nie tak")
            return False

    # ---------------- YouTube (Selenium — Faza 3) ----------------
    def handle_youtube_skip_ad(self, params: Dict):
        seconds = params.get("seconds")
        self.tts.speak("Pomijam reklamę")
        if seconds:
            self._get_youtube().skip_ad(skip_time=seconds)
        else:
            self._get_youtube().skip_ad()

    def handle_youtube_play(self, params: Dict):
        self.tts.speak("Odtwarzam")
        self._get_youtube().play()

    def handle_youtube_pause(self, params: Dict):
        self.tts.speak("Pauza")
        self._get_youtube().pause()

    def handle_youtube_next(self, params: Dict):
        self.tts.speak("Następne wideo")
        self._get_youtube().next_video()

    def handle_youtube_previous(self, params: Dict):
        self.tts.speak("Poprzednie wideo")
        self._get_youtube().previous_video()

    def handle_youtube_fullscreen(self, params: Dict):
        self.tts.speak("Pełny ekran")
        self._get_youtube().fullscreen()

    # ---------------- Discord (PyAutoGUI — Faza 4) ----------------
    def handle_discord_mute(self, params: Dict):
        self.tts.speak("Przełączam mikrofon")
        self._get_discord().toggle_mute()

    def handle_discord_unmute(self, params: Dict):
        self.tts.speak("Przełączam mikrofon")
        self._get_discord().toggle_mute()

    def handle_discord_deafen(self, params: Dict):
        self.tts.speak("Przełączam dźwięk")
        self._get_discord().toggle_deafen()

    def handle_discord_switch_channel(self, params: Dict):
        channel = params.get("channel_name", "kanał")
        self.tts.speak(f"Przełączam na {channel}")
        self._get_discord().switch_channel(channel)

    def handle_discord_join_channel(self, params: Dict):
        channel = params.get("channel_name", "kanał")
        self.tts.speak(f"Dołączam do {channel}")
        self._get_discord().join_channel(channel)

    def handle_discord_leave_channel(self, params: Dict):
        self.tts.speak("Opuszczam kanał")
        self._get_discord().leave_channel()

    def handle_discord_mute_user(self, params: Dict):
        user = params.get("user_name")
        if not user:
            self.tts.speak("Nie usłyszałem czyje imię")
            return
        self.tts.speak(f"Wyciszam {user}, tylko dla mnie")
        self._get_discord().mute_user(user)

    def handle_discord_view_screen(self, params: Dict):
        user = params.get("user_name")
        if not user:
            self.tts.speak("Nie usłyszałem czyj ekran")
            return
        self.tts.speak(f"Pokazuję ekran {user}")
        self._get_discord().view_user_screen(user)

    # ---------------- System ----------------
    def handle_system_time(self, params: Dict):
        from datetime import datetime

        now = datetime.now().strftime("%H:%M")
        self.tts.speak(f"Jest {now}")
        logger.info(f"🕐 Podano godzinę: {now}")

    def handle_system_exit(self, params: Dict):
        self.tts.speak("Wyłączam się, do zobaczenia")
        self.shutdown()
        logger.info("🛑 Zamykanie aplikacji...")

    def shutdown(self) -> None:
        """Sprząta zasoby (zamyka przeglądarkę YouTube, jeśli była uruchomiona)."""
        if self._youtube is not None:
            self._youtube.close()
            self._youtube = None
