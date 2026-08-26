"""
voice/speech_engine.py — Rozpoznawanie mowy (Speech-to-Text).

Używa darmowego, nieoficjalnego endpointu Google przez
SpeechRecognition.recognize_google() — bez klucza API, wymaga internetu.
"""
import threading
from typing import Callable, Optional

import speech_recognition as sr

import config
from utils.logger import get_logger

logger = get_logger(__name__)


class SpeechEngine:
    def __init__(
        self,
        language: str = config.RECOGNITION_LANGUAGE,
        engine: str = config.SPEECH_ENGINE,
        microphone_index: Optional[int] = config.MICROPHONE_INDEX,
    ):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.engine = engine
        self.microphone = sr.Microphone(device_index=microphone_index)
        self.is_listening = False
        self.on_recognized: Optional[Callable[[str], None]] = None

    def recognize(
        self,
        timeout: int = config.LISTEN_TIMEOUT,
        phrase_time_limit: int = config.PHRASE_TIME_LIMIT,
    ) -> Optional[str]:
        """Nasłuchuje z mikrofonu i zwraca rozpoznany tekst (lowercase) lub None."""
        try:
            with self.microphone as source:
                # Kalibracja szumu otoczenia
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                logger.info("🎤 Słucham...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

            if self.engine == "google":
                text = self.recognizer.recognize_google(audio, language=self.language)
            else:
                raise ValueError(f"Nieobsługiwany silnik rozpoznawania mowy: {self.engine}")

            logger.info(f"📝 Rozpoznano: {text}")
            return text.lower()

        except sr.WaitTimeoutError:
            logger.warning("⏱️ Nie wykryto mowy w wyznaczonym czasie")
            return None
        except sr.UnknownValueError:
            logger.warning("❌ Nie zrozumiałem, spróbuj ponownie")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Błąd API rozpoznawania mowy: {e}")
            return None

    def start_listening_async(self, callback: Callable[[str], None]) -> None:
        """Uruchamia nasłuchiwanie w tle (osobny wątek), wywołuje callback po każdym rozpoznaniu."""
        self.is_listening = True
        self.on_recognized = callback

        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()

    def _listen_loop(self) -> None:
        while self.is_listening:
            text = self.recognize()
            if text and self.on_recognized:
                self.on_recognized(text)

    def stop_listening(self) -> None:
        self.is_listening = False
