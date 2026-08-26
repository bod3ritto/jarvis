"""
voice/tts_engine.py — Synteza mowy (Text-to-Speech).

Używa pyttsx3 (offline, głosy systemowe SAPI5 na Windows).
Jeśli w systemie brak polskiego głosu, używany jest domyślny głos
z ostrzeżeniem w logu.
"""
import threading

import pyttsx3

import config
from utils.logger import get_logger

logger = get_logger(__name__)


class TTSEngine:
    def __init__(
        self,
        language: str = config.TTS_LANGUAGE,
        rate: int = config.TTS_RATE,
        volume: float = config.TTS_VOLUME,
    ):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.language = language

        self._select_voice(language)

    def _select_voice(self, language: str) -> None:
        """Próbuje znaleźć głos pasujący do języka (np. polski). Loguje ostrzeżenie jeśli brak."""
        voices = self.engine.getProperty("voices")
        for voice in voices:
            languages = getattr(voice, "languages", None) or []
            name = getattr(voice, "name", "") or ""
            voice_id = getattr(voice, "id", "") or ""

            matches_lang = language in languages or any(language in str(l).lower() for l in languages)
            matches_name = "polish" in name.lower() or "polski" in name.lower() or "pl-pl" in voice_id.lower()

            if matches_lang or matches_name:
                self.engine.setProperty("voice", voice.id)
                logger.info(f"🔊 Wybrano głos TTS: {name or voice.id}")
                return

        logger.warning(
            f"⚠️ Nie znaleziono głosu '{language}' w systemie — używam domyślnego. "
            "Zainstaluj polski pakiet głosowy w Ustawieniach Windows > Mowa, "
            "aby uzyskać naturalną polską wymowę."
        )

    def speak(self, text: str, wait: bool = True) -> None:
        """Mów tekst synchronicznie (wait=True) lub asynchronicznie (wait=False)."""
        logger.info(f"🔊 Mówię: {text}")
        self.engine.say(text)

        if wait:
            self.engine.runAndWait()
        else:
            thread = threading.Thread(target=self.engine.runAndWait, daemon=True)
            thread.start()

    def speak_async(self, text: str) -> None:
        self.speak(text, wait=False)

    def stop(self) -> None:
        self.engine.stop()
