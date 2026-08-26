"""
commands/command_executor.py — Wykonuje rozpoznane komendy.

Moduły automatyzacji (Selenium, PyAutoGUI, pywinauto) importowane są dopiero
przy pierwszym użyciu danej integracji. Dzięki temu testy parsera i logiki
komend nie wymagają zainstalowanej przeglądarki ani bibliotek sterujących
pulpitem — a i sam start aplikacji jest szybszy.
"""
from typing import Callable, Dict, Optional

from voice.tts_engine import TTSEngine
from utils.logger import get_logger

logger = get_logger(__name__)

YOUTUBE_HOME = "https://www.youtube.com"


class CommandExecutor:
    def __init__(self, tts: Optional[TTSEngine] = None):
        # Gdy silnik przyszedł z zewnątrz, to nie my go zamykamy.
        self._owns_tts = tts is None
        self.tts = tts or TTSEngine()

        self.handlers: Dict[str, Callable[[Dict], None]] = self._init_handlers()
        self._youtube = None
        self._discord = None

    def _get_youtube(self):
        """Leniwy start — przeglądarka podnosi się przy pierwszej komendzie YouTube."""
        if self._youtube is None:
            from automation.youtube_automation import YouTubeAutomation

            self._youtube = YouTubeAutomation()
            self._youtube.initialize()
            self._youtube.open_video(YOUTUBE_HOME)
        return self._youtube

    def _get_discord(self):
        if self._discord is None:
            from automation.discord_automation import DiscordAutomation

            self._discord = DiscordAutomation()
        return self._discord

    def _init_handlers(self) -> Dict[str, Callable[[Dict], None]]:
        return {
            "youtube_skip_ad": self.handle_youtube_skip_ad,
            "youtube_play": self.handle_youtube_play,
            "youtube_pause": self.handle_youtube_pause,
            "youtube_next": self.handle_youtube_next,
            "youtube_previous": self.handle_youtube_previous,
            "youtube_fullscreen": self.handle_youtube_fullscreen,
            "discord_mute": self.handle_discord_mute,
            "discord_unmute": self.handle_discord_unmute,
            "discord_deafen": self.handle_discord_deafen,
            "discord_switch_channel": self.handle_discord_switch_channel,
            "discord_join_channel": self.handle_discord_join_channel,
            "discord_leave_channel": self.handle_discord_leave_channel,
            "discord_mute_user": self.handle_discord_mute_user,
            "discord_view_screen": self.handle_discord_view_screen,
            "system_time": self.handle_system_time,
            "system_exit": self.handle_system_exit,
        }

    def execute(self, command: str, params: Dict) -> bool:
        """Wykonuje komendę po nazwie. Zwraca True przy powodzeniu."""
        handler = self.handlers.get(command)
        if handler is None:
            logger.warning(f"❓ Nieznana komenda: {command}")
            self.tts.speak("Nie znam takiej komendy")
            return False

        try:
            handler(params)
            return True
        except Exception as e:
            logger.error(f"💥 Błąd przy wykonywaniu {command}: {e}", exc_info=True)
            self.tts.speak("Coś poszło nie tak")
            return False

    # ---------------- YouTube ----------------

    def handle_youtube_skip_ad(self, params: Dict):
        self.tts.speak_async("Pomijam reklamę")
        seconds = params.get("seconds")
        yt = self._get_youtube()
        yt.skip_ad(skip_time=seconds) if seconds else yt.skip_ad()

    def handle_youtube_play(self, params: Dict):
        self.tts.speak_async("Odtwarzam")
        self._get_youtube().play()

    def handle_youtube_pause(self, params: Dict):
        self.tts.speak_async("Pauza")
        self._get_youtube().pause()

    def handle_youtube_next(self, params: Dict):
        self.tts.speak_async("Następne wideo")
        self._get_youtube().next_video()

    def handle_youtube_previous(self, params: Dict):
        self.tts.speak_async("Poprzednie wideo")
        self._get_youtube().previous_video()

    def handle_youtube_fullscreen(self, params: Dict):
        self.tts.speak_async("Pełny ekran")
        self._get_youtube().fullscreen()

    # ---------------- Discord ----------------

    def handle_discord_mute(self, params: Dict):
        self.tts.speak_async("Przełączam mikrofon")
        self._get_discord().toggle_mute()

    def handle_discord_unmute(self, params: Dict):
        self.tts.speak_async("Przełączam mikrofon")
        self._get_discord().toggle_mute()

    def handle_discord_deafen(self, params: Dict):
        self.tts.speak_async("Przełączam dźwięk")
        self._get_discord().toggle_deafen()

    def handle_discord_switch_channel(self, params: Dict):
        channel = params.get("channel_name")
        if not channel:
            self.tts.speak("Nie usłyszałem nazwy kanału")
            return
        self.tts.speak_async(f"Przełączam na {channel}")
        self._get_discord().switch_channel(channel)

    def handle_discord_join_channel(self, params: Dict):
        channel = params.get("channel_name")
        if not channel:
            self.tts.speak("Nie usłyszałem nazwy kanału")
            return
        self.tts.speak_async(f"Dołączam do {channel}")
        self._get_discord().join_channel(channel)

    def handle_discord_leave_channel(self, params: Dict):
        self.tts.speak_async("Opuszczam kanał")
        self._get_discord().leave_channel()

    def handle_discord_mute_user(self, params: Dict):
        user = params.get("user_name")
        if not user:
            self.tts.speak("Nie usłyszałem, kogo wyciszyć")
            return
        self.tts.speak_async(f"Wyciszam {user}, tylko dla mnie")
        self._get_discord().mute_user(user)

    def handle_discord_view_screen(self, params: Dict):
        user = params.get("user_name")
        if not user:
            self.tts.speak("Nie usłyszałem, czyj ekran pokazać")
            return
        self.tts.speak_async(f"Pokazuję ekran {user}")
        self._get_discord().view_user_screen(user)

    # ---------------- System ----------------

    def handle_system_time(self, params: Dict):
        from datetime import datetime

        now = datetime.now()
        self.tts.speak(f"Jest {now.hour} {now.minute:02d}")
        logger.info(f"🕐 Podano godzinę: {now:%H:%M}")

    def handle_system_exit(self, params: Dict):
        # Czekamy na koniec wypowiedzi — zaraz potem gasną zasoby i głos.
        self.tts.speak("Wyłączam się, do zobaczenia")
        logger.info("🛑 Zamykanie na życzenie użytkownika")
        self.shutdown()

    # ---------------- Sprzątanie ----------------

    def shutdown(self) -> None:
        """Zwalnia zasoby: przeglądarkę i (jeśli to nasz) silnik mowy."""
        if self._youtube is not None:
            self._youtube.close()
            self._youtube = None

        self._discord = None

        if self._owns_tts:
            self.tts.shutdown()
