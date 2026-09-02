"""
voice/speech_engine.py — Rozpoznawanie mowy (Speech-to-Text).

Domyślnie: lokalny Whisper (faster-whisper) — offline, nie zależy od jakości
darmowego, nieoficjalnego endpointu Google. Opcja "google" (recognize_google())
zostaje jako zapasowa dla słabszych maszyn, gdzie lokalny model za bardzo
obciąża CPU.

Model Whisper jest wspólny dla wszystkich instancji (ładowanie trwa kilka
sekund i zajmuje pamięć) — wczytuje się raz, leniwie, przy pierwszym użyciu.

Kalibracja szumu otoczenia robiona jest RAZ, przy pierwszym nasłuchu.
Powtarzanie jej przed każdą komendą dokładało pół sekundy do każdego
rozpoznania, a warunki akustyczne i tak nie zmieniają się z minuty na minutę.
Do ponownej kalibracji (np. po włączeniu wentylatora) służy recalibrate().
"""
import io
import threading
from typing import Callable, List, Optional

import speech_recognition as sr

import config
from utils.logger import get_logger

logger = get_logger(__name__)

CALIBRATION_DURATION = 0.8  # sekund nasłuchu tła przy kalibracji

_whisper_model = None  # leniwy singleton — współdzielony, żeby nie ładować modelu wielokrotnie


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel  # ciężki import — tylko gdy faktycznie używany

        logger.info(f"🧠 Ładuję model Whisper ({config.WHISPER_MODEL_SIZE})... (pierwszy raz może potrwać)")
        _whisper_model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
    return _whisper_model


class SpeechEngine:
    def __init__(
        self,
        language: str = config.RECOGNITION_LANGUAGE,
        engine: str = config.SPEECH_ENGINE,
        microphone_index: Optional[int] = config.MICROPHONE_INDEX,
    ):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.NOISE_THRESHOLD * 20  # skala 0-100 -> energia
        self.recognizer.dynamic_energy_threshold = True

        self.language = language
        self.engine = engine
        self.microphone = sr.Microphone(device_index=microphone_index)

        self._calibrated = False
        self.is_listening = False
        self.on_recognized: Optional[Callable[[str], None]] = None

    @staticmethod
    def list_microphones() -> List[str]:
        """Nazwy dostępnych mikrofonów — indeks na liście to MICROPHONE_INDEX z config.py."""
        return sr.Microphone.list_microphone_names()

    def recalibrate(self) -> None:
        """Wymusza ponowną kalibrację szumu przy następnym nasłuchu."""
        self._calibrated = False

    def recognize(
        self,
        timeout: int = config.LISTEN_TIMEOUT,
        phrase_time_limit: int = config.PHRASE_TIME_LIMIT,
    ) -> Optional[str]:
        """Nasłuchuje z mikrofonu i zwraca rozpoznany tekst (lowercase) albo None."""
        try:
            with self.microphone as source:
                if not self._calibrated:
                    logger.info("🎚️ Kalibruję poziom szumu otoczenia...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=CALIBRATION_DURATION)
                    self._calibrated = True

                logger.info("🎤 Słucham...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

            if self.engine == "whisper":
                text = self._recognize_whisper(audio)
            elif self.engine == "google":
                text = self.recognizer.recognize_google(audio, language=self.language)
            else:
                raise ValueError(f"Nieobsługiwany silnik rozpoznawania mowy: {self.engine}")

            logger.info(f"📝 Rozpoznano: {text}")
            return text.lower()

        except sr.WaitTimeoutError:
            logger.info("⏱️ Nie wykryto mowy w wyznaczonym czasie")
            return None
        except sr.UnknownValueError:
            logger.info("❓ Nie zrozumiałem nagrania")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Błąd usługi rozpoznawania (brak internetu?): {e}")
            return None
        except OSError as e:
            logger.error(f"❌ Problem z mikrofonem: {e}")
            return None
        except ImportError as e:
            logger.error(f"❌ Brak biblioteki dla silnika '{self.engine}': {e}")
            return None

    def _recognize_whisper(self, audio: sr.AudioData) -> str:
        """Transkrybuje lokalnym Whisperem. Pusty wynik zgłasza tak samo jak Google."""
        model = _get_whisper_model()
        wav_stream = io.BytesIO(audio.get_wav_data())
        segments, _info = model.transcribe(wav_stream, language=config.WHISPER_LANGUAGE, beam_size=5)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise sr.UnknownValueError()
        return text

    def start_listening_async(self, callback: Callable[[str], None]) -> None:
        """Nasłuch w tle; callback dostaje każdy rozpoznany tekst."""
        self.is_listening = True
        self.on_recognized = callback
        threading.Thread(target=self._listen_loop, name="stt", daemon=True).start()

    def _listen_loop(self) -> None:
        while self.is_listening:
            text = self.recognize()
            if text and self.is_listening and self.on_recognized:
                self.on_recognized(text)

    def stop_listening(self) -> None:
        self.is_listening = False
