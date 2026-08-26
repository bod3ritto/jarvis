"""
automation/youtube_automation.py — Sterowanie YouTube przez Selenium.

Decyzja architektoniczna: JARVIS uruchamia WŁASNĄ, oddzielną przeglądarkę Chrome
(nie podłącza się do przeglądarki użytkownika). Żeby nie logować się do Google
przy każdym starcie, używany jest trwały profil w data/chrome_profile/ —
zaloguj się tam RAZ ręcznie, sesja zostanie zapamiętana.
"""
import os

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import config
from utils.logger import get_logger

logger = get_logger(__name__)

CHROME_PROFILE_DIR = os.path.join(config.DATA_DIR, "chrome_profile")
ELEMENT_WAIT_TIMEOUT = 5  # sekund na pojawienie się elementu wideo
SKIP_BUTTON_WAIT = 1.5  # krótko — gdy reklamy nie ma, nie ma na co czekać

# YouTube przez lata zmieniał klasę przycisku "Pomiń reklamę"; łapiemy warianty.
SKIP_BUTTON_SELECTOR = (
    "button[class*='ytp-ad-skip-button'], "
    "button[class*='ytp-skip-ad-button'], "
    "button[class*='ytp-ad-survey-answer-button']"
)


class YouTubeAutomation:
    def __init__(self, browser: str = config.YOUTUBE_BROWSER):
        self.browser = browser
        self.driver = None

    def initialize(self) -> None:
        """Uruchamia dedykowaną przeglądarkę Chrome z trwałym profilem."""
        if self.driver is not None:
            logger.warning("⚠️ Przeglądarka już uruchomiona")
            return

        os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)

        if self.browser != "chrome":
            logger.warning(f"⚠️ Silnik '{self.browser}' nieobsługiwany — używam Chrome")

        options = Options()
        options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("🌐 Przeglądarka YouTube (Selenium) uruchomiona")

    def is_running(self) -> bool:
        return self.driver is not None

    def close(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
            except WebDriverException as e:
                logger.warning(f"⚠️ Przeglądarka zamknięta niepełnie: {e}")
            finally:
                self.driver = None
                logger.info("🌐 Przeglądarka YouTube zamknięta")

    def open_video(self, url: str) -> None:
        """Otwiera dany URL (konkretne wideo lub youtube.com)."""
        if not self.is_running():
            self.initialize()
        self.driver.get(url)

    def _get_video_element(self):
        """Element <video> aktualnej strony. Rzuca TimeoutException, gdy go brak."""
        return WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

    def _require_driver(self, action: str) -> bool:
        if not self.is_running():
            logger.warning(f"⚠️ Przeglądarka nieuruchomiona — nie mogę wykonać: {action}")
            return False
        return True

    def skip_ad(self, skip_time: int = config.YOUTUBE_SKIP_AD_TIME) -> bool:
        """
        Klika "Pomiń reklamę", a gdy przycisku nie ma — przeskakuje do przodu.

        Skok robimy przez JS (currentTime += n), bo jest dokładny co do sekundy.
        Wcześniejsza wersja wysyłała n naciśnięć strzałki w prawo, a jedno
        naciśnięcie to w YouTube 5 sekund — 30 "sekund" przewijało 150.
        """
        if not self._require_driver("pominięcie reklamy"):
            return False

        try:
            skip_button = WebDriverWait(self.driver, SKIP_BUTTON_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SKIP_BUTTON_SELECTOR))
            )
            skip_button.click()
            logger.info("✅ Reklama pominięta (przycisk Pomiń)")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException):
            logger.info("ℹ️ Brak przycisku Pomiń — przewijam do przodu")

        return self.seek(skip_time)

    def seek(self, seconds: int) -> bool:
        """Przeskakuje o zadaną liczbę sekund (ujemna = do tyłu)."""
        if not self._require_driver("przewinięcie"):
            return False
        try:
            video = self._get_video_element()
            self.driver.execute_script(
                "arguments[0].currentTime = Math.max(0, arguments[0].currentTime + arguments[1]);",
                video,
                seconds,
            )
            logger.info(f"⏭️ Przewinięto o {seconds}s")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"❌ Nie udało się przewinąć: {e}")
            return False

    def _set_paused(self, should_pause: bool) -> bool:
        """Wspólna logika play/pause — ustawia stan, zamiast go przełączać."""
        action = "pauza" if should_pause else "odtwarzanie"
        if not self._require_driver(action):
            return False
        try:
            video = self._get_video_element()
            self.driver.execute_script(
                "if (arguments[1]) { arguments[0].pause(); } else { arguments[0].play(); }",
                video,
                should_pause,
            )
            logger.info("⏸️ Zatrzymano" if should_pause else "▶️ Wznowiono")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"❌ Błąd ({action}): {e}")
            return False

    def play(self) -> bool:
        """Wznawia odtwarzanie. Na grającym wideo nie robi nic (nie jest przełącznikiem)."""
        return self._set_paused(False)

    def pause(self) -> bool:
        """Zatrzymuje odtwarzanie. Na zatrzymanym nie robi nic."""
        return self._set_paused(True)

    def play_pause(self) -> bool:
        """Przełącza stan odtwarzania (gra <-> pauza)."""
        if not self._require_driver("play/pause"):
            return False
        try:
            video = self._get_video_element()
            self.driver.execute_script(
                "if (arguments[0].paused) { arguments[0].play(); } else { arguments[0].pause(); }",
                video,
            )
            logger.info("▶️/⏸️ Przełączono odtwarzanie")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"❌ Błąd play/pause: {e}")
            return False

    def next_video(self) -> bool:
        """Następne wideo — działa w kontekście playlisty/kolejki."""
        if not self._require_driver("następne wideo"):
            return False
        try:
            next_btn = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ytp-next-button"))
            )
            next_btn.click()
            logger.info("⏭️ Następne wideo")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException):
            logger.warning("⚠️ Brak przycisku 'następne' (poza playlistą?)")
            return False

    def previous_video(self) -> bool:
        """Cofa do poprzedniej strony — YouTube nie ma natywnego 'poprzednie wideo'."""
        if not self._require_driver("poprzednie wideo"):
            return False
        try:
            self.driver.back()
            logger.info("⏪ Cofnięto do poprzedniej strony")
            return True
        except WebDriverException as e:
            logger.error(f"❌ Błąd przy cofaniu: {e}")
            return False

    def fullscreen(self) -> bool:
        """
        Przełącza pełny ekran klikając prawdziwy przycisk w pasku odtwarzacza.

        Chrome wymaga, żeby Fullscreen API wywoływało prawdziwe kliknięcie
        użytkownika ("user gesture") — element.click() z execute_script()
        się nie liczy i YouTube go odrzuca. Klawisz 'f' wysłany na <video>
        też zawodzi, bo element bywa "not interactable" pod nakładkami
        sterującymi. Kliknięcie realnego przycisku ytp-fullscreen-button
        omija oba problemy naraz.
        """
        if not self._require_driver("pełny ekran"):
            return False
        try:
            player = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "movie_player"))
            )
            # Pasek sterowania chowa się po bezczynności — trzeba go odsłonić
            # ruchem myszy, zanim przycisk stanie się klikalny.
            ActionChains(self.driver).move_to_element(player).perform()
            button = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ytp-fullscreen-button"))
            )
            button.click()
            logger.info("🖥️ Pełny ekran")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logger.error(f"❌ Błąd pełnego ekranu: {e}")
            return False
