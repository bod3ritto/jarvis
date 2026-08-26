"""
voice/tts_engine.py — Synteza mowy (Text-to-Speech), pyttsx3 / offline.

Silnik pyttsx3 nie jest bezpieczny wątkowo: wywołanie runAndWait() z dwóch
wątków naraz kończy się "RuntimeError: run loop already started", a na Windows
sterownik SAPI5 to obiekt COM przywiązany do wątku, w którym powstał. Dlatego
silnik jest tworzony i obsługiwany WYŁĄCZNIE przez jeden wątek roboczy, a
reszta aplikacji zleca mu mówienie przez kolejkę.

    tts.speak("tekst")              # czeka aż wypowie
    tts.speak_async("tekst")        # wraca natychmiast, mówi w tle
"""
import queue
import threading
from typing import Optional

import config
from utils.logger import get_logger

logger = get_logger(__name__)

INIT_TIMEOUT = 15  # sekund na uruchomienie silnika w wątku roboczym
_STOP = object()  # wartownik kończący pętlę wątku


class TTSEngine:
    def __init__(
        self,
        language: str = config.TTS_LANGUAGE,
        rate: int = config.TTS_RATE,
        volume: float = config.TTS_VOLUME,
    ):
        self.language = language
        self._rate = rate
        self._volume = volume

        self._engine = None
        self._queue: "queue.Queue" = queue.Queue()
        self._ready = threading.Event()
        self._init_error: Optional[BaseException] = None

        self._thread = threading.Thread(target=self._worker, name="tts", daemon=True)
        self._thread.start()

        if not self._ready.wait(timeout=INIT_TIMEOUT):
            logger.error(f"❌ Silnik TTS nie wystartował w ciągu {INIT_TIMEOUT}s")
        elif self._init_error is not None:
            logger.error(f"❌ Nie udało się uruchomić TTS: {self._init_error}")

    @property
    def available(self) -> bool:
        """False jeśli silnik się nie podniósł — aplikacja działa dalej, tylko bez głosu."""
        return self._engine is not None and self._init_error is None

    # ---------------- Wątek roboczy (jedyny właściciel silnika) ----------------

    def _worker(self) -> None:
        try:
            import pyttsx3  # import tutaj: brak paczki nie ma blokować testów reszty kodu

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
            self._select_voice(self.language)
        except Exception as e:
            self._init_error = e
        finally:
            self._ready.set()

        if self._init_error is not None:
            return

        while True:
            item = self._queue.get()
            if item is _STOP:
                break
            text, done = item
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error(f"❌ Błąd syntezy mowy: {e}")
            finally:
                if done is not None:
                    done.set()

    def _select_voice(self, language: str) -> None:
        """Szuka głosu pasującego do języka. Bez polskiego głosu mówi domyślnym."""
        for voice in self._engine.getProperty("voices"):
            languages = getattr(voice, "languages", None) or []
            name = getattr(voice, "name", "") or ""
            voice_id = getattr(voice, "id", "") or ""

            matches_lang = any(language in str(l).lower() for l in languages)
            matches_name = any(
                marker in f"{name} {voice_id}".lower()
                for marker in ("polish", "polski", "pl-pl", "pl_pl")
            )
            if matches_lang or matches_name:
                self._engine.setProperty("voice", voice.id)
                logger.info(f"🔊 Wybrano głos TTS: {name or voice_id}")
                return

        logger.warning(
            f"⚠️ Nie znaleziono głosu '{language}' w systemie — używam domyślnego. "
            "Polski głos dodasz w: Ustawienia Windows > Czas i język > Mowa."
        )

    # ---------------- API publiczne ----------------

    def speak(self, text: str, wait: bool = True) -> None:
        """Wypowiada tekst. wait=True blokuje do końca wypowiedzi."""
        if not self.available:
            logger.warning(f"🔇 TTS niedostępny, pomijam: {text}")
            return

        logger.info(f"🔊 Mówię: {text}")
        done = threading.Event() if wait else None
        self._queue.put((text, done))
        if done is not None:
            done.wait()

    def speak_async(self, text: str) -> None:
        """Zleca wypowiedź i wraca natychmiast — kolejne zlecenia ustawiają się w kolejce."""
        self.speak(text, wait=False)

    def stop(self) -> None:
        """Przerywa bieżącą wypowiedź i czyści kolejkę oczekujących."""
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                break
            if item is not _STOP and item[1] is not None:
                item[1].set()  # nie zostawiaj nikogo czekającego w nieskończoność

        if self.available:
            try:
                self._engine.stop()
            except Exception as e:
                logger.error(f"❌ Nie udało się zatrzymać TTS: {e}")

    def shutdown(self) -> None:
        """Zamyka wątek roboczy — wołane przy zamykaniu aplikacji."""
        self.stop()
        self._queue.put(_STOP)
        self._thread.join(timeout=5)
